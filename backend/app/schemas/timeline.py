from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class TimelineEvent(BaseModel):
    """Single chronological event in the complaint audit timeline."""

    id: str
    event_type: str = Field(
        description="CREATED | AI_ANALYZED | STATUS_CHANGED | NOTE_ADDED | CAPA_COMPLETED | RESOLVED"
    )
    title: str
    description: Optional[str] = None
    author: Optional[str] = None
    timestamp: datetime
    icon: str = Field(default="📌")
    status: Optional[str] = None


class ComplaintTimelineResponse(BaseModel):
    """Response model for GET /api/complaints/{id}/timeline."""

    complaint_id: UUID
    complaint_number: str
    events: list[TimelineEvent] = Field(default_factory=list)
