"""Bridge: bridge.api.identity -> canonical implementations."""
from __future__ import annotations
from lukhas._bridgeutils import bridge_from_candidates

_CANDIDATES = (
    "lukhas_website.lukhas.bridge.api.identity",
    "candidate.bridge.api.identity",
)

__all__, _exports = bridge_from_candidates(*_CANDIDATES)
globals().update(_exports)
