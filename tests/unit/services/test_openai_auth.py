"""Unit tests for OpenAI façade authentication helpers."""
from __future__ import annotations

import pytest
from fastapi import HTTPException

from adapters.openai import TokenClaims, require_bearer, verify_token_with_policy


@pytest.mark.parametrize(
    "token,expected_owner,expected_type",
    [
        ("sk-lukhas-standard-1234567890abcdef", "standard", "pat"),
        ("sk-lukhas-org1-aaaaaaaaaaaaaaaa", "org1", "pat"),
    ],
)
def test_verify_token_with_policy_for_pat(token: str, expected_owner: str, expected_type: str) -> None:
    """Personal access tokens resolve to TokenClaims with policy guard validation."""
    claims = verify_token_with_policy(token)

    assert isinstance(claims, TokenClaims)
    assert claims.owner == expected_owner
    assert claims.token_type == expected_type
    assert claims.has_scope("api.read")
    assert claims.lane in {"experimental", "candidate", "prod"}
    assert len(claims.token_hash) == 64


def test_verify_token_with_policy_for_service_token() -> None:
    """Service tokens gain service scopes and prod lane."""
    token = "st-lukhas-router-abcdef123456"
    claims = verify_token_with_policy(token)

    assert claims.token_type == "service"
    assert claims.owner == "router"
    assert claims.lane == "prod"
    assert claims.has_scope("api.service")
    assert claims.org_id.startswith("service:")


def test_require_bearer_missing_header_raises() -> None:
    """Missing authorization header yields HTTP 401 error."""
    with pytest.raises(HTTPException) as exc:
        require_bearer(None)

    assert exc.value.status_code == 401
    assert exc.value.detail["error"]["type"] == "invalid_api_key"


def test_require_bearer_enforces_scopes() -> None:
    """Required scopes are enforced as 403 responses."""
    token = "sk-lukhas-standard-1234567890abcdef"

    with pytest.raises(HTTPException) as exc:
        require_bearer(
            authorization=f"Bearer {token}",
            required_scopes=("admin.delete",),
        )

    assert exc.value.status_code == 403
    assert exc.value.detail["error"]["type"] == "insufficient_permissions"
