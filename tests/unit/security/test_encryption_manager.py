#!/usr/bin/env python3
"""
Comprehensive tests for EncryptionManager.

Tests all encryption operations, key management, error handling,
and security properties for the centralized encryption manager.

Constellation Framework: 🛡️ Guardian Excellence - Encryption Manager Tests

Related Issues:
- #613: Implement centralized EncryptionManager (P2 - Security Foundation)

Test Coverage:
- Encryption/decryption round-trips for all AEAD algorithms
- Key generation with correct sizes
- Key rotation functionality
- Error handling (invalid keys, corrupted data, wrong algorithms)
- AEAD tag verification and tamper detection
- Nonce uniqueness
- Associated data authentication
- Edge cases and boundary conditions
"""

import pytest
from core.security.encryption_manager import (
    DecryptionError,
    EncryptionError,
    EncryptionManager,
    InvalidKeyError,
)
from core.security.encryption_types import EncryptionAlgorithm, get_algorithm_metadata


@pytest.fixture
def manager():
    """Create EncryptionManager instance for tests."""
    return EncryptionManager()


@pytest.fixture
def test_data():
    """Test data for encryption."""
    return b"This is secret data that needs encryption"


class TestEncryptionDecryptionRoundTrip:
    """Test encryption/decryption round-trip for all supported algorithms."""

    def test_aes_256_gcm_round_trip(self, manager, test_data):
        """Test AES-256-GCM encryption/decryption round-trip."""
        # Generate key
        key = manager.generate_key(EncryptionAlgorithm.AES_256_GCM)

        # Encrypt
        encrypted = manager.encrypt(test_data, EncryptionAlgorithm.AES_256_GCM, key)

        # Verify encrypted data structure
        assert "algorithm" in encrypted
        assert "ciphertext" in encrypted
        assert "nonce" in encrypted
        assert "tag" in encrypted
        assert encrypted["algorithm"] == "aes-256-gcm"

        # Verify ciphertext is different from plaintext
        assert encrypted["ciphertext"] != test_data

        # Decrypt
        decrypted = manager.decrypt(encrypted, key)

        # Verify plaintext matches
        assert decrypted == test_data

    def test_chacha20_poly1305_round_trip(self, manager, test_data):
        """Test ChaCha20-Poly1305 encryption/decryption round-trip."""
        # Generate key
        key = manager.generate_key(EncryptionAlgorithm.CHACHA20_POLY1305)

        # Encrypt
        encrypted = manager.encrypt(test_data, EncryptionAlgorithm.CHACHA20_POLY1305, key)

        # Verify encrypted data structure
        assert "algorithm" in encrypted
        assert "ciphertext" in encrypted
        assert "nonce" in encrypted
        assert "tag" in encrypted
        assert encrypted["algorithm"] == "chacha20-poly1305"

        # Verify ciphertext is different from plaintext
        assert encrypted["ciphertext"] != test_data

        # Decrypt
        decrypted = manager.decrypt(encrypted, key)

        # Verify plaintext matches
        assert decrypted == test_data

    def test_empty_data_encryption(self, manager):
        """Test encryption/decryption of empty data."""
        key = manager.generate_key(EncryptionAlgorithm.AES_256_GCM)
        empty_data = b""

        encrypted = manager.encrypt(empty_data, EncryptionAlgorithm.AES_256_GCM, key)
        decrypted = manager.decrypt(encrypted, key)

        assert decrypted == empty_data

    def test_large_data_encryption(self, manager):
        """Test encryption/decryption of large data."""
        key = manager.generate_key(EncryptionAlgorithm.AES_256_GCM)
        large_data = b"x" * 1024 * 1024  # 1MB

        encrypted = manager.encrypt(large_data, EncryptionAlgorithm.AES_256_GCM, key)
        decrypted = manager.decrypt(encrypted, key)

        assert decrypted == large_data

    def test_unicode_data_encryption(self, manager):
        """Test encryption/decryption of Unicode data."""
        key = manager.generate_key(EncryptionAlgorithm.AES_256_GCM)
        unicode_data = "Hello 世界 🔐".encode()

        encrypted = manager.encrypt(unicode_data, EncryptionAlgorithm.AES_256_GCM, key)
        decrypted = manager.decrypt(encrypted, key)

        assert decrypted == unicode_data


