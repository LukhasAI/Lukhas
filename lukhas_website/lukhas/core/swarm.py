"""
Swarm module for core - compatibility layer

This module provides backward compatibility for swarm-related imports
by re-exporting classes from the colonies module.
"""

# For compatibility with legacy imports, import from the shim
from ..shims.core_swarm import AgentColony, SwarmHub
from .colonies import SwarmAgent

__all__ = ["SwarmAgent", "SwarmHub", "AgentColony"]
