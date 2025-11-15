"""Bridge for governance.identity.core.sent.symbolic_scopes"""
from __future__ import annotations

from _bridgeutils import bridge_from_candidates, safe_guard

_CANDIDATES = (
    "labs.governance.identity.core.sent.symbolic_scopes",
    "candidate.governance.identity.core.sent.symbolic_scopes",
)
__all__, _exports = bridge_from_candidates(*_CANDIDATES)
globals().update(_exports)

# Ensure SymbolicScopesManager is available
if "SymbolicScopesManager" not in globals():
    class SymbolicScopesManager:
        """Stub SymbolicScopesManager class."""
        def __init__(self, *args, **kwargs):
            pass
    globals()["SymbolicScopesManager"] = SymbolicScopesManager
    if "SymbolicScopesManager" not in __all__:
        __all__.append("SymbolicScopesManager")

safe_guard(__name__, __all__)
