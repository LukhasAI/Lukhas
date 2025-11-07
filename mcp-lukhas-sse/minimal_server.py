#!/usr/bin/env python3
"""Simple OAuth MCP Server without FastMCP dependency."""

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

class OAuth2Middleware(BaseHTTPMiddleware):
    """Simple OAuth 2.0 middleware."""

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
            payload = jwt.decode(token, OAUTH_SECRET, algorithms=['HS256'], options={"verify_aud": False})
            logger.info(f"Valid token for user: {payload.get('sub', 'unknown')}")
            request.state.user = payload
        except JWTError as e:
            logger.warning(f"Invalid token: {e}")
            return JSONResponse(
                {"error": "Invalid token"},
                status_code=403
            )

        return await call_next(request)

# Create Starlette app
app = Starlette()
app.add_middleware(OAuth2Middleware)

@app.route("/health")
async def health_check(request):
    """Health check endpoint."""
    return JSONResponse({
        "status": "healthy",
        "timestamp": time.time(),
        "server": "LUKHAS OAuth MCP Server"
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

@app.route("/sse", methods=["GET", "POST"])
async def mcp_endpoint(request):
    """MCP endpoint for tools."""
    if request.method == "GET":
        # Return available tools
        return JSONResponse({
            "tools": list(TOOLS.keys()),
            "server": "LUKHAS OAuth MCP Server",
            "authentication": "OAuth 2.1 (JWT Bearer)",
            "user": getattr(request.state, 'user', {}).get('sub', 'unknown')
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

    logger.info(f"🚀 Starting LUKHAS OAuth MCP Server on port {port}")
    logger.info(f"📁 Allowed roots: {allowed_roots}")
    logger.info(f"🔗 Health check: http://localhost:{port}/health")
    logger.info(f"🔗 MCP endpoint: http://localhost:{port}/sse")
    logger.info("🔐 Authentication: JWT Bearer token required")

    uvicorn.run(app, host="0.0.0.0", port=port)
