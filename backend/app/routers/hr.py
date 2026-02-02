"""
HR API endpoints.

Supplementary endpoints for HR dashboard.
"""

import logging
from typing import List
from fastapi import APIRouter, Depends, Query, Request, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.hr import HRRequestResponse
from app.services import hr_service
from app.dependencies.security import require_hr_api_key
from app.core.rate_limit import apply_rate_limit
from app.models.request import RequestStatus

router = APIRouter(prefix="/hr", tags=["hr"])
logger = logging.getLogger(__name__)


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

    if status:
        status = status.lower().strip()
        valid_statuses = [s.value for s in RequestStatus]
        if status not in valid_statuses:
            logger.warning("Invalid status filter attempted: %s", status)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )

    try:
        requests = hr_service.get_hr_queue(db, status=status, limit=limit, offset=offset)
        return requests
    except Exception as e:
        logger.error("Failed to retrieve HR queue: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve request queue. Please try again later."
        )


@router.get("/stats", dependencies=[Depends(require_hr_api_key)])
def get_request_stats(http_request: Request, db: Session = Depends(get_db)):
    """
    Get request statistics by status.
    
    Rate limited to 60 requests per minute.
    Returns count of requests in each status for dashboard display.
    """
    # Apply rate limiting
    apply_rate_limit(http_request, "hr.get_request_stats", "60/minute")

    try:
        counts = hr_service.get_request_count_by_status(db)
        return {
            "status_counts": counts,
            "total": sum(counts.values())
        }
    except Exception as e:
        logger.error("Failed to retrieve request stats: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve statistics. Please try again later."
        )
