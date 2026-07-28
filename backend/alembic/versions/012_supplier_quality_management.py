"""create supplier quality management tables

Revision ID: 012_supplier_quality_management
Revises: 011_training_management
Create Date: 2026-07-28 11:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sm

# revision identifiers, used by Alembic.
revision: str = '012'
down_revision: Union[str, None] = '011'
branch_labels: Union[Sequence[str], None] = None
depends_on: Union[Sequence[str], None] = None


def upgrade() -> None:
    # 1. suppliers
    op.create_table(
        'suppliers',
        sm.Column('id', sm.UUID(), primary_key=True),
        sm.Column('supplier_number', sm.String(50), nullable=False, unique=True, index=True),
        sm.Column('supplier_name', sm.String(255), nullable=False),
        sm.Column('supplier_type', sm.String(100), nullable=False, server_default='RAW_MATERIAL'), # RAW_MATERIAL, COMPONENT, CONTRACT_MANUFACTURER, SERVICE, PACKAGING
        sm.Column('category', sm.String(100), nullable=False, server_default='PRIMARY'),
        sm.Column('status', sm.String(50), nullable=False, server_default='PENDING_QUALIFICATION'), # PENDING_QUALIFICATION, APPROVED, CONDITIONAL, DISQUALIFIED
        sm.Column('risk_level', sm.String(50), nullable=False, server_default='MEDIUM'), # LOW, MEDIUM, HIGH, CRITICAL
        sm.Column('address', sm.String(255), nullable=True),
        sm.Column('city', sm.String(100), nullable=True),
        sm.Column('state', sm.String(100), nullable=True),
        sm.Column('country', sm.String(100), nullable=True),
        sm.Column('zip_code', sm.String(20), nullable=True),
        sm.Column('phone', sm.String(50), nullable=True),
        sm.Column('email', sm.String(255), nullable=True),
        sm.Column('website', sm.String(255), nullable=True),
        sm.Column('approval_status', sm.String(50), nullable=False, server_default='PENDING'),
        sm.Column('approved_by', sm.String(255), nullable=True),
        sm.Column('approved_at', sm.DateTime(timezone=True), nullable=True),
        sm.Column('created_by', sm.String(255), nullable=False),
        sm.Column('updated_by', sm.String(255), nullable=False),
        sm.Column('created_at', sm.DateTime(timezone=True), nullable=False),
        sm.Column('updated_at', sm.DateTime(timezone=True), nullable=False),
    )

    # 2. supplier_contacts
    op.create_table(
        'supplier_contacts',
        sm.Column('id', sm.UUID(), primary_key=True),
        sm.Column('supplier_id', sm.UUID(), sm.ForeignKey('suppliers.id', ondelete='CASCADE'), nullable=False, index=True),
        sm.Column('name', sm.String(255), nullable=False),
        sm.Column('email', sm.String(255), nullable=False),
        sm.Column('phone', sm.String(50), nullable=True),
        sm.Column('title', sm.String(100), nullable=True),
        sm.Column('is_primary', sm.Boolean(), nullable=False, server_default='0'),
    )

    # 3. supplier_documents
    op.create_table(
        'supplier_documents',
        sm.Column('id', sm.UUID(), primary_key=True),
        sm.Column('supplier_id', sm.UUID(), sm.ForeignKey('suppliers.id', ondelete='CASCADE'), nullable=False, index=True),
        sm.Column('document_id', sm.UUID(), sm.ForeignKey('documents.id', ondelete='SET NULL'), nullable=True, index=True),
        sm.Column('document_type', sm.String(100), nullable=False), # ISO_CERTIFICATE, QUALITY_AGREEMENT, AUDIT_REPORT, COA
        sm.Column('valid_until', sm.DateTime(timezone=True), nullable=True),
    )

    # 4. supplier_audits
    op.create_table(
        'supplier_audits',
        sm.Column('id', sm.UUID(), primary_key=True),
        sm.Column('supplier_id', sm.UUID(), sm.ForeignKey('suppliers.id', ondelete='CASCADE'), nullable=False, index=True),
        sm.Column('audit_number', sm.String(50), nullable=False, unique=True, index=True),
        sm.Column('audit_type', sm.String(50), nullable=False, server_default='QUALIFICATION'), # QUALIFICATION, PERIODIC, FOR_CAUSE
        sm.Column('scheduled_date', sm.DateTime(timezone=True), nullable=False),
        sm.Column('completed_date', sm.DateTime(timezone=True), nullable=True),
        sm.Column('auditor', sm.String(255), nullable=False),
        sm.Column('status', sm.String(50), nullable=False, server_default='SCHEDULED'), # SCHEDULED, IN_PROGRESS, COMPLETED, CANCELLED
        sm.Column('score', sm.Float(), nullable=True),
        sm.Column('findings_summary', sm.Text(), nullable=True),
    )

    # 5. supplier_scorecards
    op.create_table(
        'supplier_scorecards',
        sm.Column('id', sm.UUID(), primary_key=True),
        sm.Column('supplier_id', sm.UUID(), sm.ForeignKey('suppliers.id', ondelete='CASCADE'), nullable=False, index=True),
        sm.Column('period', sm.String(50), nullable=False), # e.g. 2026-Q1
        sm.Column('quality_score', sm.Float(), nullable=False, server_default='100.0'),
        sm.Column('delivery_score', sm.Float(), nullable=False, server_default='100.0'),
        sm.Column('compliance_score', sm.Float(), nullable=False, server_default='100.0'),
        sm.Column('overall_score', sm.Float(), nullable=False, server_default='100.0'),
        sm.Column('grade', sm.String(10), nullable=False, server_default='A'), # A, B, C, D, F
        sm.Column('evaluated_by', sm.String(255), nullable=False),
        sm.Column('evaluated_at', sm.DateTime(timezone=True), nullable=False),
    )

    # 6. supplier_nonconformances
    op.create_table(
        'supplier_nonconformances',
        sm.Column('id', sm.UUID(), primary_key=True),
        sm.Column('supplier_id', sm.UUID(), sm.ForeignKey('suppliers.id', ondelete='CASCADE'), nullable=False, index=True),
        sm.Column('complaint_id', sm.UUID(), sm.ForeignKey('complaints.id', ondelete='SET NULL'), nullable=True, index=True),
        sm.Column('ncr_number', sm.String(50), nullable=False, unique=True, index=True),
        sm.Column('title', sm.String(255), nullable=False),
        sm.Column('description', sm.Text(), nullable=False),
        sm.Column('severity', sm.String(50), nullable=False, server_default='MEDIUM'), # MINOR, MAJOR, CRITICAL
        sm.Column('status', sm.String(50), nullable=False, server_default='OPEN'), # OPEN, INVESTIGATING, CLOSED
        sm.Column('created_at', sm.DateTime(timezone=True), nullable=False),
    )

    # 7. supplier_corrective_actions
    op.create_table(
        'supplier_corrective_actions',
        sm.Column('id', sm.UUID(), primary_key=True),
        sm.Column('supplier_id', sm.UUID(), sm.ForeignKey('suppliers.id', ondelete='CASCADE'), nullable=False, index=True),
        sm.Column('capa_id', sm.UUID(), sm.ForeignKey('capa_records.id', ondelete='SET NULL'), nullable=True, index=True),
        sm.Column('action_number', sm.String(50), nullable=False, unique=True, index=True),
        sm.Column('action_plan', sm.Text(), nullable=False),
        sm.Column('owner', sm.String(255), nullable=False),
        sm.Column('due_date', sm.DateTime(timezone=True), nullable=False),
        sm.Column('status', sm.String(50), nullable=False, server_default='OPEN'), # OPEN, IN_PROGRESS, COMPLETED
        sm.Column('completed_at', sm.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_table('supplier_corrective_actions')
    op.drop_table('supplier_nonconformances')
    op.drop_table('supplier_scorecards')
    op.drop_table('supplier_audits')
    op.drop_table('supplier_documents')
    op.drop_table('supplier_contacts')
    op.drop_table('suppliers')
