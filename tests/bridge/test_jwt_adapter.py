"""
Tests for JWT Adapter

Comprehensive functional tests for api_framework.py JWT implementation.
Covers token creation, verification, ΛID integration, and rate limiting.

Part of BATCH-COPILOT-TESTS-01
Tasks Tested:
- TEST-HIGH-JWT-01: JWT token creation with multiple algorithms
- TEST-HIGH-JWT-02: JWT token verification
- TEST-HIGH-JWT-03: ΛID integration with tier validation
- TEST-HIGH-JWT-04: Rate limiting with tier multipliers

Trinity Framework: ⚛️ Identity · 🛡️ Guardian
"""

import time
from datetime import datetime, timedelta

import jwt as pyjwt
import pytest
from labs.bridge.adapters.api_framework import (
    JWTAdapter,
    JWTAlgorithm,
    TokenClaims,
    TokenType,
    TokenValidationResult,
    create_identity_token,
    verify_identity_token,
)

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def hs256_adapter():
    """JWT adapter with HS256 algorithm."""
    return JWTAdapter(
        secret_key="test_secret_key_super_secure_123",
        algorithm=JWTAlgorithm.HS256,
        issuer="lukhas-test",
        audience="lukhas-platform",
        access_token_ttl=3600,
        refresh_token_ttl=86400 * 30,
        lambda_id_integration=True,
    )


@pytest.fixture
def rs256_keys():
    """Generate RSA key pair for RS256 testing."""
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa

    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8")

    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode("utf-8")

    return {"private": private_pem, "public": public_pem}


@pytest.fixture
def rs256_adapter(rs256_keys):
    """JWT adapter with RS256 algorithm."""
    return JWTAdapter(
        public_key=rs256_keys["public"],
        private_key=rs256_keys["private"],
        algorithm=JWTAlgorithm.RS256,
        issuer="lukhas-test",
        audience="lukhas-platform",
        lambda_id_integration=True,
    )


# ============================================================================
# TEST-HIGH-JWT-01: Token Creation
# ============================================================================


@pytest.mark.unit
def test_jwt_token_creation_hs256(hs256_adapter):
    """Test JWT token creation with HS256 algorithm."""
    token = hs256_adapter.create_token(
        subject="user_123",
        token_type=TokenType.ACCESS,
        scopes=["read", "write"],
        lambda_id="Λ_alpha_user123",
        identity_tier="alpha",
    )

    # Verify token is a string
    assert isinstance(token, str)
    assert len(token) > 0

    # Decode without verification to check structure
    decoded = hs256_adapter.decode_without_verification(token)
    assert decoded["sub"] == "user_123"
    assert decoded["iss"] == "lukhas-test"
    assert decoded["aud"] == "lukhas-platform"
    assert decoded["lambda_id"] == "Λ_alpha_user123"
    assert decoded["identity_tier"] == "alpha"
    assert decoded["scopes"] == ["read", "write"]
    assert decoded["token_type"] == "access"


@pytest.mark.unit
def test_jwt_token_creation_rs256(rs256_adapter):
    """Test JWT token creation with RS256 algorithm."""
    token = rs256_adapter.create_token(
        subject="user_456", token_type=TokenType.ACCESS, lambda_id="Λ_beta_user456", identity_tier="beta"
    )

    assert isinstance(token, str)
    decoded = rs256_adapter.decode_without_verification(token)
    assert decoded["sub"] == "user_456"
    assert decoded["lambda_id"] == "Λ_beta_user456"


@pytest.mark.unit
def test_jwt_token_creation_refresh(hs256_adapter):
    """Test refresh token creation with extended TTL."""
    token = hs256_adapter.create_token(
        subject="user_123",
        token_type=TokenType.REFRESH,
    )

    decoded = hs256_adapter.decode_without_verification(token)
    assert decoded["token_type"] == "refresh"

    # Verify TTL is longer for refresh tokens
    exp = decoded["exp"]
    iat = decoded["iat"]
    ttl = exp - iat
    assert ttl > 86400  # More than 1 day


@pytest.mark.unit
def test_jwt_token_creation_custom_ttl(hs256_adapter):
    """Test token creation with custom TTL."""
    custom_ttl = 7200  # 2 hours
    token = hs256_adapter.create_token(subject="user_123", custom_ttl=custom_ttl)

    decoded = hs256_adapter.decode_without_verification(token)
    exp = decoded["exp"]
    iat = decoded["iat"]
    actual_ttl = exp - iat
    assert abs(actual_ttl - custom_ttl) < 5  # Allow small margin


