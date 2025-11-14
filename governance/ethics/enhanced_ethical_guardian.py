"""Bridge for governance.ethics.enhanced_ethical_guardian."""

from __future__ import annotations

from _bridgeutils import bridge_from_candidates, safe_guard

_CANDIDATES = (
    "lukhas_website.governance.ethics.enhanced_ethical_guardian",
    "candidate.governance.ethics.enhanced_ethical_guardian",
    "labs.governance.ethics.enhanced_ethical_guardian",
)
__all__, _exports = bridge_from_candidates(*_CANDIDATES)
globals().update(_exports)

# Ensure EnhancedEthicalGuardian is always available
if "EnhancedEthicalGuardian" not in globals():
    class EnhancedEthicalGuardian:
        """Stub EnhancedEthicalGuardian class."""
        def __init__(self, *args, **kwargs):
            pass
    globals()["EnhancedEthicalGuardian"] = EnhancedEthicalGuardian
    if "EnhancedEthicalGuardian" not in __all__:
        __all__.append("EnhancedEthicalGuardian")

safe_guard(__name__, __all__)
