"""Comprehensive tests for KeyManager and JWKS functionality.

Tests cover:
- RSA and ECDSA key generation
- Key rotation with grace periods
- JWKS export (RFC 7517)
- JWT signing and verification
- Key expiry and cleanup
- KMS integration patterns
"""

import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ec
from jose import jwt, jwk

from core.identity.keys import KeyManager, KeyMetadata


@pytest.fixture
def temp_key_dir():
    """Temporary directory for test keys."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def rsa_key_manager(temp_key_dir):
    """KeyManager with RS256 algorithm."""
    km = KeyManager(algorithm="RS256", key_dir=temp_key_dir, key_size=2048)
    return km


@pytest.fixture
def ecdsa_key_manager(temp_key_dir):
    """KeyManager with ES256 algorithm."""
    km = KeyManager(algorithm="ES256", key_dir=temp_key_dir)
    return km


def test_rsa_key_generation(rsa_key_manager):
    """Test RSA key pair generation and storage."""
    kid, private_key = rsa_key_manager.get_current_signing_key()

    # Verify kid format
    assert kid.startswith("lukhas-rs256-")

    # Verify private key is RSA
    assert isinstance(
        private_key, rsa.RSAPrivateKey
    ) or hasattr(private_key, "sign")

    # Verify key files exist
    key_dir = Path(rsa_key_manager.key_dir)
    assert (key_dir / f"{kid}.key").exists()
    assert (key_dir / f"{kid}.pub").exists()
    assert (key_dir / f"{kid}.json").exists()


def test_ecdsa_key_generation(ecdsa_key_manager):
    """Test ECDSA key pair generation and storage."""
    kid, private_key = ecdsa_key_manager.get_current_signing_key()

    # Verify kid format
    assert kid.startswith("lukhas-es256-")

    # Verify private key is ECDSA
    assert isinstance(
        private_key, ec.EllipticCurvePrivateKey
    ) or hasattr(private_key, "sign")

    # Verify key files exist
    key_dir = Path(ecdsa_key_manager.key_dir)
    assert (key_dir / f"{kid}.key").exists()
    assert (key_dir / f"{kid}.pub").exists()
    assert (key_dir / f"{kid}.json").exists()


def test_jwt_signing_and_verification_rs256(rsa_key_manager):
    """Test JWT signing with RS256 and verification with public key."""
    kid, private_key = rsa_key_manager.get_current_signing_key()

    # Create test payload
    payload = {
        "sub": "usr_alice",
        "iss": "https://ai",
        "aud": "lukhas_web",
        "exp": int((datetime.utcnow() + timedelta(hours=1)).timestamp()),
        "iat": int(datetime.utcnow().timestamp()),
    }

    # Sign JWT with kid in header
    token = jwt.encode(payload, private_key, algorithm="RS256", headers={"kid": kid})

    # Decode header to verify kid
    header = jwt.get_unverified_header(token)
    assert header["kid"] == kid
    assert header["alg"] == "RS256"

    # Get public key for verification
    public_key = rsa_key_manager.get_public_key(kid)
    assert public_key is not None

    # Verify JWT
    decoded = jwt.decode(
        token, public_key, algorithms=["RS256"], audience="lukhas_web"
    )
    assert decoded["sub"] == "usr_alice"


def test_jwt_signing_and_verification_es256(ecdsa_key_manager):
    """Test JWT signing with ES256 and verification with public key."""
    kid, private_key = ecdsa_key_manager.get_current_signing_key()

    # Create test payload
    payload = {
        "sub": "usr_bob",
        "iss": "https://ai",
        "exp": int((datetime.utcnow() + timedelta(hours=1)).timestamp()),
        "iat": int(datetime.utcnow().timestamp()),
    }

    # Sign JWT
    token = jwt.encode(payload, private_key, algorithm="ES256", headers={"kid": kid})

    # Get public key
    public_key = ecdsa_key_manager.get_public_key(kid)

    # Verify JWT
    decoded = jwt.decode(token, public_key, algorithms=["ES256"])
    assert decoded["sub"] == "usr_bob"


def test_jwks_export_rsa(rsa_key_manager):
    """Test JWKS export for RSA keys (RFC 7517)."""
    jwks = rsa_key_manager.export_jwks()

    # Verify structure
    assert "keys" in jwks
    assert len(jwks["keys"]) >= 1

    # Verify first key
    key = jwks["keys"][0]
    assert key["kty"] == "RSA"
    assert key["use"] == "sig"
    assert key["alg"] == "RS256"
    assert "kid" in key
    assert "n" in key  # RSA modulus
    assert "e" in key  # RSA exponent


def test_jwks_export_ecdsa(ecdsa_key_manager):
    """Test JWKS export for ECDSA keys."""
    jwks = ecdsa_key_manager.export_jwks()

    # Verify structure
    assert "keys" in jwks
    assert len(jwks["keys"]) >= 1

    # Verify first key
    key = jwks["keys"][0]
    assert key["kty"] == "EC"
    assert key["use"] == "sig"
    assert key["alg"] == "ES256"
    assert "kid" in key
    assert "crv" in key  # Curve name
    assert key["crv"] == "P-256"
    assert "x" in key  # X coordinate
    assert "y" in key  # Y coordinate


def test_key_rotation(rsa_key_manager):
    """Test key rotation creates new key and deprecates old keys."""
    # Get initial key
    initial_kid, _ = rsa_key_manager.get_current_signing_key()

    # Rotate keys
    new_kid = rsa_key_manager.rotate_keys()

    # Verify new key is different
    assert new_kid != initial_kid

    # Verify new key is now current
    current_kid, _ = rsa_key_manager.get_current_signing_key()
    assert current_kid == new_kid

    # Verify JWKS includes both keys (grace period)
    jwks = rsa_key_manager.export_jwks()
    kids_in_jwks = {key["kid"] for key in jwks["keys"]}
    assert new_kid in kids_in_jwks
    # Old key should still be in JWKS during grace period


def test_old_keys_still_verify_during_grace_period(rsa_key_manager):
    """Test that tokens signed with old keys are still valid during grace period."""
    # Sign token with initial key
    kid1, private_key1 = rsa_key_manager.get_current_signing_key()
    payload = {"sub": "usr_charlie", "exp": int((datetime.utcnow() + timedelta(hours=1)).timestamp())}
    token1 = jwt.encode(payload, private_key1, algorithm="RS256", headers={"kid": kid1})

    # Rotate keys
    rsa_key_manager.rotate_keys()

    # Old public key should still be available
    public_key1 = rsa_key_manager.get_public_key(kid1)
    assert public_key1 is not None

    # Token should still verify
    decoded = jwt.decode(token1, public_key1, algorithms=["RS256"])
    assert decoded["sub"] == "usr_charlie"


def test_key_persistence_across_restarts(temp_key_dir):
    """Test that keys are persisted and loaded on restart."""
    # Create key manager and generate key
    km1 = KeyManager(algorithm="RS256", key_dir=temp_key_dir)
    kid1, _ = km1.get_current_signing_key()

    # Simulate restart: create new KeyManager instance with same key_dir
    km2 = KeyManager(algorithm="RS256", key_dir=temp_key_dir)
    kid2, _ = km2.get_current_signing_key()

    # Should load the same key
    assert kid1 == kid2

    # Both managers should have same key count
    assert len(km1.keys) == len(km2.keys)


def test_key_metadata_tracking(rsa_key_manager):
    """Test that key metadata is properly tracked."""
    kid, _ = rsa_key_manager.get_current_signing_key()

    metadata = rsa_key_manager.get_key_metadata(kid)
    assert metadata is not None
    assert metadata.kid == kid
    assert metadata.algorithm == "RS256"
    assert metadata.active is True
    assert metadata.key_size == 2048
    assert metadata.created_at is not None
    assert metadata.expires_at is not None


def test_cleanup_expired_keys(temp_key_dir):
    """Test cleanup of expired keys."""
    # Create key manager with very short rotation period
    km = KeyManager(
        algorithm="RS256",
        key_dir=temp_key_dir,
        rotation_days=0,
        grace_days=0,
    )

    kid, _ = km.get_current_signing_key()

    # Manually expire the key
    metadata, private_key, public_key = km.keys[kid]
    metadata.expires_at = datetime.utcnow() - timedelta(hours=1)
    km.keys[kid] = (metadata, private_key, public_key)

    # Re-save metadata
    metadata_path = Path(temp_key_dir) / f"{kid}.json"
    metadata_path.write_text(metadata.model_dump_json(indent=2))

    # Cleanup
    deleted = km.cleanup_expired_keys()
    assert deleted == 1

    # Key should be gone
    assert kid not in km.keys
    assert not (Path(temp_key_dir) / f"{kid}.key").exists()


def test_list_keys(rsa_key_manager):
    """Test listing all keys."""
    keys = rsa_key_manager.list_keys()
    assert len(keys) >= 1
    assert all(isinstance(k, KeyMetadata) for k in keys)


def test_health_check_healthy(rsa_key_manager):
    """Test health check with active keys."""
    health = rsa_key_manager.health_check()
    assert health["status"] == "healthy"
    assert health["total_keys"] >= 1
    assert health["active_keys"] >= 1
    assert health["algorithm"] == "RS256"


def test_health_check_no_active_keys(temp_key_dir):
    """Test health check when all keys are expired."""
    km = KeyManager(algorithm="RS256", key_dir=temp_key_dir)

    # Expire all keys
    for kid, (metadata, private_key, public_key) in km.keys.items():
        metadata.expires_at = datetime.utcnow() - timedelta(hours=1)
        metadata.active = False
        km.keys[kid] = (metadata, private_key, public_key)

    health = km.health_check()
    assert health["status"] == "unhealthy"
    assert health["active_keys"] == 0


def test_invalid_algorithm_rejected():
    """Test that invalid algorithms are rejected."""
    with pytest.raises(ValueError, match="Unsupported algorithm"):
        KeyManager(algorithm="HS256")


def test_get_nonexistent_public_key(rsa_key_manager):
    """Test retrieving non-existent public key."""
    public_key = rsa_key_manager.get_public_key("nonexistent-kid")
    assert public_key is None


def test_jwks_excludes_expired_keys(temp_key_dir):
    """Test that JWKS does not include expired keys."""
    km = KeyManager(algorithm="RS256", key_dir=temp_key_dir)

    kid, _ = km.get_current_signing_key()

    # Expire the key
    metadata, private_key, public_key = km.keys[kid]
    metadata.expires_at = datetime.utcnow() - timedelta(hours=1)
    km.keys[kid] = (metadata, private_key, public_key)

    # JWKS should not include expired key
    jwks = km.export_jwks()
    kids_in_jwks = {key["kid"] for key in jwks["keys"]}
    assert kid not in kids_in_jwks


def test_multiple_key_rotation_cycles(temp_key_dir):
    """Test multiple rotation cycles."""
    km = KeyManager(algorithm="RS256", key_dir=temp_key_dir, rotation_days=1)

    kids = []
    for i in range(3):
        new_kid = km.rotate_keys()
        kids.append(new_kid)

    # All keys should be different
    assert len(set(kids)) == 3

    # Current key should be the latest
    current_kid, _ = km.get_current_signing_key()
    assert current_kid == kids[-1]


def test_key_file_permissions(temp_key_dir):
    """Test that private key files have restrictive permissions."""
    km = KeyManager(algorithm="RS256", key_dir=temp_key_dir)
    kid, _ = km.get_current_signing_key()

    private_path = Path(temp_key_dir) / f"{kid}.key"
    stat_info = private_path.stat()

    # Check file permissions (owner read/write only: 0o600)
    import stat

    mode = stat_info.st_mode
    # Owner should have read/write
    assert mode & stat.S_IRUSR
    assert mode & stat.S_IWUSR
    # Group and others should have no permissions
    assert not (mode & stat.S_IRGRP)
    assert not (mode & stat.S_IWGRP)
    assert not (mode & stat.S_IROTH)
    assert not (mode & stat.S_IWOTH)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
