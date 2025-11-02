#!/usr/bin/env python3
"""
Official MCP-compliant server for LUKHAS AI Platform.
Implements the Model Context Protocol v2025-06-18 specification.
"""

import json
import logging
import os
import time
import uuid
from typing import Any, Dict, Optional

import uvicorn
from starlette.applications import Starlette
from starlette.responses import JSONResponse, StreamingResponse
from starlette.routing import Route

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MCP Protocol version
MCP_PROTOCOL_VERSION = "2025-06-18"


class MCPServer:
    """Official MCP-compliant server implementation."""

    def __init__(self):
        self.session_id: Optional[str] = None
        self.initialized = False
        self.server_info = {"name": "lukhas-mcp-server", "version": "1.0.0"}

    def generate_session_id(self) -> str:
        """Generate a cryptographically secure session ID."""
        return str(uuid.uuid4())

    async def handle_initialize(self, request_data: Dict) -> Dict:
        """Handle MCP initialization request."""
        logger.info("Handling MCP initialization request")

        # Extract client info
        client_info = request_data.get("params", {}).get("clientInfo", {})
        protocol_version = request_data.get("params", {}).get("protocolVersion", "2025-06-18")
        request_data.get("params", {}).get("capabilities", {})

        logger.info(f"Client: {client_info.get('name', 'unknown')} v{client_info.get('version', 'unknown')}")
        logger.info(f"Protocol version: {protocol_version}")

        # Generate session ID
        self.session_id = self.generate_session_id()
        self.initialized = True

        # Return initialization response
        return {
            "jsonrpc": "2.0",
            "id": request_data.get("id"),
            "result": {
                "protocolVersion": MCP_PROTOCOL_VERSION,
                "capabilities": {
                    "tools": {"listChanged": False},
                    "resources": {"subscribe": False, "listChanged": False},
                },
                "serverInfo": self.server_info,
            },
        }

    async def handle_tools_list(self, request_data: Dict) -> Dict:
        """Handle tools/list request."""
        logger.info("Handling tools/list request")

        tools = [
            {
                "name": "list_directory",
                "description": "List files and directories in a given path",
                "inputSchema": {
                    "type": "object",
                    "properties": {"path": {"type": "string", "description": "The directory path to list"}},
                    "required": ["path"],
                },
            },
            {
                "name": "read_file",
                "description": "Read the contents of a text file",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "The file path to read"},
                        "max_lines": {
                            "type": "integer",
                            "description": "Maximum number of lines to read",
                            "default": 100,
                        },
                    },
                    "required": ["path"],
                },
            },
        ]

        return {"jsonrpc": "2.0", "id": request_data.get("id"), "result": {"tools": tools}}

    async def handle_tools_call(self, request_data: Dict) -> Dict:
        """Handle tools/call request."""
        logger.info("Handling tools/call request")

        params = request_data.get("params", {})
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if tool_name == "list_directory":
            result = await self.list_directory_tool(arguments.get("path", "/tmp"))
        elif tool_name == "read_file":
            result = await self.read_file_tool(arguments.get("path"), arguments.get("max_lines", 100))
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_data.get("id"),
                "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"},
            }

        return {
            "jsonrpc": "2.0",
            "id": request_data.get("id"),
            "result": {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]},
        }

    async def list_directory_tool(self, path: str) -> Dict[str, Any]:
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
                items.append(
                    {
                        "name": item,
                        "type": "directory" if os.path.isdir(full_path) else "file",
                        "size": os.path.getsize(full_path) if os.path.isfile(full_path) else None,
                    }
                )

            return {"path": path, "items": items}
        except Exception as e:
            return {"error": str(e)}

    async def read_file_tool(self, path: str, max_lines: int = 100) -> Dict[str, Any]:
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

            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()[:max_lines]

            return {"path": path, "content": "".join(lines), "truncated": len(lines) >= max_lines}
        except Exception as e:
            return {"error": str(e)}

    async def handle_jsonrpc_request(self, request_data: Dict) -> Dict:
        """Handle JSON-RPC requests according to MCP specification."""
        method = request_data.get("method")

        if method == "initialize":
            return await self.handle_initialize(request_data)
        elif method == "tools/list":
            return await self.handle_tools_list(request_data)
        elif method == "tools/call":
            return await self.handle_tools_call(request_data)
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_data.get("id"),
                "error": {"code": -32601, "message": f"Method not found: {method}"},
            }


