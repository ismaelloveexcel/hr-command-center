"""
Request tracking service.

Public tracking functionality for employees (no authentication required).
"""

from sqlalchemy.orm import Session
from app.models.request import Request
from app.schemas.tracking import RequestTrackingResponse, TimelineEvent


# Friendly status labels
STATUS_LABELS = {
    "submitted": "Submitted - Awaiting Review",
    "reviewing": "Under Review",
    "approved": "Approved",
    "completed": "Completed",
    "rejected": "Not Approved"
}

# Next steps guidance
NEXT_STEPS = {
    "submitted": "Your request is in the queue. HR will review it shortly.",
    "reviewing": "HR is currently reviewing your request. You will be notified of any updates.",
    "approved": "Your request has been approved. HR will proceed with the next steps.",
    "completed": "Your request has been completed. No further action needed.",
    "rejected": "Your request was not approved. Please contact HR for more information."
}


def get_request_tracking(db: Session, reference: str) -> RequestTrackingResponse:
    """
    Get sanitized request tracking information for public access.
    
    Args:
        db: Database session
        reference: Request reference (e.g., REF-2026-001)
        
    Returns:
        Sanitized tracking response (no internal HR notes)
        
    Raises:
        ValueError: If request not found
    """
    # Get request
    request = db.query(Request).filter(Request.reference == reference).first()
    
    if not request:
        raise ValueError(f"Request {reference} not found")
    
    # Build timeline
    timeline = []
    
    # Submission event
    timeline.append(TimelineEvent(
        timestamp=request.submitted_at,
        status="submitted",
        description="Request submitted",
        notes=None
    ))
    
    # Review events (if reviewed)
    if request.reviewed_at and request.status.value != "submitted":
        timeline.append(TimelineEvent(
            timestamp=request.reviewed_at,
            status=request.status.value,
            description=f"Status changed to {STATUS_LABELS.get(request.status.value, request.status.value)}",
            notes=request.public_notes  # Only public notes
        ))
    
    # Build response
    status_value = request.status.value
    
    return RequestTrackingResponse(
        reference=request.reference,
        title=request.title,
        description=request.description,
        current_status=status_value,
        submitted_at=request.submitted_at,
        timeline=timeline,
        last_updated=request.updated_at,
        status_label=STATUS_LABELS.get(status_value, status_value),
        next_steps=NEXT_STEPS.get(status_value)
    )
