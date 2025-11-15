"""Bridge for governance.ethics.constitutional_ai."""

from __future__ import annotations

from _bridgeutils import bridge_from_candidates, safe_guard

_CANDIDATES = (
    "lukhas_website.lukhas.governance.ethics.constitutional_ai",
    "lukhas_website.governance.ethics.constitutional_ai",
    "candidate.governance.ethics.constitutional_ai",
    "labs.governance.ethics.constitutional_ai",
    "labs.core.governance.constitutional_ai",
)
__all__, _exports = bridge_from_candidates(*_CANDIDATES)
globals().update(_exports)

# Ensure ConstitutionalFramework is always available
if "ConstitutionalFramework" not in globals():
    class ConstitutionalFramework:
        """Stub ConstitutionalFramework class."""
        def __init__(self, *args, **kwargs):
            pass
    globals()["ConstitutionalFramework"] = ConstitutionalFramework
    if "ConstitutionalFramework" not in __all__:
        __all__.append("ConstitutionalFramework")

# Ensure ConstitutionalAI is available
if "ConstitutionalAI" not in globals():
    class ConstitutionalAI:
        """Stub ConstitutionalAI class."""
        def __init__(self, *args, **kwargs):
            pass
    globals()["ConstitutionalAI"] = ConstitutionalAI
    if "ConstitutionalAI" not in __all__:
        __all__.append("ConstitutionalAI")

safe_guard(__name__, __all__)
