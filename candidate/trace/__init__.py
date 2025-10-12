"""Bridge: candidate.trace (router trace / metrics hooks)."""
from __future__ import annotations

from lukhas._bridgeutils import bridge_from_candidates

_CANDIDATES = (
    "lukhas_website.lukhas.candidate.trace",
    "candidate.core.trace",
    "core.trace",
    "candidate.trace",
)
__all__, _exports = bridge_from_candidates(*_CANDIDATES); globals().update(_exports)
