"""Bridge: products.experience (public facade for UX modules)."""

from __future__ import annotations

from _bridgeutils import bridge_from_candidates, deprecate

_CANDIDATES = (
    "lukhas_website.products.experience",
    "candidate.products.experience",
    "products.experience",
)
__all__, _exports = bridge_from_candidates(*_CANDIDATES)
globals().update(_exports)
deprecate(__name__, "use via products.experience")
