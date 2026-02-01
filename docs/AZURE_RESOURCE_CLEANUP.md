# 🧹 Azure Resource Cleanup Guide

## Understanding Redundant Resources

When testing deployments or running the workflow multiple times, Azure resources can accumulate. This guide helps you identify and clean up redundant resources to avoid unnecessary costs.

## 📊 What You're Seeing

Based on your Azure Portal screenshots, you have multiple resources that appear to be duplicates or from different deployment attempts:

**Resource Groups:**
- `HR-PORTAL`
- `baynunah-hr-portal-rg`
- Multiple resource groups with similar names

**App Services:**
- `uae-hr-portal-api`
- `baynunah-hr-portal`
- `hrportal-backend-new`
- `hrportal-backend-fix`
- `hrportal-backend-ai`

**Static Web Apps:**
- `hrportal-frontend-new`

## 🎯 Why This Happens

1. **Multiple Test Runs**: Each time you run a deployment workflow or script, it may create new resources
2. **Different Naming Schemes**: Different deployment methods use different naming conventions
3. **Failed Deployments**: Partial deployments may leave resources behind
4. **Manual Testing**: Resources created during manual Azure Portal testing

## 🧹 How to Clean Up

### Option 1: Delete Entire Resource Groups (Recommended)

This is the **fastest and safest** way to clean up everything at once.

#### Step 1: Identify Which Resource Groups to Keep

