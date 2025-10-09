"""Bridge for lukhas.api package."""

from __future__ import annotations

from importlib import import_module

for _candidate in (
    "lukhas_website.lukhas.api",
    "api",
    "candidate.api",
):
    try:
        _mod = import_module(_candidate)
    except Exception:
        continue
    globals().update({k: getattr(_mod, k) for k in dir(_mod) if not k.startswith("_")})
    break
