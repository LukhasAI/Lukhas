#!/usr/bin/env python3
"""Symbolic emotion example with drift and affect metrics."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Sequence

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class EmotionSnapshot:
    """Immutable record of the current symbolic emotion metrics."""

    affect_delta: float
    drift_score: float
    intensity_vector: tuple[float, ...]


# ΛTAG: affect_delta
def compute_affect_delta(intensity_vector: Sequence[float]) -> float:
    """Compute the affect_delta as the delta between final and initial intensity."""

    if not intensity_vector:
        return 0.0

    start = intensity_vector[0]
    end = intensity_vector[-1]
    return float(end - start)


# ΛTAG: drift
def compute_drift_score(intensity_vector: Sequence[float]) -> float:
    """Compute a simple driftScore by averaging absolute neighbor changes."""

    if len(intensity_vector) < 2:
        return 0.0

    deltas = [abs(current - previous) for previous, current in zip(intensity_vector, intensity_vector[1:])]
    return float(sum(deltas) / len(deltas))


def build_emotion_snapshot(intensity_vector: Sequence[float]) -> EmotionSnapshot:
    """Create an :class:`EmotionSnapshot` from raw intensity readings."""

    vector_tuple = tuple(float(value) for value in intensity_vector)
    affect_delta = compute_affect_delta(vector_tuple)
    drift_score = compute_drift_score(vector_tuple)
    snapshot = EmotionSnapshot(affect_delta=affect_delta, drift_score=drift_score, intensity_vector=vector_tuple)

    logger.info(
        "Emotion snapshot prepared",
        extra={"affect_delta": affect_delta, "driftScore": drift_score, "Λvector": vector_tuple},
    )
    return snapshot


def render_symbolic_trace(snapshot: EmotionSnapshot) -> str:
    """Render a human-readable symbolic trace for the provided snapshot."""

    trace = (
        "Emotion Trace\n"
        f"  • affect_delta: {snapshot.affect_delta:.3f}\n"
        f"  • driftScore: {snapshot.drift_score:.3f}\n"
        f"  • intensity_vector: {', '.join(f'{value:.3f}' for value in snapshot.intensity_vector)}"
    )

    logger.debug("Symbolic trace generated", extra={"trace": trace})
    return trace


def main() -> None:
    """Execute the basic emotion example."""

    baseline_vector = (0.12, 0.25, 0.40, 0.36)
    snapshot = build_emotion_snapshot(baseline_vector)
    print(render_symbolic_trace(snapshot))


if __name__ == "__main__":
    main()
