"""
Request API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.request import RequestCreate, RequestUpdate, RequestResponse
from app.services import request_service

router = APIRouter(prefix="/requests", tags=["requests"])


@router.post("", response_model=RequestResponse, status_code=status.HTTP_201_CREATED)
def create_request(
    request_data: RequestCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new request.
    
    The system will automatically generate a unique reference (REF-YYYY-NNN)
    and set the status to 'submitted'.
    """
    try:
        db_request = request_service.create_request(db, request_data)
        return db_request
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create request: {str(e)}"
        )


@router.patch("/{reference}", response_model=RequestResponse)
def update_request(
    reference: str,
    update_data: RequestUpdate,
    db: Session = Depends(get_db)
):
    """
    Update request status and fields.
    
    This endpoint is primarily for HR staff to update request status.
    No authentication at this stage (stub HR check only).
    
    Valid status values: submitted, reviewing, approved, completed, rejected
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
