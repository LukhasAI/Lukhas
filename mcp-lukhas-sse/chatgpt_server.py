#!/usr/bin/env python3
"""ChatGPT-compatible MCP Server."""

import logging
import os
import time
from typing import Any, Dict

import uvicorn
from jose import JWTError, jwt
from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OAuth configuration
OAUTH_SECRET = "test-secret-key-for-local-development-only-do-not-use-in-production"

class FlexibleAuthMiddleware(BaseHTTPMiddleware):
    """Flexible authentication middleware for ChatGPT compatibility."""

    async def dispatch(self, request: Request, call_next):
        # Allow health check
        if request.url.path == "/health":
            return await call_next(request)

        # Check multiple auth methods for ChatGPT compatibility
        token = None

        # Method 1: Authorization header (Bearer token)
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]

        # Method 2: X-API-Key header (some clients use this)
        elif request.headers.get("X-API-Key"):
            token = request.headers.get("X-API-Key")

        # Method 3: Query parameter (for testing - not recommended for production)
        elif request.query_params.get("token"):
            token = request.query_params.get("token")

        # Method 4: Allow access without token for testing
        elif os.getenv("ALLOW_NO_AUTH", "false").lower() == "true":
            logger.info("No auth mode - allowing access without token")
            request.state.user = {"sub": "anonymous", "scope": "read:files"}
            return await call_next(request)

        if not token:
            return JSONResponse({
                "error": "Authentication required",
                "methods": [
                    "Authorization: Bearer <token>",
                    "X-API-Key: <token>",
                    "?token=<token>",
                    "Set ALLOW_NO_AUTH=true for testing"
                ]
            }, status_code=401)

        # Validate JWT
        try:
            payload = jwt.decode(token, OAUTH_SECRET, algorithms=['HS256'], options={"verify_aud": False})
            logger.info(f"Valid token for user: {payload.get('sub', 'unknown')}")
            request.state.user = payload
        except JWTError as e:
            logger.warning(f"Invalid token: {e}")
            return JSONResponse(
                {"error": f"Invalid token: {e}"},
                status_code=403
            )

        return await call_next(request)

# Create Starlette app
app = Starlette()
app.add_middleware(FlexibleAuthMiddleware)

@app.route("/health")
async def health_check(request):
    """Health check endpoint."""
    return JSONResponse({
        "status": "healthy",
        "timestamp": time.time(),
        "server": "LUKHAS ChatGPT-Compatible MCP Server",
        "auth_methods": [
            "Authorization: Bearer <token>",
            "X-API-Key: <token>",
            "?token=<token>"
        ]
    })

@app.route("/.well-known/oauth-authorization-server")
@app.route("/.well-known/openid_configuration")
async def oauth_discovery(request):
    """OAuth 2.0 / OpenID Connect discovery endpoint."""
    base_url = f"https://{request.headers.get('host', 'localhost:8080')}"

    return JSONResponse({
        "issuer": base_url,
        "authorization_endpoint": f"{base_url}/oauth/authorize",
        "token_endpoint": f"{base_url}/oauth/token",
        "userinfo_endpoint": f"{base_url}/oauth/userinfo",
        "jwks_uri": f"{base_url}/.well-known/jwks.json",
        "scopes_supported": ["openid", "read:files"],
        "response_types_supported": ["code", "token"],
        "grant_types_supported": ["authorization_code", "client_credentials"],
        "token_endpoint_auth_methods_supported": ["client_secret_post", "none"],
        "subject_types_supported": ["public"],
        "id_token_signing_alg_values_supported": ["HS256"],
        "claims_supported": ["sub", "aud", "exp", "iat", "iss"],
        "code_challenge_methods_supported": ["S256", "plain"]
    })

@app.route("/.well-known/jwks.json")
async def jwks_endpoint(request):
    """JWKS endpoint for public keys."""
    return JSONResponse({
        "keys": [
            {
                "kty": "oct",
                "k": OAUTH_SECRET,
                "alg": "HS256",
                "use": "sig",
                "kid": "test-key-1"
            }
        ]
    })

