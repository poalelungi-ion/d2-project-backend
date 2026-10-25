"""
Ingestion Domain Service.
Handles file parsing (.xlsx, .xls, .csv, .tsv, .ods) and pasted spreadsheets,
column mapping, name splitting, preview validation, and atomic batch confirmation.
"""
import io
from typing import Optional
import pandas as pd
from fastapi import HTTPException, Response, UploadFile, status
from sqlalchemy.orm import Session

from src.database.models import Course, Exam, ExamResult, Student
from src.lib.column_names import HeaderConflict, UnrecognizedHeaders, standardize_columns
from src.lib.study_program import UNASSIGNED_PROGRAM, is_known_program, normalize_study_program
from src.router.dto import UploadConfirmRequest
from src.services.grade_outcome import (
    UnrecognizedGrade,
    evaluate_grade,
    is_filtered_status_code,
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

# ECTS/credits are not tracked. Drop those headers so they cannot be mapped
# onto a field or fail a later closed-name check.
ECTS_COLUMN_NAMES = frozenset(
    {
        "ects",
        "credit",
        "credits",
        "ectscredit",
        "ectscredits",
        "kreditpunkte",
        "leistungspunkte",
    }
)


def is_course_column(name: object) -> bool:
    """True for a header naming the course, in English or German, however punctuated."""
    return "".join(ch for ch in str(name).lower() if ch.isalnum()) in COURSE_COLUMN_NAMES


def is_ects_column(name: object) -> bool:
    """True for a header naming ECTS / credits, however punctuated."""
    return "".join(ch for ch in str(name).lower() if ch.isalnum()) in ECTS_COLUMN_NAMES


def _is_dropped_column(name: object) -> bool:
    """Headers the parser never reads: pass/fail labels, course ids, and ECTS."""
    return is_ignored_column(name) or is_course_column(name) or is_ects_column(name)


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
    df = pd.read_csv(io.StringIO(stripped), sep=sep, keep_default_na=False)
    if df.empty:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Pasted data has no data rows.")
    return df


def _read_file(filename: str, contents: bytes) -> pd.DataFrame:
    if not contents or len(contents) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file is empty (0 bytes). Please select or upload a valid spreadsheet with student grades.",
        )
    try:
        if filename.endswith(".csv"):
            return pd.read_csv(io.BytesIO(contents), keep_default_na=False)
        if filename.endswith(".tsv"):
            return pd.read_csv(io.BytesIO(contents), sep="\t", keep_default_na=False)
        if filename.endswith(".ods"):
            return pd.read_excel(io.BytesIO(contents), engine="odf", keep_default_na=False)
        if filename.endswith(".xlsx"):
            return pd.read_excel(io.BytesIO(contents), engine="openpyxl", keep_default_na=False)
        if filename.endswith(".xls"):
            return pd.read_excel(io.BytesIO(contents), keep_default_na=False)
        return pd.read_excel(io.BytesIO(contents), engine="openpyxl", keep_default_na=False)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not parse spreadsheet file: {str(e)}",
        )


async def preview_upload(
    file: Optional[UploadFile],
    paste: Optional[str],
    course: Optional[str],
    courseName: Optional[str],
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

        # Pass/fail labels and course identifiers are noise. Drop them before
        # the remaining headers are checked against the closed name list.
        # ECTS/credits are also not tracked and are removed before validation.
        drop = [col for col in df.columns if _is_dropped_column(col)]
        if drop:
            df = df.drop(columns=drop)

        try:
            df = df.rename(columns=standardize_columns(df.columns))
        except (UnrecognizedHeaders, HeaderConflict) as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc

        # Client-supplied mapping is ignored: standard names are enforced here
        # so a typo cannot be aliased onto the wrong field.
        _ = mapping

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

            # NE/EX/NA/TA/AT are not grades. Drop the row so the student is not tracked.
            if is_filtered_status_code(record["grade"]):
                continue

            # Fill the placeholder or normalize common abbreviations here so the review
            # grid shows clean canonical values and resolves aliases.
            record["program"] = normalize_study_program(record["program"])

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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not parse {source_label}: {str(e)}",
        )


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


def convert_paste_to_excel(paste_text: str, filename: Optional[str] = "pasted_table.xlsx") -> Response:
    """Converts a pasted tabular string into an openpyxl .xlsx file stream."""
    df = _read_paste(paste_text)
    out = io.BytesIO()
    with pd.ExcelWriter(out, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Grades")
    excel_bytes = out.getvalue()
    safe_name = filename if filename and filename.endswith(".xlsx") else f"{filename or 'pasted_table'}.xlsx"
    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{safe_name}"'},
    )
