from pydantic import BaseModel
from typing import List, Optional

class ConfirmRecord(BaseModel):
    student_id: str
    first_name: str = ""
    last_name: str = ""
    name: str = ""
    program: str
    semester: str
    grade: str

class UploadConfirmRequest(BaseModel):
    course: str
    courseName: str
    ects: str
    semester: str
    records: list[ConfirmRecord]

class GradeUpdate(BaseModel):
    result_id: int
    version: int
    grade: float
    passed: bool

class CourseArchiveUpdate(BaseModel):
    is_archived: bool
    version: int

class CourseCreate(BaseModel):
    course_id: int = None
    course_name: str
    semester: str
    study_program: str
    professor: str = "Not Assigned"

class CourseUpdate(BaseModel):
    new_course_id: Optional[int] = None
    course_name: str
    semester: str
    study_program: str
    professor: str = "Not Assigned"
    version: int

class StudentUpdate(BaseModel):
    new_student_id: Optional[int] = None
    program: str
    name: str
    status: str
    version: int

class StudentCreate(BaseModel):
    student_id: int
    name: str
    program: str
    status: str = "active"

class AddGradeRequest(BaseModel):
    course_id: int
    semester: str
    grade: float

class StudentStatusUpdate(BaseModel):
    status: str
    version: int