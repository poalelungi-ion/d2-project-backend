"""
Upload and Ingestion Data Transfer Objects (DTOs).
"""
from typing import List, Optional
from pydantic import BaseModel


class ConfirmRecord(BaseModel):
    student_id: str
    first_name: str = ""
    last_name: str = ""
    name: str = ""
    program: str = ""
    semester: str = ""
    grade: str = ""


class UploadConfirmRequest(BaseModel):
    course: Optional[str] = None
    courseName: str
    ects: Optional[str] = "6"
    semester: str
    records: List[ConfirmRecord]
