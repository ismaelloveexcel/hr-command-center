# 🚀 Quick Deployment Reference Card

**UAE HR Portal - Deployment Cheat Sheet**

---

## 📌 Two Ways to Deploy (Choose One)

### 🖱️ Method 1: GitHub Actions (Click Buttons)
**Time**: 10-15 minutes | **Skills**: None needed

1. **Setup Once**: Add 3 secrets to GitHub Settings → Secrets → Actions
   - `AZURE_CLIENT_ID`
   - `AZURE_TENANT_ID` 
   - `AZURE_SUBSCRIPTION_ID`

2. **Deploy**: 
   - Go to GitHub → Actions → "Complete Azure Setup & Deploy"
   - Click "Run workflow" → "Run workflow"
   - Wait 10-15 min
   - Get URLs from workflow output

3. **Result**: ✅ Live HR Portal

---

### 🤖 Method 2: AI Agent (Fully Automated)
**Time**: 5-10 minutes | **Skills**: None needed

1. **Open**: Project in Cursor IDE or VS Code + Copilot

2. **Type**: `@AZURE_DEPLOY_AUTOPILOT Deploy this application to Azure`

3. **Answer**: Any questions the agent asks

4. **Result**: ✅ Live HR Portal + All URLs

---

## 🔗 URLs After Deployment

| What | URL Pattern |
|------|-------------|
| **HR Portal** (share with employees) | `https://[name]-frontend.azurestaticapps.net` |
| **API Backend** | `https://[name]-backend.azurewebsites.net` |
| **Health Check** | `https://[name]-backend.azurewebsites.net/health` |
| **API Docs** | `https://[name]-backend.azurewebsites.net/docs` |

Replace `[name]` with your app name (default: `hrportal`)

---

## 💰 Cost

- **Free trial**: $0 (uses $200 Azure credit)
- **Development**: ~$13/month (B1 tier)
- **Production**: ~$56/month (S1 tier)

---

## 🔄 Update Deployment

**Automatic** (after initial setup):
- Just push code to `main` branch → Auto-deploys

**Manual**:
- Re-run workflow OR ask agent: `Update my deployment`

---

## 🗑️ Delete Everything

1. Go to [portal.azure.com](https://portal.azure.com)
2. Search: `hr-portal-rg`
3. Click: "Delete resource group"
4. Confirm: Type the name → Delete

---

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| Secrets not found | Add all 3 secrets to GitHub |
| Azure login fails | Check secret values |
| Blank frontend | Wait 2 min, hard refresh (Ctrl+Shift+R) |
| Backend health fails | Wait 2 min, check Azure Portal logs |
| Agent not found | Use Cursor IDE or type without `@` |

---

## ✅ Success Checklist

After deployment, verify:

- [ ] Frontend URL loads
- [ ] Can submit test request
- [ ] Can track request
- [ ] Backend `/health` returns OK
- [ ] API docs accessible at `/docs`

---

## 📚 Full Documentation

| Document | Purpose |
|----------|---------|
| [SIMPLE_DEPLOYMENT_GUIDE.md](./SIMPLE_DEPLOYMENT_GUIDE.md) | Complete step-by-step guide |
| [HOW_TO_USE_AGENTS.md](./HOW_TO_USE_AGENTS.md) | AI agent detailed guide |
| [README.md](./README.md) | Technical documentation |

---

## 🎯 Getting Help

**Stuck?** Include this info when asking:
- Error message
- Which step failed
- Screenshot of error
- Which method you used (Actions or Agent)

---

## 🔐 Get Azure Secrets (If Needed)

```bash
# 1. Login
az login

# 2. Get subscription ID
az account show --query id -o tsv

# 3. Create service principal
az ad sp create-for-rbac \
  --name "github-actions-hr-portal" \
  --role contributor \
  --scopes /subscriptions/YOUR_SUBSCRIPTION_ID

# 4. Save the output values as GitHub secrets
```

---

## 🎉 Quick Start

**First time?**

1. Choose Method 1 (GitHub Actions) OR Method 2 (AI Agent)
2. Follow the checklist for your chosen method
3. Wait for completion
4. Test the URLs
5. Done! ✅

**Already deployed?**

- **Update code**: Push to `main` branch
- **Check status**: Visit Backend URL + `/health`
- **View logs**: Azure Portal → App Service → Log stream

---

**Last Updated**: Feb 2026  
**Questions?** See [SIMPLE_DEPLOYMENT_GUIDE.md](./SIMPLE_DEPLOYMENT_GUIDE.md)
