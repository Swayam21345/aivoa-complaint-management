from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ReviewerNoteCreate(BaseModel):
    """Request body for creating a reviewer note."""

    author: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)


class ReviewerNoteUpdate(BaseModel):
    """Request body for updating a reviewer note."""

    content: str = Field(..., min_length=1)


class ReviewerNoteRead(BaseModel):
    """Reviewer note response schema."""

    id: UUID
    complaint_id: UUID
    author: str
    content: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
