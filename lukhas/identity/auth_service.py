"""Bridge for lukhas.identity.auth_service."""

from __future__ import annotations

from importlib import import_module

for _candidate in (
    "lukhas_website.lukhas.identity.auth_service",
    "identity.auth_service",
    "labs.identity.auth_service",
):
    try:
        _mod = import_module(_candidate)
    except Exception:
        continue
    globals().update({k: getattr(_mod, k) for k in dir(_mod) if not k.startswith("_")})
    break


class LUKHASIdentityService:  # type: ignore[misc]
    """Fallback identity service."""

    async def resolve_identity(self, user_id: str):
        return {"user_id": user_id, "tier": "basic"}
