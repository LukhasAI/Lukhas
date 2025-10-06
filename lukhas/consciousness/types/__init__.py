"""Bridge: consciousness.types -> canonical implementations."""
from __future__ import annotations

from lukhas._bridgeutils import bridge_from_candidates

_CANDIDATES = (
    "lukhas_website.lukhas.consciousness.types",
    "candidate.consciousness.types",
    "consciousness.types",
)

__all__, _exports = bridge_from_candidates(*_CANDIDATES)
globals().update(_exports)
