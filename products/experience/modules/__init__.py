"""Bridge: products.experience.modules (composable UX pieces)."""
from __future__ import annotations

from _bridgeutils import bridge_from_candidates

_CANDIDATES = (
    "lukhas_website.products.experience.modules",
    "candidate.products.experience.modules",
    "products.experience.modules",
)
__all__, _exports = bridge_from_candidates(*_CANDIDATES); globals().update(_exports)
