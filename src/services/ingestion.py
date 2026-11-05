"""
Ingestion Domain Service.
Handles file parsing (.xlsx, .xls, .csv, .tsv, .ods) and pasted spreadsheets,
column mapping, name splitting, preview validation, and atomic batch confirmation.
"""
import io
import json
import re
from typing import Optional
import pandas as pd
from fastapi import HTTPException, Response, UploadFile, status
from sqlalchemy.orm import Session

from src.database.models import Course, Exam, ExamResult, Student
from src.lib.column_names import (
    FIELD_LABEL,
    HeaderConflict,
    UnrecognizedHeaders,
    field_for_header,
    normalize_header,
    standardize_columns,
)
from src.lib.study_program import UNASSIGNED_PROGRAM, is_known_program, normalize_study_program
from src.router.dto import UploadConfirmRequest
from src.services.grade_outcome import (
    UnrecognizedGrade,
    evaluate_grade,
    is_filtered_status_code,
    is_ignored_column,
    is_valid_numeric_grade,
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

EXAM_EXTRA_COLUMN_NAMES = frozenset(
    {
        "points",
        "punkte",
        "gesamtpunkte",
        "summe",
        "total",
        "attended",
        "teilgenommen",
        "publish",
        "veroeffentlichen",
        "attest",
        "notes",
        "notizen",
        "bemerkung",
        "bemerkungen",
        "attempt",
        "versuch",
    }
)

_EXERCISE_HEADER_RE = re.compile(r"^(?:ex(?:ercise)?|aufgabe|task|q)?\s*\d+[a-z]?$", re.IGNORECASE)


def is_course_column(name: object) -> bool:
    """True for a header naming the course, in English or German, however punctuated."""
    return "".join(ch for ch in str(name).lower() if ch.isalnum()) in COURSE_COLUMN_NAMES


def is_ects_column(name: object) -> bool:
    """True for a header naming ECTS / credits, however punctuated."""
    return "".join(ch for ch in str(name).lower() if ch.isalnum()) in ECTS_COLUMN_NAMES


def is_exam_extra_column(name: object) -> bool:
    """True for exam point subtask columns (1a, 1b, 2a...) and grading sheet metadata (Points, Attended, Publish, Attest, Notes)."""
    raw = str(name).strip()
    if _EXERCISE_HEADER_RE.match(raw):
        return True
    alnum = "".join(ch for ch in raw.lower() if ch.isalnum())
    return alnum in EXAM_EXTRA_COLUMN_NAMES


def _is_dropped_column(name: object) -> bool:
    """Headers the parser never reads: pass/fail labels, course ids, ECTS, and exam points metadata."""
    return (
        is_ignored_column(name)
        or is_course_column(name)
        or is_ects_column(name)
        or is_exam_extra_column(name)
    )


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


_VALID_TARGET_FIELDS = frozenset(
    {"student_id", "name", "first_name", "last_name", "program", "semester", "grade"}
)
_IGNORE_TARGETS = frozenset({"ignore", "ignored", "—", "-", ""})


def _resolve_target_field(raw_target: object) -> Optional[str]:
    """Resolves a client-supplied target field or canonical display label to an internal field."""
    if raw_target is None:
        return "ignore"
    val = str(raw_target).strip()
    if val.lower() in _IGNORE_TARGETS:
        return "ignore"
    if val in _VALID_TARGET_FIELDS:
        return val
    alias = field_for_header(val)
    if alias is not None:
        return alias
    return None


async def extract_upload_headers(
    file: Optional[UploadFile],
    paste: Optional[str],
):
    """Reads a spreadsheet or pasted table and returns headers, row count, and sample values."""
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

        headers: list[str] = []
        samples: dict[str, str] = {}
        for raw_col in df.columns:
            col_name = str(raw_col).strip()
            norm = normalize_header(col_name)
            if not norm or norm.startswith("unnamed"):
                continue
            headers.append(col_name)
            sample_val = ""
            for val in df[raw_col]:
                text_val = str(val).strip()
                if text_val and text_val.lower() != "nan":
                    sample_val = f"e.g. {text_val}"
                    break
            if sample_val:
                samples[col_name] = sample_val

        return {
            "status": "success",
            "headers": headers,
            "row_count": int(len(df)),
            "samples": samples,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not inspect {source_label}: {str(e)}",
        )


def _apply_dynamic_mapping(df: pd.DataFrame, mapping_str: Optional[str]) -> pd.DataFrame:
    """
    Applies dynamic column mapping when supplied by the client, or falls back to
    strict header standardization when no mapping is provided.
    """
    client_map: Optional[dict[str, str]] = None
    if mapping_str and mapping_str.strip():
        try:
            parsed = json.loads(mapping_str)
            if isinstance(parsed, dict):
                client_map = {str(k).strip(): str(v).strip() for k, v in parsed.items()}
        except Exception:
            client_map = None

    if client_map is None:
        drop = [col for col in df.columns if _is_dropped_column(col)]
        if drop:
            df = df.drop(columns=drop)
        return df.rename(columns=standardize_columns(df.columns))

    rename: dict[object, str] = {}
    drop_cols: list[object] = []
    claimed: dict[str, str] = {}

    # First pass: honor explicit client mappings
    for raw_col in df.columns:
        col_str = str(raw_col)
        col_trimmed = col_str.strip()
        norm = normalize_header(col_str)
        if not norm or norm.startswith("unnamed"):
            drop_cols.append(raw_col)
            continue

        explicit_raw = client_map.get(col_str, client_map.get(col_trimmed))
        if explicit_raw is not None:
            resolved = _resolve_target_field(explicit_raw)
            if resolved == "ignore" or resolved is None:
                drop_cols.append(raw_col)
                continue
            prev = claimed.get(resolved)
            if prev is not None:
                label = FIELD_LABEL.get(resolved, resolved)
                raise HeaderConflict(
                    f"Columns '{prev}' and '{col_trimmed}' both standardise to {label}. Keep exactly one."
                )
            claimed[resolved] = col_trimmed
            rename[raw_col] = resolved

    # Second pass: handle columns not explicitly listed in client_map
    for raw_col in df.columns:
        if raw_col in rename or raw_col in drop_cols:
            continue
        col_str = str(raw_col)
        col_trimmed = col_str.strip()
        if _is_dropped_column(col_str):
            drop_cols.append(raw_col)
            continue
        inferred = field_for_header(col_str)
        if inferred is not None and inferred not in claimed:
            claimed[inferred] = col_trimmed
            rename[raw_col] = inferred
        else:
            # Extra unmapped columns (e.g., 1a, 1b, Points, Attended, Notes) are ignored
            drop_cols.append(raw_col)

    if drop_cols:
        df = df.drop(columns=drop_cols)
    return df.rename(columns=rename)


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

        try:
            df = _apply_dynamic_mapping(df, mapping)
        except (UnrecognizedHeaders, HeaderConflict) as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc

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
                "student_id": re.sub(r"\.0$", "", str(row.get("student_id", "")).strip()),
                "first_name": str(row.get("first_name", "")).strip(),
                "last_name": str(row.get("last_name", "")).strip(),
                "name": str(row.get("name", "")).strip(),
                "program": str(row.get("program", "")).strip(),
                "semester": re.sub(r"\.0$", "", str(row.get("semester", semester or "")).strip()),
                "grade": str(row.get("grade", "")).strip(),
            }

            for k in record:
                if str(record[k]).lower() == "nan":
                    record[k] = ""

            # Skip spreadsheet summary footer rows (e.g., Max:, Max Achieved:, Average:)
            # that have no student identifier and no student name.
            if (
                not record["student_id"]
                and not record["first_name"]
                and not record["last_name"]
                and not record["name"]
            ):
                continue

            # NE/EX/NA/TA/AT are not grades. Empty cells have no grade.
            # Skip rows where a student has no grade (#104085)
            if not record["grade"].strip() or is_filtered_status_code(record["grade"]):
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
        # [Ticket #104085: Exclude students without valid grades from database persistence]
        # Rows lacking a valid numeric grade are excluded from persistence.
        # No orphan student profiles without exam grade entries are created in PostgreSQL.
        valid_records = []
        for rec in req.records:
            if not is_valid_numeric_grade(rec.grade):
                continue
            try:
                verdict = evaluate_grade(rec.grade)
                if verdict.grade is not None and 1.0 <= verdict.grade <= 5.0:
                    valid_records.append((rec, verdict))
            except UnrecognizedGrade:
                continue

        # If records were sent but none have a valid numeric grade, reject with 400
        if req.records and not valid_records:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No records with valid numeric grades to import.",
            )

        # 1. Resolve the course -- the active one when the upload came from a Course view
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

        # 3. Process records (only valid records are persisted; students are only created
        # when an exam result is also created, preventing orphan student profiles)
        imported_count = 0
        for rec, verdict in valid_records:
            try:
                sid = int(float(rec.student_id))
            except (ValueError, TypeError):
                continue

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

            res = ExamResult(
                student_id=student.student_id,
                exam_id=exam.exam_id,
                grade=verdict.grade,
                passed=verdict.passed,
                absence_code=verdict.absence_code,
                attempt_type=req.attemptType,
            )
            db.add(res)
            imported_count += 1

        db.commit()
        return {
            "status": "success",
            "message": f"Successfully imported {imported_count} records.",
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
