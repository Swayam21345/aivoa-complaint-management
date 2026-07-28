import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.capa import CAPARecord
    from app.models.complaint import Complaint
    from app.models.document import Document


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class Supplier(Base):
    __tablename__ = "suppliers"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, index=True
    )
    supplier_number: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )
    supplier_name: Mapped[str] = mapped_column(String(255), nullable=False)
    supplier_type: Mapped[str] = mapped_column(
        String(100), default="RAW_MATERIAL"
    )  # RAW_MATERIAL, COMPONENT, CONTRACT_MANUFACTURER, SERVICE, PACKAGING
    category: Mapped[str] = mapped_column(String(100), default="PRIMARY")
    status: Mapped[str] = mapped_column(
        String(50), default="PENDING_QUALIFICATION"
    )  # PENDING_QUALIFICATION, APPROVED, CONDITIONAL, DISQUALIFIED
    risk_level: Mapped[str] = mapped_column(
        String(50), default="MEDIUM"
    )  # LOW, MEDIUM, HIGH, CRITICAL

    address: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    zip_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    approval_status: Mapped[str] = mapped_column(String(50), default="PENDING")
    approved_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    created_by: Mapped[str] = mapped_column(String(255), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=now_utc
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=now_utc, onupdate=now_utc
    )

    # Relationships using lazy="noload"
    contacts: Mapped[List["SupplierContact"]] = relationship(
        "SupplierContact", back_populates="supplier", cascade="all, delete-orphan", lazy="noload"
    )
    documents: Mapped[List["SupplierDocument"]] = relationship(
        "SupplierDocument", back_populates="supplier", cascade="all, delete-orphan", lazy="noload"
    )
    audits: Mapped[List["SupplierAudit"]] = relationship(
        "SupplierAudit", back_populates="supplier", cascade="all, delete-orphan", lazy="noload"
    )
    scorecards: Mapped[List["SupplierScorecard"]] = relationship(
        "SupplierScorecard", back_populates="supplier", cascade="all, delete-orphan", lazy="noload"
    )
    nonconformances: Mapped[List["SupplierNonconformance"]] = relationship(
        "SupplierNonconformance", back_populates="supplier", cascade="all, delete-orphan", lazy="noload"
    )
    corrective_actions: Mapped[List["SupplierCorrectiveAction"]] = relationship(
        "SupplierCorrectiveAction", back_populates="supplier", cascade="all, delete-orphan", lazy="noload"
    )


class SupplierContact(Base):
    __tablename__ = "supplier_contacts"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, index=True
    )
    supplier_id: Mapped[UUID] = mapped_column(
        ForeignKey("suppliers.id", ondelete="CASCADE"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    title: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)

    supplier: Mapped["Supplier"] = relationship("Supplier", back_populates="contacts", lazy="noload")


class SupplierDocument(Base):
    __tablename__ = "supplier_documents"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, index=True
    )
    supplier_id: Mapped[UUID] = mapped_column(
        ForeignKey("suppliers.id", ondelete="CASCADE"), index=True, nullable=False
    )
    document_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("documents.id", ondelete="SET NULL"), index=True, nullable=True
    )
    document_type: Mapped[str] = mapped_column(String(100), nullable=False)  # ISO_CERTIFICATE, QUALITY_AGREEMENT, AUDIT_REPORT, COA
    valid_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    supplier: Mapped["Supplier"] = relationship("Supplier", back_populates="documents", lazy="noload")
    document: Mapped[Optional["Document"]] = relationship("Document", lazy="noload")


class SupplierAudit(Base):
    __tablename__ = "supplier_audits"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, index=True
    )
    supplier_id: Mapped[UUID] = mapped_column(
        ForeignKey("suppliers.id", ondelete="CASCADE"), index=True, nullable=False
    )
    audit_number: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )
    audit_type: Mapped[str] = mapped_column(
        String(50), default="QUALIFICATION"
    )  # QUALIFICATION, PERIODIC, FOR_CAUSE
    scheduled_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    auditor: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(
        String(50), default="SCHEDULED"
    )  # SCHEDULED, IN_PROGRESS, COMPLETED, CANCELLED
    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    findings_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    supplier: Mapped["Supplier"] = relationship("Supplier", back_populates="audits", lazy="noload")


class SupplierScorecard(Base):
    __tablename__ = "supplier_scorecards"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, index=True
    )
    supplier_id: Mapped[UUID] = mapped_column(
        ForeignKey("suppliers.id", ondelete="CASCADE"), index=True, nullable=False
    )
    period: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g. 2026-Q1
    quality_score: Mapped[float] = mapped_column(Float, default=100.0)
    delivery_score: Mapped[float] = mapped_column(Float, default=100.0)
    compliance_score: Mapped[float] = mapped_column(Float, default=100.0)
    overall_score: Mapped[float] = mapped_column(Float, default=100.0)
    grade: Mapped[str] = mapped_column(String(10), default="A")  # A, B, C, D, F
    evaluated_by: Mapped[str] = mapped_column(String(255), nullable=False)
    evaluated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=now_utc
    )

    supplier: Mapped["Supplier"] = relationship("Supplier", back_populates="scorecards", lazy="noload")


class SupplierNonconformance(Base):
    __tablename__ = "supplier_nonconformances"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, index=True
    )
    supplier_id: Mapped[UUID] = mapped_column(
        ForeignKey("suppliers.id", ondelete="CASCADE"), index=True, nullable=False
    )
    complaint_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("complaints.id", ondelete="SET NULL"), index=True, nullable=True
    )
    ncr_number: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(
        String(50), default="MEDIUM"
    )  # MINOR, MAJOR, CRITICAL
    status: Mapped[str] = mapped_column(
        String(50), default="OPEN"
    )  # OPEN, INVESTIGATING, CLOSED
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=now_utc
    )

    supplier: Mapped["Supplier"] = relationship("Supplier", back_populates="nonconformances", lazy="noload")
    complaint: Mapped[Optional["Complaint"]] = relationship("Complaint", lazy="noload")


class SupplierCorrectiveAction(Base):
    __tablename__ = "supplier_corrective_actions"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, index=True
    )
    supplier_id: Mapped[UUID] = mapped_column(
        ForeignKey("suppliers.id", ondelete="CASCADE"), index=True, nullable=False
    )
    capa_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("capa_records.id", ondelete="SET NULL"), index=True, nullable=True
    )
    action_number: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )
    action_plan: Mapped[str] = mapped_column(Text, nullable=False)
    owner: Mapped[str] = mapped_column(String(255), nullable=False)
    due_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(
        String(50), default="OPEN"
    )  # OPEN, IN_PROGRESS, COMPLETED
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    supplier: Mapped["Supplier"] = relationship("Supplier", back_populates="corrective_actions", lazy="noload")
    capa: Mapped[Optional["CAPARecord"]] = relationship("CAPARecord", lazy="noload")
