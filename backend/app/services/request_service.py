"""
Request service layer.

Business logic for request management.
"""

from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.request import Request, RequestStatus
from app.schemas.request import RequestCreate, RequestUpdate


def generate_reference(db: Session) -> str:
    """
    Generate unique request reference in format REF-YYYY-NNN.
    
    Args:
        db: Database session
        
    Returns:
        Unique reference string (e.g., REF-2026-001)
    """
    year = datetime.utcnow().year
    
    # Get the count of requests for this year
    count = db.query(func.count(Request.id)).filter(
        Request.reference.like(f"REF-{year}-%")
    ).scalar()
    
    # Generate next sequential number
    next_num = (count or 0) + 1
    
    return f"REF-{year}-{next_num:03d}"


def create_request(db: Session, request_data: RequestCreate) -> Request:
    """
    Create a new request.
    
    Args:
        db: Database session
        request_data: Request creation data
        
    Returns:
        Created request object
    """
    # Generate unique reference
    reference = generate_reference(db)
    
    # Create request
    db_request = Request(
        reference=reference,
        title=request_data.title,
        description=request_data.description,
        submitted_by=request_data.submitted_by,
        status=RequestStatus.SUBMITTED,
        submitted_at=datetime.utcnow()
    )
    
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    
    return db_request


def update_request_status(
    db: Session,
    reference: str,
    update_data: RequestUpdate
) -> Request:
    """
    Update request status and related fields.
    
    Args:
        db: Database session
        reference: Request reference (e.g., REF-2026-001)
        update_data: Update data
        
    Returns:
        Updated request object
        
    Raises:
        ValueError: If request not found
    """
    # Find request
    db_request = db.query(Request).filter(Request.reference == reference).first()
    
    if not db_request:
        raise ValueError(f"Request {reference} not found")
    
    # Update fields
    if update_data.status:
        # Validate status
        try:
            new_status = RequestStatus(update_data.status)
            db_request.status = new_status
            
            # Set reviewed_at when status changes
            if update_data.reviewed_by:
                db_request.reviewed_by = update_data.reviewed_by
                db_request.reviewed_at = datetime.utcnow()
        except ValueError:
            raise ValueError(f"Invalid status: {update_data.status}")
    
    if update_data.public_notes is not None:
        db_request.public_notes = update_data.public_notes
    
    if update_data.internal_notes is not None:
        db_request.internal_notes = update_data.internal_notes
    
    if update_data.reviewed_by:
        db_request.reviewed_by = update_data.reviewed_by
    
    db_request.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_request)
    
    return db_request


def get_request_by_reference(db: Session, reference: str) -> Request:
    """
    Get request by reference.
    
    Args:
        db: Database session
        reference: Request reference
        
    Returns:
        Request object or None
    """
    return db.query(Request).filter(Request.reference == reference).first()