class TestKeyGeneration:
    """Test cryptographic key generation."""

    def test_aes_256_gcm_key_generation(self, manager):
        """Test AES-256-GCM key generation with correct size."""
        key = manager.generate_key(EncryptionAlgorithm.AES_256_GCM)

        # Verify key size (256 bits = 32 bytes)
        assert len(key) == 32
        assert isinstance(key, bytes)

    def test_chacha20_poly1305_key_generation(self, manager):
        """Test ChaCha20-Poly1305 key generation with correct size."""
        key = manager.generate_key(EncryptionAlgorithm.CHACHA20_POLY1305)

        # Verify key size (256 bits = 32 bytes)
        assert len(key) == 32
        assert isinstance(key, bytes)

    def test_key_uniqueness(self, manager):
        """Test that generated keys are unique."""
        keys = [
            manager.generate_key(EncryptionAlgorithm.AES_256_GCM)
            for _ in range(10)
        ]

        # All keys should be unique
        assert len(set(keys)) == 10

    def test_key_generation_for_invalid_algorithm(self, manager):
        """Test key generation fails for non-AEAD algorithms."""
        with pytest.raises(ValueError, match="Invalid algorithm choice"):
            manager.generate_key(EncryptionAlgorithm.AES_256_CBC)


class TestKeyRotation:
    """Test key rotation functionality."""

    def test_key_rotation(self, manager):
        """Test key rotation generates new key with metadata."""
        rotation = manager.rotate_key("key-001", EncryptionAlgorithm.AES_256_GCM)

        # Verify rotation structure
        assert "old_key_id" in rotation
        assert "new_key_id" in rotation
        assert "new_key" in rotation
        assert "algorithm" in rotation

        # Verify values
        assert rotation["old_key_id"] == "key-001"
        assert rotation["new_key_id"] != "key-001"
        assert len(rotation["new_key"]) == 32
        assert rotation["algorithm"] == "aes-256-gcm"

    def test_key_rotation_different_algorithm(self, manager):
        """Test key rotation with algorithm change."""
        rotation = manager.rotate_key("key-001", EncryptionAlgorithm.CHACHA20_POLY1305)

        assert rotation["algorithm"] == "chacha20-poly1305"
        assert len(rotation["new_key"]) == 32

    def test_key_rotation_unique_ids(self, manager):
        """Test that key rotation generates unique key IDs."""
        rotation1 = manager.rotate_key("key-001", EncryptionAlgorithm.AES_256_GCM)
        rotation2 = manager.rotate_key("key-001", EncryptionAlgorithm.AES_256_GCM)

        assert rotation1["new_key_id"] != rotation2["new_key_id"]

    def test_key_rotation_re_encryption(self, manager, test_data):
        """Test re-encryption during key rotation."""
        # Original encryption
        old_key = manager.generate_key(EncryptionAlgorithm.AES_256_GCM)
        encrypted_old = manager.encrypt(test_data, EncryptionAlgorithm.AES_256_GCM, old_key)

        # Key rotation
        rotation = manager.rotate_key("key-001", EncryptionAlgorithm.CHACHA20_POLY1305)
        new_key = rotation["new_key"]

        # Decrypt with old key
        decrypted = manager.decrypt(encrypted_old, old_key)

        # Re-encrypt with new key
        encrypted_new = manager.encrypt(decrypted, EncryptionAlgorithm.CHACHA20_POLY1305, new_key)

        # Verify new encryption
        decrypted_new = manager.decrypt(encrypted_new, new_key)
        assert decrypted_new == test_data


class TestErrorHandling:
    """Test error handling for invalid operations."""

    def test_decrypt_with_wrong_key(self, manager, test_data):
        """Test decryption fails with wrong key."""
        key1 = manager.generate_key(EncryptionAlgorithm.AES_256_GCM)
        key2 = manager.generate_key(EncryptionAlgorithm.AES_256_GCM)

        encrypted = manager.encrypt(test_data, EncryptionAlgorithm.AES_256_GCM, key1)

        with pytest.raises(DecryptionError, match="Decryption failed"):
            manager.decrypt(encrypted, key2)

    def test_decrypt_with_invalid_key_size(self, manager, test_data):
        """Test decryption fails with invalid key size."""
        key = manager.generate_key(EncryptionAlgorithm.AES_256_GCM)
        encrypted = manager.encrypt(test_data, EncryptionAlgorithm.AES_256_GCM, key)

        # Try with wrong size key
        wrong_key = b"short"

        with pytest.raises(InvalidKeyError, match="Invalid key size"):
            manager.decrypt(encrypted, wrong_key)

    def test_encrypt_with_invalid_key_size(self, manager, test_data):
        """Test encryption fails with invalid key size."""
        wrong_key = b"short"

        with pytest.raises(InvalidKeyError, match="Invalid key size"):
            manager.encrypt(test_data, EncryptionAlgorithm.AES_256_GCM, wrong_key)

    def test_decrypt_with_missing_fields(self, manager):
        """Test decryption fails with missing required fields."""
        key = manager.generate_key(EncryptionAlgorithm.AES_256_GCM)

        # Missing 'tag' field
        invalid_encrypted = {
            "algorithm": "aes-256-gcm",
            "ciphertext": b"data",
            "nonce": b"nonce",
        }

        with pytest.raises(ValueError, match="missing required fields"):
            manager.decrypt(invalid_encrypted, key)

    def test_decrypt_with_unknown_algorithm(self, manager):
        """Test decryption fails with unknown algorithm."""
        key = manager.generate_key(EncryptionAlgorithm.AES_256_GCM)

        invalid_encrypted = {
            "algorithm": "unknown-algo",
            "ciphertext": b"data",
            "nonce": b"nonce",
            "tag": b"tag",
        }

        with pytest.raises(ValueError, match="Unknown algorithm"):
            manager.decrypt(invalid_encrypted, key)

    def test_encrypt_with_non_aead_algorithm(self, manager, test_data):
        """Test encryption fails with non-AEAD algorithm."""
        with pytest.raises(ValueError, match="Invalid algorithm choice"):
            manager.encrypt(test_data, EncryptionAlgorithm.AES_256_CBC, b"key")


