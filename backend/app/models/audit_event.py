import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Dict, Optional

from sqlalchemy import DateTime, Index, String, Text, UUID, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.complaint import Complaint


class AuditEvent(Base):
    """
    Immutable audit event record for regulatory compliance (21 CFR Part 11).
    Actions recorded:
      Created, Assigned, Status Changed, AI Analysis, CAPA Updated, PDF Exported, Login, Logout.
    """

    __tablename__ = "audit_events"

    __table_args__ = (
        Index("idx_audit_events_complaint_id", "complaint_id"),
        Index("idx_audit_events_action_type", "action_type"),
        Index("idx_audit_events_created_at", "created_at"),
        Index("idx_audit_events_actor_email", "actor_email"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    complaint_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("complaints.id", ondelete="CASCADE"),
        nullable=True,
    )

    actor_email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="system@aiccms.local",
    )

    action_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Created | Assigned | Status Changed | AI Analysis | CAPA Updated | PDF Exported | Login | Logout",
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    event_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    complaint: Mapped[Optional["Complaint"]] = relationship(
        "Complaint",
        back_populates="audit_events",
    )

    def __repr__(self) -> str:
        return f"<AuditEvent action={self.action_type} actor={self.actor_email} created_at={self.created_at}>"
