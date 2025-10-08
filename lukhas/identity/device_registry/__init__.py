"""Bridge for lukhas.identity.device_registry."""

from __future__ import annotations

from importlib import import_module

for _candidate in (
    "lukhas_website.lukhas.identity.device_registry",
    "identity.device_registry",
    "candidate.identity.device_registry",
):
    try:
        _mod = import_module(_candidate)
    except Exception:
        continue
    for _attr in dir(_mod):
        if _attr.startswith("_"):
            continue
        globals()[_attr] = getattr(_mod, _attr)
    break
