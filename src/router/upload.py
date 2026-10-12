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


@router.post("/api/upload/paste-to-excel/", summary="Convert pasted tabular text to Excel (.xlsx) file")
async def paste_to_excel(
    paste: str = Form(...),
    filename: Optional[str] = Form("pasted_table.xlsx"),
):
    """Parses tabular paste text and returns a downloadable/importable Excel (.xlsx) spreadsheet."""
    return ingestion_service.convert_paste_to_excel(paste, filename)

