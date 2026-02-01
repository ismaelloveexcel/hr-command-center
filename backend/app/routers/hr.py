"""
HR API endpoints.

Supplementary endpoints for HR dashboard.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import hr_service

router = APIRouter(prefix="/hr", tags=["hr"])


@router.get("/stats")
def get_request_stats(db: Session = Depends(get_db)):
    """
    Get request statistics by status.
    
    Returns count of requests in each status for dashboard display.
    """
    counts = hr_service.get_request_count_by_status(db)
    return {
        "status_counts": counts,
        "total": sum(counts.values())
    }
