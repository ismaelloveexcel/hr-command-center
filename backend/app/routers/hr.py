"""
HR API endpoints.

Supplementary endpoints for HR dashboard.
"""

from typing import List
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.hr import HRRequestResponse
from app.services import hr_service
from app.dependencies.security import require_hr_api_key
from app.core.rate_limit import apply_rate_limit

router = APIRouter(prefix="/hr", tags=["hr"])


@router.get(
    "/requests",
    response_model=List[HRRequestResponse],
    dependencies=[Depends(require_hr_api_key)]
)
def get_hr_queue(
    http_request: Request,
    status: str | None = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Return the full HR request queue (requires API key).
    
    Rate limited to 100 requests per minute for authenticated users.
    """
    # Apply rate limiting
    apply_rate_limit(http_request, "hr.get_hr_queue", "100/minute")
    
    requests = hr_service.get_hr_queue(db, status=status, limit=limit, offset=offset)
    return requests


@router.get("/stats", dependencies=[Depends(require_hr_api_key)])
def get_request_stats(http_request: Request, db: Session = Depends(get_db)):
    """
    Get request statistics by status.
    
    Rate limited to 60 requests per minute.
    Returns count of requests in each status for dashboard display.
    """
    # Apply rate limiting
    apply_rate_limit(http_request, "hr.get_request_stats", "60/minute")
    
    counts = hr_service.get_request_count_by_status(db)
    return {
        "status_counts": counts,
        "total": sum(counts.values())
    }
