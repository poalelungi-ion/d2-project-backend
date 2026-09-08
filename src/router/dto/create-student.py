"""
Student and Grading Data Transfer Objects (DTOs).
Validates inputs for student creation, profile editing, status updates, and grade recording.
"""
from typing import Optional
from pydantic import BaseModel, Field


class StudentCreate(BaseModel):
    student_id: int
    name: str
    program: str = "SE Master"
    status: str = "active"


class StudentUpdate(BaseModel):
    new_student_id: Optional[int] = None
    program: str
    name: str
    status: str
    version: int


class StudentStatusUpdate(BaseModel):
    status: str
    version: int


class AddGradeRequest(BaseModel):
    course_id: int
    semester: str
    grade: float = Field(..., ge=1.0, le=5.0)
