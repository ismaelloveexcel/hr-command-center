# Azure Deployment Guide

This guide explains how to deploy the UAE HR Portal to Azure.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Azure Cloud                          │
│                                                             │
│  ┌─────────────────────┐    ┌─────────────────────────────┐│
│  │  Azure Static Web   │    │    Azure App Service        ││
│  │       Apps          │───▶│      (Python/Linux)         ││
│  │                     │    │                             ││
│  │  React Frontend     │    │  FastAPI Backend            ││
│  │  - Home Page        │    │  - /health                  ││
│  │  - Track Request    │    │  - /requests                ││
│  │  - HR Dashboard     │    │  - /hr/stats                ││
│  └─────────────────────┘    └──────────────┬──────────────┘│
│                                            │               │
│                              ┌─────────────▼──────────────┐│
│                              │   SQLite / PostgreSQL      ││
│                              │      (Database)            ││
│                              └────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

## Prerequisites

1. Azure account with active subscription
2. GitHub repository with this code
3. Azure CLI installed locally (optional, for manual setup)

## Step 1: Create Azure Resources

### Option A: Azure Portal (Recommended for beginners)

#### Backend - App Service

1. Go to [Azure Portal](https://portal.azure.com)
2. Click **Create a resource** → **Web App**
3. Configure:
   - **Subscription**: Your subscription
   - **Resource Group**: Create new → `hr-portal-rg`
   - **Name**: `hr-portal-api` (must be globally unique)
   - **Publish**: Code
   - **Runtime stack**: Python 3.11
   - **Operating System**: Linux
   - **Region**: Choose nearest (e.g., UAE North)
   - **Pricing Plan**: B1 (Basic) or higher
4. Click **Review + create** → **Create**
5. After creation, go to the App Service
6. **Configuration** → **General settings**:
   - Startup Command: `bash startup.sh`
7. **Configuration** → **Application settings**, add:
  - `DATABASE_URL`: `sqlite:///./hr_portal.db`
  - `CORS_ORIGINS`: Your frontend URL
  - `HR_API_KEY`: Generate a long random string (store securely and share only with HR staff)

#### Frontend - Static Web Apps

1. Go to [Azure Portal](https://portal.azure.com)
2. Click **Create a resource** → **Static Web App**
3. Configure:
   - **Subscription**: Your subscription
   - **Resource Group**: `hr-portal-rg`
   - **Name**: `hr-portal-web`
   - **Hosting plan**: Free
   - **Region**: Choose nearest
   - **Source**: GitHub
   - **Organization**: Your GitHub org
   - **Repository**: hr-command-center
   - **Branch**: main
   - **Build Presets**: React
   - **App location**: `/frontend`
   - **Output location**: `build`
4. Click **Review + create** → **Create**

### Option B: Azure CLI (For automation)

```bash
# Login to Azure
az login

# Create resource group
az group create --name hr-portal-rg --location uaenorth

# Create App Service Plan
az appservice plan create \
  --name hr-portal-plan \
  --resource-group hr-portal-rg \
  --sku B1 \
  --is-linux

# Create Backend Web App
az webapp create \
  --name hr-portal-api \
  --resource-group hr-portal-rg \
  --plan hr-portal-plan \
  --runtime "PYTHON:3.11"

# Configure startup command
az webapp config set \
  --name hr-portal-api \
  --resource-group hr-portal-rg \
  --startup-file "bash startup.sh"

# Set environment variables
az webapp config appsettings set \
  --name hr-portal-api \
  --resource-group hr-portal-rg \
  --settings \
    DATABASE_URL="sqlite:///./hr_portal.db" \
    CORS_ORIGINS="https://hr-portal-web.azurestaticapps.net"

# Create Static Web App (requires GitHub connection)
az staticwebapp create \
  --name hr-portal-web \
  --resource-group hr-portal-rg \
  --source https://github.com/YOUR_ORG/hr-command-center \
  --branch main \
  --app-location "/frontend" \
  --output-location "build" \
  --login-with-github
```

## Step 2: Configure GitHub Secrets

Go to your GitHub repository → **Settings** → **Secrets and variables** → **Actions**

Add these secrets:

| Secret Name | How to Get It |
|-------------|---------------|
| `AZURE_BACKEND_APP_NAME` | Your App Service name (e.g., `hr-portal-api`) |
| `AZURE_BACKEND_PUBLISH_PROFILE` | App Service → Deployment Center → Download publish profile |
| `AZURE_STATIC_WEB_APPS_API_TOKEN` | Static Web App → Overview → Manage deployment token |
| `REACT_APP_API_URL` | Your backend URL (e.g., `https://hr-portal-api.azurewebsites.net`) |

### Getting the Publish Profile

1. Go to your App Service in Azure Portal
2. Click **Deployment Center** in the left menu
3. Click **Manage publish profile** → **Download**
4. Open the downloaded file and copy the entire content
5. Paste as the value for `AZURE_BACKEND_PUBLISH_PROFILE` secret

### Getting Static Web Apps Token

1. Go to your Static Web App in Azure Portal
2. Click **Overview**
3. Click **Manage deployment token**
4. Copy the token
5. Paste as the value for `AZURE_STATIC_WEB_APPS_API_TOKEN` secret

## Step 3: Deploy

### Automatic Deployment

Push to the `main` branch and GitHub Actions will automatically deploy:

```bash
git push origin main
```

### Manual Deployment

Go to GitHub → **Actions** → Select workflow → **Run workflow**

## Step 4: Verify Deployment

### Backend

```bash
# Check health endpoint
curl https://hr-portal-api.azurewebsites.net/health

# Expected response:
# {"status":"healthy","service":"UAE HR Portal API"}
```

### Frontend

Open `https://hr-portal-web.azurestaticapps.net` in your browser.

## Environment Variables Reference

### Backend (.env / App Settings)

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `sqlite:///./hr_portal.db` |
| `CORS_ORIGINS` | Allowed frontend URLs | `https://hr-portal-web.azurestaticapps.net` |
| `DEBUG` | Enable debug mode | `false` |

### Frontend (Build-time)

| Variable | Description | Example |
|----------|-------------|---------|
| `REACT_APP_API_URL` | Backend API URL | `https://hr-portal-api.azurewebsites.net` |

## Production Considerations

### Database

For production, consider Azure Database for PostgreSQL:

```bash
# Create PostgreSQL server
az postgres flexible-server create \
  --name hr-portal-db \
  --resource-group hr-portal-rg \
  --admin-user hradmin \
  --admin-password <secure-password> \
  --sku-name Standard_B1ms

# Update DATABASE_URL to:
# postgresql://hradmin:<password>@hr-portal-db.postgres.database.azure.com:5432/hrportal
```

### Custom Domain

1. Go to Static Web App → **Custom domains**
2. Add your domain and configure DNS

### SSL/TLS

Azure provides free SSL for both App Service and Static Web Apps.

## Troubleshooting

### Backend not starting

1. Check App Service logs: **Monitoring** → **Log stream**
2. Verify startup command is set correctly
3. Check Application settings are configured

### Frontend API calls failing

1. Check CORS_ORIGINS includes the frontend URL
2. Verify REACT_APP_API_URL is set correctly during build
3. Check browser console for errors

### Deployment failing

1. Check GitHub Actions logs
2. Verify all secrets are set correctly
3. Ensure publish profile is not expired

## Cost Estimate

| Resource | SKU | Estimated Monthly Cost |
|----------|-----|------------------------|
| App Service | B1 | ~$13 USD |
| Static Web App | Free | $0 |
| PostgreSQL (optional) | B1ms | ~$15 USD |
| **Total** | | **~$13-28 USD** |

Free tier options available for development/testing.
