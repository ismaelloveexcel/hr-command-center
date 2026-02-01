# Deployment Runbook - UAE HR Portal

Quick reference guide for deploying the UAE HR Portal to Azure.

## 🚀 Quick Deployment (Assuming Azure is Set Up)

If Azure resources and GitHub secrets are already configured:

```bash
# 1. Merge security PR
git checkout main
git pull
git merge origin/copilot/fix-security-gaps-hr-portal
git push origin main

# 2. Monitor deployment
# Go to: https://github.com/ismaelloveexcel/hr-command-center/actions

# 3. Verify deployment
curl https://YOUR-BACKEND.azurewebsites.net/health
open https://YOUR-FRONTEND.azurestaticapps.net
```

## 📋 Full Deployment Guide

### Phase 1: Pre-Deployment Preparation

#### 1.1 Review and Merge Security PR

```bash
# Check PR status
gh pr view 9

# Review changes
gh pr diff 9

# Merge when ready
gh pr merge 9 --squash --delete-branch

# Pull latest main
git checkout main
git pull
```

#### 1.2 Verify Repository State

```bash
# Ensure on main branch
git branch --show-current

# Check for uncommitted changes
git status

# View recent commits
git log --oneline -5
```

### Phase 2: Azure Resource Setup

#### 2.1 Login to Azure

```bash
az login
az account show
```

#### 2.2 Option A: Use Infrastructure Scripts

```bash
cd infrastructure

# Deploy with defaults
./deploy.sh

# Or specify custom values
./deploy.sh my-resource-group eastus

# Save the output - it contains your secret values!
```

#### 2.3 Option B: Azure Portal Setup

Follow the detailed guide in [AZURE_SETUP_GUIDE.md](./AZURE_SETUP_GUIDE.md).

**Required Resources**:
- Resource Group: `hr-portal-rg`
- App Service: `YOUR-APP-NAME` (Python 3.11, Linux)
- Static Web App: `YOUR-SWA-NAME`

#### 2.4 Configure App Service

```bash
# Set startup command
az webapp config set \
  --name YOUR-APP-NAME \
  --resource-group hr-portal-rg \
  --startup-file "bash startup.sh"

# Set environment variables
az webapp config appsettings set \
  --name YOUR-APP-NAME \
  --resource-group hr-portal-rg \
  --settings \
    DATABASE_URL="sqlite:///./hr_portal.db" \
    CORS_ORIGINS="https://YOUR-FRONTEND.azurestaticapps.net" \
    HR_API_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')" \
    DEBUG="false"
```

### Phase 3: GitHub Secrets Configuration

#### 3.1 Collect Required Values

```bash
# Backend app name
BACKEND_NAME="YOUR-APP-NAME"

# Backend URL
BACKEND_URL="https://$BACKEND_NAME.azurewebsites.net"

# Get publish profile
az webapp deployment list-publishing-profiles \
  --name $BACKEND_NAME \
  --resource-group hr-portal-rg \
  --xml > publish-profile.xml

# Get Static Web App token
SWA_TOKEN=$(az staticwebapp secrets list \
  --name YOUR-SWA-NAME \
  --resource-group hr-portal-rg \
  --query 'properties.apiKey' -o tsv)

echo "Backend URL: $BACKEND_URL"
echo "SWA Token: $SWA_TOKEN"
```

#### 3.2 Add Secrets to GitHub

Go to: `https://github.com/ismaelloveexcel/hr-command-center/settings/secrets/actions`

Click **New repository secret** for each:

| Secret Name | Value | Example |
|-------------|-------|---------|
| `AZURE_BACKEND_APP_NAME` | Your App Service name | `uae-hr-portal-api` |
| `AZURE_BACKEND_PUBLISH_PROFILE` | Content of publish-profile.xml | `<publishData>...</publishData>` |
| `AZURE_STATIC_WEB_APPS_API_TOKEN` | Token from Azure | `abc123...xyz789` |
| `REACT_APP_API_URL` | Backend URL | `https://uae-hr-portal-api.azurewebsites.net` |

