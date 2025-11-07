"""
Shim module for core.swarm components.

This module provides fallback implementations for swarm-related classes
to ensure backward compatibility and avoid cross-lane imports from lukhas.
"""

class SwarmHub:
    """Fallback SwarmHub implementation"""

    def __init__(self, *args, **kwargs):
        pass

class AgentColony:
    """Fallback AgentColony implementation"""

    def __init__(self, *args, **kwargs):
        pass

__all__ = ["AgentColony", "SwarmHub"]