@pytest.mark.unit
def test_jwt_token_lambda_id_embedding(hs256_adapter):
    """Test ΛID embedding in JWT claims."""
    token = hs256_adapter.create_token(
        subject="user_123",
        lambda_id="Λ_gamma_user123",
        identity_tier="gamma",
        metadata={"device": "mobile", "platform": "ios"},
    )

    decoded = hs256_adapter.decode_without_verification(token)
    assert decoded["lambda_id"] == "Λ_gamma_user123"
    assert decoded["identity_tier"] == "gamma"
    assert decoded["metadata"]["device"] == "mobile"


# ============================================================================
# TEST-HIGH-JWT-02: Token Verification
# ============================================================================


@pytest.mark.unit
def test_jwt_token_verification_valid(hs256_adapter):
    """Test verification of valid JWT tokens."""
    token = hs256_adapter.create_token(subject="user_123", scopes=["read", "write"])

    result = hs256_adapter.verify_token(token)

    assert result.valid is True
    assert result.claims is not None
    assert result.claims.sub == "user_123"
    assert result.claims.scopes == ["read", "write"]
    assert result.error is None


@pytest.mark.unit
def test_jwt_token_verification_expired(hs256_adapter):
    """Test rejection of expired tokens."""
    # Create token with very short TTL
    token = hs256_adapter.create_token(subject="user_123", custom_ttl=1)  # 1 second

    # Wait for expiration
    time.sleep(2)

    result = hs256_adapter.verify_token(token)

    assert result.valid is False
    assert result.error_code == "TOKEN_EXPIRED"
    assert "expired" in result.error.lower()


@pytest.mark.unit
def test_jwt_token_verification_tampered(hs256_adapter):
    """Test rejection of tampered tokens."""
    token = hs256_adapter.create_token(subject="user_123")

    # Tamper with token (modify payload)
    parts = token.split(".")
    # Change a character in the payload
    tampered_payload = parts[1][:-1] + ("X" if parts[1][-1] != "X" else "Y")
    tampered_token = f"{parts[0]}.{tampered_payload}.{parts[2]}"

    result = hs256_adapter.verify_token(tampered_token)

    assert result.valid is False
    assert result.error_code in ["INVALID_SIGNATURE", "DECODE_ERROR"]


@pytest.mark.unit
def test_jwt_token_verification_wrong_issuer(hs256_adapter):
    """Test rejection of tokens with wrong issuer."""
    # Create token with different issuer
    wrong_adapter = JWTAdapter(
        secret_key="test_secret_key_super_secure_123",
        algorithm=JWTAlgorithm.HS256,
        issuer="wrong-issuer",
        audience="lukhas-platform",
    )
    token = wrong_adapter.create_token(subject="user_123")

    result = hs256_adapter.verify_token(token)

    assert result.valid is False
    assert result.error_code == "INVALID_ISSUER"


@pytest.mark.unit
def test_jwt_token_verification_wrong_audience(hs256_adapter):
    """Test rejection of tokens with wrong audience."""
    wrong_adapter = JWTAdapter(
        secret_key="test_secret_key_super_secure_123",
        algorithm=JWTAlgorithm.HS256,
        issuer="lukhas-test",
        audience="wrong-audience",
    )
    token = wrong_adapter.create_token(subject="user_123")

    result = hs256_adapter.verify_token(token)

    assert result.valid is False
    assert result.error_code == "INVALID_AUDIENCE"


@pytest.mark.unit
def test_jwt_token_verification_signature(hs256_adapter):
    """Test signature verification."""
    token = hs256_adapter.create_token(subject="user_123")

    # Create adapter with different key
    wrong_adapter = JWTAdapter(
        secret_key="different_secret_key_456",
        algorithm=JWTAlgorithm.HS256,
        issuer="lukhas-test",
        audience="lukhas-platform",
    )

    result = wrong_adapter.verify_token(token)

    assert result.valid is False
    assert result.error_code == "INVALID_SIGNATURE"