**Security**: Delete `publish-profile.xml` after uploading to GitHub!

```bash
rm publish-profile.xml
```

### Phase 4: Deploy Application

#### 4.1 Trigger Backend Deployment

```bash
# Option A: Push change to trigger automatic deployment
git checkout main
touch backend/.deploy-trigger
git add backend/.deploy-trigger
git commit -m "Trigger backend deployment"
git push origin main

# Option B: Manual workflow dispatch
gh workflow run backend-deploy.yml
```

#### 4.2 Trigger Frontend Deployment

```bash
# Option A: Push change to trigger automatic deployment
touch frontend/.deploy-trigger
git add frontend/.deploy-trigger
git commit -m "Trigger frontend deployment"
git push origin main

# Option B: Manual workflow dispatch
gh workflow run frontend-deploy.yml
```

#### 4.3 Monitor Deployments

```bash
# Watch GitHub Actions
gh run watch

# Or view in browser
open https://github.com/ismaelloveexcel/hr-command-center/actions
```

### Phase 5: Verification

#### 5.1 Backend Verification

```bash
# Set your backend URL
BACKEND_URL="https://YOUR-APP-NAME.azurewebsites.net"

# Health check
echo "Testing health endpoint..."
curl -i $BACKEND_URL/health
# Expected: {"status":"healthy","service":"UAE HR Portal API"}

# API docs
echo "Opening API documentation..."
open $BACKEND_URL/docs

# Test request creation
echo "Testing request creation..."
curl -X POST $BACKEND_URL/requests \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Request",
    "type": "visa_application",
    "description": "Testing deployment",
    "requester_name": "Test User",
    "requester_email": "test@example.com"
  }'
# Should return request with reference number
```

#### 5.2 Frontend Verification

```bash
# Set your frontend URL
FRONTEND_URL="https://YOUR-SWA-NAME.azurestaticapps.net"

# Open frontend
open $FRONTEND_URL

# Manual tests:
# 1. ✅ Home page loads
# 2. ✅ Navigation works
# 3. ✅ Submit request form loads
# 4. ✅ Can submit a test request
# 5. ✅ Receives reference number
# 6. ✅ Can track request by reference
# 7. ✅ HR Dashboard loads
# 8. ✅ HR Dashboard requires API key
```

#### 5.3 Integration Testing

```bash
# Full user flow test
echo "=== Integration Test ==="

# 1. Submit request via frontend
REF_NUMBER=$(curl -X POST $BACKEND_URL/requests \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Integration Test Request",
    "type": "visa_application",
    "description": "End-to-end deployment test",
    "requester_name": "Test User",
    "requester_email": "test@example.com"
  }' | jq -r '.reference_number')

echo "Created request: $REF_NUMBER"

# 2. Track request
echo "Tracking request..."
curl -i $BACKEND_URL/requests/$REF_NUMBER

# 3. Test HR endpoints (requires HR_API_KEY)
# Get HR_API_KEY from Azure App Service configuration
HR_API_KEY="your-hr-api-key-here"

echo "Fetching HR queue..."
curl -i $BACKEND_URL/hr/requests \
  -H "X-HR-API-Key: $HR_API_KEY"

echo "✅ Integration test complete!"
```

#### 5.4 Security Verification

```bash
# Test rate limiting
echo "Testing rate limiting..."
for i in {1..12}; do
  echo "Request $i:"
  curl -w "\nHTTP %{http_code}\n" $BACKEND_URL/requests/$REF_NUMBER
  sleep 1
done
# Should see 429 (Too Many Requests) after ~10 requests

# Test CORS
echo "Testing CORS..."
curl -i $BACKEND_URL/health \
  -H "Origin: https://evil-site.com"
# Should NOT have Access-Control-Allow-Origin header for evil-site.com

# Test security headers
echo "Testing security headers..."
curl -I $BACKEND_URL/health
# Should see:
# - X-Content-Type-Options: nosniff
# - X-Frame-Options: DENY
# - Content-Security-Policy: ...
```

