from datetime import datetime, timezone
import uuid
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.complaint import Complaint


class CAPARecord(Base):
    """
    SQLAlchemy model representing a Corrective and Preventive Action (CAPA) record.
    Tracks root cause, corrective actions, preventive actions, implementation ownership,
    effectiveness reviews, and workflow status.
    """

    __tablename__ = "capa_records"

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
    capa_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    root_cause: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    corrective_action: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    preventive_action: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    owner: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )
    reviewer: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    effectiveness_check: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    effectiveness_due_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    target_completion_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    completed_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    priority: Mapped[str] = mapped_column(
        String(20),
        default="Medium",
        nullable=False,
    )
    risk_level: Mapped[str] = mapped_column(
        String(20),
        default="Medium",
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(30),
        default="OPEN",
        index=True,
        nullable=False,
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
        back_populates="capas",
        lazy="selectin",
    )


    def __repr__(self) -> str:
        return f"<CAPARecord(id={self.id}, capa_number='{self.capa_number}', status='{self.status}')>"
