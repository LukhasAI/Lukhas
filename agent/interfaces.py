"""
LUKHAS Agent Orchestration Interfaces
====================================

Standard interfaces for LUKHAS agent orchestration.
Migrated from lukhas.core.orchestration.interfaces.agent_interface

Provides:
- AgentInterface (base interface)
- SimpleAgent (basic implementation)
- Agent metadata and message structures
- Agent lifecycle management

Constellation Framework: ⚛️🧠🛡️
"""

import contextlib

# Import agent interface system
_available = False
with contextlib.suppress(ImportError):
    from lukhas.core.orchestration.interfaces.agent_interface import (
        AgentCapability,
        AgentContext,
        AgentInterface,
        AgentMessage,
        AgentMetadata,
        AgentStatus,
        SimpleAgent,
    )

    _available = True

if _available:
    __all__ = [
        "AgentCapability",
        "AgentContext",
        "AgentInterface",
        "AgentMessage",
        "AgentMetadata",
        "AgentStatus",
        "SimpleAgent",
    ]
else:
    __all__ = []


def is_available() -> bool:
    """Check if agent interfaces are available"""
    return _available
