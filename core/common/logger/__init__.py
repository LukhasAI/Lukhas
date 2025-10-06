"""Bridge: core.common.logger (getLogger, adapters, formatters)."""
from __future__ import annotations
from lukhas._bridgeutils import bridge_from_candidates
_CANDIDATES = (
    "lukhas_website.lukhas.core.common.logger",
    "candidate.core.common.logger",
    "core.common.logger",
)
__all__, _exports = bridge_from_candidates(*_CANDIDATES); globals().update(_exports)
