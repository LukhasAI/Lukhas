"""Bridge for lukhas.governance.guardian.guardian_impl."""

from __future__ import annotations

from importlib import import_module
from typing import List

__all__: List[str] = []

_BACKENDS = (
    "lukhas_website.lukhas.governance.guardian.guardian_impl",
    "governance.guardian.guardian_impl",
    "candidate.governance.guardian.guardian_impl",
)

for _candidate in _BACKENDS:
    try:
        _mod = import_module(_candidate)
    except Exception:
        continue
    for _attr in dir(_mod):
        if _attr.startswith("_"):
            continue
        globals()[_attr] = getattr(_mod, _attr)
        if _attr not in __all__:
            __all__.append(_attr)
    break


if "GuardianSystemImpl" not in globals():

    class GuardianSystemImpl:  # type: ignore[misc]
        """Fallback guardian system implementation."""

        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

        def evaluate(self, *args, **kwargs):
            return {"allowed": True, "reason": "stub"}

    __all__.append("GuardianSystemImpl")
