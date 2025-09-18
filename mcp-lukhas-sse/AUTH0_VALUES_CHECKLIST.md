# 📋 Auth0 Configuration Checklist

## Required Values from Auth0 Dashboard

### From your API settings:
- **API Identifier**: Copy this from Applications → APIs → LUKHAS MCP API
- **Tenant Domain**: Your tenant URL (e.g., lukhas-ai.auth0.com)

### From your Machine-to-Machine App:
- **Client ID**: Found in Applications → LUKHAS MCP Client → Settings
- **Client Secret**: Found in Applications → LUKHAS MCP Client → Settings

## Copy these into your .env file:

```bash
# Auth0 Configuration
OAUTH_ISSUER=https://YOUR-TENANT.auth0.com/.well-known/openid-configuration
OAUTH_AUDIENCE=https://api.lukhas.ai  # Your API Identifier
PUBLIC_BASE_URL=http://localhost:8080

# LUKHAS MCP Settings
LUKHAS_MCP_ROOTS=/Users/agi_dev/LOCAL-REPOS/Lukhas
WRITE_ENABLED=false
```

## Test Token Generation

You can get a test JWT token from:
Auth0 Dashboard → Applications → APIs → LUKHAS MCP API → Test tab

Save the test JWT token - you'll need it to test the server!