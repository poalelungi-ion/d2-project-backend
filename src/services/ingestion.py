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
from src.lib.study_program import UNASSIGNED_PROGRAM, is_known_program
from src.router.dto import UploadConfirmRequest
from src.services.grade_outcome import (
    UnrecognizedGrade,
    evaluate_grade,
    is_ignored_column,
)

_FILE_EXTENSIONS = (".xlsx", ".xls", ".csv", ".tsv", ".ods")

# The course an import belongs to comes from the Course view the lecturer
# started the upload in, never from the sheet. A course identifier column is
# therefore noise: it is dropped before validation, so it can neither be mapped
# onto a field nor be reported as a problem with the file.
COURSE_COLUMN_NAMES = frozenset(
    {
        "course",
        "courseid",
        "coursenumber",
        "courseno",
        "coursecode",
        "kurs",
        "kursid",
        "kursnummer",
        "modulnummer",
        "veranstaltungsnummer",
    }
)


def is_course_column(name: object) -> bool:
    """True for a header naming the course, in English or German, however punctuated."""
    return "".join(ch for ch in str(name).lower() if ch.isalnum()) in COURSE_COLUMN_NAMES


def _is_dropped_column(name: object) -> bool:
    """Headers the parser never reads: pass/fail labels and course identifiers."""
    return is_ignored_column(name) or is_course_column(name)


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
                column_mapping = {
                    source: target
                    for source, target in json.loads(mapping).items()
                    if not _is_dropped_column(source) and not _is_dropped_column(target)
                }
                df = df.rename(columns=column_mapping)
            except Exception as e:
                print("Mapping parsing error:", e)

        # Pass/fail labels are never a result and the course is already known —
        # drop both even if they survived mapping under their original header.
        drop = [col for col in df.columns if _is_dropped_column(col)]
        if drop:
            df = df.drop(columns=drop)

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
            invalid = []
            if not record["student_id"]:
                missing.append("Matrikelnummer")
            if not record["first_name"] and not record["name"]:
                missing.append("First Name")
            if not record["last_name"] and not record["name"]:
                missing.append("Last Name")
            if not is_known_program(record["program"]):
                invalid.append("Study Program")
            if not record["semester"]:
                missing.append("Semester")

            try:
                verdict = evaluate_grade(record["grade"])
                record["outcome"] = verdict.outcome
                record["absence_code"] = verdict.absence_code
            except UnrecognizedGrade:
                record["outcome"] = "invalid"
                record["absence_code"] = None
                missing.append("Grade")

            record["missing_fields"] = missing
            record["invalid_fields"] = invalid
            record["is_valid"] = len(missing) == 0 and len(invalid) == 0
            preview_data.append(record)

        return {"status": "success", "preview_data": preview_data}
    except HTTPException:
        raise
    except Exception as e:
        status_code = status.HTTP_400_BAD_REQUEST if source_label == "pasted data" else status.HTTP_500_INTERNAL_SERVER_ERROR
        raise HTTPException(status_code=status_code, detail=f"Could not parse {source_label}: {str(e)}")


def resolve_course(db: Session, req: UploadConfirmRequest) -> Course:
    """
    The course this import belongs to.

    An upload started from a Course view carries that view's courseId, so the
    records attach to exactly that course and nothing has to be inferred from
    the file or from a typed-in name. Only the standalone wizard, which has no
    active course, falls back to matching — then creating — a course by name.
    """
    if req.courseId is not None:
        course = db.query(Course).filter(Course.course_id == req.courseId).first()
        if course is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Course {req.courseId} not found.",
            )
        return course

    if req.course and req.course.isdigit():
        course_by_id = db.query(Course).filter(Course.course_id == int(req.course)).first()
        if course_by_id is not None:
            return course_by_id

    c_name = req.courseName if req.courseName else "Unnamed Course"
    course = db.query(Course).filter(Course.course_name == c_name).first()
    if course is None:
        cid = int(req.course) if (req.course and req.course.isdigit()) else abs(hash(c_name)) % (10**8)
        course = Course(course_id=cid, course_name=c_name)
        db.add(course)
        db.flush()
    return course


def confirm_upload(db: Session, req: UploadConfirmRequest):
    """
    [AC2: Atomic Transactions & No Partial Saves]
    Saves imported records in a single database transaction.
    Guarantees that on any exception, db.rollback() executes and no partial data remains.
    """
    try:
        # 1. Resolve the course — the active one when the upload came from a Course view
        course_obj = resolve_course(db, req)

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

            try:
                verdict = evaluate_grade(rec.grade)
            except UnrecognizedGrade as exc:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid grade for student {sid}: {exc}",
                ) from exc

            res = ExamResult(
                student_id=student.student_id,
                exam_id=exam.exam_id,
                grade=verdict.grade,
                passed=verdict.passed,
                absence_code=verdict.absence_code,
                attempt_type=req.attemptType,
            )
            db.add(res)

        db.commit()
        return {
            "status": "success",
            "message": f"Successfully imported {len(req.records)} records.",
            "course_id": course_obj.course_id,
        }
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
