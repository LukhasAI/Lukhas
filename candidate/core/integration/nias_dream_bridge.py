"""

#TAG:core
#TAG:integration
#TAG:neuroplastic
#TAG:colony

NIAS-Dream Bridge
Bidirectional communication bridge between NIAS and Dream systems
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class NIASDreamBridge:
    """
    Bridge for communication between NIAS and Dream systems.

    Provides:
    - Bidirectional data flow
    - Event synchronization
    - Dream message integration
    - NIAS-Dream feedback loops
    """

    def __init__(self):
        self.nias_hub = None  # Will be initialized later
        self.dream_hub = None
        self.event_mappings = {}
        self.is_connected = False

        logger.info("NIAS-Dream Bridge initialized")

    async def connect(self) -> bool:
        """Establish connection between NIAS and Dream systems"""
        try:
            # Get system hubs
            from core.modules.nias.nias_hub import get_nias_hub
            from orchestration.dream.dream_hub import get_dream_hub

            self.nias_hub = get_nias_hub()
            self.dream_hub = get_dream_hub()

            # Set up event mappings
            self.setup_event_mappings()

            self.is_connected = True
            logger.info("Bridge connected between NIAS and Dream systems")
            return True

        except Exception as e:
            logger.error(f"Failed to connect NIAS-Dream bridge: {e}")
            return False

    def setup_event_mappings(self):
        """Set up event type mappings between systems"""
        self.event_mappings = {
            # NIAS -> Dream events
            "message_deferred": "dream_message_processing",
            "symbolic_match": "dream_symbol_integration",
            "user_context_update": "dream_personalization_update",
            "nias_feedback": "dream_learning_feedback",
            # Dream -> NIAS events
            "dream_completion": "nias_message_delivery",
            "dream_symbols_extracted": "nias_symbolic_update",
            "dream_insights": "nias_user_insights",
            "dream_narrative": "nias_voice_integration",
        }

    async def nias_to_dream(
        self, event_type: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Forward event from NIAS to Dream system"""
        if not self.is_connected:
            await self.connect()

        try:
            # Map event type
            mapped_event = self.event_mappings.get(event_type, event_type)

            # Transform data for dream processing
            transformed_data = self.transform_data_nias_to_dream(data)

            # Send to dream system
            if self.dream_hub:
                result = await self.dream_hub.process_event(
                    mapped_event, transformed_data
                )
                logger.debug(f"Forwarded {event_type} from NIAS to Dream")
                return result

            return {"error": "dream hub not available"}

        except Exception as e:
            logger.error(f"Error forwarding from NIAS to Dream: {e}")
            return {"error": str(e)}

    async def dream_to_nias(
        self, event_type: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Forward event from Dream to NIAS system"""
        if not self.is_connected:
            await self.connect()

        try:
            # Map event type
            mapped_event = self.event_mappings.get(event_type, event_type)

            # Transform data for NIAS processing
            transformed_data = self.transform_data_dream_to_nias(data)

            # Send to NIAS system
            if self.nias_hub:
                result = await self.nias_hub.process_event(
                    mapped_event, transformed_data
                )
                logger.debug(f"Forwarded {event_type} from Dream to NIAS")
                return result

            return {"error": "NIAS hub not available"}

        except Exception as e:
            logger.error(f"Error forwarding from Dream to NIAS: {e}")
            return {"error": str(e)}

    def transform_data_nias_to_dream(self, data: dict[str, Any]) -> dict[str, Any]:
        """Transform data format from NIAS to Dream"""
        return {
            "source_system": "nias",
            "target_system": "dream",
            "data": data,
            "timestamp": self._get_timestamp(),
            "bridge_version": "1.0",
        }

    def transform_data_dream_to_nias(self, data: dict[str, Any]) -> dict[str, Any]:
        """Transform data format from Dream to NIAS"""
        return {
            "source_system": "dream",
            "target_system": "nias",
            "data": data,
            "timestamp": self._get_timestamp(),
            "bridge_version": "1.0",
        }

    async def handle_message_deferral(
        self, message_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Handle NIAS message deferral to Dream system"""
        dream_data = {
            "message_content": message_data.get("content"),
            "user_context": message_data.get("user_context", {}),
            "defer_reason": message_data.get("reason"),
            "priority": message_data.get("priority", "normal"),
            "processing_type": "deferred_message",
        }

        return await self.nias_to_dream("message_deferred", dream_data)

    async def handle_dream_completion(
        self, dream_result: dict[str, Any]
    ) -> dict[str, Any]:
        """Handle Dream processing completion back to NIAS"""
        nias_data = {
            "dream_id": dream_result.get("dream_id"),
            "processed_content": dream_result.get("result"),
            "insights": dream_result.get("insights", []),
            "delivery_ready": True,
            "processing_complete": True,
        }

        return await self.dream_to_nias("dream_completion", nias_data)

    async def sync_symbolic_data(self) -> bool:
        """Synchronize symbolic data between NIAS and Dream systems"""
        try:
            # Get symbolic data from NIAS
            if self.nias_hub:
                symbolic_matcher = self.nias_hub.get_service("symbolic_matcher")
                if symbolic_matcher and hasattr(
                    symbolic_matcher, "get_current_symbols"
                ):
                    symbols = symbolic_matcher.get_current_symbols()

                    # Send to Dream for processing
                    await self.nias_to_dream("symbolic_match", {"symbols": symbols})

            return True
        except Exception as e:
            logger.error(f"Symbolic data sync failed: {e}")
            return False

    async def register_nias_events(self, event_handlers: dict[str, callable]):
        """Register NIAS event handlers with the bridge"""
        for event_type, handler in event_handlers.items():
            # Register handler for mapped dream events
            mapped_event = self.event_mappings.get(event_type)
            if mapped_event and self.dream_hub:
                self.dream_hub.register_event_handler(mapped_event, handler)
                logger.debug(f"Registered NIAS handler for {mapped_event}")

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime

        return datetime.now().isoformat()

    async def health_check(self) -> dict[str, Any]:
        """Health check for the bridge"""
        health = {
            "bridge_status": ("healthy" if self.is_connected else "disconnected"),
            "nias_hub_available": self.nias_hub is not None,
            "dream_hub_available": self.dream_hub is not None,
            "event_mappings": len(self.event_mappings),
            "timestamp": self._get_timestamp(),
        }

        return health


# Singleton instance
_nias_dream_bridge_instance = None


def get_nias_dream_bridge() -> NIASDreamBridge:
    """Get or create the NIAS-Dream bridge instance"""
    global _nias_dream_bridge_instance
    if _nias_dream_bridge_instance is None:
        _nias_dream_bridge_instance = NIASDreamBridge()
    return _nias_dream_bridge_instance
