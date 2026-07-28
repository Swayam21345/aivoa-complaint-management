import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.complaint import Complaint
    from app.models.user import User


class ElectronicSignature(Base):
    """
    21 CFR Part 11 compliant immutable electronic signature record.

    Signatures are cryptographically hashed (SHA-256) and appended to the complaint ledger.
    Neither UPDATE nor DELETE is permitted on signature records.
    """

    __tablename__ = "electronic_signatures"

    __table_args__ = (
        Index("idx_signatures_complaint_id", "complaint_id"),
        Index("idx_signatures_user_id", "user_id"),
        Index("idx_signatures_timestamp", "signature_timestamp"),
    )

    # ── Primary key ────────────────────────────────────────────────────────
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # ── Foreign keys ───────────────────────────────────────────────────────
    complaint_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("complaints.id", ondelete="CASCADE"),
        nullable=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )

    # ── Signature Metadata ──────────────────────────────────────────────────
    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Specific action signed, e.g. QA Approval, Complaint Closure",
    )
    status_before: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )
    status_after: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )
    reason: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Mandatory 21 CFR Part 11 legal signing rationale",
    )
    signature_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    ip_address: Mapped[str | None] = mapped_column(
        String(45),
        nullable=True,
    )
    user_agent: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    signature_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        comment="SHA-256 cryptographic signature checksum",
    )

    # ── Audit timestamp ─────────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # ── Relationships ──────────────────────────────────────────────────────
    complaint: Mapped["Complaint"] = relationship(
        "Complaint",
        back_populates="signatures",
    )
    user: Mapped["User"] = relationship(
        "User",
        back_populates="signatures",
    )

    def __repr__(self) -> str:
        return f"<ElectronicSignature {self.id} action='{self.action}' user_id={self.user_id}>"
