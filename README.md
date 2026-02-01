# UAE HR Portal

A unified request management system for UAE-based HR operations.

## Project Structure

```
hr-command-center/
├── backend/          # FastAPI backend
├── frontend/         # React frontend
├── docs/             # Documentation
└── .github/          # GitHub Actions workflows
```

## Features

- **Unified Request System**: Submit and track HR requests
- **REF-YYYY-NNN Reference Numbers**: Unique, trackable references
- **Status Lifecycle**: Submitted → Reviewing → Approved → Completed / Rejected
- **Public Request Tracking**: No login required to track requests
- **HR Dashboard**: Manage and update request statuses
	- Requires HR API key for access to administrative endpoints
- **Notification Stub**: Logs notifications (ready for future integration)
- **Security Features**:
	- Rate limiting to prevent abuse (10 requests/hour for submissions)
	- Security headers (XSS, clickjacking protection)
	- Input sanitization to prevent XSS attacks
	- CORS configuration for specific origins
	- API key authentication for HR endpoints

## Quick Start

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend API: http://localhost:8000
API Docs: http://localhost:8000/docs

### Frontend

```bash
cd frontend
npm install
npm start
```

Frontend: http://localhost:3000

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/requests` | Submit new request |
| GET | `/requests/{ref}` | Track request (public) |
| PATCH | `/requests/{ref}/status` | Update status (requires HR API key) |
| GET | `/hr/requests` | HR request queue (requires HR API key) |
| GET | `/hr/stats` | Request statistics (requires HR API key) |

## Deployment

The project includes automated Azure deployment:

### Quick Start
1. **Get Azure subscription** - [Free account](https://azure.microsoft.com/free/) with $200 credit
2. **Create resources** - See [Azure Setup Guide](./docs/AZURE_SETUP_GUIDE.md)
3. **Configure secrets** - Add 4 secrets to GitHub repository
4. **Push to main** - Automatic deployment triggers

### GitHub Secrets Required

| Secret | Description |
|--------|-------------|
| `AZURE_BACKEND_APP_NAME` | Your App Service name |
| `AZURE_BACKEND_PUBLISH_PROFILE` | XML from App Service deployment center |
| `AZURE_STATIC_WEB_APPS_API_TOKEN` | Token from Static Web App |
| `REACT_APP_API_URL` | Backend URL (https://...) |

See [Azure Setup Guide](./docs/AZURE_SETUP_GUIDE.md) for step-by-step instructions.

## Environment Variables

### Backend (.env)
```
DATABASE_URL=sqlite:///./hr_portal.db
CORS_ORIGINS=http://localhost:3000
HR_API_KEY=generate-a-strong-secret-value
DEBUG=true
```

**Production Configuration:**
- Use PostgreSQL: `DATABASE_URL=postgresql://user:pass@host/db?sslmode=require`
- Set specific CORS origins: `CORS_ORIGINS=https://myapp.azurewebsites.net`
- Generate strong HR_API_KEY: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- Set `DEBUG=false`

See [SECURITY.md](./docs/SECURITY.md) for complete security configuration guide.

### Frontend (.env)
```
REACT_APP_API_URL=http://localhost:8000
```

### HR Dashboard Access

- Share the `HR_API_KEY` with authorised HR staff only.
- The React HR dashboard prompts for the key at runtime and never stores it in source control.
- Losing or rotating the key requires updating the backend environment variable and notifying HR users.

## Documentation

See the [docs](./docs) folder for detailed documentation:
- [Security Configuration Guide](./docs/SECURITY.md) - Security features and production setup
- [Azure Setup Guide](./docs/AZURE_SETUP_GUIDE.md) - Deployment to Azure
- [Backend Architecture](./docs/BACKEND_ARCHITECTURE.md) - Technical architecture details

## Security Considerations

⚠️ **Before Production Deployment:**
1. Set `DEBUG=false`
2. Configure strong `HR_API_KEY` 
3. Use PostgreSQL instead of SQLite
4. Set specific CORS origins (no wildcards)
5. Review the [Security Guide](./docs/SECURITY.md)

**Current Security Features:**
- ✅ Security headers (XSS, clickjacking protection)
- ✅ Rate limiting (10 req/hour for submissions, 30 req/min for tracking)
- ✅ Input sanitization (HTML stripping, length validation)
- ✅ API key authentication for HR endpoints
- ✅ CORS configured for specific origins
- ✅ Startup validation of critical settings

**Recommended Future Enhancements:**
- Azure AD/OAuth 2.0 authentication
- Role-based access control (RBAC)
- Audit logging
- Monitoring with Azure Application Insights
