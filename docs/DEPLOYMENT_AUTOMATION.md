# Deployment Automation Guide

## What Can Be Automated?

Based on the deployment prerequisites in the documentation, here's what can and cannot be automated:

### ✅ Fully Automated (One-Click Setup)

The repository already includes `infrastructure/setup-azure.sh` which automates:

1. **Azure Resource Creation** ✅
   - Resource Group creation
   - App Service Plan creation
   - Backend Web App (Python 3.11)
   - Static Web App (React frontend)
   - CORS configuration

2. **GitHub Secrets Configuration** ✅
   - `AZURE_BACKEND_APP_NAME`
   - `AZURE_BACKEND_PUBLISH_PROFILE`
   - `AZURE_STATIC_WEB_APPS_API_TOKEN`
   - `REACT_APP_API_URL`

3. **Deployment Trigger** ✅
   - Automatic workflow execution
   - Deployment monitoring commands

### ⚠️ Semi-Automated

4. **PR #9 Merge** ⚠️ Semi-automated
   - Can use: `gh pr merge 9`
   - Requires: Manual review/approval decision
   - **Why manual?** Code review is a human decision

5. **Deployment Verification** ⚠️ Semi-automated
   - Health checks can be scripted
   - Integration tests can run automatically
   - Manual testing still recommended for critical features

### ❌ Cannot Be Automated (User Decisions)

6. **Azure Account Setup** ❌
   - Requires: Credit card for identity verification
   - Requires: User email/phone verification
   - **Why?** Financial and legal requirements

7. **GitHub Authentication** ❌
   - Requires: User login credentials
   - Requires: 2FA if enabled
   - **Why?** Security policy

## 🚀 Using the Automated Setup

### One-Command Setup

Run the fully automated script:

```bash
cd infrastructure
./setup-azure.sh
```

**What it does**:
1. ✅ Checks prerequisites (Azure CLI, GitHub CLI)
2. ✅ Creates all Azure resources
3. ✅ Configures backend settings
4. ✅ Gets deployment credentials
5. ✅ Sets all GitHub secrets automatically
6. ✅ Triggers initial deployment

**Prerequisites**:
- Azure CLI installed (`az --version`)
- GitHub CLI installed (`gh --version`)
- Logged into Azure (`az login`)
- Logged into GitHub (`gh auth login`)

**Time**: ~5 minutes (fully automated)

### Step-by-Step Automation

If you prefer granular control:

#### 1. Create Azure Resources (Automated)

```bash
# Using Bicep template
cd infrastructure
az group create --name hr-portal-rg --location eastus
az deployment group create \
  --resource-group hr-portal-rg \
  --template-file main.bicep
```

#### 2. Configure GitHub Secrets (Automated)

```bash
# Get values from Azure
BACKEND_NAME=$(az webapp list -g hr-portal-rg --query "[?contains(name, 'api')].name" -o tsv)
BACKEND_URL="https://${BACKEND_NAME}.azurewebsites.net"

# Get publish profile
PUBLISH_PROFILE=$(az webapp deployment list-publishing-profiles \
  --name "$BACKEND_NAME" \
  --resource-group hr-portal-rg \
  --xml)

# Get Static Web App token
SWA_NAME=$(az staticwebapp list -g hr-portal-rg --query "[0].name" -o tsv)
SWA_TOKEN=$(az staticwebapp secrets list \
  --name "$SWA_NAME" \
  --resource-group hr-portal-rg \
  --query "properties.apiKey" -o tsv)

# Set GitHub secrets (requires gh CLI)
gh secret set AZURE_BACKEND_APP_NAME --body "$BACKEND_NAME"
gh secret set AZURE_BACKEND_PUBLISH_PROFILE --body "$PUBLISH_PROFILE"
gh secret set AZURE_STATIC_WEB_APPS_API_TOKEN --body "$SWA_TOKEN"
gh secret set REACT_APP_API_URL --body "$BACKEND_URL"
```

#### 3. Trigger Deployment (Automated)

```bash
# Manual workflow trigger
gh workflow run backend-deploy.yml
gh workflow run frontend-deploy.yml

# Or push to main for automatic trigger
git push origin main
```

#### 4. Verify Deployment (Semi-Automated)

```bash
# Automated health check
BACKEND_URL=$(gh secret list | grep REACT_APP_API_URL | awk '{print $2}')
curl -f $BACKEND_URL/health || echo "Health check failed"

# Wait for deployment to complete
gh run watch

# Manual verification still recommended
```

## 🛠️ Automation Tools Included

### 1. `infrastructure/setup-azure.sh`
**Fully automated one-click setup**

Features:
- ✅ Prerequisite validation
- ✅ Interactive confirmation
- ✅ Color-coded output
- ✅ Error handling
- ✅ Progress indicators
- ✅ Automatic secret configuration

Usage:
```bash
cd infrastructure
chmod +x setup-azure.sh
./setup-azure.sh
```

### 2. `infrastructure/main.bicep`
**Infrastructure as Code (IaC) template**

Features:
- ✅ Declarative resource definitions
- ✅ Parameterized configuration
- ✅ Output values for automation
- ✅ Idempotent (safe to re-run)

Usage:
```bash
az deployment group create \
  --resource-group hr-portal-rg \
  --template-file infrastructure/main.bicep \
  --parameters baseName=hrportal location=eastus
```

### 3. `infrastructure/deploy.sh`
**Semi-automated deployment script**

