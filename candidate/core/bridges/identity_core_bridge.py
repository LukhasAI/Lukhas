"""
Identity-Core Bridge
Bidirectional communication bridge between identity and core systems
"""
from __future__ import annotations

import logging
from collections.abc import Mapping, Sequence
from typing import Any

# Import system hubs (will be available after hub creation)
# from identity.identity_hub import get_identity_hub
# from candidate.core.core_hub import get_core_hub

logger = logging.getLogger(__name__)


class IdentityCoreBridge:
    """
    Bridge for communication between identity and core systems.

    Provides:
    - Bidirectional data flow
    - Event synchronization
    - State consistency
    - Error handling and recovery
    """

    def __init__(self):
        self.identity_hub = None  # Will be initialized later
        self.core_hub = None
        self.event_mappings = {}
        self.is_connected = False

        logger.info("IdentityCoreBridge initialized")

    async def connect(self) -> bool:
        """Establish connection between systems"""
        try:
            # Get system hubs
            # self.identity_hub = get_identity_hub()
            # self.core_hub = get_core_hub()

            # Set up event mappings
            self.setup_event_mappings()

            self.is_connected = True
            logger.info("Bridge connected between identity and core")
            return True

        except Exception as e:
            logger.error(f"Failed to connect bridge: {e}")
            return False

    def setup_event_mappings(self):
        """Set up event type mappings between systems"""
        self.event_mappings = {
            # identity -> core events
            "identity_state_change": "core_sync_request",
            "identity_data_update": "core_data_sync",
            # core -> identity events
            "core_state_change": "identity_sync_request",
            "core_data_update": "identity_data_sync",
        }

    async def identity_to_core(self, event_type: str, data: dict[str, Any]) -> dict[str, Any]:
        """Forward event from identity to core"""
        if not self.is_connected:
            await self.connect()

        try:
            # Map event type
            mapped_event = self.event_mappings.get(event_type, event_type)

            # Transform data if needed
            transformed_data = self.transform_data_identity_to_core(data)

            # Send to core
            if self.core_hub:
                result = await self.core_hub.process_event(mapped_event, transformed_data)
                logger.debug(f"Forwarded {event_type} from identity to core")
                return result

            return {"error": "core hub not available"}

        except Exception as e:
            logger.error(f"Error forwarding from identity to core: {e}")
            return {"error": str(e)}

    async def core_to_identity(self, event_type: str, data: dict[str, Any]) -> dict[str, Any]:
        """Forward event from core to identity"""
        if not self.is_connected:
            await self.connect()

        try:
            # Map event type
            mapped_event = self.event_mappings.get(event_type, event_type)

            # Transform data if needed
            transformed_data = self.transform_data_core_to_identity(data)

            # Send to identity
            if self.identity_hub:
                result = await self.identity_hub.process_event(mapped_event, transformed_data)
                logger.debug(f"Forwarded {event_type} from core to identity")
                return result

            return {"error": "identity hub not available"}

        except Exception as e:
            logger.error(f"Error forwarding from core to identity: {e}")
            return {"error": str(e)}

    def transform_data_identity_to_core(self, data: dict[str, Any]) -> dict[str, Any]:
        """Transform data format from identity to core"""
        # Add system-specific transformations here
        return {
            "source_system": "identity",
            "target_system": "core",
            "data": data,
            "timestamp": "{}".format(__import__("datetime").datetime.now().isoformat()),
        }

    def transform_data_core_to_identity(self, data: dict[str, Any]) -> dict[str, Any]:
        """Transform data format from core to identity"""
        # Add system-specific transformations here
        return {
            "source_system": "core",
            "target_system": "identity",
            "data": data,
            "timestamp": "{}".format(__import__("datetime").datetime.now().isoformat()),
        }

    async def sync_state(self) -> bool:
        """Synchronize state between systems"""
        if not self.is_connected:
            return False

        try:
            # Get state from both systems
            identity_state = await self.get_identity_state()
            core_state = await self.get_core_state()

            # Detect differences and sync
            differences = self.compare_states(identity_state, core_state)

            if differences:
                await self.resolve_differences(differences)
                logger.info(f"Synchronized {len(differences)} state differences")

            return True

        except Exception as e:
            logger.error(f"State sync failed: {e}")
            return False

    async def get_identity_state(self) -> dict[str, Any]:
        """Get current state from identity system"""
        if self.identity_hub:
            # Implement identity-specific state retrieval
            return {"system": "identity", "state": "active"}
        return {}

    async def get_core_state(self) -> dict[str, Any]:
        """Get current state from core system"""
        if self.core_hub:
            # Implement core-specific state retrieval
            return {"system": "core", "state": "active"}
        return {}

    def compare_states(
        self,
        state1: dict[str, Any],
        state2: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Compare states and return differences"""
        differences: list[dict[str, Any]] = []

        # ΛTAG: trinity_identity_state
        for path, identity_value, core_value in self._iter_state_pairs(state1, state2):
            if self._values_equal(identity_value, core_value):
                continue

            drift_score = self._calculate_drift(identity_value, core_value)
            delta = None
            if isinstance(identity_value, (int, float)) and isinstance(core_value, (int, float)):
                delta = round(float(core_value) - float(identity_value), 6)

            differences.append(
                {
                    "path": path,
                    "identity_value": identity_value,
                    "core_value": core_value,
                    "delta": delta,
                    "driftScore": drift_score,
                    "trinity_axis": self._infer_trinity_axis(path),
                }
            )

        logger.debug(
            "identity_core_bridge.state_diff",
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
        logger.info("Bridge disconnected between identity and core")


# Singleton instance
_identity_core_bridge_instance = None


def get_identity_core_bridge() -> IdentityCoreBridge:
    """Get or create bridge instance"""
    global _identity_core_bridge_instance
    if _identity_core_bridge_instance is None:
        _identity_core_bridge_instance = IdentityCoreBridge()
    return _identity_core_bridge_instance
