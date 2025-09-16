"""Core-Consciousness Bridge

Bidirectional communication between the core and consciousness systems.
"""
from __future__ import annotations

import inspect
import logging
from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from typing import Any, Optional

# ΛTAG: logging, trinity_bridge
logger = logging.getLogger(__name__)


class CoreConsciousnessBridge:
    """Bridge connecting core and consciousness modules."""

    def __init__(
        self,
        core_system: Optional[Any] = None,
        consciousness_system: Optional[Any] = None,
    ) -> None:
        self.core_system = core_system
        self.consciousness_system = consciousness_system
        self.event_mappings: dict[str, str] = {}
        self.is_connected = False
        self._setup_event_mappings()

    async def connect(self) -> bool:
        """Attempt to connect to the core and consciousness systems."""

        if self.core_system is not None and self.consciousness_system is not None:
            self.is_connected = True
            return True

        # ΛTAG: bridge_connection
        try:
            if self.consciousness_system is None:
                from lukhas.consciousness.reflection.consciousness_hub import (
                    get_consciousness_hub,
                )

                self.consciousness_system = get_consciousness_hub()
        except Exception as exc:  # pragma: no cover - import best effort
            logger.debug("consciousness hub lookup failed", exc_info=exc)

        try:
            if self.core_system is None:
                from candidate.core.core_hub import get_core_hub

                self.core_system = get_core_hub()
        except Exception as exc:  # pragma: no cover - import best effort
            logger.debug("core hub lookup failed", exc_info=exc)

        self.is_connected = self.core_system is not None and self.consciousness_system is not None
        if self.is_connected:
            logger.info("Core-Consciousness bridge connected")
        else:
            logger.warning("Core-Consciousness bridge operating in degraded mode")

        return self.is_connected

    def _setup_event_mappings(self) -> None:
        """Define default event mappings between core and consciousness systems."""

        # ΛTAG: event_mapping
        self.event_mappings = {
            "core_state_update": "consciousness_state_sync",
            "core_alert": "consciousness_signal",
            "core_metric": "consciousness_metric",
            "consciousness_state_update": "core_state_sync",
            "consciousness_signal": "core_signal",
            "consciousness_metric": "core_metric",
        }

    async def core_to_consciousness(self, data: dict[str, Any]) -> dict[str, Any]:
        """Send data from core to the consciousness system."""

        if not self.is_connected:
            await self.connect()
        if self.consciousness_system is None:
            logger.error("Consciousness system unavailable for bridge dispatch")
            return {"status": "missing_consciousness"}

        envelope = self._prepare_envelope("core", data)
        return await self._dispatch(self.consciousness_system, envelope)

    async def consciousness_to_core(self, data: dict[str, Any]) -> dict[str, Any]:
        """Send data from consciousness to the core system."""

        if not self.is_connected:
            await self.connect()
        if self.core_system is None:
            logger.error("Core system unavailable for bridge dispatch")
            return {"status": "missing_core"}

        envelope = self._prepare_envelope("consciousness", data)
        return await self._dispatch(self.core_system, envelope)

    async def sync_state(self) -> dict[str, Any]:
        """Synchronize state between systems and return drift analysis."""

        await self.connect()
        core_state = await self._extract_state(self.core_system)
        consciousness_state = await self._extract_state(self.consciousness_system)
        differences = self._compare_states(core_state, consciousness_state)

        if differences:
            await self._apply_patch(self.core_system, differences, source="consciousness")
            await self._apply_patch(self.consciousness_system, differences, source="core")

        return {
            "core_state": core_state,
            "consciousness_state": consciousness_state,
            "differences": differences,
        }

    async def handle_event(self, event: dict[str, Any]) -> dict[str, Any]:
        """Handle cross-system events."""

        await self.connect()
        source = event.get("source")
        if source == "consciousness":
            payload = event.get("payload", event)
            payload.setdefault("event_type", event.get("event_type", "consciousness_signal"))
            logger.debug("Routing event from consciousness to core", extra={"event_type": payload["event_type"]})
            return await self.consciousness_to_core(payload)

        payload = event.get("payload", event)
        payload.setdefault("event_type", event.get("event_type", "core_signal"))
        logger.debug("Routing event from core to consciousness", extra={"event_type": payload["event_type"]})
        response = await self.core_to_consciousness(payload)

        if source not in {"core", "consciousness"}:
            # Unknown origin - propagate acknowledgement to both for safety.
            await self.consciousness_to_core({"event_type": "bridge_ack", "payload": response})

        return response

    async def _dispatch(self, target: Any, envelope: dict[str, Any]) -> dict[str, Any]:
        """Dispatch envelope to target, supporting multiple handler signatures."""

        event_type = envelope["event_type"]
        payload = envelope["payload"]

        for method_name in ("process_event", "process"):
            handler = getattr(target, method_name, None)
            if handler is None:
                continue

            try:
                if method_name == "process_event":
                    result = handler(event_type, payload)
                else:
                    result = handler(payload)
                if inspect.isawaitable(result):
                    result = await result
                return result or {"status": "processed"}
            except Exception as exc:
                logger.error("Bridge dispatch failed", exc_info=exc)
                return {"status": "error", "message": str(exc)}

        logger.warning("No handler available on bridge target", extra={"event_type": event_type})
        return {"status": "unhandled", "event_type": event_type}

    async def _extract_state(self, system: Any) -> dict[str, Any]:
        """Safely extract a state mapping from an arbitrary system."""

        if system is None:
            return {}

        for attr in ("get_state", "get_current_state", "state"):
            candidate = getattr(system, attr, None)
            if candidate is None:
                continue
            value = candidate() if callable(candidate) else candidate
            if inspect.isawaitable(value):
                value = await value
            if isinstance(value, Mapping):
                return dict(value)
            if value is not None:
                return {"value": value}

        return {}

    def _compare_states(
        self, core_state: Mapping[str, Any], consciousness_state: Mapping[str, Any]
    ) -> list[dict[str, Any]]:
        """Compare state dictionaries and record Trinity-aware drift."""

        differences: list[dict[str, Any]] = []
        for path, core_value, consciousness_value in self._iter_state_pairs(core_state, consciousness_state):
            if self._values_equal(core_value, consciousness_value):
                continue

            drift_score = self._calculate_drift(core_value, consciousness_value)
            differences.append(
                {
                    "path": path,
                    "core_value": core_value,
                    "consciousness_value": consciousness_value,
                    "driftScore": drift_score,
                    "trinity_axis": self._infer_trinity_axis(path),
                }
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

        if isinstance(left, Sequence) and not isinstance(left, (str, bytes)) or (
            isinstance(right, Sequence) and not isinstance(right, (str, bytes))
        ):
            left_seq = list(left) if isinstance(left, Sequence) and not isinstance(left, (str, bytes)) else []
            right_seq = list(right) if isinstance(right, Sequence) and not isinstance(right, (str, bytes)) else []
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

    async def _apply_patch(self, target: Any, differences: list[dict[str, Any]], *, source: str) -> None:
        if target is None or not differences:
            return

        payload = {"source": source, "differences": differences, "timestamp": self._utc_timestamp()}
        for method_name in ("apply_state_patch", "sync_patch", "update_from_bridge"):
            handler = getattr(target, method_name, None)
            if handler is None:
                continue
            result = handler(payload) if method_name != "sync_patch" else handler(differences)
            if inspect.isawaitable(result):
                await result
            return

    def _prepare_envelope(self, source: str, data: Any) -> dict[str, Any]:
        payload = data.get("payload") if isinstance(data, Mapping) else None
        if not isinstance(payload, Mapping):
            payload = data if isinstance(data, Mapping) else {"value": data}

        event_type = payload.get("event_type") if isinstance(payload, Mapping) else None
        if isinstance(data, Mapping):
            event_type = data.get("event_type", event_type)

        mapped_type = self.event_mappings.get(event_type, event_type or "bridge_event")

        # ΛTAG: temporal_sync
        timestamp = data.get("timestamp") if isinstance(data, Mapping) else None
        if timestamp is None:
            timestamp = self._utc_timestamp()

        envelope = {
            "event_type": mapped_type,
            "payload": dict(payload),
            "timestamp": timestamp,
            "source": source,
        }
        return envelope

    @staticmethod
    def _utc_timestamp() -> str:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
