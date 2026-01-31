# Secrets Management Guide

This document provides guidance on how to manage secrets and environment variables for the UAE HR Portal project.

## Local Development

### Backend (.env file)

1. Copy the `.env.example` file in the `backend/` directory to `.env`
2. Update the values with your local configuration
3. **Never commit the `.env` file to git** - it contains sensitive credentials

Example:
```bash
cd backend
cp .env.example .env
# Edit .env with your actual values
```

### Frontend (.env file)

1. Copy the `.env.example` file in the `frontend/` directory to `.env`
2. Update the API URL if needed (defaults to `http://localhost:8000`)

Example:
```bash
cd frontend
cp .env.example .env
# Edit .env with your actual values
```

## GitHub Actions Secrets

For CI/CD pipelines using GitHub Actions, secrets should be configured in the repository settings:

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add the following secrets as needed:

### Required Secrets for GitHub Actions

- `DATABASE_URL` - PostgreSQL connection string for staging/production
- `AZURE_SECRET_KEY` - Azure service principal secret
- `AZURE_TENANT_ID` - Azure tenant ID
- `AZURE_CLIENT_ID` - Azure client ID
- `TWILIO_ACCOUNT_SID` - Twilio account SID for SMS
- `TWILIO_AUTH_TOKEN` - Twilio authentication token
- `TWILIO_PHONE_NUMBER` - Twilio phone number
- `SECRET_KEY` - Application secret key for JWT/sessions

### Using Secrets in Workflows

Reference secrets in your GitHub Actions workflow files like this:

```yaml
- name: Deploy Backend
  env:
    DATABASE_URL: ${{ secrets.DATABASE_URL }}
    AZURE_SECRET_KEY: ${{ secrets.AZURE_SECRET_KEY }}
    TWILIO_ACCOUNT_SID: ${{ secrets.TWILIO_ACCOUNT_SID }}
```

## Azure Deployment

For deploying to Azure, secrets can be managed in several ways:

### Option 1: Azure Key Vault (Recommended)

1. Create an Azure Key Vault in your resource group
2. Add secrets to Key Vault through Azure Portal or CLI:
   ```bash
   az keyvault secret set --vault-name <your-vault-name> --name DATABASE-URL --value "<your-db-url>"
   az keyvault secret set --vault-name <your-vault-name> --name TWILIO-ACCOUNT-SID --value "<your-sid>"
   ```
3. Configure your App Service to reference Key Vault secrets:
   - In Azure Portal, go to your App Service
   - Navigate to **Configuration** → **Application settings**
   - Add references like: `@Microsoft.KeyVault(SecretUri=https://<vault-name>.vault.azure.net/secrets/DATABASE-URL/)`

### Option 2: Azure App Service Configuration

1. Go to Azure Portal
2. Navigate to your **App Service**
3. Go to **Configuration** → **Application settings**
4. Add environment variables:
   - Name: `DATABASE_URL`, Value: `<your-database-connection-string>`
   - Name: `AZURE_SECRET_KEY`, Value: `<your-azure-secret>`
   - Name: `TWILIO_ACCOUNT_SID`, Value: `<your-twilio-sid>`
   - etc.
5. Click **Save**

**Note**: App Service configuration is automatically injected as environment variables at runtime.

### Option 3: Azure DevOps Variable Groups

If using Azure DevOps for CI/CD:

1. Go to **Pipelines** → **Library**
2. Create a **Variable group** (e.g., "HR-Portal-Secrets")
3. Add variables and mark sensitive ones as "secret"
4. Link the variable group in your pipeline YAML:
   ```yaml
   variables:
   - group: HR-Portal-Secrets
   ```

## Security Best Practices

1. **Never commit secrets to git** - Use `.gitignore` to exclude `.env` files
2. **Rotate secrets regularly** - Especially for production environments
3. **Use different secrets for each environment** - Development, staging, and production should have separate credentials
4. **Limit access** - Only grant secret access to team members who need it
5. **Use Azure Key Vault for production** - It provides better security, audit logging, and access control
6. **Monitor secret usage** - Enable logging and alerts for secret access

## Environment-Specific Configuration

### Development
- Use SQLite database (default)
- Use stub implementations for Twilio/email (no real API calls)
- Set `DEBUG=true` for verbose logging

### Staging
- Use PostgreSQL database
- Use test Twilio credentials
- Set `DEBUG=false`

### Production
- Use PostgreSQL database with connection pooling
- Use production Twilio credentials
- Set `DEBUG=false`
- Enable all security features
- Use HTTPS only

## Troubleshooting

### Backend not loading .env file
- Ensure `.env` file is in the `backend/` directory (same level as `main.py`)
- Check file permissions
- Verify `pydantic-settings` is installed: `pip install pydantic-settings`

### Frontend not using environment variables
- Ensure variable names start with `REACT_APP_`
- Restart the development server after changing `.env`
- Clear browser cache if needed

### Azure deployment not using secrets
- Check App Service logs: `az webapp log tail --name <app-name> --resource-group <rg-name>`
- Verify secrets are set in App Service Configuration
- Restart the App Service after adding/updating secrets
