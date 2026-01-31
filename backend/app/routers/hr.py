"""
HR API endpoints.

Endpoints for HR staff to manage requests.
No authentication at this stage - HR is trusted.
"""

from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.hr import HRRequestResponse, HRRequestFilter
from app.services import hr_service

router = APIRouter(prefix="/hr", tags=["hr"])


@router.get("/requests", response_model=List[HRRequestResponse])
def get_hr_queue(
    status: str = Query(None, description="Filter by status (submitted, reviewing, approved, completed, rejected)"),
    limit: int = Query(50, ge=1, le=100, description="Number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: Session = Depends(get_db)
):
    """
    Get HR request queue.
    
    Returns all requests with internal notes (HR-only view).
    No authentication at this stage - HR is trusted.
    
    Supports filtering by status and pagination.
    """
    requests = hr_service.get_hr_queue(db, status=status, limit=limit, offset=offset)
    return requests


@router.get("/requests/stats")
def get_request_stats(db: Session = Depends(get_db)):
    """
    Get request statistics by status.
    
    Returns count of requests in each status.
    Useful for dashboard widgets.
    """
    counts = hr_service.get_request_count_by_status(db)
    return {
        "status_counts": counts,
        "total": sum(counts.values())
    }
