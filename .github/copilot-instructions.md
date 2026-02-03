# hr-command-center – GitHub Copilot Instructions

## Project Overview
This is the **UAE HR Portal** — an internal request management system for UAE-based HR operations. The system enables employees to submit HR requests, track their status with unique reference numbers (REF-YYYY-NNN), and allows HR staff to manage and process those requests through a dashboard.

**Key Features:**
- Unified request submission system with auto-generated REF-YYYY-NNN references
- Public request tracking (no login required)
- HR dashboard for managing request statuses
- Status lifecycle: Submitted → Reviewing → Approved → Completed / Rejected
- Rate limiting, security headers, input sanitization
- API key authentication for HR endpoints

**Target users:** HR admins, department managers, employees (self-service portal)  
**Deployment:** Azure (App Service for backend, Static Web Apps for frontend)  
**Repository structure:** Monorepo with separate `/frontend` and `/backend` directories

## Core Technologies & Stack

### Frontend (`/frontend`)
- **Framework:** React 18 with JavaScript (not TypeScript)
- **Build tool:** Create React App (react-scripts 5.0.1)
- **Routing:** React Router v6 (`react-router-dom ^6.20.0`)
- **Styling:** CSS files (App.css, page-specific CSS)
- **State management:** React hooks (useState, useEffect)
- **API calls:** Native fetch API
- **Configuration:** Environment variables via `REACT_APP_*` prefix

### Backend (`/backend`)
- **Framework:** FastAPI 0.109.1
- **Server:** Uvicorn 0.24.0 (development), Gunicorn 21.2.0 (production)
- **Database:** SQLAlchemy 2.0.25 ORM with Alembic 1.13.1 migrations
  - SQLite for development (`sqlite:///./hr_portal.db`)
  - PostgreSQL for production (via psycopg2-binary)
- **Configuration:** Pydantic Settings (`pydantic-settings 2.1.0`) + python-dotenv
- **Security:** 
  - slowapi 0.1.9 (rate limiting)
  - bleach 6.1.0 (input sanitization)
  - Custom security headers middleware
- **Testing:** pytest 7.4.3 + httpx 0.25.2

### Infrastructure
- **Cloud:** Azure (App Service, Static Web Apps)
- **CI/CD:** GitHub Actions workflows
- **IaC:** Bicep templates (`/infrastructure/main.bicep`)
- **Authentication:** Azure OIDC for deployments, API key for HR endpoints

## Project Structure

```
hr-command-center/
├── backend/                    # FastAPI backend application
│   ├── app/
│   │   ├── core/              # Security middleware, rate limiting, validation
│   │   ├── dependencies/      # FastAPI dependency injection (security)
│   │   ├── models/            # SQLAlchemy ORM models (request, notification)
│   │   ├── routers/           # API route handlers (requests, hr)
│   │   ├── schemas/           # Pydantic schemas for request/response
│   │   ├── services/          # Business logic services
│   │   ├── config.py          # Application settings
│   │   └── database.py        # Database connection setup
│   ├── tests/                 # pytest test suite
│   ├── alembic/               # Database migrations
│   ├── main.py                # FastAPI application entry point
│   ├── requirements.txt       # Python dependencies
│   └── startup.sh             # Azure App Service startup script
│
├── frontend/                   # React frontend application
│   ├── src/
│   │   ├── pages/             # Page components (Home, TrackRequest, HRQueue)
│   │   ├── components/        # Reusable UI components
│   │   ├── App.js             # Main app component with routing
│   │   ├── config.js          # API configuration
│   │   └── index.js           # React entry point
│   ├── public/                # Static assets
│   └── package.json           # npm dependencies
│
├── docs/                       # Documentation
├── infrastructure/             # Azure deployment scripts and Bicep templates
└── .github/workflows/          # CI/CD workflows
```

## Build, Run & Test Commands

### Backend
```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest

# Run tests with verbose output
pytest -v

# Run specific test file
pytest tests/test_api.py

# Run tests by marker
pytest -m security
pytest -m api
pytest -m validation
```

### Frontend
```bash
cd frontend

# Install dependencies
npm install

# Start development server (localhost:3000)
npm start

# Create production build
npm run build

# Run tests
npm test
```

### Full Stack Development
```bash
# Terminal 1: Backend
cd backend && uvicorn main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend && npm start
```

## API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/health` | Health check | None |
| POST | `/requests` | Submit new request | Rate limited (10/hour) |
| GET | `/requests/{ref}` | Track request (public) | Rate limited (30/min) |
| PATCH | `/requests/{ref}/status` | Update status | HR API Key |
| GET | `/hr/requests` | HR request queue | HR API Key |
| GET | `/hr/stats` | Request statistics | HR API Key |

**API Documentation:** http://localhost:8000/docs (Swagger UI, debug mode only)

## Coding Standards & Style Rules

### Backend (Python)
- Use type hints for function parameters and return values
- Follow PEP 8 style guidelines
- Use Pydantic models for request/response validation
- Use dependency injection via FastAPI's `Depends()`
- Organize code by feature: routers → services → models
- Use logging module for application logs (not print statements)
- Handle errors with proper HTTP status codes and descriptive messages
- Use `bleach` for sanitizing user input
- Apply rate limiting via decorators

