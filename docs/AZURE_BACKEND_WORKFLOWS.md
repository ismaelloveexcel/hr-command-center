# Azure Backend Deployment Guide

This guide explains how to use the three autonomous Azure App Service deployment workflows.

## Overview

The backend deployment system consists of three workflows:

1. **backend-bootstrap.yml** - First-time deployment only
2. **backend-deploy.yml** - Regular code deployments
3. **backend-repair.yml** - Autonomous self-healing

## Prerequisites

### Required GitHub Secrets

Configure these secrets in your GitHub repository settings:

1. **AZURE_CLIENT_ID** - Azure service principal client ID for OIDC authentication
2. **AZURE_TENANT_ID** - Azure tenant ID
3. **AZURE_SUBSCRIPTION_ID** - Azure subscription ID

### Optional GitHub Secrets

- **FRONTEND_URL** - Frontend URL for CORS configuration (defaults to `https://hrportal-frontend.azurewebsites.net`)

### Setting up OIDC Authentication

Follow Microsoft's guide to configure OIDC: https://learn.microsoft.com/azure/developer/github/connect-from-azure

Quick steps:
```bash
# Create a service principal
az ad sp create-for-rbac \
  --name "github-actions-hr-portal" \
  --role contributor \
  --scopes /subscriptions/{subscription-id}/resourceGroups/baynunah-hr-portal-rg

# Configure federated credentials for GitHub Actions
az ad app federated-credential create \
  --id {app-id} \
  --parameters @federated-credential.json
```

## Workflows

### 1. Backend Bootstrap (First Deployment)

**File**: `.github/workflows/backend-bootstrap.yml`

**Purpose**: First-time deployment only. Creates all infrastructure and performs initial deployment.

**When to use**: 
- First deployment to a new Azure subscription
- After manually deleting all backend resources
- Never run if backend already exists (will fail safely)

**What it does**:
1. ✅ Validates required files (startup.sh, requirements.txt, main.py)
2. ✅ Validates required GitHub secrets exist
3. ✅ Checks backend doesn't already exist (fails if it does)
4. ✅ Creates Resource Group (idempotent)
5. ✅ Creates App Service Plan (idempotent)
6. ✅ Creates Web App
7. ✅ Generates HR_API_KEY (if missing)
8. ✅ Stores secrets in both Azure and GitHub
9. ✅ Configures app settings (CORS, startup, etc.)
10. ✅ Deploys backend code
11. ✅ Verifies health (10 retries)
12. ✅ Locks configuration version

**How to run**:
```bash
# Via GitHub UI
Go to: Actions → Backend Bootstrap → Run workflow

# Via GitHub CLI
gh workflow run backend-bootstrap.yml
```

**Expected outcome**:
- Backend URL: https://hrportal-backend.azurewebsites.net
- Health endpoint: https://hrportal-backend.azurewebsites.net/health
- API docs: https://hrportal-backend.azurewebsites.net/docs

### 2. Backend Deploy (Regular Deployments)

**File**: `.github/workflows/backend-deploy.yml`

**Purpose**: Regular code-only deployments. Does NOT create infrastructure or rotate secrets.

**When to use**:
- After backend-bootstrap.yml has been run
- For all code changes to backend/
- Automatic on push to main

