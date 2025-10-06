"""
Cognitive Core bridge - canonical namespace for cognitive infrastructure.

Bridges to existing cognitive implementations in consciousness/cognitive.
"""
from __future__ import annotations

from importlib import import_module

# Prefer the rich implementation if present
_candidates = [
    "candidate.consciousness.cognitive",
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
    # Minimal façade - no error, just empty module
    __all__ = []
else:
    __all__ = getattr(_backend, "__all__", [n for n in dir(_backend) if not n.startswith("_")])
    globals().update({name: getattr(_backend, name) for name in __all__})
