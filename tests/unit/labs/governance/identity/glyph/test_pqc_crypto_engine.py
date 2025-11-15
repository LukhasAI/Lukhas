"""
Unit Tests for GLYPH Pipeline Components

Tests the interface behavior, security properties, and performance
of the GLYPH generation pipeline components.

Author: LUKHAS Identity Team
Version: 1.0.0
"""
import time

import pytest

from labs.governance.identity.auth_backend.pqc_crypto_engine import (
    PQCCryptoEngine,
    PQCKeyPair,
    PQCSignature,
)


class TestPQCCryptoEngine:
    """Test Post-Quantum Cryptography Engine"""

    def test_generate_dilithium_keypair(self):
        """Test Dilithium key pair generation"""
        engine = PQCCryptoEngine()
        keypair = engine.generate_signature_keypair("Dilithium3")

        assert isinstance(keypair, PQCKeyPair)
        assert keypair.algorithm == "Dilithium3"
        assert len(keypair.public_key) == 1952  # Dilithium3 public key size
        assert len(keypair.private_key) == 4000  # Dilithium3 private key size

    def test_generate_dilithium2_keypair(self):
        """Test Dilithium2 key pair generation"""
        engine = PQCCryptoEngine()
        keypair = engine.generate_signature_keypair("Dilithium2")

        assert keypair.algorithm == "Dilithium2"
        assert len(keypair.public_key) == 1312
        assert len(keypair.private_key) == 2528

    def test_generate_dilithium5_keypair(self):
        """Test Dilithium5 key pair generation"""
        engine = PQCCryptoEngine()
        keypair = engine.generate_signature_keypair("Dilithium5")

        assert keypair.algorithm == "Dilithium5"
        assert len(keypair.public_key) == 2592
        assert len(keypair.private_key) == 4864

    def test_sign_message(self):
        """Test message signing"""
        engine = PQCCryptoEngine()
        keypair = engine.generate_signature_keypair("Dilithium3")
        message = b"Test message for signing"

        signature = engine.sign_message(message, keypair.private_key, "Dilithium3")

        assert isinstance(signature, PQCSignature)
        assert signature.algorithm == "Dilithium3"
        assert len(signature.signature) == 3293  # Dilithium3 signature size
        assert signature.timestamp > 0

    def test_verify_signature(self):
        """Test signature verification"""
        engine = PQCCryptoEngine()
        keypair = engine.generate_signature_keypair("Dilithium3")
        message = b"Test message"

        signature = engine.sign_message(message, keypair.private_key, "Dilithium3")
        is_valid = engine.verify_signature(message, signature, keypair.public_key)

        assert is_valid is True

    def test_generate_kyber_keypair(self):
        """Test Kyber KEM key pair generation"""
        engine = PQCCryptoEngine()
        keypair = engine.generate_kem_keypair("Kyber768")

        assert isinstance(keypair, PQCKeyPair)
        assert keypair.algorithm == "Kyber768"
        assert len(keypair.public_key) == 1184
        assert len(keypair.private_key) == 2400

    def test_encapsulate_decapsulate(self):
        """Test KEM encapsulation and decapsulation"""
        engine = PQCCryptoEngine()
        keypair = engine.generate_kem_keypair("Kyber768")

        ciphertext, shared_secret1 = engine.encapsulate(
            keypair.public_key, "Kyber768"
        )
        shared_secret2 = engine.decapsulate(
            ciphertext, keypair.private_key, "Kyber768"
        )

        assert len(ciphertext) == 1088  # Kyber768 ciphertext size
        assert len(shared_secret1) == 32  # Shared secret size
        assert len(shared_secret2) == 32

    def test_algorithm_info(self):
        """Test algorithm information retrieval"""
        engine = PQCCryptoEngine()
        info = engine.get_algorithm_info("Dilithium3")

        assert info["type"] == "signature"
        assert info["security_level"] == "NIST Level 3"
        assert info["signature_size"] == 3293

    def test_multiple_algorithms(self):
        """Test different Dilithium variants"""
        engine = PQCCryptoEngine()
        
        # Test Dilithium2
        kp2 = engine.generate_signature_keypair("Dilithium2")
        msg = b"test"
        sig2 = engine.sign_message(msg, kp2.private_key, "Dilithium2")
        assert len(sig2.signature) == 2420
        
        # Test Dilithium5
        kp5 = engine.generate_signature_keypair("Dilithium5")
        sig5 = engine.sign_message(msg, kp5.private_key, "Dilithium5")
        assert len(sig5.signature) == 4595

    def test_kyber_variants(self):
        """Test different Kyber variants"""
        engine = PQCCryptoEngine()
        
        # Kyber512
        kp512 = engine.generate_kem_keypair("Kyber512")
        assert len(kp512.public_key) == 800
        ct512, ss512 = engine.encapsulate(kp512.public_key, "Kyber512")
        assert len(ct512) == 768
        assert len(ss512) == 32
        
        # Kyber1024
        kp1024 = engine.generate_kem_keypair("Kyber1024")
        assert len(kp1024.public_key) == 1568
        ct1024, ss1024 = engine.encapsulate(kp1024.public_key, "Kyber1024")
        assert len(ct1024) == 1568
        assert len(ss1024) == 32


@pytest.mark.benchmark
class TestPQCPerformance:
    """Performance tests for PQC operations"""

    def test_signature_performance(self):
        """Test PQC signature generation performance"""
        engine = PQCCryptoEngine()
        keypair = engine.generate_signature_keypair("Dilithium3")
        message = b"Performance test message"
        
        start = time.perf_counter()
        for _ in range(100):
            engine.sign_message(message, keypair.private_key, "Dilithium3")
        end = time.perf_counter()
        
        avg_time = (end - start) / 100
        # Stub implementation should be fast
        assert avg_time < 0.010  # < 10ms per signature (stub)

    def test_keypair_generation_performance(self):
        """Test key pair generation performance"""
        engine = PQCCryptoEngine()
        
        start = time.perf_counter()
        for _ in range(100):
            engine.generate_signature_keypair("Dilithium3")
        end = time.perf_counter()
        
        avg_time = (end - start) / 100
        assert avg_time < 0.010  # < 10ms per keypair

    def test_kem_performance(self):
        """Test KEM operations performance"""
        engine = PQCCryptoEngine()
        keypair = engine.generate_kem_keypair("Kyber768")
        
        start = time.perf_counter()
        for _ in range(100):
            ct, ss = engine.encapsulate(keypair.public_key, "Kyber768")
            engine.decapsulate(ct, keypair.private_key, "Kyber768")
        end = time.perf_counter()
        
        avg_time = (end - start) / 100
        assert avg_time < 0.010  # < 10ms per encap+decap
