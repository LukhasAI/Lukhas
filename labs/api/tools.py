"""Tools Registry API ⚛️🛡️
Registry endpoint for OpenAI function-calling tools with governance.
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from openai.tooling import get_all_tools, get_tool_names

router = APIRouter(prefix="/tools", tags=["tools"])


@router.get("/registry")
def get_tools_registry():
    """Get the complete tools registry with schemas"""
    return JSONResponse(
        content={
            "tools": get_all_tools(),
            "available_tools": get_tool_names(),
            "registry_info": {
                "version": "1.0",
                "governance": "LUKHAS Guardian System",
                "safety_mode": "tool_allowlist_required",
            },
        }
    )


@router.get("/available")
def get_available_tools():
    """Get list of available tool names"""
    return JSONResponse(
        content={
            "available_tools": get_tool_names(),
            "count": len(get_tool_names()),
        }
    )


@router.get("/{tool_name}")
def get_tool_schema(tool_name: str):
    """Get schema for a specific tool"""
    tools_registry = get_all_tools()

    if tool_name not in tools_registry:
        return JSONResponse(
            status_code=404,
            content={
                "error": f"Tool '{tool_name}' not found",
                "available": get_tool_names(),
            },
        )

    return JSONResponse(
        content={
            "tool_name": tool_name,
            "schema": tools_registry[tool_name],
            "governance": "Requires inclusion in tool_allowlist",
        }
    )
