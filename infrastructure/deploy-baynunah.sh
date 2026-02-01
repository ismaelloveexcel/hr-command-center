#!/bin/bash
# FULLY AUTOMATED - NO INPUT NEEDED
# Hardcoded for baynunah-hr-portal

echo "🚀 Deploying UAE HR Portal..."

# Hardcoded values - YOUR setup
RG="baynunah-hr-portal-rg"
SWA_NAME="hrportal-frontend-new"
BACKEND_NAME="baynunah-hr-api"
FRONTEND_URL="https://proud-forest-051662503.4.azurestaticapps.net"
BACKEND_URL="https://baynunah-hr-api.azurewebsites.net"

echo "[1/7] Creating App Service Plan..."
az appservice plan create --name baynunah-plan --resource-group "$RG" --sku F1 --is-linux -o none 2>/dev/null || echo "Plan exists"

echo "[2/7] Creating Web App..."
az webapp create --name "$BACKEND_NAME" --resource-group "$RG" --plan baynunah-plan --runtime "PYTHON:3.11" -o none 2>/dev/null || echo "App exists"

echo "[3/7] Configuring startup..."
az webapp config set --name "$BACKEND_NAME" --resource-group "$RG" --startup-file "gunicorn main:app --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000" -o none

echo "[4/7] Setting environment variables..."
az webapp config appsettings set --name "$BACKEND_NAME" --resource-group "$RG" --settings DATABASE_URL="sqlite:///./hr_portal.db" CORS_ORIGINS="$FRONTEND_URL" -o none

echo "[5/7] Setting GitHub secrets..."
gh secret set AZURE_BACKEND_APP_NAME --body "$BACKEND_NAME" --repo ismaelloveexcel/hr-command-center
gh secret set REACT_APP_API_URL --body "$BACKEND_URL" --repo ismaelloveexcel/hr-command-center

echo "[6/7] Getting publish profile..."
PROFILE=$(az webapp deployment list-publishing-profiles --name "$BACKEND_NAME" --resource-group "$RG" --xml 2>/dev/null)
echo "$PROFILE" | gh secret set AZURE_BACKEND_PUBLISH_PROFILE --repo ismaelloveexcel/hr-command-center

echo "[7/7] Getting SWA token..."
TOKEN=$(az staticwebapp secrets list --name "$SWA_NAME" --resource-group "$RG" --query "properties.apiKey" -o tsv 2>/dev/null)
echo "$TOKEN" | gh secret set AZURE_STATIC_WEB_APPS_API_TOKEN --repo ismaelloveexcel/hr-command-center

echo ""
echo "🚀 Triggering deployment..."
gh workflow run backend-deploy.yml --repo ismaelloveexcel/hr-command-center
gh workflow run frontend-deploy.yml --repo ismaelloveexcel/hr-command-center

echo ""
echo "=============================================="
echo "✅ COMPLETE!"
echo "=============================================="
echo "Frontend: $FRONTEND_URL"
echo "Backend:  $BACKEND_URL"
echo ""
echo "Check status: gh run list --limit 3"
