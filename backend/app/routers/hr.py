"""
HR API endpoints.

Supplementary endpoints for HR dashboard.
"""

from typing import List
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.database import get_db
from app.schemas.hr import HRRequestResponse
from app.services import hr_service
from app.dependencies.security import require_hr_api_key

router = APIRouter(prefix="/hr", tags=["hr"])

# Initialize rate limiter for this router
limiter = Limiter(key_func=get_remote_address)


@router.get(
    "/requests",
    response_model=List[HRRequestResponse],
    dependencies=[Depends(require_hr_api_key)]
)
@limiter.limit("100/minute")  # Reasonable limit for authenticated HR staff
def get_hr_queue(
    request: Request,
    status: str | None = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Return the full HR request queue (requires API key).
    
    Rate limited to 100 requests per minute for authenticated users.
    """
    requests = hr_service.get_hr_queue(db, status=status, limit=limit, offset=offset)
    return requests


@router.get("/stats", dependencies=[Depends(require_hr_api_key)])
@limiter.limit("60/minute")  # Stats endpoint can be called frequently
def get_request_stats(request: Request, db: Session = Depends(get_db)):
    """
    Get request statistics by status.
    
    Rate limited to 60 requests per minute.
    Returns count of requests in each status for dashboard display.
    """
    counts = hr_service.get_request_count_by_status(db)
    return {
        "status_counts": counts,
        "total": sum(counts.values())
    }
