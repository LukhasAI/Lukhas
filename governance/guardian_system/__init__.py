"""Bridge: governance.guardian_system -> canonical implementations."""
from __future__ import annotations
from lukhas._bridgeutils import bridge_from_candidates

_CANDIDATES = (
    "lukhas_website.lukhas.governance.guardian_system",
    "candidate.governance.guardian_system",
)

__all__, _exports = bridge_from_candidates(*_CANDIDATES)
globals().update(_exports)
