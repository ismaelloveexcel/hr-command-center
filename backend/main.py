from fastapi import FastAPI
from app.database import engine, Base
from app.routers import requests, hr, compliance

# Import models to ensure they're registered with Base
from app.models import request, compliance as compliance_model, notification

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="UAE HR Portal API")

# Include routers
app.include_router(requests.router)
app.include_router(hr.router)
app.include_router(compliance.router)


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
