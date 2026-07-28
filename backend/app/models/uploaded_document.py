import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Index, String, Text, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.complaint import Complaint


class UploadedDocument(Base):
    """
    Stores metadata for documents uploaded and linked to a complaint record.
    """

    __tablename__ = "uploaded_documents"

    __table_args__ = (
        Index("idx_uploaded_documents_complaint_id", "complaint_id"),
        Index("idx_uploaded_documents_created_at", "created_at"),
    )

    # ── Primary key ────────────────────────────────────────────────────────
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # ── Foreign key ────────────────────────────────────────────────────────
    complaint_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("complaints.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # ── Upload context ─────────────────────────────────────────────────────
    input_type: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        comment="pdf | image | email | text",
    )
    original_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    content_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    file_size_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    storage_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    extracted_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    # ── Timestamp ──────────────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # ── Relationship ───────────────────────────────────────────────────────
    complaint: Mapped["Complaint | None"] = relationship(
        "Complaint",
        back_populates="uploaded_documents",
    )

    def __repr__(self) -> str:
        return f"<UploadedDocument id={self.id} complaint_id={self.complaint_id}>"
