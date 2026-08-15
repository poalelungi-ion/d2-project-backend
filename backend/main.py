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
from routers import students, courses, upload, stats, grades
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
app.include_router(students.router, tags=["students"])
app.include_router(courses.router, tags=["courses"])
app.include_router(upload.router, tags=["upload"])
app.include_router(stats.router, tags=["stats"])
app.include_router(grades.router, tags=["grades"])


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




