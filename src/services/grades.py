"""
Grades Domain Service.
Handles grade retrieval and batch updates with optimistic concurrency control.
"""
from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import StaleDataError

from src.database.models import ExamResult
from src.router.dto import GradeUpdate
from src.services.grade_outcome import evaluate_grade, result_outcome_fields


def get_all_grades(db: Session):
    results = db.query(ExamResult).all()
    data = []
    for r in results:
        data.append({
            "result_id": r.result_id,
            "student_id": r.student.student_id if r.student else None,
            "name": r.student.name if r.student else "Unknown",
            "course": r.exam.course.course_name if r.exam and r.exam.course else "Unknown",
            "semester": r.exam.semester if r.exam else "Unknown",
            "grade": r.grade,
            **result_outcome_fields(r),
            "version": r.version,
        })
    return data


def update_grades_batch(db: Session, updates: List[GradeUpdate]):
    for u in updates:
        verdict = evaluate_grade(u.grade)
        result = db.query(ExamResult).filter(ExamResult.result_id == u.result_id).first()
        if result:
            if result.version != u.version:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Data modified by another user. Please refresh.")
            result.grade = verdict.grade
            result.passed = verdict.passed
            result.absence_code = verdict.absence_code

    try:
        db.commit()
        return {"status": "success", "message": "Grades updated successfully"}
    except StaleDataError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Data modified by another user. Please refresh.")
    except Exception:
        db.rollback()
        raise
