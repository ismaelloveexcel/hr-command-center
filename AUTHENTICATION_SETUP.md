# 🔐 Authentication Setup Guide

**Complete guide for configuring Azure OIDC authentication for GitHub Actions**

---

## 📋 Overview

This guide walks you through setting up OpenID Connect (OIDC) authentication between GitHub Actions and Azure. This is the **recommended and most secure** method as it eliminates the need for long-lived credentials.

### Why OIDC?

✅ **No long-lived secrets** - Tokens are short-lived and auto-rotated  
✅ **More secure** - No credentials stored in GitHub  
✅ **Azure-native** - Uses Azure AD for authentication  
✅ **Auditable** - Full audit trail in Azure AD  

---

## 🎯 Prerequisites

Before starting, ensure you have:

- [ ] Azure subscription (with Owner or User Access Administrator role)
- [ ] Access to Azure Portal (https://portal.azure.com)
- [ ] Admin access to GitHub repository settings
- [ ] Azure CLI installed (for command-line setup)

---

## 🚀 Quick Setup (Automated)

### Option 1: Using Azure Portal Script

```bash
# Run this in Azure Cloud Shell
curl -sSL https://aka.ms/create-github-oidc | bash
```

### Option 2: Using Azure CLI

```bash
# Login to Azure
az login

# Set variables (customize these)
SUBSCRIPTION_ID="your-subscription-id"
RESOURCE_GROUP="baynunah-hr-portal-rg"
REPO_OWNER="ismaelloveexcel"
REPO_NAME="hr-command-center"

# Create Azure AD application
APP_NAME="github-actions-${REPO_NAME}"

APP_ID=$(az ad app create \
  --display-name "$APP_NAME" \
  --query appId -o tsv)

echo "✅ App created with ID: $APP_ID"

# Create service principal
az ad sp create --id $APP_ID

# Wait for propagation
sleep 10

# Get service principal object ID
SP_OBJECT_ID=$(az ad sp show --id $APP_ID --query id -o tsv)

# Assign contributor role
az role assignment create \
  --role Contributor \
  --assignee-object-id $SP_OBJECT_ID \
  --subscription $SUBSCRIPTION_ID \
  --scope "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP"

echo "✅ Role assigned"

# Configure federated credentials
az ad app federated-credential create \
  --id $APP_ID \
  --parameters '{
    "name": "github-actions-main",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:'"$REPO_OWNER"'/'"$REPO_NAME"':ref:refs/heads/main",
    "audiences": ["api://AzureADTokenExchange"]
  }'

echo "✅ Federated credential created for main branch"

# Get tenant ID
TENANT_ID=$(az account show --query tenantId -o tsv)

# Display secrets to add to GitHub
echo ""
echo "=========================================="
echo "🔐 ADD THESE SECRETS TO GITHUB:"
echo "=========================================="
echo ""
echo "AZURE_CLIENT_ID: $APP_ID"
echo "AZURE_TENANT_ID: $TENANT_ID"
echo "AZURE_SUBSCRIPTION_ID: $SUBSCRIPTION_ID"
echo ""
echo "Add these at:"
echo "https://github.com/$REPO_OWNER/$REPO_NAME/settings/secrets/actions"
echo ""
```

---

## 📖 Manual Setup (Step-by-Step)

### Step 1: Create Azure AD Application

1. Go to **Azure Portal** → **Azure Active Directory** → **App registrations**
2. Click **+ New registration**
3. Configure:
   - **Name**: `github-actions-hr-command-center`
   - **Supported account types**: Single tenant
   - **Redirect URI**: Leave empty
4. Click **Register**
5. **Copy the Application (client) ID** - you'll need this as `AZURE_CLIENT_ID`

### Step 2: Create Service Principal

1. In the app registration, go to **Overview**
2. The service principal is created automatically
3. Note the **Directory (tenant) ID** - you'll need this as `AZURE_TENANT_ID`

### Step 3: Assign Azure Permissions

1. Go to your **Azure Subscription**
2. Click **Access control (IAM)**
3. Click **+ Add** → **Add role assignment**
4. Configure:
   - **Role**: Contributor
   - **Assign access to**: User, group, or service principal
   - **Members**: Search for `github-actions-hr-command-center`
5. Click **Review + assign**

Alternatively, assign at resource group level:
1. Go to your **Resource Group** (`baynunah-hr-portal-rg`)
2. Click **Access control (IAM)**
3. Follow same steps as above

### Step 4: Configure Federated Credentials

1. In the app registration, go to **Certificates & secrets**
2. Click **Federated credentials** tab
3. Click **+ Add credential**
4. Configure:
   - **Federated credential scenario**: GitHub Actions deploying Azure resources
   - **Organization**: `ismaelloveexcel`
   - **Repository**: `hr-command-center`
   - **Entity type**: Branch
   - **GitHub branch name**: `main`
   - **Name**: `github-actions-main`
5. Click **Add**

**Important**: Add credentials for each branch/environment you need:
- Main branch: `repo:ismaelloveexcel/hr-command-center:ref:refs/heads/main`
- Pull requests: `repo:ismaelloveexcel/hr-command-center:pull_request`
- Tags: `repo:ismaelloveexcel/hr-command-center:ref:refs/tags/*`

### Step 5: Add Secrets to GitHub

1. Go to **GitHub Repository** → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret** for each:

**AZURE_CLIENT_ID**
```
Value: [Application (client) ID from Step 1]
```

**AZURE_TENANT_ID**
```
Value: [Directory (tenant) ID from Step 2]
```

**AZURE_SUBSCRIPTION_ID**
```
Value: [Your Azure subscription ID]
```

To find subscription ID:
```bash
az account show --query id -o tsv
```

---

## ✅ Verification

### Test 1: Run Validation Workflow

1. Go to **GitHub Actions** → **Integration Test (Simulation)**
2. Click **Run workflow**
3. Enter test environment name: `auth-test`
4. Click **Run workflow**
5. Check if authentication step passes

### Test 2: Manual Verification

```bash
# In GitHub Actions workflow
- name: Test Azure Login
  uses: azure/login@v1
  with:
    client-id: ${{ secrets.AZURE_CLIENT_ID }}
    tenant-id: ${{ secrets.AZURE_TENANT_ID }}
    subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}

- name: Verify Access
  run: |
    az account show
    az group list
```

### Test 3: Check Permissions

```bash
# Run this in a workflow
az role assignment list \
  --assignee ${{ secrets.AZURE_CLIENT_ID }} \
  --all \
  --query "[].{Role:roleDefinitionName,Scope:scope}" \
  -o table
```

---

## 🔧 Troubleshooting

### Error: "Failed to get OIDC token"

**Cause**: Federated credentials not configured correctly

**Solution**:
1. Verify the subject claim matches exactly: `repo:OWNER/REPO:ref:refs/heads/BRANCH`
2. Check that the credential is for the correct branch
3. Wait 5 minutes for Azure AD propagation

### Error: "Invalid audience"

**Cause**: Audience mismatch in federated credential

**Solution**:
1. Ensure audience is set to: `api://AzureADTokenExchange`
2. Recreate federated credential if needed

### Error: "Insufficient permissions"

**Cause**: Service principal doesn't have required Azure permissions

**Solution**:
1. Go to Azure Portal → Subscription → Access control (IAM)
2. Verify the service principal has Contributor role
3. Check scope includes the resource group

### Error: "AADSTS700016: Application not found"

**Cause**: Application not found or deleted

**Solution**:
1. Verify `AZURE_CLIENT_ID` is correct
2. Check application still exists in Azure AD
3. Ensure you're using the right tenant

---

## 🔐 Security Best Practices

### 1. Principle of Least Privilege

Only grant permissions needed:
```bash
# Instead of Contributor on subscription, use on resource group
az role assignment create \
  --role Contributor \
  --scope "/subscriptions/$SUB_ID/resourceGroups/$RG_NAME" \
  --assignee $APP_ID
```

### 2. Use Separate Identities

Create different apps for different environments:
- `github-actions-hr-portal-prod`
- `github-actions-hr-portal-test`
- `github-actions-hr-portal-dev`

### 3. Audit Regularly

```bash
# List all role assignments
az role assignment list \
  --assignee $APP_ID \
  --all \
  -o table

# Review sign-in logs in Azure AD
```

### 4. Rotate When Needed

While OIDC tokens auto-rotate, you may need to recreate credentials if:
- Repository renamed
- Organization changed
- Security incident

### 5. Monitor Usage

Set up alerts for:
- Failed authentication attempts
- Unusual access patterns
- Permission changes

---

## 📚 Additional Resources

### Microsoft Documentation
- [Azure OIDC with GitHub Actions](https://docs.microsoft.com/azure/developer/github/connect-from-azure)
- [Federated Credentials](https://docs.microsoft.com/azure/active-directory/develop/workload-identity-federation)
- [GitHub Actions Azure Login](https://github.com/Azure/login)

### GitHub Documentation
- [OIDC in GitHub Actions](https://docs.github.com/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect)
- [Configuring OIDC in Azure](https://docs.github.com/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-azure)

### Videos
- [Setting up OIDC with Azure](https://www.youtube.com/watch?v=...)
- [GitHub Actions Security Best Practices](https://www.youtube.com/watch?v=...)

---

## 🎯 Quick Reference

### Required Secrets
| Secret | Description | Where to Find |
|--------|-------------|---------------|
| `AZURE_CLIENT_ID` | App ID | Azure AD → App registrations → Application (client) ID |
| `AZURE_TENANT_ID` | Tenant ID | Azure AD → Overview → Directory (tenant) ID |
| `AZURE_SUBSCRIPTION_ID` | Subscription | Azure → Subscriptions → Subscription ID |

### Required Azure Permissions
| Permission | Scope | Why |
|------------|-------|-----|
| Contributor | Resource Group | Create/manage resources |
| Application Administrator | Azure AD | Optional: For self-service |

### Federated Credential Format
```
Subject: repo:OWNER/REPO:ENTITY_TYPE:ENTITY_NAME
Issuer: https://token.actions.githubusercontent.com
Audience: api://AzureADTokenExchange
```

---

## ❓ FAQ

### Q: Can I use this with pull requests?

**A**: Yes! Add a federated credential with subject: `repo:OWNER/REPO:pull_request`

### Q: Do I need to rotate secrets?

**A**: No! OIDC tokens are short-lived and auto-rotate. No manual rotation needed.

### Q: Can I use the same identity for multiple repos?

**A**: Not recommended. Create separate identities for better security and isolation.

### Q: What if I don't have Owner role?

**A**: You need at least:
- User Access Administrator (to assign roles)
- Application Administrator (to create app registrations)

Contact your Azure admin if you don't have these.

### Q: Can I test this locally?

**A**: OIDC only works in GitHub Actions. For local testing, use:
```bash
az login  # Interactive login
```

---

## ✅ Completion Checklist

Before considering setup complete:

- [ ] Azure AD application created
- [ ] Service principal has Contributor role
- [ ] Federated credentials configured for main branch
- [ ] All 3 secrets added to GitHub
- [ ] Test workflow run successful
- [ ] Azure access verified
- [ ] Permissions validated
- [ ] Documentation updated (if custom setup)

---

**Last Updated**: February 3, 2026  
**Status**: Production Ready  
**Maintained By**: DevOps Team

---

**Need Help?**

1. Check troubleshooting section above
2. Review [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)
3. Contact Azure admin for permission issues
4. Review Azure AD sign-in logs for auth failures
