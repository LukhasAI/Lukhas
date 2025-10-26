"""High priority tests for JWTAdapter metadata enhancements."""

import pytest

from labs.bridge.adapters.api_framework import JWTAdapter, TokenType


@pytest.fixture
def jwt_adapter() -> JWTAdapter:
    return JWTAdapter(secret_key="super-secret")


def test_jwt_adapter_validates_scopes_and_metadata(jwt_adapter: JWTAdapter):
    token = jwt_adapter.create_token(
        subject="user-1",
        token_type=TokenType.ACCESS,
        scopes=["guardian.read"],
        lambda_id="lambda-1",
    )

    result = jwt_adapter.verify_token(
        token,
        expected_type=TokenType.ACCESS,
        required_scopes=["guardian.read"],
    )

    assert result.valid
    assert result.validation_metadata["scopes_checked"] == ["guardian.read"]
    assert result.validation_metadata["lambda_id_verified"] is True


def test_jwt_adapter_reports_missing_scopes(jwt_adapter: JWTAdapter):
    token = jwt_adapter.create_token(
        subject="user-2",
        token_type=TokenType.ACCESS,
        scopes=["guardian.read"],
    )

    result = jwt_adapter.verify_token(
        token,
        expected_type=TokenType.ACCESS,
        required_scopes=["guardian.write"],
    )

    assert not result.valid
    assert result.error_code == "INSUFFICIENT_SCOPES"
    assert result.validation_metadata["missing_scopes"] == ["guardian.write"]


def test_jwt_adapter_revocation_blocks_future_use(jwt_adapter: JWTAdapter):
    refresh_token = jwt_adapter.create_token(
        subject="user-3",
        token_type=TokenType.REFRESH,
        scopes=["guardian.read"],
    )

    assert jwt_adapter.revoke_token(refresh_token)

    result = jwt_adapter.verify_token(refresh_token, expected_type=TokenType.REFRESH)

    assert not result.valid
    assert result.error_code == "TOKEN_REVOKED"


def test_jwt_adapter_refreshes_access_token(jwt_adapter: JWTAdapter):
    refresh_token = jwt_adapter.create_token(
        subject="user-4",
        token_type=TokenType.REFRESH,
        scopes=["guardian.read"],
    )

    new_access = jwt_adapter.refresh_token(refresh_token, new_scopes=["guardian.read", "guardian.write"])

    assert new_access is not None
    verification = jwt_adapter.verify_token(
        new_access,
        expected_type=TokenType.ACCESS,
        required_scopes=["guardian.write"],
    )

    assert verification.valid
    assert set(verification.claims.scopes) == {"guardian.read", "guardian.write"}
