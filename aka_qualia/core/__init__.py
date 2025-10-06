"""Bridge: aka_qualia.core"""
from __future__ import annotations
from lukhas._bridgeutils import bridge_from_candidates, safe_guard, deprecate
_CANDIDATES = (
    "lukhas_website.lukhas.aka_qualia.core",
    "candidate.aka_qualia.core",
)
__all__, _exp = bridge_from_candidates(*_CANDIDATES); globals().update(_exp)
safe_guard(__name__, __all__); deprecate(__name__, "prefer lukhas.aka_qualia.core")
