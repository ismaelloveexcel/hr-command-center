"""
UAE Compliance Calendar Model.

Track important UAE compliance dates and deadlines.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Date, DateTime, Text
from app.database import Base


class ComplianceEvent(Base):
    """
    UAE compliance calendar event.
    
    Tracks various UAE-specific compliance deadlines and alerts.
    """
    __tablename__ = "compliance_calendar_events"
    
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(50), nullable=False, index=True)
    # Event types: wps_deadline, visa_expiry, emirates_id_expiry, 
    #              medical_expiry, ramadan_hours
    
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Key dates
    event_date = Column(Date, nullable=False, index=True)
    alert_days_before = Column(Integer, default=7)  # When to start alerting
    
    # Severity for visual indicators
    severity = Column(String(20), default="normal")  # normal, warning, critical
    
    # Related entity (optional)
    related_entity = Column(String(100), nullable=True)  # Employee ID, company, etc.
    
    # Status
    is_active = Column(Integer, default=1)  # 1 = active, 0 = resolved/archived
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<ComplianceEvent {self.event_type}: {self.title}>"
