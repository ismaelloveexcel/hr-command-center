"""
Compliance service layer.

Business logic for UAE compliance calendar.
"""

from datetime import date, timedelta
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.compliance import ComplianceEvent


def calculate_wps_deadline(year: int, month: int) -> date:
    """
    Calculate WPS (Wage Protection System) deadline.
    
    WPS deadline is the 10th of each month for previous month's salaries.
    
    Args:
        year: Year
        month: Month (1-12)
        
    Returns:
        Date of WPS deadline (10th of the month)
    """
    return date(year, month, 10)


def calculate_visa_expiry_alerts(expiry_date: date, days_before: List[int] = [60, 30, 7]) -> List[date]:
    """
    Calculate visa expiry alert dates.
    
    UAE requires visa renewal well in advance.
    
    Args:
        expiry_date: Visa expiry date
        days_before: Days before expiry to alert (default: 60, 30, 7)
        
    Returns:
        List of alert dates
    """
    return [expiry_date - timedelta(days=days) for days in days_before]


def get_upcoming_events(
    db: Session,
    days_ahead: int = 60,
    include_inactive: bool = False
) -> List[ComplianceEvent]:
    """
    Get upcoming compliance events.
    
    Args:
        db: Database session
        days_ahead: Number of days to look ahead (default: 60)
        include_inactive: Include inactive events
        
    Returns:
        List of upcoming compliance events
    """
    today = date.today()
    end_date = today + timedelta(days=days_ahead)
    
    query = db.query(ComplianceEvent).filter(
        and_(
            ComplianceEvent.event_date >= today,
            ComplianceEvent.event_date <= end_date
        )
    )
    
    if not include_inactive:
        query = query.filter(ComplianceEvent.is_active == 1)
    
    return query.order_by(ComplianceEvent.event_date).all()


def get_critical_events(db: Session, days_ahead: int = 30) -> List[ComplianceEvent]:
    """
    Get critical compliance events in the next N days.
    
    Args:
        db: Database session
        days_ahead: Number of days to look ahead
        
    Returns:
        List of critical events
    """
    today = date.today()
    end_date = today + timedelta(days=days_ahead)
    
    return db.query(ComplianceEvent).filter(
        and_(
            ComplianceEvent.event_date >= today,
            ComplianceEvent.event_date <= end_date,
            ComplianceEvent.severity == "critical",
            ComplianceEvent.is_active == 1
        )
    ).order_by(ComplianceEvent.event_date).all()


def get_calendar_summary(db: Session, days_ahead: int = 30) -> dict:
    """
    Get summary statistics for compliance calendar.
    
    Args:
        db: Database session
        days_ahead: Number of days to look ahead
        
    Returns:
        Dictionary with summary counts
    """
    today = date.today()
    end_date = today + timedelta(days=days_ahead)
    seven_days = today + timedelta(days=7)
    
    # All active upcoming events
    all_events = db.query(ComplianceEvent).filter(
        and_(
            ComplianceEvent.event_date >= today,
            ComplianceEvent.event_date <= end_date,
            ComplianceEvent.is_active == 1
        )
    ).all()
    
    # Count by severity
    critical = sum(1 for e in all_events if e.severity == "critical")
    warning = sum(1 for e in all_events if e.severity == "warning")
    normal = sum(1 for e in all_events if e.severity == "normal")
    
    # Count by timeframe
    upcoming_7 = sum(1 for e in all_events if e.event_date <= seven_days)
    
    return {
        "total_events": len(all_events),
        "critical_count": critical,
        "warning_count": warning,
        "normal_count": normal,
        "upcoming_7_days": upcoming_7,
        "upcoming_30_days": len(all_events)
    }


def create_compliance_event(db: Session, event_data: dict) -> ComplianceEvent:
    """
    Create a new compliance event.
    
    Args:
        db: Database session
        event_data: Event data dictionary
        
    Returns:
        Created compliance event
    """
    event = ComplianceEvent(**event_data)
    db.add(event)
    db.commit()
    db.refresh(event)
    return event
