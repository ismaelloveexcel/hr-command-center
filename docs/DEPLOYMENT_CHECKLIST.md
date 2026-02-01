# Deployment Readiness Checklist

This checklist ensures the UAE HR Portal is ready for production deployment to Azure.

## Pre-Deployment Review

### ✅ Code Review - PR #9 (Security Hardening)

**Status**: Ready for merge

**Implemented Features**:
- ✅ Security middleware (XSS, clickjacking, CSP protection)
- ✅ Rate limiting (10/hr submissions, 30/min tracking, 100/min HR)
- ✅ Input sanitization (HTML stripping via bleach)
- ✅ CORS and host protection
- ✅ Environment validation at startup
- ✅ 26 comprehensive tests
- ✅ CodeQL security scan passed (0 vulnerabilities)
- ✅ Documentation (SECURITY.md)

**Action**: Merge PR #9 before deployment

### 📋 GitHub Secrets Configuration

The following secrets must be configured in GitHub repository settings:

#### Required Secrets

| Secret Name | Status | Description |
|-------------|--------|-------------|
| `AZURE_BACKEND_APP_NAME` | ⚠️ TO VERIFY | Azure App Service name |
| `AZURE_BACKEND_PUBLISH_PROFILE` | ⚠️ TO VERIFY | App Service publish profile (XML) |
| `AZURE_STATIC_WEB_APPS_API_TOKEN` | ⚠️ TO VERIFY | Static Web App deployment token |
| `AZURE_STATIC_WEB_APPS_API_TOKEN_PROUD_COAST_0AB079210` | ⚠️ TO VERIFY | Alternate Static Web App token |
| `REACT_APP_API_URL` | ⚠️ TO VERIFY | Backend API URL |

#### How to Verify Secrets

1. Go to GitHub repository
2. Settings → Secrets and variables → Actions
3. Confirm all required secrets are present

#### How to Get Secret Values

See [AZURE_SETUP_GUIDE.md](./AZURE_SETUP_GUIDE.md) for detailed instructions on obtaining each secret.

### 🔧 Azure Resources

#### Required Azure Resources

- [ ] **Resource Group**: `hr-portal-rg`
- [ ] **App Service**: Backend API (Python 3.11 on Linux)
  - [ ] Startup command: `bash startup.sh`
  - [ ] Environment variables configured:
    - [ ] `DATABASE_URL`
    - [ ] `CORS_ORIGINS`
    - [ ] `HR_API_KEY` (secure random string)
- [ ] **Static Web App**: Frontend (React)
  - [ ] Connected to GitHub repository
  - [ ] Build configuration: app_location="/frontend", output_location="build"

#### How to Create Azure Resources

Choose one method:

1. **Azure Portal** (Recommended): Follow [AZURE_SETUP_GUIDE.md](./AZURE_SETUP_GUIDE.md)
2. **Azure CLI**: Use scripts in `infrastructure/` directory
3. **Bicep Template**: Run `infrastructure/deploy.sh`

### 🔄 Deployment Workflows

#### Backend Workflow (`backend-deploy.yml`)

**Triggers**:
- Push to `main` branch with changes to `backend/` directory
- Manual dispatch

**Steps**:
1. Test: Verify application imports and routes
2. Build: Create deployment package
3. Deploy: Push to Azure App Service
4. Verify: Health check endpoint

**Dependencies**:
- `AZURE_BACKEND_APP_NAME`
- `AZURE_BACKEND_PUBLISH_PROFILE`

#### Frontend Workflow (`frontend-deploy.yml`)

**Triggers**:
- Push to `main` branch with changes to `frontend/` directory
- Pull request events
- Manual dispatch

**Steps**:
1. Install dependencies
2. Build React application with `REACT_APP_API_URL`
3. Deploy to Azure Static Web Apps

**Dependencies**:
- `REACT_APP_API_URL`
- `AZURE_STATIC_WEB_APPS_API_TOKEN`

#### Static Web Apps Workflow (Auto-generated)

**Note**: There are TWO Static Web Apps workflows:
1. `frontend-deploy.yml` (custom)
2. `azure-static-web-apps-proud-coast-0ab079210.yml` (auto-generated)

**Action Required**: 
- Determine which workflow to use
- Remove or disable the other to avoid conflicts
- Ensure correct secret name is used

### 📝 Environment Variables

#### Backend Environment Variables

Must be configured in Azure App Service → Configuration → Application Settings:

```bash
DATABASE_URL=sqlite:///./hr_portal.db  # For production, use PostgreSQL
CORS_ORIGINS=https://YOUR-FRONTEND-URL.azurestaticapps.net
HR_API_KEY=<GENERATE-STRONG-RANDOM-STRING>
DEBUG=false  # Ensure false for production
```

**Security Note**: Generate `HR_API_KEY` using:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### Frontend Environment Variables

Configured via GitHub secrets, injected at build time:

```bash
REACT_APP_API_URL=https://YOUR-BACKEND.azurewebsites.net
```

### 🔐 Security Considerations

- [ ] HR_API_KEY is strong and securely stored
- [ ] CORS_ORIGINS is explicitly set (no wildcards)
- [ ] Database URL is secure (SQLite for testing, PostgreSQL for production)
- [ ] All secrets are in GitHub Secrets, not in code
- [ ] TLS/HTTPS is enabled (automatic with Azure)
- [ ] Rate limiting is configured and tested

### 🧪 Pre-Deployment Testing

