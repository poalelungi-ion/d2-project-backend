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

@router.get("/api/stats/")
def get_stats(db: Session = Depends(get_db)):
    """
    Retrieves key performance indicators (KPIs) for the Analysis Hub dashboard.
    Calculates total students, passing rates, average grades, and identifies at-risk students.
    """
    results = db.query(models.ExamResult).all()
    students = db.query(models.Student).all()
    courses = db.query(models.Course).all()
    
    active_students = [s for s in students if s.status == "active"]
    active_results = [r for r in results if r.student and r.student.status == "active"]
    
    total_active_students = len(active_students)
    total_archived_courses = sum(1 for c in courses if c.is_archived)
    
    active_passed = sum(1 for r in active_results if r.passed)
    active_pass_rate = (active_passed / len(active_results) * 100) if active_results else 0
    active_avg_grade = (sum(r.grade for r in active_results) / len(active_results)) if active_results else 0
    
    kpis = {
        "total_active_students": total_active_students,
        "total_archived_courses": total_archived_courses,
        "active_pass_rate": round(active_pass_rate, 1),
        "active_avg_grade": round(active_avg_grade, 2)
    }
    
    at_risk = []
    for s in active_students:
        fails = sum(1 for r in s.results if not r.passed)
        if fails >= 2:
            at_risk.append({"name": s.name, "fails": fails, "student_id": s.student_id})
            
    course_stats = []
    for c in courses:
        if c.is_archived: continue
        c_results = []
        for e in c.exams:
            c_results.extend([r for r in e.results if r.student and r.student.status == "active"])
        if len(c_results) > 0:
            c_pass = sum(1 for r in c_results if r.passed)
            c_rate = c_pass / len(c_results) * 100
            course_stats.append({
                "course_name": c.course_name,
                "pass_rate": round(c_rate, 1),
                "avg_grade": round(sum(r.grade for r in c_results) / len(c_results), 2)
            })
    course_stats.sort(key=lambda x: x["pass_rate"])
    toughest_courses = course_stats[:5]
    
    return {
        "kpis": kpis,
        "toughest_courses": toughest_courses,
        "atRisk": sorted(at_risk, key=lambda x: x['fails'], reverse=True)
    }


