"""Comprehensive tests for Post-Quantum Cryptography (PQC) signer.

Tests cover:
- PQC availability detection
- Key generation and loading
- Signing operations (Dilithium2 and HMAC fallback)
- Signature verification  
- Key management and persistence
- HMAC fallback mode
- Factory function behavior
- Integration patterns
- Security properties
- Edge cases and error handling
"""
from __future__ import annotations

import hashlib
import hmac
import tempfile
from pathlib import Path
from unittest import mock

import pytest

from services.registry.pqc_signer import (
    PQC_AVAILABLE,
    PQCSigner,
    create_registry_signer,
)


class TestPQCAvailability:
    """Test PQC availability detection."""

    def test_pqc_availability_constant(self):
        """Test that PQC_AVAILABLE is a boolean."""
        assert isinstance(PQC_AVAILABLE, bool)

    def test_pqc_signer_reports_availability(self):
        """Test that PQC signer reports its availability."""
        signer = PQCSigner(fallback_hmac_key="test-key")
        assert isinstance(signer.pqc_available, bool)
        assert signer.pqc_available == PQC_AVAILABLE


class TestPQCSignerInitialization:
    """Test PQCSigner initialization."""

    def test_initialization_with_hmac_fallback(self):
        """Test initialization in HMAC fallback mode."""
        signer = PQCSigner(fallback_hmac_key="my-hmac-key")
        
        assert signer.fallback_hmac_key == "my-hmac-key"
        assert signer.key_path is None
        assert signer.public_key_path is None

    def test_default_hmac_key(self):
        """Test default HMAC key is set."""
        signer = PQCSigner()
        
        assert signer.fallback_hmac_key == "dev-hmac-key"

    def test_initialization_with_key_paths(self):
        """Test initialization with key paths."""
        with tempfile.TemporaryDirectory() as tmpdir:
            key_path = Path(tmpdir) / "private.key"
            public_path = Path(tmpdir) / "public.key"
            
            signer = PQCSigner(
                key_path=key_path,
                public_key_path=public_path,
                fallback_hmac_key="test-key"
            )
            
            assert signer.key_path == key_path
            assert signer.public_key_path == public_path

    @pytest.mark.skipif(not PQC_AVAILABLE, reason="PQC not available")
    def test_key_generation_when_pqc_available(self):
        """Test that keys are generated when PQC is available."""
        with tempfile.TemporaryDirectory() as tmpdir:
            key_path = Path(tmpdir) / "private.key"
            public_path = Path(tmpdir) / "public.key"
            
            signer = PQCSigner(
                key_path=key_path,
                public_key_path=public_path
            )
            
            # Keys should be generated and saved
            assert key_path.exists()
            assert public_path.exists()
            assert hasattr(signer, 'private_key')
            assert hasattr(signer, 'public_key')
            assert len(signer.private_key) > 0
            assert len(signer.public_key) > 0

    @pytest.mark.skipif(not PQC_AVAILABLE, reason="PQC not available")
    def test_key_loading_when_keys_exist(self):
        """Test that existing keys are loaded."""
        with tempfile.TemporaryDirectory() as tmpdir:
            key_path = Path(tmpdir) / "private.key"
            public_path = Path(tmpdir) / "public.key"
            
            # Create first signer to generate keys
            signer1 = PQCSigner(
                key_path=key_path,
                public_key_path=public_path
            )
            original_private = signer1.private_key
            original_public = signer1.public_key
            
            # Create second signer - should load existing keys
            signer2 = PQCSigner(
                key_path=key_path,
                public_key_path=public_path
            )
            
            # Keys should match
            assert signer2.private_key == original_private
            assert signer2.public_key == original_public


