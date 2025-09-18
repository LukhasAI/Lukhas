# Auth0 OAuth Configuration for ChatGPT Integration

## Step 1: Create Auth0 Account
1. Go to https://auth0.com and sign up
2. Create a new tenant (e.g., "lukhas-ai")

## Step 2: Create API (Current Auth0 Interface)
**Option A: From Get Started Page**
1. Go to https://auth0.com/docs/get-started
2. Click "Backend/API" - "An API or service protected by Auth0"
3. Follow the quickstart to create your API

**Option B: From Dashboard**
1. Go to Applications → APIs in Auth0 Dashboard
2. Click "Create API"
3. Fill in:
   - Name: "LUKHAS MCP API"
   - Identifier: `https://api.lukhas.ai` (use your domain)
   - Signing Algorithm: RS256

## Step 3: Create Machine-to-Machine Application
1. Go to Applications
2. Click "Create Application"
3. Choose "Machine to Machine Applications"
4. Name: "ChatGPT MCP Client"
5. Select your API
6. Grant required scopes

## Step 4: Configure Environment
```bash
# Replace these with your Auth0 values:
OAUTH_ISSUER=https://your-tenant.auth0.com/.well-known/openid-configuration
OAUTH_AUDIENCE=https://api.lukhas.ai
PUBLIC_BASE_URL=http://localhost:8080

# Your filesystem access
LUKHAS_MCP_ROOTS=/Users/agi_dev/LOCAL-REPOS/Lukhas
WRITE_ENABLED=false
```

## Step 5: Get Test Token
Use Auth0's Test tab in your API to get a JWT token for testing.

## Step 6: Test Integration
```bash
# Start server
python server.py

# Test with Auth0 JWT
curl -H "Authorization: Bearer <auth0-jwt>" http://localhost:8080/sse/
```

## ChatGPT Plugin Configuration
```json
{
  "schema_version": "v1",
  "name_for_human": "LUKHAS MCP",
  "name_for_model": "lukhas_mcp",
  "description_for_human": "Access LUKHAS filesystem via MCP",
  "description_for_model": "OAuth-secured Model Context Protocol server for LUKHAS AI filesystem access",
  "auth": {
    "type": "oauth",
    "oauth_client_id": "your-auth0-client-id",
    "authorization_url": "https://your-tenant.auth0.com/authorize",
    "scope": "read:files write:files"
  },
  "api": {
    "type": "mcp",
    "url": "http://localhost:8080/sse/"
  }
}
```

## Security Benefits
- ✅ Industry-standard OAuth 2.1
- ✅ JWT token validation
- ✅ Automatic token refresh
- ✅ Rate limiting and abuse protection
- ✅ Audit logs and monitoring
- ✅ Multi-factor authentication support