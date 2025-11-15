"""
Comprehensive unit tests for QRG (Quantum-Resistant Governance) Token Generator.

Tests cover:
- Token generation uniqueness
- Signature verification accuracy
- Scope permission checks
- Token rotation with scope preservation
- Token revocation
- Token expiration
- Performance requirements
- Error handling

LUKHAS AI - Consciousness-aware AI Development Platform
"""

import time
from typing import Any, Dict

import pytest

from governance.identity.core.qrs.qrg_generator import (
    QRGGenerator,
    QRGTokenError,
    QRGTokenExpiredError,
    QRGVerificationError,
)


class TestQRGGeneratorInitialization:
    """Test QRGGenerator initialization and configuration."""

    def test_init_with_default_config(self):
        """Test initialization with default configuration."""
        generator = QRGGenerator()
        assert generator.config == {}
        assert generator.security_level == 2
        assert generator.algorithm == "dilithium2"
        assert generator.enable_revocation is True

    def test_init_with_custom_config(self):
        """Test initialization with custom configuration."""
        config = {
            "security_level": 3,
            "algorithm": "dilithium3",
            "enable_revocation": False,
        }
        generator = QRGGenerator(config)
        assert generator.security_level == 3
        assert generator.algorithm == "dilithium3"
        assert generator.enable_revocation is False

    def test_init_creates_keypair(self):
        """Test that initialization creates cryptographic keys."""
        generator = QRGGenerator()
        # Check that keys are initialized (either PQC or fallback)
        assert hasattr(generator, '_public_key')
        assert hasattr(generator, '_private_key')


class TestTokenGeneration:
    """Test QRG token generation functionality."""

    @pytest.fixture
    def generator(self) -> QRGGenerator:
        """Create a QRGGenerator instance for testing."""
        return QRGGenerator()

    def test_generate_token_basic(self, generator):
        """Test basic token generation."""
        token = generator.generate_qrg_token("user123", ["read", "write"])
        assert token.startswith("QRG_")
        assert len(token) > 10

    def test_generate_token_format(self, generator):
        """Test that generated token has correct format."""
        token = generator.generate_qrg_token("user456", ["admin"])
        # Token should be QRG_ + base64url encoded data
        assert token.startswith("QRG_")
        encoded_part = token[4:]
        # Base64url characters: A-Z, a-z, 0-9, -, _
        assert all(c.isalnum() or c in ['-', '_', '='] for c in encoded_part)

    def test_generate_token_uniqueness(self, generator):
        """Test that each generated token is unique."""
        tokens = set()
        for i in range(10):
            token = generator.generate_qrg_token(f"user{i}", ["read"])
            tokens.add(token)
        assert len(tokens) == 10  # All tokens should be unique

    def test_generate_token_with_multiple_scopes(self, generator):
        """Test token generation with multiple scopes."""
        scopes = ["read", "write", "admin", "delete"]
        token = generator.generate_qrg_token("user789", scopes)
        assert token.startswith("QRG_")

        # Verify scopes are preserved
        claims = generator.decode_token(token)
        assert set(claims["scopes"]) == set(scopes)

    def test_generate_token_with_custom_ttl(self, generator):
        """Test token generation with custom TTL."""
        ttl = 7200  # 2 hours
        token = generator.generate_qrg_token("user999", ["read"], ttl_seconds=ttl)

        claims = generator.decode_token(token)
        expected_expiry = claims["issued_at"] + ttl
        assert abs(claims["expires_at"] - expected_expiry) < 2  # Allow 2s tolerance

    def test_generate_token_empty_user_id_raises_error(self, generator):
        """Test that empty user_id raises ValueError."""
        with pytest.raises(ValueError, match="user_id cannot be empty"):
            generator.generate_qrg_token("", ["read"])

    def test_generate_token_empty_scopes_raises_error(self, generator):
        """Test that empty scopes raises ValueError."""
        with pytest.raises(ValueError, match="scopes cannot be empty"):
            generator.generate_qrg_token("user123", [])

    def test_generate_token_scope_sorting(self, generator):
        """Test that scopes are sorted for consistency."""
        scopes1 = ["write", "read", "admin"]
        scopes2 = ["admin", "read", "write"]

        token1 = generator.generate_qrg_token("user1", scopes1)
        token2 = generator.generate_qrg_token("user1", scopes2)

        claims1 = generator.decode_token(token1)
        claims2 = generator.decode_token(token2)

        # Scopes should be sorted the same way
        assert claims1["scopes"] == claims2["scopes"]
        assert claims1["scopes"] == ["admin", "read", "write"]


