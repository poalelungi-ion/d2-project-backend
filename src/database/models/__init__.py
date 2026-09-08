from src.database.connection import Base
from src.database.models.course import Course, Exam
from src.database.models.student import Student, ExamResult

__all__ = ["Base", "Course", "Exam", "Student", "ExamResult"]
