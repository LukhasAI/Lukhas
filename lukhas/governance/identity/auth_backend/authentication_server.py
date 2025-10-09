"""Bridge for lukhas.governance.identity.auth_backend.authentication_server."""

from __future__ import annotations

from importlib import import_module

for _candidate in (
    "lukhas_website.lukhas.governance.identity.auth_backend.authentication_server",
    "governance.identity.auth_backend.authentication_server",
    "candidate.governance.identity.auth_backend.authentication_server",
):
    try:
        _mod = import_module(_candidate)
    except Exception:
        continue
    globals().update({k: getattr(_mod, k) for k in dir(_mod) if not k.startswith("_")})
    break


class AuthenticationServer:  # type: ignore[misc]
    def start(self):
        return True


class DataSubjectRight:  # type: ignore[misc]
    ACCESS = "access"
    ERASURE = "erasure"
