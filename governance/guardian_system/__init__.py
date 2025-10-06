"""Guardian system package bridge."""
from __future__ import annotations

# Import from parent package
try:
    from governance.guardian_system import *  # noqa: F401, F403
    __all__ = [n for n in dir() if not n.startswith("_")]
except ImportError:
    try:
        from candidate.governance.guardian_system import *  # noqa: F401, F403
        __all__ = [n for n in dir() if not n.startswith("_")]
    except ImportError:
        __all__ = []
