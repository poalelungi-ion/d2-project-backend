"""
Course Router (HTTP Controller).
Handles course catalogue querying, creation, updating, and archiving.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.database.connection import get_db
from src.lib.auth.validator import verify_token
from src.router.dto import (
    CourseArchiveUpdate,
    CourseCreate,
    CourseUpdate,
)
from src.services import course as course_service

router = APIRouter()


@router.get("/api/courses/", summary="Get all courses")
def get_courses(db: Session = Depends(get_db)):
    """Retrieves all courses alongside pass rates and average grades."""
    return course_service.get_all_courses(db)


@router.post(
    "/api/courses/",
    dependencies=[Depends(verify_token)],
    status_code=status.HTTP_201_CREATED,
    summary="Create course",
)
def create_course(course: CourseCreate, db: Session = Depends(get_db)):
    """Creates a new course in the catalogue (Protected endpoint)."""
    return course_service.create_course(db, course)


@router.put(
    "/api/courses/{course_id}",
    dependencies=[Depends(verify_token)],
    summary="Update course",
)
def update_course(course_id: int, course: CourseUpdate, db: Session = Depends(get_db)):
    """Updates course metadata under optimistic locking (Protected endpoint)."""
    return course_service.update_course(db, course_id, course)


@router.put("/api/courses/{course_id}/archive", summary="Archive or unarchive course")
def update_course_archive(course_id: int, update: CourseArchiveUpdate, db: Session = Depends(get_db)):
    """Toggles course archive state."""
    return course_service.archive_course(db, course_id, update)
