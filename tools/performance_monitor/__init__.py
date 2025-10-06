"""Bridge: tools.performance_monitor (used heavily by tests)."""
from __future__ import annotations
from lukhas._bridgeutils import bridge_from_candidates
_CANDIDATES = (
    "lukhas_website.lukhas.tools.performance_monitor",
    "candidate.tools.performance_monitor",
    "tools.performance_monitor",
)
__all__, _exports = bridge_from_candidates(*_CANDIDATES); globals().update(_exports)
