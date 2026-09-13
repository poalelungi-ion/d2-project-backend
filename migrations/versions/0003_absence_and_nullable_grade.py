"""Allow null grades for excused attempts and store absence codes

AT (medical note) is an excused sitting with no numeric grade. NE/EX stay
as fails and keep 5.0; the code is stored so the UI can show the official
label instead of a hardcoded Passed/Failed column from the file.

Revision ID: 0003_absence_and_nullable_grade
Revises: 0002_add_attempt_type
Create Date: 2026-09-13 00:00:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0003_absence_and_nullable_grade"
down_revision: Union[str, None] = "0002_add_attempt_type"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("exam_results") as batch_op:
        batch_op.add_column(sa.Column("absence_code", sa.String(), nullable=True))
        batch_op.alter_column("grade", existing_type=sa.Float(), nullable=True)


def downgrade() -> None:
    with op.batch_alter_table("exam_results") as batch_op:
        batch_op.alter_column("grade", existing_type=sa.Float(), nullable=False)
        batch_op.drop_column("absence_code")
