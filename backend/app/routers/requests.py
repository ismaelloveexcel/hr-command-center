"""
Request API endpoints.

Unified request system for the UAE HR Portal.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.database import get_db
from app.schemas.request import RequestCreate, RequestUpdate, RequestResponse
from app.schemas.tracking import RequestTrackingResponse
from app.services import request_service, tracking_service
from app.dependencies.security import require_hr_api_key

router = APIRouter(prefix="/requests", tags=["requests"])

# Initialize rate limiter for this router
limiter = Limiter(key_func=get_remote_address)


@router.post("", response_model=RequestResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/hour")  # Limit request creation to prevent spam
def create_request(
    request: Request,
    request_data: RequestCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new request (employee submit).
    
    Rate limited to 10 requests per hour per IP to prevent spam.
    The system automatically generates a unique reference (REF-YYYY-NNN)
    and sets status to 'submitted'.
    """
    try:
        db_request = request_service.create_request(db, request_data)
        return db_request
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create request: {str(e)}"
        )


@router.get("/{reference}", response_model=RequestTrackingResponse)
@limiter.limit("30/minute")  # Allow reasonable tracking frequency
def track_request(
    request: Request,
    reference: str,
    db: Session = Depends(get_db)
):
    """
    Track a request by reference (public access, no login required).
    
    Rate limited to 30 requests per minute per IP.
    Returns sanitized information suitable for employee viewing.
    Internal HR notes are NOT included in the response.
    """
    try:
        tracking_info = tracking_service.get_request_tracking(db, reference)
        return tracking_info
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve tracking information: {str(e)}"
        )


@router.patch(
    "/{reference}/status",
    response_model=RequestResponse,
    dependencies=[Depends(require_hr_api_key)]
)
@limiter.limit("100/minute")  # Higher limit for authenticated HR staff
def update_request_status(
    request: Request,
    reference: str,
    update_data: RequestUpdate,
    db: Session = Depends(get_db)
):
    """
    Update request status (HR updates).
    
    Rate limited to 100 requests per minute (authenticated endpoint).
    Valid status values: submitted, reviewing, approved, completed, rejected
    Requires HR API key authentication.
    """
    try:
        db_request = request_service.update_request_status(db, reference, update_data)
        return db_request
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update request: {str(e)}"
        )
