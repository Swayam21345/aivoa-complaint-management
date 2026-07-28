from datetime import datetime, timezone
import uuid
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.capa import CAPARecord
    from app.models.complaint import Complaint
    from app.models.rca import RCARecord


class Document(Base):
    """
    SQLAlchemy model representing a controlled document / evidence record.
    Supports linking to Complaints, RCAs, and CAPAs across multiple categories.
    """

    __tablename__ = "documents"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    document_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    category: Mapped[str] = mapped_column(
        String(50),
        default="Complaint Evidence",
        index=True,
        nullable=False,
    )
    entity_type: Mapped[str] = mapped_column(
        String(50),
        default="COMPLAINT",
        index=True,
        nullable=False,
    )
    entity_id: Mapped[UUID] = mapped_column(
        index=True,
        nullable=False,
    )

    current_version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(30),
        default="DRAFT",
        index=True,
        nullable=False,
    )
    approved_by: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    approved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_by: Mapped[str] = mapped_column(
        String(255),
        default="system@aiccms.local",
        nullable=False,
    )
    updated_by: Mapped[str] = mapped_column(
        String(255),
        default="system@aiccms.local",
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    versions: Mapped[List["DocumentVersion"]] = relationship(
        "DocumentVersion",
        back_populates="document",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="DocumentVersion.version.desc()",
    )
    download_logs: Mapped[List["DocumentDownloadLog"]] = relationship(
        "DocumentDownloadLog",
        back_populates="document",
        cascade="all, delete-orphan",
        lazy="noload",
    )

    def __repr__(self) -> str:
        return f"<Document(id={self.id}, number='{self.document_number}', title='{self.title}')>"


class DocumentVersion(Base):
    """
    SQLAlchemy model representing an immutable version file entry.
    Contains stored filename, mime type, size, storage path, and SHA-256 hash.
    """

    __tablename__ = "document_versions"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    document_id: Mapped[UUID] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    original_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    stored_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    mime_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    size: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    sha256_hash: Mapped[str] = mapped_column(
        String(64),
        index=True,
        nullable=False,
    )
    storage_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )
    uploaded_by: Mapped[str] = mapped_column(
        String(255),
        default="system@aiccms.local",
        nullable=False,
    )
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    change_summary: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # Relationships
    document: Mapped["Document"] = relationship(
        "Document",
        back_populates="versions",
        lazy="noload",
    )

    def __repr__(self) -> str:
        return f"<DocumentVersion(id={self.id}, version={self.version}, file='{self.original_filename}')>"


class DocumentDownloadLog(Base):
    """
    SQLAlchemy model tracking document downloads for audit compliance.
    """

    __tablename__ = "document_download_log"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    document_id: Mapped[UUID] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version_id: Mapped[UUID] = mapped_column(
        ForeignKey("document_versions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    downloaded_by: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    downloaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45),
        nullable=True,
    )
    user_agent: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )

    # Relationships
    document: Mapped["Document"] = relationship(
        "Document",
        back_populates="download_logs",
        lazy="noload",
    )

    def __repr__(self) -> str:
        return f"<DocumentDownloadLog(id={self.id}, user='{self.downloaded_by}')>"