### Phase 6: Post-Deployment Configuration

#### 6.1 Update CORS with Final Frontend URL

```bash
# Get frontend URL
FRONTEND_URL=$(az staticwebapp show \
  --name YOUR-SWA-NAME \
  --resource-group hr-portal-rg \
  --query "defaultHostname" -o tsv)

echo "Frontend URL: https://$FRONTEND_URL"

# Update backend CORS
az webapp config appsettings set \
  --name YOUR-APP-NAME \
  --resource-group hr-portal-rg \
  --settings CORS_ORIGINS="https://$FRONTEND_URL"

# Restart app service to apply changes
az webapp restart \
  --name YOUR-APP-NAME \
  --resource-group hr-portal-rg
```

#### 6.2 Configure Custom Domain (Optional)

```bash
# For Static Web App
az staticwebapp hostname set \
  --name YOUR-SWA-NAME \
  --resource-group hr-portal-rg \
  --hostname hr.yourdomain.com

# For App Service
az webapp config hostname add \
  --webapp-name YOUR-APP-NAME \
  --resource-group hr-portal-rg \
  --hostname api.yourdomain.com
```

#### 6.3 Set Up Monitoring

```bash
# Enable Application Insights
az monitor app-insights component create \
  --app hr-portal-insights \
  --location eastus \
  --resource-group hr-portal-rg \
  --application-type web

# Link to App Service
INSTRUMENTATION_KEY=$(az monitor app-insights component show \
  --app hr-portal-insights \
  --resource-group hr-portal-rg \
  --query instrumentationKey -o tsv)

az webapp config appsettings set \
  --name YOUR-APP-NAME \
  --resource-group hr-portal-rg \
  --settings APPINSIGHTS_INSTRUMENTATIONKEY="$INSTRUMENTATION_KEY"
```

## 🔧 Troubleshooting

### Issue: Backend Health Check Fails

```bash
# Check App Service status
az webapp show \
  --name YOUR-APP-NAME \
  --resource-group hr-portal-rg \
  --query "state" -o tsv

# View logs
az webapp log tail \
  --name YOUR-APP-NAME \
  --resource-group hr-portal-rg

# Check startup command
az webapp config show \
  --name YOUR-APP-NAME \
  --resource-group hr-portal-rg \
  --query "appCommandLine" -o tsv

# Restart app
az webapp restart \
  --name YOUR-APP-NAME \
  --resource-group hr-portal-rg
```

### Issue: Frontend Build Fails

```bash
# Check GitHub Actions logs
gh run list --workflow=frontend-deploy.yml --limit 1
gh run view --log

# Test build locally
cd frontend
npm install
npm run build
# Check for errors
```

### Issue: CORS Errors

```bash
# Verify CORS settings
az webapp config appsettings list \
  --name YOUR-APP-NAME \
  --resource-group hr-portal-rg \
  --query "[?name=='CORS_ORIGINS'].value" -o tsv

# Update if needed
az webapp config appsettings set \
  --name YOUR-APP-NAME \
  --resource-group hr-portal-rg \
  --settings CORS_ORIGINS="https://YOUR-CORRECT-FRONTEND-URL.azurestaticapps.net"

# Restart
az webapp restart \
  --name YOUR-APP-NAME \
  --resource-group hr-portal-rg
```

## 📊 Monitoring Commands

```bash
# View recent logs
az webapp log tail \
  --name YOUR-APP-NAME \
  --resource-group hr-portal-rg

# Check metrics
az monitor metrics list \
  --resource /subscriptions/YOUR-SUB/resourceGroups/hr-portal-rg/providers/Microsoft.Web/sites/YOUR-APP-NAME \
  --metric "Requests,AverageResponseTime,Http5xx"

# View deployment history
az webapp deployment list-publishing-credentials \
  --name YOUR-APP-NAME \
  --resource-group hr-portal-rg
```

## 🔄 Redeployment

To redeploy after changes:

