"""Bridge: tools.scripts."""
from __future__ import annotations

from lukhas._bridgeutils import bridge_from_candidates

_CANDIDATES = (
    "lukhas_website.lukhas.tools.scripts",
    "candidate.tools.scripts",
    "tools.scripts",
)
__all__, _exports = bridge_from_candidates(*_CANDIDATES); globals().update(_exports)