**Triggers**:
- Push to main branch (if backend/** or workflow file changes)
- Manual via workflow_dispatch
- Called by backend-repair.yml (if needed)

**What it does**:
1. ✅ Validates backend exists (fails if missing)
2. ✅ Validates secrets exist (fails if missing)
3. ✅ Builds Python application
4. ✅ Deploys code only
5. ✅ Verifies health (5 retries)

**What it does NOT do**:
- ❌ Create infrastructure
- ❌ Rotate secrets
- ❌ Modify configuration

**How to run**:
```bash
# Automatic on push
git push origin main

# Via GitHub UI
Go to: Actions → Backend Deploy → Run workflow

# Via GitHub CLI
gh workflow run backend-deploy.yml
```

**Troubleshooting**:
- If validation fails: Run backend-repair.yml
- If health check fails: Run backend-repair.yml
- If backend missing: Run backend-bootstrap.yml

### 3. Backend Repair (Autonomous Self-Healing)

**File**: `.github/workflows/backend-repair.yml`

**Purpose**: Autonomous detection and repair of infrastructure, configuration, and health issues.

**When to use**:
- Runs automatically every 6 hours
- Run manually if backend is broken
- Run manually with `repair_mode: true` to force full repair

**Triggers**:
- Schedule: Every 6 hours (0 */6 * * *)
- Manual with optional `repair_mode` parameter

**What it does**:

**Phase 1: Diagnosis**
- Detects backend state:
  - ✅ Healthy (no action needed)
  - ⚠️ Missing (needs recreation)
  - ⚠️ Misconfigured (needs config fix)
  - ⚠️ Unhealthy (needs deployment)

**Phase 2: Repair** (only if needed)
- If missing: Recreates infrastructure
- If misconfigured: Fixes configuration drift
- If unhealthy: Triggers deployment
- Syncs secrets (NO rotation unless missing)

**Phase 3: Verification**
- Health check (10 retries)
- Comprehensive diagnostics on failure
- Reports repair status

**How to run**:
```bash
# Via GitHub UI
Go to: Actions → Backend Repair → Run workflow
# Optionally check "Force repair mode"

# Via GitHub CLI (normal mode)
gh workflow run backend-repair.yml

# Via GitHub CLI (force repair)
gh workflow run backend-repair.yml -f repair_mode=true
```

**Repair Logic**:

| State | Actions Taken |
|-------|--------------|
| Healthy | No action (exits early) |
| Missing | Recreate infra → Sync secrets → Fix config → Deploy |
| Misconfigured | Fix config → Verify health |
| Unhealthy | Diagnose → Fix config → Deploy → Verify |

