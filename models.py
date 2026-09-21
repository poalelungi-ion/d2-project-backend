"""Backward-compatible shim for database models."""
from src.database.models import Base, Course, Exam, ExamResult, RefreshToken, Student, User
__all__ = ["Base", "Course", "Exam", "ExamResult", "Student", "User", "RefreshToken"]