- [ ] Run backend tests: `cd backend && pytest`
- [ ] Build backend successfully: `cd backend && pip install -r requirements.txt`
- [ ] Build frontend successfully: `cd frontend && npm install && npm run build`
- [ ] Verify all environment variables are set correctly
- [ ] Test database migrations (if using Alembic)

### 📊 Post-Deployment Verification

After deployment completes:

#### Backend Verification

```bash
# Health check
curl https://YOUR-BACKEND.azurewebsites.net/health

# Expected response:
# {"status":"healthy","service":"UAE HR Portal API"}

# API documentation
open https://YOUR-BACKEND.azurewebsites.net/docs
```

#### Frontend Verification

```bash
# Open frontend
open https://YOUR-FRONTEND.azurestaticapps.net

# Test features:
# 1. Home page loads
# 2. Submit a test request
# 3. Track request by reference number
# 4. HR Dashboard accessible (requires HR_API_KEY)
```

#### Integration Testing

- [ ] Submit a request from frontend
- [ ] Verify request appears in backend
- [ ] Track request by reference number
- [ ] Update request status from HR Dashboard
- [ ] Verify status update reflects on tracking page
- [ ] Test CORS (frontend can call backend)
- [ ] Verify rate limiting is active
- [ ] Test error handling

### 🛠️ Troubleshooting Guide

#### Issue: Backend deployment fails

**Solutions**:
1. Check GitHub Actions logs for errors
2. Verify `AZURE_BACKEND_PUBLISH_PROFILE` is not expired
3. Re-download publish profile from Azure Portal
4. Ensure Python 3.11 is selected in App Service

#### Issue: Frontend deployment fails

**Solutions**:
1. Verify `AZURE_STATIC_WEB_APPS_API_TOKEN` is correct
2. Check that repository/branch settings match
3. Review build logs in GitHub Actions
4. Ensure `REACT_APP_API_URL` is set

#### Issue: CORS errors in browser

**Solutions**:
1. Update `CORS_ORIGINS` in App Service → Configuration
2. Include full URL with `https://`
3. Restart App Service after changing settings
4. Clear browser cache

#### Issue: 502 Bad Gateway

**Solutions**:
1. Check App Service logs: Monitoring → Log stream
2. Verify startup command: `bash startup.sh`
3. Check Python runtime is 3.11
4. Review application logs for errors

### 📈 Monitoring & Maintenance

#### Set Up Monitoring

- [ ] Enable Application Insights (Azure)
- [ ] Configure log retention
- [ ] Set up alerts for errors/downtime
- [ ] Monitor rate limiting effectiveness

#### Regular Maintenance

- [ ] Weekly: Review application logs
- [ ] Monthly: Update dependencies (security patches)
- [ ] Quarterly: Review and rotate HR_API_KEY
- [ ] As needed: Scale resources based on usage

### 💰 Cost Management

**Estimated Monthly Costs**:
- App Service (B1 Basic): ~$13 USD
- Static Web App (Free tier): $0
- PostgreSQL (B1ms, optional): ~$15 USD
- **Total**: $13-28 USD/month

**Tips**:
- Use free $200 Azure credit for new accounts
- Scale down to Free tier for development/testing
- Set up budget alerts in Azure

## Quick Deployment Steps

### 1. Merge Security PR

```bash
# Review and merge PR #9
gh pr review 9 --approve
gh pr merge 9
```

### 2. Verify Secrets

Go to GitHub → Settings → Secrets and variables → Actions

Confirm all 4-5 secrets are configured.

### 3. Deploy

Option A: Push to main (automatic)
```bash
git checkout main
git pull
git push origin main
```

Option B: Manual trigger
1. Go to GitHub → Actions
2. Select workflow (backend-deploy or frontend-deploy)
3. Click "Run workflow"

### 4. Verify

```bash
# Backend
curl https://YOUR-BACKEND.azurewebsites.net/health

# Frontend
open https://YOUR-FRONTEND.azurestaticapps.net
```

## Deployment Workflow Consolidation Needed

**⚠️ Action Required**: Two Static Web Apps workflows exist:

1. `frontend-deploy.yml` - Custom workflow using `AZURE_STATIC_WEB_APPS_API_TOKEN`
2. `azure-static-web-apps-proud-coast-0ab079210.yml` - Auto-generated using `AZURE_STATIC_WEB_APPS_API_TOKEN_PROUD_COAST_0AB079210`

**Recommendation**: 
- Keep `frontend-deploy.yml` (more control, consistent naming)
- Archive or remove auto-generated workflow
- Consolidate to single token name: `AZURE_STATIC_WEB_APPS_API_TOKEN`

## Next Steps

1. ✅ Review this checklist
2. ⚠️ Verify GitHub secrets are configured
3. ⚠️ Confirm Azure resources are created
4. ⚠️ Merge PR #9 (security hardening)
5. ⚠️ Consolidate Static Web Apps workflows
6. ⚠️ Deploy and verify
7. ✅ Monitor and maintain

## Support Resources

- [Azure Setup Guide](./AZURE_SETUP_GUIDE.md) - Step-by-step Azure configuration
- [Azure Deployment Guide](./AZURE_DEPLOYMENT.md) - Deployment architecture and details
- [Security Guide](./SECURITY.md) - Security considerations for production (from PR #9)
- [Backend Architecture](./BACKEND_ARCHITECTURE.md) - Backend design and structure

---

**Last Updated**: 2026-02-01
**Status**: Pre-deployment checklist prepared
