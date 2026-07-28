import uuid
from datetime import datetime, timezone

from sqlalchemy import BigInteger, DateTime, Index, String, Text, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class UploadRecord(Base):
    """
    Stores metadata for every file uploaded to the system.

    One UploadRecord is created per upload request (before a Complaint is
    submitted). It captures the original filename, MIME type, file size,
    storage path, input type, and the extracted plain text — providing a
    full audit trail of every ingested document independent of whether the
    user goes on to submit a complaint form.
    """

    __tablename__ = "upload_records"

    __table_args__ = (
        Index("idx_upload_records_input_type", "input_type"),
        Index("idx_upload_records_created_at", "created_at"),
    )

    # ── Primary key ────────────────────────────────────────────────────────
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # ── Upload context ─────────────────────────────────────────────────────
    input_type: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        comment="pdf | image | email | text",
    )
    original_filename: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Original filename as provided by the client",
    )
    content_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="MIME type of the uploaded file",
    )
    file_size_bytes: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
        comment="Size of the uploaded file in bytes",
    )
    storage_path: Mapped[str | None] = mapped_column(
        String(512),
        nullable=True,
        comment="Relative path where the file is stored on disk",
    )

    # ── Extraction result ──────────────────────────────────────────────────
    extracted_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Plain text extracted from the document",
    )
    extraction_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="success",
        server_default="success",
        comment="success | failed | partial",
    )
    extraction_error: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Error message if extraction failed or was partial",
    )

    # ── Timestamp ──────────────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return (
            f"<UploadRecord id={self.id} "
            f"type={self.input_type} "
            f"status={self.extraction_status}>"
        )