### Frontend (JavaScript/React)
- Use functional components with hooks (no class components)
- Keep components focused and small
- Use semantic HTML elements and proper accessibility attributes
- Follow existing CSS file conventions (component-specific CSS files)
- Use the `config.js` file for API URL configuration
- Handle loading and error states in components

### General
- Use meaningful variable and function names
- Add docstrings/comments for complex logic
- Keep functions small and focused
- No hardcoded secrets or credentials
- Use environment variables for configuration

## Git & PR Workflow
- **Branch naming:** `feature/description`, `bugfix/description`, `refactor/description`
- **Commit messages:** Use Conventional Commits format:
  - `feat:` new features
  - `fix:` bug fixes
  - `refactor:` code restructuring
  - `docs:` documentation changes
  - `test:` test additions/changes
  - `chore:` maintenance tasks
- Keep PRs focused and reasonably sized
- Include clear descriptions and link to related issues

## Testing Expectations

### Backend (pytest)
- Tests live in `/backend/tests/`
- Use fixtures from `conftest.py` for database sessions and test client
- Test markers available: `@pytest.mark.security`, `@pytest.mark.api`, `@pytest.mark.validation`
- Use in-memory SQLite for test isolation
- Mock external dependencies when needed
- Test both success and error cases

### Frontend
- Use React Testing Library patterns
- Test user interactions and component behavior
- Mock API calls for unit tests

## Security & Compliance

### Current Security Features
- ✅ Security headers middleware (XSS, clickjacking protection, CSP)
- ✅ Rate limiting (10 req/hour for submissions, 30 req/min for tracking)
- ✅ Input sanitization with bleach (HTML stripping, length validation)
- ✅ API key authentication for HR endpoints (`X-HR-API-Key` header)
- ✅ CORS configured for specific origins (no wildcards with credentials)
- ✅ Request size limits (1MB max)
- ✅ Startup validation of critical settings

### Security Guidelines
- Never commit secrets (use `.env` files and environment variables)
- Validate and sanitize all user input
- Use parameterized queries (SQLAlchemy handles this)
- Implement proper error handling without exposing internal details
- Apply role-based access: HR endpoints require API key authentication
- Log security-relevant events without exposing PII

### Environment Variables

**Backend (`backend/.env`):**
```
DATABASE_URL=sqlite:///./hr_portal.db
CORS_ORIGINS=http://localhost:3000
# IMPORTANT: Generate a secure random key for production!
# Use: python -c "import secrets; print(secrets.token_urlsafe(32))"
HR_API_KEY=<generate-a-secure-random-key>
DEBUG=true
```

**Frontend (`frontend/.env`):**
```
REACT_APP_API_URL=http://localhost:8000
```

## Deployment

### Azure Deployment (Production)
The project uses GitHub Actions workflows for Azure deployment:

- `backend-bootstrap.yml` - First-time backend deployment
- `backend-deploy.yml` - Automatic backend deployments on push to main
- `backend-repair.yml` - Autonomous self-healing (runs every 6 hours)
- `frontend-deploy.yml` - Frontend deployment to Azure Static Web Apps

**Production URLs:**
- Backend: `https://hrportal-backend.azurewebsites.net`
- API Docs: Available only when `DEBUG=true` (disabled in production for security)

### Required GitHub Secrets
| Secret | Description |
|--------|-------------|
| `AZURE_CLIENT_ID` | Service principal client ID for OIDC |
| `AZURE_TENANT_ID` | Azure tenant ID |
| `AZURE_SUBSCRIPTION_ID` | Azure subscription ID |

## How to Validate Changes

After implementing changes:

1. **Backend changes:**
   - Run `pytest` to ensure all tests pass
   - Start dev server and test endpoints manually
   - Check `/docs` for API documentation updates
   - Verify no sensitive data in logs

2. **Frontend changes:**
   - Run `npm start` and test UI manually
   - Check browser console for errors
   - Test on different screen sizes
   - Verify accessibility (keyboard navigation, screen reader)

3. **Both:**
   - Test full request flow (submit → track → HR update)
   - Check network tab for correct API calls
   - Verify error handling works correctly

## Preferred Patterns

**Do:**
- Use FastAPI dependency injection for shared logic
- Use Pydantic models for data validation
- Use service layer for business logic
- Keep route handlers thin
- Use meaningful HTTP status codes
- Write tests for new functionality

**Avoid:**
- Direct database access in route handlers
- Hardcoded configuration values
- Overly complex components (>200 lines)
- Ignoring error handling
- Skipping input validation

## Additional Resources

- [README.md](../README.md) — Project overview and quick start
- [docs/SECURITY.md](../docs/SECURITY.md) — Security configuration guide
- [docs/AZURE_BACKEND_WORKFLOWS.md](../docs/AZURE_BACKEND_WORKFLOWS.md) — Deployment guide
- [docs/BACKEND_ARCHITECTURE.md](../docs/BACKEND_ARCHITECTURE.md) — Technical architecture

---

Follow these instructions precisely when working on any issue in this repository.
