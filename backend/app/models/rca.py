from datetime import datetime, timezone
import uuid
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.complaint import Complaint


class RCARecord(Base):
    """
    SQLAlchemy model representing a Root Cause Analysis (RCA) investigation record.
    Tracks 5 Whys analysis, 6M Fishbone categories, primary root cause, and QA approval status.
    """

    __tablename__ = "rca_records"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    complaint_id: Mapped[UUID] = mapped_column(
        ForeignKey("complaints.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    rca_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
    )
    methodology: Mapped[str] = mapped_column(
        String(30),
        default="HYBRID",
        nullable=False,
    )
    primary_root_cause: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    root_cause_category: Mapped[str] = mapped_column(
        String(50),
        default="Equipment Failure",
        index=True,
        nullable=False,
    )
    five_whys_json: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    fishbone_json: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    contributing_factors: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
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
    complaint: Mapped["Complaint"] = relationship(
        "Complaint",
        back_populates="rca_records",
        lazy="selectin",
    )
    fmea_items: Mapped[List["FMEAAssessment"]] = relationship(
        "FMEAAssessment",
        back_populates="rca",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="FMEAAssessment.rpn.desc()",
    )

    def __repr__(self) -> str:
        return f"<RCARecord(id={self.id}, rca_number='{self.rca_number}', status='{self.status}')>"


class FMEAAssessment(Base):
    """
    SQLAlchemy model representing a Failure Mode and Effects Analysis (FMEA) line item.
    Calculates Risk Priority Number (RPN = Severity * Occurrence * Detection).
    """

    __tablename__ = "fmea_assessments"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    rca_id: Mapped[UUID] = mapped_column(
        ForeignKey("rca_records.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    complaint_id: Mapped[UUID] = mapped_column(
        ForeignKey("complaints.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    failure_mode: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    effect_of_failure: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    severity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    occurrence: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    detection: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    rpn: Mapped[int] = mapped_column(
        Integer,
        index=True,
        nullable=False,
    )
    risk_class: Mapped[str] = mapped_column(
        String(20),
        default="Medium",
        nullable=False,
    )
    recommended_action: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    action_taken: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    revised_severity: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )
    revised_occurrence: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )
    revised_detection: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )
    revised_rpn: Mapped[Optional[int]] = mapped_column(
        Integer,
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
    rca: Mapped["RCARecord"] = relationship(
        "RCARecord",
        back_populates="fmea_items",
        lazy="noload",
    )

    def __repr__(self) -> str:
        return f"<FMEAAssessment(id={self.id}, failure_mode='{self.failure_mode}', RPN={self.rpn})>"
