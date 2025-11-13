"""Bridge for governance.identity.auth_integrations."""

from __future__ import annotations

from importlib import import_module
__all__: list[str] = []

for _candidate in (
    "lukhas_website.governance.identity.auth_integrations",
    "candidate.governance.identity.auth_integrations",
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
