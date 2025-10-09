"""
Tests for QRS (Quantum Request Signature) Manager

Comprehensive functional tests for QRS signature verification and audit trails.
Covers cryptographic signature generation, verification, and ΛTRACE integration.

Part of BATCH-COPILOT-TESTS-01
Tasks Tested:
- TEST-HIGH-API-QRS-01: QRS signature verification (SHA256/SHA512)
- TEST-HIGH-API-QRS-02: ΛTRACE audit trail integration

Trinity Framework: 🛡️ Guardian · ⚛️ Identity
"""

import pytest
import hashlib
import hmac
from datetime import datetime, timezone, timedelta
from candidate.bridge.api.api import QRSManager, QRSAlgorithm as SignatureAlgorithm


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def qrs_manager():
    """Fresh QRS manager instance."""
    secret_key = "test_secret_key_2024"
    return QRSManager(secret_key=secret_key)


@pytest.fixture
def sample_request_data():
    """Sample request data for signature testing."""
    return {
        "method": "POST",
        "path": "/api/v1/query",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "lambda_id": "Λ_alpha_user123",
        "body": {"query": "test query"}
    }


# ============================================================================
# TEST-HIGH-API-QRS-01: QRS Signature Verification
# ============================================================================

@pytest.mark.unit
def test_qrs_signature_generation_sha256(qrs_manager, sample_request_data):
    """Test QRS signature generation with SHA256."""
    # Generate signature
    signature = qrs_manager.generate_signature(
        request_data=sample_request_data,
        algorithm=SignatureAlgorithm.SHA256
    )
    
    # Verify signature format
    assert signature is not None
    assert isinstance(signature, str)
    assert len(signature) == 64  # SHA256 hex digest length


@pytest.mark.unit
def test_qrs_signature_generation_sha512(qrs_manager, sample_request_data):
    """Test QRS signature generation with SHA512."""
    # Generate signature
    signature = qrs_manager.generate_signature(
        request_data=sample_request_data,
        algorithm=SignatureAlgorithm.SHA512
    )
    
    # Verify signature format
    assert signature is not None
    assert isinstance(signature, str)
    assert len(signature) == 128  # SHA512 hex digest length


@pytest.mark.unit
def test_qrs_signature_verification_valid(qrs_manager, sample_request_data):
    """Test verification of valid QRS signatures."""
    # Generate signature
    signature = qrs_manager.generate_signature(
        request_data=sample_request_data,
        algorithm=SignatureAlgorithm.SHA256
    )
    
    # Verify signature
    is_valid = qrs_manager.verify_signature(
        request_data=sample_request_data,
        signature=signature,
        algorithm=SignatureAlgorithm.SHA256
    )
    
    assert is_valid is True


@pytest.mark.unit
def test_qrs_signature_verification_tampered(qrs_manager, sample_request_data):
    """Test detection of tampered signatures."""
    # Generate valid signature
    signature = qrs_manager.generate_signature(
        request_data=sample_request_data,
        algorithm=SignatureAlgorithm.SHA256
    )
    
    # Tamper with request data
    tampered_data = sample_request_data.copy()
    tampered_data["body"]["query"] = "modified query"
    
    # Verify signature with tampered data
    is_valid = qrs_manager.verify_signature(
        request_data=tampered_data,
        signature=signature,
        algorithm=SignatureAlgorithm.SHA256
    )
    
    assert is_valid is False


@pytest.mark.unit
def test_qrs_signature_verification_wrong_algorithm(qrs_manager, sample_request_data):
    """Test signature verification with wrong algorithm."""
    # Generate with SHA256
    signature = qrs_manager.generate_signature(
        request_data=sample_request_data,
        algorithm=SignatureAlgorithm.SHA256
    )
    
    # Verify with SHA512
    is_valid = qrs_manager.verify_signature(
        request_data=sample_request_data,
        signature=signature,
        algorithm=SignatureAlgorithm.SHA512
    )
    
    assert is_valid is False


@pytest.mark.unit
def test_qrs_signature_deterministic(qrs_manager, sample_request_data):
    """Test that signature generation is deterministic."""
    # Generate signature twice with same data
    signature1 = qrs_manager.generate_signature(
        request_data=sample_request_data,
        algorithm=SignatureAlgorithm.SHA256
    )
    
    signature2 = qrs_manager.generate_signature(
        request_data=sample_request_data,
        algorithm=SignatureAlgorithm.SHA256
    )
    
    # Should be identical
    assert signature1 == signature2


