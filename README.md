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

The project includes automated Azure deployment with comprehensive documentation:

### 🤖 Automated Setup (Recommended)

**One command to deploy everything:**

```bash
cd infrastructure && ./setup-azure.sh
```

Creates Azure resources, configures secrets, and triggers deployment automatically.  
**Time**: 5-10 minutes | **Details**: [Deployment Automation](./docs/DEPLOYMENT_AUTOMATION.md)

### 📚 Deployment Documentation

| Document | Purpose | When to Use |
|----------|---------|-------------|
| [Deployment Automation](./docs/DEPLOYMENT_AUTOMATION.md) | **Automated setup** - One-command deployment | Fastest method ⭐ |
| [Deployment Status](./docs/DEPLOYMENT_STATUS.md) | Current status & next steps | Check readiness |
| [Deployment Checklist](./docs/DEPLOYMENT_CHECKLIST.md) | Pre-deployment verification | Before deploying |
| [Deployment Runbook](./docs/DEPLOYMENT_RUNBOOK.md) | Step-by-step deployment guide | Manual deployment |
| [Azure Setup Guide](./docs/AZURE_SETUP_GUIDE.md) | Azure resource creation | Manual setup |
| [Azure Deployment](./docs/AZURE_DEPLOYMENT.md) | Architecture & design | Understanding system |

### Quick Start

**Option A: Automated (⭐ Recommended)**
```bash
brew install azure-cli gh    # Install CLIs
az login && gh auth login    # Login
cd infrastructure && ./setup-azure.sh  # Deploy!
```

**Option B: Manual**
1. **Get Azure subscription** - [Free account](https://azure.microsoft.com/free/) with $200 credit
2. **Create resources** - Follow [Azure Setup Guide](./docs/AZURE_SETUP_GUIDE.md)
3. **Configure secrets** - Add 4 secrets to GitHub repository
4. **Push to main** - Automatic deployment triggers
5. **Verify** - Use [Deployment Runbook](./docs/DEPLOYMENT_RUNBOOK.md)

### GitHub Secrets Required

| Secret | Description |
|--------|-------------|
| `AZURE_BACKEND_APP_NAME` | Your App Service name |
| `AZURE_BACKEND_PUBLISH_PROFILE` | XML from App Service deployment center |
| `AZURE_STATIC_WEB_APPS_API_TOKEN` | Token from Static Web App |
| `REACT_APP_API_URL` | Backend URL (https://...) |

**📋 See [Deployment Status](./docs/DEPLOYMENT_STATUS.md) for current deployment readiness.**

## Environment Variables

### Backend (.env)
```
DATABASE_URL=sqlite:///./hr_portal.db
CORS_ORIGINS=http://localhost:3000
HR_API_KEY=generate-a-strong-secret-value
```

### Frontend (.env)
```
REACT_APP_API_URL=http://localhost:8000
```

### HR Dashboard Access

- Share the `HR_API_KEY` with authorised HR staff only.
- The React HR dashboard prompts for the key at runtime and never stores it in source control.
- Losing or rotating the key requires updating the backend environment variable and notifying HR users.

## Documentation

See the [docs](./docs) folder for detailed documentation.
