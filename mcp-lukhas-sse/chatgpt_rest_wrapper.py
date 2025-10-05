#!/usr/bin/env python3
"""
LUKHAS MCP REST API Wrapper for ChatGPT Custom GPT Actions and Connectors
Supports both REST API calls and MCP SSE transport for ChatGPT integration.
"""

import logging
import os
import time
import uuid
from typing import Any, Dict

import uvicorn

# MCP imports for SSE transport
from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from starlette.routing import Route

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LukhasMCPRestWrapper:
    """REST API wrapper for LUKHAS MCP server functionality."""

    def __init__(self):
        self.session_id = str(uuid.uuid4())
        self.initialized = True
        self.server_info = {
            "name": "lukhas-ai-rest-wrapper",
            "version": "1.0.0"
        }

    async def list_directory_impl(self, path: str) -> Dict[str, Any]:
        """Internal implementation of list_directory."""
        try:
            # Security: Only allow paths under allowed roots
            allowed_roots = os.getenv("ALLOWED_ROOTS", "/tmp,/var/tmp").split(",")
            abs_path = os.path.abspath(path)

            if not any(abs_path.startswith(os.path.abspath(root.strip())) for root in allowed_roots):
                return {
                    "error": f"Path '{path}' not allowed",
                    "allowed_roots": allowed_roots
                }

            if not os.path.exists(path):
                return {"error": f"Path '{path}' does not exist"}

            if not os.path.isdir(path):
                return {"error": f"Path '{path}' is not a directory"}

            items = []
            for item in sorted(os.listdir(path)):
                full_path = os.path.join(path, item)
                item_type = "directory" if os.path.isdir(full_path) else "file"
                size = os.path.getsize(full_path) if os.path.isfile(full_path) else None

                item_info = {
                    "name": item,
                    "type": item_type,
                    "path": full_path
                }
                if size is not None:
                    item_info["size_bytes"] = size

                items.append(item_info)

            return {
                "success": True,
                "path": path,
                "items": items,
                "total_items": len(items),
                "lukhas_ai": "⚛️🧠🛡️ LUKHAS AI Constellation Framework"
            }

        except Exception as e:
            logger.error(f"Error listing directory {path}: {e}")
            return {"error": f"Error listing directory: {str(e)}"}

    async def read_file_impl(self, path: str, max_lines: int = 100) -> Dict[str, Any]:
        """Internal implementation of read_file."""
        try:
            # Security: Only allow paths under allowed roots
            allowed_roots = os.getenv("ALLOWED_ROOTS", "/tmp,/var/tmp").split(",")
            abs_path = os.path.abspath(path)

            if not any(abs_path.startswith(os.path.abspath(root.strip())) for root in allowed_roots):
                return {
                    "error": f"Path '{path}' not allowed",
                    "allowed_roots": allowed_roots
                }

            if not os.path.exists(path):
                return {"error": f"File '{path}' does not exist"}

            if not os.path.isfile(path):
                return {"error": f"Path '{path}' is not a regular file"}

            # Check file size (limit to 1MB)
            file_size = os.path.getsize(path)
            if file_size > 1024 * 1024:  # 1MB
                return {
                    "error": f"File '{path}' is too large ({file_size} bytes). Maximum allowed: 1MB"
                }

            with open(path, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()

            # Limit the number of lines
            if len(lines) > max_lines:
                content_lines = lines[:max_lines]
                truncated = True
            else:
                content_lines = lines
                truncated = False

            content = ''.join(content_lines)

            return {
                "success": True,
                "path": path,
                "content": content,
                "total_lines": len(lines),
                "displayed_lines": len(content_lines),
                "truncated": truncated,
                "file_size_bytes": file_size,
                "lukhas_ai": "⚛️🧠🛡️ LUKHAS AI Constellation Framework"
            }

        except UnicodeDecodeError:
            return {
                "error": f"File '{path}' appears to be a binary file or uses unsupported encoding"
            }
        except Exception as e:
            logger.error(f"Error reading file {path}: {e}")
            return {"error": f"Error reading file: {str(e)}"}

# Global server instance
mcp_wrapper = LukhasMCPRestWrapper()

# Create FastMCP server for SSE transport (ChatGPT Connectors)
mcp = FastMCP(name="lukhas-mcp-server")

@mcp.tool()
def list_directory(path: str) -> dict:
    """List directory contents using MCP tool interface."""
    # Security: Only allow paths under allowed roots
    allowed_roots = os.getenv("ALLOWED_ROOTS", "/tmp,/var/tmp").split(",")
    abs_path = os.path.abspath(path)

    if not any(abs_path.startswith(os.path.abspath(root.strip())) for root in allowed_roots):
        return {
            "error": f"Path '{path}' not allowed",
            "allowed_roots": allowed_roots
        }

    if not os.path.exists(path):
        return {"error": f"Path '{path}' does not exist"}

    if not os.path.isdir(path):
        return {"error": f"Path '{path}' is not a directory"}

    try:
        items = []
        for item in sorted(os.listdir(path)):
            full_path = os.path.join(path, item)
            item_type = "directory" if os.path.isdir(full_path) else "file"
            size = os.path.getsize(full_path) if os.path.isfile(full_path) else None

            item_info = {
                "name": item,
                "type": item_type,
                "path": full_path
            }
            if size is not None:
                item_info["size_bytes"] = size

            items.append(item_info)

        return {
            "success": True,
            "path": path,
            "items": items,
            "total_items": len(items),
            "lukhas_ai": "⚛️🧠🛡️ LUKHAS AI Constellation Framework"
        }
    except Exception as e:
        return {"error": f"Error listing directory: {str(e)}"}

@mcp.tool()
def read_file(path: str, max_lines: int = 100) -> dict:
    """Read file contents using MCP tool interface."""
    # Security: Only allow paths under allowed roots
    allowed_roots = os.getenv("ALLOWED_ROOTS", "/tmp,/var/tmp").split(",")
    abs_path = os.path.abspath(path)

    if not any(abs_path.startswith(os.path.abspath(root.strip())) for root in allowed_roots):
        return {
            "error": f"Path '{path}' not allowed",
            "allowed_roots": allowed_roots
        }

    if not os.path.exists(path):
        return {"error": f"File '{path}' does not exist"}

    if not os.path.isfile(path):
        return {"error": f"Path '{path}' is not a regular file"}

    try:
        # Check file size (limit to 1MB)
        file_size = os.path.getsize(path)
        if file_size > 1024 * 1024:  # 1MB
            return {
                "error": f"File '{path}' is too large ({file_size} bytes). Maximum allowed: 1MB"
            }

        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()

        # Limit the number of lines
        if len(lines) > max_lines:
            content_lines = lines[:max_lines]
            truncated = True
        else:
            content_lines = lines
            truncated = False

        content = ''.join(content_lines)

        return {
            "success": True,
            "path": path,
            "content": content,
            "total_lines": len(lines),
            "displayed_lines": len(content_lines),
            "truncated": truncated,
            "file_size_bytes": file_size,
            "lukhas_ai": "⚛️🧠🛡️ LUKHAS AI Constellation Framework"
        }
    except UnicodeDecodeError:
        return {
            "error": f"File '{path}' appears to be a binary file or uses unsupported encoding"
        }
    except Exception as e:
        return {"error": f"Error reading file: {str(e)}"}

# OAuth PRM configuration
OIDC_DISCOVERY = os.getenv("OAUTH_ISSUER", "").rstrip("/")
OAUTH_AUDIENCE = os.getenv("OAUTH_AUDIENCE", "")
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "").rstrip("/")

