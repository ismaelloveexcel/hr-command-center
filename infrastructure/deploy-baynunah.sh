#!/bin/bash
# FULLY AUTOMATED DEPLOYMENT

set -e

echo "🚀 UAE HR Portal - Automated Deployment"
echo ""

RG="baynunah-hr-portal-rg"
PLAN="baynunah-plan"
BACKEND="baynunah-hr-api"
SWA="hrportal-frontend-new"
FRONTEND_URL="https://proud-forest-051662503.4.azurestaticapps.net"

# Step 1: Ensure resource group exists
echo "[1/8] Checking resource group..."
az group show --name $RG -o none 2>/dev/null || az group create --name $RG --location eastus -o none
echo "✓ Resource group ready"

# Step 2: Create app service plan
echo "[2/8] Creating app service plan..."
az appservice plan show --name $PLAN --resource-group $RG -o none 2>/dev/null || \
az appservice plan create --name $PLAN --resource-group $RG --sku F1 --is-linux -o none
echo "✓ App service plan ready"

# Step 3: Create web app
echo "[3/8] Creating web app..."
az webapp show --name $BACKEND --resource-group $RG -o none 2>/dev/null || \
az webapp create --name $BACKEND --resource-group $RG --plan $PLAN --runtime "PYTHON:3.11" -o none
echo "✓ Web app ready"

# Step 4: Configure web app
echo "[4/8] Configuring web app..."
az webapp config set --name $BACKEND --resource-group $RG \
  --startup-file "gunicorn main:app --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000" -o none
az webapp config appsettings set --name $BACKEND --resource-group $RG \
  --settings DATABASE_URL="sqlite:///./hr_portal.db" CORS_ORIGINS="$FRONTEND_URL" -o none
echo "✓ Configuration complete"

# Step 5: Get fresh publish profile
echo "[5/8] Getting publish profile..."
PROFILE=$(az webapp deployment list-publishing-profiles --name $BACKEND --resource-group $RG --xml)
if [ -z "$PROFILE" ]; then
  echo "❌ Failed to get publish profile"
  exit 1
fi
echo "✓ Got publish profile"

# Step 6: Set GitHub secrets
echo "[6/8] Setting GitHub secrets..."
echo "$PROFILE" | gh secret set AZURE_BACKEND_PUBLISH_PROFILE --repo ismaelloveexcel/hr-command-center
gh secret set AZURE_BACKEND_APP_NAME --body "$BACKEND" --repo ismaelloveexcel/hr-command-center
gh secret set REACT_APP_API_URL --body "https://${BACKEND}.azurewebsites.net" --repo ismaelloveexcel/hr-command-center
echo "✓ Backend secrets set"

# Step 7: Set SWA token
echo "[7/8] Setting frontend secret..."
TOKEN=$(az staticwebapp secrets list --name $SWA --resource-group $RG --query "properties.apiKey" -o tsv)
echo "$TOKEN" | gh secret set AZURE_STATIC_WEB_APPS_API_TOKEN --repo ismaelloveexcel/hr-command-center
echo "✓ Frontend secret set"

# Step 8: Trigger deployment
echo "[8/8] Triggering deployment..."
gh workflow run backend-deploy.yml --repo ismaelloveexcel/hr-command-center
sleep 2
gh workflow run frontend-deploy.yml --repo ismaelloveexcel/hr-command-center

echo ""
echo "=============================================="
echo "✅ DEPLOYMENT TRIGGERED!"
echo "=============================================="
echo ""
echo "Frontend: $FRONTEND_URL"
echo "Backend:  https://${BACKEND}.azurewebsites.net"
echo ""
echo "Checking status in 10 seconds..."
sleep 10
gh run list --limit 2 --repo ismaelloveexcel/hr-command-center
