"""Add attempt_type to exam_results

Records which sitting ("Exam 1", "Exam 2" or "Other") an imported batch of
results belongs to. Existing rows predate the lecturer-chosen attempt type,
so they are backfilled with "Other" by the server default.

Revision ID: 0002_add_attempt_type
Revises: 0001_initial_schema
Create Date: 2026-09-08 00:00:00

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0002_add_attempt_type"
down_revision: Union[str, None] = "0001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "exam_results",
        sa.Column(
            "attempt_type",
            sa.String(),
            nullable=False,
            server_default="Other",
        ),
    )


def downgrade() -> None:
    op.drop_column("exam_results", "attempt_type")
