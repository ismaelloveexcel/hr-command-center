# 🚀 Complete Azure Setup & Deploy Workflow

## Overview

The **Complete Azure Setup & Deploy** workflow is a comprehensive, end-to-end automation solution that handles the entire deployment process for the HR Portal application. It's designed specifically for non-technical users who want to deploy to Azure with minimal effort and maximum reliability.

## 🎯 What This Workflow Does

This workflow automates the complete deployment lifecycle:

### 1. **Infrastructure Provisioning** ✅
- Creates Azure Resource Group
- Sets up Key Vault for secrets management
- Deploys all Azure resources (App Service, Static Web App)
- Configures networking and security settings

### 2. **Application Deployment** ✅
- Builds and deploys the backend (FastAPI)
- Builds and deploys the frontend (React)
- Configures environment variables and settings
- Sets up CORS between frontend and backend

### 3. **Validation & Verification** ✅
- Health checks for backend API
- Accessibility checks for frontend
- Stores deployment information in Key Vault
- Generates comprehensive deployment summary

## 🚀 How to Use

### Prerequisites

Before running the workflow, ensure you have:

1. **Azure Subscription** with appropriate permissions
2. **GitHub Secrets Configured**:
   - `AZURE_CLIENT_ID` - Azure Service Principal Client ID
   - `AZURE_TENANT_ID` - Azure Tenant ID
   - `AZURE_SUBSCRIPTION_ID` - Azure Subscription ID

> **Note**: The workflow uses **OIDC authentication** (OpenID Connect) which is more secure than traditional credentials.

### Running the Workflow

1. **Navigate to GitHub Actions**:
   - Go to your repository on GitHub
   - Click on the "Actions" tab
   - Select "Complete Azure Setup & Deploy" from the workflow list

2. **Click "Run workflow"**:
   - Choose the branch to deploy from (usually `main`)
   - Fill in the required parameters (see below)
   - Click the green "Run workflow" button

3. **Monitor Progress**:
   - Watch the workflow execution in real-time
   - Each step provides detailed progress indicators
   - Final summary is generated at the end

### Workflow Parameters

| Parameter | Description | Default | Required |
|-----------|-------------|---------|----------|
| **resource_group** | Name of the Azure Resource Group | `hr-portal-rg` | Yes |
| **location** | Azure region for resources | `eastus` | Yes |
| **base_name** | Base name for all resources (lowercase, no special chars) | `hrportal` | Yes |
| **keyvault_name** | Key Vault name (auto-generated if empty) | - | No |
| **app_service_sku** | App Service pricing tier | `B1` | Yes |
| **skip_backend_deploy** | Skip backend deployment | `false` | No |
| **skip_frontend_deploy** | Skip frontend deployment | `false` | No |

### Example Configurations

#### Basic Deployment (Recommended)
```yaml
resource_group: hr-portal-rg
location: eastus
base_name: hrportal
keyvault_name: (leave empty)
app_service_sku: B1
skip_backend_deploy: false
skip_frontend_deploy: false
```

#### Production Deployment
```yaml
resource_group: hr-portal-prod-rg
location: eastus
base_name: hrportalprod
keyvault_name: hrportal-prod-kv
app_service_sku: S1
skip_backend_deploy: false
skip_frontend_deploy: false
```

#### Infrastructure Only (No App Deployment)
```yaml
resource_group: hr-portal-rg
location: westus
base_name: hrportal
keyvault_name: (leave empty)
app_service_sku: B1
skip_backend_deploy: true
skip_frontend_deploy: true
```

## 📋 Workflow Architecture

The workflow is organized into four jobs that run sequentially:

### Job 1: `validate-and-setup`
**Purpose**: Validate inputs and provision Azure infrastructure

**Steps**:
1. ✅ Validate input parameters
2. 🔐 Authenticate with Azure (OIDC)
3. ⚙️ Set up environment variables
4. 🗂️ Create or verify Resource Group
5. 🔐 Create or verify Key Vault
6. 🔑 Store initial secrets in Key Vault
7. 📄 Generate Bicep parameter file
8. 🚀 Deploy infrastructure using Bicep
9. ⚙️ Configure backend application settings

