from typing import Optional

from .consciousness_quantum_bridge import ConsciousnessQuantumBridge
from .core_consciousness_bridge import CoreConsciousnessBridge
from .core_safety_bridge import CoreSafetyBridge
from .identity_core_bridge import IdentityCoreBridge
from .memory_consciousness_bridge import get_memory_consciousness_bridge
from .memory_learning_bridge import (
    MemoryLearningBridge,
    get_memory_learning_bridge,
)
from .nias_dream_bridge import get_nias_dream_bridge
from .quantum_memory_bridge import get_quantum_memory_bridge

# from .orchestration_core_bridge import OrchestrationCoreBridge


class BridgeRegistry:
    """Central registry for all system bridges"""

    def __init__(self) -> None:
        self.bridges = {
            "core_consciousness": CoreConsciousnessBridge,
            "consciousness_quantum": ConsciousnessQuantumBridge,
            "core_safety": CoreSafetyBridge,
            "memory_consciousness": get_memory_consciousness_bridge,
            "nias_dream": get_nias_dream_bridge,
            "quantum_memory": get_quantum_memory_bridge,
            "memory_learning": get_memory_learning_bridge,
        }

    def get_bridge(self, bridge_name: str):
        """Get a bridge by name"""
        factory = self.bridges.get(bridge_name)
        if factory is None:
            return None
        return factory() if callable(factory) else factory

    async def connect_all(self) -> dict[str, bool]:
        """Connect all bridges"""
        results = {}
        for name, factory in self.bridges.items():
            bridge = factory() if callable(factory) else factory
            if hasattr(bridge, "connect"):
                results[name] = await bridge.connect()
            else:
                results[name] = False
        return results

    async def health_check_all(self) -> dict[str, any]:
        """Health check all bridges"""
        results = {}
        for name, factory in self.bridges.items():
            bridge = factory() if callable(factory) else factory
            if hasattr(bridge, "health_check"):
                results[name] = await bridge.health_check()
            else:
                results[name] = {"status": "unknown"}
        return results


_bridge_registry: Optional[BridgeRegistry] = None


def get_bridge_registry() -> BridgeRegistry:
    """Get or create bridge registry singleton"""
    global _bridge_registry
    if _bridge_registry is None:
        _bridge_registry = BridgeRegistry()
    return _bridge_registry


__all__ = [
    "CoreConsciousnessBridge",
    "ConsciousnessQuantumBridge",
    "CoreSafetyBridge",
    "MemoryLearningBridge",
    "get_memory_learning_bridge",
    "get_memory_consciousness_bridge",
    "get_quantum_memory_bridge",
    "get_nias_dream_bridge",
    "IdentityCoreBridge",
    # "OrchestrationCoreBridge",
    "BridgeRegistry",
    "get_bridge_registry",
]