class TestTokenVerification:
    """Test QRG token verification functionality."""

    @pytest.fixture
    def generator(self) -> QRGGenerator:
        """Create a QRGGenerator instance for testing."""
        return QRGGenerator()

    def test_verify_valid_token(self, generator):
        """Test verification of a valid token."""
        token = generator.generate_qrg_token("user123", ["read", "write"])
        assert generator.verify_token(token) is True

    def test_verify_token_with_required_scopes_present(self, generator):
        """Test verification when required scopes are present."""
        token = generator.generate_qrg_token("user123", ["read", "write", "admin"])
        assert generator.verify_token(token, ["read"]) is True
        assert generator.verify_token(token, ["read", "write"]) is True

    def test_verify_token_with_required_scopes_missing(self, generator):
        """Test verification fails when required scopes are missing."""
        token = generator.generate_qrg_token("user123", ["read"])

        with pytest.raises(QRGVerificationError, match="missing required scopes"):
            generator.verify_token(token, ["write"])

    def test_verify_invalid_token_format(self, generator):
        """Test verification fails for invalid token format."""
        with pytest.raises(QRGVerificationError, match="Invalid token format"):
            generator.verify_token("INVALID_TOKEN")

    def test_verify_token_without_prefix(self, generator):
        """Test verification fails for token without QRG_ prefix."""
        with pytest.raises(QRGVerificationError, match="missing QRG_ prefix"):
            generator.verify_token("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9")

    def test_verify_tampered_token(self, generator):
        """Test verification fails for tampered token."""
        token = generator.generate_qrg_token("user123", ["read"])
        # Tamper with token by changing a character
        tampered_token = token[:-5] + "XXXXX"

        with pytest.raises(QRGVerificationError):
            generator.verify_token(tampered_token)

    def test_verify_expired_token(self, generator):
        """Test verification fails for expired token."""
        # Generate token with 1 second TTL
        token = generator.generate_qrg_token("user123", ["read"], ttl_seconds=1)

        # Wait for token to expire
        time.sleep(2)

        with pytest.raises(QRGTokenExpiredError, match="Token has expired"):
            generator.verify_token(token)

    def test_verify_token_signature_accuracy(self, generator):
        """Test that signature verification is accurate."""
        # Generate token with one generator
        token = generator.generate_qrg_token("user123", ["read"])

        # Create a different generator (different keys)
        other_generator = QRGGenerator()

        # Verification should fail with different keys
        with pytest.raises(QRGVerificationError):
            other_generator.verify_token(token)


class TestTokenRevocation:
    """Test QRG token revocation functionality."""

    @pytest.fixture
    def generator(self) -> QRGGenerator:
        """Create a QRGGenerator instance for testing."""
        return QRGGenerator()

    def test_revoke_token_success(self, generator):
        """Test successful token revocation."""
        token = generator.generate_qrg_token("user123", ["read"])

        # Token should be valid before revocation
        assert generator.verify_token(token) is True

        # Revoke token
        result = generator.revoke_token(token)
        assert result is True

        # Token should be invalid after revocation
        with pytest.raises(QRGVerificationError, match="Token has been revoked"):
            generator.verify_token(token)

    def test_revoke_already_revoked_token(self, generator):
        """Test revoking an already revoked token."""
        token = generator.generate_qrg_token("user123", ["read"])

        # Revoke token first time
        result1 = generator.revoke_token(token)
        assert result1 is True

        # Revoke token second time
        result2 = generator.revoke_token(token)
        assert result2 is False  # Already revoked

    def test_revoke_token_with_revocation_disabled(self):
        """Test revocation fails when disabled."""
        generator = QRGGenerator({"enable_revocation": False})
        token = generator.generate_qrg_token("user123", ["read"])

        with pytest.raises(QRGTokenError, match="Token revocation is disabled"):
            generator.revoke_token(token)


