"""Add due_date column and update status CheckConstraint for complaints

Revision ID: 006
Revises: 005
Create Date: 2026-07-28 03:30:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "006"
down_revision: Union[str, None] = "005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

ALL_STATUSES = (
    "'Draft', 'NEW', 'TRIAGED', 'ASSIGNED', 'UNDER_INVESTIGATION', "
    "'ROOT_CAUSE_IDENTIFIED', 'CAPA_IN_PROGRESS', 'QA_REVIEW', 'QA_APPROVED', "
    "'CLOSED', 'REJECTED', 'ON_HOLD', 'CANCELLED', 'UNDER_REVIEW', 'IN_PROGRESS', "
    "'WAITING_CUSTOMER', 'RESOLVED', 'Under Review', 'Closed'"
)


def upgrade() -> None:
    op.add_column("complaints", sa.Column("due_date", sa.DateTime(timezone=True), nullable=True))
    try:
        op.drop_constraint("ck_complaints_status", "complaints", type_="check")
    except Exception:
        pass
    op.create_check_constraint(
        "ck_complaints_status",
        "complaints",
        f"status IN ({ALL_STATUSES})",
    )


def downgrade() -> None:
    op.drop_column("complaints", "due_date")
