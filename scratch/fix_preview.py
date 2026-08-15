import re

with open(r'c:\Users\ionut\Desktop\Project\SPA_System\backend\main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Make first_name and last_name optional in ConfirmRecord
content = re.sub(
    r'class ConfirmRecord\(BaseModel\):\n    student_id: str\n    first_name: str\n    last_name: str',
    r'class ConfirmRecord(BaseModel):\n    student_id: str\n    first_name: str = ""\n    last_name: str = ""',
    content
)

old_preview = """        # Check required columns
        if 'student_id' in df.columns and 'grade' in df.columns:
            # 1. Ensure course exists, or create it
            c_name = courseName if courseName else "Unnamed Course"
            course_obj = db.query(models.Course).filter(models.Course.course_name == c_name).first()
            if not course_obj:
                # Generate a pseudo-random ID based on the course name string
                c_id = abs(hash(c_name)) % (10 ** 8)
                c_ects = int(ects) if ects and ects.isdigit() else 6
                course_obj = models.Course(course_id=c_id, course_name=c_name)
                db.add(course_obj)
                db.commit()
                
            # 2. Ensure exam exists for this course and semester
            exam = db.query(models.Exam).filter(models.Exam.course_id == course_obj.course_id, models.Exam.semester == semester).first()
            if not exam:
                exam = models.Exam(course_id=course_obj.course_id, semester=semester)
                db.add(exam)
                db.commit()
            
            # 3. Process records
            for _, row in df.iterrows():
                try:
                    sid = int(float(row['student_id']))
                    student = db.query(models.Student).filter(models.Student.student_id == sid).first()
                    
                    if not student:
                        s_name = "Unknown"
                        if 'name' in df.columns:
                            s_name = str(row['name'])
                        elif 'first_name' in df.columns and 'last_name' in df.columns:
                            s_name = f"{row['first_name']} {row['last_name']}"
                        
                        s_prog = str(row['program']) if 'program' in df.columns else "Unknown"
                        
                        student = models.Student(student_id=sid, name=s_name, program=s_prog)
                        db.add(student)
                        db.commit()
                    
                    raw_g = str(row['grade']).strip().upper()
                    if raw_g in ['TA', 'AT', 'NE']:
                        continue # F.3 Ignore absences
                    try:
                        grade = float(row['grade'])
                    except ValueError:
                        continue
                    if grade < 1.0 or grade > 5.0:
                        continue
                    
                    passed = grade <= 4.0
                    # Append new attempt instead of overwriting
                    res = models.ExamResult(student_id=student.student_id, exam_id=exam.exam_id, grade=grade, passed=passed)
                    db.add(res)
                except Exception as e:
                    print("Error processing row:", e)
                    continue
            db.commit()
            
        preview_df = df.head(5).fillna("")
        preview_data = preview_df.to_dict(orient="records")"""

new_preview = """        # Validation check for columns
        if 'student_id' not in df.columns or 'grade' not in df.columns:
            raise HTTPException(status_code=400, detail="Missing required columns: student_id or grade")
            
        # Do not insert into DB during preview. Just return all records for confirmation.
        df = df.fillna("")
        
        # Add is_valid flag
        df['is_valid'] = True
        
        preview_data = df.to_dict(orient="records")"""

content = content.replace(old_preview, new_preview)

content = content.replace('"preview": preview_data', '"preview_data": preview_data')

with open(r'c:\Users\ionut\Desktop\Project\SPA_System\backend\main.py', 'w', encoding='utf-8') as f:
    f.write(content)
