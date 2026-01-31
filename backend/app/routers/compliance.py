"""
Compliance API endpoints.

Endpoints for UAE compliance calendar.
"""

from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.compliance import (
    ComplianceEventCreate,
    ComplianceEventResponse,
    ComplianceCalendarSummary
)
from app.services import compliance_service

router = APIRouter(prefix="/compliance", tags=["compliance"])


@router.get("/events", response_model=List[ComplianceEventResponse])
def get_upcoming_events(
    days_ahead: int = Query(60, ge=1, le=365, description="Days to look ahead"),
    db: Session = Depends(get_db)
):
    """
    Get upcoming compliance events for the next N days.
    
    Default is 60 days. Used for compliance calendar widgets.
    """
    events = compliance_service.get_upcoming_events(db, days_ahead=days_ahead)
    return events


@router.get("/events/critical", response_model=List[ComplianceEventResponse])
def get_critical_events(
    days_ahead: int = Query(30, ge=1, le=90, description="Days to look ahead"),
    db: Session = Depends(get_db)
):
    """
    Get only critical compliance events.
    
    Returns events marked as 'critical' severity within the specified timeframe.
    Red-alert items only.
    """
    events = compliance_service.get_critical_events(db, days_ahead=days_ahead)
    return events


@router.get("/summary", response_model=ComplianceCalendarSummary)
def get_calendar_summary(
    days_ahead: int = Query(30, ge=1, le=365, description="Days to look ahead"),
    db: Session = Depends(get_db)
):
    """
    Get compliance calendar summary statistics.
    
    Returns counts by severity and timeframe.
    Useful for dashboard widgets.
    """
    summary = compliance_service.get_calendar_summary(db, days_ahead=days_ahead)
    return summary


@router.post("/events", response_model=ComplianceEventResponse)
def create_compliance_event(
    event_data: ComplianceEventCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new compliance event.
    
    Event types:
    - wps_deadline: WPS payment deadline (10th of month)
    - visa_expiry: Employee visa expiration
    - emirates_id_expiry: Emirates ID expiration
    - medical_expiry: Medical insurance expiration
    - ramadan_hours: Ramadan working hours reminder
    
    Severity levels:
    - normal: Standard tracking
    - warning: Needs attention soon (30 days or less)
    - critical: Urgent action required (7 days or less)
    """
    event = compliance_service.create_compliance_event(db, event_data.model_dump())
    return event
