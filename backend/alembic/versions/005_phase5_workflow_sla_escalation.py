"""Add assignment, escalation, and audit_events table

Revision ID: 005
Revises: 004
Create Date: 2026-07-28 02:55:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add assignment columns to complaints
    op.add_column("complaints", sa.Column("assigned_to", sa.String(length=255), nullable=True))
    op.add_column("complaints", sa.Column("assigned_by", sa.String(length=255), nullable=True))
    op.add_column("complaints", sa.Column("assigned_at", sa.DateTime(timezone=True), nullable=True))

    # 2. Add escalation columns to complaints
    op.add_column("complaints", sa.Column("is_escalated", sa.Boolean(), server_default="false", nullable=False))
    op.add_column("complaints", sa.Column("escalated_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("complaints", sa.Column("escalation_reason", sa.Text(), nullable=True))

    op.create_index("idx_complaints_assigned_to", "complaints", ["assigned_to"])
    op.create_index("idx_complaints_is_escalated", "complaints", ["is_escalated"])

    # 3. Create audit_events table
    op.create_table(
        "audit_events",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("complaint_id", sa.UUID(), nullable=True),
        sa.Column("actor_email", sa.String(length=255), nullable=False, server_default="system@aiccms.local"),
        sa.Column("action_type", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("event_metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["complaint_id"], ["complaints.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_audit_events_complaint_id", "audit_events", ["complaint_id"])
    op.create_index("idx_audit_events_action_type", "audit_events", ["action_type"])
    op.create_index("idx_audit_events_created_at", "audit_events", ["created_at"])
    op.create_index("idx_audit_events_actor_email", "audit_events", ["actor_email"])


def downgrade() -> None:
    op.drop_index("idx_audit_events_actor_email", table_name="audit_events")
    op.drop_index("idx_audit_events_created_at", table_name="audit_events")
    op.drop_index("idx_audit_events_action_type", table_name="audit_events")
    op.drop_index("idx_audit_events_complaint_id", table_name="audit_events")
    op.drop_table("audit_events")

    op.drop_index("idx_complaints_is_escalated", table_name="complaints")
    op.drop_index("idx_complaints_assigned_to", table_name="complaints")
    op.drop_column("complaints", "escalation_reason")
    op.drop_column("complaints", "escalated_at")
    op.drop_column("complaints", "is_escalated")
    op.drop_column("complaints", "assigned_at")
    op.drop_column("complaints", "assigned_by")
    op.drop_column("complaints", "assigned_to")
