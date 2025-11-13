"""Bridge: tools.commands."""
from __future__ import annotations

from _bridgeutils import bridge_from_candidates

_CANDIDATES = (
    "lukhas_website.tools.commands",
    "labs.tools.commands",
    "tools.commands",
)
__all__, _exports = bridge_from_candidates(*_CANDIDATES)
globals().update(_exports)
