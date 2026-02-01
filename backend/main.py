from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.config import settings
from app.routers import requests, hr

# Import models to ensure they're registered with Base
from app.models import request, notification

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="UAE HR Portal API")

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(requests.router)
app.include_router(hr.router)


@app.get("/health")
def health_check():
    """Health check endpoint for Azure App Service."""
    return {"status": "healthy", "service": "UAE HR Portal API"}