# Global MCP server instance
mcp_server = MCPServer()


async def health_check(request):
    """Health check endpoint."""
    return JSONResponse(
        {
            "status": "healthy",
            "timestamp": time.time(),
            "server": "LUKHAS MCP Server (Official Spec v2025-06-18)",
            "protocol_version": MCP_PROTOCOL_VERSION,
            "session_initialized": mcp_server.initialized,
        }
    )


async def mcp_endpoint(request):
    """
    Main MCP endpoint implementing Streamable HTTP transport.
    Supports both POST (sending messages) and GET (receiving messages via SSE).
    """
    # Validate protocol version header
    protocol_version = request.headers.get("MCP-Protocol-Version", "2025-03-26")
    if protocol_version not in ["2025-06-18", "2025-03-26"]:
        return JSONResponse({"error": "Unsupported MCP-Protocol-Version"}, status_code=400)

    # Validate session ID if present
    session_id = request.headers.get("Mcp-Session-Id")
    if session_id and mcp_server.session_id and session_id != mcp_server.session_id:
        return JSONResponse({"error": "Invalid session ID"}, status_code=404)

    if request.method == "POST":
        # Handle JSON-RPC message from client
        try:
            request_data = await request.json()
            logger.info(f"Received JSON-RPC request: {request_data.get('method', 'unknown')}")

            # Process the JSON-RPC request
            response_data = await mcp_server.handle_jsonrpc_request(request_data)

            # Add session ID header for initialization responses
            headers = {}
            if request_data.get("method") == "initialize" and mcp_server.session_id:
                headers["Mcp-Session-Id"] = mcp_server.session_id

            # Check if client accepts SSE for streaming responses
            accept_header = request.headers.get("Accept", "")
            if "text/event-stream" in accept_header:
                # Return SSE stream with the response
                async def generate_sse():
                    # Send the JSON-RPC response as SSE event
                    yield f"data: {json.dumps(response_data)}\n\n"

                return StreamingResponse(generate_sse(), media_type="text/event-stream", headers=headers)
            else:
                # Return standard JSON response
                return JSONResponse(response_data, headers=headers)

        except json.JSONDecodeError:
            return JSONResponse({"error": "Invalid JSON"}, status_code=400)
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            return JSONResponse({"error": "Internal server error"}, status_code=500)

    elif request.method == "GET":
        # Handle SSE stream for server-to-client messages
        accept_header = request.headers.get("Accept", "")
        if "text/event-stream" not in accept_header:
            return JSONResponse({"error": "This endpoint requires text/event-stream"}, status_code=405)

        # For now, return a simple SSE stream indicating the server is ready
        async def generate_sse():
            yield f"data: {json.dumps({'type': 'ready', 'server': 'LUKHAS MCP Server'})}\n\n"

        return StreamingResponse(generate_sse(), media_type="text/event-stream")

    else:
        return JSONResponse({"error": "Method not allowed"}, status_code=405)


async def delete_session(request):
    """Handle session termination."""
    session_id = request.headers.get("Mcp-Session-Id")
    if session_id == mcp_server.session_id:
        mcp_server.session_id = None
        mcp_server.initialized = False
        return JSONResponse({"message": "Session terminated"})
    else:
        return JSONResponse({"error": "Invalid session ID"}, status_code=404)


# Define routes
routes = [
    Route("/health", health_check, methods=["GET"]),
    Route("/mcp", mcp_endpoint, methods=["GET", "POST"]),
    Route("/mcp", delete_session, methods=["DELETE"]),
]

# Create Starlette app
app = Starlette(routes=routes)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    host = os.getenv("HOST", "0.0.0.0")
    allowed_roots = os.getenv("ALLOWED_ROOTS", "/tmp")

    logger.info(f"🚀 Starting LUKHAS MCP Server (Official Spec v{MCP_PROTOCOL_VERSION})")
    logger.info(f"🔗 Listening on {host}:{port}")
    logger.info(f"🔗 Health check: http://{host}:{port}/health")
    logger.info(f"🔗 MCP endpoint: http://{host}:{port}/mcp")
    logger.info(f"📁 Allowed roots: {allowed_roots}")
    logger.info(f"📋 Protocol version: {MCP_PROTOCOL_VERSION}")

    uvicorn.run(app, host=host, port=port)
