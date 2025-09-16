"""Quantum entanglement utilities for the QI subsystem."""

from __future__ import annotations

import hashlib
import logging
import math
from collections.abc import Iterable, Sequence
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class QuantumState:
    """Representation of a simplified qubit-like state."""

    label: str
    amplitudes: Sequence[float]
    phase: float = 0.0
    coherence: float = 1.0
    affect_bias: float = 0.0

    def normalized(self) -> tuple[float, ...]:
        """Return the normalized amplitude vector."""

        magnitude = math.sqrt(sum(component**2 for component in self.amplitudes))
        if magnitude == 0:
            msg = f"State '{self.label}' has zero magnitude amplitudes"
            logger.error(msg)
            raise ValueError(msg)
        return tuple(component / magnitude for component in self.amplitudes)

    def probabilities(self) -> tuple[float, ...]:
        """Return probabilities for measuring the state."""

        normalized = self.normalized()
        return tuple(component**2 for component in normalized)


@dataclass(frozen=True)
class EntanglementResult:
    """Container for entanglement analysis results."""

    state_a: QuantumState
    state_b: QuantumState
    entanglement_score: float
    driftScore: float
    affect_delta: float
    collapseHash: str
    correlation_index: float
    diagnostics: dict[str, float]


def validate_states(*states: QuantumState) -> None:
    """Validate that all quantum states share a compatible structure."""

    if not states:
        raise ValueError("At least one state is required for entanglement analysis")

    length = len(states[0].amplitudes)
    for state in states:
        if len(state.amplitudes) != length:
            msg = "Quantum states must have equal amplitude dimensions"
            logger.error(msg)
            raise ValueError(msg)


def _collapse_hash(states: Iterable[QuantumState], entanglement_score: float) -> str:
    """Create a deterministic hash for the collapse signature."""

    hash_input = ";".join(
        f"{state.label}:{','.join(f'{amp:.6f}' for amp in state.normalized())}:{state.phase:.6f}:{state.coherence:.6f}"
        for state in states
    )
    hash_input += f"|score:{entanglement_score:.6f}"
    digest = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()
    return digest[:24]


def _phase_alignment(a: float, b: float) -> float:
    """Compute normalized phase alignment between two states."""

    return (math.cos(a - b) + 1) / 2


def compute_entanglement(state_a: QuantumState, state_b: QuantumState) -> EntanglementResult:
    """Compute an entanglement metric between two simplified states."""

    validate_states(state_a, state_b)

    # ΛTAG: entanglement_analysis
    norm_a = state_a.normalized()
    norm_b = state_b.normalized()

    alignment = sum(component_a * component_b for component_a, component_b in zip(norm_a, norm_b))
    phase_alignment = _phase_alignment(state_a.phase, state_b.phase)
    coherence = min(
        max(state_a.coherence, 0.0),
        max(state_b.coherence, 0.0),
        1.0,
    )

    entanglement_score = max(0.0, min(1.0, abs(alignment) * phase_alignment * coherence))

    vector_delta = math.sqrt(sum((a - b) ** 2 for a, b in zip(norm_a, norm_b)))
    drift_score = max(0.0, 1.0 - min(1.0, vector_delta))
    affect_delta = state_a.affect_bias - state_b.affect_bias

    correlation_index = max(0.0, min(1.0, (abs(alignment) + phase_alignment) / 2))

    diagnostics = {
        "alignment": alignment,
        "phase_alignment": phase_alignment,
        "vector_delta": vector_delta,
    }

    collapse_hash = _collapse_hash((state_a, state_b), entanglement_score)

    logger.debug(
        "Entanglement computed | states=%s/%s score=%.3f drift=%.3f affect_delta=%.3f",
        state_a.label,
        state_b.label,
        entanglement_score,
        drift_score,
        affect_delta,
    )

    return EntanglementResult(
        state_a=state_a,
        state_b=state_b,
        entanglement_score=entanglement_score,
        driftScore=drift_score,
        affect_delta=affect_delta,
        collapseHash=collapse_hash,
        correlation_index=correlation_index,
        diagnostics=diagnostics,
    )


def generate_entanglement_report(result: EntanglementResult) -> dict[str, float | str]:
    """Produce a structured report from an entanglement result."""

    return {
        "state_a": result.state_a.label,
        "state_b": result.state_b.label,
        "entanglement_score": round(result.entanglement_score, 6),
        "driftScore": round(result.driftScore, 6),
        "affect_delta": round(result.affect_delta, 6),
        "collapseHash": result.collapseHash,
        "correlation_index": round(result.correlation_index, 6),
        "alignment": round(result.diagnostics["alignment"], 6),
        "phase_alignment": round(result.diagnostics["phase_alignment"], 6),
        "vector_delta": round(result.diagnostics["vector_delta"], 6),
    }


__all__ = [
    "QuantumState",
    "EntanglementResult",
    "compute_entanglement",
    "generate_entanglement_report",
    "validate_states",
]
