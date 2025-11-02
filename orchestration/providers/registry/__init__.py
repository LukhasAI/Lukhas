"""Bridge: orchestration.providers.registry (provider lookup/feature flags)."""

from __future__ import annotations

from _bridgeutils import bridge_from_candidates

_CANDIDATES = (
    "lukhas_website.orchestration.providers.registry",
    "candidate.orchestration.providers.registry",
    "orchestration.providers.registry",
)
__all__, _exports = bridge_from_candidates(*_CANDIDATES)
globals().update(_exports)
