"""Bridge: aka_qualia  canonical surface for qualia research components."""
from __future__ import annotations

from lukhas._bridgeutils import bridge_from_candidates, safe_guard

__all__, _exp = bridge_from_candidates(
    "lukhas_website.lukhas.aka_qualia",
    "candidate.aka_qualia",
    "aka_qualia",
)
globals().update(_exp)
safe_guard(__name__, __all__)
