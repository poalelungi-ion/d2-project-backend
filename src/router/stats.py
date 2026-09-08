"""
Statistics Router (HTTP Controller).
Serves dashboard KPIs, failure trends, and course rankings.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.database.connection import get_db
from src.services import stats as stats_service

router = APIRouter()


@router.get("/api/stats/", summary="Get dashboard analytics and KPIs")
def get_stats(db: Session = Depends(get_db)):
    """Retrieves key performance indicators for the Analysis Hub."""
    return stats_service.get_dashboard_stats(db)
