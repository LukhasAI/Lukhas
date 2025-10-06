"""Bridge: lukhas.cognitive_core -> candidate implementations."""
from __future__ import annotations

from importlib import import_module

_candidates = [
    "candidate.cognitive_core",
    "consciousness.cognitive",
]

_backend = None
for path in _candidates:
    try:
        _backend = import_module(path)
        break
    except Exception:
        continue

if _backend is None:
    __all__ = []
else:
    __all__ = getattr(_backend, "__all__", [n for n in dir(_backend) if not n.startswith("_")])
    globals().update({name: getattr(_backend, name) for name in __all__})
