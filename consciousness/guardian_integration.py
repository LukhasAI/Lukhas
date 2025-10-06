"""Bridge for consciousness.guardian_integration -> candidate implementations."""
from __future__ import annotations

from lukhas._bridgeutils import bridge

_mod, _exports, __all__ = bridge(
    candidates=(
        "candidate.consciousness.integration.guardian",
        "candidate.governance.guardian_system",
    ),
    deprecation=(
        "Importing from 'consciousness.guardian_integration' is deprecated; "
        "prefer 'lukhas.consciousness' or 'governance.guardian_system' APIs."
    ),
)

globals().update(_exports)
del _mod, _exports
