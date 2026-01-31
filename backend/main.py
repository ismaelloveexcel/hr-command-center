from fastapi import FastAPI
from app.database import engine, Base
from app.routers import requests

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="UAE HR Portal API")

# Include routers
app.include_router(requests.router)


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
