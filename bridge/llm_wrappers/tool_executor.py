"""
Compatibility bridge for tool execution used by tests.

Exports an execute_tool function and ToolExecutionError class so tests can
monkeypatch without touching core executor internals.
"""

from typing import Any

from tools.tool_executor import get_tool_executor


class ToolExecutionError(Exception):
    pass


async def execute_tool(tool_name: str, args_json: Any):
    executor = get_tool_executor()
    return await executor.execute(tool_name, args_json)
