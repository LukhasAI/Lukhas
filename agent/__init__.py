"""
LUKHAS AI Agent System
=====================

Consolidated LUKHAS consciousness agent system.
Real LUKHAS agents for internal consciousness operations.

This is the main LUKHAS agent system containing:
- Core AI Agents (AIAgentActor, SupervisorAgent)
- Agent Interfaces (AgentInterface, SimpleAgent)
- Collaborative Agents (LukhasAIAgent, LukhasAIAgentTeam)
- Intelligence Bridge (Agent-Intelligence communication)
- Orchestration Agents (Multi-agent coordination)

Constellation Framework: ⚛️🧠🛡️
Author: LUKHAS AI Agent Systems
Version: 2.0.0
"""

import contextlib
from typing import Any, Optional

# Core LUKHAS agent implementations
try:
    from core.actor_system import AIAgentActor
    from core.supervisor_agent import SupervisorAgent, get_supervisor_agent

    _core_agents_available = True
except ImportError as e:
    print(f"Warning: Core agents not available: {e}")
    _core_agents_available = False

# Agent interfaces and orchestration
_agent_interfaces_available = False
with contextlib.suppress(ImportError):
    from core.orchestration.interfaces.agent_interface import (
        AgentCapability,
        AgentContext,
        AgentInterface,
        AgentMessage,
        AgentMetadata,
        AgentStatus,
        SimpleAgent,
    )

    _agent_interfaces_available = True

# Collaborative agent system
_collaborative_agents_available = False
with contextlib.suppress(ImportError):
    from core.orchestration.brain.collaborative_ai_agent_system import (
        AgentCapabilities,
        AgentTier,
        LukhasAIAgent,
        LukhasAIAgentTeam,
    )

    _collaborative_agents_available = True

# Intelligence bridge
_intelligence_bridge_available = False
with contextlib.suppress(ImportError):
    from orchestration.agent_orchestrator.intelligence_bridge import (
        AgentIntelligenceBridge,
        AgentType,
        IntelligenceRequestType,
    )

    _intelligence_bridge_available = True

__version__ = "2.0.0"

# Build __all__ based on what's actually available
__all__ = []

if _core_agents_available:
    __all__.extend(
        [
            "AIAgentActor",
            "SupervisorAgent",
            "get_supervisor_agent",
        ]
    )

if _agent_interfaces_available:
    __all__.extend(
        [
            "AgentCapability",
            "AgentContext",
            "AgentInterface",
            "AgentMessage",
            "AgentMetadata",
            "AgentStatus",
            "SimpleAgent",
        ]
    )

if _collaborative_agents_available:
    __all__.extend(
        [
            "AgentCapabilities",
            "AgentTier",
            "LukhasAIAgent",
            "LukhasAIAgentTeam",
        ]
    )

if _intelligence_bridge_available:
    __all__.extend(
        [
            "AgentIntelligenceBridge",
            "AgentType",
            "IntelligenceRequestType",
        ]
    )

# Export availability flags for runtime checks
__all__.extend(
    [
        "_agent_interfaces_available",
        "_collaborative_agents_available",
        "_core_agents_available",
        "_intelligence_bridge_available",
    ]
)


# Agent system status
def get_agent_system_status() -> dict[str, Any]:
    """Get comprehensive status of LUKHAS agent system"""
    return {
        "version": __version__,
        "core_agents": _core_agents_available,
        "agent_interfaces": _agent_interfaces_available,
        "collaborative_agents": _collaborative_agents_available,
        "intelligence_bridge": _intelligence_bridge_available,
        "total_components": len(__all__),
        "operational_status": "READY" if _core_agents_available else "LIMITED",
    }


__all__.append("get_agent_system_status")
