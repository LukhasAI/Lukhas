---
status: wip
type: documentation
---
# 🚀 MCP FileSystem Server Ultimate - OAuth Protected

**Comprehensive AI Development Toolkit for ChatGPT-5** with enterprise-grade OAuth authentication.

## 🔐 OAuth Authentication Support

Supports **Auth0**, **Keycloak**, and **Cloudflare Access** with JWT verification.

### 🛡️ Security Features
- **JWT Token Verification** with JWKS endpoint validation  
- **Scope-based Authorization** (configurable required scopes)
- **Provider Flexibility** (Auth0, Keycloak, Cloudflare Access)
- **Rate Limiting** + **Audit Logging** + **Path Traversal Protection**
- **Credential Redaction** (AWS keys, GitHub tokens, API keys)

## 🔧 OAuth Configuration

### Environment Variables

```bash
# OAuth Configuration (all required)
OAUTH_PROVIDER=auth0          # or 'keycloak' or 'cloudflare'
OAUTH_JWKS_URL=https://your-domain.auth0.com/.well-known/jwks.json
OAUTH_ISSUER=https://your-domain.auth0.com/
OAUTH_AUDIENCE=https://api.lukhas.dev
OAUTH_CLIENT_ID=your-client-id
OAUTH_REQUIRED_SCOPES=read:files,write:files,execute:commands
OAUTH_CACHE_TTL=300000        # JWT cache TTL in ms (optional)

# MCP Server Configuration  
MCP_FS_ROOT=/Users/agi_dev/LOCAL-REPOS/Lukhas
MCP_MAX_BYTES=2097152
```

### Provider-Specific Setup

#### 🔵 **Auth0 Setup**
1. **Create Auth0 Application:**
   - Go to Auth0 Dashboard → Applications → Create Application
   - Choose "Machine to Machine" (for Client Credentials) or "Single Page Application" (for Auth Code)
   - Note your Domain, Client ID, Client Secret

2. **Configure API:**
   - Go to APIs → Create API  
   - Identifier: `https://api.lukhas.dev` (use as AUDIENCE)
   - Define scopes: `read:files`, `write:files`, `execute:commands`

3. **Environment Variables:**
   ```bash
   OAUTH_PROVIDER=auth0
   OAUTH_JWKS_URL=https://your-domain.auth0.com/.well-known/jwks.json
   OAUTH_ISSUER=https://your-domain.auth0.com/
   OAUTH_AUDIENCE=https://api.lukhas.dev
   OAUTH_CLIENT_ID=your-client-id
   OAUTH_REQUIRED_SCOPES=read:files,write:files,execute:commands
   ```

#### 🔵 **Keycloak Setup**
1. **Create Keycloak Client:**
   - Admin Console → Realm → Clients → Create
   - Client Type: OpenID Connect
   - Client authentication: ON (for confidential clients)

2. **Configure Client Scopes:**
   - Create custom scopes: `files:read`, `files:write`, `commands:execute`
   - Assign to client

3. **Environment Variables:**
   ```bash
   OAUTH_PROVIDER=keycloak
   OAUTH_JWKS_URL=https://keycloak.yourdomain.com/realms/lukhas/protocol/openid-connect/certs
   OAUTH_ISSUER=https://keycloak.yourdomain.com/realms/lukhas
   OAUTH_AUDIENCE=mcp-fs-lukhas
   OAUTH_CLIENT_ID=mcp-fs-lukhas
   OAUTH_REQUIRED_SCOPES=files:read,files:write,commands:execute
   ```

#### 🔵 **Cloudflare Access Setup**
1. **Create Cloudflare Access Application:**
   - Cloudflare Dashboard → Zero Trust → Access → Applications → Add Application
   - Choose "API" type
   - Set policies for who can access

2. **Environment Variables:**
   ```bash
   OAUTH_PROVIDER=cloudflare
   OAUTH_JWKS_URL=https://your-account.cloudflareaccess.com/cdn-cgi/access/certs
   OAUTH_ISSUER=https://your-account.cloudflareaccess.com
   OAUTH_AUDIENCE=your-application-aud
   OAUTH_REQUIRED_SCOPES=read,write,execute
   ```

## 🔌 ChatGPT Integration with OAuth

### Option 1: Client Credentials Flow (Recommended)

**Best for server-to-server communication:**

1. **Get Access Token:**
   ```bash
   curl -X POST https://your-domain.auth0.com/oauth/token \
     -H "Content-Type: application/json" \
     -d '{
       "client_id": "your-client-id",
       "client_secret": "your-client-secret", 
       "audience": "https://api.lukhas.dev",
       "grant_type": "client_credentials"
     }'
   ```

2. **ChatGPT Custom Connector Setup:**
   - **Connection Type:** HTTP with Authentication
   - **Authentication:** Bearer Token
   - **Token:** (paste the access_token from step 1)
   - **Base URL:** `http://localhost:3000` (if running locally)
   - **Custom Headers:** `Authorization: Bearer {your-token}`

