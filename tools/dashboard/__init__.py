"""Bridge: tools.dashboard (avoid shadowing if lukhas/tools.py existed)."""

from __future__ import annotations

from _bridgeutils import bridge_from_candidates

_CANDIDATES = (
    "lukhas_website.tools.dashboard",
    "labs.tools.dashboard",
    "tools.dashboard",
)
__all__, _exports = bridge_from_candidates(*_CANDIDATES)
globals().update(_exports)
