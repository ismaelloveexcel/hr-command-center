#!/bin/bash

# UAE HR Portal - Azure Deployment Script
# Usage: ./deploy.sh [resource-group-name] [location]

set -e

RESOURCE_GROUP=${1:-"hr-portal-rg"}
LOCATION=${2:-"eastus"}

echo "=========================================="
echo "UAE HR Portal - Azure Deployment"
echo "=========================================="
echo "Resource Group: $RESOURCE_GROUP"
echo "Location: $LOCATION"
echo ""

# Check if logged in to Azure
if ! az account show > /dev/null 2>&1; then
    echo "Please login to Azure first:"
    echo "  az login"
    exit 1
fi

# Create resource group
echo "Creating resource group..."
az group create \
    --name "$RESOURCE_GROUP" \
    --location "$LOCATION" \
    --output none

# Deploy infrastructure
echo "Deploying infrastructure..."
DEPLOYMENT_OUTPUT=$(az deployment group create \
    --resource-group "$RESOURCE_GROUP" \
    --template-file main.bicep \
    --query "properties.outputs" \
    --output json)

# Extract outputs
BACKEND_NAME=$(echo $DEPLOYMENT_OUTPUT | jq -r '.backendAppName.value')
BACKEND_URL=$(echo $DEPLOYMENT_OUTPUT | jq -r '.backendUrl.value')
STATIC_WEB_APP_NAME=$(echo $DEPLOYMENT_OUTPUT | jq -r '.staticWebAppName.value')
STATIC_WEB_APP_URL=$(echo $DEPLOYMENT_OUTPUT | jq -r '.staticWebAppUrl.value')

echo ""
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo ""
echo "Backend App Name: $BACKEND_NAME"
echo "Backend URL: $BACKEND_URL"
echo ""
echo "Static Web App Name: $STATIC_WEB_APP_NAME"
echo "Static Web App URL: $STATIC_WEB_APP_URL"
echo ""
echo "=========================================="
echo "GitHub Secrets to Configure:"
echo "=========================================="
echo ""
echo "1. AZURE_BACKEND_APP_NAME = $BACKEND_NAME"
echo ""
echo "2. AZURE_BACKEND_PUBLISH_PROFILE = (run command below)"
echo "   az webapp deployment list-publishing-profiles --name $BACKEND_NAME --resource-group $RESOURCE_GROUP --xml"
echo ""
echo "3. AZURE_STATIC_WEB_APPS_API_TOKEN = (run command below)"
echo "   az staticwebapp secrets list --name $STATIC_WEB_APP_NAME --resource-group $RESOURCE_GROUP --query 'properties.apiKey' -o tsv"
echo ""
echo "4. REACT_APP_API_URL = $BACKEND_URL"
echo ""
echo "=========================================="
echo "After configuring secrets, push to main:"
echo "  git push origin main"
echo "=========================================="
