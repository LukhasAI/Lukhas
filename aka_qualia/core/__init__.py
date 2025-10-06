"""Bridge: aka_qualia.core (package vs module ambiguity)."""
from __future__ import annotations
from lukhas._bridgeutils import bridge_from_candidates
_CANDIDATES = (
    "lukhas_website.lukhas.aka_qualia.core",
    "candidate.aka_qualia.core",
    "aka_qualia.core",
)
__all__, _exports = bridge_from_candidates(*_CANDIDATES); globals().update(_exports)
