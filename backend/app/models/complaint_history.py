import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.complaint import Complaint


class ComplaintHistory(Base):
    """
    Audit log recording every status transition for a complaint record.
    """

    __tablename__ = "complaint_history"

    __table_args__ = (
        Index("idx_complaint_history_complaint_id", "complaint_id"),
        Index("idx_complaint_history_created_at", "created_at"),
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

    # ── Audit fields ───────────────────────────────────────────────────────
    old_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    new_status: Mapped[str] = mapped_column(String(30), nullable=False)
    changed_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    change_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ── Timestamp ──────────────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # ── Relationship ───────────────────────────────────────────────────────
    complaint: Mapped["Complaint"] = relationship(
        "Complaint",
        back_populates="history",
    )

    def __repr__(self) -> str:
        return (
            f"<ComplaintHistory complaint_id={self.complaint_id} "
            f"{self.old_status}->{self.new_status}>"
        )
