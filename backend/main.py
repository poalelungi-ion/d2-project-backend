"""
SPA System Backend API

This is the primary FastAPI application module. It defines all REST endpoints for
file uploading, data retrieval, and student profile management.

Key functionalities:
- Uploading and validating CSV/Excel exam data.
- Processing valid records atomically using SQLAlchemy.
- Retrieving longitudinal and cross-sectional analytics data.
- Enforcing token-based authentication via Dependency Injection.
"""
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io
from database import engine, get_db
import models
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import StaleDataError
from pydantic import BaseModel
from typing import List
import random
from collections import Counter
from fastapi import Header
def verify_token(authorization: str = Header(None)):
    if authorization != "Bearer sse-staff-token":
        raise HTTPException(status_code=401, detail="Unauthorized")
    return True

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Study Progress Analysis API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def seed_db():
    db = next(get_db())
    try:
        if db.query(models.Student).count() == 0:
            # Expanded student list for better statistics
            students = [
                models.Student(student_id=1001, name="Anna Chiriciuc", program="SE Master"),
                models.Student(student_id=1002, name="Ion Poalelungi", program="SE Master"),
                models.Student(student_id=1003, name="Jacqueline Denise", program="SE Master"),
                models.Student(student_id=1004, name="Max Mustermann", program="Data Science Master"),
                models.Student(student_id=1005, name="Erika Musterfrau", program="SE Master"),
                models.Student(student_id=1006, name="Lukas Schmidt", program="SE Master"),
                models.Student(student_id=1007, name="Sophie Wagner", program="SE Master"),
                models.Student(student_id=1008, name="Leon Becker", program="Data Science Master"),
                models.Student(student_id=1009, name="Marie Hoffmann", program="SE Master"),
                models.Student(student_id=1010, name="Julia Alumni", program="SE Master", status="graduated"),
                models.Student(student_id=1011, name="Tom Graduated", program="Data Science Master", status="graduated"),
                models.Student(student_id=1012, name="Markus Failed", program="SE Master", status="failed"),
            ]
            db.add_all(students)
            db.commit()

            course_names = [
                "Software Architecture", "Software Product Line Engineering",
                "Machine Learning", "Data Mining", "Advanced Databases",
                "Cloud Computing", "Requirements Engineering", "Project Management"
            ]
            courses = [models.Course(course_name=name) for name in course_names]
            courses.append(models.Course(course_name="Legacy Systems 2018", is_archived=True))
            courses.append(models.Course(course_name="Old Data Structures", is_archived=True))
            db.add_all(courses)
            db.commit()

            exams = []
            for c in courses:
                exams.append(models.Exam(course_id=c.course_id, semester="SOSE_25"))
                exams.append(models.Exam(course_id=c.course_id, semester="WISE_25"))
                exams.append(models.Exam(course_id=c.course_id, semester="SOSE_26"))
            db.add_all(exams)
            db.commit()

            results_dict = {}
            for s in students:
                sampled_exams = random.sample(exams, random.randint(8, 12))
                for e in sampled_exams:
                    grade = random.choices(
                        [1.0, 1.3, 1.7, 2.0, 2.3, 2.7, 3.0, 3.3, 3.7, 4.0, 5.0],
                        weights=[5, 10, 15, 20, 15, 10, 5, 5, 5, 5, 15], k=1
                    )[0]
                    key = (s.student_id, e.course_id)
                    if key not in results_dict or grade < results_dict[key]['grade']:
                        results_dict[key] = {'exam_id': e.exam_id, 'grade': grade, 'passed': grade <= 4.0}
                    
                    if grade > 4.0:
                        retry_exam = next((ex for ex in exams if ex.course_id == e.course_id and ex.exam_id != e.exam_id), None)
                        if retry_exam:
                            retry_grade = random.choices([1.0, 1.3, 1.7, 2.0, 2.3, 2.7, 3.0, 3.3, 3.7, 4.0], weights=[5,10,15,20,15,10,10,5,5,5], k=1)[0]
                            if retry_grade < results_dict[key]['grade']:
                                results_dict[key] = {'exam_id': retry_exam.exam_id, 'grade': retry_grade, 'passed': True}
                                
            results = [models.ExamResult(student_id=k[0], exam_id=v['exam_id'], grade=v['grade'], passed=v['passed']) for k, v in results_dict.items()]
            db.add_all(results)
            db.commit()
    except Exception as e:
        print("Seed error:", e)

seed_db()

@app.get("/")
def read_root():
    return {"message": "Welcome to the SPA Backend API!"}

