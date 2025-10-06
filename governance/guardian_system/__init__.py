"""Bridge: governance.guardian_system (safety guard orchestration)."""
from __future__ import annotations

from lukhas._bridgeutils import bridge_from_candidates, safe_guard, deprecate

_CANDIDATES = (
    "lukhas_website.lukhas.governance.guardian_system",
    "candidate.governance.guardian_system",
    "guardian",
)

__all__, _exports = bridge_from_candidates(*_CANDIDATES)
globals().update(_exports)
safe_guard(__name__, __all__)
deprecate(__name__, "prefer guardian or lukhas.governance.guardian_system")
