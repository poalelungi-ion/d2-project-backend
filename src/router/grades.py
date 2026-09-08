"""
Grades Router (HTTP Controller).
Handles grade views and batch grade modifications under optimistic concurrency control.
"""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.database.connection import get_db
from src.router.dto import GradeUpdate
from src.services import grades as grades_service

router = APIRouter()


@router.get("/api/grades/", summary="Get all exam results")
def get_grades(db: Session = Depends(get_db)):
    """Retrieves all recorded exam grades across courses."""
    return grades_service.get_all_grades(db)


@router.post("/api/grades/", summary="Batch update grades")
def update_grades(updates: List[GradeUpdate], db: Session = Depends(get_db)):
    """Updates grades in batch under optimistic concurrency control."""
    return grades_service.update_grades_batch(db, updates)
