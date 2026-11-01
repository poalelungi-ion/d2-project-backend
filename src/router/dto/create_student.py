"""
Student and Grading Data Transfer Objects (DTOs).
Validates inputs for student creation, profile editing, status updates, and grade recording.
"""
from typing import Optional, Union
from pydantic import BaseModel, Field

from src.lib.study_program import NamedStudyProgram


class StudentCreate(BaseModel):
    student_id: int
    name: str
    program: NamedStudyProgram = "SE Master"
    status: Optional[str] = "active"


class StudentUpdate(BaseModel):
    new_student_id: Optional[int] = None
    program: NamedStudyProgram
    name: str
    status: Optional[str] = None
    version: int


class StudentStatusUpdate(BaseModel):
    status: str
    version: int


class AddGradeRequest(BaseModel):
    course_id: int
    semester: str
    grade: Union[float, str]
    attempt_type: Optional[str] = "Exam 1"
