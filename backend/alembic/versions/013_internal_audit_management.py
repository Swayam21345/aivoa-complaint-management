"""create internal audit management and inspection readiness tables

Revision ID: 013_internal_audit_management
Revises: 012_supplier_quality_management
Create Date: 2026-07-28 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sm

# revision identifiers, used by Alembic.
revision: str = '013'
down_revision: Union[str, None] = '012'
branch_labels: Union[Sequence[str], None] = None
depends_on: Union[Sequence[str], None] = None


def upgrade() -> None:
    # 1. internal_audits
    op.create_table(
        'internal_audits',
        sm.Column('id', sm.UUID(), primary_key=True),
        sm.Column('audit_number', sm.String(50), nullable=False, unique=True, index=True),
        sm.Column('title', sm.String(255), nullable=False),
        sm.Column('audit_type', sm.String(100), nullable=False, server_default='INTERNAL_SOP'),
        sm.Column('scope', sm.Text(), nullable=False),
        sm.Column('lead_auditor', sm.String(255), nullable=False),
        sm.Column('audit_team', sm.Text(), nullable=True),
        sm.Column('department', sm.String(100), nullable=False, server_default='QUALITY_ASSURANCE'),
        sm.Column('scheduled_start_date', sm.DateTime(timezone=True), nullable=False),
        sm.Column('scheduled_end_date', sm.DateTime(timezone=True), nullable=False),
        sm.Column('actual_start_date', sm.DateTime(timezone=True), nullable=True),
        sm.Column('actual_end_date', sm.DateTime(timezone=True), nullable=True),
        sm.Column('status', sm.String(50), nullable=False, server_default='PLANNED'),
        sm.Column('conclusion', sm.Text(), nullable=True),
        sm.Column('approved_by', sm.String(255), nullable=True),
        sm.Column('approved_at', sm.DateTime(timezone=True), nullable=True),
        sm.Column('created_by', sm.String(255), nullable=False),
        sm.Column('updated_by', sm.String(255), nullable=False),
        sm.Column('created_at', sm.DateTime(timezone=True), nullable=False),
        sm.Column('updated_at', sm.DateTime(timezone=True), nullable=False),
    )

    # 2. audit_checklists
    op.create_table(
        'audit_checklists',
        sm.Column('id', sm.UUID(), primary_key=True),
        sm.Column('audit_id', sm.UUID(), sm.ForeignKey('internal_audits.id', ondelete='CASCADE'), nullable=False, index=True),
        sm.Column('section', sm.String(100), nullable=False),
        sm.Column('requirement', sm.String(255), nullable=False),
        sm.Column('question', sm.Text(), nullable=False),
        sm.Column('compliance_status', sm.String(50), nullable=False, server_default='COMPLIANT'),
        sm.Column('comments', sm.Text(), nullable=True),
        sm.Column('evidence_summary', sm.Text(), nullable=True),
    )

    # 3. audit_findings
    op.create_table(
        'audit_findings',
        sm.Column('id', sm.UUID(), primary_key=True),
        sm.Column('audit_id', sm.UUID(), sm.ForeignKey('internal_audits.id', ondelete='CASCADE'), nullable=False, index=True),
        sm.Column('finding_number', sm.String(50), nullable=False, unique=True, index=True),
        sm.Column('category', sm.String(50), nullable=False, server_default='OBSERVATION'),
        sm.Column('description', sm.Text(), nullable=False),
        sm.Column('clause_reference', sm.String(100), nullable=True),
        sm.Column('capa_id', sm.UUID(), sm.ForeignKey('capa_records.id', ondelete='SET NULL'), nullable=True, index=True),
        sm.Column('status', sm.String(50), nullable=False, server_default='OPEN'),
        sm.Column('created_at', sm.DateTime(timezone=True), nullable=False),
    )

    # 4. inspection_readiness_packages
    op.create_table(
        'inspection_readiness_packages',
        sm.Column('id', sm.UUID(), primary_key=True),
        sm.Column('package_number', sm.String(50), nullable=False, unique=True, index=True),
        sm.Column('agency', sm.String(100), nullable=False, server_default='FDA'),
        sm.Column('title', sm.String(255), nullable=False),
        sm.Column('description', sm.Text(), nullable=False),
        sm.Column('readiness_score', sm.Float(), nullable=False, server_default='100.0'),
        sm.Column('status', sm.String(50), nullable=False, server_default='READY'),
        sm.Column('created_by', sm.String(255), nullable=False),
        sm.Column('updated_by', sm.String(255), nullable=False),
        sm.Column('created_at', sm.DateTime(timezone=True), nullable=False),
        sm.Column('updated_at', sm.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('inspection_readiness_packages')
    op.drop_table('audit_findings')
    op.drop_table('audit_checklists')
    op.drop_table('internal_audits')
