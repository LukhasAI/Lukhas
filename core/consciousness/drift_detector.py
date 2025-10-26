"""Drift detection utilities for consciousness dashboards."""
from __future__ import annotations

import logging
from math import sqrt
from typing import Iterable, Mapping

logger = logging.getLogger("drift_detector")


def _vector(values: Iterable[float]) -> list[float]:
    return [float(v) for v in values]


class DriftDetector:
    """Basic symbolic drift detector with affect tracing."""

    def __init__(self, *, drift_threshold: float = 0.2) -> None:
        self.drift_threshold = drift_threshold
        # ΛTAG: driftScore - monitor baseline drift metrics
        logger.debug(
            "DriftDetector initialized",
            extra={"drift_threshold": drift_threshold},
        )

    def measure(self, baseline: Mapping[str, Iterable[float]], current: Mapping[str, Iterable[float]]) -> float:
        """Compute drift score using Euclidean distance normalized by vector length."""

        baseline_vector = _vector(baseline.get("emotion_vector", [])) or [0.0]
        current_vector = _vector(current.get("emotion_vector", [])) or [0.0]
        length = min(len(baseline_vector), len(current_vector))
        if length == 0:
            return 0.0
        numerator = sqrt(sum((current_vector[i] - baseline_vector[i]) ** 2 for i in range(length)))
        denominator = sqrt(length)
        drift_score = min(1.0, numerator / denominator)
        logger.debug(
            "Drift measured",
            extra={
                "driftScore": drift_score,
                "baseline_vector": baseline_vector,
                "current_vector": current_vector,
            },
        )
        return drift_score

    def is_drift(self, baseline: Mapping[str, Iterable[float]], current: Mapping[str, Iterable[float]]) -> bool:
        """Return True when measured drift exceeds configured threshold."""

        drift_score = self.measure(baseline, current)
        is_drift = drift_score >= self.drift_threshold
        logger.info(
            "Drift evaluation performed",
            extra={"driftScore": drift_score, "threshold": self.drift_threshold, "is_drift": is_drift},
        )
        return is_drift

    def summarize(self, baseline: Mapping[str, Iterable[float]], current: Mapping[str, Iterable[float]]) -> dict[str, float]:
        """Return a structured summary for dashboards."""

        drift_score = self.measure(baseline, current)
        affect_delta = drift_score
        summary = {"driftScore": drift_score, "affect_delta": affect_delta}
        logger.debug("Drift summary computed", extra=summary)
        return summary

    # ✅ TODO: integrate multi-metric drift fusion once consciousness mesh exposes them
