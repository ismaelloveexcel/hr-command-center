"""
Request Model (SQLAlchemy).

Placeholder for database model representing a request entity.
No database connection or actual implementation at this stage.
"""

from enum import Enum


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


class Request:
    """
    Placeholder for Request database model.
    
    This is a structure placeholder only - no SQLAlchemy Base,
    no table definition, no database connection.
    
    Expected attributes (COMMENTED ONLY - not implemented):
    - id: Primary key (integer, auto-increment)
    - reference: Unique request reference (e.g., REF-2026-001)
    - title: Request title (string, required)
    - description: Request description (text, optional)
    - status: Current status (RequestStatus enum, default: SUBMITTED)
    - submitted_by: Employee identifier (string, required)
    - submitted_at: Submission timestamp (datetime, auto-set)
    - reviewed_by: HR staff identifier (string, optional)
    - reviewed_at: Review timestamp (datetime, optional)
    - public_notes: Notes visible to employee (text, optional)
    - internal_notes: HR-only notes (text, optional)
    - created_at: Record creation timestamp (datetime, auto-set)
    - updated_at: Record update timestamp (datetime, auto-update)
    """
    pass