```bash
# 1. Make changes
git checkout -b feature/my-changes

# 2. Commit changes
git add .
git commit -m "Description of changes"

# 3. Push and create PR
git push origin feature/my-changes
gh pr create

# 4. After review, merge to main
gh pr merge --squash

# 5. Deployment triggers automatically
# Monitor at: https://github.com/ismaelloveexcel/hr-command-center/actions
```

## 🔐 Secrets Rotation

### Rotate HR_API_KEY

```bash
# Generate new key
NEW_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(32))')

# Update in Azure
az webapp config appsettings set \
  --name YOUR-APP-NAME \
  --resource-group hr-portal-rg \
  --settings HR_API_KEY="$NEW_KEY"

# Restart app
az webapp restart \
  --name YOUR-APP-NAME \
  --resource-group hr-portal-rg

# Share new key with HR staff securely
echo "New HR API Key: $NEW_KEY"
```

### Rotate Publish Profile

```bash
# Download new profile
az webapp deployment list-publishing-profiles \
  --name YOUR-APP-NAME \
  --resource-group hr-portal-rg \
  --xml > new-publish-profile.xml

# Update GitHub secret manually:
# Go to: Settings → Secrets → AZURE_BACKEND_PUBLISH_PROFILE
# Paste content of new-publish-profile.xml

# Delete local file
rm new-publish-profile.xml
```

## 📈 Scaling

### Scale App Service

```bash
# Scale up (more powerful instance)
az appservice plan update \
  --name hr-portal-plan \
  --resource-group hr-portal-rg \
  --sku S1

# Scale out (more instances)
az appservice plan update \
  --name hr-portal-plan \
  --resource-group hr-portal-rg \
  --number-of-workers 3
```

### Database Migration (SQLite → PostgreSQL)

```bash
# Create PostgreSQL server
az postgres flexible-server create \
  --name hr-portal-db \
  --resource-group hr-portal-rg \
  --location eastus \
  --admin-user hradmin \
  --admin-password "YOUR-SECURE-PASSWORD" \
  --sku-name Standard_B1ms \
  --tier Burstable

# Update connection string
DB_URL="postgresql://hradmin:YOUR-SECURE-PASSWORD@hr-portal-db.postgres.database.azure.com:5432/hrportal"

az webapp config appsettings set \
  --name YOUR-APP-NAME \
  --resource-group hr-portal-rg \
  --settings DATABASE_URL="$DB_URL"

# Restart
az webapp restart \
  --name YOUR-APP-NAME \
  --resource-group hr-portal-rg
```

## 🆘 Emergency Procedures

### Rollback Deployment

```bash
# List recent deployments
az webapp deployment list \
  --name YOUR-APP-NAME \
  --resource-group hr-portal-rg

# Rollback via Azure Portal:
# App Service → Deployment Center → Logs → Select previous deployment → Redeploy

# Or revert in git
git revert HEAD
git push origin main
```

### Take Application Offline

```bash
# Stop App Service
az webapp stop \
  --name YOUR-APP-NAME \
  --resource-group hr-portal-rg

# Stop Static Web App (disable in GitHub Actions)
# Or delete the deployment
```

### Emergency Contact

- **Azure Support**: https://portal.azure.com → Help + support
- **GitHub Support**: https://support.github.com
- **Repository Owner**: @ismaelloveexcel

## 📚 References

- [Deployment Checklist](./DEPLOYMENT_CHECKLIST.md) - Complete pre-deployment checklist
- [Azure Setup Guide](./AZURE_SETUP_GUIDE.md) - Detailed Azure configuration
- [Azure Deployment](./AZURE_DEPLOYMENT.md) - Architecture and design
- [Workflow Consolidation](./WORKFLOW_CONSOLIDATION.md) - Workflow management
- [Backend README](../backend/README.md) - Backend documentation
- [Frontend README](../frontend/README.md) - Frontend documentation

---

**Last Updated**: 2026-02-01
**Maintainer**: @ismaelloveexcel
**Status**: Production Ready
