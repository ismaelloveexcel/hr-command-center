"""
Request schema placeholders (plain Python classes).

Placeholder schemas for future request validation and serialization.
No validation rules or Pydantic models defined at this stage.
"""

# NOTE: These are shape placeholders only.
# Do not add fields or validation until Phase 2 (Validation Layer).


class RequestBase:
    """
    Base Request schema placeholder.
    
    Expected fields (COMMENTED ONLY - not implemented):
    - title: Request title (string, required, max 200 chars)
    - description: Detailed description (string, optional, max 2000 chars)
    """
    pass


class RequestCreate(RequestBase):
    """
    Schema for creating a new request.
    
    Expected fields (COMMENTED ONLY - not implemented):
    - title: Request title (string, required)
    - description: Request description (string, optional)
    - submitted_by: Employee identifier (string, required)
    
    Auto-set by system:
    - reference: Generated unique reference (REF-YYYY-NNN)
    - status: Always starts as 'submitted'
    - submitted_at: Current timestamp
    """
    pass


class RequestUpdate(RequestBase):
    """
    Schema for updating an existing request.
    
    Expected fields (COMMENTED ONLY - not implemented):
    - status: New status (RequestStatus enum, optional)
    - public_notes: Notes visible to employee (string, optional)
    - internal_notes: HR-only notes (string, optional)
    - reviewed_by: HR staff identifier (string, optional)
    
    Auto-set by system:
    - reviewed_at: Timestamp when status changes
    - updated_at: Current timestamp
    """
    pass


class RequestResponse(RequestBase):
    """
    Schema for request response.
    
    Expected fields (COMMENTED ONLY - not implemented):
    - id: Request ID (integer)
    - reference: Unique reference (string, e.g., REF-2026-001)
    - title: Request title (string)
    - description: Request description (string, optional)
    - status: Current status (string)
    - submitted_by: Employee identifier (string)
    - submitted_at: Submission timestamp (datetime)
    - reviewed_by: HR staff identifier (string, optional)
    - reviewed_at: Review timestamp (datetime, optional)
    - public_notes: Employee-visible notes (string, optional)
    - created_at: Creation timestamp (datetime)
    - updated_at: Last update timestamp (datetime)
    
    Note: internal_notes should NOT be included in public responses
    """
    pass
