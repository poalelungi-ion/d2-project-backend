from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session
from database import get_db
from dependencies import verify_token
import models, schemas
import pandas as pd
import io

router = APIRouter()

_FILE_EXTENSIONS = ('.xlsx', '.xls', '.csv', '.tsv', '.ods')


def _paste_separator(header_line: str) -> Optional[str]:
    """Pick a delimiter the way a spreadsheet paste usually arrives: tabs, then ;, then ,."""
    tabs = header_line.count('\t')
    semis = header_line.count(';')
    commas = header_line.count(',')
    if tabs > 0 and tabs >= commas and tabs >= semis:
        return '\t'
    if semis > commas:
        return ';'
    if commas > 0:
        return ','
    return None


def _read_paste(text: str) -> pd.DataFrame:
    """Parse copied cells (Excel/Sheets TSV, CSV, or semicolon CSV) into a dataframe."""
    stripped = text.strip().lstrip('\ufeff')
    lines = [line for line in stripped.splitlines() if line.strip()]
    if not lines:
        raise HTTPException(status_code=400, detail="Pasted data is empty.")
    sep = _paste_separator(lines[0])
    if sep is None:
        raise HTTPException(
            status_code=400,
            detail="Pasted data is not tabular. Copy cells from a spreadsheet or paste CSV.",
        )
    df = pd.read_csv(io.StringIO(stripped), sep=sep)
    if df.empty:
        raise HTTPException(status_code=400, detail="Pasted data has no data rows.")
    return df


def _read_file(filename: str, contents: bytes) -> pd.DataFrame:
    if filename.endswith('.csv'):
        return pd.read_csv(io.BytesIO(contents))
    if filename.endswith('.tsv'):
        return pd.read_csv(io.BytesIO(contents), sep='\t')
    if filename.endswith('.ods'):
        return pd.read_excel(io.BytesIO(contents), engine='odf')
    return pd.read_excel(io.BytesIO(contents))


@router.post("/api/upload/preview/")
async def upload_file_preview(
    file: Optional[UploadFile] = File(None),
    paste: Optional[str] = Form(None),
    course: str = Form(None),
    courseName: str = Form(None),
    ects: str = Form(None),
    semester: str = Form(None),
    mapping: str = Form(None),
    nameSplitRule: str = Form(None),
    db: Session = Depends(get_db)
):
    import json
    source_label = "file"
    try:
        if file is not None and file.filename:
            if not file.filename.endswith(_FILE_EXTENSIONS):
                raise HTTPException(
                    status_code=400,
                    detail="Invalid file type. Please upload an Excel, CSV, TSV, or ODS file.",
                )
            df = _read_file(file.filename, await file.read())
        elif paste is not None and paste.strip():
            source_label = "pasted data"
            df = _read_paste(paste)
        else:
            raise HTTPException(
                status_code=400,
                detail="Provide a spreadsheet file or paste tabular data.",
            )

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

        preview_data = []
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

            for k in record:
                if record[k].lower() == 'nan':
                    record[k] = ''

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
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        status = 400 if source_label == "pasted data" else 500
        raise HTTPException(status_code=status, detail=f"Could not parse {source_label}: {str(e)}")




@router.post("/api/upload/confirm/")
async def upload_confirm(req: schemas.UploadConfirmRequest, db: Session = Depends(get_db)):
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



@router.post("/api/upload/")
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
