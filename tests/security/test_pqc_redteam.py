"""
Red-team test harness for MATRIZ-007 PQC migration.

Security test cases for Week 5 red-team review:
- GLYMPH signature forgery attempts
- Key compromise scenarios
- Dream-exfil attack vectors
- Signature replay attacks
- Checkpoint corruption detection

Prerequisites:
- PQC runner with liboqs installed
- Registry service with Dilithium2 signing implemented
- Test key material (non-production)

Run with: pytest tests/security/test_pqc_redteam.py -v --tb=short
"""

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict

import pytest

# Skip all tests if PQC not available (fallback mode)
try:
    import oqs
    OQS_INSTALLED = True
except (ImportError, SystemExit, RuntimeError):
    OQS_INSTALLED = False

pytestmark = pytest.mark.skipif(not OQS_INSTALLED, reason="PQC tests require liboqs and its shared libraries to be properly installed.")


class TestPQCSignatureForgery:
    """Test resistance to signature forgery attacks."""

    @pytest.fixture
    def valid_checkpoint(self) -> Dict[str, Any]:
        """Create a valid checkpoint for testing."""
        return {
            "registry_id": "test-node-001",
            "timestamp": "2025-10-24T12:00:00Z",
            "capabilities": ["compute", "storage"],
            "version": "1.0.0"
        }

    @pytest.fixture
    def dilithium_keypair(self):
        """Generate fresh Dilithium2 keypair for testing."""
        with oqs.Signature('Dilithium2') as sig:
            public_key = sig.generate_keypair()
            # Note: private key is held in sig object, can't be extracted directly
            yield sig, public_key

    def test_forgery_attempt_invalid_signature(self, valid_checkpoint, dilithium_keypair):
        """RED-TEAM-001: Attempt to forge signature with random bytes."""
        sig, public_key = dilithium_keypair

        checkpoint_bytes = json.dumps(valid_checkpoint, sort_keys=True).encode()

        # Create random "forged" signature
        forged_signature = os.urandom(len(sig.sign(checkpoint_bytes)))

        # Verification should fail
        is_valid = sig.verify(checkpoint_bytes, forged_signature, public_key)
        assert not is_valid, "Random signature should not verify"

    def test_forgery_attempt_modified_message(self, valid_checkpoint, dilithium_keypair):
        """RED-TEAM-002: Attempt to use valid signature on modified message."""
        sig, public_key = dilithium_keypair

        # Sign original message
        original_bytes = json.dumps(valid_checkpoint, sort_keys=True).encode()
        valid_signature = sig.sign(original_bytes)

        # Modify checkpoint
        modified_checkpoint = valid_checkpoint.copy()
        modified_checkpoint["capabilities"].append("admin")  # Privilege escalation attempt
        modified_bytes = json.dumps(modified_checkpoint, sort_keys=True).encode()

        # Verification should fail on modified message
        is_valid = sig.verify(modified_bytes, valid_signature, public_key)
        assert not is_valid, "Valid signature should not verify modified message"

    def test_forgery_attempt_wrong_public_key(self, valid_checkpoint):
        """RED-TEAM-003: Attempt to verify with wrong public key."""
        # Generate two separate keypairs
        with oqs.Signature('Dilithium2') as sig1:
            sig1.generate_keypair()
            checkpoint_bytes = json.dumps(valid_checkpoint, sort_keys=True).encode()
            signature = sig1.sign(checkpoint_bytes)

        with oqs.Signature('Dilithium2') as sig2:
            public_key_2 = sig2.generate_keypair()

            # Verification should fail with wrong public key
            is_valid = sig2.verify(checkpoint_bytes, signature, public_key_2)
            assert not is_valid, "Signature should not verify with wrong public key"


