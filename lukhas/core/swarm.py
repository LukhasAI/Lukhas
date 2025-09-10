"""
Swarm module for lukhas.core - compatibility layer

This module provides backward compatibility for swarm-related imports
by re-exporting classes from the colonies module.
"""

from .colonies import SwarmAgent

# For compatibility with legacy imports
# Fallback implementations if candidate module unavailable
class SwarmHub:
    """Fallback SwarmHub implementation"""

    def __init__(self, *args, **kwargs):
        pass

class AgentColony:
    """Fallback AgentColony implementation"""

    def __init__(self, *args, **kwargs):
        pass


__all__ = ["SwarmAgent", "SwarmHub", "AgentColony"]
