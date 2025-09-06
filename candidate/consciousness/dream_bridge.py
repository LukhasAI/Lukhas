#!/usr/bin/env python3
"""
Dream-Consciousness Bridge
Implements the critical connection between dream synthesis and consciousness.
"""

from typing import Any

from dream.engine import DreamEngine

from candidate.orchestration.integration_hub import get_integration_hub
from consciousness.bridge import ConsciousnessBridge
from lukhas.memory.core import MemoryCore


class DreamConsciousnessBridge:
    """
    Bridges dream synthesis with consciousness processing.
    This enables dreams to influence consciousness and vice versa.
    """

    def __init__(self):
        self.consciousness = ConsciousnessBridge()
        self.dream_engine = DreamEngine()
        self.memory = MemoryCore()

    async def process_dream_to_consciousness(self, dream_data: dict[str, Any]) -> dict[str, Any]:
        """Process dream data through consciousness."""
        # Store dream in memory
        await self.memory.store_dream(dream_data)

        # Process through consciousness
        consciousness_result = await self.consciousness.process_dream(dream_data)

        # Update dream engine with consciousness feedback
        await self.dream_engine.update_from_consciousness(consciousness_result)

        return consciousness_result

    async def process_consciousness_to_dream(self, consciousness_data: dict[str, Any]) -> dict[str, Any]:
        """Generate dreams from consciousness states."""
        # Analyze consciousness state
        dream_seed = await self.consciousness.extract_dream_seed(consciousness_data)

        # Generate dream
        dream_result = await self.dream_engine.synthesize_from_seed(dream_seed)

        # Store the synthesis
        await self.memory.store_synthesis(consciousness_data, dream_result)

        return dream_result


# 🔁 Cross-layer: Dream-consciousness integration


def register_with_hub():
    """Register this bridge with the integration hub."""
    hub = get_integration_hub()
    bridge = DreamConsciousnessBridge()
    hub.register_component("dream_consciousness_bridge", bridge)


# Auto-register on import
register_with_hub()
