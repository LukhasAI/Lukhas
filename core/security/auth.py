"""Core security auth module.

This module re-exports authentication functionality from labs.core.security.auth
to maintain the expected import path: from core.security.auth import ...
"""

# Re-export all authentication functionality from labs
try:
    from labs.core.security.auth import *
    from labs.core.security.auth import (
        AuthMethod,
        AuthSession,
        EnhancedAuthenticationSystem,
        MFASetup,
        get_auth_system,
    )

    __all__ = [
        "AuthMethod",
        "AuthSession",
        "MFASetup",
        "EnhancedAuthenticationSystem",
        "get_auth_system",
    ]

except ImportError as e:
    # Fallback if labs module not available
    import logging
    logging.getLogger(__name__).warning(f"Could not import from labs.core.security.auth: {e}")

    # Provide minimal fallback implementations
    class EnhancedAuthenticationSystem:
        """Minimal fallback authentication system."""
        def __init__(self):
            pass

    def get_auth_system():
        """Minimal fallback auth system getter."""
        return EnhancedAuthenticationSystem()

    __all__ = ["EnhancedAuthenticationSystem", "get_auth_system"]
