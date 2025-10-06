"""Bridge: matriz_thought_loop -> canonical implementations."""
from __future__ import annotations

from lukhas._bridgeutils import bridge_from_candidates

_CANDIDATES = (
    "lukhas_website.lukhas.consciousness.matriz_thought_loop",
    "candidate.consciousness.matriz_thought_loop",
    "consciousness.matriz_thought_loop",
)

__all__, _exports = bridge_from_candidates(*_CANDIDATES)
globals().update(_exports)