### Option 2: Authorization Code Flow

**For interactive ChatGPT setup:**

1. **ChatGPT Connector Form:**
   - **OAuth Provider:** Custom
   - **Authorization URL:** `https://your-domain.auth0.com/authorize`
   - **Token URL:** `https://your-domain.auth0.com/oauth/token`
   - **Client ID:** your-client-id
   - **Scopes:** `read:files write:files execute:commands`
   - **Redirect URI:** (copy from ChatGPT during setup)

2. **Update OAuth App:**
   - Add the ChatGPT redirect URI to your OAuth application's allowed redirect URLs

## 🚀 Running the OAuth-Protected Server

```bash
# Set environment variables
export OAUTH_PROVIDER=auth0
export OAUTH_JWKS_URL=https://your-domain.auth0.com/.well-known/jwks.json
export OAUTH_ISSUER=https://your-domain.auth0.com/
export OAUTH_AUDIENCE=https://api.lukhas.dev
export OAUTH_CLIENT_ID=your-client-id
export OAUTH_REQUIRED_SCOPES=read:files,write:files,execute:commands

export MCP_FS_ROOT=/Users/agi_dev/LOCAL-REPOS/Lukhas
export MCP_MAX_BYTES=2097152

# Install dependencies
npm install

# Start OAuth-protected server
npm run start:oauth
```

## 🧪 Testing OAuth Authentication

```bash
# Test without token (should fail)
curl -X POST http://localhost:3000/mcp \
  -H "Content-Type: application/json" \
  -d '{"tool": "stat", "args": {"rel": "."}}'

# Test with valid token (should succeed)
curl -X POST http://localhost:3000/mcp \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-jwt-token" \
  -d '{"tool": "stat", "args": {"rel": "."}}'
```

## 🛠️ Complete Tool Catalog

### **TIER 1: File Operations**
- `stat(rel)` - File/directory metadata
- `list_dir(rel)` - Directory listing  
- `search(query, glob?, limit?)` - Full-text search
- `get_file(rel)` - Read files safely
- `write_file(rel, content, mode?)` - Create/update files
- `delete_file(rel)` - Remove files
- `move_file(src, dest)` - Rename/move files
- `create_directory(rel)` - Make directories
- `copy_file(src, dest)` - Duplicate files

### **TIER 2: Git Operations**  
- `git_status()` - Working tree status
- `git_diff(file?, staged?)` - Show changes
- `git_add(files)` - Stage files
- `git_commit(message, files?)` - Commit changes
- `git_create_branch(name)` - Create branches
- `git_checkout(branch)` - Switch branches
- `git_stash(message?)` - Stash changes

### **TIER 3: Development Tools**
- `run_command(cmd, cwd?, timeout?)` - Execute shell commands
- `run_linter(files?, fix?)` - ESLint/Pylint with auto-fix
- `format_code(files?)` - Prettier/Black formatting
- `run_tests(pattern?, watch?)` - Test execution
- `find_symbol_usage(symbol, scope?)` - Symbol references
- `extract_imports(file)` - Dependency analysis
- `install_dependencies(packageManager?)` - Package installation

### **TIER 4: LUKHAS-Specific**
- `validate_trinity_compliance(files?)` - ⚛️🧠🛡️ framework validation
- `update_consciousness_docs()` - Auto-update docs
- `sync_agent_configs()` - Agent synchronization
- `audit_symbolic_vocabulary()` - Symbolic consistency
- `semantic_code_search(query)` - AI-powered search
- `find_todos_fixmes()` - Technical debt extraction
- `analyze_code_complexity(files?)` - Complexity metrics
- `find_unused_code()` - Dead code detection

## 🔒 Security Model

**Authentication:** JWT tokens verified against provider JWKS endpoint
**Authorization:** Scope-based access control (configurable required scopes)  
**Rate Limiting:** Token bucket (10 requests/10 seconds)
**Path Security:** Traversal protection + sensitive file denylist
**Credential Protection:** Auto-redaction of secrets in file contents
**Audit Trail:** Complete request logging with authentication context

## ⚠️ Development vs Production

**Development (No OAuth):**
```bash
# No OAuth environment variables = authentication disabled
npm run start  # Runs without authentication
```

**Production (OAuth Required):**
```bash
# All OAuth environment variables set = authentication enforced
npm run start:oauth  # Requires valid JWT tokens
```

## 🎯 Next Steps

1. **Configure your OAuth provider** (Auth0/Keycloak/Cloudflare)
2. **Set environment variables** for your chosen provider  
3. **Test locally** with curl and valid JWT tokens
4. **Integrate with ChatGPT** using Custom Connector with OAuth
5. **Deploy to production** with proper OAuth configuration

Your ChatGPT-5 instance will now have **secure, authenticated access** to your entire LUKHAS development workflow! 🚀
