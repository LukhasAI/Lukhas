"""Type definitions for OAuth 2.0 and JWT token management.

This module provides TypedDict definitions for JWT claims (RFC 7519) and
token introspection responses (RFC 7662), along with validation and
utility functions.
"""
from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone
from typing import Any, cast

from typing_extensions import NotRequired, TypedDict


class TokenClaims(TypedDict):
    """Represents the standard claims of a JSON Web Token (JWT) as per RFC 7519."""

    iss: str  # Issuer
    sub: str  # Subject
    aud: str | list[str]  # Audience
    exp: int  # Expiration Time (Unix timestamp)
    nbf: NotRequired[int]  # Not Before (Unix timestamp)
    iat: NotRequired[int]  # Issued At (Unix timestamp)
    jti: NotRequired[str]  # JWT ID
    scope: NotRequired[str]  # OAuth scope


class TokenIntrospection(TypedDict):
    """Represents the response from a token introspection endpoint as per RFC 7662."""

    active: bool  # Whether the token is active
    scope: NotRequired[str]  # Scope of the token
    client_id: NotRequired[str]  # Client identifier
    username: NotRequired[str]  # Human-readable identifier for the resource owner
    token_type: NotRequired[str]  # Type of the token (e.g., "bearer")
    exp: NotRequired[int]  # Expiration Time (Unix timestamp)
    iat: NotRequired[int]  # Issued At (Unix timestamp)
    nbf: NotRequired[int]  # Not Before (Unix timestamp)
    sub: NotRequired[str]  # Subject
    aud: NotRequired[str | list[str]]  # Audience
    iss: NotRequired[str]  # Issuer
    jti: NotRequired[str]  # JWT ID


def validate_token_claims(claims: dict[str, Any]) -> TokenClaims:
    """
    Validates and casts a dictionary to the TokenClaims TypedDict.

    Args:
        claims: A dictionary of token claims.

    Returns:
        The validated TokenClaims object.

    Raises:
        TypeError: If required fields are missing or have the wrong type.
    """
    if not all(key in claims for key in ("iss", "sub", "aud", "exp")):
        raise TypeError("Missing required claims in token.")
    return cast(TokenClaims, claims)


def validate_token_introspection(response: dict[str, Any]) -> TokenIntrospection:
    """
    Validates and casts a dictionary to the TokenIntrospection TypedDict.

    Args:
        response: A dictionary from a token introspection endpoint.

    Returns:
        The validated TokenIntrospection object.

    Raises:
        TypeError: If the 'active' field is missing or has the wrong type.
    """
    if "active" not in response or not isinstance(response["active"], bool):
        raise TypeError("Missing or invalid 'active' field in introspection response.")
    return cast(TokenIntrospection, response)


def is_token_expired(claims: TokenClaims) -> bool:
    """
    Checks if a token is expired based on its 'exp' claim.

    Args:
        claims: The token claims.

    Returns:
        True if the token is expired, False otherwise.
    """
    now = int(time.time())
    return claims["exp"] < now


def get_remaining_lifetime(claims: TokenClaims) -> timedelta:
    """
    Calculates the remaining lifetime of a token.

    Args:
        claims: The token claims.

    Returns:
        A timedelta object representing the remaining time. Returns a zero
        timedelta if the token is already expired.
    """
    if is_token_expired(claims):
        return timedelta(0)

    expiration_dt = datetime.fromtimestamp(claims["exp"], tz=timezone.utc)
    now_dt = datetime.now(timezone.utc)

    return expiration_dt - now_dt
