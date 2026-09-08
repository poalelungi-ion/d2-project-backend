"""
Upload and Ingestion Router (HTTP Controller).
Handles spreadsheet uploads, interactive preview, and permanent batch confirmation.
"""
from typing import Optional
from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from src.database.connection import get_db
from src.router.dto import UploadConfirmRequest
from src.services import ingestion as ingestion_service

router = APIRouter()


@router.post("/api/upload/preview/", summary="Preview uploaded or pasted exam data")
async def upload_file_preview(
    file: Optional[UploadFile] = File(None),
    paste: Optional[str] = Form(None),
    course: Optional[str] = Form(None),
    courseName: Optional[str] = Form(None),
    ects: Optional[str] = Form(None),
    semester: Optional[str] = Form(None),
    mapping: Optional[str] = Form(None),
    nameSplitRule: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    """Parses file or pasted tabular data and validates fields before confirmation."""
    return await ingestion_service.preview_upload(
        file, paste, course, courseName, ects, semester, mapping, nameSplitRule, db
    )


@router.post("/api/upload/confirm/", summary="Confirm and persist vetted exam records")
async def upload_confirm(req: UploadConfirmRequest, db: Session = Depends(get_db)):
    """Permanently archives vetted exam records using an atomic database transaction."""
    return ingestion_service.confirm_upload(db, req)


@router.post("/api/upload/", summary="Direct file upload preview (legacy)")
async def upload_grades(
    file: UploadFile = File(...),
    semester: str = Form(...),
    course: str = Form(...),
    courseName: Optional[str] = Form(None),
    ects: Optional[str] = Form(None),
    mapping: Optional[str] = Form(None),
    nameSplitRule: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    """Direct file upload preview compatibility endpoint."""
    return await ingestion_service.preview_upload(
        file=file,
        paste=None,
        course=course,
        courseName=courseName,
        ects=ects,
        semester=semester,
        mapping=mapping,
        nameSplitRule=nameSplitRule,
        db=db,
    )
