"""Bridge for governance.ethics.constitutional_ai."""

from __future__ import annotations

from importlib import import_module
__all__: list[str] = []

_CANDIDATES = [
    "lukhas_website.governance.ethics.constitutional_ai",
    "governance.ethics.constitutional_ai",
    "labs.governance.ethics.constitutional_ai",
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
