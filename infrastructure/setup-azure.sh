#!/bin/bash

# ==============================================
# UAE HR Portal - Fully Automated Azure Setup
# ==============================================
# This script:
# 1. Creates all Azure resources
# 2. Configures GitHub secrets automatically
# 3. Triggers deployment
#
# Prerequisites:
# - Azure CLI installed and logged in (az login)
# - GitHub CLI installed and logged in (gh auth login)
# ==============================================

set -e

# Configuration
RESOURCE_GROUP="hr-portal-rg"
LOCATION="eastus"
APP_NAME_PREFIX="hrportal"
UNIQUE_SUFFIX=$(date +%s | tail -c 6)

BACKEND_NAME="${APP_NAME_PREFIX}-api-${UNIQUE_SUFFIX}"
PLAN_NAME="${APP_NAME_PREFIX}-plan"
STATIC_WEB_APP_NAME="${APP_NAME_PREFIX}-web-${UNIQUE_SUFFIX}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "=============================================="
echo "  UAE HR Portal - Automated Azure Setup"
echo "=============================================="
echo -e "${NC}"

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

if ! command -v az &> /dev/null; then
    echo -e "${RED}Error: Azure CLI not installed${NC}"
    echo "Install from: https://docs.microsoft.com/cli/azure/install-azure-cli"
    exit 1
fi

if ! command -v gh &> /dev/null; then
    echo -e "${RED}Error: GitHub CLI not installed${NC}"
    echo "Install from: https://cli.github.com/"
    exit 1
fi

# Check Azure login
if ! az account show &> /dev/null; then
    echo -e "${YELLOW}Not logged into Azure. Logging in...${NC}"
    az login
fi

# Check GitHub login
if ! gh auth status &> /dev/null; then
    echo -e "${YELLOW}Not logged into GitHub. Logging in...${NC}"
    gh auth login
fi

AZURE_ACCOUNT=$(az account show --query name -o tsv)
echo -e "${GREEN}✓ Azure account: ${AZURE_ACCOUNT}${NC}"

GH_USER=$(gh api user --jq '.login')
echo -e "${GREEN}✓ GitHub user: ${GH_USER}${NC}"

# Get repository info
REPO=$(gh repo view --json nameWithOwner -q '.nameWithOwner' 2>/dev/null || echo "")
if [ -z "$REPO" ]; then
    echo -e "${RED}Error: Not in a GitHub repository${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Repository: ${REPO}${NC}"

echo ""
echo -e "${BLUE}Configuration:${NC}"
echo "  Resource Group: $RESOURCE_GROUP"
echo "  Location: $LOCATION"
echo "  Backend App: $BACKEND_NAME"
echo "  Static Web App: $STATIC_WEB_APP_NAME"
echo ""

read -p "Proceed with deployment? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

# ==============================================
# Step 1: Create Azure Resources
# ==============================================

echo ""
echo -e "${BLUE}[1/6] Creating resource group...${NC}"
az group create \
    --name "$RESOURCE_GROUP" \
    --location "$LOCATION" \
    --output none
echo -e "${GREEN}✓ Resource group created${NC}"

echo ""
echo -e "${BLUE}[2/6] Creating App Service Plan...${NC}"
az appservice plan create \
    --name "$PLAN_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --sku B1 \
    --is-linux \
    --output none
echo -e "${GREEN}✓ App Service Plan created${NC}"

echo ""
echo -e "${BLUE}[3/6] Creating Backend Web App...${NC}"
az webapp create \
    --name "$BACKEND_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --plan "$PLAN_NAME" \
    --runtime "PYTHON:3.11" \
    --output none

# Configure startup command
az webapp config set \
    --name "$BACKEND_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --startup-file "bash startup.sh" \
    --output none

BACKEND_URL="https://${BACKEND_NAME}.azurewebsites.net"
echo -e "${GREEN}✓ Backend created: ${BACKEND_URL}${NC}"

