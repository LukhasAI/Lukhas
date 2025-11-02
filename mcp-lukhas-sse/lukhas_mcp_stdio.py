#!/usr/bin/env python3
"""
LUKHAS MCP STDIO Server - Official MCP Specification Compliant
Implements the Model Context Protocol v2025-06-18 with STDIO transport for ChatGPT integration.
"""

import json
import logging
import os
import sys

from mcp.server.fastmcp import FastMCP

# Configure logging to stderr (NEVER use stdout in STDIO servers)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server with LUKHAS branding
mcp = FastMCP("lukhas-ai")


@mcp.tool()
async def list_directory(path: str) -> str:
    """List files and directories in a given path.

    Args:
        path: The directory path to list (must be within allowed roots)
    """
    try:
        # Security: Only allow paths under allowed roots
        allowed_roots = os.getenv("ALLOWED_ROOTS", "/tmp,/var/tmp").split(",")
        abs_path = os.path.abspath(path)

        if not any(abs_path.startswith(os.path.abspath(root.strip())) for root in allowed_roots):
            return f"Error: Path '{path}' not allowed. Allowed roots: {', '.join(allowed_roots)}"

        if not os.path.exists(path):
            return f"Error: Path '{path}' does not exist"

        if not os.path.isdir(path):
            return f"Error: Path '{path}' is not a directory"

        items = []
        for item in sorted(os.listdir(path)):
            full_path = os.path.join(path, item)
            item_type = "directory" if os.path.isdir(full_path) else "file"
            size = os.path.getsize(full_path) if os.path.isfile(full_path) else None

            item_info = {"name": item, "type": item_type, "path": full_path}
            if size is not None:
                item_info["size"] = size

            items.append(item_info)

        result = {"path": path, "items": items, "total_items": len(items)}

        return json.dumps(result, indent=2)

    except Exception as e:
        logger.error(f"Error listing directory {path}: {e}")
        return f"Error listing directory: {str(e)}"


@mcp.tool()
async def read_file(path: str, max_lines: int = 100) -> str:
    """Read the contents of a text file.

    Args:
        path: The file path to read (must be within allowed roots)
        max_lines: Maximum number of lines to read (default: 100)
    """
    try:
        # Security: Only allow paths under allowed roots
        allowed_roots = os.getenv("ALLOWED_ROOTS", "/tmp,/var/tmp").split(",")
        abs_path = os.path.abspath(path)

        if not any(abs_path.startswith(os.path.abspath(root.strip())) for root in allowed_roots):
            return f"Error: Path '{path}' not allowed. Allowed roots: {', '.join(allowed_roots)}"

        if not os.path.exists(path):
            return f"Error: File '{path}' does not exist"

        if not os.path.isfile(path):
            return f"Error: Path '{path}' is not a regular file"

        # Check file size (limit to 1MB)
        file_size = os.path.getsize(path)
        if file_size > 1024 * 1024:  # 1MB
            return f"Error: File '{path}' is too large ({file_size} bytes). Maximum allowed: 1MB"

        with open(path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()

        # Limit the number of lines
        if len(lines) > max_lines:
            content_lines = lines[:max_lines]
            truncated = True
        else:
            content_lines = lines
            truncated = False

        content = "".join(content_lines)

        result = {
            "path": path,
            "content": content,
            "total_lines": len(lines),
            "displayed_lines": len(content_lines),
            "truncated": truncated,
            "file_size": file_size,
        }

        return json.dumps(result, indent=2)

    except UnicodeDecodeError:
        return f"Error: File '{path}' appears to be a binary file or uses unsupported encoding"
    except Exception as e:
        logger.error(f"Error reading file {path}: {e}")
        return f"Error reading file: {str(e)}"


@mcp.tool()
async def search_files(directory: str, pattern: str, max_results: int = 20) -> str:
    """Search for files matching a pattern in a directory.

    Args:
        directory: The directory to search in (must be within allowed roots)
        pattern: The filename pattern to search for (supports wildcards)
        max_results: Maximum number of results to return (default: 20)
    """
    try:
        import fnmatch

        # Security: Only allow paths under allowed roots
        allowed_roots = os.getenv("ALLOWED_ROOTS", "/tmp,/var/tmp").split(",")
        abs_directory = os.path.abspath(directory)

        if not any(abs_directory.startswith(os.path.abspath(root.strip())) for root in allowed_roots):
            return f"Error: Directory '{directory}' not allowed. Allowed roots: {', '.join(allowed_roots)}"

        if not os.path.exists(directory):
            return f"Error: Directory '{directory}' does not exist"

        if not os.path.isdir(directory):
            return f"Error: Path '{directory}' is not a directory"

        matches = []
        for root, dirs, files in os.walk(directory):
            # Only search up to 3 levels deep to prevent excessive traversal
            level = root[len(directory) :].count(os.sep)
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
                        "size": os.path.getsize(full_path),
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
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        logger.error(f"Error searching files in {directory}: {e}")
        return f"Error searching files: {str(e)}"


@mcp.tool()
async def get_system_info() -> str:
    """Get basic system information about the LUKHAS AI environment."""
    try:
        import platform

        import psutil

        info = {
            "lukhas_ai": {
                "server_name": "LUKHAS AI MCP Server",
                "version": "1.0.0",
                "protocol_version": "2025-06-18",
                "constellation_framework": "⚛️🧠🛡️ (Identity, Consciousness, Guardian)",
            },
            "system": {
                "platform": platform.platform(),
                "python_version": platform.python_version(),
                "architecture": platform.architecture()[0],
                "processor": platform.processor() or "Unknown",
            },
            "resources": {
                "cpu_count": psutil.cpu_count(),
                "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
                "disk_usage": {
                    "total_gb": round(psutil.disk_usage("/").total / (1024**3), 2),
                    "free_gb": round(psutil.disk_usage("/").free / (1024**3), 2),
                },
            },
            "environment": {
                "allowed_roots": os.getenv("ALLOWED_ROOTS", "/tmp,/var/tmp").split(","),
                "working_directory": os.getcwd(),
                "user": os.getenv("USER", "unknown"),
            },
        }

        return json.dumps(info, indent=2)

    except Exception as e:
        logger.error(f"Error getting system info: {e}")
        return f"Error getting system info: {str(e)}"


if __name__ == "__main__":
    # Set environment variables for security
    if not os.getenv("ALLOWED_ROOTS"):
        os.environ["ALLOWED_ROOTS"] = "/tmp,/var/tmp,/Users/cognitive_dev/LOCAL-REPOS/Lukhas/test_data"

    logger.info("🚀 Starting LUKHAS AI MCP STDIO Server")
    logger.info("⚛️🧠🛡️ Constellation Framework: Identity, Consciousness, Guardian")
    logger.info(f"📁 Allowed roots: {os.getenv('ALLOWED_ROOTS')}")
    logger.info("📋 Protocol: MCP v2025-06-18 with STDIO transport")
    logger.info("🔗 Ready for ChatGPT integration")

    # Run the server with STDIO transport (required for ChatGPT)
    mcp.run(transport="stdio")