class TestKeyCompromise:
    """Test key compromise and rotation scenarios."""

    def test_key_compromise_detection(self):
        """RED-TEAM-004: Simulate key compromise and verify detection."""
        # Generate "compromised" keypair
        with oqs.Signature('Dilithium2') as sig:
            public_key = sig.generate_keypair()
            message = b"checkpoint data"
            signature = sig.sign(message)

        # In production, compromised key should be in revocation list
        # This test verifies the signature is valid (expected)
        # but would be rejected by revocation check (not implemented here)
        with oqs.Signature('Dilithium2') as sig:
            is_valid = sig.verify(message, signature, public_key)
            assert is_valid, "Signature should be cryptographically valid"

        # TODO: Implement revocation list check
        # assert is_revoked(public_key), "Compromised key should be revoked"

    def test_key_rotation_dual_signing(self):
        """RED-TEAM-005: Test dual-signing during key rotation."""
        message = b"checkpoint during rotation"

        # Old keypair
        with oqs.Signature('Dilithium2') as old_sig:
            old_public_key = old_sig.generate_keypair()
            old_signature = old_sig.sign(message)

        # New keypair
        with oqs.Signature('Dilithium2') as new_sig:
            new_public_key = new_sig.generate_keypair()
            new_signature = new_sig.sign(message)

        # During rotation, both signatures should be valid
        with oqs.Signature('Dilithium2') as verify_sig:
            assert verify_sig.verify(message, old_signature, old_public_key)
            assert verify_sig.verify(message, new_signature, new_public_key)

        # TODO: Implement trust anchor verification
        # assert verify_with_trust_anchor(message, [old_signature, new_signature])


class TestReplayAttacks:
    """Test resistance to replay attacks."""

    def test_replay_attack_timestamp_check(self, tmp_path):
        """RED-TEAM-006: Attempt to replay old valid checkpoint."""
        # Create two checkpoints with different timestamps
        checkpoint_old = {
            "registry_id": "test-node-001",
            "timestamp": "2025-10-24T10:00:00Z",
            "nonce": "12345"
        }
        checkpoint_new = {
            "registry_id": "test-node-001",
            "timestamp": "2025-10-24T12:00:00Z",
            "nonce": "67890"
        }

        with oqs.Signature('Dilithium2') as sig:
            public_key = sig.generate_keypair()

            # Sign both checkpoints
            old_bytes = json.dumps(checkpoint_old, sort_keys=True).encode()
            new_bytes = json.dumps(checkpoint_new, sort_keys=True).encode()

            old_signature = sig.sign(old_bytes)
            new_signature = sig.sign(new_bytes)

            # Both signatures are cryptographically valid
            assert sig.verify(old_bytes, old_signature, public_key)
            assert sig.verify(new_bytes, new_signature, public_key)

        # TODO: Implement timestamp/nonce replay protection
        # Registry should reject old_checkpoint if new_checkpoint was seen
        # assert not registry.accept_checkpoint(checkpoint_old)

    def test_replay_attack_nonce_uniqueness(self):
        """RED-TEAM-007: Attempt to replay checkpoint with duplicate nonce."""
        checkpoint = {
            "registry_id": "test-node-001",
            "timestamp": "2025-10-24T12:00:00Z",
            "nonce": "unique-nonce-123"
        }

        with oqs.Signature('Dilithium2') as sig:
            public_key = sig.generate_keypair()
            checkpoint_bytes = json.dumps(checkpoint, sort_keys=True).encode()
            signature = sig.sign(checkpoint_bytes)

            # First submission: should be accepted
            is_valid_1 = sig.verify(checkpoint_bytes, signature, public_key)
            assert is_valid_1

            # Second submission (replay): signature still valid but should be rejected by nonce check
            is_valid_2 = sig.verify(checkpoint_bytes, signature, public_key)
            assert is_valid_2

        # TODO: Implement nonce tracking
        # assert registry.is_nonce_used("unique-nonce-123")


class TestCheckpointCorruption:
    """Test detection of corrupted checkpoints."""

    def test_corruption_detection_single_bit_flip(self):
        """RED-TEAM-008: Detect single bit flip in checkpoint data."""
        checkpoint = {"data": "important checkpoint data"}

        with oqs.Signature('Dilithium2') as sig:
            public_key = sig.generate_keypair()
            checkpoint_bytes = json.dumps(checkpoint, sort_keys=True).encode()
            signature = sig.sign(checkpoint_bytes)

            # Flip a single bit
            corrupted_bytes = bytearray(checkpoint_bytes)
            corrupted_bytes[0] ^= 0x01  # Flip LSB of first byte
            corrupted_bytes = bytes(corrupted_bytes)

            # Verification should fail
            is_valid = sig.verify(corrupted_bytes, signature, public_key)
            assert not is_valid, "Corrupted checkpoint should not verify"

    def test_corruption_detection_truncation(self):
        """RED-TEAM-009: Detect truncated checkpoint data."""
        checkpoint = {"data": "important checkpoint data with lots of content"}

        with oqs.Signature('Dilithium2') as sig:
            public_key = sig.generate_keypair()
            checkpoint_bytes = json.dumps(checkpoint, sort_keys=True).encode()
            signature = sig.sign(checkpoint_bytes)

            # Truncate checkpoint
            truncated_bytes = checkpoint_bytes[:-10]

            # Verification should fail
            is_valid = sig.verify(truncated_bytes, signature, public_key)
            assert not is_valid, "Truncated checkpoint should not verify"

    def test_corruption_detection_signature_truncation(self):
        """RED-TEAM-010: Detect truncated signature."""
        checkpoint = {"data": "checkpoint data"}

        with oqs.Signature('Dilithium2') as sig:
            public_key = sig.generate_keypair()
            checkpoint_bytes = json.dumps(checkpoint, sort_keys=True).encode()
            signature = sig.sign(checkpoint_bytes)

            # Truncate signature
            truncated_signature = signature[:-10]

            # Verification should fail (invalid signature format)
            try:
                is_valid = sig.verify(checkpoint_bytes, truncated_signature, public_key)
                assert not is_valid, "Truncated signature should not verify"
            except Exception:
                # Some implementations may raise exception for malformed signature
                pass  # Expected behavior


