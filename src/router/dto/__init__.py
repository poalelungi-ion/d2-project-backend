from src.router.dto.create_student import (
    StudentCreate,
    StudentUpdate,
    StudentStatusUpdate,
    AddGradeRequest,
)
from src.router.dto.course_dto import (
    CourseCreate,
    CourseUpdate,
    CourseArchiveUpdate,
)
from src.router.dto.grade_dto import GradeUpdate
from src.router.dto.upload_dto import ConfirmRecord, UploadConfirmRequest
from src.router.dto.auth_dto import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)

__all__ = [
    "StudentCreate",
    "StudentUpdate",
    "StudentStatusUpdate",
    "AddGradeRequest",
    "CourseCreate",
    "CourseUpdate",
    "CourseArchiveUpdate",
    "GradeUpdate",
    "ConfirmRecord",
    "UploadConfirmRequest",
    "LoginRequest",
    "RegisterRequest",
    "TokenResponse",
    "UserResponse",
]
