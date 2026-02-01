# Deployment Troubleshooting Guide

## Current Deployment Status (As of Feb 1, 2026)

### 🔴 Backend Deployment: FAILING
**Error**: `Publish profile is invalid for app-name and slot-name provided`

**Status**: All recent backend deployments are failing (last 10+ attempts)

**Impact**: Backend API is not being updated with latest code changes

### ✅ Frontend Deployment: WORKING
**Status**: Frontend deployments to Azure Static Web Apps are succeeding

**Latest Success**: Feb 1, 2026 at 15:57 UTC

---

## Root Cause Analysis

### Backend Deployment Failure

The backend deployment is failing at the Azure Web Apps deployment step with the error:

```
##[error]Deployment Failed, Error: Publish profile is invalid for app-name 
and slot-name provided. Provide correct publish profile credentials for app.
```

**Why This Happens:**

1. **Expired/Invalid Publish Profile**: Azure publish profiles can become invalid if:
   - The App Service was recreated
   - Deployment credentials were regenerated
   - The App Service was deleted and recreated with the same name
   - The resource group or subscription changed

2. **Mismatched App Name**: The `AZURE_BACKEND_APP_NAME` secret doesn't match the actual App Service name in the publish profile

3. **Wrong Slot**: The workflow is trying to deploy to 'production' slot, but the publish profile might be for a different slot or configuration

**Evidence from Logs:**
- Build phase completes successfully ✅
- Dependencies install correctly ✅
- Application verification passes ✅
- Deployment package creation succeeds ✅
- **Azure deployment fails** ❌

---

## Immediate Fix: Regenerate & Update Secrets

### Step 1: Verify Azure Resources Exist

```bash
# Login to Azure
az login

# List all App Services in your subscription
az webapp list --query "[].{name:name, resourceGroup:resourceGroup, state:state}" -o table

# Check if your specific app exists
az webapp show --name YOUR-APP-NAME --resource-group hr-portal-rg
```

**Expected Output**: Should show your backend App Service with state "Running"

**If App Service doesn't exist**: You need to create it first (see "Creating Azure Resources" section below)

### Step 2: Regenerate Publish Profile

```bash
# Set your actual app name
BACKEND_NAME="your-actual-backend-app-name"
RESOURCE_GROUP="hr-portal-rg"

# Get fresh publish profile
az webapp deployment list-publishing-profiles \
  --name "$BACKEND_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --xml > publish-profile.xml

# View the file
cat publish-profile.xml
```

### Step 3: Update GitHub Secrets

1. Go to GitHub repository settings:
   ```
   https://github.com/ismaelloveexcel/hr-command-center/settings/secrets/actions
   ```

2. Update these secrets:

   **a) AZURE_BACKEND_APP_NAME**
   - Click on the secret name
   - Update with your actual App Service name (e.g., `hrportal-api-123456`)
   - Save

   **b) AZURE_BACKEND_PUBLISH_PROFILE**
   - Click on the secret name
   - Copy the ENTIRE contents of `publish-profile.xml` file
   - Paste into the secret value
   - Save

3. **Delete the local publish profile file** (security):
   ```bash
   rm publish-profile.xml
   ```

### Step 4: Verify Other Secrets

Also verify these secrets are correctly set:

**AZURE_STATIC_WEB_APPS_API_TOKEN** (Frontend - already working)
```bash
# Get the token
SWA_NAME="your-static-web-app-name"
az staticwebapp secrets list \
  --name "$SWA_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --query "properties.apiKey" -o tsv
```

**REACT_APP_API_URL** (Backend URL for frontend)
```bash
# Should be your backend URL
echo "https://${BACKEND_NAME}.azurewebsites.net"
```

### Step 5: Trigger Deployment

After updating secrets:

```bash
# Option A: Manual workflow trigger (recommended for testing)
gh workflow run backend-deploy.yml

# Monitor the run
gh run watch

# Option B: Push a commit to trigger automatically
git commit --allow-empty -m "Trigger deployment after secret update"
git push origin main
```

---

## Alternative: Use Automated Setup Script

