"""
LUKHAS Identity Facades
======================
T4 Architecture compliant facades for identity services
"""

from .authentication_facade import (
    AuthenticationFacade,
    AuthResult,
    UserProfile,
    AuthenticatorInterface,
    TokenManagerInterface,
    SessionManagerInterface,
    get_authentication_facade,
    authenticate_user,
    authenticate_token,
    authenticate_api_key
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
    "authenticate_api_key"
]