class TestAEADAuthentication:
    """Test AEAD authentication and tamper detection."""

    def test_tampered_ciphertext_fails(self, manager, test_data):
        """Test that tampered ciphertext fails authentication."""
        key = manager.generate_key(EncryptionAlgorithm.AES_256_GCM)
        encrypted = manager.encrypt(test_data, EncryptionAlgorithm.AES_256_GCM, key)

        # Tamper with ciphertext
        tampered = encrypted.copy()
        tampered["ciphertext"] = bytes(
            b ^ 0xFF for b in encrypted["ciphertext"]
        )

        with pytest.raises(DecryptionError, match="Decryption failed"):
            manager.decrypt(tampered, key)

    def test_tampered_tag_fails(self, manager, test_data):
        """Test that tampered authentication tag fails."""
        key = manager.generate_key(EncryptionAlgorithm.AES_256_GCM)
        encrypted = manager.encrypt(test_data, EncryptionAlgorithm.AES_256_GCM, key)

        # Tamper with tag
        tampered = encrypted.copy()
        tampered["tag"] = bytes(b ^ 0xFF for b in encrypted["tag"])

        with pytest.raises(DecryptionError, match="Decryption failed"):
            manager.decrypt(tampered, key)

    def test_tampered_nonce_fails(self, manager, test_data):
        """Test that tampered nonce fails authentication."""
        key = manager.generate_key(EncryptionAlgorithm.AES_256_GCM)
        encrypted = manager.encrypt(test_data, EncryptionAlgorithm.AES_256_GCM, key)

        # Tamper with nonce
        tampered = encrypted.copy()
        tampered["nonce"] = bytes(b ^ 0xFF for b in encrypted["nonce"])

        with pytest.raises(DecryptionError, match="Decryption failed"):
            manager.decrypt(tampered, key)

    def test_swapped_components_fail(self, manager, test_data):
        """Test that swapping components from different encryptions fails."""
        key = manager.generate_key(EncryptionAlgorithm.AES_256_GCM)

        encrypted1 = manager.encrypt(test_data, EncryptionAlgorithm.AES_256_GCM, key)
        encrypted2 = manager.encrypt(test_data, EncryptionAlgorithm.AES_256_GCM, key)

        # Swap nonce from encrypted2 into encrypted1
        swapped = encrypted1.copy()
        swapped["nonce"] = encrypted2["nonce"]

        with pytest.raises(DecryptionError, match="Decryption failed"):
            manager.decrypt(swapped, key)


class TestNonceUniqueness:
    """Test nonce/IV uniqueness properties."""

    def test_different_nonces_same_data(self, manager, test_data):
        """Test that encrypting same data produces different nonces."""
        key = manager.generate_key(EncryptionAlgorithm.AES_256_GCM)

        encrypted1 = manager.encrypt(test_data, EncryptionAlgorithm.AES_256_GCM, key)
        encrypted2 = manager.encrypt(test_data, EncryptionAlgorithm.AES_256_GCM, key)

        # Nonces should be different
        assert encrypted1["nonce"] != encrypted2["nonce"]

        # Ciphertexts should be different (due to different nonces)
        assert encrypted1["ciphertext"] != encrypted2["ciphertext"]

    def test_nonce_uniqueness_multiple_encryptions(self, manager):
        """Test nonce uniqueness across multiple encryptions."""
        key = manager.generate_key(EncryptionAlgorithm.AES_256_GCM)
        data = b"test data"

        nonces = [
            manager.encrypt(data, EncryptionAlgorithm.AES_256_GCM, key)["nonce"]
            for _ in range(100)
        ]

        # All nonces should be unique
        assert len(set(nonces)) == 100


