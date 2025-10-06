"""Thin shim: bridge.api.analysis.drift_score -> canonical."""
from __future__ import annotations
from lukhas._bridgeutils import bridge_from_candidates

_CANDIDATES = (
    "lukhas_website.lukhas.bridge.api.analysis.drift_score",
    "candidate.bridge.api.analysis.drift_score",
)
__all__, _exports = bridge_from_candidates(*_CANDIDATES); globals().update(_exports)

# Add stub function if not in bridge
if "update_user_drift_profile" not in globals():
    async def update_user_drift_profile(*args, **kwargs):
        """Stub for drift profile update."""
        pass
    if "__all__" in globals() and "update_user_drift_profile" not in __all__:
        __all__.append("update_user_drift_profile")
    elif "__all__" not in globals():
        __all__ = ["update_user_drift_profile"]
