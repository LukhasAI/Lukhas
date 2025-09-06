"""
LUKHAS Agent Intelligence Bridge
==============================

Communication layer between LUKHAS agents and intelligence engines.
Migrated from candidate.orchestration.agent_orchestrator.intelligence_bridge

Provides standardized API for agent-driven intelligence operations.
Enables 6 specialized Claude Code agents to coordinate intelligence engine operations.

Trinity Framework: ⚛️🧠🛡️
"""

import contextlib

# Import intelligence bridge system
_available = False
with contextlib.suppress(ImportError):
    from candidate.orchestration.agent_orchestrator.intelligence_bridge import (
        AgentIntelligenceBridge,
        AgentType,
        IntelligenceRequestType,
    )
    _available = True

__all__ = [
    "AgentIntelligenceBridge",
    "AgentType",
    "IntelligenceRequestType",
] if _available else []

def is_available() -> bool:
    """Check if intelligence bridge is available"""
    return _available
