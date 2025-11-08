#!/usr/bin/env python3
"""
Tests for T4/0.01% Guardian Decision Envelope System.

- ED25519 cryptographic signing
- SHA-256 integrity hashing
- JSONSchema validation
- Decision serialization/deserialization
- Signature verification
"""
import base64
import hashlib
import json
import logging
import os
import sys
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from lukhas_website.lukhas.governance.guardian_system import (
    ActorType,
    DecisionStatus,
    EnforcementMode,
    EthicalSeverity,
    GuardianAudit,
    GuardianContext,
    GuardianDecision,
    GuardianEnforcement,
    GuardianJSONEncoder,
    GuardianMetrics,
    GuardianSubject,
    GuardianSystem,
    RuntimeEnvironment,
    create_simple_decision,
)

# A real, valid 32-byte Ed25519 private key, base64 encoded.
MOCK_PRIVATE_KEY_B64 = "a" * 43 + "="
MOCK_PUBLIC_KEY_B64 = "E" * 43 + "=" # This is just a placeholder for the mock
MOCK_SIGNATURE = b"mock_signature_bytes"

# Mock for jsonschema library
MOCK_SCHEMA = {"type": "object", "properties": {"schema_version": {"type": "string"}}}


@pytest.fixture
def mock_crypto(monkeypatch):
    """Fixture to mock the cryptography library."""
    monkeypatch.setattr("lukhas_website.lukhas.governance.guardian_system.CRYPTO_AVAILABLE", True)
    mock_ed25519 = MagicMock()
    mock_private_key = MagicMock()
    mock_public_key = MagicMock()
    mock_private_key.sign.return_value = MOCK_SIGNATURE
    mock_private_key.public_key.return_value = mock_public_key
    mock_public_key.public_bytes.return_value = base64.b64decode(MOCK_PUBLIC_KEY_B64)
    mock_ed25519.Ed25519PrivateKey.from_private_bytes.return_value = mock_private_key

    monkeypatch.setattr("lukhas_website.lukhas.governance.guardian_system.ed25519", mock_ed25519)
    return mock_ed25519


@pytest.fixture
def mock_jsonschema(monkeypatch):
    """Fixture to mock the jsonschema library."""
    monkeypatch.setattr("lukhas_website.lukhas.governance.guardian_system.SCHEMA_VALIDATION", True)
    mock_validate = MagicMock()
    monkeypatch.setattr("lukhas_website.lukhas.governance.guardian_system.jsonschema.validate", mock_validate)
    return mock_validate


@pytest.fixture
def guardian_components():
    """Provides a set of Guardian components for building a decision."""
    now_iso = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    return {
        "decision": GuardianDecision(
            status=DecisionStatus.ALLOW,
            policy="test/v1",
            timestamp=now_iso,
            confidence=0.99,
            ttl_seconds=300,
        ),
        "subject": GuardianSubject(
            correlation_id="test-corr-id",
            actor_type=ActorType.USER,
            actor_id="user-123",
            operation_name="test_op",
            lane="blue",
            canary_percent=10.0,
            actor_tier="premium",
            operation_resource="/test/resource",
            operation_parameters={"key": "value"},
        ),
        "context": GuardianContext(
            region="us-west-2",
            runtime=RuntimeEnvironment.STAGING,
            version="1.2.3",
            kill_switch_path="/features/off",
        ),
        "metrics": GuardianMetrics(
            latency_ms=12.5,
            risk_score=0.1,
            drift_score=0.05,
            quota_remaining=999,
            counters={"invocations": 1},
        ),
        "enforcement": GuardianEnforcement(
            mode=EnforcementMode.ENFORCED,
            actions=["log", "alert"],
        ),
        "audit": GuardianAudit(
            event_id="evt-abc",
            timestamp=now_iso,
            source_system="test_harness",
            audit_trail=[{"step": "one"}],
        ),
        "reasons": [{"code": "policy_ok"}],
        "rule_evaluations": [{"rule": "rule1", "result": "pass"}],
        "approvals": [{"approver": "boss"}],
        "redactions": {"field": "removed"},
        "extensions": {"custom": "data"},
        "debug": {"trace_id": "trace-xyz"},
    }