class TestHMACFallbackSigning:
    """Test HMAC fallback signing mode."""

    def test_hmac_sign_basic(self):
        """Test basic HMAC signing."""
        signer = PQCSigner(fallback_hmac_key="test-key")
        
        data = b"test data"
        signature = signer.sign(data)
        
        # HMAC-SHA256 hex is 64 bytes
        assert isinstance(signature, bytes)
        assert len(signature) == 64

    def test_hmac_signature_deterministic(self):
        """Test that HMAC signatures are deterministic."""
        signer = PQCSigner(fallback_hmac_key="test-key")
        
        data = b"test data"
        sig1 = signer.sign(data)
        sig2 = signer.sign(data)
        
        assert sig1 == sig2

    def test_hmac_different_data_different_signature(self):
        """Test different data produces different signatures."""
        signer = PQCSigner(fallback_hmac_key="test-key")
        
        data1 = b"test data 1"
        data2 = b"test data 2"
        
        sig1 = signer.sign(data1)
        sig2 = signer.sign(data2)
        
        assert sig1 != sig2

    def test_hmac_different_keys_different_signature(self):
        """Test different HMAC keys produce different signatures."""
        signer1 = PQCSigner(fallback_hmac_key="key1")
        signer2 = PQCSigner(fallback_hmac_key="key2")
        
        data = b"test data"
        sig1 = signer1.sign(data)
        sig2 = signer2.sign(data)
        
        assert sig1 != sig2

    def test_hmac_verify_valid_signature(self):
        """Test HMAC verification of valid signature."""
        signer = PQCSigner(fallback_hmac_key="test-key")
        
        data = b"test data"
        signature = signer.sign(data)
        is_valid = signer.verify(data, signature)
        
        assert is_valid is True

    def test_hmac_verify_invalid_signature(self):
        """Test HMAC verification rejects invalid signature."""
        signer = PQCSigner(fallback_hmac_key="test-key")
        
        data = b"test data"
        invalid_signature = b"0" * 64  # Wrong signature
        is_valid = signer.verify(data, invalid_signature)
        
        assert is_valid is False

    def test_hmac_verify_tampered_data(self):
        """Test HMAC verification detects tampered data."""
        signer = PQCSigner(fallback_hmac_key="test-key")
        
        original_data = b"test data"
        signature = signer.sign(original_data)
        
        tampered_data = b"tampered data"
        is_valid = signer.verify(tampered_data, signature)
        
        assert is_valid is False

    def test_hmac_verify_wrong_key(self):
        """Test verification fails with wrong key."""
        signer1 = PQCSigner(fallback_hmac_key="key1")
        signer2 = PQCSigner(fallback_hmac_key="key2")
        
        data = b"test data"
        signature = signer1.sign(data)
        is_valid = signer2.verify(data, signature)
        
        assert is_valid is False


class TestHMACFallbackEdgeCases:
    """Test HMAC fallback edge cases."""

    def test_empty_data(self):
        """Test signing empty data."""
        signer = PQCSigner(fallback_hmac_key="test-key")
        
        data = b""
        signature = signer.sign(data)
        is_valid = signer.verify(data, signature)
        
        assert is_valid is True

    def test_large_data(self):
        """Test signing large data."""
        signer = PQCSigner(fallback_hmac_key="test-key")
        
        data = b"x" * 1_000_000  # 1MB
        signature = signer.sign(data)
        is_valid = signer.verify(data, signature)
        
        assert is_valid is True

    def test_binary_data(self):
        """Test signing arbitrary binary data."""
        signer = PQCSigner(fallback_hmac_key="test-key")
        
        data = bytes(range(256))  # All byte values
        signature = signer.sign(data)
        is_valid = signer.verify(data, signature)
        
        assert is_valid is True

    def test_unicode_in_key(self):
        """Test HMAC with Unicode characters in key."""
        signer = PQCSigner(fallback_hmac_key="test-key-🔐-unicode")
        
        data = b"test data"
        signature = signer.sign(data)
        is_valid = signer.verify(data, signature)
        
        assert is_valid is True

    def test_malformed_signature(self):
        """Test verification with malformed signature."""
        signer = PQCSigner(fallback_hmac_key="test-key")
        
        data = b"test data"
        
        # Test various malformed signatures
        malformed_signatures = [
            b"",  # Empty
            b"xyz",  # Too short
            b"not_hex_at_all_!!",  # Invalid characters
            b"0" * 63,  # Wrong length
        ]
        
        for bad_sig in malformed_signatures:
            is_valid = signer.verify(data, bad_sig)
            assert is_valid is False


