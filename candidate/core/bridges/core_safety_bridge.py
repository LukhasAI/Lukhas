"""
Core-Safety Bridge
Bidirectional communication bridge between core and safety systems
"""
from __future__ import annotations

import logging
from collections.abc import Mapping, Sequence
from typing import Any

# Import system hubs (will be available after hub creation)
# from candidate.core.core_hub import get_core_hub
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

    async def core_to_safety(self, event_type: str, data: dict[str, Any]) -> dict[str, Any]:
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
                result = await self.safety_hub.process_event(mapped_event, transformed_data)
                logger.debug(f"Forwarded {event_type} from core to safety")
                return result

            return {"error": "safety hub not available"}

        except Exception as e:
            logger.error(f"Error forwarding from core to safety: {e}")
            return {"error": str(e)}

    async def safety_to_core(self, event_type: str, data: dict[str, Any]) -> dict[str, Any]:
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
                result = await self.core_hub.process_event(mapped_event, transformed_data)
                logger.debug(f"Forwarded {event_type} from safety to core")
                return result

            return {"error": "core hub not available"}

        except Exception as e:
            logger.error(f"Error forwarding from safety to core: {e}")
            return {"error": str(e)}

    def transform_data_core_to_safety(self, data: dict[str, Any]) -> dict[str, Any]:
        """Transform data format from core to safety"""
        # Add system-specific transformations here
        return {
            "source_system": "core",
            "target_system": "safety",
            "data": data,
            "timestamp": "{}".format(__import__("datetime").datetime.now().isoformat()),
        }

    def transform_data_safety_to_core(self, data: dict[str, Any]) -> dict[str, Any]:
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

    async def get_core_state(self) -> dict[str, Any]:
        """Get current state from core system"""
        if self.core_hub:
            # Implement core-specific state retrieval
            return {"system": "core", "state": "active"}
        return {}

    async def get_safety_state(self) -> dict[str, Any]:
        """Get current state from safety system"""
        if self.safety_hub:
            # Implement safety-specific state retrieval
            return {"system": "safety", "state": "active"}
        return {}

    def compare_states(
        self,
        state1: dict[str, Any],
        state2: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Compare states and return differences"""
        differences: list[dict[str, Any]] = []

        # ΛTAG: trinity_state_comparison
        for path, value_core, value_safety in self._iter_state_pairs(state1, state2):
            if self._values_equal(value_core, value_safety):
                continue

            drift_score = self._calculate_drift(value_core, value_safety)
            delta = None
            if isinstance(value_core, (int, float)) and isinstance(value_safety, (int, float)):
                delta = round(float(value_safety) - float(value_core), 6)

            differences.append(
                {
                    "path": path,
                    "core_value": value_core,
                    "safety_value": value_safety,
                    "delta": delta,
                    "driftScore": drift_score,
                    "trinity_axis": self._infer_trinity_axis(path),
                }
            )

        logger.debug(
            "core_safety_bridge.state_diff",
            extra={"diff_count": len(differences), "paths": [d["path"] for d in differences[:5]]},
        )
        return differences

    def _iter_state_pairs(self, left: Any, right: Any, path: str = ""):
        if isinstance(left, Mapping) or isinstance(right, Mapping):
            left_map = left if isinstance(left, Mapping) else {}
            right_map = right if isinstance(right, Mapping) else {}
            for key in sorted(set(left_map) | set(right_map)):
                next_path = f"{path}.{key}" if path else str(key)
                yield from self._iter_state_pairs(left_map.get(key), right_map.get(key), next_path)
            return

        is_seq_left = isinstance(left, Sequence) and not isinstance(left, (str, bytes))
        is_seq_right = isinstance(right, Sequence) and not isinstance(right, (str, bytes))
        if is_seq_left or is_seq_right:
            left_seq = list(left) if is_seq_left else []
            right_seq = list(right) if is_seq_right else []
            max_len = max(len(left_seq), len(right_seq))
            for idx in range(max_len):
                next_path = f"{path}[{idx}]" if path else f"[{idx}]"
                yield from self._iter_state_pairs(
                    left_seq[idx] if idx < len(left_seq) else None,
                    right_seq[idx] if idx < len(right_seq) else None,
                    next_path,
                )
            return

        yield path or "root", left, right

    @staticmethod
    def _values_equal(left: Any, right: Any) -> bool:
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return abs(float(left) - float(right)) <= 1e-6
        return left == right

    @staticmethod
    def _calculate_drift(left: Any, right: Any) -> float:
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return round(abs(float(left) - float(right)), 6)
        if left is None or right is None:
            return 1.0
        return 0.75 if left != right else 0.0

    @staticmethod
    def _infer_trinity_axis(path: str) -> str:
        path_lower = path.lower()
        if "identity" in path_lower:
            return "⚛️"
        if "consciousness" in path_lower:
            return "🧠"
        if "guardian" in path_lower or "safety" in path_lower:
            return "🛡️"
        return "neutral"

    async def resolve_differences(self, differences: list[dict[str, Any]]) -> None:
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
