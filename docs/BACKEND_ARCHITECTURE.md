# Backend Architecture

## Overview

The backend has been extended with a standard FastAPI application structure that supports future feature development while maintaining separation of concerns.

## Current State

### What EXISTS (Structure Only)

1. **Folder Structure**
   - `app/routers/` - API endpoint handlers (empty)
   - `app/services/` - Business logic layer (empty)
   - `app/models/` - Database models (placeholders)
   - `app/schemas/` - Pydantic validation schemas (placeholders)

2. **Placeholder Files**
   - `app/models/request.py` - Empty Request model class
   - `app/schemas/request.py` - Empty Request schemas (Base, Create, Update, Response)

3. **Working Features**
   - `/health` endpoint - Returns `{"status": "healthy"}`
   - Auto-generated OpenAPI documentation at `/docs`

### What DOES NOT Exist

- ❌ No database connection or session management
- ❌ No SQLAlchemy Base or declarative models
- ❌ No database migrations (Alembic)
- ❌ No Pydantic validation rules or Field constraints
- ❌ No service layer implementations
- ❌ No API routers beyond /health
- ❌ No authentication or authorization
- ❌ No business logic or workflows

## Architecture Pattern

The structure follows a layered architecture:

```
Client Request
      ↓
[Routers] ← API endpoints, request/response handling
      ↓
[Services] ← Business logic, orchestration
      ↓
[Models] ← Database interaction via SQLAlchemy
      ↓
Database
```

**Schemas** are used at the router level for validation and serialization.

## Dependencies

- **FastAPI 0.109.1** - Web framework (security patched)
- **Uvicorn 0.24.0** - ASGI server
- **SQLAlchemy 2.0.23** - ORM for future database models
- **Pydantic 2.5.3** - Data validation (explicit version)

## Placeholders Explained

### Models (`app/models/request.py`)

```python
class Request:
    """Placeholder for Request database model."""
    pass
```

This is a plain Python class, NOT a SQLAlchemy model yet. Future implementation will:
- Inherit from SQLAlchemy Base
- Define table columns
- Set up relationships
- Configure indexes

### Schemas (`app/schemas/request.py`)

```python
class RequestBase:
    """Base Request schema placeholder."""
    pass

class RequestCreate(RequestBase):
    """Schema for creating a new request."""
    pass
```

These are plain Python classes, NOT Pydantic models yet. Future implementation will:
- Inherit from `pydantic.BaseModel`
- Define fields with types
- Add validation rules with `Field()`
- Configure serialization options

## Future Development Path

### Phase 1: Database Layer (Next)
- Set up SQLAlchemy Base
- Configure database connection
- Implement actual Request model
- Add Alembic migrations

### Phase 2: Validation Layer
- Convert schemas to Pydantic BaseModel
- Add field definitions and types
- Implement validation rules
- Add custom validators

### Phase 3: Service Layer
- Implement CRUD operations
- Add business logic
- Handle transactions
- Error handling

### Phase 4: API Layer
- Create router modules
- Implement endpoints
- Add request/response handling
- OpenAPI documentation

### Phase 5: Features
- Authentication/authorization
- HR workflows
- Request processing
- Reporting

## Development Guidelines

When implementing features:

1. **Models First** - Define database schema
2. **Schemas Next** - Define API contracts
3. **Services Third** - Implement business logic
4. **Routers Last** - Expose via API

Always maintain:
- Clear separation of concerns
- Type hints everywhere
- Comprehensive docstrings
- No business logic in routers
- No database access in routers (use services)

## Testing Strategy

Future test structure:
```
tests/
├── unit/
│   ├── test_models.py
│   ├── test_schemas.py
│   └── test_services.py
└── integration/
    └── test_api.py
```

Currently: No tests (structure-only phase)
