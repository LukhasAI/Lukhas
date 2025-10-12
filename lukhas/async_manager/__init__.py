"""Bridge: lukhas.async_manager -> canonical implementations (TaskManager)."""
from __future__ import annotations

from lukhas._bridgeutils import bridge_from_candidates

_CANDIDATES = (
    "lukhas_website.lukhas.async_manager",
    "labs.async_manager",
)

__all__, _exports = bridge_from_candidates(*_CANDIDATES)
globals().update(_exports)
