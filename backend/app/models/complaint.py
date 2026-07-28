import uuid
from datetime import date, datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Index,
    String,
    Text,
    UUID,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.ai_analysis import AIAnalysis
    from app.models.audit_event import AuditEvent
    from app.models.capa import CAPARecord
    from app.models.complaint_history import ComplaintHistory
    from app.models.document import Document
    from app.models.electronic_signature import ElectronicSignature
    from app.models.rca import RCARecord
    from app.models.reviewer_note import ReviewerNote
    from app.models.uploaded_document import UploadedDocument





class Complaint(Base):
    """
    Core complaint record.

    complaint_id follows the format CC-YYYYMMDD-NNNN and is generated
    by the service layer (not the DB) to keep the logic portable.
    """

    __tablename__ = "complaints"

    __table_args__ = (
        CheckConstraint(
            "status IN ('Draft', 'NEW', 'TRIAGED', 'ASSIGNED', 'UNDER_INVESTIGATION', 'ROOT_CAUSE_IDENTIFIED', 'CAPA_IN_PROGRESS', 'QA_REVIEW', 'QA_APPROVED', 'CLOSED', 'REJECTED', 'ON_HOLD', 'CANCELLED', 'UNDER_REVIEW', 'IN_PROGRESS', 'WAITING_CUSTOMER', 'RESOLVED', 'Under Review', 'Closed')",
            name="ck_complaints_status",
        ),
        # Composite indexes for common query patterns
        Index("idx_complaints_status", "status"),
        Index("idx_complaints_risk_level", "risk_level"),
        Index("idx_complaints_priority", "priority"),
        Index("idx_complaints_category", "category"),
        Index("idx_complaints_created_at", "created_at"),
        Index("idx_complaints_is_deleted", "is_deleted"),
        Index("idx_complaints_assigned_to", "assigned_to"),
        Index("idx_complaints_is_escalated", "is_escalated"),
    )

    # ── Primary key ────────────────────────────────────────────────────────
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # ── Identifiers ────────────────────────────────────────────────────────
    complaint_id: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        unique=True,
        index=True,
        comment="Human-readable ID, e.g. CC-20260727-0001",
    )

    # ── Core fields ────────────────────────────────────────────────────────
    date_received: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="NEW",
        server_default="NEW",
    )
    priority: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="Critical | High | Medium | Low",
    )
    product_name: Mapped[str | None] = mapped_column(String(255))
    batch_number: Mapped[str | None] = mapped_column(String(100))
    customer_name: Mapped[str | None] = mapped_column(String(255))
    category: Mapped[str | None] = mapped_column(String(100))
    risk_level: Mapped[str | None] = mapped_column(
        String(10),
        comment="High | Medium | Low",
    )
    complaint_text: Mapped[str | None] = mapped_column(Text)
    reviewer_notes: Mapped[str | None] = mapped_column(Text)
    submitted_by: Mapped[str | None] = mapped_column(String(255))

    # ── SLA & Target Due Date ──────────────────────────────────────────────
    due_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Target SLA completion timestamp",
    )

    # ── Assignment fields ──────────────────────────────────────────────────
    assigned_to: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Investigator full_name or email",
    )
    assigned_by: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Assigner full_name or email",
    )
    assigned_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # ── Escalation fields ──────────────────────────────────────────────────
    is_escalated: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )
    escalated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    escalation_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # ── Soft delete ────────────────────────────────────────────────────────
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
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

    # ── Relationships ──────────────────────────────────────────────────────
    ai_analysis: Mapped["AIAnalysis | None"] = relationship(  # noqa: F821
        "AIAnalysis",
        back_populates="complaint",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    history: Mapped[list["ComplaintHistory"]] = relationship(
        "ComplaintHistory",
        back_populates="complaint",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="ComplaintHistory.created_at.asc()",
    )
    notes: Mapped[list["ReviewerNote"]] = relationship(
        "ReviewerNote",
        back_populates="complaint",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="ReviewerNote.created_at.desc()",
    )
    uploaded_documents: Mapped[list["UploadedDocument"]] = relationship(
        "UploadedDocument",
        back_populates="complaint",
        lazy="selectin",
    )
    audit_events: Mapped[list["AuditEvent"]] = relationship(
        "AuditEvent",
        back_populates="complaint",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="AuditEvent.created_at.asc()",
    )
    signatures: Mapped[list["ElectronicSignature"]] = relationship(
        "ElectronicSignature",
        back_populates="complaint",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="ElectronicSignature.signature_timestamp.asc()",
    )
    capas: Mapped[list["CAPARecord"]] = relationship(
        "CAPARecord",
        back_populates="complaint",
        cascade="all, delete-orphan",
        lazy="noload",
        order_by="CAPARecord.created_at.desc()",
    )
    rca_records: Mapped[list["RCARecord"]] = relationship(
        "RCARecord",
        back_populates="complaint",
        cascade="all, delete-orphan",
        lazy="noload",
        order_by="RCARecord.created_at.desc()",
    )




    def __repr__(self) -> str:
        return f"<Complaint {self.complaint_id} status={self.status}>"
