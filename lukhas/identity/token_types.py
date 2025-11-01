from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Union, cast

from typing_extensions import NotRequired, TypedDict


class TokenClaims(TypedDict):
    """RFC 7519 minimal JWT claims used by the system.

    Required fields are enforced by ``validate_token_claims``.
    Optional fields are passed through when present.
    """

    iss: str
    sub: str
    aud: Union[str, List[str]]
    exp: int
    nbf: NotRequired[int]
    iat: NotRequired[int]
    jti: NotRequired[str]
    scope: NotRequired[str]


class TokenIntrospection(TypedDict):
    """RFC 7662 token introspection response fields accepted by the system."""

    active: bool
    scope: NotRequired[str]
    client_id: NotRequired[str]
    username: NotRequired[str]
    token_type: NotRequired[str]
    exp: NotRequired[int]
    iat: NotRequired[int]
    nbf: NotRequired[int]
    sub: NotRequired[str]
    aud: NotRequired[Union[str, List[str]]]
    iss: NotRequired[str]
    jti: NotRequired[str]


def _now_ts() -> int:
    """Return current UTC timestamp as seconds since epoch (int)."""
    return int(datetime.now(timezone.utc).timestamp())


def mk_exp(seconds_from_now: int) -> int:
    """Return an ``exp`` timestamp ``seconds_from_now`` in UTC.

    Conservative helper to keep tests deterministic and avoid repeated datetime logic.
    """
    if not isinstance(seconds_from_now, int):  # defensive
        raise TypeError("seconds_from_now must be an int")
    if seconds_from_now < 0:
        # Allow negative for already-expired tokens but keep explicit behavior
        return _now_ts() + seconds_from_now
    return _now_ts() + seconds_from_now


def mk_iat(seconds_ago: int = 0) -> int:
    """Return an ``iat`` timestamp ``seconds_ago`` in UTC (default: now).

    Helps tests create deterministic issued-at values.
    """
    if not isinstance(seconds_ago, int):
        raise TypeError("seconds_ago must be an int")
    if seconds_ago < 0:
        return _now_ts() - seconds_ago
    return _now_ts() - seconds_ago


def validate_token_claims(claims: Dict[str, Any]) -> TokenClaims:
    """Validate a dict and return it typed as :class:`TokenClaims`.

    Raises TypeError or ValueError on invalid/missing required fields.
    """
    if not isinstance(claims, dict):
        raise TypeError("claims must be a dict")

    required = ["iss", "sub", "aud", "exp"]
    for k in required:
        if k not in claims:
            raise ValueError(f"missing required claim: {k}")

    # Basic type checks
    if not isinstance(claims["iss"], str):
        raise TypeError("iss must be a string")
    if not isinstance(claims["sub"], str):
        raise TypeError("sub must be a string")
    aud = claims["aud"]
    if not isinstance(aud, (str, list)):
        raise TypeError("aud must be a string or list of strings")
    if isinstance(aud, list) and not all(isinstance(x, str) for x in aud):
        raise TypeError("aud list must contain only strings")
    if not isinstance(claims["exp"], int):
        raise TypeError("exp must be an integer timestamp")

    return cast(TokenClaims, claims)


def validate_token_introspection(response: Dict[str, Any]) -> TokenIntrospection:
    """Validate an RFC 7662 token introspection response.

    Raises TypeError/ValueError on invalid input.
    """
    if not isinstance(response, dict):
        raise TypeError("introspection response must be a dict")

    if "active" not in response:
        raise ValueError("introspection response missing 'active' field")
    if not isinstance(response["active"], bool):
        raise TypeError("'active' must be a boolean")

    # optional fields are not strictly typed here, but basic checks can be done
    aud = response.get("aud")
    if aud is not None and not isinstance(aud, (str, list)):
        raise TypeError("aud must be a string or list of strings if present")

    return cast(TokenIntrospection, response)


def is_token_expired(claims: TokenClaims) -> bool:
    """Return True if token represented by claims is expired.

    Uses UTC timestamps.
    """
    now = _now_ts()
    return claims["exp"] <= now


def get_remaining_lifetime(claims: TokenClaims) -> timedelta:
    """Return a timedelta of remaining lifetime (0 if expired)."""
    now = _now_ts()
    remaining = claims["exp"] - now
    if remaining <= 0:
        return timedelta(seconds=0)
    return timedelta(seconds=remaining)


__all__ = [
    "TokenClaims",
    "TokenIntrospection",
    "validate_token_claims",
    "validate_token_introspection",
    "is_token_expired",
    "get_remaining_lifetime",
    "mk_exp",
    "mk_iat",
]
