# 🔧 Deployment Troubleshooting Guide

**Quick Reference Guide for Common Deployment Issues**

---

## 🚨 Common Issues & Solutions

### Issue 1: "Unable to retrieve details of the existing app"

**Symptoms:**
```
ERROR: Unable to retrieve details of the existing app 'baynunah-hr-portal'.
```

**Cause:** Azure Web App in inconsistent state (partially created or deleted)

**Solution:**
```bash
# Option A: Use cleanup workflow (recommended)
1. Go to GitHub Actions
2. Run workflow: "Backend Cleanup (Reset Infrastructure)"
3. Type: DELETE-BACKEND
4. Wait 2-5 minutes
5. Run "Backend Bootstrap (First Deployment)"

# Option B: Manual cleanup (requires Azure CLI)
az webapp delete \
  --name baynunah-hr-portal \
  --resource-group baynunah-hr-portal-rg

# Wait 2-5 minutes, then run bootstrap workflow
```

---

### Issue 2: "Backend does not exist"

**Symptoms:**
```
❌ ERROR: Backend 'baynunah-hr-portal' does not exist!
Run 'backend-bootstrap.yml' workflow first to create the infrastructure.
```

**Cause:** Infrastructure not created or deleted

**Solution:**
```bash
1. Go to GitHub Actions
2. Run workflow: "Backend Bootstrap (First Deployment)"
3. Wait for completion (~5-10 minutes)
4. Verify: https://baynunah-hr-portal.azurewebsites.net/health
5. Now run regular deployment
```

**If bootstrap fails, see Issue 1**

---

### Issue 3: "npm ci can only install packages when package.json and package-lock.json are in sync"

**Symptoms:**
```
npm error `npm ci` can only install packages when your package.json 
          and package-lock.json are in sync.
npm error Missing: yaml@2.8.2 from lock file
```

**Cause:** package-lock.json out of sync with package.json

**Solution:**
```bash
# Fixed in this PR - if you still see this:
cd frontend
rm package-lock.json
npm install
git add package-lock.json
git commit -m "Regenerate package-lock.json"
git push
```

**Status:** ✅ Already fixed in this branch

---

### Issue 4: "Health check failed"

**Symptoms:**
```
❌ Health check failed after 5 attempts
```

**Cause:** Backend application not starting correctly

**Solution:**
```bash
# 1. Check application logs
az webapp log tail \
  --name baynunah-hr-portal \
  --resource-group baynunah-hr-portal-rg

# 2. Check configuration
az webapp config appsettings list \
  --name baynunah-hr-portal \
  --resource-group baynunah-hr-portal-rg

# 3. Common fixes:
# - Verify startup.sh exists and is executable
# - Check DATABASE_URL is set
# - Verify HR_API_KEY is configured
# - Check Python dependencies installed

# 4. If nothing works, run repair workflow
Go to GitHub Actions → "Backend Repair (Autonomous Self-Healing)"
```

---

### Issue 5: "Missing AZURE_CLIENT_ID secret"

**Symptoms:**
```
❌ Missing AZURE_CLIENT_ID secret.
```

**Cause:** OIDC authentication not configured

**Solution:**
```bash
# Set up OIDC authentication (one-time setup)
# See: https://learn.microsoft.com/azure/developer/github/connect-from-azure

# Required GitHub Secrets:
1. AZURE_CLIENT_ID
2. AZURE_TENANT_ID  
3. AZURE_SUBSCRIPTION_ID

# To add secrets:
1. Go to: https://github.com/ismaelloveexcel/hr-command-center/settings/secrets/actions
2. Click "New repository secret"
3. Add each secret with values from Azure
```

---

### Issue 6: Workflow stuck or timeout

**Symptoms:**
- Workflow runs for 30+ minutes
- No progress updates
- Eventually times out

**Solution:**
```bash
# 1. Cancel the stuck workflow
# 2. Check Azure Portal for resource state
# 3. If resource creation stuck, delete it:

az webapp delete --name baynunah-hr-portal --resource-group baynunah-hr-portal-rg

# 4. Wait 5 minutes, then retry
```

---

## 📋 Quick Diagnostic Commands

### Check if resources exist
```bash
# Login to Azure
az login

# List all web apps in resource group
az webapp list --resource-group baynunah-hr-portal-rg -o table

# Check specific web app
az webapp show \
  --name baynunah-hr-portal \
  --resource-group baynunah-hr-portal-rg

# Check app state
az webapp show \
  --name baynunah-hr-portal \
  --resource-group baynunah-hr-portal-rg \
  --query "state" -o tsv
```

### Check application health
```bash
# Test health endpoint
curl https://baynunah-hr-portal.azurewebsites.net/health

# Expected response:
# {"status":"healthy","service":"UAE HR Portal API"}

# Check application logs
az webapp log tail \
  --name baynunah-hr-portal \
  --resource-group baynunah-hr-portal-rg
```