async def health_check(request):
    """Health check endpoint."""
    return JSONResponse({
        "status": "healthy",
        "timestamp": time.time(),
        "server": "LUKHAS MCP REST Wrapper for ChatGPT",
        "version": "1.0.0",
        "constellation_framework": "⚛️🧠🛡️",
        "session_id": mcp_wrapper.session_id
    })

async def get_server_info(request):
    """Get LUKHAS AI server information."""
    info = {
        "lukhas_ai": {
            "name": "LUKHAS AI Platform",
            "description": "Consciousness-Aware AI Development Platform",
            "version": "1.0.0",
            "constellation_framework": {
                "symbol": "⚛️🧠🛡️",
                "components": {
                    "⚛️ Identity": "Lambda ID system, authentication, symbolic self-representation",
                    "🧠 Consciousness": "692-module cognitive processing, memory systems, awareness",
                    "🛡️ Guardian": "Constitutional AI, ethical frameworks, drift detection"
                }
            },
            "architecture": {
                "lane_based": True,
                "total_files": "~7,000 Python files",
                "lanes": ["lukhas/", "candidate/", "matriz/", "core/", "tests/", "mcp-servers/"]
            }
        },
        "rest_wrapper": {
            "name": "LUKHAS MCP REST Wrapper",
            "purpose": "ChatGPT Custom GPT Actions integration",
            "session_id": mcp_wrapper.session_id,
            "capabilities": ["list_directory", "read_file", "system_info"],
            "security": {
                "path_sandboxing": True,
                "allowed_roots": os.getenv("ALLOWED_ROOTS", "/tmp,/var/tmp").split(",")
            }
        }
    }

    return JSONResponse(info)

