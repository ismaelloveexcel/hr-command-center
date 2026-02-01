#!/bin/bash
# CREATE BRAND NEW UAE HR PORTAL
# Fresh setup - no old apps

echo "🚀 Creating NEW UAE HR Portal..."

# NEW resource group and apps
RG="uae-hr-portal-rg"
BACKEND_NAME="uae-hr-portal-api"
SWA_NAME="uae-hr-portal-web"
PLAN_NAME="uae-hr-portal-plan"

echo "[1/8] Creating new resource group..."
az group create --name "$RG" --location eastus -o none

echo "[2/8] Creating App Service Plan (Free tier)..."
az appservice plan create --name "$PLAN_NAME" --resource-group "$RG" --sku F1 --is-linux -o none

echo "[3/8] Creating Backend Web App..."
az webapp create --name "$BACKEND_NAME" --resource-group "$RG" --plan "$PLAN_NAME" --runtime "PYTHON:3.11" -o none

echo "[4/8] Creating Static Web App..."
az staticwebapp create --name "$SWA_NAME" --resource-group "$RG" --sku Free -o none

# Get the frontend URL
FRONTEND_URL=$(az staticwebapp show --name "$SWA_NAME" --resource-group "$RG" --query "defaultHostname" -o tsv)
FRONTEND_URL="https://$FRONTEND_URL"
BACKEND_URL="https://${BACKEND_NAME}.azurewebsites.net"

echo "[5/8] Configuring backend..."
az webapp config set --name "$BACKEND_NAME" --resource-group "$RG" --startup-file "gunicorn main:app --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000" -o none
az webapp config appsettings set --name "$BACKEND_NAME" --resource-group "$RG" --settings DATABASE_URL="sqlite:///./hr_portal.db" CORS_ORIGINS="$FRONTEND_URL" -o none

echo "[6/8] Setting GitHub secrets..."
gh secret set AZURE_BACKEND_APP_NAME --body "$BACKEND_NAME" --repo ismaelloveexcel/hr-command-center
gh secret set REACT_APP_API_URL --body "$BACKEND_URL" --repo ismaelloveexcel/hr-command-center

echo "[7/8] Getting and setting credentials..."
PROFILE=$(az webapp deployment list-publishing-profiles --name "$BACKEND_NAME" --resource-group "$RG" --xml)
echo "$PROFILE" | gh secret set AZURE_BACKEND_PUBLISH_PROFILE --repo ismaelloveexcel/hr-command-center

TOKEN=$(az staticwebapp secrets list --name "$SWA_NAME" --resource-group "$RG" --query "properties.apiKey" -o tsv)
echo "$TOKEN" | gh secret set AZURE_STATIC_WEB_APPS_API_TOKEN --repo ismaelloveexcel/hr-command-center

echo "[8/8] Triggering deployment..."
gh workflow run backend-deploy.yml --repo ismaelloveexcel/hr-command-center
gh workflow run frontend-deploy.yml --repo ismaelloveexcel/hr-command-center

echo ""
echo "=============================================="
echo "✅ NEW UAE HR PORTAL CREATED!"
echo "=============================================="
echo ""
echo "Frontend: $FRONTEND_URL"
echo "Backend:  $BACKEND_URL"
echo ""
echo "App will be live in ~5 minutes."
echo "Check: gh run list --limit 3"
