"""Bridge: products.core (domain DTOs + flows)."""
from __future__ import annotations
from lukhas._bridgeutils import bridge_from_candidates
_CANDIDATES = (
    "lukhas_website.lukhas.products.core",
    "candidate.products.core",
    "products.core",
)
__all__, _exports = bridge_from_candidates(*_CANDIDATES); globals().update(_exports)
