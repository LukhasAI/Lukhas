"""Thin shim: bridge.api.analysis.analytics -> canonical."""
from __future__ import annotations

from lukhas._bridgeutils import bridge_from_candidates

_CANDIDATES = (
    "lukhas_website.lukhas.bridge.api.analysis.analytics",
    "candidate.bridge.api.analysis.analytics",
)
__all__, _exports = bridge_from_candidates(*_CANDIDATES); globals().update(_exports)
