"""Bridge: core.consciousness_ticker -> canonical implementations."""
from __future__ import annotations

from lukhas._bridgeutils import bridge_from_candidates

_CANDIDATES = (
    "lukhas_website.lukhas.core.consciousness_ticker",
    "candidate.core.consciousness_ticker",
)

__all__, _exports = bridge_from_candidates(*_CANDIDATES)
globals().update(_exports)
