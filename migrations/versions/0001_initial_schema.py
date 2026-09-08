"""Initial database schema migration

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-09-08 16:00:00

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create students table
    op.create_table(
        "students",
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("program", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.PrimaryKeyConstraint("student_id"),
    )
    op.create_index(op.f("ix_students_student_id"), "students", ["student_id"], unique=False)

    # 2. Create courses table
    op.create_table(
        "courses",
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.Column("course_name", sa.String(), nullable=False),
        sa.Column("professor", sa.String(), nullable=True),
        sa.Column("semester", sa.String(), nullable=True),
        sa.Column("study_program", sa.String(), nullable=True),
        sa.Column("is_archived", sa.Boolean(), nullable=True, server_default="false"),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.PrimaryKeyConstraint("course_id"),
        sa.UniqueConstraint("course_name"),
    )
    op.create_index(op.f("ix_courses_course_id"), "courses", ["course_id"], unique=False)

    # 3. Create exams table
    op.create_table(
        "exams",
        sa.Column("exam_id", sa.Integer(), nullable=False),
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.Column("semester", sa.String(), nullable=False),
        sa.Column("exam_date", sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(["course_id"], ["courses.course_id"]),
        sa.PrimaryKeyConstraint("exam_id"),
    )
    op.create_index(op.f("ix_exams_exam_id"), "exams", ["exam_id"], unique=False)

    # 4. Create exam_results table with check constraint
    op.create_table(
        "exam_results",
        sa.Column("result_id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("exam_id", sa.Integer(), nullable=False),
        sa.Column("grade", sa.Float(), nullable=False),
        sa.Column("passed", sa.Boolean(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.CheckConstraint("grade >= 1.0 AND grade <= 5.0", name="check_valid_grade"),
        sa.ForeignKeyConstraint(["exam_id"], ["exams.exam_id"]),
        sa.ForeignKeyConstraint(["student_id"], ["students.student_id"]),
        sa.PrimaryKeyConstraint("result_id"),
    )
    op.create_index(op.f("ix_exam_results_result_id"), "exam_results", ["result_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_exam_results_result_id"), table_name="exam_results")
    op.drop_table("exam_results")
    op.drop_index(op.f("ix_exams_exam_id"), table_name="exams")
    op.drop_table("exams")
    op.drop_index(op.f("ix_courses_course_id"), table_name="courses")
    op.drop_table("courses")
    op.drop_index(op.f("ix_students_student_id"), table_name="students")
    op.drop_table("students")
