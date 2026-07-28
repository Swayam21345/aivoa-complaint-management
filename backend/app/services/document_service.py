import hashlib
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document, DocumentDownloadLog, DocumentVersion
from app.models.user import User
from app.schemas.document import (
    DocumentApproval,
    DocumentCreate,
    DocumentDashboardRead,
    DocumentListResponse,
    DocumentRead,
    DocumentUpdate,
    DocumentUploadResponse,
    DocumentVersionRead,
    DocumentVerifyResponse,
)
from app.schemas.electronic_signature import ElectronicSignatureCreate
from app.services.signature_service import create_signature
from app.services.workflow_service import log_audit_event

# File Upload Constants
MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB
ALLOWED_EXTENSIONS = {
    "pdf",
    "png",
    "jpg",
    "jpeg",
    "gif",
    "docx",
    "xlsx",
    "xls",
    "csv",
    "txt",
    "zip",
    "mp4",
}
STORAGE_BASE_DIR = "uploads/documents"


def get_file_extension(filename: str) -> str:
    parts = filename.rsplit(".", 1)
    if len(parts) > 1:
        return parts[1].lower()
    return ""


def calculate_sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


class DocumentService:
    @staticmethod
    async def generate_document_number(db: AsyncSession) -> str:
        year_str = datetime.now(timezone.utc).strftime("%Y")
        prefix = f"DOC-{year_str}-"
        stmt = select(func.count()).select_from(Document).where(Document.document_number.like(f"{prefix}%"))
        count = (await db.execute(stmt)).scalar_one() or 0
        return f"{prefix}{count + 1:04d}"

    @staticmethod
    async def get_document_or_404(db: AsyncSession, doc_id: UUID) -> Document:
        stmt = select(Document).where(Document.id == doc_id)
        res = await db.execute(stmt)
        doc = res.scalar_one_or_none()
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with ID '{doc_id}' not found.",
            )
        return doc

    @staticmethod
    async def upload_document(
        db: AsyncSession,
        file: UploadFile,
        create_payload: DocumentCreate,
        current_user: User,
    ) -> DocumentUploadResponse:
        ext = get_file_extension(file.filename or "")
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File extension '.{ext}' is not allowed. Allowed extensions: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
            )

        content = await file.read()
        if len(content) > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size exceeds 50 MB limit. Provided size: {len(content) / (1024 * 1024):.1f} MB.",
            )

        sha256_hash = calculate_sha256(content)
        doc_number = await DocumentService.generate_document_number(db)
        uploader_name = current_user.full_name or current_user.email

        doc_dir = os.path.join(STORAGE_BASE_DIR, doc_number)
        os.makedirs(doc_dir, exist_ok=True)

        original_filename = file.filename or "unnamed_file"
        stored_filename = f"v1_{sha256_hash[:8]}_{original_filename}"
        storage_path = os.path.join(doc_dir, stored_filename)

        with open(storage_path, "wb") as f:
            f.write(content)

        doc = Document(
            document_number=doc_number,
            title=create_payload.title,
            description=create_payload.description,
            category=create_payload.category,
            entity_type=create_payload.entity_type,
            entity_id=create_payload.entity_id,
            current_version=1,
            status="DRAFT",
            created_by=uploader_name,
            updated_by=uploader_name,
        )
        db.add(doc)
        await db.flush()

        version = DocumentVersion(
            document_id=doc.id,
            version=1,
            original_filename=original_filename,
            stored_filename=stored_filename,
            mime_type=file.content_type or "application/octet-stream",
            size=len(content),
            sha256_hash=sha256_hash,
            storage_path=storage_path,
            uploaded_by=uploader_name,
            change_summary="Initial document upload",
        )
        db.add(version)

        # Audit Event
        complaint_fk = doc.entity_id if doc.entity_type == "COMPLAINT" else None
        await log_audit_event(
            db=db,
            action_type="Document Uploaded",
            description=f"Uploaded document {doc_number} ('{doc.title}') v1 with SHA-256 {sha256_hash[:8]}...",
            actor_email=current_user.email,
            complaint_id=complaint_fk,
            metadata={"document_id": str(doc.id), "hash": sha256_hash, "size": len(content)},
        )

        await db.commit()
        await db.refresh(doc)
        await db.refresh(version)

        return DocumentUploadResponse(
            document=DocumentRead.model_validate(doc),
            latest_version=DocumentVersionRead.model_validate(version),
        )

    @staticmethod
    async def create_new_version(
        db: AsyncSession,
        doc_id: UUID,
        file: UploadFile,
        change_summary: Optional[str],
        current_user: User,
    ) -> DocumentUploadResponse:
        doc = await DocumentService.get_document_or_404(db, doc_id)
        ext = get_file_extension(file.filename or "")
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File extension '.{ext}' is not allowed.",
            )

        content = await file.read()
        if len(content) > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size exceeds 50 MB limit.",
            )

        sha256_hash = calculate_sha256(content)
        uploader_name = current_user.full_name or current_user.email

        new_v_num = doc.current_version + 1
        doc_dir = os.path.join(STORAGE_BASE_DIR, doc.document_number)
        os.makedirs(doc_dir, exist_ok=True)

        original_filename = file.filename or "unnamed_file"
        stored_filename = f"v{new_v_num}_{sha256_hash[:8]}_{original_filename}"
        storage_path = os.path.join(doc_dir, stored_filename)

        with open(storage_path, "wb") as f:
            f.write(content)

        doc.current_version = new_v_num
        doc.updated_by = uploader_name
        doc.updated_at = datetime.now(timezone.utc)

        version = DocumentVersion(
            document_id=doc.id,
            version=new_v_num,
            original_filename=original_filename,
            stored_filename=stored_filename,
            mime_type=file.content_type or "application/octet-stream",
            size=len(content),
            sha256_hash=sha256_hash,
            storage_path=storage_path,
            uploaded_by=uploader_name,
            change_summary=change_summary or f"Uploaded version {new_v_num}",
        )
        db.add(version)

        complaint_fk = doc.entity_id if doc.entity_type == "COMPLAINT" else None
        await log_audit_event(
            db=db,
            action_type="Document Version Created",
            description=f"Uploaded new version v{new_v_num} for document {doc.document_number}.",
            actor_email=current_user.email,
            complaint_id=complaint_fk,
        )

        # Step 5 Automatic Retraining Trigger when SOP / Document version updates
        if doc.category in ("SOP", "Training Document", "Quality Document", "Complaint Evidence"):
            from app.services.training_service import trigger_automatic_retraining
            await trigger_automatic_retraining(
                db=db,
                source_type="DOCUMENT",
                source_id=str(doc.id),
                title=f"{doc.document_number} (v{new_v_num}): {doc.title}",
                description=f"SOP/Document version updated to v{new_v_num}. Re-training required.",
                affected_user_ids=[],
            )

        await db.commit()
        await db.refresh(doc)
        await db.refresh(version)


        return DocumentUploadResponse(
            document=DocumentRead.model_validate(doc),
            latest_version=DocumentVersionRead.model_validate(version),
        )

    @staticmethod
    async def get_document(db: AsyncSession, doc_id: UUID) -> DocumentRead:
        doc = await DocumentService.get_document_or_404(db, doc_id)
        return DocumentRead.model_validate(doc)

    @staticmethod
    async def update_document(
        db: AsyncSession,
        doc_id: UUID,
        payload: DocumentUpdate,
        current_user: User,
    ) -> DocumentRead:
        doc = await DocumentService.get_document_or_404(db, doc_id)
        updater_name = current_user.full_name or current_user.email

        if payload.title is not None:
            doc.title = payload.title
        if payload.description is not None:
            doc.description = payload.description
        if payload.category is not None:
            doc.category = payload.category
        if payload.status is not None:
            if payload.status == "APPROVED":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Document approval requires 21 CFR Part 11 electronic signature via POST /api/documents/{id}/approve.",
                )
            doc.status = payload.status

        doc.updated_by = updater_name
        doc.updated_at = datetime.now(timezone.utc)

        await db.commit()
        await db.refresh(doc)
        return DocumentRead.model_validate(doc)

    @staticmethod
    async def approve_document(
        db: AsyncSession,
        doc_id: UUID,
        payload: DocumentApproval,
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> DocumentRead:
        doc = await DocumentService.get_document_or_404(db, doc_id)
        if doc.status == "APPROVED":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Document {doc.document_number} is already APPROVED.",
            )

        complaint_fk = doc.entity_id if doc.entity_type == "COMPLAINT" else doc.id

        sig_payload = ElectronicSignatureCreate(
            password=payload.password,
            reason=payload.reason,
            action="Document Approval",
            target_status="APPROVED",
        )
        await create_signature(
            db=db,
            complaint_id=complaint_fk,
            payload=sig_payload,
            current_user=current_user,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        now = datetime.now(timezone.utc)
        doc.status = "APPROVED"
        doc.approved_by = current_user.full_name or current_user.email
        doc.approved_at = now
        doc.updated_by = current_user.full_name or current_user.email
        doc.updated_at = now

        await log_audit_event(
            db=db,
            action_type="Document Approved",
            description=f"Approved document {doc.document_number} with 21 CFR Part 11 electronic signature.",
            actor_email=current_user.email,
            complaint_id=doc.entity_id if doc.entity_type == "COMPLAINT" else None,
        )

        await db.commit()
        await db.refresh(doc)
        return DocumentRead.model_validate(doc)

    @staticmethod
    async def archive_document(
        db: AsyncSession,
        doc_id: UUID,
        current_user: User,
    ) -> DocumentRead:
        doc = await DocumentService.get_document_or_404(db, doc_id)
        doc.status = "ARCHIVED"
        doc.updated_by = current_user.full_name or current_user.email
        doc.updated_at = datetime.now(timezone.utc)

        await log_audit_event(
            db=db,
            action_type="Document Archived",
            description=f"Archived document {doc.document_number}.",
            actor_email=current_user.email,
            complaint_id=doc.entity_id if doc.entity_type == "COMPLAINT" else None,
        )

        await db.commit()
        await db.refresh(doc)
        return DocumentRead.model_validate(doc)

    @staticmethod
    async def restore_document(
        db: AsyncSession,
        doc_id: UUID,
        current_user: User,
    ) -> DocumentRead:
        doc = await DocumentService.get_document_or_404(db, doc_id)
        doc.status = "DRAFT"
        doc.updated_by = current_user.full_name or current_user.email
        doc.updated_at = datetime.now(timezone.utc)

        await log_audit_event(
            db=db,
            action_type="Document Restored",
            description=f"Restored document {doc.document_number} to DRAFT status.",
            actor_email=current_user.email,
            complaint_id=doc.entity_id if doc.entity_type == "COMPLAINT" else None,
        )

        await db.commit()
        await db.refresh(doc)
        return DocumentRead.model_validate(doc)

    @staticmethod
    async def download_document(
        db: AsyncSession,
        doc_id: UUID,
        version_id: Optional[UUID],
        current_user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Tuple[str, str, str]:
        doc = await DocumentService.get_document_or_404(db, doc_id)

        if version_id:
            stmt = select(DocumentVersion).where(DocumentVersion.id == version_id, DocumentVersion.document_id == doc_id)
        else:
            stmt = (
                select(DocumentVersion)
                .where(DocumentVersion.document_id == doc_id)
                .order_by(DocumentVersion.version.desc())
            )

        res = await db.execute(stmt)
        ver = res.scalar_one_or_none()
        if not ver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Requested version for document '{doc.document_number}' not found.",
            )

        # Log Download
        dl_log = DocumentDownloadLog(
            document_id=doc.id,
            version_id=ver.id,
            downloaded_by=current_user.full_name or current_user.email,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        db.add(dl_log)

        await log_audit_event(
            db=db,
            action_type="Document Downloaded",
            description=f"Downloaded version v{ver.version} of document {doc.document_number} ('{ver.original_filename}').",
            actor_email=current_user.email,
            complaint_id=doc.entity_id if doc.entity_type == "COMPLAINT" else None,
        )

        await db.commit()
        return ver.storage_path, ver.original_filename, ver.mime_type

    @staticmethod
    async def verify_document_hash(
        db: AsyncSession,
        doc_id: UUID,
        version_id: Optional[UUID] = None,
    ) -> DocumentVerifyResponse:
        doc = await DocumentService.get_document_or_404(db, doc_id)

        if version_id:
            stmt = select(DocumentVersion).where(DocumentVersion.id == version_id, DocumentVersion.document_id == doc_id)
        else:
            stmt = (
                select(DocumentVersion)
                .where(DocumentVersion.document_id == doc_id)
                .order_by(DocumentVersion.version.desc())
            )

        res = await db.execute(stmt)
        ver = res.scalar_one_or_none()
        if not ver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document version not found for verification.",
            )

        if not os.path.exists(ver.storage_path):
            return DocumentVerifyResponse(
                document_id=doc.id,
                version_id=ver.id,
                original_filename=ver.original_filename,
                stored_hash=ver.sha256_hash,
                calculated_hash="FILE_NOT_FOUND",
                is_valid=False,
                verification_message="CRITICAL WARNING: Storage file missing from disk.",
            )

        with open(ver.storage_path, "rb") as f:
            content = f.read()

        calc_hash = calculate_sha256(content)
        is_valid = calc_hash == ver.sha256_hash

        msg = (
            "Integrity Verified: SHA-256 hash matches disk content exactly."
            if is_valid
            else "CRITICAL ALERT: File hash mismatch detected! Possible file tampering."
        )

        return DocumentVerifyResponse(
            document_id=doc.id,
            version_id=ver.id,
            original_filename=ver.original_filename,
            stored_hash=ver.sha256_hash,
            calculated_hash=calc_hash,
            is_valid=is_valid,
            verification_message=msg,
        )

    @staticmethod
    async def delete_document(
        db: AsyncSession,
        doc_id: UUID,
        current_user: User,
    ) -> None:
        doc = await DocumentService.get_document_or_404(db, doc_id)

        await log_audit_event(
            db=db,
            action_type="Document Deleted",
            description=f"Deleted document {doc.document_number} ('{doc.title}').",
            actor_email=current_user.email,
            complaint_id=doc.entity_id if doc.entity_type == "COMPLAINT" else None,
        )

        await db.delete(doc)
        await db.commit()

    @staticmethod
    async def list_documents(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 10,
        category: Optional[str] = None,
        status_filter: Optional[str] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[UUID] = None,
        search: Optional[str] = None,
    ) -> DocumentListResponse:
        stmt = select(Document)

        filters = []
        if category:
            filters.append(Document.category == category)
        if status_filter:
            filters.append(Document.status == status_filter)
        if entity_type:
            filters.append(Document.entity_type == entity_type)
        if entity_id:
            filters.append(Document.entity_id == entity_id)
        if search:
            pattern = f"%{search}%"
            filters.append(
                or_(
                    Document.document_number.ilike(pattern),
                    Document.title.ilike(pattern),
                    Document.description.ilike(pattern),
                )
            )

        if filters:
            stmt = stmt.where(*filters)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await db.execute(count_stmt)).scalar_one() or 0

        stmt = stmt.order_by(Document.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        docs = (await db.execute(stmt)).scalars().all()

        items = [DocumentRead.model_validate(d) for d in docs]
        total_pages = (total + page_size - 1) // page_size if total > 0 else 1

        return DocumentListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    @staticmethod
    async def get_dashboard_metrics(db: AsyncSession) -> DocumentDashboardRead:
        stmt = select(Document)
        docs = (await db.execute(stmt)).scalars().all()

        total = len(docs)
        approved = sum(1 for d in docs if d.status == "APPROVED")
        draft = sum(1 for d in docs if d.status in ("DRAFT", "UNDER_REVIEW"))
        archived = sum(1 for d in docs if d.status == "ARCHIVED")

        cat_counts: Dict[str, int] = {}
        entity_counts: Dict[str, int] = {}

        for d in docs:
            cat_counts[d.category] = cat_counts.get(d.category, 0) + 1
            entity_counts[d.entity_type] = entity_counts.get(d.entity_type, 0) + 1

        return DocumentDashboardRead(
            total_documents=total,
            approved_documents=approved,
            draft_documents=draft,
            archived_documents=archived,
            by_category=cat_counts,
            by_entity_type=entity_counts,
        )

    # ── AI Copilot Extension Hooks ──────────────────────────────────────────
    @staticmethod
    async def ai_hook_ocr_extraction(file_bytes: bytes, mime_type: str) -> Dict[str, Any]:
        """Extension point for future OCR text extraction."""
        return {"status": "AI_HOOK_READY", "text": "", "confidence": 1.0}

    @staticmethod
    async def ai_hook_generate_summary(extracted_text: str) -> str:
        """Extension point for future AI document summarization."""
        return "AI Summary hook ready."

    @staticmethod
    async def ai_hook_detect_duplicates(sha256_hash: str) -> bool:
        """Extension point for future AI duplicate document detection."""
        return False

    @staticmethod
    async def ai_hook_classify_document(title: str, text: str) -> str:
        """Extension point for future AI document classification."""
        return "Complaint Evidence"