class TestTokenRotation:
    """Test QRG token rotation functionality."""

    @pytest.fixture
    def generator(self) -> QRGGenerator:
        """Create a QRGGenerator instance for testing."""
        return QRGGenerator()

    def test_rotate_token_preserves_scopes(self, generator):
        """Test that token rotation preserves scopes."""
        original_scopes = ["read", "write", "admin"]
        old_token = generator.generate_qrg_token("user123", original_scopes)

        # Rotate token
        new_token = generator.rotate_token(old_token)

        # New token should be different
        assert new_token != old_token

        # New token should have same scopes
        new_claims = generator.decode_token(new_token)
        assert set(new_claims["scopes"]) == set(original_scopes)

    def test_rotate_token_preserves_user_id(self, generator):
        """Test that token rotation preserves user_id."""
        old_token = generator.generate_qrg_token("user456", ["read"])

        # Rotate token
        new_token = generator.rotate_token(old_token)

        # New token should have same user_id
        old_claims = generator.decode_token(old_token)
        new_claims = generator.decode_token(new_token)
        assert new_claims["user_id"] == old_claims["user_id"]

    def test_rotate_token_revokes_old_token(self, generator):
        """Test that token rotation revokes the old token."""
        old_token = generator.generate_qrg_token("user789", ["read"])

        # Rotate token
        new_token = generator.rotate_token(old_token)

        # Old token should be revoked
        with pytest.raises(QRGVerificationError, match="Token has been revoked"):
            generator.verify_token(old_token)

        # New token should be valid
        assert generator.verify_token(new_token) is True

    def test_rotate_invalid_token_raises_error(self, generator):
        """Test that rotating an invalid token raises error."""
        with pytest.raises(QRGVerificationError):
            generator.rotate_token("INVALID_TOKEN")

    def test_rotate_expired_token_raises_error(self, generator):
        """Test that rotating an expired token raises error."""
        # Generate token with 1 second TTL
        old_token = generator.generate_qrg_token("user123", ["read"], ttl_seconds=1)

        # Wait for token to expire
        time.sleep(2)

        # Rotation should fail
        with pytest.raises(QRGTokenExpiredError):
            generator.rotate_token(old_token)


class TestTokenDecoding:
    """Test QRG token decoding functionality."""

    @pytest.fixture
    def generator(self) -> QRGGenerator:
        """Create a QRGGenerator instance for testing."""
        return QRGGenerator()

    def test_decode_token_returns_claims(self, generator):
        """Test that decode_token returns correct claims."""
        user_id = "user123"
        scopes = ["read", "write"]
        token = generator.generate_qrg_token(user_id, scopes)

        claims = generator.decode_token(token)

        assert claims["user_id"] == user_id
        assert set(claims["scopes"]) == set(scopes)
        assert "token_id" in claims
        assert "issued_at" in claims
        assert "expires_at" in claims
        assert claims["version"] == "1.0"

    def test_decode_invalid_token_raises_error(self, generator):
        """Test that decoding invalid token raises error."""
        with pytest.raises(QRGVerificationError):
            generator.decode_token("INVALID_TOKEN")

    def test_decode_token_without_verification(self, generator):
        """Test that decode_token does not verify signature."""
        token = generator.generate_qrg_token("user123", ["read"])

        # Decode should work even with different generator
        other_generator = QRGGenerator()
        claims = other_generator.decode_token(token)

        # Should successfully decode (but wouldn't verify)
        assert claims["user_id"] == "user123"


