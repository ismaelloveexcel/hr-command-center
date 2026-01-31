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
    
    Future attributes might include:
    - title: str
    - description: str
    - status: str
    
    No validation rules or Field constraints at this stage.
    """
    pass


class RequestCreate(RequestBase):
    """
    Schema for creating a new request.
    Placeholder only - no actual fields or validation.
    """
    pass


class RequestUpdate(RequestBase):
    """
    Schema for updating an existing request.
    Placeholder only - no actual fields or validation.
    """
    pass


class RequestResponse(RequestBase):
    """
    Schema for request response.
    Placeholder only - no actual fields or validation.
    
    Future attributes might include:
    - id: int
    - created_at: datetime
    - updated_at: datetime
    """
    pass
