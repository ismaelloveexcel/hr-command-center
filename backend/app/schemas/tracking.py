"""
Public tracking schemas.

Schemas for employee-safe request tracking (no internal data).
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class TimelineEvent(BaseModel):
    """A single event in the request timeline."""
    timestamp: datetime
    status: str
    description: str
    notes: Optional[str] = None  # Only public notes


class RequestTrackingResponse(BaseModel):
    """
    Public tracking response for employees.
    
    This response is sanitized - no internal HR notes or sensitive data.
    """
    reference: str
    title: str
    description: Optional[str] = None
    current_status: str
    submitted_by: str
    submitted_at: datetime
    timeline: List[TimelineEvent] = Field(default_factory=list, description="Status change history")
    last_updated: datetime
    
    # Friendly status messages
    status_label: str = Field(description="Human-friendly status description")
    next_steps: Optional[str] = Field(None, description="What happens next")
