# 🤖 How to Use AI Agents for Deployment

This guide explains how to use the available AI agents to deploy the HR Portal automatically.

## What Are AI Agents?

AI agents are specialized AI assistants that can perform specific tasks automatically. This repository includes the **AZURE_DEPLOY_AUTOPILOT** agent that can deploy your application to Azure with minimal input from you.

Think of it as having an expert DevOps engineer available 24/7 who can handle all the technical deployment work for you!

---

## Available Agents

### 🚀 AZURE_DEPLOY_AUTOPILOT

**What it does:**
- Automatically detects your application type (React + FastAPI)
- Creates Azure resources if they don't exist
- Deploys both frontend and backend
- Configures everything to work together
- Validates the deployment is working
- Gives you the URLs to access your app

**When to use it:**
- First-time deployment to Azure
- When automatic deployment workflows aren't working
- When you want the fastest deployment method
- When you don't want to learn Azure or GitHub Actions

---

## How to Access AI Agents

You can use AI agents through:

### Option 1: Cursor IDE (Recommended)
[Cursor](https://cursor.sh/) is an AI-powered code editor built on VS Code.

### Option 2: GitHub Copilot in VS Code
If you have GitHub Copilot, you can use agents through the chat interface.

### Option 3: GitHub Copilot Workspace (Web)
Access through [github.com/copilot](https://github.com/copilot) (requires GitHub Copilot subscription).

---

## 🎯 Step-by-Step: Using AZURE_DEPLOY_AUTOPILOT

### Prerequisites

1. **Have the repository open** in Cursor IDE or VS Code
2. **Be logged into Azure** (the agent will check this)
3. **Have Azure subscription** (free trial is fine)

### Steps

#### Using Cursor IDE:

1. **Open the project**:
   ```bash
   cd hr-command-center
   code . # or open in Cursor
   ```

2. **Open the AI chat**:
   - Press `Ctrl+K` (Windows/Linux) or `Cmd+K` (Mac)
   - Or click the Cursor button in the sidebar

3. **Invoke the agent**:
   Type in the chat:
   ```
   @AZURE_DEPLOY_AUTOPILOT Deploy this application to Azure
   ```
   
   Or be more specific:
   ```
   @AZURE_DEPLOY_AUTOPILOT Deploy the HR Portal to Azure with resource group 'hr-portal-rg' in region 'eastus'
   ```

4. **Answer any questions**:
   The agent might ask:
   - Your Azure subscription ID (if not already logged in)
   - Preferred resource group name (default: `hr-portal-rg`)
   - Preferred region (default: `eastus`)
   - Whether to create new resources or use existing ones

5. **Wait for completion**:
   The agent will show progress as it:
   - ✅ Validates prerequisites
   - ✅ Checks Azure credentials
   - ✅ Creates/verifies resources
   - ✅ Deploys backend
   - ✅ Deploys frontend
   - ✅ Configures settings
   - ✅ Validates health

6. **Get your URLs**:
   When finished, the agent will provide:
   - **Frontend URL**: `https://your-app.azurestaticapps.net`
   - **Backend URL**: `https://your-app.azurewebsites.net`
   - **Health Check**: `https://your-app.azurewebsites.net/health`

#### Using GitHub Copilot in VS Code:

1. **Open Copilot Chat**:
   - Click the chat icon in the sidebar
   - Or press `Ctrl+Alt+I` (Windows/Linux) or `Cmd+Alt+I` (Mac)

2. **Ask for deployment**:
   ```
   Deploy this application to Azure using the AZURE_DEPLOY_AUTOPILOT agent
   ```

3. **Follow the agent's prompts** (same as Cursor)

---

## 💡 Example Conversations

### Basic Deployment

**You:**
```
@AZURE_DEPLOY_AUTOPILOT Deploy this HR Portal to Azure
```

**Agent:**
```
I'll deploy the HR Portal to Azure. Let me check your setup...

✅ Detected: React frontend + FastAPI backend
✅ Azure CLI found and authenticated
✅ Subscription: abc-123-def (Active)

I'll create:
- Resource Group: hr-portal-rg
- Region: eastus
- App Service: hrportal-backend
- Static Web App: hrportal-frontend

Proceeding with deployment...
```

### Deployment with Custom Settings

**You:**
```
@AZURE_DEPLOY_AUTOPILOT Deploy to Azure with these settings:
- Resource group: my-hr-portal
- Region: westus2
- Environment: production
```

**Agent:**
```
Deploying with custom configuration...

✅ Resource Group: my-hr-portal
✅ Region: westus2
✅ Environment: production

Creating production-grade resources...
- App Service Plan: S1 (production tier)
- SSL/TLS: Enabled
- Auto-scaling: Configured
...
```

### Fixing a Failed Deployment

**You:**
```
@AZURE_DEPLOY_AUTOPILOT The previous deployment failed. Can you fix it?
```

**Agent:**
```
I'll diagnose and repair the deployment...

Found issues:
❌ Backend health check failing
❌ Frontend can't reach backend (CORS)

Fixing:
1. Updating backend environment variables...
2. Configuring CORS for frontend URL...
3. Restarting backend service...

✅ All issues resolved. Testing health checks...
✅ Backend: Healthy
✅ Frontend: Connected
```

---

## 🎛️ Advanced Agent Commands

### Check Deployment Status
```
@AZURE_DEPLOY_AUTOPILOT Check the status of my Azure deployment
```

### Update Existing Deployment
```
@AZURE_DEPLOY_AUTOPILOT Update my production deployment with the latest code
```

### Deploy Specific Component
```
@AZURE_DEPLOY_AUTOPILOT Only deploy the backend to Azure
```

### Create Staging Environment
```
@AZURE_DEPLOY_AUTOPILOT Create a staging environment separate from production
```

### Fix Deployment Issues
```
@AZURE_DEPLOY_AUTOPILOT My deployment is failing with error: [paste error]. Please fix it.
```

---

## 🆘 Troubleshooting

### Agent Not Found

**Problem**: "Agent AZURE_DEPLOY_AUTOPILOT not found"

**Solutions**:
1. Make sure you're in the project directory
2. Verify the `.cursor/agents/` directory exists
3. Try without the `@` symbol:
   ```
   Use the AZURE_DEPLOY_AUTOPILOT agent to deploy to Azure
   ```

### Azure Authentication Issues

**Problem**: "Not authenticated to Azure"

**Solution**:
```bash
# In terminal
az login

# Verify
az account show
```

### Agent Asks Too Many Questions

**Problem**: Agent keeps asking for information

**Solution**: Provide all details upfront:
```
@AZURE_DEPLOY_AUTOPILOT Deploy to Azure:
- Subscription: abc-123-def
- Resource Group: hr-portal-rg
- Region: eastus
- Skip interactive prompts
```

### Deployment Partially Completed

**Problem**: Some resources created but deployment incomplete

**Solution**:
```
@AZURE_DEPLOY_AUTOPILOT Complete my partial deployment in resource group 'hr-portal-rg'
```

---

## 📊 What the Agent Does Behind the Scenes

When you invoke AZURE_DEPLOY_AUTOPILOT, it automatically:

1. **Analyzes Your Project**:
   - Detects React app in `/frontend`
   - Detects FastAPI app in `/backend`
   - Reads configuration files

2. **Validates Prerequisites**:
   - Checks Azure CLI installation
   - Verifies Azure authentication
   - Confirms subscription access

3. **Plans Infrastructure**:
   - Chooses appropriate Azure services
   - Calculates resource names
   - Determines configuration

4. **Creates Resources**:
   - Resource Group
   - App Service Plan
   - App Service (for backend)
   - Static Web App (for frontend)
   - Key Vault (for secrets)

5. **Deploys Applications**:
   - Builds backend code
   - Installs dependencies
   - Configures environment variables
   - Deploys frontend build
   - Connects frontend to backend

6. **Validates Deployment**:
   - Runs health checks
   - Tests API endpoints
   - Verifies frontend loads
   - Checks connectivity

7. **Reports Results**:
   - Provides all URLs
   - Lists any warnings
   - Suggests next steps

---

## ✅ Success Indicators

Your deployment is successful when you see:

```
✅ Backend deployed: https://hrportal-backend.azurewebsites.net
✅ Backend health: OK
✅ Frontend deployed: https://hrportal-frontend.azurestaticapps.net
✅ Frontend loads: OK
✅ API connectivity: OK

Deployment URL: https://hrportal-frontend.azurestaticapps.net
Deployment complete! 🎉
```

---

## 🔄 Comparison: Agent vs Manual vs Workflow

| Method | Time | Complexity | Best For |
|--------|------|------------|----------|
| **AI Agent** | 5-10 min | Very Easy | Quick deployments, fixing issues |
| **GitHub Workflow** | 10-15 min | Easy | Automated CI/CD, production |
| **Manual Azure** | 30-60 min | Complex | Learning, custom setups |

**Recommendation**: 
- Start with **AI Agent** for first deployment
- Switch to **GitHub Workflow** for ongoing deployments
- Use **AI Agent** for troubleshooting and repairs

---

## 💡 Pro Tips

1. **Be Specific**: The more details you provide upfront, the faster the deployment
   
2. **Use Natural Language**: The agent understands context:
   ```
   "Deploy my HR Portal to Azure in the East US region using the cheapest tier available"
   ```

3. **Ask for Explanations**:
   ```
   "Explain what resources you're creating and why"
   ```

4. **Request Validation**:
   ```
   "After deploying, run a full health check and show me the results"
   ```

5. **Save Outputs**: Copy the URLs and save them for future reference

6. **Combine with Workflows**: Use the agent for first deployment, then let GitHub Actions handle updates

---

## 📚 Additional Resources

- [Simple Deployment Guide](./SIMPLE_DEPLOYMENT_GUIDE.md) - For non-technical users
- [Agent Definition](./.cursor/agents/AZURE_DEPLOY_AUTOPILOT.md) - Technical details about the agent
- [Azure Backend Workflows](./docs/AZURE_BACKEND_WORKFLOWS.md) - Alternative deployment method
- [Deployment Troubleshooting](./docs/DEPLOYMENT_RUNBOOK.md) - Manual troubleshooting guide

---

## 🎉 Quick Start Checklist

Ready to use the agent? Make sure you have:

- [ ] Cursor IDE or VS Code with GitHub Copilot installed
- [ ] Project open in the editor
- [ ] Azure CLI installed: `az --version`
- [ ] Logged into Azure: `az login`
- [ ] Know your subscription ID: `az account show`

**Then simply invoke**:
```
@AZURE_DEPLOY_AUTOPILOT Deploy this application to Azure
```

**That's it!** The agent handles everything else. ✨
