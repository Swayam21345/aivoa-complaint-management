from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class ComplaintHistoryRead(BaseModel):
    """Audit log entry schema for a complaint status transition."""

    id: UUID
    complaint_id: UUID
    old_status: Optional[str] = None
    new_status: str
    changed_by: Optional[str] = None
    change_reason: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
