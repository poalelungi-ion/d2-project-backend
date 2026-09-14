"""
Upload and Ingestion Data Transfer Objects (DTOs).
"""
from typing import List, Literal, Optional
from pydantic import BaseModel

# The sittings a lecturer can tag an upload with. Kept as a Literal so an
# unrecognised value is rejected at the API boundary rather than reaching the DB.
AttemptType = Literal["Exam 1", "Exam 2", "Other"]


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
    # The course view the upload was started from. When present the batch
    # attaches to exactly this course; the standalone wizard leaves it unset
    # and the course is matched by name instead.
    courseId: Optional[int] = None
    courseName: str
    ects: Optional[str] = "6"
    semester: str
    # Defaulted so callers predating the attempt-type dropdown still import.
    attemptType: AttemptType = "Other"
    records: List[ConfirmRecord]
