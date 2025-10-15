"""Bridge: core.business (products/experience integration points)."""
from __future__ import annotations

from lukhas._bridgeutils import bridge_from_candidates

_CANDIDATES = (
    "lukhas_website.lukhas.core.business",
    "labs.core.business",
    "core.business",
)
__all__, _exports = bridge_from_candidates(*_CANDIDATES)
globals().update(_exports)