**Outputs**:
- Resource Group name
- Key Vault name
- Backend app name and URL
- Frontend app name and URL
- Deployment ID

### Job 2: `deploy-backend`
**Purpose**: Build and deploy the FastAPI backend

**Steps**:
1. 📥 Checkout code
2. 🔐 Azure authentication
3. 🐍 Set up Python 3.11
4. 📦 Install Python dependencies
5. ✅ Verify application imports
6. 📦 Create deployment package
7. 🚀 Deploy to Azure App Service
8. 🏥 Run health checks

**Conditional**: Skipped if `skip_backend_deploy` is true

### Job 3: `deploy-frontend`
**Purpose**: Build and deploy the React frontend

**Steps**:
1. 📥 Checkout code
2. 🔐 Azure authentication
3. 📦 Retrieve Static Web App deployment token
4. 🔧 Set up Node.js 18
5. 📦 Install npm dependencies
6. 🏗️ Build React application
7. 🚀 Deploy to Azure Static Web Apps
8. 🏥 Verify frontend accessibility

**Conditional**: Skipped if `skip_frontend_deploy` is true or if backend deployment failed (unless backend was skipped)

### Job 4: `verify-deployment`
**Purpose**: Verify deployment and generate summary

**Steps**:
1. 🔐 Azure authentication
2. 📊 Generate comprehensive deployment summary
3. 🔍 Verify Key Vault access
4. 📝 Store deployment information in Key Vault

**Always runs** (even if previous jobs partially failed) as long as infrastructure was set up

## 🔐 Security Features

### Authentication
- Uses **OIDC (OpenID Connect)** for Azure authentication
- No long-lived credentials stored in GitHub
- Short-lived tokens issued per workflow run

### Secrets Management
- All deployment secrets stored in Azure Key Vault
- GitHub Secrets only store authentication credentials
- Deployment tokens retrieved dynamically

### Resource Security
- All resources tagged with deployment metadata
- HTTPS enforced for all endpoints
- TLS 1.2+ required for all connections
- Key Vault access controlled via Azure RBAC

## 📊 Output and Reporting

### Deployment Summary

After successful deployment, the workflow generates a comprehensive summary including:

- ✅ Status of each component (Resource Group, Key Vault, Backend, Frontend)
- 🔗 Access URLs for all deployed services
- 🔐 Azure resource information
- 🎯 Next steps for verification

### Example Summary Output

```markdown
# 🎉 Deployment Summary

## 📋 Deployment Details

| Component | Status |
|-----------|--------|
| Resource Group | ✅ Created |
| Key Vault | ✅ Created |
| Infrastructure | ✅ Deployed |
| Backend | ✅ Deployed |
| Frontend | ✅ Deployed |

## 🔗 Access URLs

- **Backend API**: https://hrportal-api-123456.azurewebsites.net
- **Backend Health**: https://hrportal-api-123456.azurewebsites.net/health
- **API Docs**: https://hrportal-api-123456.azurewebsites.net/docs
- **Frontend**: https://hrportal-web-123456.azurestaticapps.net

## 🔐 Azure Resources

- **Resource Group**: hr-portal-rg
- **Key Vault**: hrportalkv123456
- **Location**: eastus
- **Deployment ID**: deploy-20260201-174500

## 🎯 Next Steps

1. ✅ Test the backend health endpoint
2. ✅ Access the frontend application
3. ✅ Review the API documentation
4. ✅ Monitor application logs in Azure Portal
```

## 🔧 Troubleshooting

### Common Issues and Solutions

#### Issue: Workflow fails with "Resource Group already exists"
**Solution**: This is expected behavior. The workflow checks for existing resources and uses them if available. This is not an error.

#### Issue: Key Vault name conflict
**Solution**: 
- Either delete the existing Key Vault with the same name
- Or provide a different `keyvault_name` parameter
- Or leave `keyvault_name` empty to auto-generate a unique name

