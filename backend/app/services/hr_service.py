"""
HR service layer.

Business logic for HR staff operations.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.request import Request, RequestStatus


def get_hr_queue(
    db: Session,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> List[Request]:
    """
    Get HR request queue with filtering.
    
    Args:
        db: Database session
        status: Optional status filter
        limit: Maximum number of results
        offset: Offset for pagination
        
    Returns:
        List of requests (most recent first)
    """
    query = db.query(Request)
    
    # Filter by status if provided
    if status:
        try:
            status_enum = RequestStatus(status)
            query = query.filter(Request.status == status_enum)
        except ValueError:
            # Invalid status, return empty
            return []
    
    # Order by most recent first
    query = query.order_by(desc(Request.created_at))
    
    # Apply pagination
    query = query.limit(limit).offset(offset)
    
    return query.all()


def get_request_count_by_status(db: Session) -> dict:
    """
    Get count of requests by status.
    
    Args:
        db: Database session
        
    Returns:
        Dictionary with status counts
    """
    counts = {}
    
    for status in RequestStatus:
        count = db.query(Request).filter(Request.status == status).count()
        counts[status.value] = count
    
    return counts