@app.get("/api/grades/")
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

@app.post("/api/grades/")
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

@app.get("/api/courses/")
def get_courses(db: Session = Depends(get_db)):
    """
    Retrieves the list of all courses alongside success metrics (pass rate, average grade) per course.
    """
    courses = db.query(models.Course).all()
    data = []
    for c in courses:
        exams = c.exams
        results = []
        marks_detailed = []
        semesters = set()
        for e in exams:
            semesters.add(e.semester)
            results.extend(e.results)
            for r in e.results:
                marks_detailed.append({
                    "student_id": r.student.student_id if r.student else None,
                    "student_name": r.student.name if r.student else "Unknown",
                    "program": r.student.program if r.student else "Unknown",
                    "semester": e.semester,
                    "grade": r.grade,
                    "passed": r.passed,
                    "version": r.version
                })
        
        total = len(results)
        passed_results = [r for r in results if r.passed]
        passed = len(passed_results)
        avg_grade = sum(r.grade for r in passed_results) / passed if passed > 0 else 0
        
        # Sort semesters safely. E.g. SOSE_25, WISE_25. We can just take max() string-wise for a naive approach
        # or simply join them if there are multiple. For simplicity, we'll sort alphabetically and pick the last.
        latest_semester = sorted(list(semesters))[-1] if semesters else "N/A"

        data.append({
            "course_id": c.course_id,
            "course_name": c.course_name,
            "assigned_professor": getattr(c, 'professor', 'Not Assigned'),
            "semester": c.semester if getattr(c, 'semester', None) else latest_semester,
            "study_program": getattr(c, 'study_program', 'Not Assigned'),
            "total_attempts": total,
            "pass_rate": round((passed / total * 100), 1) if total > 0 else 0,
            "avg_grade": round(avg_grade, 2),
            "is_archived": c.is_archived,
            "version": c.version,
            "marks": marks_detailed
        })
    return data

class CourseArchiveUpdate(BaseModel):
    is_archived: bool
    version: int