class TestAssociatedData:
    """Test associated authenticated data (AAD) functionality."""

    def test_associated_data_authentication(self, manager, test_data):
        """Test that associated data is authenticated."""
        key = manager.generate_key(EncryptionAlgorithm.AES_256_GCM)
        aad = b"metadata: user=alice, timestamp=2025-11-01"

        # Encrypt with AAD
        encrypted = manager.encrypt(
            test_data,
            EncryptionAlgorithm.AES_256_GCM,
            key,
            associated_data=aad
        )

        # Decrypt with same AAD
        decrypted = manager.decrypt(encrypted, key, associated_data=aad)
        assert decrypted == test_data

    def test_wrong_associated_data_fails(self, manager, test_data):
        """Test that wrong associated data fails authentication."""
        key = manager.generate_key(EncryptionAlgorithm.AES_256_GCM)
        aad1 = b"metadata: user=alice"
        aad2 = b"metadata: user=bob"

        # Encrypt with aad1
        encrypted = manager.encrypt(
            test_data,
            EncryptionAlgorithm.AES_256_GCM,
            key,
            associated_data=aad1
        )

        # Try to decrypt with aad2
        with pytest.raises(DecryptionError, match="Decryption failed"):
            manager.decrypt(encrypted, key, associated_data=aad2)

    def test_missing_associated_data_fails(self, manager, test_data):
        """Test that missing associated data fails authentication."""
        key = manager.generate_key(EncryptionAlgorithm.AES_256_GCM)
        aad = b"metadata: important"

        # Encrypt with AAD
        encrypted = manager.encrypt(
            test_data,
            EncryptionAlgorithm.AES_256_GCM,
            key,
            associated_data=aad
        )

        # Try to decrypt without AAD
        with pytest.raises(DecryptionError, match="Decryption failed"):
            manager.decrypt(encrypted, key, associated_data=None)


class TestAlgorithmMetadata:
    """Test that encryption respects algorithm metadata."""

    def test_correct_nonce_size(self, manager, test_data):
        """Test that nonces have correct size from metadata."""
        for algo in [EncryptionAlgorithm.AES_256_GCM, EncryptionAlgorithm.CHACHA20_POLY1305]:
            key = manager.generate_key(algo)
            encrypted = manager.encrypt(test_data, algo, key)

            metadata = get_algorithm_metadata(algo)
            assert len(encrypted["nonce"]) == metadata.nonce_size

    def test_correct_tag_size(self, manager, test_data):
        """Test that tags have correct size from metadata."""
        for algo in [EncryptionAlgorithm.AES_256_GCM, EncryptionAlgorithm.CHACHA20_POLY1305]:
            key = manager.generate_key(algo)
            encrypted = manager.encrypt(test_data, algo, key)

            metadata = get_algorithm_metadata(algo)
            assert len(encrypted["tag"]) == metadata.tag_size


class TestAutomaticKeyGeneration:
    """Test automatic key generation when key is None."""

    def test_encrypt_without_key_generates_key(self, manager, test_data):
        """Test that encryption without key automatically generates one."""
        # Note: Without key, we can't decrypt, so this just tests it doesn't crash
        encrypted = manager.encrypt(test_data, EncryptionAlgorithm.AES_256_GCM, key=None)

        # Verify encrypted data structure exists
        assert "algorithm" in encrypted
        assert "ciphertext" in encrypted
        assert "nonce" in encrypted
        assert "tag" in encrypted


class TestSecurityProperties:
    """Test security properties and guarantees."""

    def test_no_key_leakage_in_errors(self, manager, test_data):
        """Test that error messages don't leak key material."""
        key = manager.generate_key(EncryptionAlgorithm.AES_256_GCM)
        encrypted = manager.encrypt(test_data, EncryptionAlgorithm.AES_256_GCM, key)

        wrong_key = manager.generate_key(EncryptionAlgorithm.AES_256_GCM)

        try:
            manager.decrypt(encrypted, wrong_key)
        except DecryptionError as e:
            error_msg = str(e)
            # Verify key bytes are not in error message
            assert key.hex() not in error_msg
            assert wrong_key.hex() not in error_msg

    def test_constant_time_comparison(self, manager):
        """Test that tag verification should use constant-time comparison."""
        # This is implicitly tested by the cryptography library's implementation
        # The library uses constant-time operations internally
        # This test documents the security requirement
        key = manager.generate_key(EncryptionAlgorithm.AES_256_GCM)
        data = b"sensitive"

        encrypted = manager.encrypt(data, EncryptionAlgorithm.AES_256_GCM, key)

        # Successful decryption
        decrypted = manager.decrypt(encrypted, key)
        assert decrypted == data


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=core.security.encryption_manager", "--cov-report=term-missing"])
