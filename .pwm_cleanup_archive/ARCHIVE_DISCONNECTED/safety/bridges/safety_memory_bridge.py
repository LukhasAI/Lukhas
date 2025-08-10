"""
Safety-Memory Bridge
Bidirectional communication bridge between Safety and Memory systems
"""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class SafetyMemoryBridge:
    """
    Bridge for communication between Safety and Memory systems.

    Provides:
    - Safety Rules ↔ Memory Storage
    - Safety History ↔ Memory Recall
    - Safety Patterns ↔ Memory Patterns
    - Safety Incidents ↔ Memory Tracking
    - Safety Learning ↔ Memory Consolidation
    """

    def __init__(self):
        self.safety_hub = None
        self.memory_hub = None
        self.event_mappings = {}
        self.is_connected = False

        logger.info("Safety-Memory Bridge initialized")

    async def connect(self) -> bool:
        """Establish connection between Safety and Memory systems"""
        try:
            from safety.safety_hub import get_safety_hub

            from memory.memory_hub import get_memory_hub

            self.safety_hub = get_safety_hub()
            self.memory_hub = get_memory_hub()

            self.setup_event_mappings()

            self.is_connected = True
            logger.info("Bridge connected between Safety and Memory systems")
            return True

        except Exception as e:
            logger.error(f"Failed to connect Safety-Memory bridge: {e}")
            return False

    def setup_event_mappings(self):
        """Set up event type mappings between systems"""
        self.event_mappings = {
            # Safety -> Memory events
            "safety_rule_created": "memory_store_rule",
            "safety_incident_logged": "memory_store_incident",
            "safety_pattern_detected": "memory_store_pattern",
            "safety_history_request": "memory_recall_safety_data",
            "safety_learning_update": "memory_consolidate_learning",
            # Memory -> Safety events
            "memory_safety_recall": "safety_history_retrieved",
            "memory_pattern_matched": "safety_pattern_alert",
            "memory_incident_found": "safety_incident_review",
            "memory_rule_retrieved": "safety_rule_validation",
            "memory_learning_complete": "safety_knowledge_update",
        }

    async def safety_to_memory(
        self, event_type: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Forward event from Safety to Memory system"""
        if not self.is_connected:
            await self.connect()

        try:
            mapped_event = self.event_mappings.get(event_type, event_type)
            transformed_data = self.transform_data_safety_to_memory(data)

            if self.memory_hub:
                result = await self.memory_hub.process_event(
                    mapped_event, transformed_data
                )
                logger.debug(f"Forwarded {event_type} from Safety to Memory")
                return result

            return {"error": "memory hub not available"}

        except Exception as e:
            logger.error(f"Error forwarding from Safety to Memory: {e}")
            return {"error": str(e)}

    async def memory_to_safety(
        self, event_type: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Forward event from Memory to Safety system"""
        if not self.is_connected:
            await self.connect()

        try:
            mapped_event = self.event_mappings.get(event_type, event_type)
            transformed_data = self.transform_data_memory_to_safety(data)

            if self.safety_hub:
                result = await self.safety_hub.process_event(
                    mapped_event, transformed_data
                )
                logger.debug(f"Forwarded {event_type} from Memory to Safety")
                return result

            return {"error": "safety hub not available"}

        except Exception as e:
            logger.error(f"Error forwarding from Memory to Safety: {e}")
            return {"error": str(e)}

    def transform_data_safety_to_memory(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform data format from Safety to Memory"""
        return {
            "source_system": "safety",
            "target_system": "memory",
            "data": data,
            "memory_context": {
                "storage_type": data.get("storage_type", "safety_data"),
                "retention_policy": data.get("retention", "permanent"),
                "priority": data.get("priority", "high"),
            },
            "timestamp": self._get_timestamp(),
        }

    def transform_data_memory_to_safety(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform data format from Memory to Safety"""
        return {
            "source_system": "memory",
            "target_system": "safety",
            "data": data,
            "safety_context": {
                "memory_type": data.get("memory_type", "episodic"),
                "confidence": data.get("confidence", 0.9),
                "relevance": data.get("relevance", "high"),
            },
            "timestamp": self._get_timestamp(),
        }

    async def store_safety_rule(self, rule_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store safety rule in memory system"""
        memory_data = {
            "storage_request": "safety_rule",
            "rule_content": rule_data,
            "storage_type": "semantic",
            "retention": "permanent",
            "indexing": ["safety", "rules", rule_data.get("category", "general")],
        }

        return await self.safety_to_memory("safety_rule_created", memory_data)

    async def recall_safety_history(self, query_data: Dict[str, Any]) -> Dict[str, Any]:
        """Recall safety history from memory"""
        memory_query = {
            "recall_type": "safety_history",
            "query": query_data,
            "time_range": query_data.get("time_range"),
            "incident_types": query_data.get("incident_types", []),
        }

        result = await self.safety_to_memory("safety_history_request", memory_query)

        if result.get("results"):
            return await self.memory_to_safety("memory_safety_recall", result)

        return result

    async def log_safety_incident(
        self, incident_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Log safety incident to memory"""
        memory_data = {
            "incident_type": "safety_violation",
            "incident_data": incident_data,
            "severity": incident_data.get("severity", "medium"),
            "storage_type": "episodic",
            "tags": ["safety", "incident", incident_data.get("category", "general")],
        }

        return await self.safety_to_memory("safety_incident_logged", memory_data)

    async def detect_safety_patterns(
        self, pattern_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Detect and store safety patterns"""
        memory_data = {
            "pattern_type": "safety_pattern",
            "pattern_data": pattern_data,
            "pattern_confidence": pattern_data.get("confidence", 0.8),
            "storage_type": "semantic",
            "learning_enabled": True,
        }

        return await self.safety_to_memory("safety_pattern_detected", memory_data)

    async def sync_safety_memory_knowledge(self) -> bool:
        """Synchronize safety knowledge with memory system"""
        try:
            # Get current safety rules
            safety_rules = await self.get_safety_rules()

            # Get memory safety data
            memory_safety = await self.get_memory_safety_data()

            # Cross-synchronize
            await self.safety_to_memory(
                "safety_knowledge_sync",
                {"rules": safety_rules, "sync_type": "bidirectional"},
            )

            await self.memory_to_safety(
                "memory_knowledge_sync",
                {"safety_memories": memory_safety, "sync_type": "knowledge_update"},
            )

            logger.debug("Safety-Memory knowledge synchronization completed")
            return True

        except Exception as e:
            logger.error(f"Knowledge synchronization failed: {e}")
            return False

    async def get_safety_rules(self) -> Dict[str, Any]:
        """Get current safety rules"""
        if self.safety_hub:
            rule_manager = self.safety_hub.get_service("rule_manager")
            if rule_manager and hasattr(rule_manager, "get_all_rules"):
                return rule_manager.get_all_rules()

        return {"rules": [], "count": 0}

    async def get_memory_safety_data(self) -> Dict[str, Any]:
        """Get safety-related data from memory"""
        if self.memory_hub:
            memory_manager = self.memory_hub.get_service("memory_manager")
            if memory_manager and hasattr(memory_manager, "query_by_tags"):
                return memory_manager.query_by_tags(["safety"])

        return {"memories": [], "count": 0}

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime

        return datetime.now().isoformat()

    async def health_check(self) -> Dict[str, Any]:
        """Health check for the bridge"""
        return {
            "bridge_status": "healthy" if self.is_connected else "disconnected",
            "safety_hub_available": self.safety_hub is not None,
            "memory_hub_available": self.memory_hub is not None,
            "event_mappings": len(self.event_mappings),
            "timestamp": self._get_timestamp(),
        }


# Singleton instance
_safety_memory_bridge_instance = None


def get_safety_memory_bridge() -> SafetyMemoryBridge:
    """Get or create the Safety-Memory bridge instance"""
    global _safety_memory_bridge_instance
    if _safety_memory_bridge_instance is None:
        _safety_memory_bridge_instance = SafetyMemoryBridge()
    return _safety_memory_bridge_instance