@app.put("/api/courses/{course_id}/archive")
def update_course_archive(course_id: int, update: CourseArchiveUpdate, db: Session = Depends(get_db)):
    c = db.query(models.Course).filter(models.Course.course_id == course_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Course not found")
    if c.version != update.version:
        raise HTTPException(status_code=409, detail="Data modified by another user. Please refresh.")
    c.is_archived = update.is_archived
    try:
        db.commit()
    except StaleDataError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Data modified by another user. Please refresh.")
    return {"status": "success"}

class CourseCreate(BaseModel):
    course_id: int = None
    course_name: str
    semester: str
    study_program: str
    professor: str = "Not Assigned"

@app.post("/api/courses/", dependencies=[Depends(verify_token)])
def create_course(course: CourseCreate, db: Session = Depends(get_db)):
    if course.course_id:
        existing_id = db.query(models.Course).filter(models.Course.course_id == course.course_id).first()
        if existing_id:
            raise HTTPException(status_code=409, detail="Course ID already exists")
            
    existing = db.query(models.Course).filter(models.Course.course_name == course.course_name).first()
    if existing:
        raise HTTPException(status_code=409, detail="Course name already exists")
        
    new_course = models.Course(
        course_id=course.course_id if course.course_id else abs(hash(course.course_name)) % (10 ** 8),
        course_name=course.course_name,
        semester=course.semester,
        study_program=course.study_program,
        professor=course.professor
    )
    db.add(new_course)
    db.commit()
    return {"status": "success", "course_id": new_course.course_id, "course_name": new_course.course_name}

from typing import Optional
class CourseUpdate(BaseModel):
    new_course_id: Optional[int] = None
    course_name: str
    semester: str
    study_program: str
    professor: str = "Not Assigned"
    version: int

@app.put("/api/courses/{course_id}", dependencies=[Depends(verify_token)])
def update_course(course_id: int, course: CourseUpdate, db: Session = Depends(get_db)):
    c = db.query(models.Course).filter(models.Course.course_id == course_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Course not found")
    if c.version != course.version:
        raise HTTPException(status_code=409, detail="Data modified by another user. Please refresh.")
        
    if course.new_course_id and course.new_course_id != course_id:
        existing_id = db.query(models.Course).filter(models.Course.course_id == course.new_course_id).first()
        if existing_id:
            raise HTTPException(status_code=409, detail="Course ID already exists")
        c.course_id = course.new_course_id

    c.course_name = course.course_name
    c.semester = course.semester
    c.study_program = course.study_program
    c.professor = course.professor
    
    try:
        db.commit()
    except StaleDataError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Data modified by another user. Please refresh.")
    return {"status": "success", "message": "Course updated successfully"}

@app.get("/api/students/")
def get_students(db: Session = Depends(get_db)):
    """
    Retrieves the complete student roster with their aggregate performance metrics (average grade, credits).
    """
    students = db.query(models.Student).all()
    data = []
    for s in students:
        results = s.results
        total = len(results)
        passed_results = [r for r in results if r.passed]
        passed = len(passed_results)
        avg_grade = sum(r.grade for r in passed_results) / passed if passed > 0 else 0
        
        data.append({
            "student_id": s.student_id,
            "name": s.name,
            "program": s.program,
            "status": s.status,
            "total_exams": total,
            "passed_exams": passed,
            "avg_grade": round(avg_grade, 2),
            "version": s.version
        })
    return data

@app.get("/api/students/{student_id}")
def get_student_details(student_id: int, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
        
    transcript = []
    course_attempts = {}
    
    # Sort by exam_id to approximate chronological order
    sorted_results = sorted(student.results, key=lambda r: r.exam_id)
    
    for r in sorted_results:
        c_name = r.exam.course.course_name
        course_attempts[c_name] = course_attempts.get(c_name, 0) + 1
        transcript.append({
            "result_id": r.result_id,
            "student_id": student.student_id,
            "name": student.name,
            "course": c_name,
            "semester": r.exam.semester,
            "grade": r.grade,
            "passed": r.passed,
            "version": r.version,
            "attempt": course_attempts[c_name],
            "version": r.version
        })
        
    transcript.sort(key=lambda x: (x["course"], x["attempt"]))
        
    return {
        "student_id": student.student_id,
        "name": student.name,
        "program": student.program,
        "status": student.status,
        "version": student.version,
        "transcript": transcript
    }

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



@app.post("/api/students/", dependencies=[Depends(verify_token)])
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    """
    [User Story: Profile Creation]
    Creates a new student profile and stores it in the database.
    Enforces authorization and performs a 409 Conflict check if the Student ID already exists.
    """
    """
    [User Story: Profile Creation]
    Creates a new student profile and stores it in the database.
    Enforces authorization and performs a 409 Conflict check if the Student ID already exists.
    """
    existing = db.query(models.Student).filter(models.Student.student_id == student.student_id).first()
    if existing:
        raise HTTPException(status_code=409, detail="Student ID already exists")
    
    new_student = models.Student(
        student_id=student.student_id,
        name=student.name,
        program=student.program,
        status=student.status
    )
    db.add(new_student)
    db.commit()
    return {"status": "success", "student_id": new_student.student_id}

@app.put("/api/students/{student_id}", dependencies=[Depends(verify_token)])
def update_student(student_id: int, update: StudentUpdate, db: Session = Depends(get_db)):
    """
    [User Story: Profile Editing]
    Updates an existing student profile.
    Validates the student exists and enforces optimistic locking (version check).
    Includes conflict handling if a modified Student ID collides with an existing one.
    """
    """
    [User Story: Profile Editing]
    Updates an existing student profile.
    Validates the student exists and enforces optimistic locking (version check).
    Includes conflict handling if a modified Student ID collides with an existing one.
    """
    student = db.query(models.Student).filter(models.Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    if student.version != update.version:
        raise HTTPException(status_code=409, detail="Data modified by another user. Please refresh.")
        
    if update.new_student_id and update.new_student_id != student_id:
        existing = db.query(models.Student).filter(models.Student.student_id == update.new_student_id).first()
        if existing:
            raise HTTPException(status_code=409, detail="Student ID already exists")
        student.student_id = update.new_student_id

    student.program = update.program
    student.name = update.name
    student.status = update.status
    
    try:
        db.commit()
    except StaleDataError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Data modified by another user. Please refresh.")
        
    return {"status": "success"}

class AddGradeRequest(BaseModel):
    course_id: int
    semester: str
    grade: float

@app.post("/api/students/{student_id}/grades")
def add_student_grade(student_id: int, request: AddGradeRequest, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
        
    course = db.query(models.Course).filter(models.Course.course_id == request.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    exam = db.query(models.Exam).filter(models.Exam.course_id == request.course_id, models.Exam.semester == request.semester).first()
    if not exam:
        exam = models.Exam(course_id=request.course_id, semester=request.semester)
        db.add(exam)
        db.commit()

    passed = request.grade <= 4.0
    existing = db.query(models.ExamResult).join(models.Exam).filter(models.ExamResult.student_id == student.student_id, models.Exam.course_id == exam.course_id).first()
    if existing:
        if request.grade < existing.grade:
            existing.grade = request.grade
            existing.passed = passed
            existing.exam_id = exam.exam_id
            db.commit()
    else:
        res = models.ExamResult(student_id=student.student_id, exam_id=exam.exam_id, grade=request.grade, passed=passed)
        db.add(res)
        db.commit()
    return {"status": "success"}

class StudentStatusUpdate(BaseModel):
    status: str
    version: int

@app.put("/api/students/{student_id}/status")
def update_student_status(student_id: int, update: StudentStatusUpdate, db: Session = Depends(get_db)):
    s = db.query(models.Student).filter(models.Student.student_id == student_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Student not found")
    s.status = update.status
    db.commit()
    return {"status": "success"}

@app.get("/api/stats/")
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


@app.post("/api/upload/preview/")
async def upload_file_preview(
    file: UploadFile = File(...),
    course: str = Form(None),
    courseName: str = Form(None),
    ects: str = Form(None),
    semester: str = Form(None),
    mapping: str = Form(None),
    nameSplitRule: str = Form(None),
    db: Session = Depends(get_db)
):
    import json
    import math
    if not file.filename.endswith(('.xlsx', '.xls', '.csv', '.tsv', '.ods')):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an Excel, CSV, TSV, or ODS file.")
    
    preview_data = []
    try:
        contents = await file.read()
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        elif file.filename.endswith('.tsv'):
            df = pd.read_csv(io.BytesIO(contents), sep='\t')
        elif file.filename.endswith('.ods'):
            df = pd.read_excel(io.BytesIO(contents), engine='odf')
        else:
            df = pd.read_excel(io.BytesIO(contents))
            
        column_mapping = {}
        if mapping:
            try:
                column_mapping = json.loads(mapping)
                df = df.rename(columns=column_mapping)
            except Exception as e:
                print("Mapping parsing error", e)
                
        if nameSplitRule and 'name' in df.columns:
            if nameSplitRule == 'Last, First':
                split_names = df['name'].str.split(',', n=1, expand=True)
                if split_names.shape[1] == 2:
                    df['last_name'] = split_names[0].str.strip()
                    df['first_name'] = split_names[1].str.strip()
            elif nameSplitRule == 'First Last':
                split_names = df['name'].str.split(' ', n=1, expand=True)
                if split_names.shape[1] == 2:
                    df['first_name'] = split_names[0].str.strip()
                    df['last_name'] = split_names[1].str.strip()

        # Build preview data
        for _, row in df.iterrows():
            record = {
                "student_id": str(row.get('student_id', '')),
                "first_name": str(row.get('first_name', '')),
                "last_name": str(row.get('last_name', '')),
                "name": str(row.get('name', '')),
                "program": str(row.get('program', '')),
                "semester": str(row.get('semester', semester or '')),
                "grade": str(row.get('grade', ''))
            }
            
            # Clean up NaNs
            for k in record:
                if record[k].lower() == 'nan':
                    record[k] = ''

            # Check required fields
            missing = []
            if not record['student_id']:
                missing.append('Matrikelnummer')
            if not record['first_name'] and not record['name']:
                missing.append('First Name')
            if not record['last_name'] and not record['name']:
                missing.append('Last Name')
            if not record['program']:
                missing.append('Study Program')
            if not record['semester']:
                missing.append('Semester')

            record['missing_fields'] = missing
            record['is_valid'] = len(missing) == 0
            
            preview_data.append(record)

        return {"status": "success", "preview_data": preview_data}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Could not parse file: {str(e)}")


@app.post("/api/upload/confirm/")
async def upload_confirm(req: UploadConfirmRequest, db: Session = Depends(get_db)):
    """
    [User Story: Permanent Archive & No Partial Saves]
    Receives the vetted records from the frontend preview grid and saves them permanently.
    Uses atomic transactions (db.flush() and rollback on error) to guarantee no partial saves.
    """
    try:
        # 1. Ensure course exists, or create it
        c_name = req.courseName if req.courseName else "Unnamed Course"
        course_obj = db.query(models.Course).filter(models.Course.course_name == c_name).first()
        if not course_obj:
            c_id = abs(hash(c_name)) % (10 ** 8)
            c_ects = int(req.ects) if req.ects and req.ects.isdigit() else 6
            course_obj = models.Course(course_id=c_id, course_name=c_name)
            db.add(course_obj)
            db.flush()
            
        # 2. Ensure exam exists
        exam = db.query(models.Exam).filter(models.Exam.course_id == course_obj.course_id, models.Exam.semester == req.semester).first()
        if not exam:
            exam = models.Exam(course_id=course_obj.course_id, semester=req.semester)
            db.add(exam)
            db.flush()
        
        # 3. Process records
        for rec in req.records:
            try:
                sid = int(float(rec.student_id))
                student = db.query(models.Student).filter(models.Student.student_id == sid).first()
                
                if not student:
                    s_name = "Unknown"
                    if rec.first_name and rec.last_name:
                        s_name = f"{rec.first_name} {rec.last_name}"
                    elif rec.name:
                        s_name = rec.name
                    
                    student = models.Student(student_id=sid, name=s_name, program=rec.program)
                    db.add(student)
                    db.flush()
                
                raw_g = rec.grade.strip().lower()
                # If they explicitly checked an NA/TA, the frontend converts it to '5.0'.
                # Any row sent here is intended for import.
                if raw_g in ['ta', 'at', 'ne', 'na', 'nan', '']:
                    raise ValueError(f"Invalid grade {raw_g} sent for import.")
                    
                grade = float(rec.grade)
                passed = grade <= 4.0
                
                res = models.ExamResult(student_id=student.student_id, exam_id=exam.exam_id, grade=grade, passed=passed)
                db.add(res)
            except Exception as e:
                print("Error processing row:", e)
                db.rollback()
                raise HTTPException(status_code=400, detail=f"Error processing row for student {rec.student_id}: {str(e)}")
        
        db.commit()
        return {"status": "success", "message": f"Successfully imported {len(req.records)} records."}
    except HTTPException:
        raise
    except Exception as e:
        print("Upload confirm error:", e)
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload/")
async def upload_grades(
    file: UploadFile = File(...),
    semester: str = Form(...),
    course: str = Form(...),
    courseName: str = Form(None),
    ects: str = Form(None),
    mapping: str = Form(None),
    nameSplitRule: str = Form(None),
    db: Session = Depends(get_db)
):
    import json
    if not file.filename.endswith(('.xlsx', '.xls', '.csv', '.tsv', '.ods')):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an Excel, CSV, TSV, or ODS file.")
    
    preview_data = []
    try:
        contents = await file.read()
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        elif file.filename.endswith('.tsv'):
            df = pd.read_csv(io.BytesIO(contents), sep='\t')
        elif file.filename.endswith('.ods'):
            df = pd.read_excel(io.BytesIO(contents), engine='odf')
        else:
            df = pd.read_excel(io.BytesIO(contents))
            
        # Parse mapping if provided
        column_mapping = {}
        if mapping:
            try:
                column_mapping = json.loads(mapping)
                # Reverse mapping: frontend sends { "Matrikelnr": "student_id", ... }
                # Actually, frontend UI might be sending it however we define it.
                # Let's assume we map "Matrikelnr" -> "student_id"
                df.rename(columns=column_mapping, inplace=True)
            except Exception as e:
                print("Mapping parsing error", e)
                
        # Handle Name Splitting
        if nameSplitRule and 'name' in df.columns:
            if nameSplitRule == 'Last, First':
                # Example: Schneider, Lena
                split_names = df['name'].str.split(',', n=1, expand=True)
                if split_names.shape[1] == 2:
                    df['last_name'] = split_names[0].str.strip()
                    df['first_name'] = split_names[1].str.strip()
            elif nameSplitRule == 'First Last':
                # Example: Lena Schneider
                split_names = df['name'].str.split(' ', n=1, expand=True)
                if split_names.shape[1] == 2:
                    df['first_name'] = split_names[0].str.strip()
                    df['last_name'] = split_names[1].str.strip()

        # Validation check for columns
        if 'student_id' not in df.columns or 'grade' not in df.columns:
            raise HTTPException(status_code=400, detail="Missing required columns: student_id or grade")
            
        # Do not insert into DB during preview. Just return all records for confirmation.
        df = df.fillna("")
        
        # Add is_valid flag
        df['is_valid'] = True
        
        preview_data = df.to_dict(orient="records")
    except Exception as e:
        print("General error:", e)
        raise HTTPException(status_code=500, detail=str(e))
    
    return {
        "status": "success", 
        "message": f"Successfully processed {file.filename} for course {course} in {semester}",
        "records_processed": len(df) if 'df' in locals() else 0,
        "preview_data": preview_data
    }