**Secret Sync Rules** (NO ROTATION):
- If secret exists in Azure only → Sync to GitHub
- If secret missing in both → Generate new and sync
- If secret exists in GitHub only → Generate new (can't read from GitHub)
- NEVER rotates existing secrets

## Architecture

### Resource Naming Convention

| Resource | Name | Location |
|----------|------|----------|
| Resource Group | baynunah-hr-portal-rg | uaenorth |
| App Service Plan | hrportal-plan-be | uaenorth |
| Web App | hrportal-backend | uaenorth |
| Runtime | Python 3.11 | Linux |
| SKU | B1 (Basic) | - |

### Configuration

**Environment Variables (Azure App Settings)**:
- `HR_API_KEY` - API key for HR endpoints (auto-generated)
- `DEBUG` - Set to "False" in production
- `CORS_ORIGINS` - Comma-separated allowed origins
- `DATABASE_URL` - Database connection string (SQLite by default)
- `CONFIG_VERSION` - Configuration version (1.0.0)
- `BOOTSTRAP_COMPLETED` - Bootstrap completion flag
- `SCM_DO_BUILD_DURING_DEPLOYMENT` - Enable Oryx build
- `ENABLE_ORYX_BUILD` - Enable Oryx build

**Startup Configuration**:
- Startup command: `startup.sh`
- Health endpoint: `/health`
- HTTPS only: Enabled

### Idempotency

All workflows are designed to be idempotent:

1. **backend-bootstrap.yml**:
   - Checks if backend exists before creating
   - Creates resources only if missing
   - Reuses existing secrets if available
   - Fails safely if backend already exists

2. **backend-deploy.yml**:
   - Only deploys code (no infrastructure changes)
   - Validates prerequisites before deployment
   - Fails if backend doesn't exist

3. **backend-repair.yml**:
   - Detects current state before acting
   - Only applies changes where drift detected
   - Never rotates secrets unless missing
   - Skips repair if already healthy

## Troubleshooting

### Bootstrap Issues

**Error: Backend already exists**
```
Solution: Use backend-deploy.yml for deployments
```

**Error: AZURE_CLIENT_ID secret is missing**
```
Solution: Configure OIDC authentication (see Prerequisites)
```

**Error: Health check failed after 10 attempts**
```
Solution: Check application logs:
az webapp log tail --name hrportal-backend --resource-group baynunah-hr-portal-rg
```

### Deploy Issues

**Error: Backend does not exist**
```
Solution: Run backend-bootstrap.yml first
```

**Error: HR_API_KEY not configured**
```
Solution: Run backend-repair.yml to sync secrets
```

### Repair Issues

**Error: Repair failed after multiple attempts**
```
Solution: Check diagnostics output in workflow logs
Manual intervention may be required
```

## Monitoring

### Health Check

The backend exposes a health endpoint:
```bash
curl https://hrportal-backend.azurewebsites.net/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "UAE HR Portal API"
}
```

### Application Logs

View real-time logs:
```bash
az webapp log tail \
  --name hrportal-backend \
  --resource-group baynunah-hr-portal-rg
```

Download logs:
```bash
az webapp log download \
  --name hrportal-backend \
  --resource-group baynunah-hr-portal-rg \
  --log-file logs.zip
```

## Security

### OIDC Authentication

All workflows use Azure OIDC authentication (OpenID Connect) instead of service principal credentials:
- ✅ No credentials stored in GitHub
- ✅ Short-lived tokens
- ✅ Automatic token refresh
- ✅ Scoped permissions

### Secret Management

- HR_API_KEY generated with `openssl rand -hex 32` (256-bit)
- Stored in both Azure App Settings and GitHub Secrets
- Never logged or exposed in workflow output
- Synced but never rotated (unless missing)

### CORS Configuration

- Explicit origins only (no wildcards)
- Credentials allowed
- Specific methods: GET, POST, PATCH, DELETE, OPTIONS
- Specific headers: Content-Type, Authorization, X-HR-API-Key

## Best Practices

1. **Initial Setup**:
   - Run backend-bootstrap.yml once
   - Verify health endpoint works
   - Test API endpoints

2. **Regular Development**:
   - Push to main triggers automatic deployment
   - Monitor deployment success
   - Verify health after deployment

3. **Maintenance**:
   - Let backend-repair.yml run automatically
   - Monitor repair workflow results
   - Run manually if issues detected

4. **Troubleshooting**:
   - Check workflow logs first
   - Use Azure CLI to inspect resources
   - Run backend-repair.yml to fix issues
   - Only run backend-bootstrap.yml for fresh deployments

## Advanced Usage

### Manual Secret Rotation

To rotate HR_API_KEY manually:
```bash
# Delete from both locations
az webapp config appsettings delete \
  --name hrportal-backend \
  --resource-group baynunah-hr-portal-rg \
  --setting-names HR_API_KEY

gh secret delete HR_API_KEY --repo ismaelloveexcel/hr-command-center

# Run repair to generate new key
gh workflow run backend-repair.yml
```

### Force Infrastructure Rebuild

To rebuild infrastructure:
```bash
# Option 1: Delete web app and run repair
az webapp delete \
  --name hrportal-backend \
  --resource-group baynunah-hr-portal-rg

gh workflow run backend-repair.yml -f repair_mode=true

# Option 2: Delete everything and bootstrap
az group delete --name baynunah-hr-portal-rg
gh workflow run backend-bootstrap.yml
```

### Custom Configuration

To modify configuration:
1. Update workflow environment variables
2. Run backend-repair.yml to apply changes
3. Or modify directly in Azure Portal

## Support

For issues:
1. Check workflow logs
2. Check application logs
3. Run backend-repair.yml
4. Create GitHub issue if problem persists
