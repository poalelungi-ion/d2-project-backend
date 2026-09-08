"""
Central Router Aggregator.
Registers all resource routers with appropriate tags and prefixes.
"""
from fastapi import APIRouter

from src.router import course, grades, stats, student, upload

api_router = APIRouter()
api_router.include_router(student.router, tags=["students"])
api_router.include_router(course.router, tags=["courses"])
api_router.include_router(grades.router, tags=["grades"])
api_router.include_router(upload.router, tags=["upload"])
api_router.include_router(stats.router, tags=["stats"])
