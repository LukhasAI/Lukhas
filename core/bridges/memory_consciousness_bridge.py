"""Memory-Consciousness Bridge
Bidirectional communication bridge between memory and consciousness systems
"""

from typing import Any, Dict, Optional
import asyncio
import logging

logger = logging.getLogger(__name__)


class MemoryConsciousnessBridge:
    """Bridge for communication between Memory and Consciousness systems."""

    def __init__(self) -> None:
        self.memory_hub = None
        self.consciousness_hub = None
        self.event_mappings: Dict[str, str] = {}
        self.is_connected = False
        logger.info("MemoryConsciousnessBridge initialized")

    async def connect(self) -> bool:
        """Establish connection between systems"""
        try:
            from consciousness.reflection.memory_hub import get_memory_hub
            from consciousness.reflection.consciousness_hub import get_consciousness_hub

            self.memory_hub = get_memory_hub()
            self.consciousness_hub = get_consciousness_hub()

            self.setup_event_mappings()
            self.is_connected = True
            logger.info("Bridge connected between Memory and Consciousness")
            return True
        except Exception as e:
            logger.error(f"Failed to connect bridge: {e}")
            return False

    def setup_event_mappings(self) -> None:
        """Set up event type mappings between systems"""
        self.event_mappings = {
            # memory -> consciousness events
            "memory_recall": "consciousness_memory_recall",
            "memory_update": "consciousness_memory_update",
            # consciousness -> memory events
            "consciousness_state": "memory_context_update",
            "consciousness_event": "memory_event",
        }

    async def memory_to_consciousness(self, event_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Forward event from Memory to Consciousness"""
        if not self.is_connected:
            await self.connect()
        try:
            mapped_event = self.event_mappings.get(event_type, event_type)
            transformed = self.transform_memory_to_consciousness(data)
            if self.consciousness_hub:
                return await self.consciousness_hub.process_event(mapped_event, transformed)
            return {"error": "consciousness hub not available"}
        except Exception as e:
            logger.error(f"Error forwarding from Memory to Consciousness: {e}")
            return {"error": str(e)}

    async def consciousness_to_memory(self, event_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Forward event from Consciousness to Memory"""
        if not self.is_connected:
            await self.connect()
        try:
            mapped_event = self.event_mappings.get(event_type, event_type)
            transformed = self.transform_consciousness_to_memory(data)
            if self.memory_hub:
                return await self.memory_hub.process_event(mapped_event, transformed)
            return {"error": "memory hub not available"}
        except Exception as e:
            logger.error(f"Error forwarding from Consciousness to Memory: {e}")
            return {"error": str(e)}

    def transform_memory_to_consciousness(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform data format from Memory to Consciousness"""
        return {
            "source_system": "memory",
            "target_system": "consciousness",
            "data": data,
        }

    def transform_consciousness_to_memory(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform data format from Consciousness to Memory"""
        return {
            "source_system": "consciousness",
            "target_system": "memory",
            "data": data,
        }

    async def health_check(self) -> Dict[str, Any]:
        """Health check for the bridge"""
        return {
            "bridge": "memory_consciousness_bridge",
            "connected": self.is_connected,
            "memory_hub": self.memory_hub is not None,
            "consciousness_hub": self.consciousness_hub is not None,
        }

    async def disconnect(self) -> None:
        """Disconnect the bridge"""
        self.is_connected = False
        logger.info("Bridge disconnected between Memory and Consciousness")


# Singleton instance
_memory_consciousness_bridge_instance: Optional[MemoryConsciousnessBridge] = None


def get_memory_consciousness_bridge() -> MemoryConsciousnessBridge:
    """Get or create the Memory-Consciousness bridge instance"""
    global _memory_consciousness_bridge_instance
    if _memory_consciousness_bridge_instance is None:
        _memory_consciousness_bridge_instance = MemoryConsciousnessBridge()
    return _memory_consciousness_bridge_instance