def list_directory_tool(path: str) -> Dict[str, Any]:
    """List files and directories in the given path."""
    try:
        # Security: Only allow paths under allowed roots
        allowed_roots = os.getenv("ALLOWED_ROOTS", "/tmp").split(",")
        if not any(os.path.abspath(path).startswith(os.path.abspath(root.strip())) for root in allowed_roots):
            return {"error": "Path not allowed"}

        if not os.path.exists(path):
            return {"error": "Path does not exist"}

        items = []
        for item in os.listdir(path):
            full_path = os.path.join(path, item)
            items.append({
                "name": item,
                "type": "directory" if os.path.isdir(full_path) else "file",
                "size": os.path.getsize(full_path) if os.path.isfile(full_path) else None
            })

        return {"path": path, "items": items}
    except Exception as e:
        return {"error": str(e)}

def read_file_tool(path: str, max_lines: int = 100) -> Dict[str, Any]:
    """Read the contents of a text file."""
    try:
        # Security: Only allow paths under allowed roots
        allowed_roots = os.getenv("ALLOWED_ROOTS", "/tmp").split(",")
        if not any(os.path.abspath(path).startswith(os.path.abspath(root.strip())) for root in allowed_roots):
            return {"error": "Path not allowed"}

        if not os.path.exists(path):
            return {"error": "File does not exist"}

        if not os.path.isfile(path):
            return {"error": "Path is not a file"}

        with open(path, encoding='utf-8') as f:
            lines = f.readlines()[:max_lines]

        return {
            "path": path,
            "content": "".join(lines),
            "truncated": len(lines) >= max_lines
        }
    except Exception as e:
        return {"error": str(e)}

# Available tools
TOOLS = {
    "list_directory": list_directory_tool,
    "read_file": read_file_tool
}

@app.route("/", methods=["GET"])
@app.route("/sse", methods=["GET", "POST"])
async def mcp_endpoint(request):
    """MCP endpoint for tools."""
    if request.method == "GET":
        # Return available tools and authentication info
        return JSONResponse({
            "tools": list(TOOLS.keys()),
            "server": "LUKHAS ChatGPT-Compatible MCP Server",
            "authentication": "Flexible (Bearer, X-API-Key, or query param)",
            "user": getattr(request.state, 'user', {}).get('sub', 'unknown'),
            "auth_examples": {
                "bearer": "Authorization: Bearer <token>",
                "api_key": "X-API-Key: <token>",
                "query": "?token=<token>"
            }
        })

    elif request.method == "POST":
        try:
            data = await request.json()
            tool_name = data.get("tool")
            args = data.get("args", {})

            if tool_name not in TOOLS:
                return JSONResponse(
                    {"error": f"Unknown tool: {tool_name}"},
                    status_code=400
                )

            # Execute tool
            result = TOOLS[tool_name](**args)

            return JSONResponse({
                "tool": tool_name,
                "args": args,
                "result": result,
                "user": getattr(request.state, 'user', {}).get('sub', 'unknown')
            })

        except Exception as e:
            return JSONResponse(
                {"error": str(e)},
                status_code=500
            )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    allowed_roots = os.getenv("ALLOWED_ROOTS", "/tmp")
    allow_no_auth = os.getenv("ALLOW_NO_AUTH", "true")  # Default to true for Railway
    host = os.getenv("HOST", "0.0.0.0")

    logger.info(f"🚀 Starting LUKHAS ChatGPT-Compatible MCP Server on {host}:{port}")
    logger.info(f"📁 Allowed roots: {allowed_roots}")
    logger.info(f"🔗 Health check: http://{host}:{port}/health")
    logger.info(f"🔗 MCP endpoint: http://{host}:{port}/sse")
    logger.info("🔐 Authentication: Flexible (Bearer/X-API-Key/Query)")
    logger.info(f"🔓 No-auth mode: {allow_no_auth}")

    uvicorn.run(app, host=host, port=port)
