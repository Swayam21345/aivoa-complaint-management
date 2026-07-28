import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.complaint import Complaint


class ReviewerNote(Base):
    """
    Notes added by QA reviewers or investigators for a complaint record.
    """

    __tablename__ = "reviewer_notes"

    __table_args__ = (
        Index("idx_reviewer_notes_complaint_id", "complaint_id"),
        Index("idx_reviewer_notes_created_at", "created_at"),
    )

    # ── Primary key ────────────────────────────────────────────────────────
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # ── Foreign key ────────────────────────────────────────────────────────
    complaint_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("complaints.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ── Note details ───────────────────────────────────────────────────────
    author: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    # ── Timestamps ─────────────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # ── Relationship ───────────────────────────────────────────────────────
    complaint: Mapped["Complaint"] = relationship(
        "Complaint",
        back_populates="notes",
    )

    def __repr__(self) -> str:
        return f"<ReviewerNote id={self.id} author={self.author}>"
