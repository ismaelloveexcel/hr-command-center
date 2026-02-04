# 🚀 Simple Deployment Guide - For Non-Technical Users

> **Goal**: Deploy the HR Portal to Azure in under 15 minutes with minimal technical knowledge required.

## 📌 What is "Deployment"?

Deployment means making your HR Portal application available on the internet so employees can use it. Think of it like publishing a website - after deployment, anyone with the link can access the portal.

---

## ✨ Two Easy Ways to Deploy

You have two simple options to deploy - **choose the one that works best for you**:

### Option 1: 🖱️ Click-Button Deployment (Easiest!)
**Best for**: Anyone with a GitHub account  
**Time**: 10-15 minutes  
**Technical skills needed**: None - just clicking buttons!

### Option 2: 🤖 AI Agent Deployment (Automated!)
**Best for**: Users with Cursor IDE or GitHub Copilot  
**Time**: 5-10 minutes  
**Technical skills needed**: None - the AI does everything!

---

## 🖱️ Option 1: Click-Button Deployment

### Step 1: Check Prerequisites (One-Time Setup)

Before you start, you need:

1. **An Azure account**
   - Go to [azure.com/free](https://azure.com/free)
   - Sign up for free (includes $200 credit)
   - You'll need a credit card, but won't be charged during trial

2. **Three secret values** (Ask your IT/Azure admin to provide these):
   - `AZURE_CLIENT_ID` 
   - `AZURE_TENANT_ID`
   - `AZURE_SUBSCRIPTION_ID`
   
   > **Don't have these?** See [How to Get Azure Secrets](#how-to-get-azure-secrets) below.

### Step 2: Add Secrets to GitHub (One-Time Setup)

1. Open your repository on GitHub: `https://github.com/ismaelloveexcel/hr-command-center`
2. Click **"Settings"** (top menu)
3. In the left sidebar, click **"Secrets and variables"** → **"Actions"**
4. Click the green **"New repository secret"** button
5. Add each of the three secrets:
   - Name: `AZURE_CLIENT_ID` → Value: (paste the value your admin gave you)
   - Name: `AZURE_TENANT_ID` → Value: (paste the value)
   - Name: `AZURE_SUBSCRIPTION_ID` → Value: (paste the value)

### Step 3: Run the Deployment (The Easy Part!)

1. **Go to Actions tab**:
   - Open your repository on GitHub
   - Click the **"Actions"** tab (at the top of the page)

2. **Find the deployment workflow**:
   - On the left sidebar, look for **"Complete Azure Setup & Deploy"**
   - Click on it

3. **Start the deployment**:
   - Click the **"Run workflow"** dropdown button (top right, gray button)
   - You'll see several options - **don't change anything**, use the defaults:
     - resource_group: `hr-portal-rg` ✅
     - location: `eastus` ✅
     - base_name: `hrportal` ✅
     - app_service_sku: `B1` ✅
   - Click the green **"Run workflow"** button

4. **Wait for completion**:
   - You'll see a yellow circle (⚫) - this means it's running
   - Wait 10-15 minutes
   - When done, you'll see either:
     - ✅ Green checkmark = Success!
     - ❌ Red X = Failed (see [Troubleshooting](#troubleshooting) below)

5. **Get your URLs**:
   - Click on the workflow run (the one that just completed)
   - Scroll to the bottom
   - You'll see two important URLs:
     - **Frontend URL**: This is your HR Portal (share this with employees!)
     - **Backend URL**: This is your API (for technical reference)

**🎉 Done!** Your HR Portal is now live on the internet!

### Step 4: Test Your Deployment

1. Open the **Frontend URL** in your browser
2. You should see the HR Portal homepage
3. Try submitting a test request to ensure everything works

---

## 🤖 Option 2: AI Agent Deployment

If you use **Cursor IDE** or **GitHub Copilot**, you can use the AI agent to deploy automatically!

> **📖 Detailed Guide**: See [HOW_TO_USE_AGENTS.md](./HOW_TO_USE_AGENTS.md) for comprehensive instructions, examples, and troubleshooting.

### Quick Start with AI Agent

### Step 1: Open Your Project

1. Open the `hr-command-center` project in Cursor IDE or VS Code with GitHub Copilot

### Step 2: Ask the Agent to Deploy

**In Cursor IDE**:
1. Press `Ctrl+K` (or `Cmd+K` on Mac) to open the AI chat
2. Type: `@AZURE_DEPLOY_AUTOPILOT Deploy this application to Azure`
3. Press Enter

**In GitHub Copilot Chat**:
1. Open the Copilot Chat panel
2. Type: `Deploy this application to Azure using the AZURE_DEPLOY_AUTOPILOT agent`
3. Press Enter

### Step 3: Provide Information (If Asked)

The agent might ask for:
- Your Azure subscription ID
- Resource group name (you can use: `hr-portal-rg`)
- Region (you can use: `eastus`)

Just answer the questions in the chat.

### Step 4: Wait for the Agent to Complete

The AI agent will:
1. ✅ Check your Azure credentials
2. ✅ Create all necessary Azure resources
3. ✅ Deploy the backend API
4. ✅ Deploy the frontend app
5. ✅ Configure everything to work together
6. ✅ Give you the URLs

**Time**: 5-10 minutes

### Step 5: Get Your URLs

When the agent finishes, it will provide:
- **Frontend URL**: Your HR Portal (share with employees!)
- **Backend URL**: Your API endpoint

**🎉 Done!** The AI handled everything automatically!

---

## 🆘 Troubleshooting

### Problem: "Secrets not found" error
**Solution**: Go back to [Step 2](#step-2-add-secrets-to-github-one-time-setup) and make sure you added all three secrets correctly.

### Problem: "Resource already exists" error
**Solution**: This is normal if you ran deployment before. The workflow will update existing resources - no action needed!

### Problem: Workflow failed at "Azure Login"
**Solution**: Your Azure secrets might be wrong. Double-check the values with your Azure admin.

### Problem: Frontend shows blank page
**Solution**: 
1. Wait 2-3 more minutes (deployment might still be finishing)
2. Hard refresh your browser (Ctrl+Shift+R or Cmd+Shift+R)
3. Clear your browser cache

### Problem: Backend health check failed
**Solution**:
1. Wait 2-3 more minutes
2. Visit `https://YOUR-APP.azurewebsites.net/health` manually
3. If still failing, check Azure Portal logs

---

## 💰 What Does This Cost?

Running the HR Portal on Azure costs approximately:

- **Free trial**: $0 (uses your $200 credit)
- **After trial (Basic tier)**: ~$13/month
- **Production tier**: ~$56/month

> **Note**: You can delete everything anytime to stop charges - see [How to Delete](#how-to-delete-your-deployment) below.

---

## 🔄 How to Update Your Deployment

After initial deployment, to update the HR Portal:

### Method 1: Automatic (Recommended)
1. Make changes to your code
2. Push to the `main` branch on GitHub
3. Deployment happens automatically!

### Method 2: Manual Re-deploy
1. Go to Actions → "Complete Azure Setup & Deploy"
2. Click "Run workflow"
3. Click the green "Run workflow" button

---

## 🗑️ How to Delete Your Deployment

To completely remove the HR Portal and stop Azure charges:

### Easy Way (Azure Portal):
1. Go to [portal.azure.com](https://portal.azure.com)
2. Sign in
3. Search for `hr-portal-rg` (your resource group)
4. Click on it
5. Click "Delete resource group" at the top
6. Type the name to confirm: `hr-portal-rg`
7. Click "Delete"

**Done!** All resources are removed and billing stops.

---

## 📞 Need Help?

If you're stuck:

1. **Check this guide first** - most issues are covered above
2. **Check the workflow logs**:
   - Go to Actions tab
   - Click on your failed workflow run
   - Click on the step that failed
   - Read the error message
3. **Ask for help** - Include:
   - The error message you saw
   - Which step failed
   - Screenshot of the error

---

## 📚 Appendix

### How to Get Azure Secrets

If you need to get the Azure secrets yourself:

#### Prerequisites:
- Azure CLI installed ([Install guide](https://learn.microsoft.com/cli/azure/install-azure-cli))
- Access to your Azure subscription

#### Steps:

1. **Login to Azure**:
```bash
az login
```

2. **Get your subscription ID**:
```bash
az account show --query id -o tsv
```
Save this as `AZURE_SUBSCRIPTION_ID`

3. **Create a service principal**:
```bash
az ad sp create-for-rbac \
  --name "github-actions-hr-portal" \
  --role contributor \
  --scopes /subscriptions/YOUR_SUBSCRIPTION_ID
```

Replace `YOUR_SUBSCRIPTION_ID` with the ID from step 2.

This will output:
```json
{
  "clientId": "xxx-xxx-xxx",
  "tenantId": "xxx-xxx-xxx",
  "subscriptionId": "xxx-xxx-xxx",
  ...
}
```

- Save `clientId` as `AZURE_CLIENT_ID`
- Save `tenantId` as `AZURE_TENANT_ID`
- Save `subscriptionId` as `AZURE_SUBSCRIPTION_ID`

4. **Configure federated credentials** (for GitHub Actions):
```bash
REPO_OWNER="ismaelloveexcel"
REPO_NAME="hr-command-center"
APP_ID="xxx"  # Use the clientId from step 3

az ad app federated-credential create \
  --id $APP_ID \
  --parameters '{
    "name": "github-actions-main",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:'$REPO_OWNER'/'$REPO_NAME':ref:refs/heads/main",
    "audiences": ["api://AzureADTokenExchange"]
  }'
```

Now you have all three secrets! Add them to GitHub as described in [Step 2](#step-2-add-secrets-to-github-one-time-setup).

---

## 🎯 Quick Reference

| I want to... | What to do |
|--------------|------------|
| Deploy for the first time | Follow [Option 1](#-option-1-click-button-deployment) or [Option 2](#-option-2-ai-agent-deployment) |
| Update my deployment | Push to `main` branch or re-run the workflow |
| Check if it's working | Visit the Frontend URL from deployment output |
| See API documentation | Visit `BACKEND_URL/docs` |
| Delete everything | Follow [How to Delete](#-how-to-delete-your-deployment) |
| Check costs | View Azure Portal → Cost Management |

---

## ✅ Success Checklist

After deployment, verify:

- [ ] Frontend URL loads in browser
- [ ] Can submit a test HR request
- [ ] Can track the request using the reference number
- [ ] Backend health check works: `BACKEND_URL/health`
- [ ] API docs are accessible: `BACKEND_URL/docs`

**All green?** 🎉 Your HR Portal is successfully deployed!

---

**For more detailed technical documentation**, see:
- [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) - Comprehensive deployment guide
- [docs/QUICK_DEPLOY_GUIDE.md](./docs/QUICK_DEPLOY_GUIDE.md) - Technical quick start
- [docs/AZURE_BACKEND_WORKFLOWS.md](./docs/AZURE_BACKEND_WORKFLOWS.md) - Workflow details
