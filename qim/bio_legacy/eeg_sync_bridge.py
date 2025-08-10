"""EEG Synchronization Bridge
---------------------------

Utility module for translating mock brainwave signals into
symbolic dream states. Useful for testing dream influence logic.

ΛTAG: eeg_bridge
ΛTAG: dream_influence
"""

from __future__ import annotations

import random
from collections.abc import Iterable
from enum import Enum
from typing import Dict


class BrainwaveBand(Enum):
    """Enumeration of basic brainwave bands."""

    DELTA = "delta"
    THETA = "theta"
    ALPHA = "alpha"
    BETA = "beta"
    GAMMA = "gamma"


class SymbolicState(Enum):
    """Symbolic dream states derived from brainwave dominance."""

    DEEP_DREAM = "deep_dream"
    DREAM_FLOW = "dream_flow"
    LUCID_DREAM = "lucid_dream"
    WAKE_TRANSITION = "wake_transition"
    HYPER_AWAKE = "hyper_awake"
    NEUTRAL = "neutral"


# ΛTAG: mock_signal_generation
def ingest_mock_eeg(num_samples: int = 1) -> Iterable[Dict[str, float]]:
    """Generate mock EEG readings.

    Args:
        num_samples: Number of sample readings to produce.

    Yields:
        Dictionary of brainwave amplitudes for each band.
    """

    for _ in range(num_samples):
        yield {band.value: random.random() for band in BrainwaveBand}


# ΛTAG: state_mapping
def map_to_symbolic_state(signals: Dict[str, float]) -> Dict[str, float | str]:
    """Map brainwave amplitudes to a symbolic dream state."""

    if not signals:
        return {"state": SymbolicState.NEUTRAL.value}

    dominant_band = max(signals, key=signals.get)
    mapping = {
        BrainwaveBand.DELTA.value: SymbolicState.DEEP_DREAM,
        BrainwaveBand.THETA.value: SymbolicState.DREAM_FLOW,
        BrainwaveBand.ALPHA.value: SymbolicState.LUCID_DREAM,
        BrainwaveBand.BETA.value: SymbolicState.WAKE_TRANSITION,
        BrainwaveBand.GAMMA.value: SymbolicState.HYPER_AWAKE,
    }
    symbolic_state = mapping.get(dominant_band, SymbolicState.NEUTRAL)

    drift_score = sum(abs(v - 0.5) for v in signals.values()) / len(signals)
    affect_delta = signals.get("theta", 0.0) - signals.get("beta", 0.0)

    return {
        "state": symbolic_state.value,
        "dominant_band": dominant_band,
        "driftScore": drift_score,
        "affect_delta": affect_delta,
    }


__all__ = [
    "BrainwaveBand",
    "SymbolicState",
    "ingest_mock_eeg",
    "map_to_symbolic_state",
]
