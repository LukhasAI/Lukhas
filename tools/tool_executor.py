"""Bridge module for tools.tool_executor → labs.tools.tool_executor"""
from __future__ import annotations

from labs.tools.tool_executor import ToolExecutor

# Export main class for backward compatibility
__all__ = ["ToolExecutor"]
