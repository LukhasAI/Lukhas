"""Bridge: tools.commands."""
from __future__ import annotations
from lukhas._bridgeutils import bridge_from_candidates
_CANDIDATES = (
    "lukhas_website.lukhas.tools.commands",
    "candidate.tools.commands",
    "tools.commands",
)
__all__, _exports = bridge_from_candidates(*_CANDIDATES); globals().update(_exports)