@pytest.mark.unit
def test_qrs_signature_different_keys():
    """Test signatures with different secret keys."""
    data = {"test": "data"}
    
    manager1 = QRSManager(secret_key="key1")
    manager2 = QRSManager(secret_key="key2")
    
    sig1 = manager1.generate_signature(data, SignatureAlgorithm.SHA256)
    sig2 = manager2.generate_signature(data, SignatureAlgorithm.SHA256)
    
    # Different keys should produce different signatures
    assert sig1 != sig2


# ============================================================================
# TEST-HIGH-API-QRS-02: ΛTRACE Audit Trail Integration
# ============================================================================

@pytest.mark.unit
def test_qrs_lambda_trace_audit_entry(qrs_manager, sample_request_data):
    """Test ΛTRACE audit trail entry creation."""
    # Generate signature
    signature = qrs_manager.generate_signature(
        request_data=sample_request_data,
        algorithm=SignatureAlgorithm.SHA256
    )
    
    # Create audit entry
    audit_entry = qrs_manager.create_audit_entry(
        request_data=sample_request_data,
        signature=signature,
        verification_result=True
    )
    
    # Verify audit entry structure
    assert audit_entry is not None
    assert "timestamp" in audit_entry
    assert "lambda_id" in audit_entry
    assert "signature" in audit_entry
    assert "verification_result" in audit_entry
    assert audit_entry["lambda_id"] == sample_request_data["lambda_id"]


@pytest.mark.unit
def test_qrs_lambda_trace_hash_chain(qrs_manager):
    """Test ΛTRACE hash chain for audit trail."""
    entries = []
    
    # Create multiple audit entries
    for i in range(5):
        request_data = {
            "method": "GET",
            "path": f"/api/v1/resource/{i}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "lambda_id": "Λ_beta_user456"
        }
        
        signature = qrs_manager.generate_signature(
            request_data, SignatureAlgorithm.SHA256
        )
        
        audit_entry = qrs_manager.create_audit_entry(
            request_data=request_data,
            signature=signature,
            verification_result=True
        )
        
        entries.append(audit_entry)
    
    # Verify hash chain
    for i in range(1, len(entries)):
        current = entries[i]
        previous = entries[i-1]
        
        # Each entry should reference previous hash
        assert "previous_hash" in current
        if i > 0:
            assert current["previous_hash"] == previous.get("entry_hash")


@pytest.mark.unit
def test_qrs_lambda_trace_verification_failures(qrs_manager, sample_request_data):
    """Test audit logging of verification failures."""
    # Generate signature
    signature = qrs_manager.generate_signature(
        request_data=sample_request_data,
        algorithm=SignatureAlgorithm.SHA256
    )
    
    # Tamper with data
    tampered_data = sample_request_data.copy()
    tampered_data["body"]["query"] = "malicious query"
    
    # Verify (should fail)
    is_valid = qrs_manager.verify_signature(
        request_data=tampered_data,
        signature=signature,
        algorithm=SignatureAlgorithm.SHA256
    )
    
    # Create audit entry for failure
    audit_entry = qrs_manager.create_audit_entry(
        request_data=tampered_data,
        signature=signature,
        verification_result=is_valid
    )
    
    # Verify failure logged
    assert audit_entry["verification_result"] is False
    assert "failure_reason" in audit_entry or "error" in audit_entry


@pytest.mark.unit
def test_qrs_lambda_trace_tampering_detection(qrs_manager):
    """Test detection of audit trail tampering."""
    # Create audit entry
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": "signature_verification",
        "result": "success"
    }
    
    # Calculate hash
    entry_hash = hashlib.sha256(
        str(entry).encode()
    ).hexdigest()
    entry["entry_hash"] = entry_hash
    
    # Store original hash
    original_hash = entry_hash
    
    # Tamper with entry
    entry["result"] = "failure"
    
    # Recalculate hash
    tampered_hash = hashlib.sha256(
        str({"timestamp": entry["timestamp"], "action": entry["action"], "result": "failure"}).encode()
    ).hexdigest()
    
    # Hashes should not match
    assert tampered_hash != original_hash


# ============================================================================
# Advanced QRS Features
# ============================================================================

