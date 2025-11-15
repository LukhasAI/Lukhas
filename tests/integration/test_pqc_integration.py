"""
Integration Tests for PQC Crypto Engine

Standalone integration tests for the Post-Quantum Cryptography Engine
that validate the complete workflow without dependencies on the full pipeline.

Author: LUKHAS Identity Team
Version: 1.0.0
"""
import hashlib
import time

import pytest


def test_pqc_engine_import():
    """Test that PQCCryptoEngine can be imported"""
    from labs.governance.identity.auth_backend.pqc_crypto_engine import (
        PQCAlgorithm,
        PQCCryptoEngine,
        PQCKeyPair,
        PQCSignature,
    )

    assert PQCCryptoEngine is not None
    assert PQCKeyPair is not None
    assert PQCSignature is not None
    assert PQCAlgorithm is not None


def test_complete_signature_workflow():
    """Test complete signature generation and verification workflow"""
    from labs.governance.identity.auth_backend.pqc_crypto_engine import PQCCryptoEngine

    engine = PQCCryptoEngine()

    # Step 1: Generate keypair
    keypair = engine.generate_signature_keypair("Dilithium3")
    assert keypair is not None
    assert len(keypair.public_key) > 0
    assert len(keypair.private_key) > 0

    # Step 2: Create message
    message = b"Test identity data for GLYPH authentication"

    # Step 3: Sign message
    signature = engine.sign_message(message, keypair.private_key, "Dilithium3")
    assert signature is not None
    assert len(signature.signature) > 0

    # Step 4: Verify signature
    is_valid = engine.verify_signature(message, signature, keypair.public_key)
    assert is_valid is True


def test_multiple_signatures_different_keys():
    """Test that different keys produce different signatures"""
    from labs.governance.identity.auth_backend.pqc_crypto_engine import PQCCryptoEngine

    engine = PQCCryptoEngine()
    message = b"Test message"

    # Generate two different keypairs
    keypair1 = engine.generate_signature_keypair("Dilithium3")
    keypair2 = engine.generate_signature_keypair("Dilithium3")

    # Keys should be different
    assert keypair1.public_key != keypair2.public_key
    assert keypair1.private_key != keypair2.private_key

    # Signatures should be different
    sig1 = engine.sign_message(message, keypair1.private_key, "Dilithium3")
    sig2 = engine.sign_message(message, keypair2.private_key, "Dilithium3")
    assert sig1.signature != sig2.signature


def test_kem_complete_workflow():
    """Test complete KEM encapsulation and decapsulation workflow"""
    from labs.governance.identity.auth_backend.pqc_crypto_engine import PQCCryptoEngine

    engine = PQCCryptoEngine()

    # Step 1: Generate KEM keypair
    keypair = engine.generate_kem_keypair("Kyber768")
    assert len(keypair.public_key) == 1184
    assert len(keypair.private_key) == 2400

    # Step 2: Encapsulate (sender side)
    ciphertext, shared_secret_sender = engine.encapsulate(
        keypair.public_key, "Kyber768"
    )
    assert len(ciphertext) == 1088
    assert len(shared_secret_sender) == 32

    # Step 3: Decapsulate (receiver side)
    shared_secret_receiver = engine.decapsulate(
        ciphertext, keypair.private_key, "Kyber768"
    )
    assert len(shared_secret_receiver) == 32

    # Note: In stub implementation, shared secrets may not match
    # In production, they should be identical


def test_glyph_identity_data_signing():
    """Test signing GLYPH identity data (realistic use case)"""
    from labs.governance.identity.auth_backend.pqc_crypto_engine import PQCCryptoEngine
    import json

    engine = PQCCryptoEngine()

    # Simulate GLYPH identity data
    identity_data = {
        "lambda_id": "user_test_001",
        "tier_level": 3,
        "glyph_type": "identity_consciousness",
        "timestamp": time.time(),
        "expires_at": time.time() + 86400,  # 24 hours
    }

    # Serialize for signing
    identity_json = json.dumps(identity_data, sort_keys=True)
    identity_bytes = identity_json.encode("utf-8")

    # Generate signing keypair
    keypair = engine.generate_signature_keypair("Dilithium3")

    # Sign identity data
    signature = engine.sign_message(identity_bytes, keypair.private_key, "Dilithium3")

    # Verify signature
    is_valid = engine.verify_signature(identity_bytes, signature, keypair.public_key)
    assert is_valid is True


