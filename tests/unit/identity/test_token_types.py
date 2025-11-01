from datetime import datetime, timezone

import pytest

from lukhas.identity.token_types import (
    get_remaining_lifetime,
    is_token_expired,
    validate_token_claims,
    validate_token_introspection,
)


def _now_ts() -> int:
    return int(datetime.now(timezone.utc).timestamp())


def test_validate_full_claims_and_lifetime() -> None:
    now = _now_ts()
    claims = {
        "iss": "issuer",
        "sub": "user123",
        "aud": ["aud1", "aud2"],
        "exp": now + 3600,
        "nbf": now - 10,
        "iat": now,
        "jti": "jid",
        "scope": "read write",
    }

    validated = validate_token_claims(claims)
    assert validated["iss"] == "issuer"
    assert not is_token_expired(validated)
    remaining = get_remaining_lifetime(validated)
    assert remaining.total_seconds() > 3500


def test_validate_minimal_claims() -> None:
    now = _now_ts()
    claims = {"iss": "i", "sub": "s", "aud": "a", "exp": now + 5}
    validated = validate_token_claims(claims)
    assert validated["aud"] == "a"


def test_introspection_active_and_inactive() -> None:
    resp_active = {"active": True, "scope": "read"}
    validated = validate_token_introspection(resp_active)
    assert validated["active"] is True

    resp_inactive = {"active": False}
    validated2 = validate_token_introspection(resp_inactive)
    assert validated2["active"] is False


def test_missing_active_in_introspection_raises() -> None:
    with pytest.raises(ValueError):
        validate_token_introspection({})


def test_missing_required_claims_raise() -> None:
    now = _now_ts()
    # missing 'iss'
    bad = {"sub": "s", "aud": "a", "exp": now + 10}
    with pytest.raises(ValueError):
        validate_token_claims(bad)


def test_expired_token_remaining_lifetime_zero() -> None:
    now = _now_ts()
    claims = {"iss": "i", "sub": "s", "aud": "a", "exp": now - 10}
    validated = validate_token_claims(claims)
    assert is_token_expired(validated)
    assert get_remaining_lifetime(validated).total_seconds() == 0
