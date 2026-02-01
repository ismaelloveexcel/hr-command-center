# 🎯 Quick Start: Complete Azure Deployment

> **For Non-Technical Users**: This guide walks you through deploying the HR Portal to Azure in under 15 minutes.

## ✅ Prerequisites (One-Time Setup)

### 1. Azure Setup

You need an **Azure subscription**. If you don't have one:
- Go to [azure.com](https://azure.com)
- Click "Start free" or "Sign in"

### 2. GitHub Secrets Setup

Ask your Azure administrator to provide these three values:

1. `AZURE_CLIENT_ID`
2. `AZURE_TENANT_ID`
3. `AZURE_SUBSCRIPTION_ID`

Then add them to GitHub:
1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each of the three secrets above

> **Don't have these?** See the [OIDC Setup Guide](#setting-up-oidc-authentication) below.

## 🚀 Deploy in 3 Steps

### Step 1: Go to Actions Tab

1. Open your repository on GitHub
2. Click the **"Actions"** tab at the top
3. Find **"Complete Azure Setup & Deploy"** in the left sidebar
4. Click on it

### Step 2: Run the Workflow

1. Click the **"Run workflow"** dropdown button (top right)
2. Leave all settings at their defaults (or customize if needed):
   - **resource_group**: `hr-portal-rg` ✅
   - **location**: `eastus` ✅
   - **base_name**: `hrportal` ✅
   - **app_service_sku**: `B1` ✅
3. Click the green **"Run workflow"** button

### Step 3: Wait and Get Your URLs

1. Wait 7-12 minutes for deployment to complete
2. Click on the running workflow to see progress
3. Once complete, scroll to the bottom to see your URLs:
   - **Frontend URL**: Where your app is running
   - **Backend URL**: Your API endpoint

**That's it!** 🎉 Your app is now live in Azure!

## 📊 What Happens During Deployment?

The workflow automatically:

1. ✅ Creates all Azure resources (Resource Group, Key Vault, App Service, Static Web App)
2. ✅ Deploys your backend API (FastAPI)
3. ✅ Deploys your frontend app (React)
4. ✅ Configures everything to work together
5. ✅ Runs health checks
6. ✅ Gives you the URLs to access your app

## 🎛️ Customization Options

### Basic Settings

| Setting | What It Does | Recommendation |
|---------|--------------|----------------|
| **resource_group** | Groups all your Azure resources | Use default `hr-portal-rg` |
| **location** | Azure region (affects performance) | Use `eastus` (reliable and fast) |
| **base_name** | Prefix for all resource names | Use `hrportal` (lowercase only) |
| **app_service_sku** | Server power/cost | Use `B1` for testing, `S1` for production |

### Advanced Settings

| Setting | What It Does | When to Use |
|---------|--------------|-------------|
| **keyvault_name** | Custom Key Vault name | Leave empty (auto-generated) |
| **skip_backend_deploy** | Don't deploy backend | When testing infrastructure only |
| **skip_frontend_deploy** | Don't deploy frontend | When testing infrastructure only |

## 🆘 Troubleshooting

### Problem: "Workflow failed at Azure Login"
**Cause**: GitHub secrets not configured correctly  
**Fix**: 
1. Go to Settings → Secrets and variables → Actions
2. Verify all three secrets exist:
   - `AZURE_CLIENT_ID`
   - `AZURE_TENANT_ID`
   - `AZURE_SUBSCRIPTION_ID`

### Problem: "Resource already exists"
**Cause**: You've run this before  
**Fix**: This is normal! The workflow will reuse existing resources. No action needed.

### Problem: "Backend health check failed"
**Cause**: Backend is still starting up  
**Fix**: 
1. Wait 2-3 more minutes
2. Visit `https://YOUR-APP.azurewebsites.net/health` manually
3. If still not working, check logs in Azure Portal

### Problem: "Frontend shows blank page"
**Cause**: Frontend hasn't deployed yet  
**Fix**: 
1. Wait 5 more minutes
2. Hard refresh your browser (Ctrl+Shift+R or Cmd+Shift+R)
3. Clear browser cache

## 💰 Cost Estimate

Running this deployment will cost approximately:

- **Development/Testing** (B1 tier): ~$13/month
- **Production** (S1 tier): ~$56/month

> You can delete everything anytime by deleting the Resource Group in Azure Portal.

## 🔄 Updating Your App

After initial deployment, to update:

1. **Push changes to main branch** → Triggers automatic deployment
2. **Or run the workflow again** → Redeploys everything

## 🗑️ Deleting Everything

To completely remove the deployment:

### Option 1: Azure Portal (Easy)
1. Go to [portal.azure.com](https://portal.azure.com)
2. Search for your Resource Group (e.g., `hr-portal-rg`)
3. Click "Delete resource group"
4. Type the name to confirm
5. Click "Delete"

### Option 2: Azure CLI
```bash
az group delete --name hr-portal-rg --yes
```

> **Note**: Deleting the Resource Group removes all resources (App Service, Static Web App, Key Vault, etc.)

## 📖 Next Steps

After deployment:

1. ✅ **Visit Your App**: Use the Frontend URL from the deployment summary
2. ✅ **Test the API**: Visit Backend URL + `/docs` (e.g., `https://your-app.azurewebsites.net/docs`)
3. ✅ **Monitor Logs**: Go to Azure Portal → Your App Service → Log stream
4. ✅ **Set Up Monitoring**: Enable Application Insights for detailed analytics

## 🤔 FAQ

### Q: Do I need to install anything on my computer?
**A**: No! Everything runs in GitHub Actions. You just click buttons on GitHub.

### Q: How long does deployment take?
**A**: 7-12 minutes on average.

### Q: Can I deploy to multiple environments (dev, staging, prod)?
**A**: Yes! Run the workflow multiple times with different `resource_group` names.

### Q: What if I make a mistake?
**A**: No problem! You can delete the Resource Group and start over. Or just run the workflow again.

### Q: Is this production-ready?
**A**: Yes! The workflow includes:
- ✅ HTTPS enforcement
- ✅ Security headers
- ✅ CORS configuration
- ✅ Health checks
- ✅ Secrets management

### Q: Can I customize the infrastructure?
**A**: Yes! Edit `infrastructure/main.bicep` and re-run the workflow.

## 📞 Getting Help

If you're stuck:

1. **Check the workflow logs**: Click on the failed step to see error details
2. **Review troubleshooting section**: See common issues above
3. **Check Azure Portal**: See if resources were created
4. **Ask for help**: Include:
   - Link to the workflow run
   - Error message
   - What you were trying to do

---

## 🔐 Appendix: Setting Up OIDC Authentication

If you need to set up Azure OIDC authentication from scratch:

### Step 1: Create Azure Service Principal

```bash
# Login to Azure
az login

# Get your subscription ID
az account show --query id -o tsv

# Create service principal
az ad sp create-for-rbac \
  --name "github-actions-hr-portal" \
  --role contributor \
  --scopes /subscriptions/YOUR_SUBSCRIPTION_ID
```

This will output:
```json
{
  "clientId": "xxx",
  "clientSecret": "xxx",
  "subscriptionId": "xxx",
  "tenantId": "xxx"
}
```

### Step 2: Configure Federated Credentials

```bash
# Replace with your GitHub repo
REPO_OWNER="your-username"
REPO_NAME="hr-command-center"
APP_ID="xxx"  # clientId from previous step

# Create federated credential
az ad app federated-credential create \
  --id $APP_ID \
  --parameters '{
    "name": "github-actions-main",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:'$REPO_OWNER'/'$REPO_NAME':ref:refs/heads/main",
    "audiences": ["api://AzureADTokenExchange"]
  }'
```

### Step 3: Add Secrets to GitHub

1. Go to your repo → Settings → Secrets and variables → Actions
2. Add these secrets:
   - `AZURE_CLIENT_ID`: The `clientId` from Step 1
   - `AZURE_TENANT_ID`: The `tenantId` from Step 1
   - `AZURE_SUBSCRIPTION_ID`: The `subscriptionId` from Step 1

### Step 4: Test the Workflow

Run the "Complete Azure Setup & Deploy" workflow to verify everything works!

---

**Need more details?** See [AZURE_COMPLETE_DEPLOYMENT.md](./AZURE_COMPLETE_DEPLOYMENT.md) for comprehensive documentation.
