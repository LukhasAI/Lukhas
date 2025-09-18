# LUKHAS OAuth 2.1 MCP Server# MCP LUKHAS SSE Server



A Model Context Protocol (MCP) server with OAuth 2.1 resource server authentication, providing secure access to filesystem tools with JWT token validation.A secure, lightweight MCP (Model Context Protocol) server that exposes read-only filesystem tools under allow-listed roots with Server-Sent Events (SSE) transport.



## 🔐 OAuth 2.1 Features## Features



- **JWT Token Validation**: Validates JWT tokens using JWKS from OIDC discovery- **Read-mostly filesystem access** with optional write capability

- **Protected Resource Metadata**: RFC 8705 compliant PRM endpoint- **SSE transport** at `/sse` endpoint with upgrade path to Streamable HTTP

- **OIDC Discovery**: Automatically fetches JWKS from OAuth provider- **Path traversal protection** with allow-listed roots

- **Secure SSE Transport**: OAuth-protected Server-Sent Events endpoint- **Size limits** and safety checks for file operations

- **Path Security**: Allow-listed root directories with path traversal protection- **Optional bearer token authentication**

- **Logging with path redaction** for security

## 🚀 Quick Start

## Quick Start

### 1. Install Dependencies

1. **Setup environment:**

```bash   ```bash

python3.11 -m venv .venv   cp .env.sample .env

source .venv/bin/activate   # Edit LUKHAS_MCP_ROOTS in .env to set allowed directories

pip install 'python-jose[cryptography]' httpx fastmcp uvicorn starlette   ```

```

2. **Install dependencies:**

### 2. Configure OAuth   ```bash

   uv add "mcp[cli]" starlette "uvicorn[standard]" python-dotenv

Copy `.env.sample` to `.env` and configure:   ```



```bash3. **Run the server:**

# Required OAuth configuration   ```bash

OAUTH_ISSUER=https://your-provider/.well-known/openid-configuration   uv run uvicorn server:app --host 0.0.0.0 --port 8000

OAUTH_AUDIENCE=api://your-api-identifier   ```

PUBLIC_BASE_URL=https://your-server.com

4. **Health check:**

# Filesystem access   ```bash

LUKHAS_MCP_ROOTS=/path/to/allowed/directory   curl http://localhost:8000/healthz

WRITE_ENABLED=false   ```

```

## Environment Configuration

### 3. Start Server

- **`LUKHAS_MCP_ROOTS`** (required): Colon-separated absolute paths the server may access

```bash- **`WRITE_ENABLED`** (default: false): Enable write operations

python server.py- **`BEARER_TOKEN`** (optional): Require Bearer token authentication for /sse endpoint

```

## Security Best Practices

Server runs on `http://localhost:8080` with these endpoints:

- **Principle of least reach**: Keep `LUKHAS_MCP_ROOTS` minimal and specific

- `GET /healthz` - Health check (no auth)- **Keep writes disabled**: Only set `WRITE_ENABLED=true` when actively editing

- `GET /.well-known/oauth-protected-resource` - Protected Resource Metadata (no auth)- **Review logs**: We redact root paths but review logs before sharing

- `SSE /sse/` - MCP Server-Sent Events (OAuth required)- **Use bearer tokens**: Set `BEARER_TOKEN` for production deployments



## 🔧 OAuth Integration## Tools Available



### Client Authentication- **`list_dir(path, show_hidden=False)`**: List directory contents

- **`read_text(file, max_bytes=128000)`**: Read text files safely

Include JWT token in requests to protected endpoints:- **`search_glob(path, pattern)`**: Search files with glob patterns

- **`write_text(file, content)`**: Write files (when enabled)

```bash

curl -H "Authorization: Bearer <your-jwt-token>" http://localhost:8080/sse/## ChatGPT Integration

```

### Step 1: Start the Server

### JWT Requirements```bash

# From the mcp-lukhas-sse directory

- **Algorithm**: RS256uv run python -c "

- **Audience**: Must match `OAUTH_AUDIENCE`import uvicorn

- **Issuer**: Must match OAuth providerimport server

- **Expiration**: Token must not be expireduvicorn.run(server.app, host='0.0.0.0', port=8000)

"

### MCP Client Configuration```



Configure your MCP client with:### Step 2: Set Up HTTPS Tunnel

```bash

```json# Option A: Cloudflare Tunnel (recommended)