#### Issue: Backend health check fails
**Solution**: 
- Wait 2-3 minutes for the backend to fully start
- Check backend logs in Azure Portal: App Services → Your App → Log stream
- Verify the startup.sh script is configured correctly

#### Issue: Frontend shows "Cannot connect to backend"
**Solution**:
- Verify CORS is configured correctly in backend settings
- Check that `REACT_APP_API_URL` is set to the correct backend URL
- Ensure backend is healthy and responding

#### Issue: OIDC authentication fails
**Solution**:
- Verify GitHub secrets are set correctly:
  - `AZURE_CLIENT_ID`
  - `AZURE_TENANT_ID`
  - `AZURE_SUBSCRIPTION_ID`
- Ensure the Service Principal has appropriate permissions
- Check that federated credentials are configured for GitHub Actions

### Debug Mode

To enable detailed debugging:

1. Go to your repository Settings
2. Navigate to Secrets and variables → Actions
3. Add a new secret: `ACTIONS_STEP_DEBUG` with value `true`
4. Re-run the workflow

This will show detailed logs for each step.

## 🎓 Best Practices

### For Non-Technical Users

1. **Use Default Values**: The default parameters are optimized for most use cases
2. **Start with B1 SKU**: Begin with the basic tier and upgrade if needed
3. **Monitor Costs**: Use Azure Cost Management to track spending
4. **Save URLs**: Bookmark the deployment summary for future reference

### For Technical Users

1. **Use Descriptive Names**: Choose meaningful names for resource groups
2. **Tag Resources**: The workflow automatically tags resources with deployment metadata
3. **Version Control**: Keep Bicep templates in source control
4. **Regular Deployments**: Run the workflow regularly to ensure reproducibility
5. **Review Logs**: Check Azure Application Insights for application logs

## 🔄 Rollback and Recovery

### If Deployment Fails

The workflow is designed to be **idempotent**, meaning you can safely re-run it:

1. **Identify the Failed Step**: Check the workflow logs
2. **Fix the Issue**: Address the root cause
3. **Re-run the Workflow**: Simply run the workflow again with the same parameters

### Manual Rollback

If you need to rollback:

1. Delete the Resource Group:
   ```bash
   az group delete --name hr-portal-rg --yes
   ```

2. Re-run the workflow with corrected parameters

### Key Vault Recovery

If you accidentally delete the Key Vault, you can recover it within 90 days:

```bash
az keyvault recover --name hrportalkv123456
```

## 📈 Performance Considerations

### Deployment Time

Typical deployment times:

- **Infrastructure Setup**: 2-3 minutes
- **Backend Deployment**: 2-4 minutes
- **Frontend Deployment**: 3-5 minutes
- **Total**: 7-12 minutes

### Resource Costs

Estimated monthly costs (as of 2026):

- **App Service B1**: ~$13/month
- **Static Web Apps (Free tier)**: $0/month
- **Key Vault**: ~$0.03/month
- **Total**: ~$13/month

> Costs may vary by region and usage. Use Azure Cost Calculator for accurate estimates.

## 🤝 Integration with Existing Workflows

This workflow is designed to be standalone but can integrate with:

- **backend-deploy.yml**: For backend-only updates
- **frontend-deploy.yml**: For frontend-only updates
- **CI/CD pipelines**: Trigger after successful builds

## 📚 Additional Resources

- [Azure Bicep Documentation](https://docs.microsoft.com/azure/azure-resource-manager/bicep/)
- [GitHub Actions OIDC](https://docs.github.com/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect)
- [Azure Key Vault Best Practices](https://docs.microsoft.com/azure/key-vault/general/best-practices)
- [Azure App Service Documentation](https://docs.microsoft.com/azure/app-service/)
- [Azure Static Web Apps Documentation](https://docs.microsoft.com/azure/static-web-apps/)

## 🆘 Support

If you encounter issues:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review the workflow logs in GitHub Actions
3. Check Azure Portal for resource status
4. Open an issue in the repository with:
   - Workflow run URL
   - Error messages
   - Expected vs actual behavior

---

**Last Updated**: February 2026  
**Workflow Version**: 1.0.0  
**Maintained By**: DevOps Team
