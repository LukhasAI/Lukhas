"""Bridge exposing the Guardian System Integration surface in labs."""
from __future__ import annotations

from _bridgeutils import bridge_from_candidates, safe_guard

__all__, _exports = bridge_from_candidates(
    "core.governance.guardian_system_integration",
    "governance.guardian_system_integration",
)

globals().update(_exports)

if not isinstance(__all__, list):
    __all__ = list(__all__)

safe_guard(__name__, __all__)