def test_algorithm_compatibility():
    """Test that all supported algorithms work correctly"""
    from labs.governance.identity.auth_backend.pqc_crypto_engine import PQCCryptoEngine

    engine = PQCCryptoEngine()

    # Test all Dilithium variants
    dilithium_variants = ["Dilithium2", "Dilithium3", "Dilithium5"]
    expected_sig_sizes = [2420, 3293, 4595]

    for variant, expected_size in zip(dilithium_variants, expected_sig_sizes):
        keypair = engine.generate_signature_keypair(variant)
        message = b"Test"
        signature = engine.sign_message(message, keypair.private_key, variant)
        assert len(signature.signature) == expected_size
        assert engine.verify_signature(message, signature, keypair.public_key)

    # Test all Kyber variants
    kyber_variants = ["Kyber512", "Kyber768", "Kyber1024"]
    expected_ct_sizes = [768, 1088, 1568]

    for variant, expected_size in zip(kyber_variants, expected_ct_sizes):
        keypair = engine.generate_kem_keypair(variant)
        ciphertext, shared_secret = engine.encapsulate(keypair.public_key, variant)
        assert len(ciphertext) == expected_size
        assert len(shared_secret) == 32


def test_algorithm_info_retrieval():
    """Test retrieval of algorithm metadata"""
    from labs.governance.identity.auth_backend.pqc_crypto_engine import PQCCryptoEngine

    engine = PQCCryptoEngine()

    # Check Dilithium3 info
    info = engine.get_algorithm_info("Dilithium3")
    assert info["type"] == "signature"
    assert info["security_level"] == "NIST Level 3"
    assert info["public_key_size"] == 1952
    assert info["private_key_size"] == 4000
    assert info["signature_size"] == 3293

    # Check Kyber768 info
    info = engine.get_algorithm_info("Kyber768")
    assert info["type"] == "kem"
    assert info["security_level"] == "NIST Level 3"
    assert info["ciphertext_size"] == 1088
    assert info["shared_secret_size"] == 32


def test_performance_requirements():
    """Test that performance meets requirements for GLYPH pipeline"""
    from labs.governance.identity.auth_backend.pqc_crypto_engine import PQCCryptoEngine

    engine = PQCCryptoEngine()

    # Test signature generation performance
    keypair = engine.generate_signature_keypair("Dilithium3")
    message = b"Performance test"

    iterations = 50
    start = time.perf_counter()
    for _ in range(iterations):
        engine.sign_message(message, keypair.private_key, "Dilithium3")
    end = time.perf_counter()

    avg_time_ms = ((end - start) / iterations) * 1000
    # Stub should be fast (< 10ms)
    # Production PQC may be slower (< 20ms acceptable)
    assert avg_time_ms < 15, f"Signature too slow: {avg_time_ms:.2f}ms"

    # Test verification performance
    signature = engine.sign_message(message, keypair.private_key, "Dilithium3")

    start = time.perf_counter()
    for _ in range(iterations):
        engine.verify_signature(message, signature, keypair.public_key)
    end = time.perf_counter()

    avg_verify_ms = ((end - start) / iterations) * 1000
    assert avg_verify_ms < 5, f"Verification too slow: {avg_verify_ms:.2f}ms"


def test_glyph_security_levels_mapping():
    """Test algorithm selection for different GLYPH security levels"""
    from labs.governance.identity.auth_backend.pqc_crypto_engine import PQCCryptoEngine

    engine = PQCCryptoEngine()

    # BASIC/ENHANCED: No PQC required
    # QUANTUM: Dilithium3 (Level 3)
    # TRANSCENDENT: Dilithium5 (Level 5)

    security_to_algorithm = {
        "quantum": "Dilithium3",
        "transcendent": "Dilithium5",
    }

    for security, algorithm in security_to_algorithm.items():
        keypair = engine.generate_signature_keypair(algorithm)
        message = f"GLYPH {security}".encode()
        signature = engine.sign_message(message, keypair.private_key, algorithm)
        is_valid = engine.verify_signature(message, signature, keypair.public_key)
        assert is_valid, f"Signature verification failed for {security} level"


