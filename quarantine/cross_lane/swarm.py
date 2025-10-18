"""
LUKHAS Core Swarm System
Links to enhanced swarm implementations for consciousness coordination

⚛️🧠🛡️ Constellation Framework: Identity-Consciousness-Guardian
"""

# Import from the enhanced swarm implementation

try:
    # Prefer the candidate enhanced swarm when available
    from core.enhanced_swarm import (
        AgentColony,
        AgentState,
        CapabilityLevel,
        SwarmAgent,
        SwarmNetwork,
    )

    # Re-export everything the enhanced module provides
    __all__ = [
        "AgentState",
        "CapabilityLevel",
        "SwarmAgent",
        "AgentColony",
        "SwarmNetwork",
    ]
except Exception:
    # Minimal local stubs to satisfy imports when enhanced module not present
    from enum import Enum

    class AgentState(Enum):
        INACTIVE = "inactive"
        ACTIVE = "active"
        PROCESSING = "processing"

    class CapabilityLevel:
        def __init__(self, level: int = 0):
            self.level = level

    class SwarmAgent:
        def __init__(self, agent_id: str):
            self.agent_id = agent_id
            self.state = AgentState.INACTIVE

    class AgentColony:
        def __init__(self, colony_id: str):
            self.colony_id = colony_id
            self.agents = []

    class SwarmNetwork:
        def __init__(self):
            self.colonies = {}

    __all__ = [
        "AgentState",
        "CapabilityLevel",
        "SwarmAgent",
        "AgentColony",
        "SwarmNetwork",
    ]
