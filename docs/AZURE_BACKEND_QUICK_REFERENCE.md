# Azure Backend Workflows - Quick Reference

## Setup (One-Time)

### 1. Configure OIDC Authentication

Create service principal and configure federated credentials:
```bash
# Create service principal
az ad sp create-for-rbac \
  --name "github-actions-hr-portal" \
  --role contributor \
  --scopes /subscriptions/{subscription-id}

# Note the output: appId, tenant, subscription
```

### 2. Add GitHub Secrets

Required secrets (in repository settings):
- `AZURE_CLIENT_ID` - The appId from step 1
- `AZURE_TENANT_ID` - The tenant from step 1
- `AZURE_SUBSCRIPTION_ID` - The subscription from step 1

Optional:
- `FRONTEND_URL` - Your frontend URL for CORS

### 3. Run Bootstrap

```bash
gh workflow run backend-bootstrap.yml
```

Wait 5-10 minutes, then verify:
```bash
curl https://hrportal-backend.azurewebsites.net/health
```

## Daily Use

### Deploy Code Changes

```bash
# Automatic on push to main
git push origin main

# Or manually
gh workflow run backend-deploy.yml
```

### Check Backend Health

```bash
# Via curl
curl https://hrportal-backend.azurewebsites.net/health

# Via workflow
gh workflow run backend-repair.yml
```

### Fix Issues

```bash
# Automatic repair
gh workflow run backend-repair.yml

# Force full repair
gh workflow run backend-repair.yml -f repair_mode=true
```

## Workflows at a Glance

| Workflow | Purpose | When to Use | Trigger |
|----------|---------|-------------|---------|
| backend-bootstrap.yml | First deployment | Once, initial setup | Manual only |
| backend-deploy.yml | Code deployment | Every code change | Auto on push, Manual |
| backend-repair.yml | Self-healing | Fix issues | Auto every 6h, Manual |

## Common Commands

### View Logs
```bash
az webapp log tail \
  --name hrportal-backend \
  --resource-group baynunah-hr-portal-rg
```

### Check Configuration
```bash
az webapp config show \
  --name hrportal-backend \
  --resource-group baynunah-hr-portal-rg
```

### View App Settings
```bash
az webapp config appsettings list \
  --name hrportal-backend \
  --resource-group baynunah-hr-portal-rg
```

### Restart Backend
```bash
az webapp restart \
  --name hrportal-backend \
  --resource-group baynunah-hr-portal-rg
```

## Troubleshooting Decision Tree

```
Backend not working?
├─ Is it deployed?
│  ├─ No → Run backend-bootstrap.yml
│  └─ Yes → Is health endpoint responding?
│     ├─ No → Run backend-repair.yml
│     └─ Yes → Check application logs
│
└─ Deploy failed?
   ├─ "Backend does not exist" → Run backend-bootstrap.yml
   ├─ "Health check failed" → Run backend-repair.yml
   └─ Other error → Check workflow logs
```

## Resource Names

| Resource | Name |
|----------|------|
| Resource Group | baynunah-hr-portal-rg |
| App Service Plan | hrportal-plan-be |
| Web App | hrportal-backend |
| Location | uaenorth |
| Runtime | Python 3.11 |

## URLs

- Backend: https://hrportal-backend.azurewebsites.net
- Health: https://hrportal-backend.azurewebsites.net/health
- API Docs: https://hrportal-backend.azurewebsites.net/docs
- Azure Portal: https://portal.azure.com

## Emergency Procedures

### Backend Completely Down
```bash
# 1. Check if exists
az webapp show --name hrportal-backend --resource-group baynunah-hr-portal-rg

# 2. If exists, repair
gh workflow run backend-repair.yml -f repair_mode=true

# 3. If doesn't exist, bootstrap
gh workflow run backend-bootstrap.yml
```

### Secrets Lost
```bash
# Run repair to regenerate
gh workflow run backend-repair.yml -f repair_mode=true
```

### Configuration Drift
```bash
# Run repair to fix
gh workflow run backend-repair.yml
```

## Monitoring Schedule

| Task | Frequency | How |
|------|-----------|-----|
| Health check | Every 6 hours | Automatic (repair workflow) |
| Deploy | On code change | Automatic (deploy workflow) |
| Log review | Weekly | Manual |
| Configuration audit | Monthly | Manual |
