"""
Core-Safety Bridge
Bidirectional communication bridge between core and safety systems
"""

import logging
from typing import Any, Dict, List

# Import system hubs (will be available after hub creation)
# from core.core_hub import get_core_hub
# from safety.safety_hub import get_safety_hub

logger = logging.getLogger(__name__)


class CoreSafetyBridge:
    """
    Bridge for communication between core and safety systems.

    Provides:
    - Bidirectional data flow
    - Event synchronization
    - State consistency
    - Error handling and recovery
    """

    def __init__(self):
        self.core_hub = None  # Will be initialized later
        self.safety_hub = None
        self.event_mappings = {}
        self.is_connected = False

        logger.info("CoreSafetyBridge initialized")

    async def connect(self) -> bool:
        """Establish connection between systems"""
        try:
            # Get system hubs
            # self.core_hub = get_core_hub()
            # self.safety_hub = get_safety_hub()

            # Set up event mappings
            self.setup_event_mappings()

            self.is_connected = True
            logger.info("Bridge connected between core and safety")
            return True

        except Exception as e:
            logger.error(f"Failed to connect bridge: {e}")
            return False

    def setup_event_mappings(self):
        """Set up event type mappings between systems"""
        self.event_mappings = {
            # core -> safety events
            "core_state_change": "safety_sync_request",
            "core_data_update": "safety_data_sync",
            # safety -> core events
            "safety_state_change": "core_sync_request",
            "safety_data_update": "core_data_sync",
        }

    async def core_to_safety(
        self, event_type: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Forward event from core to safety"""
        if not self.is_connected:
            await self.connect()

        try:
            # Map event type
            mapped_event = self.event_mappings.get(event_type, event_type)

            # Transform data if needed
            transformed_data = self.transform_data_core_to_safety(data)

            # Send to safety
            if self.safety_hub:
                result = await self.safety_hub.process_event(
                    mapped_event, transformed_data
                )
                logger.debug(f"Forwarded {event_type} from core to safety")
                return result

            return {"error": "safety hub not available"}

        except Exception as e:
            logger.error(f"Error forwarding from core to safety: {e}")
            return {"error": str(e)}

    async def safety_to_core(
        self, event_type: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Forward event from safety to core"""
        if not self.is_connected:
            await self.connect()

        try:
            # Map event type
            mapped_event = self.event_mappings.get(event_type, event_type)

            # Transform data if needed
            transformed_data = self.transform_data_safety_to_core(data)

            # Send to core
            if self.core_hub:
                result = await self.core_hub.process_event(
                    mapped_event, transformed_data
                )
                logger.debug(f"Forwarded {event_type} from safety to core")
                return result

            return {"error": "core hub not available"}

        except Exception as e:
            logger.error(f"Error forwarding from safety to core: {e}")
            return {"error": str(e)}

    def transform_data_core_to_safety(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform data format from core to safety"""
        # Add system-specific transformations here
        return {
            "source_system": "core",
            "target_system": "safety",
            "data": data,
            "timestamp": "{}".format(__import__("datetime").datetime.now().isoformat()),
        }

    def transform_data_safety_to_core(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform data format from safety to core"""
        # Add system-specific transformations here
        return {
            "source_system": "safety",
            "target_system": "core",
            "data": data,
            "timestamp": "{}".format(__import__("datetime").datetime.now().isoformat()),
        }

    async def sync_state(self) -> bool:
        """Synchronize state between systems"""
        if not self.is_connected:
            return False

        try:
            # Get state from both systems
            core_state = await self.get_core_state()
            safety_state = await self.get_safety_state()

            # Detect differences and sync
            differences = self.compare_states(core_state, safety_state)

            if differences:
                await self.resolve_differences(differences)
                logger.info(f"Synchronized {len(differences)} state differences")

            return True

        except Exception as e:
            logger.error(f"State sync failed: {e}")
            return False

    async def get_core_state(self) -> Dict[str, Any]:
        """Get current state from core system"""
        if self.core_hub:
            # Implement core-specific state retrieval
            return {"system": "core", "state": "active"}
        return {}

    async def get_safety_state(self) -> Dict[str, Any]:
        """Get current state from safety system"""
        if self.safety_hub:
            # Implement safety-specific state retrieval
            return {"system": "safety", "state": "active"}
        return {}

    def compare_states(
        self, state1: Dict[str, Any], state2: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Compare states and return differences"""
        differences = []

        # Implement state comparison logic
        # This is a placeholder - add specific comparison logic

        return differences

    async def resolve_differences(self, differences: List[Dict[str, Any]]) -> None:
        """Resolve state differences between systems"""
        for diff in differences:
            # Implement difference resolution logic
            logger.debug(f"Resolving difference: {diff}")

    async def disconnect(self) -> None:
        """Disconnect the bridge"""
        self.is_connected = False
        logger.info("Bridge disconnected between core and safety")


# Singleton instance
_core_safety_bridge_instance = None


def get_core_safety_bridge() -> CoreSafetyBridge:
    """Get or create bridge instance"""
    global _core_safety_bridge_instance
    if _core_safety_bridge_instance is None:
        _core_safety_bridge_instance = CoreSafetyBridge()
    return _core_safety_bridge_instance
