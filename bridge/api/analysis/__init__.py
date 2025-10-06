"""Bridge: bridge.api.analysis (drift_score, analytics)."""
from __future__ import annotations
from lukhas._bridgeutils import bridge_from_candidates

# Top-level package bridge
_PKG = (
    "lukhas_website.lukhas.bridge.api.analysis",
    "candidate.bridge.api.analysis",
    "bridge.api.analysis",
)
__all__, _exports = bridge_from_candidates(*_PKG); globals().update(_exports)
