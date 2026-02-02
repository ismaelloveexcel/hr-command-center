"""
Security-related dependencies for FastAPI routes.

Provides reusable helpers for enforcing simple API-key based access
controls on sensitive HR endpoints.
"""

import hmac
import logging
from fastapi import Header, HTTPException, status
from app.config import settings

logger = logging.getLogger(__name__)


def _constant_time_compare(a: str | None, b: str) -> bool:
    if a is None:
        return False
    return hmac.compare_digest(a.encode("utf-8"), b.encode("utf-8"))


def require_hr_api_key(x_hr_api_key: str | None = Header(None, alias="X-HR-API-Key")) -> None:
    """Validate the HR API key header before allowing access.

    Raises:
        HTTPException: If the API key is missing, misconfigured, or invalid.
    """
    expected_key = settings.hr_api_key

    if not expected_key:
        logger.error("HR API key is not configured on the server.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="HR API key is not configured on the server."
        )

    if not x_hr_api_key or not _constant_time_compare(x_hr_api_key, expected_key):
        logger.warning("Invalid HR API key attempt.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing HR API key."
        )

    # Returning None is enough; dependency success allows request to proceed.
