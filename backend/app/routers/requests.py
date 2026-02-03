"""
Request API endpoints.

Unified request system for the UAE HR Portal.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request, Path
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.request import RequestCreate, RequestUpdate, RequestResponse
from app.schemas.tracking import RequestTrackingResponse
from app.services import request_service, tracking_service
from app.dependencies.security import require_hr_api_key
from app.core.rate_limit import apply_rate_limit
from app.core.validation import validate_reference_format, sanitize_text

router = APIRouter(prefix="/requests", tags=["requests"])
logger = logging.getLogger(__name__)


@router.post("", response_model=RequestResponse, status_code=status.HTTP_201_CREATED)
def create_request(
    http_request: Request,
    request_data: RequestCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new request (employee submit).
    
    Rate limited to 10 requests per hour per IP to prevent spam.
    The system automatically generates a unique reference (REF-YYYY-NNN)
    and sets status to 'submitted'.
    """
    # Apply rate limiting
    apply_rate_limit(http_request, "requests.create_request", "10/hour")
    
    try:
        db_request = request_service.create_request(db, request_data)
        return db_request
    except ValueError as e:
        logger.info("Validation error creating request: %s", e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Failed to create request: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create request. Please try again later."
        )


@router.get("/{reference}", response_model=RequestTrackingResponse)
def track_request(
    http_request: Request,
    reference: str = Path(..., description="Request reference (REF-YYYY-NNN)"),
    db: Session = Depends(get_db)
):
    """
    Track a request by reference (public access, no login required).
    
    Rate limited to 30 requests per minute per IP.
    Returns sanitized information suitable for employee viewing.
    Internal HR notes are NOT included in the response.
    """
    # Apply rate limiting
    apply_rate_limit(http_request, "requests.track_request", "30/minute")
    
    try:
        reference = sanitize_text(reference, max_length=20)
        reference = reference.upper() if reference else reference
        if not reference or not validate_reference_format(reference):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reference format. Expected format: REF-YYYY-NNN"
            )

        tracking_info = tracking_service.get_request_tracking(db, reference)
        return tracking_info
    except ValueError as e:
        logger.info("Request not found for reference: %s", reference)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found."
        )
    except Exception as e:
        logger.error("Failed to retrieve tracking information for %s: %s", reference, e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve tracking information. Please try again later."
        )


@router.patch(
    "/{reference}/status",
    response_model=RequestResponse,
    dependencies=[Depends(require_hr_api_key)]
)
def update_request_status(
    http_request: Request,
    reference: str = Path(..., description="Request reference (REF-YYYY-NNN)"),
    update_data: RequestUpdate,
    db: Session = Depends(get_db)
):
    """
    Update request status (HR updates).
    
    Rate limited to 100 requests per minute (authenticated endpoint).
    Valid status values: submitted, reviewing, approved, completed, rejected
    Requires HR API key authentication.
    """
    # Apply rate limiting
    apply_rate_limit(http_request, "requests.update_request_status", "100/minute")
    
    try:
        reference = sanitize_text(reference, max_length=20)
        reference = reference.upper() if reference else reference
        if not reference or not validate_reference_format(reference):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reference format. Expected format: REF-YYYY-NNN"
            )

        db_request = request_service.update_request_status(db, reference, update_data)
        return db_request
    except ValueError as e:
        logger.info("Validation error updating request %s: %s", reference, e)
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Request not found."
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Failed to update request %s: %s", reference, e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update request. Please try again later."
        )
