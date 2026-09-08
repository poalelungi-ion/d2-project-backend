"""Backward-compatible shim for schemas."""
from src.router.dto import (
    AddGradeRequest,
    ConfirmRecord,
    CourseArchiveUpdate,
    CourseCreate,
    CourseUpdate,
    GradeUpdate,
    StudentCreate,
    StudentStatusUpdate,
    StudentUpdate,
    UploadConfirmRequest,
)
__all__ = [
    "ConfirmRecord",
    "UploadConfirmRequest",
    "GradeUpdate",
    "CourseArchiveUpdate",
    "CourseCreate",
    "CourseUpdate",
    "StudentUpdate",
    "StudentCreate",
    "AddGradeRequest",
    "StudentStatusUpdate",
]
