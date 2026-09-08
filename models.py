"""Backward-compatible shim for database models."""
from src.database.models import Base, Course, Exam, ExamResult, Student
__all__ = ["Base", "Course", "Exam", "ExamResult", "Student"]
