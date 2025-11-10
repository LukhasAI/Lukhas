"""Bridge module for tools.tool_orchestrator → labs.tools.tool_orchestrator"""
from __future__ import annotations

from labs.tools.tool_orchestrator import MultiAIConsensus, ToolOrchestrator

# Export main classes for backward compatibility
__all__ = ["MultiAIConsensus", "ToolOrchestrator"]
