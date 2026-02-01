from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.database import engine, Base
from app.config import settings
from app.routers import requests, hr
from app.core.security_middleware import SecurityHeadersMiddleware

# Import models to ensure they're registered with Base
from app.models import request, notification

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize rate limiter (disable in testing mode)
import os
import sys
# Check if running under pytest instead of using environment variable
testing_mode = "pytest" in sys.modules
limiter = Limiter(
    key_func=get_remote_address,
    enabled=not testing_mode
)

app = FastAPI(
    title="UAE HR Portal API",
    docs_url="/docs" if settings.debug else None,  # Disable docs in production
    redoc_url="/redoc" if settings.debug else None,
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Security headers middleware (applied to all responses)
app.add_middleware(SecurityHeadersMiddleware)

# CORS middleware for frontend communication
# NOTE: CORS is configured with specific origins (no wildcards with credentials)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,  # Specific origins only
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],  # Explicit methods
    allow_headers=["Content-Type", "Authorization", "X-HR-API-Key"],  # Explicit headers
    max_age=600,  # Cache preflight requests for 10 minutes
)

# Trusted host middleware to prevent host header attacks
# Allow localhost for development and configured trusted hosts
# Add testserver for test environments
trusted_hosts = ["localhost", "127.0.0.1", "testserver"]

# Optionally trust a specific Azure App Service hostname via environment variable
azure_website_hostname = os.getenv("AZURE_WEBSITE_HOSTNAME")
if azure_website_hostname:
    trusted_hosts.append(azure_website_hostname)

if settings.trusted_hosts:
    trusted_hosts.extend(settings.trusted_hosts_list)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=trusted_hosts)

# Include routers
app.include_router(requests.router)
app.include_router(hr.router)


@app.on_event("startup")
async def validate_configuration():
    """
    Validate critical configuration on startup.
    
    Ensures that required security settings are configured before
    the application starts accepting requests.
    """
    import logging
    logger = logging.getLogger("uvicorn")
    
    # Warn if HR API key is not set (critical for production)
    if not settings.hr_api_key:
        logger.warning(
            "⚠️  HR_API_KEY is not configured! HR endpoints will be inaccessible. "
            "Set HR_API_KEY environment variable for production use."
        )
    
    # Warn if using SQLite in non-debug mode
    if not settings.debug and "sqlite" in settings.database_url.lower():
        logger.warning(
            "⚠️  SQLite database detected in production mode! "
            "Consider migrating to PostgreSQL for better concurrency and persistence. "
            "See documentation for migration guide."
        )
    
    # Warn if CORS origins include wildcards with credentials
    if settings.cors_origins == "*" or (isinstance(settings.cors_origins, str) and "*" in settings.cors_origins.split(",")):
        logger.error(
            "❌ CORS wildcard (*) is not allowed with credentials! "
            "Configure specific origins in CORS_ORIGINS environment variable."
        )
    
    # Log security configuration status
    logger.info("✅ Security headers middleware: ENABLED")
    logger.info(f"✅ CORS origins: {settings.cors_origins_list}")
    logger.info(f"✅ Debug mode: {settings.debug}")


@app.get("/health")
def health_check():
    """Health check endpoint for Azure App Service."""
    return {"status": "healthy", "service": "UAE HR Portal API"}
