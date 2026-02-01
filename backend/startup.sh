#!/bin/bash

# Azure App Service startup script for FastAPI
# This script runs when the container starts

set -e

echo "Starting UAE HR Portal Backend..."

# Set Python path
export PYTHONPATH="${PYTHONPATH}:/home/site/wwwroot"

# Navigate to app directory
cd /home/site/wwwroot

# Run database migrations (if using Alembic)
if [ -f "alembic.ini" ]; then
    echo "Running database migrations..."
    python -m alembic upgrade head || echo "Migration skipped or failed"
fi

# Start the application with Gunicorn + Uvicorn workers
echo "Starting Gunicorn with Uvicorn workers..."
exec gunicorn main:app \
    --workers 2 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --timeout 120 \
    --keep-alive 5 \
    --access-logfile - \
    --error-logfile - \
    --capture-output \
    --log-level info
