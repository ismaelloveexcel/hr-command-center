"""
Request API endpoints.

Unified request system for the UAE HR Portal.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.request import RequestCreate, RequestUpdate, RequestResponse
from app.schemas.tracking import RequestTrackingResponse
from app.services import request_service, tracking_service
from app.dependencies.security import require_hr_api_key

router = APIRouter(prefix="/requests", tags=["requests"])


@router.post("", response_model=RequestResponse, status_code=status.HTTP_201_CREATED)
def create_request(
    request_data: RequestCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new request (employee submit).
    
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
def track_request(
    reference: str,
    db: Session = Depends(get_db)
):
    """
    Track a request by reference (public access, no login required).
    
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
def update_request_status(
    reference: str,
    update_data: RequestUpdate,
    db: Session = Depends(get_db)
):
    """
    Update request status (HR updates).
    
    Valid status values: submitted, reviewing, approved, completed, rejected
    No authentication at this stage.
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
