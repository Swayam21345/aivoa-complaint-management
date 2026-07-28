"""Create rca_records and fmea_assessments tables for Phase 5.4 RCA & FMEA Management

Revision ID: 009
Revises: 008
Create Date: 2026-07-28 12:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "009"
down_revision: Union[str, None] = "008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. rca_records
    op.create_table(
        "rca_records",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("complaint_id", sa.UUID(), nullable=False),
        sa.Column("rca_number", sa.String(length=50), nullable=False),
        sa.Column("methodology", sa.String(length=30), nullable=False, server_default="HYBRID"),
        sa.Column("primary_root_cause", sa.Text(), nullable=False),
        sa.Column("root_cause_category", sa.String(length=50), nullable=False, server_default="Equipment Failure"),
        sa.Column("five_whys_json", sa.Text(), nullable=True),
        sa.Column("fishbone_json", sa.Text(), nullable=True),
        sa.Column("contributing_factors", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="DRAFT"),
        sa.Column("approved_by", sa.String(length=255), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.String(length=255), nullable=False),
        sa.Column("updated_by", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["complaint_id"], ["complaints.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("rca_number", name="uq_rca_number"),
    )
    op.create_index("idx_rca_complaint_id", "rca_records", ["complaint_id"])
    op.create_index("idx_rca_status", "rca_records", ["status"])
    op.create_index("idx_rca_category", "rca_records", ["root_cause_category"])

    # 2. fmea_assessments
    op.create_table(
        "fmea_assessments",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("rca_id", sa.UUID(), nullable=False),
        sa.Column("complaint_id", sa.UUID(), nullable=False),
        sa.Column("failure_mode", sa.String(length=255), nullable=False),
        sa.Column("effect_of_failure", sa.Text(), nullable=False),
        sa.Column("severity", sa.Integer(), nullable=False),
        sa.Column("occurrence", sa.Integer(), nullable=False),
        sa.Column("detection", sa.Integer(), nullable=False),
        sa.Column("rpn", sa.Integer(), nullable=False),
        sa.Column("risk_class", sa.String(length=20), nullable=False, server_default="Medium"),
        sa.Column("recommended_action", sa.Text(), nullable=True),
        sa.Column("action_taken", sa.Text(), nullable=True),
        sa.Column("revised_severity", sa.Integer(), nullable=True),
        sa.Column("revised_occurrence", sa.Integer(), nullable=True),
        sa.Column("revised_detection", sa.Integer(), nullable=True),
        sa.Column("revised_rpn", sa.Integer(), nullable=True),
        sa.Column("created_by", sa.String(length=255), nullable=False),
        sa.Column("updated_by", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["rca_id"], ["rca_records.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["complaint_id"], ["complaints.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_fmea_rca_id", "fmea_assessments", ["rca_id"])
    op.create_index("idx_fmea_complaint_id", "fmea_assessments", ["complaint_id"])
    op.create_index("idx_fmea_rpn", "fmea_assessments", ["rpn"])


def downgrade() -> None:
    op.drop_index("idx_fmea_rpn", table_name="fmea_assessments")
    op.drop_index("idx_fmea_complaint_id", table_name="fmea_assessments")
    op.drop_index("idx_fmea_rca_id", table_name="fmea_assessments")
    op.drop_table("fmea_assessments")

    op.drop_index("idx_rca_category", table_name="rca_records")
    op.drop_index("idx_rca_status", table_name="rca_records")
    op.drop_index("idx_rca_complaint_id", table_name="rca_records")
    op.drop_table("rca_records")
