"""Bridge module for branding_bridge → lukhas_website.lukhas.branding_bridge"""
from __future__ import annotations

from _bridgeutils import bridge_from_candidates, safe_guard

_CANDIDATES = (
    "lukhas_website.lukhas.branding_bridge",
    "candidate.branding_bridge",
    "labs.branding_bridge",
)
__all__, _exports = bridge_from_candidates(*_CANDIDATES)
globals().update(_exports)

# Backwards compatibility alias: BrandingBridge = LUKHASBrandingBridge
if "LUKHASBrandingBridge" in globals() and "BrandingBridge" not in globals():
    BrandingBridge = globals()["LUKHASBrandingBridge"]
    globals()["BrandingBridge"] = BrandingBridge
    if "BrandingBridge" not in __all__:
        __all__.append("BrandingBridge")

safe_guard(__name__, __all__)
