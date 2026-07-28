"""create training management tables

Revision ID: 011_training_management
Revises: 010_document_management
Create Date: 2026-07-28 11:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sm
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision: str = '011'
down_revision: Union[str, None] = '010'
branch_labels: Union[Sequence[str], None] = None
depends_on: Union[Sequence[str], None] = None


def upgrade() -> None:
    # 1. training_courses
    op.create_table(
        'training_courses',
        sm.Column('id', sm.UUID(), primary_key=True),
        sm.Column('course_number', sm.String(50), nullable=False, unique=True, index=True),
        sm.Column('title', sm.String(255), nullable=False),
        sm.Column('description', sm.Text(), nullable=True),
        sm.Column('category', sm.String(100), nullable=False, server_default='QUALITY'),
        sm.Column('training_type', sm.String(50), nullable=False, server_default='SOP'), # SOP, CAPA, RCA, GENERAL, QUALITY, SAFETY
        sm.Column('duration_minutes', sm.Integer(), nullable=False, server_default='30'),
        sm.Column('passing_score', sm.Float(), nullable=False, server_default='80.0'),
        sm.Column('validity_days', sm.Integer(), nullable=False, server_default='365'),
        sm.Column('status', sm.String(50), nullable=False, server_default='DRAFT'), # DRAFT, ACTIVE, RETIRED
        sm.Column('created_by', sm.String(255), nullable=False),
        sm.Column('updated_by', sm.String(255), nullable=False),
        sm.Column('created_at', sm.DateTime(timezone=True), nullable=False),
        sm.Column('updated_at', sm.DateTime(timezone=True), nullable=False),
    )

    # 2. training_assignments
    op.create_table(
        'training_assignments',
        sm.Column('id', sm.UUID(), primary_key=True),
        sm.Column('course_id', sm.UUID(), sm.ForeignKey('training_courses.id', ondelete='CASCADE'), nullable=False, index=True),
        sm.Column('user_id', sm.UUID(), sm.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sm.Column('assigned_by', sm.String(255), nullable=False),
        sm.Column('assigned_date', sm.DateTime(timezone=True), nullable=False),
        sm.Column('due_date', sm.DateTime(timezone=True), nullable=False),
        sm.Column('status', sm.String(50), nullable=False, server_default='NOT_STARTED'), # NOT_STARTED, IN_PROGRESS, COMPLETED, FAILED, OVERDUE
        sm.Column('completion_date', sm.DateTime(timezone=True), nullable=True),
        sm.Column('score', sm.Float(), nullable=True),
        sm.Column('attempts', sm.Integer(), nullable=False, server_default='0'),
        sm.Column('electronic_signature_id', sm.UUID(), sm.ForeignKey('electronic_signatures.id', ondelete='SET NULL'), nullable=True),
    )

    # 3. quizzes
    op.create_table(
        'quizzes',
        sm.Column('id', sm.UUID(), primary_key=True),
        sm.Column('course_id', sm.UUID(), sm.ForeignKey('training_courses.id', ondelete='CASCADE'), nullable=False, index=True),
        sm.Column('title', sm.String(255), nullable=False),
        sm.Column('passing_score', sm.Float(), nullable=False, server_default='80.0'),
        sm.Column('randomize_questions', sm.Boolean(), nullable=False, server_default='1'),
        sm.Column('time_limit_minutes', sm.Integer(), nullable=False, server_default='15'),
        sm.Column('created_at', sm.DateTime(timezone=True), nullable=False),
    )

    # 4. quiz_questions
    op.create_table(
        'quiz_questions',
        sm.Column('id', sm.UUID(), primary_key=True),
        sm.Column('quiz_id', sm.UUID(), sm.ForeignKey('quizzes.id', ondelete='CASCADE'), nullable=False, index=True),
        sm.Column('question', sm.Text(), nullable=False),
        sm.Column('option_a', sm.String(255), nullable=False),
        sm.Column('option_b', sm.String(255), nullable=False),
        sm.Column('option_c', sm.String(255), nullable=False),
        sm.Column('option_d', sm.String(255), nullable=False),
        sm.Column('correct_answer', sm.String(10), nullable=False), # A, B, C, D
        sm.Column('explanation', sm.Text(), nullable=True),
        sm.Column('display_order', sm.Integer(), nullable=False, server_default='1'),
    )

    # 5. quiz_attempts
    op.create_table(
        'quiz_attempts',
        sm.Column('id', sm.UUID(), primary_key=True),
        sm.Column('quiz_id', sm.UUID(), sm.ForeignKey('quizzes.id', ondelete='CASCADE'), nullable=False, index=True),
        sm.Column('user_id', sm.UUID(), sm.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sm.Column('score', sm.Float(), nullable=False),
        sm.Column('passed', sm.Boolean(), nullable=False),
        sm.Column('attempted_at', sm.DateTime(timezone=True), nullable=False),
    )

    # 6. sop_acknowledgements
    op.create_table(
        'sop_acknowledgements',
        sm.Column('id', sm.UUID(), primary_key=True),
        sm.Column('document_id', sm.UUID(), sm.ForeignKey('documents.id', ondelete='CASCADE'), nullable=False, index=True),
        sm.Column('user_id', sm.UUID(), sm.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sm.Column('signature_id', sm.UUID(), sm.ForeignKey('electronic_signatures.id', ondelete='SET NULL'), nullable=True),
        sm.Column('acknowledged_at', sm.DateTime(timezone=True), nullable=False),
    )

    # 7. competency_records
    op.create_table(
        'competency_records',
        sm.Column('id', sm.UUID(), primary_key=True),
        sm.Column('user_id', sm.UUID(), sm.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sm.Column('skill', sm.String(150), nullable=False),
        sm.Column('level', sm.String(50), nullable=False, server_default='BEGINNER'), # BEGINNER, INTERMEDIATE, ADVANCED, EXPERT
        sm.Column('verified_by', sm.String(255), nullable=False),
        sm.Column('verified_at', sm.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('competency_records')
    op.drop_table('sop_acknowledgements')
    op.drop_table('quiz_attempts')
    op.drop_table('quiz_questions')
    op.drop_table('quizzes')
    op.drop_table('training_assignments')
    op.drop_table('training_courses')