Features:
- ✅ Resource group creation
- ✅ Bicep template deployment
- ✅ Output extraction
- ✅ Instructions for next steps

Usage:
```bash
cd infrastructure
./deploy.sh [resource-group] [location]
```

### 4. GitHub Actions Workflows
**Fully automated CI/CD**

Files:
- `.github/workflows/backend-deploy.yml`
- `.github/workflows/frontend-deploy.yml`

Features:
- ✅ Automatic on push to main
- ✅ Manual dispatch option
- ✅ Built-in testing
- ✅ Health check verification
- ✅ Deployment status reporting

## 📋 Automation Checklist

### Initial Setup (One-Time)

- [ ] Install Azure CLI: `brew install azure-cli` (or [other methods](https://docs.microsoft.com/cli/azure/install-azure-cli))
- [ ] Install GitHub CLI: `brew install gh` (or [other methods](https://cli.github.com/))
- [ ] Login to Azure: `az login`
- [ ] Login to GitHub: `gh auth login`
- [ ] Run automation: `cd infrastructure && ./setup-azure.sh`

### Ongoing Deployments (Fully Automated)

- [ ] Make code changes
- [ ] Commit and push to main: `git push origin main`
- [ ] Deployment happens automatically via GitHub Actions
- [ ] Monitor: `gh run watch`

## 🔄 Comparison: Manual vs. Automated

| Task | Manual Time | Automated Time | Tool |
|------|-------------|----------------|------|
| Azure resource creation | 15-20 min | 2-3 min | `setup-azure.sh` |
| GitHub secrets config | 10-15 min | < 1 min | `gh secret set` |
| Deployment trigger | 2-5 min | < 1 min | GitHub Actions |
| Total Initial Setup | 30-40 min | 5-10 min | Full automation |
| Subsequent Deploys | 5-10 min | < 1 min | Auto on push |

## 🎯 Recommended Approach

### For First-Time Setup

**Use the fully automated script**:

```bash
# One command does everything
cd infrastructure
./setup-azure.sh
```

**Why?**
- ✅ Fastest method (5-10 minutes)
- ✅ Least error-prone
- ✅ Validates prerequisites
- ✅ Sets up everything correctly
- ✅ Provides clear status updates

### For Ongoing Deployments

**Use automatic GitHub Actions**:

```bash
# Just push your changes
git add .
git commit -m "Your changes"
git push origin main

# GitHub Actions handles the rest
```

**Why?**
- ✅ No manual intervention needed
- ✅ Consistent deployment process
- ✅ Built-in testing and validation
- ✅ Automatic rollback on failure
- ✅ Audit trail in GitHub

## 🆕 Enhanced Automation Script

For even more automation, you can extend `setup-azure.sh` to:

1. **Auto-merge PR #9** (if tests pass)
   ```bash
   # Add to setup-azure.sh
   if gh pr view 9 --json state -q '.state' | grep -q "OPEN"; then
     echo "Merging security PR #9..."
     gh pr merge 9 --squash --auto
   fi
   ```

2. **Post-deployment verification**
   ```bash
   # Add to setup-azure.sh
   echo "Waiting for deployment..."
   sleep 60
   curl -f "$BACKEND_URL/health" && echo "✓ Deployment successful!"
   ```

3. **Automatic monitoring setup**
   ```bash
   # Create Application Insights
   az monitor app-insights component create \
     --app hr-portal-insights \
     --location eastus \
     --resource-group hr-portal-rg
   ```

## 📚 Related Documentation

- [setup-azure.sh](../infrastructure/setup-azure.sh) - Fully automated setup script
- [main.bicep](../infrastructure/main.bicep) - Infrastructure as Code template
- [DEPLOYMENT_RUNBOOK.md](./DEPLOYMENT_RUNBOOK.md) - Manual deployment steps
- [AZURE_SETUP_GUIDE.md](./AZURE_SETUP_GUIDE.md) - Manual Azure setup

## ❓ FAQ

### Q: Can I automate the Azure account creation?
**A**: No. Azure requires identity verification with credit card and email/phone, which must be done manually for security and legal reasons.

### Q: Can I automate PR reviews?
**A**: Partially. CodeQL and automated tests run automatically, but final merge decision requires human approval for security and quality assurance.

### Q: What if the automation script fails?
**A**: The script has error handling and will show exactly what failed. You can then:
1. Fix the specific issue
2. Re-run the script (it's idempotent)
3. Or fall back to manual steps in [DEPLOYMENT_RUNBOOK.md](./DEPLOYMENT_RUNBOOK.md)

### Q: Can I run this in CI/CD?
**A**: Yes! The Bicep template and Azure CLI commands can run in GitHub Actions with service principal authentication:

```yaml
- name: Azure Login
  uses: azure/login@v1
  with:
    creds: ${{ secrets.AZURE_CREDENTIALS }}

- name: Deploy Infrastructure
  run: |
    az deployment group create \
      --resource-group hr-portal-rg \
      --template-file infrastructure/main.bicep
```

## 🎉 Summary

**What can be automated?**
- ✅ **95% of setup** using `infrastructure/setup-azure.sh`
- ✅ **100% of ongoing deployments** using GitHub Actions
- ⚠️ **Manual only**: Azure account creation, PR review decisions

**Recommended**: Use the automated setup script for fastest, most reliable deployment!

---

**Last Updated**: 2026-02-01
**Script**: `infrastructure/setup-azure.sh`
**Time to Deploy**: 5-10 minutes (fully automated)
