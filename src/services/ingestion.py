"""
Ingestion Domain Service.
Handles file parsing (.xlsx, .xls, .csv, .tsv, .ods) and pasted spreadsheets,
column mapping, name splitting, preview validation, and atomic batch confirmation.
"""
import io
import json
from typing import Optional
import pandas as pd
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from src.database.models import Course, Exam, ExamResult, Student
from src.router.dto import UploadConfirmRequest

_FILE_EXTENSIONS = (".xlsx", ".xls", ".csv", ".tsv", ".ods")

# A blank study program is a minor gap, not a broken record: it is filled with
# this placeholder instead of failing validation and losing the row.
UNASSIGNED_PROGRAM = "Unassigned / Unknown"


def _paste_separator(header_line: str) -> Optional[str]:
    tabs = header_line.count("\t")
    semis = header_line.count(";")
    commas = header_line.count(",")
    if tabs > 0 and tabs >= commas and tabs >= semis:
        return "\t"
    if semis > commas:
        return ";"
    if commas > 0:
        return ","
    return None


def _read_paste(text: str) -> pd.DataFrame:
    stripped = text.strip().lstrip("\ufeff")
    lines = [line for line in stripped.splitlines() if line.strip()]
    if not lines:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Pasted data is empty.")
    sep = _paste_separator(lines[0])
    if sep is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pasted data is not tabular. Copy cells from a spreadsheet or paste CSV.",
        )
    df = pd.read_csv(io.StringIO(stripped), sep=sep)
    if df.empty:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Pasted data has no data rows.")
    return df


def _read_file(filename: str, contents: bytes) -> pd.DataFrame:
    if filename.endswith(".csv"):
        return pd.read_csv(io.BytesIO(contents))
    if filename.endswith(".tsv"):
        return pd.read_csv(io.BytesIO(contents), sep="\t")
    if filename.endswith(".ods"):
        return pd.read_excel(io.BytesIO(contents), engine="odf")
    return pd.read_excel(io.BytesIO(contents))


async def preview_upload(
    file: Optional[UploadFile],
    paste: Optional[str],
    course: Optional[str],
    courseName: Optional[str],
    ects: Optional[str],
    semester: Optional[str],
    mapping: Optional[str],
    nameSplitRule: Optional[str],
    db: Session,
):
    source_label = "file"
    try:
        if file is not None and file.filename:
            if not file.filename.endswith(_FILE_EXTENSIONS):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid file type. Please upload an Excel, CSV, TSV, or ODS file.",
                )
            contents = await file.read()
            df = _read_file(file.filename, contents)
        elif paste is not None and paste.strip():
            source_label = "pasted data"
            df = _read_paste(paste)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Provide a spreadsheet file or paste tabular data.",
            )

        if mapping:
            try:
                column_mapping = json.loads(mapping)
                df = df.rename(columns=column_mapping)
            except Exception as e:
                print("Mapping parsing error:", e)

        if nameSplitRule and "name" in df.columns:
            if nameSplitRule == "Last, First":
                split_names = df["name"].str.split(",", n=1, expand=True)
                if split_names.shape[1] == 2:
                    df["last_name"] = split_names[0].str.strip()
                    df["first_name"] = split_names[1].str.strip()
            elif nameSplitRule == "First Last":
                split_names = df["name"].str.split(" ", n=1, expand=True)
                if split_names.shape[1] == 2:
                    df["first_name"] = split_names[0].str.strip()
                    df["last_name"] = split_names[1].str.strip()

        preview_data = []
        for _, row in df.iterrows():
            record = {
                "student_id": str(row.get("student_id", "")),
                "first_name": str(row.get("first_name", "")),
                "last_name": str(row.get("last_name", "")),
                "name": str(row.get("name", "")),
                "program": str(row.get("program", "")),
                "semester": str(row.get("semester", semester or "")),
                "grade": str(row.get("grade", "")),
            }

            for k in record:
                if str(record[k]).lower() == "nan":
                    record[k] = ""

            # Fill the placeholder here rather than only on save, so the review
            # grid shows exactly what will be written to the database.
            record["program"] = record["program"].strip() or UNASSIGNED_PROGRAM

            missing = []
            if not record["student_id"]:
                missing.append("Matrikelnummer")
            if not record["first_name"] and not record["name"]:
                missing.append("First Name")
            if not record["last_name"] and not record["name"]:
                missing.append("Last Name")
            if not record["semester"]:
                missing.append("Semester")

            record["missing_fields"] = missing
            record["is_valid"] = len(missing) == 0
            preview_data.append(record)

        return {"status": "success", "preview_data": preview_data}
    except HTTPException:
        raise
    except Exception as e:
        status_code = status.HTTP_400_BAD_REQUEST if source_label == "pasted data" else status.HTTP_500_INTERNAL_SERVER_ERROR
        raise HTTPException(status_code=status_code, detail=f"Could not parse {source_label}: {str(e)}")


def confirm_upload(db: Session, req: UploadConfirmRequest):
    """
    [AC2: Atomic Transactions & No Partial Saves]
    Saves imported records in a single database transaction.
    Guarantees that on any exception, db.rollback() executes and no partial data remains.
    """
    try:
        # 1. Ensure course exists
        c_name = req.courseName if req.courseName else "Unnamed Course"
        course_obj = db.query(Course).filter(Course.course_name == c_name).first()
        if not course_obj:
            c_id = abs(hash(c_name)) % (10**8)
            course_obj = Course(course_id=c_id, course_name=c_name)
            db.add(course_obj)
            db.flush()

        # 2. Ensure exam exists
        exam = (
            db.query(Exam)
            .filter(Exam.course_id == course_obj.course_id, Exam.semester == req.semester)
            .first()
        )
        if not exam:
            exam = Exam(course_id=course_obj.course_id, semester=req.semester)
            db.add(exam)
            db.flush()

        # 3. Process records
        for rec in req.records:
            sid = int(float(rec.student_id))
            student = db.query(Student).filter(Student.student_id == sid).first()

            if not student:
                s_name = "Unknown"
                if rec.first_name and rec.last_name:
                    s_name = f"{rec.first_name} {rec.last_name}"
                elif rec.name:
                    s_name = rec.name

                # The review grid is editable, so re-apply the fallback here for
                # a program that was cleared after the preview normalised it.
                s_program = rec.program.strip() or UNASSIGNED_PROGRAM
                student = Student(student_id=sid, name=s_name, program=s_program)
                db.add(student)
                db.flush()

            raw_g = rec.grade.strip().lower()
            if raw_g in ["ta", "at", "ne", "na", "nan", ""]:
                raise ValueError(f"Invalid grade {raw_g} sent for import.")

            grade = float(rec.grade)
            passed = grade <= 4.0

            res = ExamResult(
                student_id=student.student_id,
                exam_id=exam.exam_id,
                grade=grade,
                passed=passed,
                attempt_type=req.attemptType,
            )
            db.add(res)

        db.commit()
        return {"status": "success", "message": f"Successfully imported {len(req.records)} records."}
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