If you're starting fresh or want to reset everything:

```bash
cd infrastructure
./setup-azure.sh
```

This script will:
1. ✅ Create/verify all Azure resources
2. ✅ Get deployment credentials
3. ✅ Automatically set all GitHub secrets
4. ✅ Trigger deployment

**Time**: 5-10 minutes

**Requirements**:
- Azure CLI installed and logged in
- GitHub CLI installed and logged in
- Permissions to create Azure resources

---

## Creating Azure Resources (If They Don't Exist)

### Quick Method: Use Bicep Template

```bash
cd infrastructure

# Create resource group
az group create --name hr-portal-rg --location eastus

# Deploy using Bicep
az deployment group create \
  --resource-group hr-portal-rg \
  --template-file main.bicep \
  --parameters baseName=hrportal location=eastus

# Get outputs (including app names)
az deployment group show \
  --resource-group hr-portal-rg \
  --name main \
  --query properties.outputs
```

### Manual Method: Azure Portal

1. **Login to Azure Portal**: https://portal.azure.com

2. **Create Resource Group**:
   - Search for "Resource groups"
   - Click "Create"
   - Name: `hr-portal-rg`
   - Region: East US
   - Click "Review + create"

3. **Create App Service Plan**:
   - Search for "App Service plans"
   - Click "Create"
   - Resource Group: `hr-portal-rg`
   - Name: `hrportal-plan`
   - Operating System: Linux
   - Region: East US
   - Pricing tier: B1 (Basic) or higher
   - Click "Review + create"

4. **Create Backend App Service**:
   - Search for "App Services"
   - Click "Create" → "Web App"
   - Resource Group: `hr-portal-rg`
   - Name: `hrportal-api-XXXXX` (must be globally unique)
   - Publish: Code
   - Runtime stack: Python 3.11
   - Operating System: Linux
   - Region: East US
   - App Service Plan: Select `hrportal-plan`
   - Click "Review + create"

