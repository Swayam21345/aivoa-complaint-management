"""Add upload_records table for document ingestion audit trail.

Revision ID: 002
Revises: 001
Create Date: 2026-07-27
"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# ── Revision identifiers ──────────────────────────────────────────────────────
revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# ─── Upgrade ──────────────────────────────────────────────────────────────────

def upgrade() -> None:
    op.create_table(
        "upload_records",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        # ── Upload context ─────────────────────────────────────────────────
        sa.Column(
            "input_type",
            sa.String(10),
            nullable=False,
            comment="pdf | image | email | text",
        ),
        sa.Column("original_filename", sa.String(255), nullable=True),
        sa.Column("content_type", sa.String(100), nullable=True),
        sa.Column(
            "file_size_bytes",
            sa.BigInteger(),
            nullable=True,
        ),
        sa.Column("storage_path", sa.String(512), nullable=True),
        # ── Extraction result ──────────────────────────────────────────────
        sa.Column("extracted_text", sa.Text(), nullable=True),
        sa.Column(
            "extraction_status",
            sa.String(20),
            nullable=False,
            server_default="success",
        ),
        sa.Column("extraction_error", sa.Text(), nullable=True),
        # ── Timestamp ──────────────────────────────────────────────────────
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    op.create_index(
        "idx_upload_records_input_type", "upload_records", ["input_type"]
    )
    op.create_index(
        "idx_upload_records_created_at", "upload_records", ["created_at"]
    )


# ─── Downgrade ────────────────────────────────────────────────────────────────

def downgrade() -> None:
    op.drop_table("upload_records")
