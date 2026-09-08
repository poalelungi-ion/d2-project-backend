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


class ExamResult(Base):
    __tablename__ = "exam_results"

    result_id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.student_id"), nullable=False)
    exam_id = Column(Integer, ForeignKey("exams.exam_id"), nullable=False)
    grade = Column(Float, nullable=False)
    passed = Column(Boolean, nullable=False)

    # [REQ-CONCURRENCY-01] Version tracking for optimistic locking
    version = Column(Integer, nullable=False, default=1)

    __mapper_args__ = {
        "version_id_col": version
    }

    __table_args__ = (
        CheckConstraint("grade >= 1.0 AND grade <= 5.0", name="check_valid_grade"),
    )

    student = relationship("Student", back_populates="results")
    exam = relationship("Exam", back_populates="results")