### Verify configuration
```bash
# List app settings
az webapp config appsettings list \
  --name baynunah-hr-portal \
  --resource-group baynunah-hr-portal-rg

# Check startup command
az webapp config show \
  --name baynunah-hr-portal \
  --resource-group baynunah-hr-portal-rg \
  --query "linuxFxVersion"
```

---

## 🔄 Recovery Workflows

### Complete Reset (Nuclear Option)

**When to use:** Everything is broken, start from scratch

```bash
# 1. Clean up all resources
GitHub Actions → "Backend Cleanup" → Type: DELETE-BACKEND

# 2. Wait 5 minutes

# 3. Bootstrap from scratch
GitHub Actions → "Backend Bootstrap (First Deployment)"

# 4. Deploy code
git push origin main
```

### Soft Reset (Preserve Resources)

**When to use:** Configuration issues, not resource issues

```bash
# 1. Run repair workflow
GitHub Actions → "Backend Repair (Autonomous Self-Healing)"

# 2. If that doesn't work, redeploy
GitHub Actions → "Backend Deploy (Regular Deployments)"
```

---

## 🎯 Decision Tree

```
Deployment Failed?
│
├─ "Unable to retrieve app" → Issue 1 → Run cleanup workflow
│
├─ "Backend does not exist" → Issue 2 → Run bootstrap workflow
│
├─ "npm ci sync error" → Issue 3 → ✅ Already fixed
│
├─ "Health check failed" → Issue 4 → Check logs, run repair
│
├─ "Missing secret" → Issue 5 → Configure GitHub secrets
│
└─ "Timeout/Stuck" → Issue 6 → Cancel and cleanup
```

---

## 🔍 Investigation Steps

### Step 1: Identify the failure
1. Go to GitHub Actions
2. Click on the failed workflow run
3. Expand failed job
4. Read error message
5. Match to issues above

### Step 2: Verify Azure state
```bash
az login
az account show  # Verify subscription
az webapp list --resource-group baynunah-hr-portal-rg -o table
```

### Step 3: Check prerequisites
- [ ] OIDC secrets configured in GitHub
- [ ] Azure subscription active
- [ ] Resource group exists
- [ ] No quota limits reached

### Step 4: Apply solution
- Use workflow solutions (recommended)
- Or use manual Azure CLI commands
- Document what you did

### Step 5: Verify fix
```bash
# Test deployment
git commit --allow-empty -m "Test deployment"
git push

# Monitor workflow
gh run watch

# Test endpoints
curl https://baynunah-hr-portal.azurewebsites.net/health
```

---

## 📚 Workflow Reference

### Backend Workflows

| Workflow | Purpose | When to Use |
|----------|---------|-------------|
| backend-bootstrap.yml | Create infrastructure | First time only |
| backend-deploy.yml | Deploy code | Every code change |
| backend-repair.yml | Fix configuration | When config broken |
| backend-cleanup.yml | Delete resources | Reset everything |

### Frontend Workflows

| Workflow | Purpose | When to Use |
|----------|---------|-------------|
| frontend-deploy.yml | Deploy frontend | Every code change |

---

## 🆘 Getting Help

### Before asking for help:
1. ✅ Read this troubleshooting guide
2. ✅ Check GitHub Actions logs
3. ✅ Verify Azure Portal shows correct state
4. ✅ Try the suggested solutions

### When asking for help, provide:
- Workflow name that failed
- Error message (full text)
- GitHub Actions run URL
- Azure resource state (screenshot if possible)
- What you've already tried

---

## 🔐 Security Checklist

Before deployment, verify:
- [ ] All secrets are in GitHub (not hardcoded)
- [ ] OIDC authentication working
- [ ] No credentials in logs
- [ ] HTTPS-only enabled
- [ ] CORS configured correctly
- [ ] DEBUG=False in production

---

## 📊 Health Check Checklist

After deployment, verify:
- [ ] Backend health endpoint responds: `/health`
- [ ] API docs accessible: `/docs`
- [ ] Frontend loads correctly
- [ ] Frontend can call backend APIs
- [ ] No errors in browser console
- [ ] No errors in Azure application logs

---

## 🎓 Learning Resources

- [Azure Web Apps Documentation](https://docs.microsoft.com/azure/app-service/)
- [GitHub Actions Documentation](https://docs.github.com/actions)
- [Azure CLI Reference](https://docs.microsoft.com/cli/azure/)
- [Troubleshooting Azure Web Apps](https://docs.microsoft.com/azure/app-service/troubleshoot-diagnostic-logs)

---

**Last Updated:** February 3, 2026  
**Version:** 1.0  
**Maintained By:** DevOps Team