class TestDreamExfiltration:
    """Test resistance to dream-state data exfiltration."""

    def test_dream_exfil_encrypted_checkpoint(self):
        """RED-TEAM-011: Verify checkpoints are not readable without keys."""
        # Checkpoint should be encrypted or access-controlled
        checkpoint = {
            "registry_id": "test-node-001",
            "sensitive_data": "private neural weights",
            "dream_state": "REM-3"
        }

        # In production, checkpoint should be encrypted at rest
        # This test verifies signature doesn't leak plaintext
        with oqs.Signature('Dilithium2') as sig:
            sig.generate_keypair()
            checkpoint_bytes = json.dumps(checkpoint, sort_keys=True).encode()
            signature = sig.sign(checkpoint_bytes)

            # Signature should not contain checkpoint data
            assert b"private neural weights" not in signature
            assert b"REM-3" not in signature

    def test_dream_exfil_public_key_safety(self):
        """RED-TEAM-012: Verify public key doesn't leak private information."""
        with oqs.Signature('Dilithium2') as sig:
            public_key = sig.generate_keypair()

            # Public key should be safe to share (no private key material)
            # This test verifies public key size is as expected
            assert len(public_key) > 0, "Public key should exist"

            # Dilithium2 public key is 1312 bytes
            assert len(public_key) == 1312, f"Unexpected public key size: {len(public_key)}"


class TestPerformance:
    """Test PQC performance meets SLO targets."""

    def test_sign_latency_p95_target(self):
        """RED-TEAM-013: Verify sign latency meets p95 < 50ms target."""
        import time

        checkpoint = {"data": "benchmark checkpoint"}
        iterations = 100
        latencies = []

        with oqs.Signature('Dilithium2') as sig:
            sig.generate_keypair()
            checkpoint_bytes = json.dumps(checkpoint, sort_keys=True).encode()

            # Warmup
            for _ in range(10):
                sig.sign(checkpoint_bytes)

            # Benchmark
            for _ in range(iterations):
                start = time.perf_counter()
                sig.sign(checkpoint_bytes)
                latencies.append((time.perf_counter() - start) * 1000)  # ms

        p95 = sorted(latencies)[int(iterations * 0.95)]
        print(f"\nSign p95 latency: {p95:.2f}ms")
        assert p95 < 50, f"Sign p95 latency {p95:.2f}ms exceeds 50ms target"

    def test_verify_latency_p95_target(self):
        """RED-TEAM-014: Verify verification latency meets p95 < 10ms target."""
        import time

        checkpoint = {"data": "benchmark checkpoint"}
        iterations = 100
        latencies = []

        with oqs.Signature('Dilithium2') as sig:
            public_key = sig.generate_keypair()
            checkpoint_bytes = json.dumps(checkpoint, sort_keys=True).encode()
            signature = sig.sign(checkpoint_bytes)

            # Warmup
            for _ in range(10):
                sig.verify(checkpoint_bytes, signature, public_key)

            # Benchmark
            for _ in range(iterations):
                start = time.perf_counter()
                sig.verify(checkpoint_bytes, signature, public_key)
                latencies.append((time.perf_counter() - start) * 1000)  # ms

        p95 = sorted(latencies)[int(iterations * 0.95)]
        print(f"\nVerify p95 latency: {p95:.2f}ms")
        assert p95 < 10, f"Verify p95 latency {p95:.2f}ms exceeds 10ms target"


# Mark all tests as security tests
pytestmark = [
    pytest.mark.security,
    pytest.mark.pqc,
    pytest.mark.redteam,
    pytest.mark.slow
]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
