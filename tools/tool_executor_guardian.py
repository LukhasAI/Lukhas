"""Bridge module for tools.tool_executor_guardian → labs.tools.tool_executor_guardian"""
from __future__ import annotations

from labs.tools.tool_executor_guardian import ToolExecutorGuardian, get_tool_executor_guardian

# Export main classes and functions for backward compatibility
__all__ = ["ToolExecutorGuardian", "get_tool_executor_guardian"]
