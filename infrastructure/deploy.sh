#!/bin/bash
#
# UAE HR Portal - Azure Deployment Script
# 
# Usage: ./deploy.sh <backend-name> <frontend-name> <resource-group>
#
# This script:
# 1. Creates/verifies Azure resources
# 2. Configures GitHub secrets
# 3. Triggers deployment
#
# Prerequisites:
# - Azure CLI (az) logged in
# - GitHub CLI (gh) logged in
#

set -e

# Parse arguments or use defaults
BACKEND_NAME="${1:-baynunah-hr-api}"
FRONTEND_NAME="${2:-hrportal-frontend-new}"
RG="${3:-baynunah-hr-portal-rg}"

# Derived values
BACKEND_URL="https://${BACKEND_NAME}.azurewebsites.net"

echo "========================================"
echo "UAE HR Portal - Azure Deployment"
echo "========================================"
echo ""
echo "Backend:  $BACKEND_NAME"
echo "Frontend: $FRONTEND_NAME"
echo "Resource Group: $RG"
echo ""

# Verify Azure login
if ! az account show &>/dev/null; then
    echo "❌ Not logged into Azure. Run: az login"
    exit 1
fi

# Verify GitHub login
if ! gh auth status &>/dev/null; then
    echo "❌ Not logged into GitHub. Run: gh auth login"
    exit 1
fi

# Get repo
REPO=$(gh repo view --json nameWithOwner -q '.nameWithOwner' 2>/dev/null)
if [ -z "$REPO" ]; then
    REPO="ismaelloveexcel/hr-command-center"
fi
echo "Repository: $REPO"
echo ""

# Step 1: Ensure resource group
echo "[1/7] Resource group..."
az group show -n "$RG" -o none 2>/dev/null || \
    az group create -n "$RG" -l eastus -o none
echo "✓ Ready"

# Step 2: App Service Plan (Free tier)
echo "[2/7] App Service plan..."
PLAN="${BACKEND_NAME}-plan"
az appservice plan show -n "$PLAN" -g "$RG" -o none 2>/dev/null || \
    az appservice plan create -n "$PLAN" -g "$RG" --sku F1 --is-linux -o none
echo "✓ Ready"

# Step 3: Web App
echo "[3/7] Web app..."
az webapp show -n "$BACKEND_NAME" -g "$RG" -o none 2>/dev/null || \
    az webapp create -n "$BACKEND_NAME" -g "$RG" -p "$PLAN" --runtime "PYTHON:3.11" -o none
echo "✓ Ready"

# Step 4: Configure Web App
echo "[4/7] Configuring..."
FRONTEND_URL=$(az staticwebapp show -n "$FRONTEND_NAME" -g "$RG" --query "defaultHostname" -o tsv 2>/dev/null)
FRONTEND_URL="https://${FRONTEND_URL}"

az webapp config set -n "$BACKEND_NAME" -g "$RG" \
    --startup-file "gunicorn main:app --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000" \
    -o none

az webapp config appsettings set -n "$BACKEND_NAME" -g "$RG" \
    --settings DATABASE_URL="sqlite:///./hr_portal.db" CORS_ORIGINS="$FRONTEND_URL" \
    -o none
echo "✓ Configured"

# Step 5: Get credentials
echo "[5/7] Getting credentials..."
PUBLISH_PROFILE=$(az webapp deployment list-publishing-profiles -n "$BACKEND_NAME" -g "$RG" --xml)
SWA_TOKEN=$(az staticwebapp secrets list -n "$FRONTEND_NAME" -g "$RG" --query "properties.apiKey" -o tsv)
echo "✓ Got credentials"

# Step 6: Set GitHub secrets
echo "[6/7] Setting GitHub secrets..."
gh secret set AZURE_BACKEND_APP_NAME -b "$BACKEND_NAME" -R "$REPO"
gh secret set AZURE_BACKEND_PUBLISH_PROFILE -b "$PUBLISH_PROFILE" -R "$REPO"
gh secret set REACT_APP_API_URL -b "$BACKEND_URL" -R "$REPO"
gh secret set AZURE_STATIC_WEB_APPS_API_TOKEN -b "$SWA_TOKEN" -R "$REPO"
echo "✓ Secrets configured"

# Step 7: Trigger deployment
echo "[7/7] Triggering deployment..."
gh workflow run backend-deploy.yml -R "$REPO" 2>/dev/null || true
gh workflow run frontend-deploy.yml -R "$REPO" 2>/dev/null || true
echo "✓ Deployment triggered"

echo ""
echo "========================================"
echo "✅ COMPLETE"
echo "========================================"
echo ""
echo "Frontend: $FRONTEND_URL"
echo "Backend:  $BACKEND_URL"
echo ""
echo "Check status: gh run list --limit 3 -R $REPO"
echo ""