async def list_directory_rest(request):
    """REST endpoint to list directory contents."""
    try:
        # Get path from query parameter
        path = request.query_params.get("path", "/tmp")

        result = await mcp_wrapper.list_directory_impl(path)
        return JSONResponse(result)

    except Exception as e:
        logger.error(f"Error in list_directory endpoint: {e}")
        return JSONResponse({"error": f"Internal server error: {str(e)}"}, status_code=500)

async def read_file_rest(request):
    """REST endpoint to read file contents."""
    try:
        # Get parameters from query
        path = request.query_params.get("path")
        if not path:
            return JSONResponse({"error": "Missing required parameter: path"}, status_code=400)

        max_lines = int(request.query_params.get("max_lines", 100))

        result = await mcp_wrapper.read_file_impl(path, max_lines)
        return JSONResponse(result)

    except ValueError:
        return JSONResponse({"error": "Invalid max_lines parameter"}, status_code=400)
    except Exception as e:
        logger.error(f"Error in read_file endpoint: {e}")
        return JSONResponse({"error": f"Internal server error: {str(e)}"}, status_code=500)

async def list_directory_post(request):
    """POST endpoint to list directory contents."""
    try:
        data = await request.json()
        path = data.get("path", "/tmp")

        result = await mcp_wrapper.list_directory_impl(path)
        return JSONResponse(result)

    except Exception as e:
        logger.error(f"Error in list_directory POST endpoint: {e}")
        return JSONResponse({"error": f"Internal server error: {str(e)}"}, status_code=500)

async def read_file_post(request):
    """POST endpoint to read file contents."""
    try:
        data = await request.json()
        path = data.get("path")
        if not path:
            return JSONResponse({"error": "Missing required parameter: path"}, status_code=400)

        max_lines = data.get("max_lines", 100)

        result = await mcp_wrapper.read_file_impl(path, max_lines)
        return JSONResponse(result)

    except Exception as e:
        logger.error(f"Error in read_file POST endpoint: {e}")
        return JSONResponse({"error": f"Internal server error: {str(e)}"}, status_code=500)