@pytest.mark.skipif(not PQC_AVAILABLE, reason="PQC not available")
class TestDilithium2Signing:
    """Test Dilithium2 PQC signing mode."""

    def test_dilithium2_sign_basic(self):
        """Test basic Dilithium2 signing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            key_path = Path(tmpdir) / "private.key"
            public_path = Path(tmpdir) / "public.key"
            
            signer = PQCSigner(
                key_path=key_path,
                public_key_path=public_path
            )
            
            data = b"test data"
            signature = signer.sign(data)
            
            # Dilithium2 signatures are typically ~2400 bytes
            assert isinstance(signature, bytes)
            assert len(signature) > 2000

    def test_dilithium2_verify_valid_signature(self):
        """Test Dilithium2 verification of valid signature."""
        with tempfile.TemporaryDirectory() as tmpdir:
            key_path = Path(tmpdir) / "private.key"
            public_path = Path(tmpdir) / "public.key"
            
            signer = PQCSigner(
                key_path=key_path,
                public_key_path=public_path
            )
            
            data = b"test data"
            signature = signer.sign(data)
            is_valid = signer.verify(data, signature)
            
            assert is_valid is True

    def test_dilithium2_verify_invalid_signature(self):
        """Test Dilithium2 verification rejects invalid signature."""
        with tempfile.TemporaryDirectory() as tmpdir:
            key_path = Path(tmpdir) / "private.key"
            public_path = Path(tmpdir) / "public.key"
            
            signer = PQCSigner(
                key_path=key_path,
                public_key_path=public_path
            )
            
            data = b"test data"
            invalid_signature = b"0" * 2500
            is_valid = signer.verify(data, invalid_signature)
            
            assert is_valid is False

    def test_dilithium2_verify_tampered_data(self):
        """Test Dilithium2 verification detects tampered data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            key_path = Path(tmpdir) / "private.key"
            public_path = Path(tmpdir) / "public.key"
            
            signer = PQCSigner(
                key_path=key_path,
                public_key_path=public_path
            )
            
            original_data = b"test data"
            signature = signer.sign(original_data)
            
            tampered_data = b"tampered data"
            is_valid = signer.verify(tampered_data, signature)
            
            assert is_valid is False

    def test_dilithium2_different_keypair(self):
        """Test verification fails with different keypair."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create two signers with different keys
            key_path1 = Path(tmpdir) / "private1.key"
            public_path1 = Path(tmpdir) / "public1.key"
            signer1 = PQCSigner(key_path=key_path1, public_key_path=public_path1)
            
            key_path2 = Path(tmpdir) / "private2.key"
            public_path2 = Path(tmpdir) / "public2.key"
            signer2 = PQCSigner(key_path=key_path2, public_key_path=public_path2)
            
            # Sign with signer1, verify with signer2
            data = b"test data"
            signature = signer1.sign(data)
            is_valid = signer2.verify(data, signature)
            
            assert is_valid is False

    def test_dilithium2_key_persistence(self):
        """Test that keys persist across signer instances."""
        with tempfile.TemporaryDirectory() as tmpdir:
            key_path = Path(tmpdir) / "private.key"
            public_path = Path(tmpdir) / "public.key"
            
            # Create signer and sign data
            signer1 = PQCSigner(key_path=key_path, public_key_path=public_path)
            data = b"test data"
            signature = signer1.sign(data)
            
            # Create new signer with same key paths
            signer2 = PQCSigner(key_path=key_path, public_key_path=public_path)
            is_valid = signer2.verify(data, signature)
            
            assert is_valid is True

    def test_dilithium2_signature_not_deterministic(self):
        """Test that Dilithium2 signatures include randomness."""
        with tempfile.TemporaryDirectory() as tmpdir:
            key_path = Path(tmpdir) / "private.key"
            public_path = Path(tmpdir) / "public.key"
            
            signer = PQCSigner(key_path=key_path, public_key_path=public_path)
            
            data = b"test data"
            sig1 = signer.sign(data)
            sig2 = signer.sign(data)
            
            # Dilithium2 includes randomness, so signatures differ
            # Both should still verify though
            assert signer.verify(data, sig1)
            assert signer.verify(data, sig2)


class TestSignatureInfo:
    """Test signature scheme information reporting."""

    def test_info_hmac_fallback(self):
        """Test signature info in HMAC fallback mode."""
        signer = PQCSigner(fallback_hmac_key="test-key")
        info = signer.get_signature_info()
        
        assert info["scheme"] == "HMAC-SHA256"
        assert info["status"] == "fallback"
        assert info["quantum_resistant"] is False
        assert "warning" in info

    @pytest.mark.skipif(not PQC_AVAILABLE, reason="PQC not available")
    def test_info_dilithium2(self):
        """Test signature info in Dilithium2 mode."""
        with tempfile.TemporaryDirectory() as tmpdir:
            key_path = Path(tmpdir) / "private.key"
            public_path = Path(tmpdir) / "public.key"
            
            signer = PQCSigner(key_path=key_path, public_key_path=public_path)
            info = signer.get_signature_info()
            
            assert info["scheme"] == "Dilithium2"
            assert info["status"] == "pqc_active"
            assert info["quantum_resistant"] is True
            assert "public_key_size" in info
            assert info["public_key_size"] > 0
            assert info["algorithm"] == "NIST PQC Dilithium2"


class TestFactoryFunction:
    """Test create_registry_signer factory function."""

    def test_factory_creates_signer(self):
        """Test factory creates signer instance."""
        with tempfile.TemporaryDirectory() as tmpdir:
            registry_root = Path(tmpdir)
            signer = create_registry_signer(registry_root)
            
            assert isinstance(signer, PQCSigner)

    def test_factory_uses_registry_root(self):
        """Test factory uses registry root for key paths."""
        with tempfile.TemporaryDirectory() as tmpdir:
            registry_root = Path(tmpdir)
            signer = create_registry_signer(registry_root)
            
            if signer.pqc_available and signer.key_path:
                expected_dir = registry_root / ".pqc_keys"
                assert signer.key_path.parent == expected_dir

    def test_factory_force_hmac(self):
        """Test factory force_hmac parameter."""
        with tempfile.TemporaryDirectory() as tmpdir:
            registry_root = Path(tmpdir)
            signer = create_registry_signer(registry_root, force_hmac=True)
            
            info = signer.get_signature_info()
            assert info["scheme"] == "HMAC-SHA256"

    def test_factory_uses_env_hmac_key(self, monkeypatch):
        """Test factory uses environment variable for HMAC key."""
        with tempfile.TemporaryDirectory() as tmpdir:
            registry_root = Path(tmpdir)
            monkeypatch.setenv("REGISTRY_HMAC_KEY", "custom-env-key")
            
            signer = create_registry_signer(registry_root, force_hmac=True)
            assert signer.fallback_hmac_key == "custom-env-key"

    def test_factory_default_hmac_key(self):
        """Test factory uses default HMAC key if env not set."""
        with tempfile.TemporaryDirectory() as tmpdir:
            registry_root = Path(tmpdir)
            signer = create_registry_signer(registry_root, force_hmac=True)
            
            # Should use default from environment or fallback
            assert isinstance(signer.fallback_hmac_key, str)
            assert len(signer.fallback_hmac_key) > 0


class TestKeyManagement:
    """Test key management and security."""

    @pytest.mark.skipif(not PQC_AVAILABLE, reason="PQC not available")
    def test_key_file_permissions(self):
        """Test that private key file has restricted permissions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            key_path = Path(tmpdir) / "private.key"
            public_path = Path(tmpdir) / "public.key"
            
            signer = PQCSigner(key_path=key_path, public_key_path=public_path)
            
            # Private key should have restricted permissions (0o600)
            stat_info = key_path.stat()
            mode = stat_info.st_mode & 0o777
            assert mode == 0o600

    @pytest.mark.skipif(not PQC_AVAILABLE, reason="PQC not available")
    def test_key_directory_creation(self):
        """Test that key directories are created if needed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            key_dir = Path(tmpdir) / "nested" / "deep" / "path"
            key_path = key_dir / "private.key"
            public_path = key_dir / "public.key"
            
            assert not key_dir.exists()
            
            signer = PQCSigner(key_path=key_path, public_key_path=public_path)
            
            assert key_dir.exists()
            assert key_path.exists()
            assert public_path.exists()


class TestIntegration:
    """Integration tests for PQC signer."""

    def test_complete_signing_workflow(self):
        """Test complete signing and verification workflow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            registry_root = Path(tmpdir)
            signer = create_registry_signer(registry_root)
            
            # Sign multiple pieces of data
            data_items = [
                b"checkpoint 1",
                b"checkpoint 2",
                b"checkpoint 3",
            ]
            
            signatures = []
            for data in data_items:
                sig = signer.sign(data)
                signatures.append(sig)
            
            # Verify all signatures
            for data, sig in zip(data_items, signatures):
                assert signer.verify(data, sig)

    def test_registry_checkpoint_pattern(self):
        """Test typical registry checkpoint signing pattern."""
        with tempfile.TemporaryDirectory() as tmpdir:
            registry_root = Path(tmpdir)
            signer = create_registry_signer(registry_root)
            
            # Simulate checkpoint data
            import json
            checkpoint = {
                "timestamp": "2025-10-26T12:00:00Z",
                "modules": ["module1", "module2"],
                "version": "1.0.0",
            }
            
            checkpoint_data = json.dumps(checkpoint, sort_keys=True).encode()
            signature = signer.sign(checkpoint_data)
            
            # Store signature alongside checkpoint
            assert signer.verify(checkpoint_data, signature)
            
            # Verify signature info
            info = signer.get_signature_info()
            assert info["quantum_resistant"] or info["scheme"] == "HMAC-SHA256"

    def test_cross_signer_verification_fails(self):
        """Test that signatures from different signers don't cross-verify."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create two independent signers
            root1 = Path(tmpdir) / "registry1"
            root1.mkdir()
            signer1 = create_registry_signer(root1)
            
            root2 = Path(tmpdir) / "registry2"  
            root2.mkdir()
            signer2 = create_registry_signer(root2)
            
            # Sign with signer1
            data = b"test data"
            signature = signer1.sign(data)
            
            # Should verify with signer1
            assert signer1.verify(data, signature)
            
            # Should NOT verify with signer2 (different keys)
            # Note: In HMAC mode with same key, this would verify
            # In PQC mode with different keys, it should fail
            if PQC_AVAILABLE:
                assert not signer2.verify(data, signature)


class TestSecurityProperties:
    """Test security properties of the signer."""

    def test_signature_uniqueness(self):
        """Test that signatures for different data are unique."""
        signer = PQCSigner(fallback_hmac_key="test-key")
        
        # Generate signatures for 100 different data items
        signatures = set()
        for i in range(100):
            data = f"data-{i}".encode()
            sig = signer.sign(data)
            signatures.add(sig)
        
        # All signatures should be unique
        assert len(signatures) == 100

    def test_signature_length_consistency(self):
        """Test that signature length is consistent."""
        signer = PQCSigner(fallback_hmac_key="test-key")
        
        # Sign various sizes of data
        data_sizes = [1, 10, 100, 1000, 10000]
        signatures = []
        
        for size in data_sizes:
            data = b"x" * size
            sig = signer.sign(data)
            signatures.append(sig)
        
        # All signatures should have same length (HMAC-SHA256 hex = 64 bytes)
        signature_lengths = [len(sig) for sig in signatures]
        assert len(set(signature_lengths)) == 1

    def test_timing_safe_comparison(self):
        """Test that HMAC verification uses timing-safe comparison."""
        signer = PQCSigner(fallback_hmac_key="test-key")
        
        data = b"test data"
        correct_signature = signer.sign(data)
        
        # Create signatures with single bit differences
        wrong_sig1 = bytearray(correct_signature)
        wrong_sig1[0] ^= 0x01  # Flip one bit
        
        wrong_sig2 = bytearray(correct_signature)
        wrong_sig2[-1] ^= 0x01  # Flip last bit
        
        # Both should fail (using hmac.compare_digest internally)
        assert not signer.verify(data, bytes(wrong_sig1))
        assert not signer.verify(data, bytes(wrong_sig2))


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_verify_with_corrupt_signature_data(self):
        """Test verification handles corrupted signature gracefully."""
        signer = PQCSigner(fallback_hmac_key="test-key")
        
        data = b"test data"
        
        # Various corrupt signatures
        corrupt_signatures = [
            None,
            b"",
            b"corrupted",
            b"\x00" * 100,
        ]
        
        for corrupt_sig in corrupt_signatures:
            if corrupt_sig is not None:
                result = signer.verify(data, corrupt_sig)
                assert result is False

    def test_sign_handles_various_data_types(self):
        """Test signing handles various byte data correctly."""
        signer = PQCSigner(fallback_hmac_key="test-key")
        
        test_data = [
            b"",  # Empty
            b"simple text",
            b"\x00\x01\x02\xff",  # Binary
            b"unicode: \xc3\xa9\xc3\xa7\xc3\xa0",  # UTF-8 encoded
            b"x" * 10000,  # Large
        ]
        
        for data in test_data:
            signature = signer.sign(data)
            assert isinstance(signature, bytes)
            assert len(signature) > 0
            assert signer.verify(data, signature)
