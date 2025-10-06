"""Thin shim: bridge.api.analysis.drift_score -> canonical."""
from __future__ import annotations
from lukhas._bridgeutils import bridge_from_candidates

_CANDIDATES = (
    "lukhas_website.lukhas.bridge.api.analysis.drift_score",
    "candidate.bridge.api.analysis.drift_score",
)
__all__, _exports = bridge_from_candidates(*_CANDIDATES); globals().update(_exports)
