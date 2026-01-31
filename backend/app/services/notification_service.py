"""
Notification service (STUB implementation).

Logs notifications without sending them.
No real Twilio/email API calls at this stage.
"""

from typing import Optional
from sqlalchemy.orm import Session
from app.models.notification import NotificationLog


class NotificationService:
    """
    Notification service abstraction.
    
    This is a STUB implementation that only logs notifications.
    Real API integration (Twilio, SendGrid, etc.) will be added later.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def _log_notification(
        self,
        notification_type: str,
        recipient: str,
        message: str,
        subject: Optional[str] = None,
        trigger_entity_type: Optional[str] = None,
        trigger_entity_id: Optional[int] = None
    ) -> NotificationLog:
        """
        Log a notification (stub - doesn't actually send).
        
        Args:
            notification_type: Type of notification
            recipient: Recipient identifier (email/phone)
            message: Notification message
            subject: Optional subject line
            trigger_entity_type: Type of entity that triggered this
            trigger_entity_id: ID of entity that triggered this
            
        Returns:
            NotificationLog record
        """
        log = NotificationLog(
            notification_type=notification_type,
            recipient=recipient,
            subject=subject,
            message=message,
            trigger_entity_type=trigger_entity_type,
            trigger_entity_id=trigger_entity_id,
            status="logged"  # Would be "sent" in real implementation
        )
        
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        
        return log
    
    def notify_request_created(
        self,
        request_id: int,
        request_reference: str,
        submitted_by: str,
        title: str
    ):
        """
        Notify when a new request is created.
        
        In a real implementation, this would:
        - Send email to employee confirming submission
        - Notify HR staff of new request
        """
        # Employee notification
        employee_message = f"""
Your request has been submitted successfully.

Reference: {request_reference}
Title: {title}

You can track your request status at any time using your reference number.

Thank you,
UAE HR Portal Team
        """.strip()
        
        self._log_notification(
            notification_type="request_created",
            recipient=submitted_by,
            subject=f"Request Submitted - {request_reference}",
            message=employee_message,
            trigger_entity_type="request",
            trigger_entity_id=request_id
        )
        
        # HR notification (stub)
        hr_message = f"""
New request submitted:

Reference: {request_reference}
Title: {title}
Submitted by: {submitted_by}

Review the request in the HR queue.
        """.strip()
        
        self._log_notification(
            notification_type="request_created",
            recipient="hr.team@company.ae",
            subject=f"New Request - {request_reference}",
            message=hr_message,
            trigger_entity_type="request",
            trigger_entity_id=request_id
        )
    
    def notify_status_updated(
        self,
        request_id: int,
        request_reference: str,
        submitted_by: str,
        old_status: str,
        new_status: str,
        public_notes: Optional[str] = None
    ):
        """
        Notify when request status changes.
        
        In a real implementation, this would send SMS/email to employee.
        """
        status_messages = {
            "reviewing": "Your request is now under review.",
            "approved": "Good news! Your request has been approved.",
            "completed": "Your request has been completed.",
            "rejected": "Your request was not approved. Please contact HR for details."
        }
        
        status_message = status_messages.get(new_status, f"Status updated to: {new_status}")
        
        message = f"""
Request Status Update

Reference: {request_reference}
New Status: {status_message}
"""
        
        if public_notes:
            message += f"\nNotes: {public_notes}"
        
        message += "\n\nTrack your request at: [portal link]/track"
        
        self._log_notification(
            notification_type="status_updated",
            recipient=submitted_by,
            subject=f"Request Update - {request_reference}",
            message=message.strip(),
            trigger_entity_type="request",
            trigger_entity_id=request_id
        )
    
    def notify_critical_compliance_alert(
        self,
        event_id: int,
        event_title: str,
        event_date: str,
        days_until: int
    ):
        """
        Notify about critical compliance deadlines.
        
        In a real implementation, this would alert HR staff via SMS/email.
        """
        urgency = "URGENT" if days_until <= 7 else "IMPORTANT"
        
        message = f"""
{urgency} COMPLIANCE ALERT

{event_title}
Due Date: {event_date}
Time Remaining: {days_until} days

Please take immediate action to ensure compliance.

UAE HR Portal
        """.strip()
        
        self._log_notification(
            notification_type="compliance_alert",
            recipient="hr.compliance@company.ae",
            subject=f"{urgency}: {event_title}",
            message=message,
            trigger_entity_type="compliance_event",
            trigger_entity_id=event_id
        )


def get_notification_service(db: Session) -> NotificationService:
    """Get notification service instance."""
    return NotificationService(db)


def get_notification_logs(
    db: Session,
    notification_type: Optional[str] = None,
    limit: int = 100
):
    """
    Retrieve notification logs.
    
    Args:
        db: Database session
        notification_type: Optional filter by type
        limit: Maximum number of records
        
    Returns:
        List of notification logs
    """
    query = db.query(NotificationLog)
    
    if notification_type:
        query = query.filter(NotificationLog.notification_type == notification_type)
    
    return query.order_by(NotificationLog.created_at.desc()).limit(limit).all()
