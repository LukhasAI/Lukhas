"""
Neuroplastic Module Bridge
Enables cross-module communication with hormone-based signaling
"""
import streamlit as st

from collections import defaultdict
from typing import Any


class NeuroplasticBridge:
    """Central bridge for inter-module communication"""

    def __init__(self):
        self.modules = {}
        self.hormone_levels = defaultdict(float)
        self.connections = defaultdict(list)

    def register_module(self, name: str, connector: Any):
        """Register a module connector"""
        self.modules[name] = connector

    async def emit_hormone(self, hormone: str, intensity: float, source: str):
        """Emit hormone signal across all modules"""
        self.hormone_levels[hormone] = intensity

        # Notify all modules
        for connector in self.modules.values():
            if hasattr(connector, "emit_hormone"):
                connector.emit_hormone(hormone, intensity)

    def create_synapse(self, module_a: str, module_b: str):
        """Create a connection between two modules"""
        self.connections[module_a].append(module_b)
        self.connections[module_b].append(module_a)

    def get_network_state(self) -> dict[str, Any]:
        """Get current state of the neural network"""
        return {
            "modules": list(self.modules.keys()),
            "hormone_levels": dict(self.hormone_levels),
            "connections": dict(self.connections),
            "stress_level": self._calculate_stress_level(),
        }

    def _calculate_stress_level(self) -> float:
        """Calculate overall system stress"""
        stress_hormones = ["cortisol", "adrenaline", "norepinephrine"]
        total_stress = sum(self.hormone_levels.get(h, 0) for h in stress_hormones)
        return min(1.0, total_stress / 3.0)


# Global bridge instance
neural_bridge = NeuroplasticBridge()
