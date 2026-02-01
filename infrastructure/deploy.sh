#!/bin/bash
#
# UAE HR Portal - Azure Deployment Script
#

set -e

# YOUR CONFIGURATION
BACKEND_NAME="baynunah-hr-api"
FRONTEND_NAME="baynunah-hr-portal"
RG="baynunah-hr-portal-rg"
LOCATION="centralus"
REPO="ismaelloveexcel/hr-command-center"

# URLs
BACKEND_URL="https://${BACKEND_NAME}.azurewebsites.net"
FRONTEND_URL="https://${FRONTEND_NAME}.azurestaticapps.net"

echo "========================================"
echo "UAE HR Portal - Azure Deployment"
echo "========================================"
echo ""
echo "Frontend: $FRONTEND_URL"
echo "Backend:  $BACKEND_URL"
echo ""

# Step 1: Resource group
echo "[1/8] Resource group..."
az group create -n "$RG" -l "$LOCATION" -o none 2>/dev/null || true
echo "✓ Ready"

# Step 2: Static Web App (create with specific name)
echo "[2/8] Creating Static Web App..."
az staticwebapp show -n "$FRONTEND_NAME" -g "$RG" -o none 2>/dev/null || \
    az staticwebapp create -n "$FRONTEND_NAME" -g "$RG" -l "centralus" --sku Free -o none
echo "✓ $FRONTEND_NAME created"

# Step 3: App Service Plan
echo "[3/8] App Service plan..."
PLAN="${BACKEND_NAME}-plan"
az appservice plan show -n "$PLAN" -g "$RG" -o none 2>/dev/null || \
    az appservice plan create -n "$PLAN" -g "$RG" --sku F1 --is-linux -o none
echo "✓ Ready"

# Step 4: Web App
echo "[4/8] Web app..."
az webapp show -n "$BACKEND_NAME" -g "$RG" -o none 2>/dev/null || \
    az webapp create -n "$BACKEND_NAME" -g "$RG" -p "$PLAN" --runtime "PYTHON:3.11" -o none
echo "✓ Ready"

# Step 5: Configure
echo "[5/8] Configuring..."
az webapp config set -n "$BACKEND_NAME" -g "$RG" \
    --startup-file "gunicorn main:app --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000" \
    -o none

az webapp config appsettings set -n "$BACKEND_NAME" -g "$RG" \
    --settings DATABASE_URL="sqlite:///./hr_portal.db" CORS_ORIGINS="$FRONTEND_URL" \
    -o none
echo "✓ Configured"

# Step 6: Get credentials
echo "[6/8] Getting credentials..."
PUBLISH_PROFILE=$(az webapp deployment list-publishing-profiles -n "$BACKEND_NAME" -g "$RG" --xml)
SWA_TOKEN=$(az staticwebapp secrets list -n "$FRONTEND_NAME" -g "$RG" --query "properties.apiKey" -o tsv)
echo "✓ Got credentials"

# Step 7: GitHub secrets
echo "[7/8] Setting GitHub secrets..."
gh secret set AZURE_BACKEND_APP_NAME -b "$BACKEND_NAME" -R "$REPO"
gh secret set AZURE_BACKEND_PUBLISH_PROFILE -b "$PUBLISH_PROFILE" -R "$REPO"
gh secret set REACT_APP_API_URL -b "$BACKEND_URL" -R "$REPO"
gh secret set AZURE_STATIC_WEB_APPS_API_TOKEN -b "$SWA_TOKEN" -R "$REPO"
echo "✓ Secrets set"

# Step 8: Deploy
echo "[8/8] Triggering deployment..."
gh workflow run backend-deploy.yml -R "$REPO" 2>/dev/null || true
gh workflow run frontend-deploy.yml -R "$REPO" 2>/dev/null || true

echo ""
echo "========================================"
echo "✅ COMPLETE"
echo "========================================"
echo ""
echo "Frontend: $FRONTEND_URL"
echo "Backend:  $BACKEND_URL"
echo ""
echo "App will be live in ~3 minutes."
echo "Check: gh run list --limit 3 -R $REPO"
