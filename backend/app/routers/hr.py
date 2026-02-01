"""
HR API endpoints.

Supplementary endpoints for HR dashboard.
"""

from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.hr import HRRequestResponse
from app.services import hr_service
from app.dependencies.security import require_hr_api_key

router = APIRouter(prefix="/hr", tags=["hr"])


@router.get(
    "/requests",
    response_model=List[HRRequestResponse],
    dependencies=[Depends(require_hr_api_key)]
)
def get_hr_queue(
    status: str | None = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Return the full HR request queue (requires API key)."""
    requests = hr_service.get_hr_queue(db, status=status, limit=limit, offset=offset)
    return requests


@router.get("/stats", dependencies=[Depends(require_hr_api_key)])
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
