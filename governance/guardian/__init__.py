"""Bridge: governance.guardian (compat with legacy tests)."""
from __future__ import annotations
from lukhas._bridgeutils import bridge_from_candidates
# Try richer guardian system first; fallback to SafetyGuard alias.
_PKG = (
  "lukhas_website.lukhas.governance.guardian",
  "candidate.governance.guardian",
  "governance.guardian",
)
__all__, _exports = bridge_from_candidates(*_PKG); globals().update(_exports)
if not __all__:
    # Minimal fallback to known class
    try:
        from lukhas._bridgeutils import bridge_from_candidates as bcf
        __all__, _exports = bcf("lukhas.core.policy_guard")
        globals().update(_exports)
    except Exception:
        pass
