"""
LUKHAS Identity Facades
======================
T4 Architecture compliant facades for identity services
"""

from .authentication_facade import (
    AuthenticationFacade,
    AuthenticatorInterface,
    AuthResult,
    SessionManagerInterface,
    TokenManagerInterface,
    UserProfile,
    authenticate_api_key,
    authenticate_token,
    authenticate_user,
    get_authentication_facade,
)

__all__ = [
    "AuthenticationFacade",
    "AuthResult",
    "UserProfile",
    "AuthenticatorInterface",
    "TokenManagerInterface",
    "SessionManagerInterface",
    "get_authentication_facade",
    "authenticate_user",
    "authenticate_token",
    "authenticate_api_key",
]
