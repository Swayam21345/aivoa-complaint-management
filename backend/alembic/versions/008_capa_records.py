"""Create capa_records table for Phase 5.3 Enterprise CAPA Management

Revision ID: 008
Revises: 007
Create Date: 2026-07-28 11:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "008"
down_revision: Union[str, None] = "007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "capa_records",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("complaint_id", sa.UUID(), nullable=False),
        sa.Column("capa_number", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("root_cause", sa.Text(), nullable=True),
        sa.Column("corrective_action", sa.Text(), nullable=True),
        sa.Column("preventive_action", sa.Text(), nullable=True),
        sa.Column("owner", sa.String(length=255), nullable=True),
        sa.Column("reviewer", sa.String(length=255), nullable=True),
        sa.Column("effectiveness_check", sa.Text(), nullable=True),
        sa.Column("effectiveness_due_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("target_completion_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("priority", sa.String(length=20), nullable=False, server_default="Medium"),
        sa.Column("risk_level", sa.String(length=20), nullable=False, server_default="Medium"),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="OPEN"),
        sa.Column("created_by", sa.String(length=255), nullable=False),
        sa.Column("updated_by", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["complaint_id"], ["complaints.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("capa_number", name="uq_capa_number"),
    )
    op.create_index("idx_capa_complaint_id", "capa_records", ["complaint_id"])
    op.create_index("idx_capa_status", "capa_records", ["status"])
    op.create_index("idx_capa_owner", "capa_records", ["owner"])
    op.create_index("idx_capa_capa_number", "capa_records", ["capa_number"])


def downgrade() -> None:
    op.drop_index("idx_capa_capa_number", table_name="capa_records")
    op.drop_index("idx_capa_owner", table_name="capa_records")
    op.drop_index("idx_capa_status", table_name="capa_records")
    op.drop_index("idx_capa_complaint_id", table_name="capa_records")
    op.drop_table("capa_records")
