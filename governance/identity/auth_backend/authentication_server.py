"""
Authentication Server Bridge
Bridge to governance identity authentication backend

Identity authentication server implementation.
Constellation Framework: ⚛️
"""
try:
    from candidate.governance.identity.auth_backend.authentication_server import *  # noqa: F401, F403
except (ModuleNotFoundError, ImportError):
    try:
        from labs.governance.identity.auth_backend.authentication_server import *  # noqa: F401, F403
    except (ModuleNotFoundError, ImportError):
        # Minimal stub
        class AuthenticationServer:
            """Placeholder for authentication server."""
            pass

__all__ = ["AuthenticationServer"]
