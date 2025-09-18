#!/usr/bin/env python3
"""
LUKHAS AI MCP Server for ChatGPT Integration
STDIO Transport - Official MCP Specification v2025-06-18
"""

import os
import sys

# Add the directory containing our server to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import and run our server
from lukhas_mcp_stdio_manual import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())