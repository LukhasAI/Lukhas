"""Bridge for governance.guardian.guardian_impl."""

from __future__ import annotations

from importlib import import_module

for _candidate in (
    "lukhas_website.governance.guardian.guardian_impl",
    "governance.guardian.guardian_impl",
):
    try:
        _mod = import_module(_candidate)
    except Exception:
        continue
    globals().update({k: getattr(_mod, k) for k in dir(_mod) if not k.startswith("_")})
    break
