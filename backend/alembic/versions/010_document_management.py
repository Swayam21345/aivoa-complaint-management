"""Create document management tables (documents, document_versions, document_download_log)

Revision ID: 010
Revises: 009
Create Date: 2026-07-28 13:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "010"
down_revision: Union[str, None] = "009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. documents
    op.create_table(
        "documents",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("document_number", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category", sa.String(length=50), nullable=False, server_default="Complaint Evidence"),
        sa.Column("entity_type", sa.String(length=50), nullable=False, server_default="COMPLAINT"),
        sa.Column("entity_id", sa.UUID(), nullable=False),
        sa.Column("current_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="DRAFT"),
        sa.Column("approved_by", sa.String(length=255), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.String(length=255), nullable=False),
        sa.Column("updated_by", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("document_number", name="uq_document_number"),
    )
    op.create_index("idx_documents_entity", "documents", ["entity_type", "entity_id"])
    op.create_index("idx_documents_status", "documents", ["status"])
    op.create_index("idx_documents_category", "documents", ["category"])

    # 2. document_versions
    op.create_table(
        "document_versions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("document_id", sa.UUID(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("stored_filename", sa.String(length=255), nullable=False),
        sa.Column("mime_type", sa.String(length=100), nullable=False),
        sa.Column("size", sa.Integer(), nullable=False),
        sa.Column("sha256_hash", sa.String(length=64), nullable=False),
        sa.Column("storage_path", sa.String(length=500), nullable=False),
        sa.Column("uploaded_by", sa.String(length=255), nullable=False),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("change_summary", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_doc_versions_doc_id", "document_versions", ["document_id"])
    op.create_index("idx_doc_versions_hash", "document_versions", ["sha256_hash"])

    # 3. document_download_log
    op.create_table(
        "document_download_log",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("document_id", sa.UUID(), nullable=False),
        sa.Column("version_id", sa.UUID(), nullable=False),
        sa.Column("downloaded_by", sa.String(length=255), nullable=False),
        sa.Column("downloaded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["version_id"], ["document_versions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_doc_dl_log_doc_id", "document_download_log", ["document_id"])


def downgrade() -> None:
    op.drop_index("idx_doc_dl_log_doc_id", table_name="document_download_log")
    op.drop_table("document_download_log")

    op.drop_index("idx_doc_versions_hash", table_name="document_versions")
    op.drop_index("idx_doc_versions_doc_id", table_name="document_versions")
    op.drop_table("document_versions")

    op.drop_index("idx_documents_category", table_name="documents")
    op.drop_index("idx_documents_status", table_name="documents")
    op.drop_index("idx_documents_entity", table_name="documents")
    op.drop_table("documents")
