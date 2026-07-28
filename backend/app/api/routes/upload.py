"""
Upload route — POST /api/upload

Pipeline:
  1. Validate input_type, file MIME type, and file size.
  2. Save the file to disk (pdf / image inputs only).
  3. Extract plain text via document_parser.
  4. Persist an UploadRecord row to PostgreSQL.
  5. Return UploadResponse with extracted_text and metadata.

Phase 3 addition: step 5.5 — invoke LangGraph workflow and populate ai_analysis.
"""
import time
import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.state import ComplaintState
from app.ai.workflow import complaint_workflow
from app.api.dependencies import get_db, require_roles
from app.config import Settings, get_settings
from app.models.upload_record import UploadRecord
from app.schemas.complaint import AIAnalysisSchema
from app.schemas.upload import InputType, UploadResponse
from app.services.document_parser import extract_text

router = APIRouter(prefix="/upload", tags=["Upload"])

# ─── Allowed MIME types per input type ───────────────────────────────────────

ALLOWED_MIME: dict[str, list[str]] = {
    "pdf": ["application/pdf"],
    "image": ["image/jpeg", "image/png", "image/tiff"],
}


# ─── Route ────────────────────────────────────────────────────────────────────

@router.post(
    "",
    response_model=UploadResponse,
    status_code=status.HTTP_200_OK,
    summary="Upload and ingest a complaint document",
    description=(
        "Accepts a PDF, image, email body, or plain text complaint. "
        "Extracts raw text, persists an UploadRecord, and returns the "
        "extracted content. AI analysis fields are null until Phase 3."
    ),
    dependencies=[Depends(require_roles("ADMIN", "QA_MANAGER"))],
)
async def upload_complaint(
    input_type: InputType = Form(..., description="pdf | image | email | text"),
    file: Optional[UploadFile] = File(
        default=None, description="Binary file — required for pdf / image"
    ),
    text: Optional[str] = Form(
        default=None, description="Raw text — required for email / text"
    ),
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> UploadResponse:

    start_ms = int(time.monotonic() * 1000)

    # ── 1. Input validation ───────────────────────────────────────────────

    if input_type in ("pdf", "image") and file is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A file is required for input_type='{input_type}'.",
        )
    if input_type in ("email", "text") and not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"'text' field is required for input_type='{input_type}'.",
        )

    # ── 2. File validation + read ─────────────────────────────────────────

    file_content: Optional[bytes] = None
    original_filename: Optional[str] = None
    content_type: Optional[str] = None
    file_size_bytes: Optional[int] = None
    storage_path: Optional[str] = None

    if file is not None:
        # MIME type check
        if input_type in ALLOWED_MIME:
            if file.content_type not in ALLOWED_MIME[input_type]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Unsupported file type '{file.content_type}'. "
                        f"Allowed for '{input_type}': "
                        f"{', '.join(ALLOWED_MIME[input_type])}"
                    ),
                )

        # Size limit check
        size_limit = (
            settings.max_pdf_size_bytes
            if input_type == "pdf"
            else settings.max_image_size_bytes
        )
        file_content = await file.read()
        if len(file_content) > size_limit:
            limit_mb = size_limit // (1024 * 1024)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File exceeds the {limit_mb} MB size limit.",
            )

        original_filename = file.filename
        content_type = file.content_type
        file_size_bytes = len(file_content)

    # ── 3. Save file to disk ──────────────────────────────────────────────

    if file_content is not None:
        storage_path = _save_file(
            content=file_content,
            input_type=input_type,
            original_filename=original_filename,
            storage_dir=settings.upload_storage_path,
        )

    # ── 4. Extract text ───────────────────────────────────────────────────

    extraction_status = "success"
    extraction_error: Optional[str] = None
    extracted_text = ""

    try:
        extracted_text = await extract_text(
            input_type=input_type,
            file_content=file_content,
            raw_text=text,
        )
        if not extracted_text.strip():
            extraction_status = "partial"
            extraction_error = (
                "No text could be extracted from the document. "
                "The file may be a scanned image without OCR-readable content."
            )
    except Exception as exc:
        extraction_status = "failed"
        extraction_error = str(exc)
        # Do not re-raise — persist the failure record and return a graceful error

    # ── 5. Persist UploadRecord ───────────────────────────────────────────

    record = UploadRecord(
        input_type=input_type,
        original_filename=original_filename,
        content_type=content_type,
        file_size_bytes=file_size_bytes,
        storage_path=storage_path,
        extracted_text=extracted_text if extraction_status != "failed" else None,
        extraction_status=extraction_status,
        extraction_error=extraction_error,
    )
    db.add(record)
    await db.flush()   # assign record.id without committing the outer transaction
    await db.commit()
    await db.refresh(record)

    # ── 5a. Handle hard extraction failure ───────────────────────────────

    if extraction_status == "failed":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"Text extraction failed: {extraction_error}. "
                "An upload record has been saved for audit purposes."
            ),
        )

    # ── 5b. Execute AI workflow ───────────────────────────────────────────

    ai_analysis_schema: Optional[AIAnalysisSchema] = None
    if extracted_text and extracted_text.strip():
        initial_state: ComplaintState = {
            "raw_text": extracted_text,
            "input_type": input_type,
        }
        try:
            workflow_res = await complaint_workflow.ainvoke(initial_state)
            out = workflow_res.get("final_output") or {}
            ai_analysis_schema = AIAnalysisSchema(
                complaint_summary=out.get("complaint_summary"),
                product_name=out.get("product_name"),
                batch_number=out.get("batch_number"),
                customer_name=out.get("customer_name"),
                category=out.get("category"),
                risk_level=out.get("risk_level"),
                root_cause_recommendation=out.get("root_cause_recommendation"),
                capa_recommendation=out.get("capa_recommendation"),
                summary=out.get("summary"),
                completeness=out.get("completeness"),
                root_cause=out.get("root_cause"),
                capa=out.get("capa"),
                duplicates=out.get("duplicates"),
                risk_explanation=out.get("risk_explanation"),
                processing_time_ms=int(time.monotonic() * 1000) - start_ms,
                model_used=settings.groq_model,
            )
        except Exception:
            pass

    # ── 6. Build response ─────────────────────────────────────────────────

    elapsed_ms = int(time.monotonic() * 1000) - start_ms

    return UploadResponse(
        status="success",
        input_type=input_type,
        upload_id=record.id,
        original_filename=original_filename,
        file_size_bytes=file_size_bytes,
        extracted_text=extracted_text,
        char_count=len(extracted_text),
        ai_analysis=ai_analysis_schema,
        processing_time_ms=elapsed_ms,
    )


# ─── Helper ───────────────────────────────────────────────────────────────────

def _save_file(
    content: bytes,
    input_type: str,
    original_filename: Optional[str],
    storage_dir: Path,
) -> str:
    """
    Write file bytes to the upload storage directory.

    Filename format: <uuid4>_<original_filename>
    Returns the relative storage path as a string.
    """

    ext = Path(original_filename).suffix if original_filename else f".{input_type}"
    safe_name = f"{uuid.uuid4().hex}{ext}"
    dest: Path = storage_dir / safe_name
    dest.write_bytes(content)
    return safe_name
