"""LUKHAS Tool Registry ⚛️🛡️
Canonical tool registry for OpenAI function-calling with governance.
"""

from typing import Any

from lukhas_pwm.flags.ff import Flags

# Canonical tool registry (JSON-schema-like) used to expose tools to OpenAI function-calling.
# Keep descriptions concise; expand schemas as needed.

_REGISTRY: dict[str, dict[str, Any]] = {
    "retrieval": {
        "type": "function",
        "function": {
            "name": "retrieve_knowledge",
            "description": "Fetch top-K relevant notes or documents.",
            "parameters": {
                "type": "object",
                "properties": {
                    "k": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 20,
                        "description": "Number of results to return",
                    },
                    "query": {"type": "string", "description": "Search query"},
                },
                "required": ["query"],
            },
        },
    },
    "browser": {
        "type": "function",
        "function": {
            "name": "open_url",
            "description": "Open a URL in a sandboxed browser and return text.",
            "parameters": {
                "type": "object",
                "properties": {"url": {"type": "string", "description": "URL to open"}},
                "required": ["url"],
            },
        },
    },
    "scheduler": {
        "type": "function",
        "function": {
            "name": "schedule_task",
            "description": "Schedule a reminder or follow-up task.",
            "parameters": {
                "type": "object",
                "properties": {
                    "when": {
                        "type": "string",
                        "description": "When to schedule (human readable)",
                    },
                    "note": {
                        "type": "string",
                        "description": "Task description",
                    },
                },
                "required": ["when", "note"],
            },
        },
    },
    "code_exec": {
        "type": "function",
        "function": {
            "name": "exec_code",
            "description": "Execute sandboxed code for analysis (non-networked).",
            "parameters": {
                "type": "object",
                "properties": {
                    "language": {
                        "type": "string",
                        "enum": ["python", "javascript", "bash"],
                        "description": "Programming language",
                    },
                    "source": {
                        "type": "string",
                        "description": "Source code to execute",
                    },
                },
                "required": ["language", "source"],
            },
        },
    },
}


def build_tools_from_allowlist(allowlist: list[str]) -> list[dict[str, Any]]:
    """Return tool schemas restricted to the provided allowlist (order preserved).

    Args:
        allowlist: List of tool names to allow

    Returns:
        List of OpenAI function tool schemas
    """
    out: list[dict[str, Any]] = []
    for name in allowlist or []:
        # Gate browser tool with FLAG_BROWSER_TOOL
        if name == "browser" and not Flags.get("BROWSER_TOOL", False):
            # Skip browser tool if flag is disabled
            continue

        tool = _REGISTRY.get(name)
        if tool:
            out.append(tool)
    return out


def get_all_tools() -> dict[str, dict[str, Any]]:
    """Return the complete tool registry."""
    return _REGISTRY.copy()


def get_tool_names() -> list[str]:
    """Return list of all available tool names."""
    return list(_REGISTRY.keys())
