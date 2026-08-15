from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
import pandas as pd
import io
from fastapi import Header

def verify_token(authorization: str = Header(None)):
    if authorization != "Bearer sse-staff-token":
        raise HTTPException(status_code=401, detail="Unauthorized")
    return True

router = APIRouter()

@router.get("/api/grades/")
def get_grades(db: Session = Depends(get_db)):
    results = db.query(models.ExamResult).all()
    data = []
    for r in results:
        data.append({
            "result_id": r.result_id,
            "student_id": r.student.student_id if r.student else None,
            "name": r.student.name if r.student else "Unknown",
            "course": r.exam.course.course_name if r.exam and r.exam.course else "Unknown",
            "semester": r.exam.semester if r.exam else "Unknown",
            "grade": r.grade,
            "passed": r.passed,
            "version": r.version
        })
    return data










@router.post("/api/grades/")
def update_grades(updates: List[GradeUpdate], db: Session = Depends(get_db)):
    for u in updates:
        if not (1.0 <= u.grade <= 5.0):
            raise HTTPException(status_code=400, detail="Grade must be between 1.0 and 5.0")
        result = db.query(models.ExamResult).filter(models.ExamResult.result_id == u.result_id).first()
        if result:
            if result.version != u.version:
                raise HTTPException(status_code=409, detail="Data modified by another user. Please refresh.")
            result.grade = u.grade
            result.passed = u.passed
    try:
        db.commit()
    except StaleDataError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Data modified by another user. Please refresh.")
    return {"status": "success", "message": "Grades updated successfully"}

