# Backend

FastAPI backend for UAE HR Portal.

## Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Run

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Endpoints

- `GET /health` - Health check endpoint

## Project Structure

```
backend/
├── main.py              # FastAPI application entry point
├── requirements.txt     # Python dependencies
├── app/                 # Application package
│   ├── routers/        # API route handlers (empty placeholders)
│   ├── services/       # Business logic layer (empty placeholders)
│   ├── models/         # SQLAlchemy models (structure only, no DB connection)
│   │   └── request.py  # Request model placeholder
│   └── schemas/        # Pydantic schemas (structure only, no validation)
│       └── request.py  # Request schema placeholders
```

## Architecture Notes

### Current State
This backend currently has:
- Minimal FastAPI setup with `/health` endpoint
- Folder structure for future development
- Placeholder models and schemas (no business logic)

### Placeholders
The following are structure-only placeholders with no implementation:
- **Models** (`app/models/`): SQLAlchemy model classes (no database connection)
- **Schemas** (`app/schemas/`): Pydantic validation schemas (no validation rules)
- **Services** (`app/services/`): Business logic (empty)
- **Routers** (`app/routers/`): API endpoints (empty)

### What's NOT Included
- ❌ No database connection or migrations
- ❌ No authentication or authorization
- ❌ No business logic or workflows
- ❌ No request processing
- ❌ No validation rules

These will be added in future phases.
