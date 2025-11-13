"""Bridge: tools.scripts."""
from __future__ import annotations

from _bridgeutils import bridge_from_candidates

_CANDIDATES = (
    "lukhas_website.tools.scripts",
    "labs.tools.scripts",
    "tools.scripts",
)
__all__, _exports = bridge_from_candidates(*_CANDIDATES)
globals().update(_exports)