echo ""
echo -e "${BLUE}[4/6] Creating Static Web App...${NC}"
STATIC_WEB_APP_RESULT=$(az staticwebapp create \
    --name "$STATIC_WEB_APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --source "https://github.com/${REPO}" \
    --branch "main" \
    --app-location "/frontend" \
    --output-location "build" \
    --login-with-github \
    --output json 2>/dev/null || echo "MANUAL")

if [ "$STATIC_WEB_APP_RESULT" == "MANUAL" ]; then
    echo -e "${YELLOW}Note: Static Web App requires manual GitHub connection${NC}"
    echo "Creating without GitHub connection..."
    az staticwebapp create \
        --name "$STATIC_WEB_APP_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --sku Free \
        --output none
fi

FRONTEND_URL=$(az staticwebapp show \
    --name "$STATIC_WEB_APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --query "defaultHostname" -o tsv)
FRONTEND_URL="https://${FRONTEND_URL}"
echo -e "${GREEN}✓ Static Web App created: ${FRONTEND_URL}${NC}"

# Configure CORS
echo ""
echo -e "${BLUE}[5/6] Configuring backend settings...${NC}"
az webapp config appsettings set \
    --name "$BACKEND_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --settings \
        DATABASE_URL="sqlite:///./hr_portal.db" \
        CORS_ORIGINS="$FRONTEND_URL" \
    --output none
echo -e "${GREEN}✓ Backend configured${NC}"

# ==============================================
# Step 2: Get Secrets and Configure GitHub
# ==============================================

echo ""
echo -e "${BLUE}[6/6] Configuring GitHub secrets...${NC}"

# Get publish profile
PUBLISH_PROFILE=$(az webapp deployment list-publishing-profiles \
    --name "$BACKEND_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --xml)

# Get Static Web App token
SWA_TOKEN=$(az staticwebapp secrets list \
    --name "$STATIC_WEB_APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --query "properties.apiKey" -o tsv)

# Set GitHub secrets
echo "  Setting AZURE_BACKEND_APP_NAME..."
gh secret set AZURE_BACKEND_APP_NAME --body "$BACKEND_NAME"

echo "  Setting AZURE_BACKEND_PUBLISH_PROFILE..."
gh secret set AZURE_BACKEND_PUBLISH_PROFILE --body "$PUBLISH_PROFILE"

echo "  Setting AZURE_STATIC_WEB_APPS_API_TOKEN..."
gh secret set AZURE_STATIC_WEB_APPS_API_TOKEN --body "$SWA_TOKEN"

echo "  Setting REACT_APP_API_URL..."
gh secret set REACT_APP_API_URL --body "$BACKEND_URL"

echo -e "${GREEN}✓ GitHub secrets configured${NC}"

# ==============================================
# Summary
# ==============================================

echo ""
echo -e "${GREEN}=============================================="
echo "  Setup Complete!"
echo "==============================================${NC}"
echo ""
echo -e "${BLUE}Azure Resources:${NC}"
echo "  Backend:  $BACKEND_URL"
echo "  Frontend: $FRONTEND_URL"
echo ""
echo -e "${BLUE}GitHub Secrets Configured:${NC}"
echo "  ✓ AZURE_BACKEND_APP_NAME"
echo "  ✓ AZURE_BACKEND_PUBLISH_PROFILE"
echo "  ✓ AZURE_STATIC_WEB_APPS_API_TOKEN"
echo "  ✓ REACT_APP_API_URL"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo "  Deployment will trigger automatically on push to main."
echo "  Or manually trigger: gh workflow run backend-deploy.yml"
echo ""
echo -e "${YELLOW}Triggering initial deployment...${NC}"

# Trigger workflows
gh workflow run backend-deploy.yml 2>/dev/null || echo "Backend workflow will run on next push"
gh workflow run frontend-deploy.yml 2>/dev/null || echo "Frontend workflow will run on next push"

echo ""
echo -e "${GREEN}Done! Your app will be live in ~5 minutes.${NC}"
echo ""
echo "Monitor deployment:"
echo "  gh run list --workflow=backend-deploy.yml"
echo "  gh run list --workflow=frontend-deploy.yml"
