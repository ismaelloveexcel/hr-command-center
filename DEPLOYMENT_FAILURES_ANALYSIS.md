# Deployment Failures Analysis

## Executive Summary

**Root Cause**: Missing Azure OIDC authentication secrets in GitHub repository settings.

All backend and infrastructure deployment workflows are failing with authentication errors because the required Azure OIDC secrets (`AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`) are not configured in the GitHub repository.

## Evidence

### Failed Workflows

1. **Backend Deploy (Regular Deployments)** - All runs failing
2. **Complete Azure Setup & Deploy** - All runs failing  
3. **Backend Bootstrap** - Would fail if run (uses same auth)
4. **Backend Repair** - Would fail if run (uses same auth)

### Successful Workflows

- **Deploy Frontend to Azure Static Web Apps** - ✅ Working (uses `AZURE_STATIC_WEB_APPS_API_TOKEN` instead of OIDC)

### Error Messages

```
Login failed with Error: Using auth-type: SERVICE_PRINCIPAL. 
Not all values are present. Ensure 'client-id' and 'tenant-id' are supplied.
```

### Logs Evidence

From failed workflow run #21569861007:
```
2026-02-01T20:40:12.9855489Z ##[error]Login failed with Error: Using auth-type: SERVICE_PRINCIPAL. 
Not all values are present. Ensure 'client-id' and 'tenant-id' are supplied.
```

From failed workflow run #21568274249:
```
env:
  AZURE_SUBSCRIPTION_ID:    <-- EMPTY!
```

## Why Frontend Works But Backend Doesn't

- **Frontend workflow** uses simple API token authentication (`AZURE_STATIC_WEB_APPS_API_TOKEN`)
- **Backend workflows** use modern OIDC authentication which requires 3 secrets:
  - `AZURE_CLIENT_ID`
  - `AZURE_TENANT_ID`  
  - `AZURE_SUBSCRIPTION_ID`

## Solution

### Step 1: Set Up Azure OIDC Authentication

Follow these steps to configure OIDC authentication for GitHub Actions:

1. **Create a Service Principal in Azure**:
   ```bash
   az ad sp create-for-rbac \
     --name "GitHub-Actions-HR-Portal" \
     --role contributor \
     --scopes /subscriptions/{subscription-id}/resourceGroups/baynunah-hr-portal-rg \
     --json-auth
   ```

2. **Create a Federated Credential** for the Service Principal:
   ```bash
   az ad app federated-credential create \
     --id {app-id} \
     --parameters '{
       "name": "GitHub-Actions-Federation",
       "issuer": "https://token.actions.githubusercontent.com",
       "subject": "repo:{GITHUB_REPOSITORY_OWNER}/{REPOSITORY_NAME}:ref:refs/heads/main",
       "audiences": ["api://AzureADTokenExchange"]
     }'
   ```

3. **Get the required values**:
   - Client ID: From the service principal (also called App ID)
   - Tenant ID: From your Azure AD
   - Subscription ID: Your Azure subscription ID

### Step 2: Add Secrets to GitHub Repository

1. Go to your GitHub repository's **Settings** page
2. Navigate to **Secrets and variables** → **Actions**
3. Click **New repository secret** and add each of these:

| Secret Name | Value | How to Get It |
|-------------|-------|---------------|
| `AZURE_CLIENT_ID` | The Client ID (App ID) from service principal | From Step 1 output or `az ad sp show` command |
| `AZURE_TENANT_ID` | Your Azure AD Tenant ID | Run: `az account show --query tenantId -o tsv` |
| `AZURE_SUBSCRIPTION_ID` | Your Azure Subscription ID | Run: `az account show --query id -o tsv` |

### Step 3: Verify Configuration

After adding the secrets, test by manually running one of these workflows:

1. **Backend Bootstrap** (if backend doesn't exist yet)
2. **Backend Deploy** (if backend already exists)
3. **Complete Azure Setup & Deploy** (for full stack deployment)

## Additional Recommendations

### 1. Add Secret Validation

I recommend adding validation steps to workflows to fail fast with clear messages. This has been implemented in the updated workflows.

### 2. Update Documentation

The repository already has good documentation about these secrets in:
- `README.md`
- `docs/AZURE_BACKEND_WORKFLOWS.md`
- `docs/QUICK_DEPLOY_GUIDE.md`

These docs are accurate and should be followed.

### 3. Consider Alternative Authentication (If Needed)

If OIDC setup is problematic, you could:
- Use Service Principal with credentials (less secure, but simpler)
- Use Publish Profiles for individual services (less flexible)

However, **OIDC is the recommended modern approach** and worth the initial setup effort.

## Timeline of Failures

Based on workflow run history:
- **All backend deployments have been failing** since the workflows were created
- **Frontend deployments work** because they use a different auth method
- **No successful backend deployments found** in the workflow history

## Impact

**Current State**:
- ❌ Cannot deploy backend application
- ❌ Cannot create/update Azure infrastructure  
- ❌ Cannot run automated deployments
- ✅ Frontend deployments working

**After Fix**:
- ✅ Full CI/CD pipeline operational
- ✅ Automated backend deployments
- ✅ Infrastructure as code deployments
- ✅ Self-healing repair workflows

## Next Steps

1. **Immediate**: Add the three Azure OIDC secrets to GitHub repository
2. **Test**: Run "Backend Bootstrap" workflow to create infrastructure
3. **Validate**: Check that health endpoints respond
4. **Monitor**: Watch for any additional issues

## References

- [Azure OIDC for GitHub Actions](https://learn.microsoft.com/azure/developer/github/connect-from-azure)
- [GitHub Actions Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- Repository docs: `docs/QUICK_DEPLOY_GUIDE.md`
