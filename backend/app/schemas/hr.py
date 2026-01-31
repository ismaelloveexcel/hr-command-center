"""
HR-specific schemas.

Schemas for HR staff operations (includes internal data).
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class HRRequestResponse(BaseModel):
    """
    HR-specific request response (includes internal notes).
    
    This response includes ALL data including internal HR notes.
    Should only be used for HR staff endpoints.
    """
    id: int
    reference: str
    title: str
    description: Optional[str] = None
    status: str
    submitted_by: str
    submitted_at: datetime
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    public_notes: Optional[str] = None
    internal_notes: Optional[str] = None  # HR-only field
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class HRRequestFilter(BaseModel):
    """Filter parameters for HR request queue."""
    status: Optional[str] = Field(None, description="Filter by status")
    limit: int = Field(50, ge=1, le=100, description="Number of results")
    offset: int = Field(0, ge=0, description="Offset for pagination")
