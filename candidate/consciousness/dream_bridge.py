#!/usr/bin/env python3
"""
Dream-Consciousness Bridge
Implements the critical connection between dream synthesis and consciousness.
"""
import logging
from typing import Any

try:
    from dream.engine import DreamEngine
except ImportError:
    DreamEngine = None

from candidate.core.orchestration.integration_hub import get_integration_hub

try:
    from consciousness.bridge import ConsciousnessBridge
except ImportError:
    ConsciousnessBridge = None

try:
    from candidate.memory.core import MemoryCore
except ImportError:
    MemoryCore = None

logger = logging.getLogger(__name__)


class DreamConsciousnessBridge:
    """
    Bridges dream synthesis with consciousness processing.
    This enables dreams to influence consciousness and vice versa.
    """

    def __init__(self):
        self.consciousness = ConsciousnessBridge() if ConsciousnessBridge else None
        self.dream_engine = DreamEngine() if DreamEngine else None
        self.memory = MemoryCore() if MemoryCore else None

    async def process_dream_to_consciousness(self, dream_data: dict[str, Any]) -> dict[str, Any]:
        """Process dream data through consciousness."""
        # Store dream in memory if available
        if self.memory:
            await self.memory.store_dream(dream_data)

        # Process through consciousness if available
        if self.consciousness:
            consciousness_result = await self.consciousness.process_dream(dream_data)

            # Update dream engine with consciousness feedback if available
            if self.dream_engine:
                await self.dream_engine.update_from_consciousness(consciousness_result)

            return consciousness_result

        # Return empty result if consciousness bridge not available
        return {"status": "consciousness_bridge_unavailable", "dream_data": dream_data}

    async def process_consciousness_to_dream(self, consciousness_data: dict[str, Any]) -> dict[str, Any]:
        """Generate dreams from consciousness states."""
        if not self.consciousness or not self.dream_engine:
            return {"status": "components_unavailable", "consciousness_data": consciousness_data}

        # Analyze consciousness state
        dream_seed = await self.consciousness.extract_dream_seed(consciousness_data)

        # Generate dream
        dream_result = await self.dream_engine.synthesize_from_seed(dream_seed)

        # Store the synthesis if memory available
        if self.memory:
            await self.memory.store_synthesis(consciousness_data, dream_result)

        return dream_result


# 🔁 Cross-layer: Dream-consciousness integration


def register_with_hub():
    """Register this bridge with the integration hub."""
    try:
        hub = get_integration_hub()
        bridge = DreamConsciousnessBridge()
        hub.register_component("dream_consciousness_bridge", bridge)
    except ImportError as e:
        logger.warning(f"Could not register with integration hub: {e}")


# Auto-register on import (with error handling) - Disabled to prevent event loop issues
# Register manually when needed instead of auto-registering
# try:
#     register_with_hub()
# except Exception as e:
#     logger.warning(f"Failed to auto-register dream bridge: {e}")