async def get_openapi_spec(request):
    """Serve OpenAPI specification for ChatGPT Connectors."""
    openapi_spec = {
        "openapi": "3.0.0",
        "info": {
            "title": "LUKHAS AI REST API",
            "description": "Access LUKHAS AI Platform capabilities through the Constellation Framework (⚛️🧠🛡️). This REST API provides ChatGPT Connectors with secure file system access and LUKHAS AI information.",
            "version": "1.0.0",
            "contact": {
                "name": "LUKHAS AI Platform",
                "url": "https://github.com/LUKHAS-AI/LUKHAS"
            }
        },
        "servers": [
            {
                "url": "https://lukhas-mcp-production.up.railway.app",
                "description": "LUKHAS AI REST API Production Server"
            }
        ],
        "paths": {
            "/health": {
                "get": {
                    "summary": "Health Check",
                    "description": "Check if the LUKHAS AI server is operational",
                    "operationId": "healthCheck",
                    "responses": {
                        "200": {
                            "description": "Server is healthy",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string", "example": "healthy"},
                                            "server": {"type": "string", "example": "LUKHAS MCP REST Wrapper for ChatGPT"},
                                            "version": {"type": "string", "example": "1.0.0"},
                                            "constellation_framework": {"type": "string", "example": "⚛️🧠🛡️"},
                                            "session_id": {"type": "string", "format": "uuid"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/info": {
                "get": {
                    "summary": "Get LUKHAS AI System Information",
                    "description": "Retrieve detailed information about the LUKHAS AI Platform and Constellation Framework",
                    "operationId": "getSystemInfo",
                    "responses": {
                        "200": {
                            "description": "LUKHAS AI system information",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "lukhas_ai": {"type": "object"},
                                            "rest_wrapper": {"type": "object"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/list-directory": {
                "get": {
                    "summary": "List Directory Contents",
                    "description": "List files and directories in a specified path (security: only allowed in safe directories)",
                    "operationId": "listDirectory",
                    "parameters": [
                        {
                            "name": "path",
                            "in": "query",
                            "required": True,
                            "description": "Directory path to list (must be within allowed roots)",
                            "schema": {"type": "string", "example": "/tmp"}
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Directory contents listed successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "success": {"type": "boolean"},
                                            "path": {"type": "string"},
                                            "items": {"type": "array"},
                                            "total_items": {"type": "integer"},
                                            "lukhas_ai": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/read-file": {
                "get": {
                    "summary": "Read File Contents",
                    "description": "Read the contents of a text file (security: only allowed in safe directories, max 1MB)",
                    "operationId": "readFile",
                    "parameters": [
                        {
                            "name": "path",
                            "in": "query",
                            "required": True,
                            "description": "File path to read (must be within allowed roots)",
                            "schema": {"type": "string", "example": "/tmp/example.txt"}
                        },
                        {
                            "name": "max_lines",
                            "in": "query",
                            "required": False,
                            "description": "Maximum number of lines to read",
                            "schema": {"type": "integer", "default": 100, "example": 100}
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "File contents read successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "success": {"type": "boolean"},
                                            "path": {"type": "string"},
                                            "content": {"type": "string"},
                                            "total_lines": {"type": "integer"},
                                            "file_size_bytes": {"type": "integer"},
                                            "lukhas_ai": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "security": [],
        "tags": [
            {
                "name": "LUKHAS AI",
                "description": "LUKHAS AI Platform operations powered by the Constellation Framework ⚛️🧠🛡️"
            }
        ]
    }

    return JSONResponse(openapi_spec)

async def oauth_prm(request):
    """OAuth Protected Resource Metadata (RFC 9728) endpoint."""
    if not (OIDC_DISCOVERY and OAUTH_AUDIENCE and PUBLIC_BASE_URL):
        return JSONResponse({"status": "disabled", "note": "OAuth not configured"}, status_code=404)

    # Minimal RFC 9728 PRM
    prm_data = {
        "resource": PUBLIC_BASE_URL,
        "authorization_servers": [OIDC_DISCOVERY],  # issuer
        "bearer_methods_supported": ["header"]
    }

    return JSONResponse(prm_data)

# Define routes
routes = [
    Route("/health", health_check, methods=["GET"]),
    Route("/info", get_server_info, methods=["GET"]),
    Route("/list-directory", list_directory_rest, methods=["GET"]),
    Route("/read-file", read_file_rest, methods=["GET"]),
    Route("/list-directory", list_directory_post, methods=["POST"]),
    Route("/read-file", read_file_post, methods=["POST"]),
    Route("/openapi.json", get_openapi_spec, methods=["GET"]),
    Route("/.well-known/oauth-protected-resource", oauth_prm, methods=["GET"]),
]

# Create main Starlette app
app = Starlette(routes=routes)

# Add CORS middleware for ChatGPT
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ChatGPT needs this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the MCP SSE app
app.mount("/sse", mcp.sse_app())

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    host = os.getenv("HOST", "0.0.0.0")

    # Set default allowed roots for security
    if not os.getenv("ALLOWED_ROOTS"):
        os.environ["ALLOWED_ROOTS"] = "/tmp,/var/tmp"

    logger.info("🚀 Starting LUKHAS MCP REST Wrapper + SSE for ChatGPT")
    logger.info("⚛️🧠🛡️ Constellation Framework: Identity, Consciousness, Guardian")
    logger.info(f"🔗 Listening on {host}:{port}")
    logger.info(f"🔗 Health check: http://{host}:{port}/health")
    logger.info(f"🔗 Server info: http://{host}:{port}/info")
    logger.info(f"🔗 List directory: http://{host}:{port}/list-directory?path=/tmp")
    logger.info(f"🔗 Read file: http://{host}:{port}/read-file?path=/tmp/example.txt")
    logger.info(f"� MCP SSE: http://{host}:{port}/sse/ (ChatGPT Connectors)")
    logger.info(f"🔗 OAuth PRM: http://{host}:{port}/.well-known/oauth-protected-resource")
    logger.info(f"�📁 Allowed roots: {os.getenv('ALLOWED_ROOTS')}")
    logger.info("🎯 Ready for ChatGPT Custom GPT Actions (REST) and Connectors (MCP SSE)")

    uvicorn.run(app, host=host, port=port)
