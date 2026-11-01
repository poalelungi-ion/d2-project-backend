"""
Upload and Ingestion Data Transfer Objects (DTOs).
"""
from typing import List, Optional
from pydantic import BaseModel, field_validator

from src.lib.study_program import UNASSIGNED_PROGRAM, UploadStudyProgram

# Lecturers can tag an upload or grade sitting with any custom attempt description (#104109).
AttemptType = str


class ConfirmRecord(BaseModel):
    student_id: str
    first_name: str = ""
    last_name: str = ""
    name: str = ""
    program: UploadStudyProgram = UNASSIGNED_PROGRAM
    semester: str = ""
    grade: str = ""


class UploadConfirmRequest(BaseModel):
    course: Optional[str] = None
    # The course view the upload was started from. When present the batch
    # attaches to exactly this course; the standalone wizard leaves it unset
    # and the course is matched by name instead.
    courseId: Optional[int] = None
    courseName: str
    semester: str
    # Defaulted so callers predating the attempt-type field still import.
    attemptType: AttemptType = "Other"
    records: List[ConfirmRecord]

    @field_validator("attemptType", mode="before")
    @classmethod
    def normalize_attempt_type(cls, value: object) -> str:
        if value is None:
            return "Other"
        cleaned = str(value).strip()
        return cleaned if cleaned else "Other"
