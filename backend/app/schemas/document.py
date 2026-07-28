from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DocumentVersionRead(BaseModel):
    id: UUID
    document_id: UUID
    version: int
    original_filename: str
    stored_filename: str
    mime_type: str
    size: int
    sha256_hash: str
    storage_path: str
    uploaded_by: str
    uploaded_at: datetime
    change_summary: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class DocumentCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = None
    category: str = Field(
        "Complaint Evidence",
        description="Complaint Evidence, Customer Images, Lab Report, Root Cause Evidence, CAPA Evidence, Supplier Evidence, Training Document, Calibration Report, Certificate, Other",
    )
    entity_type: str = Field("COMPLAINT", description="COMPLAINT, RCA, or CAPA")
    entity_id: UUID = Field(..., description="UUID of linked entity")


class DocumentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = Field(None, description="DRAFT, UNDER_REVIEW, APPROVED, ARCHIVED")


class DocumentApproval(BaseModel):
    password: str = Field(..., description="Password re-authentication for 21 CFR Part 11 electronic signature")
    reason: str = Field(..., min_length=10, description="Signature justification")


class DocumentRead(BaseModel):
    id: UUID
    document_number: str
    title: str
    description: Optional[str] = None
    category: str
    entity_type: str
    entity_id: UUID
    current_version: int
    status: str
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime
    versions: List[DocumentVersionRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class DocumentListResponse(BaseModel):
    items: List[DocumentRead]
    total: int
    page: int
    page_size: int
    total_pages: int


class DocumentDashboardRead(BaseModel):
    total_documents: int
    approved_documents: int
    draft_documents: int
    archived_documents: int
    by_category: dict[str, int]
    by_entity_type: dict[str, int]


class DocumentUploadResponse(BaseModel):
    document: DocumentRead
    latest_version: DocumentVersionRead


class DocumentVerifyResponse(BaseModel):
    document_id: UUID
    version_id: UUID
    original_filename: str
    stored_hash: str
    calculated_hash: str
    is_valid: bool
    verification_message: str
