"""Create electronic_signatures table for 21 CFR Part 11 Compliance

Revision ID: 007
Revises: 006
Create Date: 2026-07-28 04:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "007"
down_revision: Union[str, None] = "006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "electronic_signatures",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("complaint_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("status_before", sa.String(length=30), nullable=False),
        sa.Column("status_after", sa.String(length=30), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("signature_timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("signature_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["complaint_id"], ["complaints.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_signatures_complaint_id", "electronic_signatures", ["complaint_id"])
    op.create_index("idx_signatures_user_id", "electronic_signatures", ["user_id"])
    op.create_index("idx_signatures_timestamp", "electronic_signatures", ["signature_timestamp"])


def downgrade() -> None:
    op.drop_index("idx_signatures_timestamp", table_name="electronic_signatures")
    op.drop_index("idx_signatures_user_id", table_name="electronic_signatures")
    op.drop_index("idx_signatures_complaint_id", table_name="electronic_signatures")
    op.drop_table("electronic_signatures")
