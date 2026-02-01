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

router = APIRouter(prefix="/hr", tags=["hr"])


def get_limiter(http_request: Request):
    """Get the rate limiter from app state."""
    return http_request.app.state.limiter


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
    # Apply rate limiting using shared limiter from app state
    limiter = get_limiter(http_request)
    if limiter.enabled:
        limiter.limit("100/minute")(lambda: None)()
    
    requests = hr_service.get_hr_queue(db, status=status, limit=limit, offset=offset)
    return requests


@router.get("/stats", dependencies=[Depends(require_hr_api_key)])
def get_request_stats(http_request: Request, db: Session = Depends(get_db)):
    """
    Get request statistics by status.
    
    Rate limited to 60 requests per minute.
    Returns count of requests in each status for dashboard display.
    """
    # Apply rate limiting using shared limiter from app state
    limiter = get_limiter(http_request)
    if limiter.enabled:
        limiter.limit("60/minute")(lambda: None)()
    
    counts = hr_service.get_request_count_by_status(db)
    return {
        "status_counts": counts,
        "total": sum(counts.values())
    }
