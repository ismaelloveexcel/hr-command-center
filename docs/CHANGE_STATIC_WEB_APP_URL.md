# How to Change Azure Static Web App URL

This guide explains how to change your Azure Static Web App URL from the auto-generated name (like `blue-rock-0fc588010.4.azurestaticapps.net`) to something more appropriate for your HR Portal.

## Understanding the URL Structure

Azure Static Web App URLs follow this format:
```
https://{app-name}.{region}.azurestaticapps.net
```

The `{app-name}` part is either:
- **Auto-generated** (like `blue-rock-0fc588010`) - assigned by Azure when you create the app via GitHub integration
- **Custom name** - you choose it when creating the app manually

## Option 1: Add a Custom Domain (Recommended)

You can keep your existing Static Web App and add a professional custom domain.

### Steps:

1. **Get a custom domain** (e.g., `hr-portal.yourcompany.com`)
   - Purchase from any domain registrar (Namecheap, GoDaddy, Google Domains, etc.)

2. **Configure in Azure Portal:**
   1. Go to [Azure Portal](https://portal.azure.com)
   2. Navigate to your Static Web App (shown as the name you see in the Azure Portal, e.g., `blue-rock-0fc588010`)
   3. In the left menu, click **Custom domains**
   4. Click **+ Add**
   5. Choose one of:
      - **Custom domain on other DNS** - Use your own domain
      - **Azure DNS Zone** - Manage DNS in Azure

3. **Update DNS records:**
   - Add a CNAME record pointing to your current URL (e.g., `blue-rock-0fc588010.4.azurestaticapps.net`)
   - Azure will validate the domain

4. **SSL certificate:**
   - Azure automatically provides free SSL/TLS certificates

**Result:** Your app is accessible at `https://hr-portal.yourcompany.com`

---

## Option 2: Recreate with a Better Name (Free)

Delete the current Static Web App and create a new one with a meaningful name.

### Step 1: Delete Current Static Web App

1. Go to [Azure Portal](https://portal.azure.com)
2. Search for **Static Web Apps**
3. Find and select your app (e.g., `blue-rock-0fc588010`)
4. Click **Delete** in the top toolbar
5. Type the app name to confirm deletion

### Step 2: Create New Static Web App with Custom Name

1. In Azure Portal, search for **Static Web Apps**
2. Click **+ Create**
3. Fill in:
   - **Subscription**: Your subscription
   - **Resource Group**: `hr-portal-rg`
   - **Name**: `uae-hr-portal-web` (⚠️ This must be **globally unique** across all Azure Static Web Apps and becomes part of your URL!)
   - **Plan type**: Free
   - **Region**: Choose your preferred region
   - **Source**: GitHub
4. Authorize GitHub and select:
   - **Organization**: Your GitHub username
   - **Repository**: `hr-command-center`
   - **Branch**: `main`
5. Build Details:
   - **Build Presets**: React
   - **App location**: `/frontend`
   - **Api location**: (leave empty)
   - **Output location**: `build`
6. Click **Review + create** → **Create**

### Step 3: Update GitHub Secrets

After creating the new Static Web App, you need to update the deployment token:

1. In Azure Portal, go to your new Static Web App
2. Click **Manage deployment token** in the Overview page
3. Copy the new token
4. Go to GitHub → Repository Settings → Secrets and variables → Actions
5. Update the `AZURE_STATIC_WEB_APPS_API_TOKEN` secret with the new token

### Step 4: Update Backend CORS Settings

Update the CORS settings in your Azure App Service:

1. Go to your App Service in Azure Portal
2. Navigate to **Configuration** → **Application settings**
3. Update `CORS_ORIGINS` with your new Static Web App URL:
   ```
   https://uae-hr-portal-web.{region}.azurestaticapps.net
   ```
   (Replace `{region}` with your actual region, e.g., `4`, `eastus2`, etc.)
4. Click **Save**

### Step 5: Trigger Deployment

```bash
# Go to GitHub Actions and trigger the frontend-deploy workflow
# OR push a small change to main
```

**Result:** Your app is accessible at `https://uae-hr-portal-web.{region}.azurestaticapps.net`

---

## Option 3: Use Azure CLI (Advanced)

For advanced users who prefer command-line tools:

### Delete and Recreate:

```bash
# Login to Azure
az login

# Set variables
RESOURCE_GROUP="hr-portal-rg"
OLD_APP_NAME="blue-rock-0fc588010"
NEW_APP_NAME="uae-hr-portal-web"
LOCATION="eastus"

# Delete old Static Web App
az staticwebapp delete \
  --name $OLD_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --yes

# Create new Static Web App
az staticwebapp create \
  --name $NEW_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --source https://github.com/ismaelloveexcel/hr-command-center \
  --branch main \
  --app-location "/frontend" \
  --output-location "build" \
  --login-with-github

# Get the new deployment token
az staticwebapp secrets list \
  --name $NEW_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query "properties.apiKey" -o tsv
```

---

## Recommended Names for HR Portal

When recreating, consider professional names like:
- `uae-hr-portal-web`
- `hr-command-center`
- `hr-portal-app`
- `employee-portal`
- `baynunah-hr` (if company-specific)

**Note:** The name must be:
- Globally unique across all Azure Static Web Apps
- 2-60 characters
- Contain only lowercase letters, numbers, and hyphens
- Start with a letter

---

## Summary

| Option | Effort | Cost | Result |
|--------|--------|------|--------|
| Add Custom Domain | Medium | Domain cost (~$10-15/year) | Professional URL like `hr.company.com` |
| Recreate with New Name | Low | Free | Better URL like `uae-hr-portal-web.azurestaticapps.net` |
| Azure CLI | Medium | Free | Automated recreation |

**Recommendation:** If you have a company domain, use **Option 1**. Otherwise, use **Option 2** to get a meaningful Azure URL.

---

## After Making Changes

Remember to:
1. ✅ Update GitHub secrets with new deployment token (if recreated)
2. ✅ Update CORS settings in backend App Service
3. ✅ Update any documentation or links referencing the old URL
4. ✅ Test the new deployment
