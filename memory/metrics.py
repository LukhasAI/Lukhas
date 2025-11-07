"""Utility functions for memory metrics and affect tracking."""

from __future__ import annotations

import logging
from collections.abc import Mapping, Sequence
from numbers import Real
from typing import Any

logger = logging.getLogger(__name__)

# ΛTAG: affect_delta_metrics

def _clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    """Clamp a floating point value to the provided bounds."""
    return max(minimum, min(maximum, value))


def _collect_numeric_values(sequence: Sequence[Any]) -> list[float]:
    """Collect numeric values from a sequence while ignoring non-numeric entries."""
    values: list[float] = []
    for item in sequence:
        if isinstance(item, Real):
            values.append(float(item))
    return values


def _maybe_float(value: Any) -> float | None:
    """Convert a value to float when possible."""
    if isinstance(value, Real):
        return float(value)
    return None


def compute_affect_delta(payload: Mapping[str, Any]) -> float:
    """Compute an affect_delta metric from a heterogeneous payload."""
    affect_candidates: list[float] = []

    # Direct affect delta fields
    for key in ("affect_delta", "affectDelta"):
        candidate = _maybe_float(payload.get(key))
        if candidate is not None:
            affect_candidates.append(candidate)

    # Affect vector based estimation
    for key in ("affect_vector", "affectVector", "affect_signature"):
        vector = payload.get(key)
        if isinstance(vector, Sequence) and not isinstance(vector, (str, bytes)):
            numeric_values = _collect_numeric_values(vector)
            if numeric_values:
                affect_candidates.append(sum(abs(v) for v in numeric_values) / len(numeric_values))

    # Emotional signature dictionary
    signature = payload.get("emotional_signature") or payload.get("emotion_signature")
    if isinstance(signature, Mapping):
        valence = _maybe_float(signature.get("valence"))
        arousal = _maybe_float(signature.get("arousal"))
        if valence is not None and arousal is not None:
            affect_candidates.append(abs(valence - 0.5) + abs(arousal - 0.5))

    # Individual valence/arousal hints
    valence = _maybe_float(payload.get("valence"))
    arousal = _maybe_float(payload.get("arousal"))
    if valence is not None and arousal is not None:
        affect_candidates.append(abs(valence - 0.5) + abs(arousal - 0.5))

    if not affect_candidates:
        logger.debug("No affect_delta signals found; defaulting to neutral state")
        return 0.0

    affect_delta = sum(affect_candidates) / len(affect_candidates)
    affect_delta = _clamp(affect_delta)
    logger.debug("Computed affect_delta", extra={"affect_delta": affect_delta, "ΛTAG": "affect_delta"})
    return affect_delta


# ΛTAG: drift_metric

def compute_drift(previous: float | None, current: float) -> float:
    """Compute driftScore from a previous affect delta reading and the current value."""
    drift = _clamp(abs(current)) if previous is None else _clamp(abs(current - previous))
    logger.debug(
        "Computed driftScore",
        extra={"driftScore": drift, "previous_affect_delta": previous, "current_affect_delta": current},
    )
    return drift


__all__ = ["compute_affect_delta", "compute_drift"]
