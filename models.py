"""
Database Models Module

This module defines the SQLAlchemy ORM models for the SPA System.
It establishes the relational structure for Students, Courses, Exams, and ExamResults.

Key Features:
- Optimistic Concurrency Control: The `version` column and `__mapper_args__` configuration
  prevent lost updates when multiple users edit the same record simultaneously.
- Data Integrity: Strict `CheckConstraint` ensures exam grades remain between 1.0 and 5.0.
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Date, CheckConstraint
from sqlalchemy.orm import relationship
from database import Base

class Student(Base):
    """
    [REQ-CONCURRENCY-01] Optimistic Concurrency Control
    We track the `version` of this model. When an update occurs, SQLAlchemy 
    checks that the `version` matches the one originally fetched by the client.
    If it doesn't match, it means another user modified it in the meantime, 
    preventing simultaneous data alteration.
    """
    __tablename__ = "students"
    student_id = Column(Integer, primary_key=True, index=True)
    program = Column(String, nullable=False, default="SE Master")
    name = Column(String, nullable=False)
    status = Column(String, default="active")
    
    # [REQ-CONCURRENCY-01] Version tracking column for optimistic locking
    version = Column(Integer, nullable=False, default=1)
    
    __mapper_args__ = {
        "version_id_col": version
    }
    
    results = relationship("ExamResult", back_populates="student")

class Course(Base):
    """
    [REQ-CONCURRENCY-01] Optimistic Concurrency Control
    Tracks version to ensure archiving/unarchiving doesn't conflict with other users' updates.
    """
    __tablename__ = "courses"
    course_id = Column(Integer, primary_key=True, index=True)
    course_name = Column(String, nullable=False, unique=True)
    professor = Column(String, nullable=True, default="Not Assigned")
    semester = Column(String, nullable=True)
    study_program = Column(String, nullable=True)
    is_archived = Column(Boolean, default=False)
    
    # [REQ-CONCURRENCY-01] Version tracking column for optimistic locking
    version = Column(Integer, nullable=False, default=1)
    
    __mapper_args__ = {
        "version_id_col": version
    }
    
    exams = relationship("Exam", back_populates="course")

class Exam(Base):
    __tablename__ = "exams"
    exam_id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.course_id"), nullable=False)
    semester = Column(String, nullable=False) # e.g. SOSE_26
    exam_date = Column(Date, nullable=True)
    
    course = relationship("Course", back_populates="exams")
    results = relationship("ExamResult", back_populates="exam")

class ExamResult(Base):
    """
    [REQ-CONCURRENCY-01] Optimistic Concurrency Control
    Tracks version to ensure grade edits do not overwrite each other.
    """
    __tablename__ = "exam_results"
    result_id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.student_id"), nullable=False)
    exam_id = Column(Integer, ForeignKey("exams.exam_id"), nullable=False)
    grade = Column(Float, nullable=False)
    passed = Column(Boolean, nullable=False)
    
    # [REQ-CONCURRENCY-01] Version tracking column for optimistic locking
    version = Column(Integer, nullable=False, default=1)
    
    __mapper_args__ = {
        "version_id_col": version
    }
    
    # Data integrity requirement: grades must be strictly validated
    __table_args__ = (
        CheckConstraint('grade >= 1.0 AND grade <= 5.0', name='check_valid_grade'),
    )
    
    student = relationship("Student", back_populates="results")
    exam = relationship("Exam", back_populates="results")
