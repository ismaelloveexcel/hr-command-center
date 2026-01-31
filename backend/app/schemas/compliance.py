"""
Compliance schemas.

Pydantic models for compliance calendar events.
"""

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ComplianceEventBase(BaseModel):
    """Base compliance event schema."""
    event_type: str = Field(..., description="Type of compliance event")
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    event_date: date
    alert_days_before: int = Field(7, ge=0, le=90)
    severity: str = Field("normal", description="normal, warning, or critical")
    related_entity: Optional[str] = Field(None, max_length=100)


class ComplianceEventCreate(ComplianceEventBase):
    """Schema for creating a compliance event."""
    pass


class ComplianceEventResponse(ComplianceEventBase):
    """Schema for compliance event response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    is_active: int
    created_at: datetime
    updated_at: datetime


class ComplianceCalendarSummary(BaseModel):
    """Summary of upcoming compliance events."""
    total_events: int
    critical_count: int
    warning_count: int
    normal_count: int
    upcoming_7_days: int
    upcoming_30_days: int