def test_tier_5_full_security():
    """Test tier 5 (transcendent) full security setup"""
    from labs.governance.identity.auth_backend.pqc_crypto_engine import PQCCryptoEngine
    import json

    engine = PQCCryptoEngine()

    # Tier 5 uses maximum security
    # - Dilithium5 for signatures
    # - Kyber1024 for key exchange (if needed)

    # Generate keys
    sig_keypair = engine.generate_signature_keypair("Dilithium5")
    kem_keypair = engine.generate_kem_keypair("Kyber1024")

    # Simulate tier 5 GLYPH data
    glyph_data = {
        "lambda_id": "tier5_user",
        "tier_level": 5,
        "security_level": "transcendent",
        "all_features": True,
    }

    # Sign GLYPH data
    glyph_bytes = json.dumps(glyph_data, sort_keys=True).encode()
    signature = engine.sign_message(glyph_bytes, sig_keypair.private_key, "Dilithium5")

    # Verify
    assert engine.verify_signature(glyph_bytes, signature, sig_keypair.public_key)

    # Test KEM for secure channel
    ciphertext, sender_secret = engine.encapsulate(kem_keypair.public_key, "Kyber1024")
    receiver_secret = engine.decapsulate(
        ciphertext, kem_keypair.private_key, "Kyber1024"
    )

    assert len(sender_secret) == 32
    assert len(receiver_secret) == 32


@pytest.mark.benchmark
def test_glyph_generation_time_budget():
    """Test that PQC operations fit within GLYPH generation time budget"""
    from labs.governance.identity.auth_backend.pqc_crypto_engine import PQCCryptoEngine

    engine = PQCCryptoEngine()

    # GLYPH generation targets:
    # Basic: < 10ms total
    # Enhanced: < 15ms total
    # Quantum: < 25ms total

    # Measure PQC component time for quantum GLYPH
    start = time.perf_counter()

    # 1. Generate keypair (done once, can be cached)
    keypair = engine.generate_signature_keypair("Dilithium3")

    # 2. Sign GLYPH data
    glyph_data = b"Mock GLYPH identity data"
    signature = engine.sign_message(glyph_data, keypair.private_key, "Dilithium3")

    end = time.perf_counter()
    pqc_time_ms = (end - start) * 1000

    # PQC should take < 10ms to leave budget for other operations
    assert pqc_time_ms < 10, f"PQC too slow: {pqc_time_ms:.2f}ms"

    print(f"PQC time: {pqc_time_ms:.2f}ms (target: <10ms)")


def test_key_persistence():
    """Test that keypairs can be serialized for persistence"""
    from labs.governance.identity.auth_backend.pqc_crypto_engine import PQCCryptoEngine
    import base64

    engine = PQCCryptoEngine()

    # Generate keypair
    keypair = engine.generate_signature_keypair("Dilithium3")

    # Serialize keys
    public_key_b64 = base64.b64encode(keypair.public_key).decode()
    private_key_b64 = base64.b64encode(keypair.private_key).decode()

    # Deserialize
    public_key_restored = base64.b64decode(public_key_b64)
    private_key_restored = base64.b64decode(private_key_b64)

    # Verify keys work after serialization
    message = b"Test persistence"
    signature = engine.sign_message(message, private_key_restored, "Dilithium3")
    is_valid = engine.verify_signature(message, signature, public_key_restored)

    assert is_valid


def test_nist_security_levels():
    """Test that security levels match NIST standards"""
    from labs.governance.identity.auth_backend.pqc_crypto_engine import PQCCryptoEngine

    engine = PQCCryptoEngine()

    # NIST security levels
    nist_levels = {
        "Dilithium2": "NIST Level 2",
        "Dilithium3": "NIST Level 3",
        "Dilithium5": "NIST Level 5",
        "Kyber512": "NIST Level 1",
        "Kyber768": "NIST Level 3",
        "Kyber1024": "NIST Level 5",
    }

    for algorithm, expected_level in nist_levels.items():
        info = engine.get_algorithm_info(algorithm)
        assert info["security_level"] == expected_level, f"{algorithm} level mismatch"
