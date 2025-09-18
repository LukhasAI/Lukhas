#!/usr/bin/env python3
"""
LUKHAS MCP STDIO Server - Manual Implementation
Compatible with Python 3.9+ and implements MCP v2025-06-18 STDIO transport for ChatGPT.
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, Optional

# Configure logging to stderr (NEVER use stdout in STDIO servers)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

class LukhasMCPServer:
    """LUKHAS AI MCP STDIO Server - Manual implementation for Python 3.9+"""
    
    def __init__(self):
        self.server_info = {
            "name": "lukhas-ai-mcp-server",
            "version": "1.0.0"
        }
        self.capabilities = {
            "tools": {
                "listChanged": False
            },
            "resources": {
                "subscribe": False,
                "listChanged": False
            }
        }
        
    async def handle_initialize(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP initialization request."""
        logger.info("Handling MCP initialization request")
        
        params = request.get("params", {})
        client_info = params.get("clientInfo", {})
        protocol_version = params.get("protocolVersion", "2025-06-18")
        
        logger.info(f"Client: {client_info.get('name', 'unknown')} v{client_info.get('version', 'unknown')}")
        logger.info(f"Protocol version: {protocol_version}")
        
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": {
                "protocolVersion": "2025-06-18",
                "capabilities": self.capabilities,
                "serverInfo": self.server_info
            }
        }
    
    async def handle_tools_list(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/list request."""
        logger.info("Handling tools/list request")
        
        tools = [
            {
                "name": "list_directory",
                "description": "List files and directories in a given path",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "The directory path to list"
                        }
                    },
                    "required": ["path"]
                }
            },
            {
                "name": "read_file",
                "description": "Read the contents of a text file",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "The file path to read"
                        },
                        "max_lines": {
                            "type": "integer",
                            "description": "Maximum number of lines to read",
                            "default": 100
                        }
                    },
                    "required": ["path"]
                }
            },
            {
                "name": "search_files",
                "description": "Search for files matching a pattern in a directory",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "directory": {
                            "type": "string",
                            "description": "The directory to search in"
                        },
                        "pattern": {
                            "type": "string",
                            "description": "The filename pattern to search for (supports wildcards)"
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of results to return",
                            "default": 20
                        }
                    },
                    "required": ["directory", "pattern"]
                }
            },
            {
                "name": "get_lukhas_info",
                "description": "Get information about the LUKHAS AI system and Trinity Framework",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        ]
        
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": {
                "tools": tools
            }
        }
    
    async def list_directory_tool(self, path: str) -> str:
        """List files and directories in the given path."""
        try:
            # Security: Only allow paths under allowed roots
            allowed_roots = os.getenv("ALLOWED_ROOTS", "/tmp,/var/tmp,/Users/agi_dev/LOCAL-REPOS/Lukhas/test_data").split(",")
            abs_path = os.path.abspath(path)
            
            if not any(abs_path.startswith(os.path.abspath(root.strip())) for root in allowed_roots):
                return json.dumps({
                    "error": f"Path '{path}' not allowed",
                    "allowed_roots": allowed_roots
                }, indent=2)
            
            if not os.path.exists(path):
                return json.dumps({"error": f"Path '{path}' does not exist"}, indent=2)
            
            if not os.path.isdir(path):
                return json.dumps({"error": f"Path '{path}' is not a directory"}, indent=2)
            
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
            
            result = {
                "path": path,
                "items": items,
                "total_items": len(items),
                "lukhas_ai": "⚛️🧠🛡️ LUKHAS AI Trinity Framework"
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            logger.error(f"Error listing directory {path}: {e}")
            return json.dumps({"error": f"Error listing directory: {str(e)}"}, indent=2)
    
    async def read_file_tool(self, path: str, max_lines: int = 100) -> str:
        """Read the contents of a text file."""
        try:
            # Security: Only allow paths under allowed roots
            allowed_roots = os.getenv("ALLOWED_ROOTS", "/tmp,/var/tmp,/Users/agi_dev/LOCAL-REPOS/Lukhas/test_data").split(",")
            abs_path = os.path.abspath(path)
            
            if not any(abs_path.startswith(os.path.abspath(root.strip())) for root in allowed_roots):
                return json.dumps({
                    "error": f"Path '{path}' not allowed",
                    "allowed_roots": allowed_roots
                }, indent=2)
            
            if not os.path.exists(path):
                return json.dumps({"error": f"File '{path}' does not exist"}, indent=2)
            
            if not os.path.isfile(path):
                return json.dumps({"error": f"Path '{path}' is not a regular file"}, indent=2)
            
            # Check file size (limit to 1MB)
            file_size = os.path.getsize(path)
            if file_size > 1024 * 1024:  # 1MB
                return json.dumps({
                    "error": f"File '{path}' is too large ({file_size} bytes). Maximum allowed: 1MB"
                }, indent=2)
            
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
            
            result = {
                "path": path,
                "content": content,
                "total_lines": len(lines),
                "displayed_lines": len(content_lines),
                "truncated": truncated,
                "file_size_bytes": file_size,
                "lukhas_ai": "⚛️🧠🛡️ LUKHAS AI Trinity Framework"
            }
            
            return json.dumps(result, indent=2)
            
        except UnicodeDecodeError:
            return json.dumps({
                "error": f"File '{path}' appears to be a binary file or uses unsupported encoding"
            }, indent=2)
        except Exception as e:
            logger.error(f"Error reading file {path}: {e}")
            return json.dumps({"error": f"Error reading file: {str(e)}"}, indent=2)
    
    async def search_files_tool(self, directory: str, pattern: str, max_results: int = 20) -> str:
        """Search for files matching a pattern in a directory."""
        try:
            import fnmatch
            
            # Security: Only allow paths under allowed roots
            allowed_roots = os.getenv("ALLOWED_ROOTS", "/tmp,/var/tmp,/Users/agi_dev/LOCAL-REPOS/Lukhas/test_data").split(",")
            abs_directory = os.path.abspath(directory)
            
            if not any(abs_directory.startswith(os.path.abspath(root.strip())) for root in allowed_roots):
                return json.dumps({
                    "error": f"Directory '{directory}' not allowed",
                    "allowed_roots": allowed_roots
                }, indent=2)
            
            if not os.path.exists(directory):
                return json.dumps({"error": f"Directory '{directory}' does not exist"}, indent=2)
            
            if not os.path.isdir(directory):
                return json.dumps({"error": f"Path '{directory}' is not a directory"}, indent=2)
            
            matches = []
            for root, dirs, files in os.walk(directory):
                # Only search up to 3 levels deep to prevent excessive traversal
                level = root[len(directory):].count(os.sep)
                if level >= 3:
                    dirs[:] = []  # Don't descend further
                    continue
                
                for file in files:
                    if fnmatch.fnmatch(file, pattern):
                        full_path = os.path.join(root, file)
                        file_info = {
                            "name": file,
                            "path": full_path,
                            "relative_path": os.path.relpath(full_path, directory),
                            "size_bytes": os.path.getsize(full_path)
                        }
                        matches.append(file_info)
                        
                        if len(matches) >= max_results:
                            break
                
                if len(matches) >= max_results:
                    break
            
            result = {
                "directory": directory,
                "pattern": pattern,
                "matches": matches,
                "total_found": len(matches),
                "truncated": len(matches) >= max_results,
                "lukhas_ai": "⚛️🧠🛡️ LUKHAS AI Trinity Framework"
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            logger.error(f"Error searching files in {directory}: {e}")
            return json.dumps({"error": f"Error searching files: {str(e)}"}, indent=2)
    
    async def get_lukhas_info_tool(self) -> str:
        """Get information about the LUKHAS AI system and Trinity Framework."""
        try:
            import platform
            
            info = {
                "lukhas_ai": {
                    "name": "LUKHAS AI Platform",
                    "description": "Consciousness-Aware AI Development Platform",
                    "version": "1.0.0",
                    "trinity_framework": {
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
                        "lanes": ["lukhas/", "candidate/", "matriz/", "core/", "tests/", "mcp-servers/"],
                        "protocol_version": "2025-06-18"
                    }
                },
                "mcp_server": {
                    "name": "LUKHAS AI MCP STDIO Server",
                    "transport": "STDIO",
                    "capabilities": ["tools", "file_system_access"],
                    "security": {
                        "path_sandboxing": True,
                        "allowed_roots": os.getenv("ALLOWED_ROOTS", "/tmp,/var/tmp").split(","),
                        "input_validation": True
                    }
                },
                "system": {
                    "platform": platform.platform(),
                    "python_version": platform.python_version(),
                    "architecture": platform.architecture()[0],
                    "working_directory": os.getcwd()
                }
            }
            
            return json.dumps(info, indent=2)
            
        except Exception as e:
            logger.error(f"Error getting LUKHAS info: {e}")
            return json.dumps({"error": f"Error getting system info: {str(e)}"}, indent=2)
    
    async def handle_tools_call(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/call request."""
        logger.info("Handling tools/call request")
        
        params = request.get("params", {})
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        try:
            if tool_name == "list_directory":
                result = await self.list_directory_tool(arguments.get("path", "/tmp"))
            elif tool_name == "read_file":
                result = await self.read_file_tool(
                    arguments.get("path"),
                    arguments.get("max_lines", 100)
                )
            elif tool_name == "search_files":
                result = await self.search_files_tool(
                    arguments.get("directory"),
                    arguments.get("pattern"),
                    arguments.get("max_results", 20)
                )
            elif tool_name == "get_lukhas_info":
                result = await self.get_lukhas_info_tool()
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {
                        "code": -32601,
                        "message": f"Unknown tool: {tool_name}"
                    }
                }
            
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": result
                        }
                    ]
                }
            }
            
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -32603,
                    "message": f"Internal error executing tool: {str(e)}"
                }
            }
    
    async def handle_request(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle JSON-RPC requests according to MCP specification."""
        method = request.get("method")
        
        if method == "initialize":
            return await self.handle_initialize(request)
        elif method == "tools/list":
            return await self.handle_tools_list(request)
        elif method == "tools/call":
            return await self.handle_tools_call(request)
        elif method == "notifications/initialized":
            # This is a notification, no response needed
            logger.info("Server initialized notification received")
            return None
        else:
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }
    
    async def run_stdio(self):
        """Run the MCP server with STDIO transport."""
        logger.info("Starting STDIO message loop")
        
        while True:
            try:
                # Read a line from stdin
                line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                if not line:
                    # EOF reached
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                # Parse JSON-RPC request
                try:
                    request = json.loads(line)
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON received: {e}")
                    continue
                
                # Handle the request
                response = await self.handle_request(request)
                
                # Send response if needed
                if response is not None:
                    response_json = json.dumps(response)
                    print(response_json, flush=True)
                    
            except KeyboardInterrupt:
                logger.info("Received keyboard interrupt, shutting down")
                break
            except Exception as e:
                logger.error(f"Error in STDIO loop: {e}")
                continue

async def main():
    """Main entry point."""
    # Set environment variables for security
    if not os.getenv("ALLOWED_ROOTS"):
        # Default to safe directories
        default_roots = ["/tmp", "/var/tmp"]
        # Add test data directory if it exists
        test_data_path = "/Users/agi_dev/LOCAL-REPOS/Lukhas/test_data"
        if os.path.exists(test_data_path):
            default_roots.append(test_data_path)
        os.environ["ALLOWED_ROOTS"] = ",".join(default_roots)
    
    logger.info("🚀 Starting LUKHAS AI MCP STDIO Server")
    logger.info("⚛️🧠🛡️ Trinity Framework: Identity, Consciousness, Guardian")
    logger.info(f"📁 Allowed roots: {os.getenv('ALLOWED_ROOTS')}")
    logger.info("📋 Protocol: MCP v2025-06-18 with STDIO transport")
    logger.info("🔗 Ready for ChatGPT integration")
    
    # Create and run the server
    server = LukhasMCPServer()
    await server.run_stdio()

if __name__ == "__main__":
    asyncio.run(main())