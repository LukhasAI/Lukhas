"""Bridge: core.clock (time abstraction)."""
from __future__ import annotations

from _bridgeutils import bridge_from_candidates

_CANDIDATES = (
    "lukhas_website.core.clock",
    "labs.core.clock",
    "core.clock",
)
__all__, _exports = bridge_from_candidates(*_CANDIDATES)
globals().update(_exports)
