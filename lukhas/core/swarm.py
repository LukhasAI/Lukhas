"""
Swarm module for lukhas.core - compatibility layer

This module provides backward compatibility for swarm-related imports
by re-exporting classes from the colonies module.
"""

from .colonies import SwarmAgent

# For compatibility with legacy imports, import from the shim
from ..shims.core_swarm import AgentColony, SwarmHub


__all__ = ["SwarmAgent", "SwarmHub", "AgentColony"]
