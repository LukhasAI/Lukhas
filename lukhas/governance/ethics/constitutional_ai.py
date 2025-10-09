"""Bridge for lukhas.governance.ethics.constitutional_ai."""

from __future__ import annotations

from importlib import import_module
from typing import List

__all__: List[str] = []

_CANDIDATES = [
    "lukhas_website.lukhas.governance.ethics.constitutional_ai",
    "governance.ethics.constitutional_ai",
    "candidate.governance.ethics.constitutional_ai",
]

for _name in _CANDIDATES:
    try:
        _module = import_module(_name)
    except Exception:
        continue
    for attr in dir(_module):
        if attr.startswith("_"):
            continue
        globals()[attr] = getattr(_module, attr)
        if attr not in __all__:
            __all__.append(attr)
    break
