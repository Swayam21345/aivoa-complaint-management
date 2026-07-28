"""Initial schema — complaints and ai_analysis tables.

Revision ID: 001
Revises:
Create Date: 2026-07-27
"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# ── Revision identifiers ──────────────────────────────────────────────────────
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# ─── Upgrade ──────────────────────────────────────────────────────────────────

def upgrade() -> None:
    # ── complaints ────────────────────────────────────────────────────────
    op.create_table(
        "complaints",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("complaint_id", sa.String(20), nullable=False),
        sa.Column("date_received", sa.Date(), nullable=False),
        sa.Column(
            "status",
            sa.String(20),
            nullable=False,
            server_default="Draft",
        ),
        sa.Column("product_name", sa.String(255), nullable=True),
        sa.Column("batch_number", sa.String(100), nullable=True),
        sa.Column("customer_name", sa.String(255), nullable=True),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("risk_level", sa.String(10), nullable=True),
        sa.Column("complaint_text", sa.Text(), nullable=True),
        sa.Column("reviewer_notes", sa.Text(), nullable=True),
        sa.Column("submitted_by", sa.String(255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint(
            "status IN ('Draft', 'Under Review', 'Closed')",
            name="ck_complaints_status",
        ),
        sa.UniqueConstraint("complaint_id", name="uq_complaints_complaint_id"),
    )

    # Indexes
    op.create_index("idx_complaints_complaint_id", "complaints", ["complaint_id"])
    op.create_index("idx_complaints_status", "complaints", ["status"])
    op.create_index("idx_complaints_risk_level", "complaints", ["risk_level"])
    op.create_index("idx_complaints_category", "complaints", ["category"])
    op.create_index(
        "idx_complaints_created_at",
        "complaints",
        [sa.text("created_at DESC")],
    )

    # ── ai_analysis ───────────────────────────────────────────────────────
    op.create_table(
        "ai_analysis",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "complaint_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("complaints.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("complaint_summary", sa.Text(), nullable=True),
        sa.Column("extracted_product_name", sa.String(255), nullable=True),
        sa.Column("extracted_batch_number", sa.String(100), nullable=True),
        sa.Column("extracted_customer_name", sa.String(255), nullable=True),
        sa.Column("extracted_category", sa.String(100), nullable=True),
        sa.Column("risk_level", sa.String(10), nullable=True),
        sa.Column("root_cause_recommendation", sa.Text(), nullable=True),
        sa.Column("capa_recommendation", sa.Text(), nullable=True),
        sa.Column(
            "raw_llm_response",
            sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql"),
            nullable=True,
        ),
        sa.Column("processing_time_ms", sa.Integer(), nullable=True),
        sa.Column(
            "model_used",
            sa.String(100),
            nullable=True,
            server_default="gemma2-9b-it",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    op.create_index(
        "idx_ai_analysis_complaint_id", "ai_analysis", ["complaint_id"]
    )

    # ── complaint_seq ─────────────────────────────────────────────────────
    # Used by the service layer to generate CC-YYYYMMDD-NNNN identifiers.
    op.execute("CREATE SEQUENCE IF NOT EXISTS complaint_seq START 1 INCREMENT 1")


# ─── Downgrade ────────────────────────────────────────────────────────────────

def downgrade() -> None:
    op.execute("DROP SEQUENCE IF EXISTS complaint_seq")
    op.drop_table("ai_analysis")
    op.drop_table("complaints")
