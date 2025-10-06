"""Bridge: lukhas.observability.advanced_metrics."""
from __future__ import annotations
from lukhas._bridgeutils import bridge_from_candidates
_CANDIDATES = (
    "lukhas_website.lukhas.observability.advanced_metrics",
    "candidate.observability.advanced_metrics",
    "observability.advanced_metrics",
)
__all__, _exports = bridge_from_candidates(*_CANDIDATES); globals().update(_exports)
