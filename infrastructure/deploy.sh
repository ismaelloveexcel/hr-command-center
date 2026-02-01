#!/bin/bash
#
# UAE HR Portal - Azure Deployment Script
# Version: 2.0 - Robust deployment with conflict handling
#

set -e

# Configuration
BACKEND_NAME="baynunah-hr-api"
FRONTEND_NAME="baynunah-hr-portal"
RG="baynunah-hr-rg"
LOCATION="centralus"
REPO="ismaelloveexcel/hr-command-center"

# Derived URLs
BACKEND_URL="https://${BACKEND_NAME}.azurewebsites.net"
FRONTEND_URL="https://${FRONTEND_NAME}.azurestaticapps.net"

echo ""
echo "╔════════════════════════════════════════════╗"
echo "║   UAE HR Portal - Azure Deployment v2.0    ║"
echo "╚════════════════════════════════════════════╝"
echo ""
echo "  Frontend: $FRONTEND_URL"
echo "  Backend:  $BACKEND_URL"
echo "  Region:   $LOCATION"
echo ""

# Verify prerequisites
echo "Checking prerequisites..."
command -v az >/dev/null 2>&1 || { echo "❌ Azure CLI not found. Run: az login"; exit 1; }
command -v gh >/dev/null 2>&1 || { echo "❌ GitHub CLI not found."; exit 1; }
az account show >/dev/null 2>&1 || { echo "❌ Not logged into Azure. Run: az login"; exit 1; }
gh auth status >/dev/null 2>&1 || { echo "❌ Not logged into GitHub. Run: gh auth login"; exit 1; }
echo "✓ Prerequisites OK"
echo ""

# Step 1: Resource Group
echo "[1/8] Creating resource group in $LOCATION..."
az group create --name "$RG" --location "$LOCATION" --output none 2>/dev/null || true
echo "✓ Resource group: $RG"

# Step 2: Static Web App
echo "[2/8] Creating Static Web App..."
if az staticwebapp show --name "$FRONTEND_NAME" --resource-group "$RG" --output none 2>/dev/null; then
    echo "✓ Static Web App exists: $FRONTEND_NAME"
else
    echo "  Creating new Static Web App in $LOCATION..."
    az staticwebapp create \
        --name "$FRONTEND_NAME" \
        --resource-group "$RG" \
        --location "$LOCATION" \
        --sku Free \
        --output none
    echo "✓ Created: $FRONTEND_NAME"
fi

# Step 3: App Service Plan (Free tier - no quota issues)
echo "[3/8] Creating App Service Plan..."
PLAN="${BACKEND_NAME}-plan"
if az appservice plan show --name "$PLAN" --resource-group "$RG" --output none 2>/dev/null; then
    echo "✓ Plan exists: $PLAN"
else
    az appservice plan create \
        --name "$PLAN" \
        --resource-group "$RG" \
        --location "$LOCATION" \
        --sku F1 \
        --is-linux \
        --output none
    echo "✓ Created: $PLAN"
fi

# Step 4: Web App
echo "[4/8] Creating Web App..."
if az webapp show --name "$BACKEND_NAME" --resource-group "$RG" --output none 2>/dev/null; then
    echo "✓ Web App exists: $BACKEND_NAME"
else
    az webapp create \
        --name "$BACKEND_NAME" \
        --resource-group "$RG" \
        --plan "$PLAN" \
        --runtime "PYTHON:3.11" \
        --output none
    echo "✓ Created: $BACKEND_NAME"
fi

# Step 5: Configure Web App
echo "[5/8] Configuring Web App..."
az webapp config set \
    --name "$BACKEND_NAME" \
    --resource-group "$RG" \
    --startup-file "gunicorn main:app --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000" \
    --output none

# Generate a random HR API key if not provided
HR_API_KEY="${HR_API_KEY:-$(openssl rand -hex 24)}"

az webapp config appsettings set \
    --name "$BACKEND_NAME" \
    --resource-group "$RG" \
    --settings \
    DATABASE_URL="sqlite:///./hr_portal.db" \
    CORS_ORIGINS="$FRONTEND_URL" \
    DEBUG="false" \
    HR_API_KEY="$HR_API_KEY" \
    --output none

echo "  HR API Key: $HR_API_KEY"
echo "  (Save this key - HR staff need it to access the dashboard)"
echo "✓ Configuration applied"

# Step 6: Get Credentials
echo "[6/8] Retrieving deployment credentials..."
PUBLISH_PROFILE=$(az webapp deployment list-publishing-profiles \
    --name "$BACKEND_NAME" \
    --resource-group "$RG" \
    --xml 2>/dev/null)

if [ -z "$PUBLISH_PROFILE" ]; then
    echo "❌ Failed to get publish profile"
    exit 1
fi

SWA_TOKEN=$(az staticwebapp secrets list \
    --name "$FRONTEND_NAME" \
    --resource-group "$RG" \
    --query "properties.apiKey" \
    --output tsv 2>/dev/null)

if [ -z "$SWA_TOKEN" ]; then
    echo "❌ Failed to get Static Web App token"
    exit 1
fi
echo "✓ Credentials retrieved"

# Step 7: Set GitHub Secrets
echo "[7/8] Configuring GitHub secrets..."
gh secret set AZURE_BACKEND_APP_NAME --body "$BACKEND_NAME" --repo "$REPO"
gh secret set AZURE_BACKEND_PUBLISH_PROFILE --body "$PUBLISH_PROFILE" --repo "$REPO"
gh secret set REACT_APP_API_URL --body "$BACKEND_URL" --repo "$REPO"
gh secret set AZURE_STATIC_WEB_APPS_API_TOKEN --body "$SWA_TOKEN" --repo "$REPO"
gh secret set HR_API_KEY --body "$HR_API_KEY" --repo "$REPO"
echo "✓ GitHub secrets configured"

# Step 8: Trigger Deployment
echo "[8/8] Triggering deployment workflows..."
gh workflow run backend-deploy.yml --repo "$REPO" 2>/dev/null && echo "  → Backend workflow triggered" || echo "  → Backend: will deploy on next push"
sleep 2
gh workflow run frontend-deploy.yml --repo "$REPO" 2>/dev/null && echo "  → Frontend workflow triggered" || echo "  → Frontend: will deploy on next push"

echo ""
echo "╔════════════════════════════════════════════╗"
echo "║            ✅ DEPLOYMENT COMPLETE          ║"
echo "╚════════════════════════════════════════════╝"
echo ""
echo "  Frontend: $FRONTEND_URL"
echo "  Backend:  $BACKEND_URL"
echo ""
echo "  HR API Key: $HR_API_KEY"
echo "  (Share this with HR staff to access the dashboard)"
echo ""
echo "  Your app will be live in 3-5 minutes."
echo ""
echo "  Check deployment status:"
echo "    gh run list --limit 3 --repo $REPO"
echo ""
echo "  Test backend health:"
echo "    curl $BACKEND_URL/health"
echo ""
