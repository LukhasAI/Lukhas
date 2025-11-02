"""Compatibility shim for legacy `core.common.config` imports."""

from __future__ import annotations

from _bridgeutils import bridge_from_candidates, safe_guard

__all__, _exports = bridge_from_candidates(
    "labs.core.common.config",
    "lukhas_website.lukhas.core.common.config",
    "candidate.core.common.config",
)

globals().update(_exports)
safe_guard(__name__, __all__)
