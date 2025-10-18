"""
LUKHAS AI Agent System Bridge
============================

Bridge module connecting agents to the root /agent system.
The real LUKHAS consciousness agents are now located in /agent directory.

This module provides backward compatibility while directing users
to the consolidated agent system at root level.

Constellation Framework: ⚛️🧠🛡️
Author: LUKHAS AI Agent Systems
Version: 2.0.0 (Bridge to /agent)
"""

import contextlib
import sys
import time
from pathlib import Path
from typing import Any, Optional

import streamlit as st

# Add root agent directory to path
_agent_path = Path(__file__).parent.parent.parent / "agent"
if str(_agent_path) not in sys.path:
    sys.path.insert(0, str(_agent_path))

# Import from consolidated agent system
try:
    from agent import (
        AIAgentActor,
        SupervisorAgent,
        get_agent_system_status,
        get_supervisor_agent,
    )

    _core_agents_available = True
except ImportError as e:
    print(f"Warning: Core agents not available: {e}")
    _core_agents_available = False

# Import agent interfaces
_agent_interfaces_available = False
with contextlib.suppress(ImportError):
    from agent import (
        AgentCapability,
        AgentContext,
        AgentInterface,
        AgentMessage,
        AgentMetadata,
        AgentStatus,
        SimpleAgent,
    )

    _agent_interfaces_available = True

# Import collaborative agents
_collaborative_agents_available = False
with contextlib.suppress(ImportError):
    from agent import (
        AgentCapabilities,
        AgentTier,
        LukhasAIAgent,
        LukhasAIAgentTeam,
    )

    _collaborative_agents_available = True

# Import intelligence bridge
_intelligence_bridge_available = False
with contextlib.suppress(ImportError):
    from agent import (
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
            "get_agent_system_status",
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

# Note: This bridge module provides access to the consolidated agent system
# Real LUKHAS agents are in /agent directory (not /agents_external)
