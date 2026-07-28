from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.complaint import AIAnalysisSchema

# ─── Shared type alias ────────────────────────────────────────────────────────

InputType = Literal["pdf", "image", "email", "text"]

# ─── Upload request (multipart/form-data — documented for OpenAPI) ────────────


class UploadFormFields(BaseModel):
    """
    Documents the expected form fields for POST /api/upload.
    FastAPI handles these via Form() parameters in the route directly;
    this class is used for documentation purposes only.
    """

    input_type: InputType = Field(
        ..., description="Source document type: pdf | image | email | text"
    )
    text: Optional[str] = Field(
        default=None,
        description="Raw complaint or email text (required when input_type is 'email' or 'text')",
    )


# ─── Upload record (DB read) ──────────────────────────────────────────────────


class UploadRecordRead(BaseModel):
    """Full upload record as stored in the database."""

    id: UUID
    input_type: str
    original_filename: Optional[str] = None
    content_type: Optional[str] = None
    file_size_bytes: Optional[int] = None
    storage_path: Optional[str] = None
    extracted_text: Optional[str] = None
    extraction_status: str
    extraction_error: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Upload response ──────────────────────────────────────────────────────────


class UploadResponse(BaseModel):
    """
    Response returned by POST /api/upload after document ingestion.

    Phase 2A: returns extracted_text and upload metadata.
    Phase 3:  ai_analysis will be populated by the LangGraph workflow.
    """

    status: Literal["success", "error"] = "success"
    input_type: InputType
    upload_id: UUID = Field(description="UUID of the persisted UploadRecord row")
    original_filename: Optional[str] = Field(
        default=None, description="Original filename (null for text/email inputs)"
    )
    file_size_bytes: Optional[int] = Field(
        default=None, description="File size in bytes (null for text/email inputs)"
    )
    extracted_text: str = Field(
        description="Plain text extracted from the document"
    )
    char_count: int = Field(
        description="Character count of extracted_text"
    )
    # Phase 3: populated by LangGraph workflow
    ai_analysis: Optional[AIAnalysisSchema] = Field(
        default=None,
        description="AI-extracted complaint fields (null until Phase 3)",
    )
    processing_time_ms: Optional[int] = Field(
        default=None,
        description="Total wall-clock time for ingestion + AI pipeline in ms",
    )


# ─── Upload error response ────────────────────────────────────────────────────


class UploadErrorResponse(BaseModel):
    """Returned when document ingestion fails."""

    status: Literal["error"] = "error"
    input_type: Optional[InputType] = None
    detail: str
