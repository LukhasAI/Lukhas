"""Bridge: core.consciousness_ticker -> canonical implementations."""

from __future__ import annotations

from _bridgeutils import bridge_from_candidates

_CANDIDATES = (
    "lukhas_website.core.consciousness_ticker",
    "labs.core.consciousness_ticker",
)

__all__, _exports = bridge_from_candidates(*_CANDIDATES)
globals().update(_exports)
