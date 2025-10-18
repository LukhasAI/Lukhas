"""Bridge for governance.identity.core.sing."""

from __future__ import annotations

from importlib import import_module

for _candidate in (
    "lukhas_website.governance.identity.core.sing",
    "governance.identity.core.sing",
    "candidate.governance.identity.core.sing",
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
