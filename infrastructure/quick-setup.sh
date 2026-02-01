#!/bin/bash
# ONE-COMMAND AZURE SETUP
# Usage: ./quick-setup.sh

set -e

echo "🚀 UAE HR Portal - Quick Setup"
echo ""

# Auto-detect existing Static Web App
EXISTING_SWA=$(az staticwebapp list --query "[0].{name:name,rg:resourceGroup,host:defaultHostname}" -o tsv 2>/dev/null | head -1)

if [ -n "$EXISTING_SWA" ]; then
    SWA_NAME=$(echo "$EXISTING_SWA" | cut -f1)
    RG=$(echo "$EXISTING_SWA" | cut -f2)
    FRONTEND_URL="https://$(echo "$EXISTING_SWA" | cut -f3)"
    echo "✓ Found existing Static Web App: $SWA_NAME"
    echo "✓ Resource Group: $RG"
    echo "✓ Frontend URL: $FRONTEND_URL"
else
    RG="hr-portal-rg"
    SWA_NAME="hr-portal-web"
    FRONTEND_URL="https://${SWA_NAME}.azurestaticapps.net"
    echo "Creating new resource group: $RG"
    az group create --name $RG --location eastus -o none
    echo "Creating Static Web App..."
    az staticwebapp create --name $SWA_NAME --resource-group $RG --sku Free -o none
fi

BACKEND_NAME="${SWA_NAME/web/api}"
BACKEND_NAME="${BACKEND_NAME/portal/api}"
if [[ "$BACKEND_NAME" == *"api-api"* ]]; then
    BACKEND_NAME="${SWA_NAME}-api"
fi
BACKEND_URL="https://${BACKEND_NAME}.azurewebsites.net"

echo ""
echo "📦 Creating Backend: $BACKEND_NAME"

# Create App Service Plan (Free tier)
az appservice plan create --name "${BACKEND_NAME}-plan" --resource-group $RG --sku F1 --is-linux -o none 2>/dev/null || true

# Create Web App
az webapp create --name $BACKEND_NAME --resource-group $RG --plan "${BACKEND_NAME}-plan" --runtime "PYTHON:3.11" -o none 2>/dev/null || true

# Configure
az webapp config set --name $BACKEND_NAME --resource-group $RG --startup-file "gunicorn main:app --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000" -o none

az webapp config appsettings set --name $BACKEND_NAME --resource-group $RG --settings DATABASE_URL="sqlite:///./hr_portal.db" CORS_ORIGINS="$FRONTEND_URL" -o none

echo "✓ Backend configured"

echo ""
echo "🔑 Setting GitHub Secrets..."

gh secret set AZURE_BACKEND_APP_NAME --body "$BACKEND_NAME" 2>/dev/null
gh secret set REACT_APP_API_URL --body "$BACKEND_URL" 2>/dev/null

PUBLISH_PROFILE=$(az webapp deployment list-publishing-profiles --name $BACKEND_NAME --resource-group $RG --xml)
gh secret set AZURE_BACKEND_PUBLISH_PROFILE --body "$PUBLISH_PROFILE" 2>/dev/null

SWA_TOKEN=$(az staticwebapp secrets list --name $SWA_NAME --resource-group $RG --query "properties.apiKey" -o tsv)
gh secret set AZURE_STATIC_WEB_APPS_API_TOKEN --body "$SWA_TOKEN" 2>/dev/null

echo "✓ GitHub secrets configured"

echo ""
echo "🚀 Triggering deployment..."
gh workflow run backend-deploy.yml 2>/dev/null || echo "Will deploy on next push"
gh workflow run frontend-deploy.yml 2>/dev/null || echo "Will deploy on next push"

echo ""
echo "=============================================="
echo "✅ SETUP COMPLETE!"
echo "=============================================="
echo ""
echo "Frontend: $FRONTEND_URL"
echo "Backend:  $BACKEND_URL"
echo ""
echo "App will be live in ~5 minutes."
echo "Check status: gh run list --limit 3"
