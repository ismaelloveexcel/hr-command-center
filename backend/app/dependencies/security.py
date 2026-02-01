"""
Security-related dependencies for FastAPI routes.

Provides reusable helpers for enforcing simple API-key based access
controls on sensitive HR endpoints.
"""

from fastapi import Header, HTTPException, status
from app.config import settings


def require_hr_api_key(x_hr_api_key: str | None = Header(None, alias="X-HR-API-Key")) -> None:
    """Validate the HR API key header before allowing access.

    Raises:
        HTTPException: If the API key is missing, misconfigured, or invalid.
    """
    expected_key = settings.hr_api_key

    if not expected_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="HR API key is not configured on the server."
        )

    if not x_hr_api_key or x_hr_api_key != expected_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing HR API key."
        )

    # Returning None is enough; dependency success allows request to proceed.