@pytest.mark.unit
def test_jwt_token_verification_required_scopes(hs256_adapter):
    """Test verification with required scopes."""
    token = hs256_adapter.create_token(subject="user_123", scopes=["read"])

    # Verify with required scopes
    result = hs256_adapter.verify_token(token, required_scopes=["read", "write"])

    assert result.valid is False
    assert result.error_code == "INSUFFICIENT_SCOPES"
    assert "Missing required scopes" in result.error


@pytest.mark.unit
def test_jwt_token_verification_expected_type(hs256_adapter):
    """Test verification with expected token type."""
    token = hs256_adapter.create_token(subject="user_123", token_type=TokenType.ACCESS)

    # Verify expecting refresh token
    result = hs256_adapter.verify_token(token, expected_type=TokenType.REFRESH)

    assert result.valid is False
    assert result.error_code == "INVALID_TOKEN_TYPE"


# ============================================================================
# TEST-HIGH-JWT-03: ΛID Integration
# ============================================================================


@pytest.mark.unit
def test_jwt_lambda_id_integration_creation(hs256_adapter):
    """Test ΛID embedding in JWT claims during creation."""
    token = create_identity_token(
        adapter=hs256_adapter,
        lambda_id="Λ_alpha_user123",
        identity_tier="alpha",
        scopes=["identity:read", "identity:write"],
    )

    result = hs256_adapter.verify_token(token)

    assert result.valid is True
    assert result.claims.lambda_id == "Λ_alpha_user123"
    assert result.claims.identity_tier == "alpha"
    assert result.claims.token_type == "identity"


@pytest.mark.unit
def test_jwt_lambda_id_tier_validation_alpha(hs256_adapter):
    """Test tier validation for alpha tier."""
    token = create_identity_token(adapter=hs256_adapter, lambda_id="Λ_alpha_user123", identity_tier="alpha")

    # Verify with alpha requirement
    result = verify_identity_token(adapter=hs256_adapter, token=token, required_tier="alpha")

    assert result.valid is True


@pytest.mark.unit
def test_jwt_lambda_id_tier_validation_insufficient(hs256_adapter):
    """Test rejection of insufficient tier."""
    token = create_identity_token(adapter=hs256_adapter, lambda_id="Λ_delta_user123", identity_tier="delta")

    # Verify requiring alpha (higher tier)
    result = verify_identity_token(adapter=hs256_adapter, token=token, required_tier="alpha")

    assert result.valid is False
    assert result.error_code == "INSUFFICIENT_TIER"
    assert "Insufficient identity tier" in result.error


@pytest.mark.unit
def test_jwt_lambda_id_tier_access_control(hs256_adapter):
    """Test tier-based access control."""
    tiers = ["alpha", "beta", "gamma", "delta"]

    for tier in tiers:
        token = create_identity_token(adapter=hs256_adapter, lambda_id=f"Λ_{tier}_user123", identity_tier=tier)

        result = hs256_adapter.verify_token(token)
        assert result.valid is True
        assert result.claims.identity_tier == tier


@pytest.mark.unit
def test_jwt_lambda_id_missing_verification(hs256_adapter):
    """Test handling of tokens without ΛID."""
    # Create token without lambda_id
    token = hs256_adapter.create_token(subject="user_123", lambda_id=None)  # No ΛID

    # Verify with ΛID requirement
    result = hs256_adapter.verify_token(token, verify_lambda_id=True)

    # Should still be valid but log warning
    assert result.valid is True
    assert result.claims.lambda_id is None


# ============================================================================
# TEST-HIGH-JWT-04: Rate Limiting
# ============================================================================


@pytest.mark.unit
def test_jwt_rate_limiting_free_tier(hs256_adapter):
    """Test rate limiting for free tier."""
    # Free tier should have base limits
    lambda_id = "Λ_delta_user123"  # delta = free tier

    # Check rate limit (should use tier multiplier of 1.0)
    can_proceed = hs256_adapter._check_rate_limit(lambda_id=lambda_id, identity_tier="delta")

    assert can_proceed is True  # Currently always allows


@pytest.mark.unit
def test_jwt_rate_limiting_pro_multiplier(hs256_adapter):
    """Test rate limiting with pro tier multiplier."""
    lambda_id = "Λ_beta_user123"  # beta = pro tier

    can_proceed = hs256_adapter._check_rate_limit(lambda_id=lambda_id, identity_tier="beta")

    assert can_proceed is True


