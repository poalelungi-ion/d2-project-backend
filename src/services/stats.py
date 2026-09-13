"""
Statistics and KPIs Domain Service.
Calculates summary KPIs, identifies at-risk students, and course pass rates.
"""
from sqlalchemy.orm import Session
from src.database.models import Course, ExamResult, Student
from src.services.grade_outcome import counted_attempts, is_excused, mean_grade


def get_dashboard_stats(db: Session):
    results = db.query(ExamResult).all()
    students = db.query(Student).all()
    courses = db.query(Course).all()

    active_students = [s for s in students if s.status == "active"]
    active_results = [r for r in results if r.student and r.student.status == "active"]

    total_active_students = len(active_students)
    total_archived_courses = sum(1 for c in courses if c.is_archived)

    graded_active = counted_attempts(active_results)
    active_passed = sum(1 for r in graded_active if r.passed)
    active_pass_rate = (active_passed / len(graded_active) * 100) if graded_active else 0
    active_avg_grade = mean_grade(graded_active)

    kpis = {
        "total_active_students": total_active_students,
        "total_archived_courses": total_archived_courses,
        "active_pass_rate": round(active_pass_rate, 1),
        "active_avg_grade": round(active_avg_grade, 2),
    }

    at_risk = []
    for s in active_students:
        fails = sum(
            1 for r in s.results if not r.passed and not is_excused(r.absence_code)
        )
        if fails >= 2:
            at_risk.append({"name": s.name, "fails": fails, "student_id": s.student_id})

    course_stats = []
    for c in courses:
        if c.is_archived:
            continue
        c_results = []
        for e in c.exams:
            c_results.extend([r for r in e.results if r.student and r.student.status == "active"])
        graded = counted_attempts(c_results)
        if len(graded) > 0:
            c_pass = sum(1 for r in graded if r.passed)
            c_rate = c_pass / len(graded) * 100
            course_stats.append({
                "course_name": c.course_name,
                "pass_rate": round(c_rate, 1),
                "avg_grade": round(mean_grade(graded), 2),
            })
    course_stats.sort(key=lambda x: x["pass_rate"])
    toughest_courses = course_stats[:5]

    return {
        "kpis": kpis,
        "toughest_courses": toughest_courses,
        "atRisk": sorted(at_risk, key=lambda x: x["fails"], reverse=True),
    }
