"""Memory event structures and factory utilities."""

from __future__ import annotations

import copy
import logging
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict

from memory.metrics import compute_affect_delta, compute_drift

logger = logging.getLogger(__name__)


# ΛTAG: memory_event
@dataclass
class MemoryEvent:
    """Simple container for memory event data."""

    data: dict[str, Any]
    metadata: dict[str, Any]


class MemoryEventFactory:
    """Factory for creating :class:`MemoryEvent` objects."""

    def __init__(self) -> None:
        self._last_affect_delta: float | None = None
        self._drift_history: deque[float] = deque(maxlen=100)

    def create(self, data: dict[str, Any], metadata: dict[str, Any]) -> MemoryEvent:
        """Create a new :class:`MemoryEvent` instance.

        Args:
            data: Core event payload.
            metadata: Additional contextual information.

        Returns:
            A populated :class:`MemoryEvent` enriched with drift telemetry.
        """

        payload_data = self._validate_payload(data, "data")
        payload_metadata = self._validate_payload(metadata, "metadata")

        combined_payload = {**payload_data, **payload_metadata}
        affect_delta = compute_affect_delta(combined_payload)
        drift_score = self._calculate_drift(payload_metadata, affect_delta)

        enriched_metadata = self._enrich_metadata(payload_metadata, affect_delta, drift_score)

        logger.info(
            "MemoryEvent_created",
            extra={
                "affect_delta": affect_delta,
                "driftScore": drift_score,
                "events_tracked": len(self._drift_history),
                "ΛTAG": "memory_event",
            },
        )
        return MemoryEvent(data=payload_data, metadata=enriched_metadata)

    # ΛTAG: memory_event_validation
    def _validate_payload(self, payload: dict[str, Any], label: str) -> dict[str, Any]:
        """Validate payload structure and create a safe copy."""

        if not isinstance(payload, dict):
            raise TypeError(f"{label} must be a dictionary")
        return copy.deepcopy(payload)

    # ΛTAG: memory_event_metrics
    def _calculate_drift(self, metadata: dict[str, Any], affect_delta: float) -> float:
        """Determine driftScore using provided metadata and affect_delta."""

        provided = metadata.get("driftScore")
        if provided is None:
            provided = metadata.get("drift_score")

        if isinstance(provided, (int, float)):
            drift_score = compute_drift(None, float(provided))
        else:
            reference = metadata.get("previous_affect_delta")
            if not isinstance(reference, (int, float)):
                reference = self._last_affect_delta
            drift_score = compute_drift(float(reference) if isinstance(reference, (int, float)) else None, affect_delta)

        self._last_affect_delta = affect_delta
        self._drift_history.append(drift_score)
        return drift_score

    def _enrich_metadata(
        self,
        metadata: dict[str, Any],
        affect_delta: float,
        drift_score: float,
    ) -> dict[str, Any]:
        """Attach telemetry metadata including drift trends."""

        enriched = copy.deepcopy(metadata)
        metrics = copy.deepcopy(enriched.get("metrics", {}))
        metrics.update(
            {
                "affect_delta": affect_delta,
                "driftScore": drift_score,
                "driftTrend": sum(list(self._drift_history)[-3:]) / min(len(self._drift_history), 3) if self._drift_history else 0.0,
            }
        )

        enriched["metrics"] = metrics
        enriched.setdefault("timestamp_utc", datetime.now(timezone.utc).isoformat())
        return enriched


__all__ = ["MemoryEvent", "MemoryEventFactory", "logger"]
