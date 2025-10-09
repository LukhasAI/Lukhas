"""Bridge for lukhas.governance.guardian package."""

from __future__ import annotations

from importlib import import_module

for _candidate in (
    "lukhas_website.lukhas.governance.guardian",
    "governance.guardian",
    "candidate.governance.guardian",
):
    try:
        _mod = import_module(_candidate)
    except Exception:
        continue
    globals().update({k: getattr(_mod, k) for k in dir(_mod) if not k.startswith("_")})
    break
