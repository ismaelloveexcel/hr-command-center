#!/bin/bash

# Azure App Service startup script for FastAPI

# Run database migrations
python -m alembic upgrade head

# Start the application with Gunicorn + Uvicorn workers
gunicorn main:app \
    --workers 2 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
