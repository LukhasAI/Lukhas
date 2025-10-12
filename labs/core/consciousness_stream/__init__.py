"""Bridge for candidate.core.consciousness_stream."""

from __future__ import annotations

from importlib import import_module
from typing import List

__all__: List[str] = []

for _candidate in (
    "labs.candidate.core.consciousness_stream",
    "core.consciousness_stream",
    "lukhas_website.lukhas.core.consciousness_stream",
):
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


if "ConsciousnessStream" not in globals():

    class ConsciousnessStream:
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

        def snapshot(self):
            return {"state": "idle"}

    __all__.append("ConsciousnessStream")
