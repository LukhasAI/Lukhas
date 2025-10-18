"""Bridge for governance.guardian_serializers."""

from __future__ import annotations

from importlib import import_module

for _candidate in (
    "lukhas_website.governance.guardian_serializers",
    "governance.guardian_serializers",
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
