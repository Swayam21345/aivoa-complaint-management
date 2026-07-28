import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, UUID
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import Any, TYPE_CHECKING

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.complaint import Complaint


class AIAnalysis(Base):
    """
    Stores the structured output of the LangGraph AI workflow,
    linked one-to-one with a Complaint record.

    raw_llm_response persists the full LLM JSON for audit and debugging.
    """

    __tablename__ = "ai_analysis"

    # ── Primary key ────────────────────────────────────────────────────────
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # ── Foreign key (1-to-1) ───────────────────────────────────────────────
    complaint_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("complaints.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    # ── AI-extracted fields ────────────────────────────────────────────────
    complaint_summary: Mapped[str | None] = mapped_column(Text)
    extracted_product_name: Mapped[str | None] = mapped_column(String(255))
    extracted_batch_number: Mapped[str | None] = mapped_column(String(100))
    extracted_customer_name: Mapped[str | None] = mapped_column(String(255))
    extracted_category: Mapped[str | None] = mapped_column(String(100))
    risk_level: Mapped[str | None] = mapped_column(
        String(10),
        comment="High | Medium | Low",
    )
    root_cause_recommendation: Mapped[str | None] = mapped_column(Text)
    capa_recommendation: Mapped[str | None] = mapped_column(Text)

    # ── Audit / meta ───────────────────────────────────────────────────────
    raw_llm_response: Mapped[dict[str, Any] | None] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=True,
        comment="Full LLM JSON response preserved for auditability",
    )
    processing_time_ms: Mapped[int | None] = mapped_column(
        Integer,
        comment="Wall-clock time for the complete AI pipeline in milliseconds",
    )
    model_used: Mapped[str | None] = mapped_column(
        String(100),
        default="gemma2-9b-it",
        server_default="gemma2-9b-it",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # ── Relationship ───────────────────────────────────────────────────────
    complaint: Mapped["Complaint"] = relationship(  # noqa: F821
        "Complaint",
        back_populates="ai_analysis",
    )

    def __repr__(self) -> str:
        return f"<AIAnalysis complaint_id={self.complaint_id} risk={self.risk_level}>"
