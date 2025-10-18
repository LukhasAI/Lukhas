"""Bridge: consciousness.systems -> canonical implementations."""
from __future__ import annotations

from _bridgeutils import bridge_from_candidates

_CANDIDATES = (
    "lukhas_website.consciousness.systems",
    "candidate.consciousness.systems",
    "consciousness.systems",
)

__all__, _exports = bridge_from_candidates(*_CANDIDATES)
globals().update(_exports)