@pytest.fixture
def minimal_guardian_components():
    """Provides a minimal set of Guardian components with no optional fields."""
    now_iso = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    return {
        "decision": GuardianDecision(status=DecisionStatus.ALLOW, policy="test/v1", timestamp=now_iso),
        "subject": GuardianSubject(
            correlation_id="test-corr-id", actor_type=ActorType.USER, actor_id="user-123", operation_name="test_op"
        ),
        "context": GuardianContext(region="us-west-2", runtime=RuntimeEnvironment.STAGING),
        "metrics": GuardianMetrics(latency_ms=12.5),
        "enforcement": GuardianEnforcement(mode=EnforcementMode.ENFORCED),
        "audit": GuardianAudit(event_id="evt-abc", timestamp=now_iso),
    }

@pytest.fixture
def guardian_system_with_key():
    """GuardianSystem instance with a signing key."""
    return GuardianSystem(signing_key=MOCK_PRIVATE_KEY_B64)


@pytest.fixture
def guardian_system_no_key():
    """GuardianSystem instance without a signing key."""
    return GuardianSystem()


class TestGuardianSystem:
    """Test suite for the GuardianSystem decision envelope methods."""

    def test_serialize_decision_full(self, guardian_system_with_key, guardian_components, mock_crypto, mock_jsonschema):
        """Verify serialization of a decision with all optional fields."""
        system = guardian_system_with_key
        system.schema = MOCK_SCHEMA  # manually set schema for test

        envelope = system.serialize_decision(**guardian_components)

        assert "confidence" in envelope["decision"]
        assert "lane" in envelope["subject"]
        assert "tier" in envelope["subject"]["actor"]
        assert "version" in envelope["context"]["environment"]
        assert "risk_score" in envelope["metrics"]
        assert "actions" in envelope["enforcement"]
        assert "source_system" in envelope["audit"]
        assert "reasons" in envelope
        mock_crypto.Ed25519PrivateKey.from_private_bytes.assert_called_once()
        mock_jsonschema.assert_called_once()

    def test_serialize_decision_minimal(self, guardian_system_no_key, minimal_guardian_components, mock_jsonschema):
        """Verify serialization with only required fields and no optional values."""
        system = guardian_system_no_key
        system.schema = MOCK_SCHEMA

        envelope = system.serialize_decision(**minimal_guardian_components)

        assert "signature" not in envelope["integrity"]
        assert "confidence" not in envelope["decision"]
        assert "lane" not in envelope["subject"]
        assert "tier" not in envelope["subject"]["actor"]
        assert "version" not in envelope["context"]["environment"]
        assert "risk_score" not in envelope["metrics"]
        assert "actions" not in envelope["enforcement"]
        assert "source_system" not in envelope["audit"]
        assert "reasons" not in envelope
        mock_jsonschema.assert_called_once()

    def test_compute_integrity_with_signing(self, guardian_system_with_key, mock_crypto):
        """Verify integrity block creation with a signature."""
        system = guardian_system_with_key
        test_envelope = {"data": "test"}

        integrity = system._compute_integrity(test_envelope)

        assert "content_sha256" in integrity
        assert "signature" in integrity
        mock_crypto.Ed25519PrivateKey.from_private_bytes.assert_called_once()

    def test_compute_integrity_signing_failure(self, guardian_system_with_key, mock_crypto, caplog):
        """Test graceful failure when signing raises an exception."""
        system = guardian_system_with_key
        mock_crypto.Ed25519PrivateKey.from_private_bytes.side_effect = Exception("Key error")

        with caplog.at_level(logging.ERROR):
            integrity = system._compute_integrity({"data": "test"})
            assert "signature" not in integrity
            assert "Failed to sign Guardian envelope" in caplog.text

    def test_sign_content(self, guardian_system_with_key, mock_crypto):
        """Test the core signing logic."""
        system = guardian_system_with_key
        content = b'{"data":"test"}'

        signature_block = system._sign_content(content)

        assert signature_block["alg"] == "ed25519"

        private_key_mock = mock_crypto.Ed25519PrivateKey.from_private_bytes.return_value
        private_key_mock.sign.assert_called_with(content)

    def test_sign_content_crypto_unavailable(self, guardian_system_with_key, monkeypatch):
        """Verify signing raises error if crypto is unavailable."""
        monkeypatch.setattr("lukhas_website.lukhas.governance.guardian_system.CRYPTO_AVAILABLE", False)
        system = guardian_system_with_key
        with pytest.raises(RuntimeError, match="cryptography library required for signing"):
            system._sign_content(b"test")

    def test_verify_integrity_success(self, guardian_system_with_key, guardian_components, mock_crypto):
        """Test successful integrity verification."""
        system = guardian_system_with_key
        envelope = system.serialize_decision(**guardian_components)

        with patch.object(system, '_verify_signature', return_value=True) as mock_verify_sig:
            assert system.verify_integrity(envelope) is True
            mock_verify_sig.assert_called_once()

    def test_verify_integrity_tampered_data(self, guardian_system_no_key, guardian_components):
        """Test integrity verification failure on tampered data."""
        system = guardian_system_no_key
        envelope = system.serialize_decision(**guardian_components)
        envelope["decision"]["status"] = "denied"
        assert system.verify_integrity(envelope) is False

    def test_verify_integrity_invalid_signature(self, guardian_system_with_key, guardian_components, mock_crypto):
        """Test integrity verification failure on invalid signature."""
        system = guardian_system_with_key
        envelope = system.serialize_decision(**guardian_components)

        with patch.object(system, '_verify_signature', return_value=False) as mock_verify_sig:
            assert system.verify_integrity(envelope) is False
            mock_verify_sig.assert_called_once()

    def test_verify_integrity_missing_hash(self, guardian_system_no_key, guardian_components):
        """Test integrity verification failure with missing hash."""
        system = guardian_system_no_key
        envelope = system.serialize_decision(**guardian_components)
        del envelope["integrity"]["content_sha256"]
        assert system.verify_integrity(envelope) is False

    def test_verify_integrity_exception(self, guardian_system_no_key, guardian_components, caplog):
        """Test that verify_integrity returns False on exception."""
        system = guardian_system_no_key
        envelope = system.serialize_decision(**guardian_components)

        with patch("hashlib.sha256", side_effect=Exception("hash error")):
            with caplog.at_level(logging.ERROR):
                assert system.verify_integrity(envelope) is False
                assert "Guardian integrity verification error" in caplog.text

    def test_verify_signature_placeholder_logic(self, guardian_system_no_key):
        """Test the placeholder logic of _verify_signature."""
        system = guardian_system_no_key
        signature = {"alg": "ed25519", "kid": "test-key", "sig": "abc"}
        assert system._verify_signature(b"content", signature) is True

    def test_verify_signature_unsupported_alg(self, guardian_system_no_key):
        """Test signature verification with an unsupported algorithm."""
        system = guardian_system_no_key
        signature = {"alg": "unsupported", "kid": "test-key", "sig": "abc"}
        assert system._verify_signature(b"content", signature) is False

    def test_verify_signature_exception(self, guardian_system_no_key, caplog):
        """Test that _verify_signature returns False on exception."""
        system = guardian_system_no_key
        signature = {"alg": "ed25519", "kid": "test-key"}
        with patch("lukhas_website.lukhas.governance.guardian_system.logger.info", side_effect=Exception("mocked exception")):
            with caplog.at_level(logging.ERROR):
                assert not system._verify_signature(b"content", signature)
                assert "Signature verification error" in caplog.text

    def test_validate_envelope_success(self, guardian_system_no_key, mock_jsonschema):
        """Test successful schema validation."""
        system = guardian_system_no_key
        system.schema = MOCK_SCHEMA
        envelope = {"schema_version": "2.1.0"}
        assert system._validate_envelope(envelope) is True
        mock_jsonschema.assert_called_with(instance=envelope, schema=MOCK_SCHEMA)

    def test_validate_envelope_failure(self, guardian_system_no_key, mock_jsonschema):
        """Test schema validation failure."""
        from jsonschema import ValidationError
        system = guardian_system_no_key
        system.schema = MOCK_SCHEMA
        mock_jsonschema.side_effect = ValidationError("Test error")
        with pytest.raises(ValueError, match="Guardian envelope validation failed: Test error"):
            system._validate_envelope({})

    def test_validate_envelope_disabled(self, guardian_system_no_key, mock_jsonschema, monkeypatch):
        """Test that validation is skipped when disabled."""
        monkeypatch.setattr("lukhas_website.lukhas.governance.guardian_system.SCHEMA_VALIDATION", False)
        system = GuardianSystem()
        system._validate_envelope({})
        mock_jsonschema.assert_not_called()

    def test_is_decision_allow_success(self, guardian_system_no_key, guardian_components):
        """Test is_decision_allow for an 'allow' status."""
        system = guardian_system_no_key
        envelope = system.serialize_decision(**guardian_components)
        assert system.is_decision_allow(envelope) is True

    @pytest.mark.parametrize("status", [
        DecisionStatus.DENY, DecisionStatus.CHALLENGE, DecisionStatus.QUARANTINE, DecisionStatus.ERROR, "unknown"
    ])
    def test_is_decision_allow_fail_closed_statuses(self, guardian_system_no_key, guardian_components, status):
        """Test that non-'allow' statuses result in False."""
        system = guardian_system_no_key
        guardian_components["decision"].status = status if isinstance(status, DecisionStatus) else DecisionStatus.ALLOW
        envelope = system.serialize_decision(**guardian_components)
        if not isinstance(status, DecisionStatus):
             envelope["decision"]["status"] = status
        assert system.is_decision_allow(envelope) is False

    def test_is_decision_allow_integrity_failure(self, guardian_system_no_key, guardian_components):
        """Test that an integrity failure leads to a 'deny'."""
        system = guardian_system_no_key
        envelope = system.serialize_decision(**guardian_components)
        envelope["decision"]["status"] = "tampered"
        assert system.is_decision_allow(envelope) is False

    def test_is_decision_allow_enforcement_disabled(self, guardian_system_no_key, guardian_components):
        """Test that disabled enforcement always allows."""
        system = guardian_system_no_key
        guardian_components["decision"].status = DecisionStatus.DENY
        guardian_components["context"].enforcement_enabled = False
        envelope = system.serialize_decision(**guardian_components)
        assert system.is_decision_allow(envelope) is True

    def test_is_decision_allow_emergency_active(self, guardian_system_no_key, guardian_components):
        """Test that emergency mode always denies."""
        system = guardian_system_no_key
        guardian_components["context"].emergency_active = True
        envelope = system.serialize_decision(**guardian_components)
        assert system.is_decision_allow(envelope) is False

    def test_is_decision_allow_exception(self, guardian_system_no_key, guardian_components, caplog):
        """Test that is_decision_allow returns False on exception."""
        system = guardian_system_no_key
        envelope = system.serialize_decision(**guardian_components)
        with patch.object(system, 'verify_integrity', side_effect=Exception("verify error")):
             with caplog.at_level(logging.ERROR):
                assert system.is_decision_allow(envelope) is False
                assert "Guardian decision evaluation error" in caplog.text

    def test_load_schema_success(self, caplog):
        """Verify successful loading of the schema file."""
        schema_content = '{"type": "object"}'
        with patch("os.path.exists", return_value=True), \
             patch("builtins.open", MagicMock(read_data=schema_content)), \
             patch("json.load", return_value={"type": "object"}) as mock_json_load:
            with caplog.at_level(logging.INFO):
                system = GuardianSystem(schema_path="/fake/schema.json")
                assert system.schema is not None
                mock_json_load.assert_called_once()
                assert "Guardian schema loaded" in caplog.text

    def test_load_schema_failure_logs_error(self, caplog):
        """Verify that a failure to load the schema is logged."""
        with patch("os.path.exists", return_value=True), \
             patch("builtins.open", side_effect=OSError("File not found")):
            with caplog.at_level(logging.ERROR):
                GuardianSystem(schema_path="/invalid/path")
                assert "Failed to load Guardian schema" in caplog.text

    def test_json_encoder_fallback(self):
        """Test the custom JSON encoder's fallback to super().default()."""
        encoder = GuardianJSONEncoder()
        with pytest.raises(TypeError):
            encoder.default(set([1, 2, 3]))

    def test_import_fallback_crypto(self, monkeypatch):
        """Test CRYPTO_AVAILABLE is False when import fails."""
        monkeypatch.setitem(sys.modules, "cryptography.exceptions", None)
        monkeypatch.setitem(sys.modules, "cryptography.hazmat.primitives", None)
        import importlib

        import lukhas_website.lukhas.governance.guardian_system
        importlib.reload(lukhas_website.lukhas.governance.guardian_system)
        assert not lukhas_website.lukhas.governance.guardian_system.CRYPTO_AVAILABLE

    def test_import_fallback_jsonschema(self, monkeypatch):
        """Test SCHEMA_VALIDATION is False when import fails."""
        monkeypatch.setitem(sys.modules, "jsonschema", None)
        import importlib

        import lukhas_website.lukhas.governance.guardian_system
        importlib.reload(lukhas_website.lukhas.governance.guardian_system)
        assert not lukhas_website.lukhas.governance.guardian_system.SCHEMA_VALIDATION

    def test_create_simple_decision(self):
        """Test the create_simple_decision convenience function."""
        envelope = create_simple_decision(
            status=DecisionStatus.DENY,
            policy="simple/v1",
            correlation_id="corr-simple",
            actor_id="actor-simple",
            operation="op-simple"
        )
        assert envelope["decision"]["status"] == "deny"
        assert envelope["subject"]["correlation_id"] == "corr-simple"
        assert "integrity" in envelope