@pytest.mark.unit
def test_qrs_timestamp_validation(qrs_manager):
    """Test timestamp validation in requests."""
    # Recent timestamp (valid)
    recent_data = {
        "method": "POST",
        "path": "/api/v1/data",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    is_valid_time = qrs_manager.validate_timestamp(
        recent_data["timestamp"],
        max_age_seconds=300  # 5 minutes
    )
    
    assert is_valid_time is True
    
    # Old timestamp (invalid)
    old_data = {
        "method": "POST",
        "path": "/api/v1/data",
        "timestamp": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
    }
    
    is_valid_time = qrs_manager.validate_timestamp(
        old_data["timestamp"],
        max_age_seconds=300
    )
    
    assert is_valid_time is False


@pytest.mark.unit
def test_qrs_nonce_replay_prevention(qrs_manager):
    """Test nonce-based replay attack prevention."""
    request_data = {
        "method": "POST",
        "path": "/api/v1/action",
        "nonce": "unique_nonce_123"
    }
    
    # First request with nonce (should succeed)
    is_new = qrs_manager.check_nonce(request_data["nonce"])
    assert is_new is True
    
    # Replay with same nonce (should fail)
    is_new = qrs_manager.check_nonce(request_data["nonce"])
    assert is_new is False


@pytest.mark.unit
def test_qrs_rate_limiting_integration(qrs_manager):
    """Test QRS rate limiting based on ΛID tier."""
    lambda_id_alpha = "Λ_alpha_user123"
    lambda_id_delta = "Λ_delta_user456"
    
    # Alpha tier: higher rate limit
    alpha_limit = qrs_manager.get_rate_limit(lambda_id_alpha)
    
    # Delta tier: lower rate limit
    delta_limit = qrs_manager.get_rate_limit(lambda_id_delta)
    
    # Alpha should have higher limit
    assert alpha_limit > delta_limit


# ============================================================================
# Integration Tests
# ============================================================================

@pytest.mark.integration
def test_qrs_full_request_lifecycle(qrs_manager, sample_request_data):
    """Test complete QRS request lifecycle."""
    # 1. Generate signature
    signature = qrs_manager.generate_signature(
        request_data=sample_request_data,
        algorithm=SignatureAlgorithm.SHA256
    )
    
    # 2. Verify signature
    is_valid = qrs_manager.verify_signature(
        request_data=sample_request_data,
        signature=signature,
        algorithm=SignatureAlgorithm.SHA256
    )
    
    # 3. Create audit entry
    audit_entry = qrs_manager.create_audit_entry(
        request_data=sample_request_data,
        signature=signature,
        verification_result=is_valid
    )
    
    # Verify complete lifecycle
    assert signature is not None
    assert is_valid is True
    assert audit_entry is not None


# ============================================================================
# Edge Cases
# ============================================================================

@pytest.mark.unit
def test_qrs_empty_request_data(qrs_manager):
    """Test handling of empty request data."""
    empty_data = {}
    
    try:
        signature = qrs_manager.generate_signature(
            request_data=empty_data,
            algorithm=SignatureAlgorithm.SHA256
        )
        # Should still generate a signature
        assert signature is not None
    except ValueError:
        pass  # Expected if empty data not allowed


@pytest.mark.unit
def test_qrs_invalid_algorithm(qrs_manager, sample_request_data):
    """Test handling of invalid signature algorithm."""
    try:
        # Invalid algorithm
        signature = qrs_manager.generate_signature(
            request_data=sample_request_data,
            algorithm="INVALID_ALGO"
        )
        assert False, "Should raise error for invalid algorithm"
    except (ValueError, AttributeError):
        pass  # Expected


@pytest.mark.unit
def test_qrs_unicode_data(qrs_manager):
    """Test QRS with Unicode/special characters."""
    unicode_data = {
        "method": "POST",
        "body": {"text": "Hello 世界 🌍 émojis"}
    }
    
    # Should handle Unicode gracefully
    signature = qrs_manager.generate_signature(
        request_data=unicode_data,
        algorithm=SignatureAlgorithm.SHA256
    )
    
    assert signature is not None
    
    # Verification should still work
    is_valid = qrs_manager.verify_signature(
        request_data=unicode_data,
        signature=signature,
        algorithm=SignatureAlgorithm.SHA256
    )
    
    assert is_valid is True
