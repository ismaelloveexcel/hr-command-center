// UAE HR Portal - Azure Infrastructure
// Deploy with: az deployment group create -g hr-portal-rg -f main.bicep

@description('Base name for all resources')
param baseName string = 'hrportal'

@description('Azure region for resources')
param location string = resourceGroup().location

@description('App Service SKU')
@allowed(['B1', 'B2', 'S1', 'P1V2'])
param appServiceSku string = 'B1'

@description('Frontend URL for CORS configuration')
param frontendUrl string = ''

// Variables
var appServicePlanName = '${baseName}-plan'
var backendAppName = '${baseName}-api-${uniqueString(resourceGroup().id)}'
var staticWebAppName = '${baseName}-web-${uniqueString(resourceGroup().id)}'

// App Service Plan (Linux)
resource appServicePlan 'Microsoft.Web/serverfarms@2022-09-01' = {
  name: appServicePlanName
  location: location
  kind: 'linux'
  sku: {
    name: appServiceSku
    capacity: 1
  }
  properties: {
    reserved: true
  }
}

// Backend Web App (FastAPI)
resource backendApp 'Microsoft.Web/sites@2022-09-01' = {
  name: backendAppName
  location: location
  properties: {
    serverFarmId: appServicePlan.id
    httpsOnly: true
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.11'
      appCommandLine: 'bash startup.sh'
      alwaysOn: appServiceSku != 'B1'
      http20Enabled: true
      minTlsVersion: '1.2'
      appSettings: [
        {
          name: 'DATABASE_URL'
          value: 'sqlite:///./hr_portal.db'
        }
        {
          name: 'CORS_ORIGINS'
          value: frontendUrl != '' ? frontendUrl : 'http://localhost:3000'
        }
        {
          name: 'SCM_DO_BUILD_DURING_DEPLOYMENT'
          value: 'true'
        }
      ]
    }
  }
}

// Static Web App (React Frontend)
resource staticWebApp 'Microsoft.Web/staticSites@2022-09-01' = {
  name: staticWebAppName
  location: location
  sku: {
    name: 'Free'
    tier: 'Free'
  }
  properties: {
    buildProperties: {
      appLocation: '/frontend'
      outputLocation: 'build'
    }
  }
}

// Outputs for GitHub Actions configuration
output backendAppName string = backendApp.name
output backendUrl string = 'https://${backendApp.properties.defaultHostName}'
output staticWebAppName string = staticWebApp.name
output staticWebAppUrl string = 'https://${staticWebApp.properties.defaultHostname}'
output resourceGroupName string = resourceGroup().name

// Instructions output
output nextSteps string = '''
Next steps:
1. Get backend publish profile: az webapp deployment list-publishing-profiles -n ${backendAppName} -g ${resourceGroupName}
2. Get Static Web App token: az staticwebapp secrets list -n ${staticWebAppName} -g ${resourceGroupName}
3. Add these as GitHub secrets
4. Push to main branch to trigger deployment
'''
