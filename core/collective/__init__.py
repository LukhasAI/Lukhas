"""Bridge to candidate collective."""
from __future__ import annotations
try:
    from candidate.core.collective import *  # noqa: F401, F403
    __all__ = [n for n in dir() if not n.startswith("_")]
except ImportError:
    __all__ = []
