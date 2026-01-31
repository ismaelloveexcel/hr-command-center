"""
Request Schemas (Pydantic).

Placeholder schemas for request validation and serialization.
No validation rules defined at this stage.
"""

from typing import Optional
from datetime import datetime


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
