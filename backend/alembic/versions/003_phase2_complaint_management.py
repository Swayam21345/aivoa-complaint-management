"""Add complaint_history, reviewer_notes, uploaded_documents tables and soft delete to complaints

Revision ID: 003
Revises: 002
Create Date: 2026-07-27 20:45:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Alter complaints table: add priority, is_deleted, deleted_at
    op.add_column(
        "complaints",
        sa.Column("priority", sa.String(length=20), nullable=True, comment="Critical | High | Medium | Low"),
    )
    op.add_column(
        "complaints",
        sa.Column("is_deleted", sa.Boolean(), server_default="false", nullable=False),
    )
    op.add_column(
        "complaints",
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("idx_complaints_priority", "complaints", ["priority"])
    op.create_index("idx_complaints_is_deleted", "complaints", ["is_deleted"])

    # Update status check constraint
    op.drop_constraint("ck_complaints_status", "complaints", type_="check")
    op.create_check_constraint(
        "ck_complaints_status",
        "complaints",
        "status IN ('Draft', 'NEW', 'UNDER_REVIEW', 'IN_PROGRESS', 'WAITING_CUSTOMER', 'RESOLVED', 'CLOSED', 'REJECTED')",
    )

    # 2. Create complaint_history table
    op.create_table(
        "complaint_history",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("complaint_id", sa.UUID(), nullable=False),
        sa.Column("old_status", sa.String(length=30), nullable=True),
        sa.Column("new_status", sa.String(length=30), nullable=False),
        sa.Column("changed_by", sa.String(length=255), nullable=True),
        sa.Column("change_reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["complaint_id"], ["complaints.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_complaint_history_complaint_id", "complaint_history", ["complaint_id"])
    op.create_index("idx_complaint_history_created_at", "complaint_history", ["created_at"])

    # 3. Create reviewer_notes table
    op.create_table(
        "reviewer_notes",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("complaint_id", sa.UUID(), nullable=False),
        sa.Column("author", sa.String(length=255), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["complaint_id"], ["complaints.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_reviewer_notes_complaint_id", "reviewer_notes", ["complaint_id"])
    op.create_index("idx_reviewer_notes_created_at", "reviewer_notes", ["created_at"])

    # 4. Create uploaded_documents table
    op.create_table(
        "uploaded_documents",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("complaint_id", sa.UUID(), nullable=True),
        sa.Column("input_type", sa.String(length=10), nullable=False, comment="pdf | image | email | text"),
        sa.Column("original_filename", sa.String(length=255), nullable=True),
        sa.Column("content_type", sa.String(length=100), nullable=True),
        sa.Column("file_size_bytes", sa.BigInteger(), nullable=True),
        sa.Column("storage_path", sa.String(length=512), nullable=True),
        sa.Column("extracted_text", sa.Text(), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["complaint_id"], ["complaints.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_uploaded_documents_complaint_id", "uploaded_documents", ["complaint_id"])
    op.create_index("idx_uploaded_documents_created_at", "uploaded_documents", ["created_at"])


def downgrade() -> None:
    op.drop_index("idx_uploaded_documents_created_at", table_name="uploaded_documents")
    op.drop_index("idx_uploaded_documents_complaint_id", table_name="uploaded_documents")
    op.drop_table("uploaded_documents")

    op.drop_index("idx_reviewer_notes_created_at", table_name="reviewer_notes")
    op.drop_index("idx_reviewer_notes_complaint_id", table_name="reviewer_notes")
    op.drop_table("reviewer_notes")

    op.drop_index("idx_complaint_history_created_at", table_name="complaint_history")
    op.drop_index("idx_complaint_history_complaint_id", table_name="complaint_history")
    op.drop_table("complaint_history")

    op.drop_constraint("ck_complaints_status", "complaints", type_="check")
    op.create_check_constraint("ck_complaints_status", "complaints", "status IN ('Draft', 'Under Review', 'Closed')")
    op.drop_index("idx_complaints_is_deleted", table_name="complaints")
    op.drop_index("idx_complaints_priority", table_name="complaints")
    op.drop_column("complaints", "deleted_at")
    op.drop_column("complaints", "is_deleted")
    op.drop_column("complaints", "priority")
