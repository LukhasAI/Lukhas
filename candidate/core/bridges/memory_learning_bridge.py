"""
Memory-Learning Bridge
Bidirectional communication bridge between Memory and Learning systems
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class MemoryLearningBridge:
    """
    Bridge for communication between Memory and Learning systems.

    Provides:
    - Episodic Memory ↔ Experience Learning
    - Semantic Memory ↔ Concept Learning
    - Working Memory ↔ Active Learning
    - Long-term Memory ↔ Knowledge Retention
    - Memory Consolidation ↔ Learning Consolidation
    - Memory Recall ↔ Learning Application
    - Memory Formation ↔ Learning Acquisition
    - Memory Forgetting ↔ Learning Optimization
    - Memory Association ↔ Learning Generalization
    """

    def __init__(self):
        self.memory_hub = None  # Will be initialized later
        self.learning_hub = None
        self.event_mappings = {}
        self.learning_feedback_enabled = True
        self.is_connected = False

        logger.info("Memory-Learning Bridge initialized")

    async def connect(self) -> bool:
        """Establish connection between Memory and Learning systems"""
        try:
            # Get system hubs
            from learning.learning_hub import get_learning_hub

            from lukhas.consciousness.reflection.memory_hub import get_memory_hub

            self.memory_hub = get_memory_hub()
            self.learning_hub = get_learning_hub()

            # Set up event mappings
            self.setup_event_mappings()

            self.is_connected = True
            logger.info("Bridge connected between Memory and Learning systems")
            return True

        except Exception as e:
            logger.error(f"Failed to connect Memory-Learning bridge: {e}")
            return False

    def setup_event_mappings(self):
        """Set up event type mappings between systems"""
        self.event_mappings = {
            # Memory -> Learning events
            "memory_formation": "learning_acquisition",
            "memory_recall": "learning_application",
            "memory_consolidation": "learning_consolidation",
            "memory_association": "learning_generalization",
            "memory_forgetting": "learning_optimization",
            "episodic_memory_event": "experience_learning",
            "semantic_memory_update": "concept_learning",
            "working_memory_activity": "active_learning",
            "long_term_memory_access": "knowledge_retention",
            # Learning -> Memory events
            "learning_acquisition": "memory_formation_trigger",
            "learning_application": "memory_recall_request",
            "learning_consolidation": "memory_consolidation_trigger",
            "learning_generalization": "memory_association_update",
            "learning_optimization": "memory_forgetting_signal",
            "experience_learned": "episodic_memory_update",
            "concept_learned": "semantic_memory_update",
            "active_learning_state": "working_memory_activation",
            "knowledge_retained": "long_term_memory_strengthen",
        }

    async def memory_to_learning(self, event_type: str, data: dict[str, Any]) -> dict[str, Any]:
        """Forward event from Memory to Learning system"""
        if not self.is_connected:
            await self.connect()

        try:
            # Map event type
            mapped_event = self.event_mappings.get(event_type, event_type)

            # Transform data for learning processing
            transformed_data = self.transform_data_memory_to_learning(data)

            # Send to learning system
            if self.learning_hub:
                result = await self.learning_hub.process_event(mapped_event, transformed_data)
                logger.debug(f"Forwarded {event_type} from Memory to Learning")
                return result

            return {"error": "learning hub not available"}

        except Exception as e:
            logger.error(f"Error forwarding from Memory to Learning: {e}")
            return {"error": str(e)}

    async def learning_to_memory(self, event_type: str, data: dict[str, Any]) -> dict[str, Any]:
        """Forward event from Learning to Memory system"""
        if not self.is_connected:
            await self.connect()

        try:
            # Map event type
            mapped_event = self.event_mappings.get(event_type, event_type)

            # Transform data for memory processing
            transformed_data = self.transform_data_learning_to_memory(data)

            # Send to memory system
            if self.memory_hub:
                result = await self.memory_hub.process_event(mapped_event, transformed_data)
                logger.debug(f"Forwarded {event_type} from Learning to Memory")
                return result

            return {"error": "memory hub not available"}

        except Exception as e:
            logger.error(f"Error forwarding from Learning to Memory: {e}")
            return {"error": str(e)}

    def transform_data_memory_to_learning(self, data: dict[str, Any]) -> dict[str, Any]:
        """Transform data format from Memory to Learning"""
        return {
            "source_system": "memory",
            "target_system": "learning",
            "data": data,
            "learning_context": True,
            "timestamp": self._get_timestamp(),
            "bridge_version": "1.0",
        }

    def transform_data_learning_to_memory(self, data: dict[str, Any]) -> dict[str, Any]:
        """Transform data format from Learning to Memory"""
        return {
            "source_system": "learning",
            "target_system": "memory",
            "data": data,
            "memory_context": True,
            "timestamp": self._get_timestamp(),
            "bridge_version": "1.0",
        }

    async def register_learning_feedback(self, memory_event: str, learning_data: dict[str, Any]):
        """Register memory events for learning feedback"""
        if not self.learning_feedback_enabled:
            return

        try:
            feedback_data = {
                "memory_event": memory_event,
                "learning_feedback": learning_data,
                "feedback_type": "memory_to_learning",
                "timestamp": self._get_timestamp(),
            }

            await self.memory_to_learning("memory_feedback", feedback_data)
            logger.debug(f"Registered learning feedback for {memory_event}")

        except Exception as e:
            logger.warning(f"Failed to register learning feedback: {e}")

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime

        return datetime.now(, timezone).isoformat()

    async def health_check(self) -> dict[str, Any]:
        """Health check for the bridge"""
        health = {
            "bridge_status": ("healthy" if self.is_connected else "disconnected"),
            "memory_hub_available": self.memory_hub is not None,
            "learning_hub_available": self.learning_hub is not None,
            "learning_feedback_enabled": self.learning_feedback_enabled,
            "event_mappings": len(self.event_mappings),
            "timestamp": self._get_timestamp(),
        }

        return health


# Singleton instance
_memory_learning_bridge_instance = None


def get_memory_learning_bridge() -> MemoryLearningBridge:
    """Get or create the Memory-Learning bridge instance"""
    global _memory_learning_bridge_instance
    if _memory_learning_bridge_instance is None:
        _memory_learning_bridge_instance = MemoryLearningBridge()
    return _memory_learning_bridge_instance
