"""Bridge for lukhas.identity package."""

from __future__ import annotations

from importlib import import_module
from typing import Any, Dict

__all__ = ["DeviceRegistry", "LUKHASIdentityService"]

_CANDIDATES = (
    "lukhas_website.lukhas.identity",
    "identity",
    "candidate.identity",
)

for _candidate in _CANDIDATES:
    try:
        _mod = import_module(_candidate)
    except Exception:
        continue
    for name in dir(_mod):
        if name.startswith("_"):
            continue
        globals()[name] = getattr(_mod, name)
        if name not in __all__:
            __all__.append(name)
    break


if "DeviceRegistry" not in globals():

    class DeviceRegistry(dict):  # type: ignore[misc]
        def register(self, device_id: str, metadata: Dict[str, Any]):
            self[device_id] = metadata


if "LUKHASIdentityService" not in globals():

    class LUKHASIdentityService:  # type: ignore[misc]
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

        async def resolve_identity(self, user_id: str):
            return {"user_id": user_id, "tier": "basic"}
