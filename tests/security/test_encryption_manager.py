import pytest
from core.security.encryption_manager import (
    DecryptionError,
    EncryptionError,
    EncryptionManager,
    InvalidKeyError,
)
from core.security.encryption_types import EncryptionAlgorithm


@pytest.fixture
def manager():
    """Fixture to create an EncryptionManager instance."""
    return EncryptionManager()

class TestEncryptionManager:
    """Tests for the EncryptionManager."""

    def test_generate_key(self, manager):
        """Test key generation for all supported algorithms."""
        for alg in [EncryptionAlgorithm.AES_256_GCM, EncryptionAlgorithm.CHACHA20_POLY1305]:
            key = manager.generate_key(alg)
            assert isinstance(key, bytes)
            # AES and ChaCha20 both use 256-bit (32-byte) keys
            assert len(key) == 32

    def test_encrypt_decrypt_roundtrip_aes(self, manager):
        """Test a full encryption-decryption roundtrip with AES-256-GCM."""
        data = b"test data for AES"
        key = manager.generate_key(EncryptionAlgorithm.AES_256_GCM)

        encrypted_data = manager.encrypt(data, EncryptionAlgorithm.AES_256_GCM, key)
        decrypted_data = manager.decrypt(encrypted_data, key)

        assert decrypted_data == data

    def test_encrypt_decrypt_roundtrip_chacha(self, manager):
        """Test a full encryption-decryption roundtrip with ChaCha20-Poly1305."""
        data = b"test data for ChaCha"
        key = manager.generate_key(EncryptionAlgorithm.CHACHA20_POLY1305)

        encrypted_data = manager.encrypt(data, EncryptionAlgorithm.CHACHA20_POLY1305, key)
        decrypted_data = manager.decrypt(encrypted_data, key)

        assert decrypted_data == data

    def test_decrypt_with_wrong_key(self, manager):
        """Test that decryption fails with the wrong key."""
        data = b"test data"
        key1 = manager.generate_key(EncryptionAlgorithm.AES_256_GCM)
        key2 = manager.generate_key(EncryptionAlgorithm.AES_256_GCM)

        encrypted_data = manager.encrypt(data, EncryptionAlgorithm.AES_256_GCM, key1)

        with pytest.raises(DecryptionError):
            manager.decrypt(encrypted_data, key2)

    def test_decrypt_with_tampered_data(self, manager):
        """Test that decryption fails if the ciphertext is tampered with."""
        data = b"test data"
        key = manager.generate_key(EncryptionAlgorithm.AES_256_GCM)
        encrypted_data = manager.encrypt(data, EncryptionAlgorithm.AES_256_GCM, key)

        # Tamper with the ciphertext
        original_ciphertext = encrypted_data["ciphertext"]
        tampered_ciphertext = bytearray(original_ciphertext)
        tampered_ciphertext[0] ^= 1  # Flip a bit
        encrypted_data["ciphertext"] = bytes(tampered_ciphertext)

        with pytest.raises(DecryptionError):
            manager.decrypt(encrypted_data, key)

    def test_invalid_key_size_encrypt(self, manager):
        """Test that encryption fails with a key of the wrong size."""
        with pytest.raises(InvalidKeyError):
            manager.encrypt(b"data", EncryptionAlgorithm.AES_256_GCM, b"wrongsizekey")

    def test_invalid_key_size_decrypt(self, manager):
        """Test that decryption fails with a key of the wrong size."""
        # This test is a bit contrived as you can't get an encrypted blob without a valid key,
        # but it's good for ensuring the validation is there.
        encrypted_data = {
            "algorithm": "aes-256-gcm",
            "ciphertext": b"...",
            "nonce": b"...",
            "tag": b"..."
        }
        with pytest.raises(InvalidKeyError):
            manager.decrypt(encrypted_data, b"wrongsizekey")
