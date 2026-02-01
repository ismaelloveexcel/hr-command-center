# 🚀 Deployment Quick Start Guide

> **Start Here**: This guide provides the fastest path to deploying your UAE HR Portal to Azure.

## 🤖 Automated Setup (Recommended - 5 minutes)

**The repository includes a fully automated setup script!**

```bash
cd infrastructure
./setup-azure.sh
```

This script automatically:
- ✅ Creates all Azure resources
- ✅ Configures GitHub secrets
- ✅ Triggers deployment
- ✅ **95% automation** - just run one command!

**See [Deployment Automation Guide](./docs/DEPLOYMENT_AUTOMATION.md) for details.**

---

## 📋 What Was Done (PR #10)

This PR provides comprehensive deployment assistance:

✅ **Reviewed PR #9** - Security hardening features are production-ready  
✅ **Consolidated Workflows** - Removed duplicate Static Web Apps workflow  
✅ **Created Documentation** - Complete deployment guide suite  
✅ **Updated README** - Added clear documentation navigation  

## 🎯 Next Steps

### Option A: Automated Setup (Recommended ⭐)

```bash
# Prerequisites (one-time install)
brew install azure-cli gh  # Or use your package manager
az login                    # Login to Azure
gh auth login               # Login to GitHub

# Run automated setup
cd infrastructure
./setup-azure.sh

# Done! Everything is configured automatically.
```

**What it automates**:
- ✅ Azure resource creation (App Service, Static Web App)
- ✅ GitHub secrets configuration (all 4 secrets)
- ✅ Deployment trigger

**Time**: 5-10 minutes | **Automation**: 95% | **Details**: [DEPLOYMENT_AUTOMATION.md](./docs/DEPLOYMENT_AUTOMATION.md)

---

### Option B: Manual Setup (If automation fails)

### Step 1: Verify GitHub Secrets ⚠️

Go to: https://github.com/ismaelloveexcel/hr-command-center/settings/secrets/actions

**Required Secrets** (4 total):
- [ ] `AZURE_BACKEND_APP_NAME`
- [ ] `AZURE_BACKEND_PUBLISH_PROFILE`
- [ ] `AZURE_STATIC_WEB_APPS_API_TOKEN`
- [ ] `REACT_APP_API_URL`

**Don't have these?** → See [docs/AZURE_SETUP_GUIDE.md](./docs/AZURE_SETUP_GUIDE.md)

### Step 2: Verify Azure Resources ⚠️

Login to [Azure Portal](https://portal.azure.com)

**Required Resources**:
- [ ] Resource Group (e.g., `hr-portal-rg`)
- [ ] App Service (Python 3.11, Linux)
- [ ] Static Web App (React)

**Don't have these?** → See [docs/AZURE_SETUP_GUIDE.md](./docs/AZURE_SETUP_GUIDE.md)

### Step 3: Merge Security PR ⚠️

```bash
# Review PR #9
gh pr view 9

# Merge when ready
gh pr merge 9
```

**Why?** PR #9 adds critical security features that should be deployed.

### Step 4: Deploy 🚀

```bash
# Push to main (triggers automatic deployment)
git checkout main
git pull
git push origin main

# Monitor deployment
gh run watch
```

### Step 5: Verify ✅

```bash
# Replace with your actual URLs
BACKEND_URL="https://YOUR-APP-NAME.azurewebsites.net"
FRONTEND_URL="https://YOUR-SWA-NAME.azurestaticapps.net"

# Test backend
curl $BACKEND_URL/health
# Expected: {"status":"healthy","service":"UAE HR Portal API"}

# Test frontend
open $FRONTEND_URL
```

## 📚 Full Documentation

| Document | Use When |
|----------|----------|
| [DEPLOYMENT_STATUS.md](./docs/DEPLOYMENT_STATUS.md) | **Start here** - Current status |
| [DEPLOYMENT_CHECKLIST.md](./docs/DEPLOYMENT_CHECKLIST.md) | Verifying setup |
| [DEPLOYMENT_RUNBOOK.md](./docs/DEPLOYMENT_RUNBOOK.md) | Deploying step-by-step |
| [AZURE_SETUP_GUIDE.md](./docs/AZURE_SETUP_GUIDE.md) | Setting up Azure |
| [PR_SUMMARY.md](./PR_SUMMARY.md) | Understanding this PR |

## ❓ Common Questions

### Q: Do I need to setup Azure first?

**A**: Yes, if you haven't already. Follow [docs/AZURE_SETUP_GUIDE.md](./docs/AZURE_SETUP_GUIDE.md).

### Q: What if I don't have GitHub secrets?

**A**: You'll need to create Azure resources first, then get the secret values. See [docs/AZURE_SETUP_GUIDE.md](./docs/AZURE_SETUP_GUIDE.md) Part 3.

### Q: Should I merge PR #9?

**A**: Yes! PR #9 adds critical security features (rate limiting, input sanitization, security headers, tests). It's production-ready.

### Q: What if deployment fails?

**A**: Check [docs/DEPLOYMENT_RUNBOOK.md](./docs/DEPLOYMENT_RUNBOOK.md) "Troubleshooting" section for common issues and solutions.

### Q: How do I know if everything is working?

**A**: Use the verification checklist in [docs/DEPLOYMENT_CHECKLIST.md](./docs/DEPLOYMENT_CHECKLIST.md) "Post-Deployment Verification" section.

## 🎉 That's It!

You now have everything needed to deploy the UAE HR Portal to Azure:

✅ Documentation  
✅ Workflows  
✅ Security Features  
✅ Deployment Guide  

**Next Action**: Verify secrets and resources, then deploy! 🚀

---

**Questions?** Check [docs/DEPLOYMENT_STATUS.md](./docs/DEPLOYMENT_STATUS.md) for detailed information.
