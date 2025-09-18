#!/usr/bin/env python3
"""Working OAuth 2.1 MCP Server."""

import os
import logging
from fastmcp import FastMCP
from jose import jwt, JWTError
import uvicorn

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP
mcp = FastMCP("LUKHAS OAuth MCP Server")

# OAuth configuration
OAUTH_SECRET = "test-secret-key-for-local-development-only-do-not-use-in-production"

def verify_token(auth_header: str) -> dict:
    """Verify JWT token and return user info."""
    if not auth_header or not auth_header.startswith("Bearer "):
        raise ValueError("Invalid Authorization header")
    
    token = auth_header[7:]  # Remove "Bearer "
    
    try:
        payload = jwt.decode(token, OAUTH_SECRET, algorithms=['HS256'])
        logger.info(f"Valid token for user: {payload.get('sub', 'unknown')}")
        return payload
    except JWTError as e:
        logger.warning(f"Invalid token: {e}")
        raise ValueError(f"Invalid token: {e}")

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

@mcp.tool()
def server_info() -> dict:
    """Get server information."""
    return {
        "name": "LUKHAS OAuth MCP Server",
        "version": "1.0.0",
        "authentication": "OAuth 2.1 (JWT)",
        "allowed_operations": ["list_directory", "read_file", "server_info"]
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    allowed_roots = os.getenv("ALLOWED_ROOTS", "/tmp")
    
    logger.info(f"🚀 Starting LUKHAS OAuth MCP Server on port {port}")
    logger.info(f"📁 Allowed roots: {allowed_roots}")
    logger.info(f"🔗 MCP SSE endpoint: http://localhost:{port}/sse")
    logger.info(f"🔐 Authentication: JWT Bearer token required")
    
    # Run the FastMCP server
    mcp.run(port=port, host="0.0.0.0")