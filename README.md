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

The project includes autonomous Azure deployment with self-healing capabilities:

### ⚡ Autonomous Backend Deployment (New!)

**Three GitHub Actions workflows with zero manual intervention:**

1. **backend-bootstrap.yml** - First-time deployment (run once)
2. **backend-deploy.yml** - Automatic code deployments (on push to main)
3. **backend-repair.yml** - Autonomous self-healing (every 6 hours)

**Quick start:**
```bash
# 1. Configure OIDC secrets (see docs)
# 2. Run bootstrap workflow
gh workflow run backend-bootstrap.yml

# 3. Done! Future deployments are automatic
```

**Key Features:**
- ✅ 100% idempotent - safe to run multiple times
- ✅ Azure OIDC authentication (no credentials in GitHub)
- ✅ Autonomous repair - fixes issues automatically
- ✅ Fail-hard with diagnostics - no silent failures
- ✅ Secret generation & sync (never rotates unless missing)
- ✅ Health verification with retries

**Documentation:**
- [Azure Backend Workflows Guide](./docs/AZURE_BACKEND_WORKFLOWS.md) - Complete guide
- [Quick Reference](./docs/AZURE_BACKEND_QUICK_REFERENCE.md) - Common commands

### 🤖 Legacy Automated Setup

**One command to deploy everything (alternative method):**

```bash
cd infrastructure && ./setup-azure.sh
```

Creates Azure resources, configures secrets, and triggers deployment automatically.  
**Time**: 5-10 minutes | **Details**: [Deployment Automation](./docs/DEPLOYMENT_AUTOMATION.md)

### 📚 Deployment Documentation

| Document | Purpose | When to Use |
|----------|---------|-------------|
| [Azure Backend Workflows](./docs/AZURE_BACKEND_WORKFLOWS.md) | **Autonomous workflows** - New deployment system | Production deployments ⭐ |
| [Quick Reference](./docs/AZURE_BACKEND_QUICK_REFERENCE.md) | Common commands & troubleshooting | Daily operations ⭐ |
| [Deployment Automation](./docs/DEPLOYMENT_AUTOMATION.md) | **Automated setup** - One-command deployment | Legacy method |
| [Deployment Status](./docs/DEPLOYMENT_STATUS.md) | Current status & next steps | Check readiness |
| [Deployment Checklist](./docs/DEPLOYMENT_CHECKLIST.md) | Pre-deployment verification | Before deploying |
| [Deployment Runbook](./docs/DEPLOYMENT_RUNBOOK.md) | Step-by-step deployment guide | Manual deployment |
| [Azure Setup Guide](./docs/AZURE_SETUP_GUIDE.md) | Azure resource creation | Manual setup |
| [Azure Deployment](./docs/AZURE_DEPLOYMENT.md) | Architecture & design | Understanding system |

### Quick Start

**Option A: Autonomous Workflows (⭐ Recommended)**
```bash
# Prerequisites
brew install azure-cli gh    # Install CLIs
az login && gh auth login    # Login

# Configure OIDC (one-time setup)
# See: docs/AZURE_BACKEND_WORKFLOWS.md

# Deploy backend
gh workflow run backend-bootstrap.yml

# Deploy frontend (use existing workflow or manual setup)
```

**Option B: Legacy Automated**
```bash
brew install azure-cli gh    # Install CLIs
az login && gh auth login    # Login
cd infrastructure && ./setup-azure.sh  # Deploy!
```

**Option C: Manual**
1. **Get Azure subscription** - [Free account](https://azure.microsoft.com/free/) with $200 credit
2. **Create resources** - Follow [Azure Setup Guide](./docs/AZURE_SETUP_GUIDE.md)
3. **Configure secrets** - Add required secrets to GitHub repository
4. **Push to main** - Automatic deployment triggers
5. **Verify** - Use [Deployment Runbook](./docs/DEPLOYMENT_RUNBOOK.md)

### GitHub Secrets Required

**For Autonomous Workflows (Recommended):**

| Secret | Description |
|--------|-------------|
| `AZURE_CLIENT_ID` | Service principal client ID for OIDC authentication |
| `AZURE_TENANT_ID` | Azure tenant ID |
| `AZURE_SUBSCRIPTION_ID` | Azure subscription ID |
| `FRONTEND_URL` | Frontend URL for CORS (optional) |

**For Legacy Workflows:**

| Secret | Description |
|--------|-------------|
| `AZURE_BACKEND_APP_NAME` | Your App Service name |
| `AZURE_BACKEND_PUBLISH_PROFILE` | XML from App Service deployment center |
| `AZURE_STATIC_WEB_APPS_API_TOKEN` | Token from Static Web App |
| `REACT_APP_API_URL` | Backend URL (https://...) |

**Note:** Autonomous workflows auto-generate and sync `HR_API_KEY` and publish profiles.

**📋 See [Azure Backend Workflows Guide](./docs/AZURE_BACKEND_WORKFLOWS.md) for OIDC setup.**

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
