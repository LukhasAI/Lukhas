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
    "AuthResult",
    "AuthenticationFacade",
    "AuthenticatorInterface",
    "SessionManagerInterface",
    "TokenManagerInterface",
    "UserProfile",
    "authenticate_api_key",
    "authenticate_token",
    "authenticate_user",
    "get_authentication_facade"
]
