"""Bridge: orchestration.routers (multi-provider routing)."""

from __future__ import annotations

from _bridgeutils import bridge_from_candidates

_CANDIDATES = (
    "lukhas_website.orchestration.routers",
    "candidate.orchestration.routers",
    "orchestration.routers",
)
__all__, _exports = bridge_from_candidates(*_CANDIDATES)
globals().update(_exports)
