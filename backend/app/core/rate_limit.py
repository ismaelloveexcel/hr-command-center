"""
Rate limiting utilities for manual rate limit checking.

Provides a helper to apply rate limiting programmatically in endpoints.
"""

from fastapi import Request
from slowapi.errors import RateLimitExceeded


def apply_rate_limit(http_request: Request, endpoint_name: str, limit: str):
    """
    Apply rate limiting to an endpoint programmatically.
    
    Args:
        http_request: The FastAPI Request object
        endpoint_name: Unique name for this endpoint (used for tracking)
        limit: Rate limit string (e.g., "10/hour", "30/minute")
        
    Raises:
        RateLimitExceeded: If rate limit is exceeded
    """
    limiter = http_request.app.state.limiter
    
    # Skip if rate limiting is disabled (e.g., in tests)
    if not limiter.enabled:
        return
    
    # Check rate limit for this request
    # Note: Using private method as slowapi doesn't currently expose a public programmatic API
    # This is wrapped here to isolate the implementation detail and provide a stable interface
    # TODO: Monitor slowapi releases for public API alternatives to reduce coupling
    try:
        limiter._check_request_limit(
            http_request,
            endpoint_name,
            [limit],
            None,
            None,
            limiter._key_func,
            None
        )
    except Exception as e:
        # Re-raise RateLimitExceeded but wrap other exceptions
        if isinstance(e, RateLimitExceeded):
            raise
        # If something goes wrong with rate limiting, log it but don't block the request
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error checking rate limit: {e}")