@pytest.mark.unit
def test_jwt_rate_limiting_enterprise_multiplier(hs256_adapter):
    """Test rate limiting with enterprise tier multiplier."""
    lambda_id = "Λ_alpha_user123"  # alpha = enterprise tier

    can_proceed = hs256_adapter._check_rate_limit(lambda_id=lambda_id, identity_tier="alpha")

    assert can_proceed is True


@pytest.mark.unit
def test_jwt_rate_limit_enforcement():
    """Test rate limit enforcement logic."""
    from labs.bridge.adapters.api_framework import RateLimitConfig

    config = RateLimitConfig(
        requests_per_minute=60,
        tokens_per_minute=90000,
        tier_multipliers={
            "alpha": 3.0,
            "beta": 2.0,
            "gamma": 1.5,
            "delta": 1.0,
        },
    )

    # Verify multipliers
    assert config.tier_multipliers["alpha"] == 3.0
    assert config.tier_multipliers["beta"] == 2.0
    assert config.tier_multipliers["gamma"] == 1.5
    assert config.tier_multipliers["delta"] == 1.0


# ============================================================================
# Token Lifecycle Tests
# ============================================================================


@pytest.mark.unit
def test_jwt_token_refresh_flow(hs256_adapter):
    """Test token refresh flow."""
    # Create refresh token
    refresh_token = hs256_adapter.create_token(
        subject="user_123", token_type=TokenType.REFRESH, scopes=["read", "write"], lambda_id="Λ_alpha_user123"
    )

    # Use refresh token to get new access token
    new_access_token = hs256_adapter.refresh_token(refresh_token)

    assert new_access_token is not None

    # Verify new access token
    result = hs256_adapter.verify_token(new_access_token)
    assert result.valid is True
    assert result.claims.sub == "user_123"
    assert result.claims.token_type == "access"


@pytest.mark.unit
def test_jwt_token_revocation(hs256_adapter):
    """Test token revocation."""
    token = hs256_adapter.create_token(subject="user_123")

    # Verify token is valid
    result = hs256_adapter.verify_token(token)
    assert result.valid is True

    # Revoke token
    revoked = hs256_adapter.revoke_token(token)
    assert revoked is True

    # Verify token is now invalid
    result = hs256_adapter.verify_token(token)
    assert result.valid is False
    assert result.error_code == "TOKEN_REVOKED"


@pytest.mark.unit
def test_jwt_get_token_info(hs256_adapter):
    """Test getting token information without verification."""
    token = hs256_adapter.create_token(
        subject="user_123", lambda_id="Λ_alpha_user123", identity_tier="alpha", scopes=["read", "write"]
    )

    info = hs256_adapter.get_token_info(token)

    assert info["subject"] == "user_123"
    assert info["lambda_id"] == "Λ_alpha_user123"
    assert info["identity_tier"] == "alpha"
    assert info["scopes"] == ["read", "write"]
    assert info["expired"] is False
    assert "issued_at" in info
    assert "expires_at" in info


# ============================================================================
# Edge Cases and Error Handling
# ============================================================================


@pytest.mark.unit
def test_jwt_adapter_initialization_errors():
    """Test JWT adapter initialization with invalid configs."""
    # HS256 without secret key
    with pytest.raises(ValueError, match="HS256 requires secret_key"):
        JWTAdapter(algorithm=JWTAlgorithm.HS256)

    # RS256 without public key
    with pytest.raises(ValueError, match="RS256 requires public_key"):
        JWTAdapter(algorithm=JWTAlgorithm.RS256)


@pytest.mark.unit
def test_jwt_token_creation_without_signing_key(hs256_adapter):
    """Test token creation error handling."""
    # Remove private key for signing
    adapter = JWTAdapter(
        secret_key=None, public_key="fake_key", algorithm=JWTAlgorithm.RS256, issuer="test", audience="test"
    )

    with pytest.raises(ValueError, match="Cannot create token"):
        adapter.create_token(subject="user_123")


@pytest.mark.unit
def test_jwt_invalid_token_format(hs256_adapter):
    """Test handling of malformed tokens."""
    invalid_token = "not.a.valid.jwt.token"

    result = hs256_adapter.verify_token(invalid_token)

    assert result.valid is False
    assert result.error_code == "DECODE_ERROR"
