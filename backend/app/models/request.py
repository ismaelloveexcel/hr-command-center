"""
Request Model (SQLAlchemy).

Database model for request management.
"""

from enum import Enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SQLEnum
from app.database import Base


class RequestStatus(Enum):
    """
    Request lifecycle status enumeration.
    
    Defines the possible states a request can be in during its lifecycle.
    """
    SUBMITTED = "submitted"
    REVIEWING = "reviewing"
    APPROVED = "approved"
    COMPLETED = "completed"
    REJECTED = "rejected"


class Request(Base):
    """
    Request database model.
    
    Represents an employee request in the HR system.
    """
    __tablename__ = "requests"
    
    id = Column(Integer, primary_key=True, index=True)
    reference = Column(String(20), unique=True, index=True, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(
        SQLEnum(RequestStatus, values_callable=lambda obj: [e.value for e in obj]),
        default=RequestStatus.SUBMITTED,
        nullable=False
    )
    
    # Employee information
    submitted_by = Column(String(100), nullable=False)
    submitted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # HR review information
    reviewed_by = Column(String(100), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    
    # Notes
    public_notes = Column(Text, nullable=True)  # Visible to employee
    internal_notes = Column(Text, nullable=True)  # HR-only
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<Request {self.reference}: {self.title}>"