{./setup-tunnel.sh

  "transport": {# Choose option 1

    "type": "sse",

    "url": "http://localhost:8080/sse/",# Option B: ngrok

    "headers": {./setup-tunnel.sh

      "Authorization": "Bearer <your-jwt-token>"# Choose option 2

    }```

  }

}### Step 3: Verify Authentication

``````bash

./verify-bearer-token.sh

## 🛠️ Available Tools```



The server provides these MCP tools (OAuth protected):### Step 4: Configure ChatGPT Connector



1. **`list_dir(path: str)`** - List directory contents1. **Go to ChatGPT → Settings → Connectors → Add connector**

2. **`read_text(path: str)`** - Read file content as text

3. **`search_glob(pattern: str, root_path?: str)`** - Search files with glob patterns2. **Fill in the connector details:**

4. **`write_text(path: str, content: str)`** - Write text to file (if enabled)   - **Name**: `LUKHAS FS (SSE)`

   - **Custom Tool**: `Filesystem (read-only) with optional writes`

All tools respect the `LUKHAS_MCP_ROOTS` allow-list and include path traversal protection.   - **Description**: `List, read, and (optionally) write text files within LUKHAS allow-listed roots.`

   - **MCP Server URL**: `https://<your-tunnel-host>/sse`

## 🔍 Testing & Verification   - **Authentication**: 

     - Method: `Bearer Token`

### Run OAuth Tests     - Header: `Authorization: Bearer lukhas-test-token-123`



```bash3. **Confirm**: Check "I trust this application"

python test_oauth.py

```### Step 5: Test the Integration



### Verify All EndpointsIn ChatGPT, try these commands:

```

```bashUse LUKHAS FS (SSE) to list_dir at path="."

# Start server in one terminal```

python server.py

```

# Run verification in another terminal  Use LUKHAS FS (SSE) to read_text file="README.md"

python verify_oauth.py```

```

```

### Manual TestingUse LUKHAS FS (SSE) to search_glob path="." pattern="*.py"

```

```bash

# Health check (no auth)### Troubleshooting

curl http://localhost:8080/healthz

- **"No features supported"**: Check that your tunnel URL ends with `/sse`

# Protected Resource Metadata (no auth)- **"Unauthorized"**: Verify bearer token matches your `.env` file

curl http://localhost:8080/.well-known/oauth-protected-resource- **"Connection refused"**: Ensure the server is running on port 8000



# SSE endpoint (requires OAuth)## Upgrade Path

curl -H "Authorization: Bearer <jwt>" http://localhost:8080/sse/

```- **Streamable HTTP**: Mount with `mcp.streamable_http_app()` when ChatGPT supports it

- **OAuth 2.1**: Use `mcp.server.auth` for JWT validation per MCP SDK docs

## 📁 Project Structure

## Development

```

mcp-lukhas-sse/```bash

├── server.py              # Main OAuth 2.1 MCP server# Install dev dependencies

├── pyproject.toml         # Python dependenciesuv add --dev pytest pytest-asyncio httpx

├── .env.sample           # OAuth configuration template

├── .env                  # Your OAuth configuration# Run tests

├── test_oauth.py         # OAuth implementation testspytest

├── verify_oauth.py       # Endpoint verification script

└── README.md            # This file# Lint

```ruff check .

```

## 🔐 Security Features

## Security & Privacy

### OAuth 2.1 Compliance

- Scope roots narrowly and review monthly

- JWT signature validation with JWKS- Prefer local servers + tunnel for testing

- OIDC discovery for automatic JWKS fetching- Move to small VM with TLS for production

- Audience and issuer validation- Follow MCP authorization spec for OAuth
- Token expiration checking
- JWKS caching with 5-minute TTL

### Path Security

- Allow-listed root directories only
- Path traversal attack prevention
- Symbolic link resolution and validation
- Permission error handling

### Protected Resource Metadata

RFC 8705 compliant endpoint at `/.well-known/oauth-protected-resource`:

```json
{
  "resource": "https://your-server.com", 
  "authorization_servers": ["https://your-oauth-provider"]
}
```

## 🚨 Production Deployment

### Essential Configuration

1. **Use HTTPS**: Deploy behind TLS-terminating proxy
2. **Real OAuth Provider**: Configure with production OIDC provider
3. **Secure Storage**: Protect `.env` file with proper permissions
4. **Network Security**: Use firewall rules and VPC isolation
5. **Monitoring**: Monitor OAuth token validation failures

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OAUTH_ISSUER` | Yes | OIDC discovery URL (with `/.well-known/openid-configuration`) |
| `OAUTH_AUDIENCE` | Yes | Expected JWT audience/identifier |
| `PUBLIC_BASE_URL` | Yes | Public URL of this server |
| `LUKHAS_MCP_ROOTS` | Yes | Colon-separated allowed root paths |
| `WRITE_ENABLED` | No | Enable write operations (default: false) |

### OAuth Provider Examples

**Auth0**:
```bash
OAUTH_ISSUER=https://your-domain.auth0.com/.well-known/openid-configuration
OAUTH_AUDIENCE=api://your-api-identifier
```

**Azure AD**:
```bash
OAUTH_ISSUER=https://login.microsoftonline.com/{tenant}/v2.0/.well-known/openid-configuration
OAUTH_AUDIENCE=api://your-app-id
```

**Google**:
```bash
OAUTH_ISSUER=https://accounts.google.com/.well-known/openid-configuration
OAUTH_AUDIENCE=your-client-id.googleusercontent.com
```

## 📄 License

[Add your license information here]

## 🤝 Contributing

[Add contribution guidelines here]