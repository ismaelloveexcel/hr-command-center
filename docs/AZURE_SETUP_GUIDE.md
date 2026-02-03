# Azure Setup Guide - Step by Step

Complete guide to set up Azure subscription and configure GitHub secrets for automated deployment.

## Part 1: Azure Subscription

### Option A: Free Azure Account (Recommended for testing)

1. Go to [Azure Free Account](https://azure.microsoft.com/free/)
2. Click **Start free**
3. Sign in with Microsoft account (or create one)
4. Provide:
   - Phone number for verification
   - Credit card (for identity verification, won't be charged)
5. You get:
   - **$200 credit** for 30 days
   - **12 months free** of popular services
   - **Always free** services (25+ products)

### Option B: Pay-As-You-Go

1. Go to [Azure Portal](https://portal.azure.com)
2. Click **Subscriptions** → **Add**
3. Select **Pay-As-You-Go**
4. Complete billing setup

### Option C: Azure for Students (No credit card)

1. Go to [Azure for Students](https://azure.microsoft.com/free/students/)
2. Verify with school email
3. Get **$100 credit** without credit card

---

## Part 2: Create Azure Resources

### Method 1: Azure Portal (Click-by-click)

#### Step 2.1: Create Resource Group

1. Go to [Azure Portal](https://portal.azure.com)
2. Search for **Resource groups** in the top search bar
3. Click **+ Create**
4. Fill in:
   - **Subscription**: Select your subscription
   - **Resource group**: `hr-portal-rg`
   - **Region**: `East US` (or nearest to you)
5. Click **Review + create** → **Create**

#### Step 2.2: Create Backend (App Service)

1. Search for **App Services** in the top search bar
2. Click **+ Create** → **Web App**
3. Fill in **Basics** tab:
   - **Subscription**: Your subscription
   - **Resource Group**: `hr-portal-rg`
   - **Name**: `uae-hr-portal-api` (must be globally unique)
   - **Publish**: Code
   - **Runtime stack**: Python 3.11
   - **Operating System**: Linux
   - **Region**: Same as resource group
4. Fill in **Pricing** tab:
   - **Pricing Plan**: Create new → `hr-portal-plan`
   - **Sku and size**: B1 (Basic) - click "Change size" if needed
5. Click **Review + create** → **Create**
6. Wait for deployment to complete (~2 minutes)

#### Step 2.3: Configure Backend App Service

1. Go to your new App Service (`uae-hr-portal-api`)
2. In left menu, click **Configuration**
3. Click **General settings** tab:
   - **Startup Command**: `bash startup.sh`
   - Click **Save** at top
4. Click **Application settings** tab:
   - Click **+ New application setting** for each:
   
   | Name | Value |
   |------|-------|
   | `DATABASE_URL` | `sqlite:///./hr_portal.db` |
   | `CORS_ORIGINS` | `https://YOUR-FRONTEND-URL.azurestaticapps.net` |
   
5. Click **Save** at top

#### Step 2.4: Create Frontend (Static Web App)

1. Search for **Static Web Apps** in the top search bar
2. Click **+ Create**
3. Fill in:
   - **Subscription**: Your subscription
   - **Resource Group**: `hr-portal-rg`
   - **Name**: `uae-hr-portal` ⚠️ **IMPORTANT: Choose a meaningful name!**
     > This name becomes part of your URL (e.g., `uae-hr-portal.{region}.azurestaticapps.net`).
     > Avoid auto-generated names like `blue-rock-xxx` which are not professional.
     > See [CHANGE_STATIC_WEB_APP_URL.md](./CHANGE_STATIC_WEB_APP_URL.md) if you need to rename later.
   - **Plan type**: Free
   - **Region**: Same region
   - **Source**: GitHub
4. Click **Sign in with GitHub** and authorize
5. Select:
   - **Organization**: Your GitHub username
   - **Repository**: `hr-command-center`
   - **Branch**: `main`
6. Build Details:
   - **Build Presets**: React
   - **App location**: `/frontend`
   - **Api location**: (leave empty)
   - **Output location**: `build`
7. Click **Review + create** → **Create**

---

## Part 3: Get Secrets for GitHub

### Secret 1: AZURE_BACKEND_APP_NAME

This is simply the name of your App Service.

**Value**: `uae-hr-portal-api` (whatever you named it)

---

### Secret 2: AZURE_BACKEND_PUBLISH_PROFILE

This is an XML file containing deployment credentials.

**How to get it:**

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to your App Service (`uae-hr-portal-api`)
3. In the left menu, click **Deployment Center**
4. At the top, click **Manage publish profile**
5. Click **Download publish profile**
6. Open the downloaded `.PublishSettings` file with a text editor
7. **Copy the ENTIRE content** (it's XML, starts with `<publishData>`)

**The content looks like this:**
```xml
<publishData>
  <publishProfile profileName="uae-hr-portal-api - Web Deploy" ...>
    ...
  </publishProfile>
</publishData>
```

---

### Secret 3: AZURE_STATIC_WEB_APPS_API_TOKEN

This is the deployment token for Static Web Apps.

**How to get it:**

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to your Static Web App (`uae-hr-portal-web`)
3. In the **Overview** page, click **Manage deployment token**
4. Click **Copy** button next to the token
5. The token is a long string like: `a1b2c3d4e5f6...`

---

### Secret 4: REACT_APP_API_URL

This is your backend URL.

**How to get it:**

1. Go to your App Service in Azure Portal
2. In the **Overview** page, find **Default domain**
3. Copy the URL (e.g., `https://uae-hr-portal-api.azurewebsites.net`)

**Value**: `https://uae-hr-portal-api.azurewebsites.net`

---

## Part 4: Add Secrets to GitHub

1. Go to your GitHub repository
2. Click **Settings** tab
3. In left menu, click **Secrets and variables** → **Actions**
4. Click **New repository secret** for each:

| Secret Name | Value |
|-------------|-------|
| `AZURE_BACKEND_APP_NAME` | `uae-hr-portal-api` |
| `AZURE_BACKEND_PUBLISH_PROFILE` | (paste entire XML content) |
| `AZURE_STATIC_WEB_APPS_API_TOKEN` | (paste token string) |
| `REACT_APP_API_URL` | `https://uae-hr-portal-api.azurewebsites.net` |

### Screenshot Guide for Adding Secrets:

```
GitHub Repository
    └── Settings
        └── Secrets and variables
            └── Actions
                └── New repository secret
                    ├── Name: AZURE_BACKEND_APP_NAME
                    └── Secret: uae-hr-portal-api
                    └── [Add secret]
```

---

## Part 5: Update CORS After Frontend Deploys

After your first frontend deployment:

1. Go to Azure Portal → your Static Web App
2. Copy the URL from **Overview** (e.g., `https://xxx.azurestaticapps.net`)
3. Go to your App Service → **Configuration** → **Application settings**
4. Update `CORS_ORIGINS` with the Static Web App URL
5. Click **Save**

---

## Part 6: Trigger Deployment

### Option A: Push to main branch
```bash
git checkout main
git merge cursor/hr-portal-application-build-50ac
git push origin main
```

### Option B: Manual trigger
1. Go to GitHub → **Actions** tab
2. Select a workflow
3. Click **Run workflow**

---

## Verification Checklist

After deployment completes:

- [ ] Backend health check: `https://YOUR-BACKEND.azurewebsites.net/health`
- [ ] Frontend loads: `https://YOUR-FRONTEND.azurestaticapps.net`
- [ ] Can track requests on frontend
- [ ] HR Dashboard loads

---

## Troubleshooting

### "Publish profile is invalid"
- Re-download the publish profile
- Make sure you copied the ENTIRE XML content
- Check for extra spaces at the beginning/end

### "Static Web App deployment failed"
- Verify the API token is correct
- Check that the repository/branch settings match

### "CORS error in browser"
- Update CORS_ORIGINS in App Service settings
- Include the full URL with `https://`
- Restart the App Service after changing settings

### "502 Bad Gateway"
- Check App Service logs: **Monitoring** → **Log stream**
- Verify startup command is set to `bash startup.sh`
- Check that Python 3.11 runtime is selected

---

## Cost Summary

| Resource | Free Tier | Paid (B1) |
|----------|-----------|-----------|
| App Service | Not available | ~$13/month |
| Static Web App | Free | Free |
| **Total** | N/A | ~$13/month |

For development, use the $200 free credit from new Azure accounts.
