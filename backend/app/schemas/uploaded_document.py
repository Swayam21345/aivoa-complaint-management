from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class UploadedDocumentRead(BaseModel):
    """Uploaded document metadata schema."""

    id: UUID
    complaint_id: Optional[UUID] = None
    input_type: str
    original_filename: Optional[str] = None
    content_type: Optional[str] = None
    file_size_bytes: Optional[int] = None
    extracted_text: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