5. **Create Static Web App** (Frontend):
   - Search for "Static Web Apps"
   - Click "Create"
   - Resource Group: `hr-portal-rg`
   - Name: `hrportal-web-XXXXX`
   - Plan type: Free
   - Region: East US 2
   - Source: Other (we'll deploy via GitHub Actions)
   - Click "Review + create"

6. **Configure Backend App Service**:
   - Open the App Service in Azure Portal
   - Go to Configuration → General settings
   - Startup Command: `bash startup.sh`
   - Save

   - Go to Configuration → Application settings
   - Add these settings:
     ```
     DATABASE_URL=sqlite:///./hr_portal.db
     CORS_ORIGINS=https://YOUR-FRONTEND-URL.azurestaticapps.net
     HR_API_KEY=<generate-strong-key>
     DEBUG=false
     ```
   - Save

---

## Verification Checklist

After fixing the secrets and deploying:

### ✅ Backend Health Check

```bash
BACKEND_URL="https://YOUR-APP-NAME.azurewebsites.net"

# Should return: {"status":"healthy","service":"UAE HR Portal API"}
curl -i $BACKEND_URL/health

# Should return API documentation
open $BACKEND_URL/docs
```

### ✅ Frontend Check

```bash
FRONTEND_URL="https://YOUR-SWA-NAME.azurestaticapps.net"

# Should load the React app
open $FRONTEND_URL
```

### ✅ Integration Test

```bash
# Submit a test request via API
REF=$(curl -X POST $BACKEND_URL/requests \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Request",
    "type": "visa_application",
    "description": "Testing deployment",
    "requester_name": "Test User",
    "requester_email": "test@example.com"
  }' | jq -r '.reference_number')

echo "Reference number: $REF"

# Track the request
curl $BACKEND_URL/requests/$REF

# Check via frontend
open "$FRONTEND_URL?ref=$REF"
```

---

## Common Issues & Solutions

### Issue: "App Service not found"

**Cause**: The app doesn't exist or was deleted

**Solution**:
1. Verify app exists: `az webapp list -o table`
2. If missing, create it using Bicep template or Azure Portal
3. Update GitHub secrets with new app name

### Issue: "Health check fails after deployment"

**Cause**: App is starting or configuration is wrong

**Solution**:
```bash
# Check app logs
az webapp log tail \
  --name YOUR-APP-NAME \
  --resource-group hr-portal-rg

# Restart the app
az webapp restart \
  --name YOUR-APP-NAME \
  --resource-group hr-portal-rg

# Wait 30 seconds and try health check again
sleep 30
curl https://YOUR-APP-NAME.azurewebsites.net/health
```

### Issue: "CORS errors in browser console"

**Cause**: Backend CORS_ORIGINS doesn't include frontend URL

**Solution**:
```bash
# Get your frontend URL
FRONTEND_URL=$(az staticwebapp show \
  --name YOUR-SWA-NAME \
  --resource-group hr-portal-rg \
  --query "defaultHostname" -o tsv)

echo "Frontend URL: https://$FRONTEND_URL"

# Update backend CORS setting
az webapp config appsettings set \
  --name YOUR-BACKEND-NAME \
  --resource-group hr-portal-rg \
  --settings CORS_ORIGINS="https://$FRONTEND_URL"

# Restart backend
az webapp restart \
  --name YOUR-BACKEND-NAME \
  --resource-group hr-portal-rg
```

### Issue: "Rate limiting not working"

**Cause**: Rate limiting requires Redis or in-memory storage

**Solution**: The app uses in-memory rate limiting. To verify:
```bash
# Make multiple rapid requests
for i in {1..15}; do
  curl -w "\nStatus: %{http_code}\n" \
    $BACKEND_URL/requests/REF-2024-001
  sleep 0.5
done

# Should see 429 (Too Many Requests) after ~10 requests
```

### Issue: "Database not persisting data"

**Cause**: Using SQLite on ephemeral filesystem

**Solution for Production**: Migrate to Azure PostgreSQL
```bash
# Create PostgreSQL database
az postgres flexible-server create \
  --name hrportal-db \
  --resource-group hr-portal-rg \
  --location eastus \
  --admin-user hradmin \
  --admin-password "YOUR-SECURE-PASSWORD" \
  --sku-name Standard_B1ms \
  --tier Burstable \
  --storage-size 32

# Create database
az postgres flexible-server db create \
  --resource-group hr-portal-rg \
  --server-name hrportal-db \
  --database-name hrportal

# Update connection string in App Service
DB_URL="postgresql://hradmin:YOUR-SECURE-PASSWORD@hrportal-db.postgres.database.azure.com:5432/hrportal?sslmode=require"

az webapp config appsettings set \
  --name YOUR-BACKEND-NAME \
  --resource-group hr-portal-rg \
  --settings DATABASE_URL="$DB_URL"

# Restart app
az webapp restart \
  --name YOUR-BACKEND-NAME \
  --resource-group hr-portal-rg
```

---

## Monitoring & Debugging

### View Deployment Logs

```bash
# GitHub Actions logs
gh run list --workflow=backend-deploy.yml --limit 5
gh run view --log

# Azure App Service logs
az webapp log tail \
  --name YOUR-APP-NAME \
  --resource-group hr-portal-rg

# Or download logs
az webapp log download \
  --name YOUR-APP-NAME \
  --resource-group hr-portal-rg \
  --log-file app-logs.zip
```

### Check Resource Status

```bash
# All resources in resource group
az resource list \
  --resource-group hr-portal-rg \
  --output table

# App Service status
az webapp show \
  --name YOUR-APP-NAME \
  --resource-group hr-portal-rg \
  --query "{name:name, state:state, defaultHostName:defaultHostName}"

# Static Web App status
az staticwebapp show \
  --name YOUR-SWA-NAME \
  --resource-group hr-portal-rg \
  --query "{name:name, defaultHostname:defaultHostname}"
```

### Test Endpoints

```bash
BACKEND_URL="https://YOUR-APP-NAME.azurewebsites.net"

# Health check
curl $BACKEND_URL/health

# API docs (interactive)
open $BACKEND_URL/docs

# Create request
curl -X POST $BACKEND_URL/requests \
  -H "Content-Type: application/json" \
  -d @- <<EOF
{
  "title": "Test Request",
  "type": "visa_application",
  "description": "Testing API",
  "requester_name": "John Doe",
  "requester_email": "john@example.com"
}
EOF

# Get HR stats (requires API key)
curl $BACKEND_URL/hr/stats \
  -H "X-HR-API-Key: YOUR-HR-API-KEY"
```

---

## Security Considerations

### After Fixing Deployment

1. **Rotate HR API Key** (if exposed):
   ```bash
   NEW_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(32))')
   
   az webapp config appsettings set \
     --name YOUR-APP-NAME \
     --resource-group hr-portal-rg \
     --settings HR_API_KEY="$NEW_KEY"
   
   echo "New HR API Key: $NEW_KEY"
   # Share this securely with HR staff only
   ```

2. **Verify Security Headers**:
   ```bash
   curl -I $BACKEND_URL/health | grep -E "X-Content-Type-Options|X-Frame-Options|Content-Security-Policy"
   ```

3. **Test Rate Limiting**:
   ```bash
   # Should get 429 after ~10 requests in quick succession
   for i in {1..15}; do
     curl -w "\nHTTP %{http_code}\n" $BACKEND_URL/health
   done
   ```

4. **Review CORS Configuration**:
   ```bash
   # Check current CORS setting
   az webapp config appsettings list \
     --name YOUR-APP-NAME \
     --resource-group hr-portal-rg \
     --query "[?name=='CORS_ORIGINS'].value" -o tsv
   ```

---

## Emergency Procedures

### Roll Back to Previous Version

```bash
# List recent deployments
az webapp deployment list \
  --name YOUR-APP-NAME \
  --resource-group hr-portal-rg

# Via Azure Portal:
# App Service → Deployment Center → Logs
# Select previous successful deployment → Redeploy

# Or via Git revert
git log --oneline -5
git revert HEAD
git push origin main
```

### Take App Offline (Maintenance Mode)

```bash
# Stop the app
az webapp stop \
  --name YOUR-APP-NAME \
  --resource-group hr-portal-rg

# Start the app
az webapp start \
  --name YOUR-APP-NAME \
  --resource-group hr-portal-rg
```

---

## Next Steps After Resolution

1. **✅ Verify Deployment**: Run all verification checks above

2. **📊 Set Up Monitoring**:
   ```bash
   # Enable Application Insights (recommended)
   az monitor app-insights component create \
     --app hrportal-insights \
     --location eastus \
     --resource-group hr-portal-rg \
     --application-type web
   ```

3. **🔄 Set Up Automated Backups**:
   - For production, migrate to PostgreSQL with automated backups
   - Enable App Service backup for configuration

4. **📚 Document Custom Configuration**:
   - Save your actual app names
   - Document any custom settings
   - Keep secure record of secrets (use password manager)

5. **🧪 Test All Features**:
   - Submit request via frontend
   - Track request by reference number
   - Test HR dashboard (with API key)
   - Verify email notifications (if configured)

---

## Support Resources

- **Azure Documentation**: https://docs.microsoft.com/azure/app-service/
- **GitHub Actions**: https://docs.github.com/actions
- **Repository Issues**: https://github.com/ismaelloveexcel/hr-command-center/issues
- **Azure Support**: https://portal.azure.com → Help + support

---

## Summary

**To fix the current deployment failure:**

1. ✅ Verify Azure App Service exists
2. ✅ Regenerate publish profile from Azure
3. ✅ Update `AZURE_BACKEND_PUBLISH_PROFILE` secret in GitHub
4. ✅ Verify `AZURE_BACKEND_APP_NAME` matches actual app name
5. ✅ Trigger deployment via GitHub Actions
6. ✅ Verify health check passes

**Estimated time to fix**: 10-15 minutes

**Alternative**: Run `infrastructure/setup-azure.sh` for fully automated setup (5-10 minutes)

---

**Last Updated**: February 1, 2026  
**Status**: Deployment failure identified and resolution documented  
**Next Action**: Update GitHub secrets with fresh Azure credentials
