import logging
from datetime import timezone
import streamlit as st
logger = logging.getLogger(__name__)
"""
Dream Bridge Adapter for Consciousness Hub
Provides the DreamBridge interface required by consciousness_hub
"""

from datetime import datetime
from typing import Any

from candidate.core.common import get_logger

from .dream_bridge import DreamConsciousnessBridge

logger = get_logger(__name__, timezone)


class DreamBridge:
    """
    Adapter class to provide the expected DreamBridge interface
    for the consciousness hub integration
    """

    def __init__(self):
        self.bridge = DreamConsciousnessBridge()
        self.is_initialized = False
        self.active_dreams = {}
        self.consciousness_feedback = []

    async def initialize(self):
        """Initialize the dream bridge"""
        try:
            # Initialize underlying bridge
            if hasattr(self.bridge.consciousness, "initialize"):
                await self.bridge.consciousness.initialize()
            if hasattr(self.bridge.dream_engine, "initialize"):
                await self.bridge.dream_engine.initialize()
            if hasattr(self.bridge.memory, "initialize"):
                await self.bridge.memory.initialize()

            self.is_initialized = True
            logger.info("Dream bridge initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize dream bridge: {e}")
            raise

    async def process_consciousness_state(self, state: dict[str, Any]) -> dict[str, Any]:
        """Process a consciousness state through the dream bridge"""
        if not self.is_initialized:
            await self.initialize()

        # Generate dream from consciousness
        dream_result = await self.bridge.process_consciousness_to_dream(state)

        # Store active dream
        dream_id = f"dream_{datetime.now(timezone.utc).timestamp()}"
        self.active_dreams[dream_id] = dream_result

        return {"dream_id": dream_id, "dream_data": dream_result, "status": "active"}

    async def integrate_dream_feedback(self, dream_id: str, feedback: dict[str, Any]) -> dict[str, Any]:
        """Integrate feedback from a dream back into consciousness"""
        if dream_id not in self.active_dreams:
            return {"error": "Dream not found", "dream_id": dream_id}

        dream_data = self.active_dreams[dream_id]

        # Process dream through consciousness
        consciousness_result = await self.bridge.process_dream_to_consciousness(dream_data)

        # Store feedback
        self.consciousness_feedback.append(
            {
                "dream_id": dream_id,
                "feedback": feedback,
                "consciousness_result": consciousness_result,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

        return consciousness_result

    async def get_active_dreams(self) -> dict[str, Any]:
        """Get all currently active dreams"""
        return {
            "active_dreams": list(self.active_dreams.keys()),
            "count": len(self.active_dreams),
            "dreams": self.active_dreams,
        }

    async def clear_dream(self, dream_id: str) -> bool:
        """Clear a specific dream from active memory"""
        if dream_id in self.active_dreams:
            del self.active_dreams[dream_id]
            return True
        return False

    async def get_consciousness_feedback_history(self) -> list:
        """Get the history of consciousness feedback"""
        return self.consciousness_feedback

    async def update_awareness(self, awareness_state: dict[str, Any]):
        """Update dream bridge with current awareness state"""
        # This method is called by consciousness hub during awareness broadcasts
        logger.debug(f"Dream bridge received awareness update: {awareness_state}")

        # Potentially adjust dream synthesis based on awareness level
        if awareness_state.get("level") == "active":
            # More vivid dreams during active awareness
            if hasattr(self.bridge.dream_engine, "set_vividness"):
                await self.bridge.dream_engine.set_vividness(0.8)
        elif awareness_state.get("level") == "passive":
            # More abstract dreams during passive awareness
            if hasattr(self.bridge.dream_engine, "set_vividness"):
                await self.bridge.dream_engine.set_vividness(0.4)