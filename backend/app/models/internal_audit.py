import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.capa import CAPARecord


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class InternalAudit(Base):
    __tablename__ = "internal_audits"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, index=True
    )
    audit_number: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    audit_type: Mapped[str] = mapped_column(
        String(100), default="INTERNAL_SOP"
    )  # INTERNAL_SOP, REGULATORY_PREP, PROCESS, QUALITY_SYSTEM
    scope: Mapped[str] = mapped_column(Text, nullable=False)
    lead_auditor: Mapped[str] = mapped_column(String(255), nullable=False)
    audit_team: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    department: Mapped[str] = mapped_column(
        String(100), default="QUALITY_ASSURANCE"
    )

    scheduled_start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    scheduled_end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    actual_start_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    actual_end_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    status: Mapped[str] = mapped_column(
        String(50), default="PLANNED"
    )  # PLANNED, IN_PROGRESS, REPORT_PENDING, CLOSED, CANCELLED
    conclusion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    approved_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    created_by: Mapped[str] = mapped_column(String(255), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=now_utc
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=now_utc, onupdate=now_utc
    )

    checklists: Mapped[List["AuditChecklist"]] = relationship(
        "AuditChecklist", back_populates="audit", cascade="all, delete-orphan", lazy="noload"
    )
    findings: Mapped[List["AuditFinding"]] = relationship(
        "AuditFinding", back_populates="audit", cascade="all, delete-orphan", lazy="noload"
    )


class AuditChecklist(Base):
    __tablename__ = "audit_checklists"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, index=True
    )
    audit_id: Mapped[UUID] = mapped_column(
        ForeignKey("internal_audits.id", ondelete="CASCADE"), index=True, nullable=False
    )
    section: Mapped[str] = mapped_column(String(100), nullable=False)
    requirement: Mapped[str] = mapped_column(String(255), nullable=False)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    compliance_status: Mapped[str] = mapped_column(
        String(50), default="COMPLIANT"
    )  # COMPLIANT, NON_COMPLIANT, OBSERVATION, NOT_APPLICABLE
    comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    evidence_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    audit: Mapped["InternalAudit"] = relationship("InternalAudit", back_populates="checklists", lazy="noload")


class AuditFinding(Base):
    __tablename__ = "audit_findings"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, index=True
    )
    audit_id: Mapped[UUID] = mapped_column(
        ForeignKey("internal_audits.id", ondelete="CASCADE"), index=True, nullable=False
    )
    finding_number: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )
    category: Mapped[str] = mapped_column(
        String(50), default="OBSERVATION"
    )  # CRITICAL_NC, MAJOR_NC, MINOR_NC, OBSERVATION, RECOMMENDATION
    description: Mapped[str] = mapped_column(Text, nullable=False)
    clause_reference: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    capa_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("capa_records.id", ondelete="SET NULL"), index=True, nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(50), default="OPEN"
    )  # OPEN, CAPA_ASSIGNED, RESOLVED, CLOSED
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=now_utc
    )

    audit: Mapped["InternalAudit"] = relationship("InternalAudit", back_populates="findings", lazy="noload")
    capa: Mapped[Optional["CAPARecord"]] = relationship("CAPARecord", lazy="noload")


class InspectionReadinessPackage(Base):
    __tablename__ = "inspection_readiness_packages"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, index=True
    )
    package_number: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )
    agency: Mapped[str] = mapped_column(String(100), default="FDA")  # FDA, EMA, ISO_NOTIFIED_BODY, HEALTH_CANADA
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    readiness_score: Mapped[float] = mapped_column(Float, default=100.0)
    status: Mapped[str] = mapped_column(String(50), default="READY")  # DRAFT, READY, UNDER_REVIEW, ARCHIVED

    created_by: Mapped[str] = mapped_column(String(255), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=now_utc
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=now_utc, onupdate=now_utc
    )
