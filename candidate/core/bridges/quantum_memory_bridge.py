"""Quantum-Memory Bridge
Bidirectional communication bridge between Quantum and Memory systems
"""

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


class QIMemoryBridge:
    """Bridge for communication between Quantum and Memory systems."""

    def __init__(self) -> None:
        self.quantum_hub = None
        self.memory_hub = None
        self.event_mappings: dict[str, str] = {}
        self.is_connected = False
        logger.info("QuantumMemoryBridge initialized")

    async def connect(self) -> bool:
        """Establish connection between systems"""
        try:
            from lukhas.consciousness.reflection.memory_hub import get_memory_hub
            from qi.quantum_hub import get_quantum_hub

            self.quantum_hub = get_quantum_hub()
            self.memory_hub = get_memory_hub()

            self.setup_event_mappings()
            self.is_connected = True
            logger.info("Bridge connected between Quantum and Memory")
            return True
        except Exception as e:
            logger.error(f"Failed to connect bridge: {e}")
            return False

    def setup_event_mappings(self) -> None:
        """Set up event type mappings between systems"""
        self.event_mappings = {
            # quantum -> memory events
            "quantum_state_update": "memory_quantum_state",
            "quantum_result": "memory_quantum_result",
            # memory -> quantum events
            "memory_store": "quantum_memory_store",
            "memory_recall_request": "quantum_recall_request",
        }

    async def quantum_to_memory(
        self, event_type: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Forward event from Quantum to Memory"""
        if not self.is_connected:
            await self.connect()
        try:
            mapped_event = self.event_mappings.get(event_type, event_type)
            transformed = self.transform_quantum_to_memory(data)
            if self.memory_hub:
                return await self.memory_hub.process_event(mapped_event, transformed)
            return {"error": "memory hub not available"}
        except Exception as e:
            logger.error(f"Error forwarding from Quantum to Memory: {e}")
            return {"error": str(e)}

    async def memory_to_quantum(
        self, event_type: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Forward event from Memory to Quantum"""
        if not self.is_connected:
            await self.connect()
        try:
            mapped_event = self.event_mappings.get(event_type, event_type)
            transformed = self.transform_memory_to_quantum(data)
            if self.quantum_hub:
                return await self.quantum_hub.process_event(mapped_event, transformed)
            return {"error": "quantum hub not available"}
        except Exception as e:
            logger.error(f"Error forwarding from Memory to Quantum: {e}")
            return {"error": str(e)}

    def transform_quantum_to_memory(self, data: dict[str, Any]) -> dict[str, Any]:
        """Transform data format from Quantum to Memory"""
        return {
            "source_system": "quantum",
            "target_system": "memory",
            "data": data,
        }

    def transform_memory_to_quantum(self, data: dict[str, Any]) -> dict[str, Any]:
        """Transform data format from Memory to Quantum"""
        return {
            "source_system": "memory",
            "target_system": "quantum",
            "data": data,
        }

    async def health_check(self) -> dict[str, Any]:
        """Health check for the bridge"""
        return {
            "bridge": "quantum_memory_bridge",
            "connected": self.is_connected,
            "quantum_hub": self.quantum_hub is not None,
            "memory_hub": self.memory_hub is not None,
        }

    async def disconnect(self) -> None:
        """Disconnect the bridge"""
        self.is_connected = False
        logger.info("Bridge disconnected between Quantum and Memory")


# Singleton instance
_quantum_memory_bridge_instance: Optional[QuantumMemoryBridge] = None


def get_quantum_memory_bridge() -> QuantumMemoryBridge:
    """Get or create the Quantum-Memory bridge instance"""
    global _quantum_memory_bridge_instance
    if _quantum_memory_bridge_instance is None:
        _quantum_memory_bridge_instance = QuantumMemoryBridge()
    return _quantum_memory_bridge_instance
