"""
LUKHAS Collaborative Agent System
================================

Advanced multi-agent collaboration framework.
Migrated from core.orchestration.brain.collaborative_ai_agent_system

Includes:
- LukhasAIAgent (base agent class)
- LukhasAIAgentTeam (multi-agent coordination)
- AgentTier (permission levels)
- AgentCapabilities (agent feature sets)

Constellation Framework: ⚛️🧠🛡️
"""

import contextlib

# Import collaborative agent system
_available = False
with contextlib.suppress(ImportError):
    from core.orchestration.brain.collaborative_ai_agent_system import (
        AgentCapabilities,
        AgentTier,
        ConsolidationPhase,
        LukhasAIAgent,
        LukhasAIAgentTeam,
    )

    _available = True

if _available:
    __all__ = [
        "AgentCapabilities",
        "AgentTier",
        "ConsolidationPhase",
        "LukhasAIAgent",
        "LukhasAIAgentTeam",
    ]
else:
    __all__ = []


def is_available() -> bool:
    """Check if collaborative agent system is available"""
    return _available
