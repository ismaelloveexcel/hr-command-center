# Security Configuration Guide

This document outlines the security features implemented in the HR Portal and how to configure them properly.

## Security Features

### 1. Security Headers

The application automatically adds security headers to all responses to protect against common web vulnerabilities:

- **X-Content-Type-Options: nosniff** - Prevents MIME type sniffing
- **X-Frame-Options: DENY** - Prevents clickjacking attacks
- **X-XSS-Protection: 1; mode=block** - Enables XSS protection in legacy browsers
- **Strict-Transport-Security** - Enforces HTTPS (production only)
- **Content-Security-Policy** - Controls which resources can be loaded

These headers are applied automatically via the `SecurityHeadersMiddleware` in `backend/app/core/security_middleware.py`.

### 2. CORS Configuration

CORS (Cross-Origin Resource Sharing) is configured to allow specific origins only:

```bash
# Development
CORS_ORIGINS=http://localhost:3000

# Production (use specific domains, not wildcards)
CORS_ORIGINS=https://myapp.azurewebsites.net,https://mydomain.com
```

**Important:** Never use wildcard (`*`) with `allow_credentials=True` as this is a security risk.

### 3. Rate Limiting

Rate limiting protects against abuse and DDoS attacks:

| Endpoint | Limit | Purpose |
|----------|-------|---------|
| POST /requests | 10/hour | Prevent spam submissions |
| GET /requests/{ref} | 30/minute | Allow reasonable tracking |
| PATCH /requests/{ref}/status | 100/minute | HR staff updates |
| GET /hr/requests | 100/minute | HR dashboard |
| GET /hr/stats | 60/minute | Dashboard statistics |

Rate limits are enforced per IP address using the `slowapi` library.

### 4. Input Validation & Sanitization

All user input is validated and sanitized to prevent XSS attacks:

- **Field Length Limits**: Enforced at the schema level
  - Title: max 200 characters
  - Description: max 2000 characters
  - Notes: max 1000-2000 characters
  
- **HTML Sanitization**: All text fields are stripped of HTML tags using `bleach`
- **Status Validation**: Only allowed status values are accepted
- **Minimum Length**: Required fields must have at least 1 character

Sanitization is implemented in `backend/app/core/validation.py` and applied via Pydantic validators.

### 5. API Key Authentication

HR endpoints require authentication via API key:

```bash
# Generate a strong random key (example using Python)
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Set in environment
HR_API_KEY=your-generated-key-here
```

**Required for these endpoints:**
- `PATCH /requests/{ref}/status`
- `GET /hr/requests`
- `GET /hr/stats`

Include the key in requests:
```bash
curl -H "X-HR-API-Key: your-key-here" https://api.example.com/hr/requests
```

### 6. Environment Validation

The application validates configuration on startup:

- ⚠️ Warns if `HR_API_KEY` is not set
- ⚠️ Warns if using SQLite in production
- ⚠️ Errors if CORS uses wildcard with credentials
- ✅ Logs security configuration status

## Production Deployment Checklist

### Required Configuration

- [ ] Set `DEBUG=false`
- [ ] Configure `HR_API_KEY` with a strong random value
- [ ] Set `CORS_ORIGINS` to specific domain(s) (no wildcards)
- [ ] Use PostgreSQL instead of SQLite (see Database Migration section)
- [ ] Configure `TRUSTED_HOSTS` with your domain(s)
- [ ] Set `SECRET_KEY` for future JWT/session features
- [ ] Use HTTPS for all production traffic

### Recommended Configuration

- [ ] Enable Azure Application Insights for monitoring
- [ ] Configure backup strategy for database
- [ ] Set up log aggregation and alerting
- [ ] Implement Azure Key Vault for secrets management
- [ ] Configure Azure AD for authentication (future enhancement)
- [ ] Set up staging environment for testing

## Database Migration: SQLite to PostgreSQL

SQLite is not recommended for production due to:
- Limited concurrency
- Data loss on container restart (ephemeral storage)
- No built-in replication or backup

### Azure PostgreSQL Setup

1. **Create Azure Database for PostgreSQL**
   ```bash
   az postgres flexible-server create \
     --resource-group myResourceGroup \
     --name myhrportaldb \
     --location eastus \
     --admin-user myadmin \
     --admin-password <strong-password> \
     --sku-name Standard_B1ms \
     --tier Burstable \
     --version 14
   ```

2. **Configure Firewall**
   ```bash
   # Allow Azure services
   az postgres flexible-server firewall-rule create \
     --resource-group myResourceGroup \
     --name myhrportaldb \
     --rule-name AllowAzureServices \
     --start-ip-address 0.0.0.0 \
     --end-ip-address 0.0.0.0
   ```

3. **Update Connection String**
   ```bash
   DATABASE_URL=postgresql://myadmin:password@myhrportaldb.postgres.database.azure.com:5432/hr_portal?sslmode=require
   ```

4. **Run Migrations**
   ```bash
   cd backend
   alembic upgrade head
   ```

### Local PostgreSQL Testing

For local testing with PostgreSQL:

```bash
# Using Docker
docker run --name hr-postgres \
  -e POSTGRES_PASSWORD=localpass \
  -e POSTGRES_DB=hr_portal \
  -p 5432:5432 \
  -d postgres:14

# Update .env
DATABASE_URL=postgresql://postgres:localpass@localhost:5432/hr_portal

# Run migrations
cd backend
alembic upgrade head
```

## Rate Limiting Configuration

Rate limits can be adjusted in the router files if needed:

```python
# Adjust limits in backend/app/routers/requests.py
@router.post("", ...)
@limiter.limit("10/hour")  # Change to "20/hour" if needed
```

After changing limits, restart the application for changes to take effect.

## Monitoring Security

### Application Logs

Monitor logs for security events:
- Rate limit violations
- Invalid API key attempts
- Configuration warnings on startup

### Azure Application Insights (Recommended)

Configure Application Insights for production monitoring:

```bash
# Install SDK
pip install applicationinsights

# Add to main.py
from applicationinsights import TelemetryClient
tc = TelemetryClient('<instrumentation-key>')
```

## Future Security Enhancements

Planned security improvements:

1. **Azure AD Integration**: Replace API key with OAuth 2.0/JWT authentication
2. **Role-Based Access Control (RBAC)**: Fine-grained permissions for HR staff
3. **Audit Logging**: Track all data modifications
4. **Two-Factor Authentication**: Add MFA for HR staff
5. **API Versioning**: Support multiple API versions
6. **GraphQL**: Consider GraphQL for more flexible queries with built-in security

## Security Contact

For security vulnerabilities or concerns:

**Before Deployment**: Update this section with your organization's actual security contact information.

Recommended options:
- Create a private security advisory on GitHub (Settings → Security → Advisories)
- Email: security@yourcompany.ae (replace with actual email)
- Security team: Contact your IT security team directly

**Note**: Never commit sensitive contact information or security keys to the repository.

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security Documentation](https://fastapi.tiangolo.com/tutorial/security/)
- [Azure Security Best Practices](https://docs.microsoft.com/en-us/azure/security/fundamentals/best-practices-and-patterns)
