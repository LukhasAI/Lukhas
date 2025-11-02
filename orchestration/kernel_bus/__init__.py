"""Bridge: orchestration.kernel_bus (message bus/contracts)."""

from __future__ import annotations

from _bridgeutils import bridge_from_candidates, safe_guard

_CANDIDATES = (
    "lukhas_website.orchestration.kernel_bus",
    "candidate.orchestration.kernel_bus",
    "orchestration.kernel_bus",
)
__all__, _exports = bridge_from_candidates(*_CANDIDATES)
globals().update(_exports)
safe_guard(__name__, __all__)
