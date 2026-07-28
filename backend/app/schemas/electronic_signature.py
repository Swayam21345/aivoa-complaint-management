from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ElectronicSignatureCreate(BaseModel):
    """
    Payload required for 21 CFR Part 11 Electronic Signature re-authentication.
    """

    password: str = Field(
        ...,
        min_length=1,
        description="Current user password for re-authentication identity verification",
    )
    reason: str = Field(
        ...,
        min_length=3,
        description="Mandatory legal signing rationale for 21 CFR Part 11 compliance",
    )
    target_status: str | None = Field(
        default=None,
        description="Optional status to transition the complaint to (e.g., QA_APPROVED, CLOSED)",
    )
    action: str | None = Field(
        default=None,
        description="Optional custom action name (e.g., QA Approval, Complaint Closure)",
    )


class ElectronicSignatureResponse(BaseModel):
    """
    Response model returned immediately upon successful 21 CFR Part 11 signing.
    """

    signed: bool = True
    signed_by: str
    timestamp: datetime
    signature_id: UUID
    hash: str


class ElectronicSignatureRead(BaseModel):
    """
    Read representation of an immutable electronic signature record.
    """

    id: UUID
    complaint_id: UUID | None
    user_id: UUID
    user_name: str | None = None
    action: str
    status_before: str
    status_after: str
    reason: str
    signature_timestamp: datetime
    ip_address: str | None = None
    user_agent: str | None = None
    signature_hash: str
    created_at: datetime

    class Config:
        from_attributes = True
