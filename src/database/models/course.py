"""
Course and Exam ORM Models.
Tracks courses, exams, and versions for optimistic locking.
"""
from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.database.connection import Base


class Course(Base):
    __tablename__ = "courses"

    course_id = Column(Integer, primary_key=True, index=True)
    course_name = Column(String, nullable=False, unique=True)
    professor = Column(String, nullable=True, default="Not Assigned")
    semester = Column(String, nullable=True)
    study_program = Column(String, nullable=True)
    is_archived = Column(Boolean, default=False)

    # [REQ-CONCURRENCY-01] Version tracking for optimistic locking
    version = Column(Integer, nullable=False, default=1)

    __mapper_args__ = {
        "version_id_col": version
    }

    exams = relationship("Exam", back_populates="course", cascade="all, delete-orphan")


class Exam(Base):
    __tablename__ = "exams"

    exam_id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.course_id"), nullable=False)
    semester = Column(String, nullable=False)  # e.g. SOSE_26
    exam_date = Column(Date, nullable=True)

    course = relationship("Course", back_populates="exams")
    results = relationship("ExamResult", back_populates="exam", cascade="all, delete-orphan")
