"""
QI Entanglement stubs (Tier 1 + Tier 2)

Purpose
-------
Provide import-stable, deterministic, and test-friendly placeholders for
quantum entanglement functionality without introducing heavy dependencies.
This module intentionally avoids real quantum math for Phase 0, but sets
clean interfaces and observability hooks for later upgrades.

Tiers implemented
-----------------
Tier 1 (safe stubs)
- QuantumState dataclass with id/amplitude/phase
- validate_states(): basic integrity checks with logging
- compute_entanglement(): deterministic placeholder (avg magnitude)
- generate_entanglement_report(): structured, stable schema

Tier 2 (expandable hooks)
- In-memory state_registry with helpers (register/get/list/seed)
- Deterministic seed_random_state() utility for reproducible tests
- Logging throughout for traceability if used accidentally during Phase 0
"""

import logging
import math
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional

logger = logging.getLogger(__name__)

__all__ = [
    "QuantumState",
    "validate_states",
    "compute_entanglement",
    "generate_entanglement_report",
    # Tier 2 hooks
    "state_registry",
    "register_state",
    "get_state",
    "list_states",
    "seed_random_state",
]

# --------------------------------------------------------------------
# Core Types (Tier 1)
# --------------------------------------------------------------------


@dataclass(frozen=True)
class QuantumState:
    """Minimal placeholder for a quantum state.

    Fields:
        id: Stable identifier (string) to avoid UUID instance serialization quirks
        amplitude: Placeholder scalar (not physically meaningful)
        phase: Placeholder scalar (not physically meaningful)
    """

    id: str = field(default_factory=lambda: f"QS-{uuid.uuid4().hex[:8]}")
    amplitude: float = 0.0
    phase: float = 0.0

    def magnitude(self) -> float:
        """Return a simple magnitude proxy for placeholder math."""
        # hypot(amplitude, phase) is stable and cheap
        return math.hypot(self.amplitude, self.phase)


# --------------------------------------------------------------------
# Core API (Tier 1)
# --------------------------------------------------------------------


def validate_states(states: Iterable[QuantumState]) -> bool:
    """Basic integrity checks for a sequence of states.

    Rules:
    - Non-empty iterable
    - All items are QuantumState instances
    """
    states_list = list(states)
    if not states_list:
        logger.warning("validate_states: no states provided")
        return False
    ok = all(isinstance(s, QuantumState) for s in states_list)
    if not ok:
        logger.error("validate_states: non-QuantumState entries detected")
    return ok


def compute_entanglement(states: Iterable[QuantumState]) -> float:
    """Deterministic placeholder score.

    Definition (placeholder):
        average(state.magnitude()) across provided states
    """
    states_list = list(states)
    if not validate_states(states_list):
        return 0.0
    score = sum(s.magnitude() for s in states_list) / len(states_list)
    logger.debug("compute_entanglement: n=%d score=%.6f", len(states_list), score)
    return float(score)


def generate_entanglement_report(states: Iterable[QuantumState]) -> Dict[str, Any]:
    """Return a structured, stable report dictionary.

    Schema:
        {
            "entanglement_score": float,
            "states_validated": bool,
            "state_count": int,
            "metadata": {
                "version": "stub-0.2",
                "module": "candidate.qi.qi_entanglement"
            }
        }
    """
    states_list = list(states)
    valid = validate_states(states_list)
    score = compute_entanglement(states_list) if valid else 0.0
    report = {
        "entanglement_score": score,
        "states_validated": valid,
        "state_count": len(states_list),
        "metadata": {"version": "stub-0.2", "module": __name__},
    }
    logger.debug("generate_entanglement_report: %s", report)
    return report


# --------------------------------------------------------------------
# Expandable Hooks (Tier 2)
# --------------------------------------------------------------------

# Simple in-memory registry for reproducible tests and fixtures
state_registry: Dict[str, QuantumState] = {}


def register_state(state: QuantumState, *, overwrite: bool = False) -> None:
    """Register a state in the in-memory registry."""
    if not isinstance(state, QuantumState):
        raise TypeError("register_state: state must be a QuantumState")
    if state.id in state_registry and not overwrite:
        logger.info("register_state: id '%s' already present (no overwrite)", state.id)
        return
    state_registry[state.id] = state
    logger.debug("register_state: stored id=%s", state.id)


def get_state(state_id: str) -> Optional[QuantumState]:
    """Fetch a state by id from the registry."""
    return state_registry.get(state_id)


def list_states() -> List[QuantumState]:
    """List all registered states."""
    # Return a copy to prevent accidental external mutation
    return list(state_registry.values())


def seed_random_state(seed: int, *, prefix: str = "QS") -> QuantumState:
    """Create a deterministic 'random' state for tests using a simple LCG.

    We avoid importing 'random' to keep the stub as hermetic as possible.
    The simple linear congruential generator here is sufficient to produce
    deterministic pseudo-random floats in [0, 1).

    LCG: X_{n+1} = (a * X_n + c) mod m
         with a=1664525, c=1013904223, m=2**32
    """
    # Single-step LCG based on provided seed
    a = 1664525
    c = 1013904223
    m = 2**32

    x1 = (a * (seed & 0xFFFFFFFF) + c) % m
    x2 = (a * x1 + c) % m

    # Map to [0, 1)
    f1 = x1 / m
    f2 = x2 / m

    # Scale to small, well-behaved ranges
    amplitude = (f1 * 2.0) - 1.0  # [-1, 1)
    phase = (f2 * 2.0) - 1.0  # [-1, 1)

    state = QuantumState(id=f"{prefix}-{seed}", amplitude=amplitude, phase=phase)
    register_state(state, overwrite=True)
    logger.debug("seed_random_state: seed=%d amplitude=%.6f phase=%.6f id=%s", seed, amplitude, phase, state.id)
