"""
Student and ExamResult ORM Models.
Enforces optimistic locking (version column) and grade check constraints.
"""
from sqlalchemy import CheckConstraint, Column, ForeignKey, Integer, String, Float, Boolean
from sqlalchemy.orm import relationship

from src.database.connection import Base


class Student(Base):
    __tablename__ = "students"

    student_id = Column(Integer, primary_key=True, index=True)
    program = Column(String, nullable=False, default="SE Master")
    name = Column(String, nullable=False)
    status = Column(String, default="active")

    # [REQ-CONCURRENCY-01] Version tracking for optimistic locking
    version = Column(Integer, nullable=False, default=1)

    __mapper_args__ = {
        "version_id_col": version
    }

    results = relationship("ExamResult", back_populates="student", cascade="all, delete-orphan")

    @property
    def study_program(self):
        return self.program

    @study_program.setter
    def study_program(self, val):
        self.program = val


class ExamResult(Base):
    __tablename__ = "exam_results"

    result_id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.student_id"), nullable=False)
    exam_id = Column(Integer, ForeignKey("exams.exam_id"), nullable=False)
    # Numeric German grade, or null when the sitting is excused (AT).
    grade = Column(Float, nullable=True)
    passed = Column(Boolean, nullable=False)
    # Official absence code from the grade cell: NE/EX (fail) or AT (excused).
    absence_code = Column(String, nullable=True)

    # Which sitting this result came from, chosen once per upload by the lecturer:
    # "Exam 1", "Exam 2" or "Other". Stored per result so a batch stays identifiable
    # even when both sittings of a course share one Exam row.
    attempt_type = Column(String, nullable=False, default="Other", server_default="Other")

    # [REQ-CONCURRENCY-01] Version tracking for optimistic locking
    version = Column(Integer, nullable=False, default=1)

    __mapper_args__ = {
        "version_id_col": version
    }

    __table_args__ = (
        CheckConstraint(
            "grade IS NULL OR (grade >= 1.0 AND grade <= 5.0)",
            name="check_valid_grade",
        ),
    )

    student = relationship("Student", back_populates="results")
    exam = relationship("Exam", back_populates="results")
