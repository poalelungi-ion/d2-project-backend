"""
Central Router Aggregator.
Registers all resource routers with appropriate tags and prefixes.
"""
from fastapi import APIRouter, Depends

from src.lib.auth.validator import get_current_user
from src.router import auth, course, grades, stats, student, upload

protected = [Depends(get_current_user)]

api_router = APIRouter()
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(student.router, tags=["students"], dependencies=protected)
api_router.include_router(course.router, tags=["courses"], dependencies=protected)
api_router.include_router(grades.router, tags=["grades"], dependencies=protected)
api_router.include_router(upload.router, tags=["upload"], dependencies=protected)
api_router.include_router(stats.router, tags=["stats"], dependencies=protected)