class TestTokenInfo:
    """Test get_token_info functionality."""

    @pytest.fixture
    def generator(self) -> QRGGenerator:
        """Create a QRGGenerator instance for testing."""
        return QRGGenerator()

    def test_get_token_info_valid_token(self, generator):
        """Test get_token_info for valid token."""
        token = generator.generate_qrg_token("user123", ["read", "write"])
        info = generator.get_token_info(token)

        assert info["user_id"] == "user123"
        assert set(info["scopes"]) == {"read", "write"}
        assert info["is_valid"] is True
        assert info["is_expired"] is False
        assert info["is_revoked"] is False
        assert "issued_at" in info
        assert "expires_at" in info

    def test_get_token_info_expired_token(self, generator):
        """Test get_token_info for expired token."""
        token = generator.generate_qrg_token("user123", ["read"], ttl_seconds=1)
        time.sleep(2)

        info = generator.get_token_info(token)

        assert info["is_valid"] is False
        assert info["is_expired"] is True

    def test_get_token_info_revoked_token(self, generator):
        """Test get_token_info for revoked token."""
        token = generator.generate_qrg_token("user123", ["read"])
        generator.revoke_token(token)

        info = generator.get_token_info(token)

        assert info["is_valid"] is False
        assert info["is_revoked"] is True

    def test_get_token_info_invalid_token(self, generator):
        """Test get_token_info for invalid token."""
        info = generator.get_token_info("INVALID_TOKEN")

        assert info["is_valid"] is False
        assert "error" in info


class TestPerformance:
    """Test performance requirements for QRG token operations."""

    @pytest.fixture
    def generator(self) -> QRGGenerator:
        """Create a QRGGenerator instance for testing."""
        return QRGGenerator()

    def test_token_generation_performance(self, generator):
        """Test that token generation completes in <50ms."""
        start_time = time.time()
        token = generator.generate_qrg_token("user123", ["read", "write", "admin"])
        elapsed_time = (time.time() - start_time) * 1000  # Convert to ms

        assert elapsed_time < 50, f"Token generation took {elapsed_time:.2f}ms (limit: 50ms)"

    def test_token_verification_performance(self, generator):
        """Test that token verification completes in <10ms."""
        token = generator.generate_qrg_token("user123", ["read", "write"])

        start_time = time.time()
        generator.verify_token(token, ["read"])
        elapsed_time = (time.time() - start_time) * 1000  # Convert to ms

        assert elapsed_time < 10, f"Token verification took {elapsed_time:.2f}ms (limit: 10ms)"

    def test_bulk_token_generation_performance(self, generator):
        """Test performance of generating multiple tokens."""
        num_tokens = 100
        start_time = time.time()

        for i in range(num_tokens):
            generator.generate_qrg_token(f"user{i}", ["read"])

        elapsed_time = time.time() - start_time
        avg_time_ms = (elapsed_time / num_tokens) * 1000

        assert avg_time_ms < 50, f"Average generation time: {avg_time_ms:.2f}ms (limit: 50ms)"


class TestEdgeCases:
    """Test edge cases and error handling."""

    @pytest.fixture
    def generator(self) -> QRGGenerator:
        """Create a QRGGenerator instance for testing."""
        return QRGGenerator()

    def test_token_with_special_characters_in_user_id(self, generator):
        """Test token generation with special characters in user_id."""
        user_id = "user@example.com"
        token = generator.generate_qrg_token(user_id, ["read"])

        claims = generator.decode_token(token)
        assert claims["user_id"] == user_id

    def test_token_with_unicode_in_user_id(self, generator):
        """Test token generation with unicode characters."""
        user_id = "用户123"
        token = generator.generate_qrg_token(user_id, ["read"])

        claims = generator.decode_token(token)
        assert claims["user_id"] == user_id

    def test_token_with_very_long_scope_list(self, generator):
        """Test token generation with many scopes."""
        scopes = [f"scope_{i}" for i in range(100)]
        token = generator.generate_qrg_token("user123", scopes)

        claims = generator.decode_token(token)
        assert len(claims["scopes"]) == 100

    def test_token_with_zero_ttl(self, generator):
        """Test token with zero TTL (immediately expired)."""
        token = generator.generate_qrg_token("user123", ["read"], ttl_seconds=0)

        # Wait a moment to ensure token is expired
        time.sleep(0.1)

        # Token should be expired
        with pytest.raises(QRGTokenExpiredError):
            generator.verify_token(token)

    def test_concurrent_token_generation(self, generator):
        """Test that concurrent token generation produces unique tokens."""
        import concurrent.futures

        def generate_token(i):
            return generator.generate_qrg_token(f"user{i}", ["read"])

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            tokens = list(executor.map(generate_token, range(100)))

        # All tokens should be unique
        assert len(set(tokens)) == 100


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=governance.identity.core.qrs", "--cov-report=term-missing"])
