# Quick Fix for Deployment Failures

## Problem
All backend deployments are failing with:
```
Login failed with Error: Using auth-type: SERVICE_PRINCIPAL. 
Not all values are present. Ensure 'client-id' and 'tenant-id' are supplied.
```

## Root Cause
Missing Azure OIDC authentication secrets in GitHub repository.

## Solution (5 minutes)

### Step 1: Get Azure Values

Run these commands in Azure CLI:

```bash
# Get your subscription ID (save this value)
SUBSCRIPTION_ID=$(az account show --query id -o tsv)
echo "Subscription ID: $SUBSCRIPTION_ID"

# Get your tenant ID (save this value)
TENANT_ID=$(az account show --query tenantId -o tsv)
echo "Tenant ID: $TENANT_ID"

# Create service principal and get client ID
# Replace the placeholder with your subscription ID from above
az ad sp create-for-rbac \
  --name "GitHub-Actions-HR-Portal" \
  --role contributor \
  --scopes /subscriptions/$SUBSCRIPTION_ID/resourceGroups/baynunah-hr-portal-rg \
  --json-auth
```

The output will contain `clientId`. Save this value.

### Step 2: Create Federated Credential

```bash
# Use the client ID from the previous command output
CLIENT_ID="your-client-id-from-step-1"

az ad app federated-credential create \
  --id $CLIENT_ID \
  --parameters '{
    "name": "GitHub-Actions-Federation",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:ismaelloveexcel/hr-command-center:ref:refs/heads/main",
    "audiences": ["api://AzureADTokenExchange"]
  }'
```

### Step 3: Add to GitHub

1. Go to https://github.com/ismaelloveexcel/hr-command-center/settings/secrets/actions
2. Click **New repository secret**
3. Add these three secrets:

| Secret Name | Value | Example |
|-------------|-------|---------|
| `AZURE_CLIENT_ID` | Client ID from Step 1 | `12345678-1234-1234-1234-123456789abc` |
| `AZURE_TENANT_ID` | Tenant ID from Step 1 | `87654321-4321-4321-4321-cba987654321` |
| `AZURE_SUBSCRIPTION_ID` | Subscription ID from Step 1 | `abcdef12-3456-7890-abcd-ef1234567890` |

### Step 4: Test

Run the backend bootstrap workflow:

```bash
gh workflow run backend-bootstrap.yml
```

Or go to: https://github.com/ismaelloveexcel/hr-command-center/actions/workflows/backend-bootstrap.yml
and click "Run workflow"

## Verification

After adding secrets, the workflows will:
- ✅ Pass the Azure OIDC authentication step
- ✅ Successfully create/update Azure resources
- ✅ Deploy backend application
- ✅ Run health checks

## Need More Help?

See [DEPLOYMENT_FAILURES_ANALYSIS.md](./DEPLOYMENT_FAILURES_ANALYSIS.md) for detailed analysis and troubleshooting.
