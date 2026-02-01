"""Dependencies package for FastAPI route dependencies."""

from app.dependencies.security import require_hr_api_key

__all__ = ["require_hr_api_key"]
