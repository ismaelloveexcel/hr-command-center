# Azure Deploy Autopilot (Skill)

Purpose:
- Deploy the current repository to Azure with minimal user input.

Process:
1. Detect app type (Static Web App, App Service, Node, React, Vite, Next).
2. Select Azure target (Static Web Apps for frontend-only, App Service for backend/SSR).
3. Configure GitHub Actions with Azure OIDC authentication.
4. Create missing Azure resources if required.
5. Create or fix workflows and repair failed deployments.
6. Validate build output, env vars, and runtime health.

Constraints:
- Do not ask questions unless credentials or subscription access is missing.
- Never leave the deployment half-done.

Output:
- Deployment URL
- Fixes applied
- Remaining risks (if any)
