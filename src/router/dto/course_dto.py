"""
Course Data Transfer Objects (DTOs).
"""
from typing import Optional
from pydantic import BaseModel


class CourseCreate(BaseModel):
    course_id: Optional[int] = None
    course_name: str
    semester: Optional[str] = None
    study_program: Optional[str] = None
    professor: str = "Not Assigned"


class CourseUpdate(BaseModel):
    new_course_id: Optional[int] = None
    course_name: str
    semester: Optional[str] = None
    study_program: Optional[str] = None
    professor: str = "Not Assigned"
    version: int


class CourseArchiveUpdate(BaseModel):
    is_archived: bool
    version: int
