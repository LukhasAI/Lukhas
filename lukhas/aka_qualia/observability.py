"""Bridge for ``lukhas.aka_qualia.observability``."""
from __future__ import annotations

from lukhas._bridgeutils import bridge_from_candidates

__all__, _exports = bridge_from_candidates(
    "lukhas_website.lukhas.aka_qualia.observability",
    "aka_qualia.observability",
    "candidate.aka_qualia.observability",
)
globals().update(_exports)

# ΛTAG: aka_qualia_bridge -- observability shim for imports

