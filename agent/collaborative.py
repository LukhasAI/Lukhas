"""
LUKHAS Collaborative Agent System
================================

Advanced multi-agent collaboration framework.
Migrated from candidate.core.orchestration.brain.collaborative_ai_agent_system

Includes:
- LukhasAIAgent (base agent class)
- LukhasAIAgentTeam (multi-agent coordination)
- AgentTier (permission levels)
- AgentCapabilities (agent feature sets)

Trinity Framework: ⚛️🧠🛡️
"""

import contextlib

# Import collaborative agent system
_available = False
with contextlib.suppress(ImportError):
    from candidate.core.orchestration.brain.collaborative_ai_agent_system import (
        AgentCapabilities,
        AgentTier,
        ConsolidationPhase,
        LukhasAIAgent,
        LukhasAIAgentTeam,
    )

    _available = True

if _available:
    __all__ = [
        "LukhasAIAgent",
        "LukhasAIAgentTeam",
        "AgentTier",
        "AgentCapabilities",
        "ConsolidationPhase",
    ]
else:
    __all__ = []


def is_available() -> bool:
    """Check if collaborative agent system is available"""
    return _available
