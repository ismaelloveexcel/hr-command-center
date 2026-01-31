"""
Notification Model.

Track notification logs (stub implementation - no real API calls).
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.database import Base


class NotificationLog(Base):
    """
    Notification log table.
    
    Logs all notifications that would be sent.
    No actual API calls to SMS/email services at this stage.
    """
    __tablename__ = "notification_log"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Notification details
    notification_type = Column(String(50), nullable=False, index=True)
    # Types: request_created, status_updated, compliance_alert
    
    recipient = Column(String(200), nullable=False)  # Email or phone
    subject = Column(String(200), nullable=True)
    message = Column(Text, nullable=False)
    
    # Trigger context
    trigger_entity_type = Column(String(50), nullable=True)  # request, compliance_event
    trigger_entity_id = Column(Integer, nullable=True)
    
    # Status
    status = Column(String(20), default="logged")  # logged, would_send
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<NotificationLog {self.notification_type} to {self.recipient}>"
