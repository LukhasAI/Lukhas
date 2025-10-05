#!/usr/bin/env python3
"""Simplified OAuth 2.1 MCP Server for testing."""

import logging
import os
import time

from fastmcp import FastMCP
from jose import JWTError, jwt
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleOAuthMiddleware(BaseHTTPMiddleware):
    """Simple OAuth middleware for testing."""

    def __init__(self, app, oauth_secret: str = None):
        super().__init__(app)
        self.oauth_secret = oauth_secret or "test-secret-key-for-local-development-only-do-not-use-in-production"

    async def dispatch(self, request: Request, call_next):
        # Allow health check
        if request.url.path == "/health":
            return await call_next(request)

        # Check for Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JSONResponse(
                {"error": "Missing Authorization header"},
                status_code=401
            )

        # Extract token
        if not auth_header.startswith("Bearer "):
            return JSONResponse(
                {"error": "Invalid Authorization header format"},
                status_code=401
            )

        token = auth_header[7:]  # Remove "Bearer "

        # Validate JWT
        try:
            payload = jwt.decode(token, self.oauth_secret, algorithms=['HS256'])
            logger.info(f"Valid token for user: {payload.get('sub', 'unknown')}")
            # Add user info to request
            request.state.user = payload
        except JWTError as e:
            logger.warning(f"Invalid token: {e}")
            return JSONResponse(
                {"error": "Invalid token"},
                status_code=403
            )

        return await call_next(request)

# Initialize FastMCP
mcp = FastMCP("LUKHAS OAuth MCP Server")

@mcp.tool()
def list_directory(path: str) -> dict:
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

@mcp.tool()
def read_file(path: str, max_lines: int = 100) -> dict:
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

        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()[:max_lines]

        return {
            "path": path,
            "content": "".join(lines),
            "truncated": len(lines) >= max_lines
        }
    except Exception as e:
        return {"error": str(e)}

# Create the FastMCP app first
mcp_app = mcp.create_server()

# Create Starlette app with middleware
middleware = [
    Middleware(SimpleOAuthMiddleware)
]

app = Starlette(middleware=middleware)

# Add health check endpoint
@app.route("/health")
async def health_check(request):
    return JSONResponse({"status": "healthy", "timestamp": time.time()})

# Add MCP routes
@app.route("/sse", methods=["GET", "POST"])
async def mcp_endpoint(request):
    return await mcp_app(request.scope, request.receive, request._send)

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8080))
    logger.info(f"🚀 Starting LUKHAS OAuth MCP Server on port {port}")
    logger.info(f"📁 Allowed roots: {os.getenv('ALLOWED_ROOTS', '/tmp')}")
    logger.info(f"🔗 Health check: http://localhost:{port}/health")
    logger.info(f"🔗 MCP SSE endpoint: http://localhost:{port}/sse")

    uvicorn.run(app, host="0.0.0.0", port=port)