You should keep **ONE** resource group with your production deployment. Based on the naming pattern in the new workflow, you probably want to keep:
- `hr-portal-rg` (if you're using default settings)
- OR your custom-named resource group

#### Step 2: Delete Redundant Resource Groups

**Via Azure Portal:**
1. Go to [Azure Portal](https://portal.azure.com)
2. Search for "Resource groups"
3. For each resource group you want to delete:
   - Click on the resource group name
   - Click "Delete resource group" at the top
   - Type the resource group name to confirm
   - Click "Delete"

**Via Azure CLI:**
```bash
# List all resource groups
az group list --output table

# Delete a specific resource group (WARNING: This deletes ALL resources in it!)
az group delete --name "resource-group-name" --yes --no-wait

# Example: Delete old test resource groups
az group delete --name "baynunah-hr-portal-rg" --yes --no-wait
az group delete --name "hrportal-backend-fix_group" --yes --no-wait
```

### Option 2: Delete Individual Resources

If you want to keep some resources in a resource group but delete others:

**Via Azure Portal:**
1. Go to Resource Manager → Recent resources
2. Select the resources you want to delete (use checkboxes)
3. Click "Delete" at the top
4. Confirm deletion

**Via Azure CLI:**
```bash
# Delete a specific App Service
az webapp delete --name "app-name" --resource-group "resource-group-name"

# Delete a Static Web App
az staticwebapp delete --name "app-name" --resource-group "resource-group-name"

# Delete an App Service Plan
az appservice plan delete --name "plan-name" --resource-group "resource-group-name"
```

## 🎯 Recommended Cleanup Strategy

Based on your screenshots, here's what I recommend:

### Step 1: Identify Your Current Production Setup

Determine which resources are currently serving your live application:
1. Check which backend URL is in your GitHub secrets (`REACT_APP_API_URL`)
2. Check which frontend URL users are accessing
3. Note the resource group name containing these resources

### Step 2: Clean Up Old Test Resources

Delete resource groups that contain:
- Resources with "test", "fix", "new", "old" in their names
- Resources that haven't been accessed recently (check "Last accessed" column)
- Duplicate resources you're not using

**Example cleanup for your case:**

```bash
# These appear to be old test/development resources based on your screenshots:

# Delete old test deployments
az group delete --name "baynunah-hr-portal-rg" --yes --no-wait
az group delete --name "hrportal-backend-fix_group" --yes --no-wait
az group delete --name "hrportal-backend-new_group" --yes --no-wait

# Note: Replace with actual resource group names from your portal
```

### Step 3: Use the New Workflow for Fresh Deployment

Once you've cleaned up, use the new comprehensive workflow to create a clean deployment:

1. Go to Actions → "Complete Azure Setup & Deploy"
2. Click "Run workflow"
3. Use these settings:
   ```yaml
   resource_group: hr-portal-rg
   location: eastus (or your preferred region)
   base_name: hrportal
   app_service_sku: B1 (or higher for production)
   ```
4. This will create ONE set of resources with consistent naming

## 🛡️ Preventing Future Redundancy

### 1. Use Consistent Naming

Stick to ONE deployment method:
- ✅ **Recommended**: Use the "Complete Azure Setup & Deploy" workflow
- ✅ Keep the same resource group name
- ✅ Use the same base name

### 2. Update, Don't Recreate

After initial deployment, use update workflows:
- For backend changes: Use `backend-deploy.yml`
- For frontend changes: Use `frontend-deploy.yml`
- For infrastructure changes: Re-run the complete workflow with **same resource group name**

### 3. Understand Workflow Behavior

The new workflow is **idempotent**, meaning:
- ✅ Running it again with the same resource group name will **update** existing resources
- ✅ It won't create duplicates if you use the same parameters
- ❌ Using different resource group names will create new resources

### 4. Set Up Resource Tagging

The new workflow automatically tags resources with:
- `Environment=Production`
- `Project=HR-Portal`
- `ManagedBy=GitHub-Actions`
- `DeploymentId=unique-id`

Use these tags to identify which resources belong to which deployment.

## 📊 Cost Impact

Redundant resources cost money! Here's an example of what you might be paying for unnecessarily:

| Resource Type | Approximate Cost/Month | Example: Redundant Count | Example: Unnecessary Cost |
|---------------|------------------------|--------------------------|---------------------------|
| App Service (B1) | $13 | 5-6 | ~$65-78/month |
| Static Web App (Free) | $0 | Multiple | $0 |
| App Service Plans | $13 each | 3-4 | ~$39-52/month |
| Azure Database | $5-50 | 1-2 | ~$5-100/month |

**Example potential savings by cleanup: $100-200/month** 💰

> **Note**: Cost estimates are approximate and based on standard pricing. Actual costs may vary based on region, usage, and current Azure pricing. Check the [Azure Pricing Calculator](https://azure.microsoft.com/pricing/calculator/) for current rates. The counts shown are example scenarios and may differ from your actual resources.

## ✅ Post-Cleanup Checklist

After cleaning up, verify your production setup:

- [ ] One resource group with your production resources
- [ ] One backend App Service
- [ ] One frontend Static Web App
- [ ] One App Service Plan
- [ ] GitHub secrets point to the correct URLs
- [ ] Application is accessible and working
- [ ] No unnecessary resources in Azure Portal

## 🆘 If Something Goes Wrong

### If You Accidentally Delete Production Resources

Don't panic! Azure keeps deleted resources for recovery:

1. **Key Vault Recovery** (90 days):
   ```bash
   az keyvault list-deleted
   az keyvault recover --name "vault-name"
   ```

2. **Redeploy from GitHub**:
   - The workflow is idempotent
   - All infrastructure is defined in code
   - Just run the workflow again

3. **Restore from Backup** (if configured):
   - Check Azure Backup
   - Restore database if applicable

### If You're Unsure What to Delete

**Safe approach:**
1. Export a list of all resources:
   ```bash
   az resource list --output table > azure-resources-backup.txt
   ```
2. Take screenshots of current setup
3. Start by deleting obviously old resources (with "test", "old", "fix" in names)
4. Test your application after each deletion
5. Keep the "Complete Azure Setup & Deploy" workflow ready to redeploy if needed

## 🎓 Best Practices Going Forward

1. **One Environment, One Resource Group**
   - Production: `hr-portal-rg`
   - Staging: `hr-portal-staging-rg` (if needed)
   - Development: `hr-portal-dev-rg` (if needed)

2. **Use the Workflow for All Deployments**
   - Infrastructure changes: Complete workflow
   - Code updates: Specific deployment workflows

3. **Regular Cleanup**
   - Monthly: Review Azure resources
   - Remove any test/dev resources no longer needed
   - Check cost analysis in Azure Portal

4. **Monitor Costs**
   - Set up Azure cost alerts
   - Review monthly bills
   - Use Azure Cost Management

## 📚 Additional Resources

- [Azure Resource Management Documentation](https://docs.microsoft.com/azure/azure-resource-manager/)
- [Azure Cost Management Best Practices](https://docs.microsoft.com/azure/cost-management-billing/costs/)
- [Azure Resource Naming Conventions](https://docs.microsoft.com/azure/cloud-adoption-framework/ready/azure-best-practices/naming-and-tagging)

---

**Need help with cleanup?** Reply to this PR with:
- Which resources you want to keep
- Your production resource group name
- Any concerns about deletion

I can provide specific commands for your situation! 🚀
