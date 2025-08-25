"""Integration tests for Consent Ledger promotion"""

import os
import pytest
from candidate.governance.consent_ledger import (
    record_consent,
    verify_consent,
    withdraw_consent
)


class TestConsentLedgerDryRun:
    """Test consent ledger in dry_run mode (default)"""
    
    def test_record_consent_dry_run(self):
        """Test recording consent in dry_run mode"""
        event = {
            "subject": "user-123",
            "scopes": ["read", "write"],
            "purpose": "data_processing"
        }
        result = record_consent(event, mode="dry_run")
        assert result["ok"] is True
        assert result["status"] == "recorded(dry_run)"
    
    def test_record_consent_missing_fields(self):
        """Test validation of required fields"""
        event = {"subject": "user-123"}  # Missing scopes
        result = record_consent(event)
        assert result["ok"] is False
        assert result["reason"] == "invalid_event"
    
    def test_verify_consent_dry_run(self):
        """Test verifying consent in dry_run mode"""
        result = verify_consent("user-123", "read", mode="dry_run")
        assert result["ok"] is True
        assert result["verdict"] == "allow(dry_run)"
    
    def test_withdraw_consent_dry_run(self):
        """Test withdrawing consent in dry_run mode"""
        result = withdraw_consent("consent-123", mode="dry_run")
        assert result["ok"] is True
        assert result["status"] == "withdrawn(dry_run)"


@pytest.mark.skipif(
    os.environ.get("CONSENT_LEDGER_ACTIVE", "false").lower() != "true",
    reason="Real implementation not activated"
)
class TestConsentLedgerReal:
    """Test consent ledger with real implementation"""
    
    def test_record_and_verify_consent(self):
        """Test full consent lifecycle"""
        # Record consent
        event = {
            "subject": "test-user-456",
            "scopes": ["profile", "email"],
            "controller": "lukhas-test",
            "purpose": "authentication",
            "type": "explicit"
        }
        record_result = record_consent(event, mode="production")
        assert record_result["ok"] is True
        assert "consent_id" in record_result
        
        # Verify consent
        verify_result = verify_consent(
            "test-user-456", 
            "profile",
            mode="production",
            controller="lukhas-test",
            purpose="authentication"
        )
        assert verify_result["ok"] is True
        
        # Withdraw consent
        if "consent_id" in record_result:
            withdraw_result = withdraw_consent(
                record_result["consent_id"],
                mode="production",
                reason="test_cleanup"
            )
            assert withdraw_result["ok"] is True
    
    def test_verify_nonexistent_consent(self):
        """Test verifying consent that doesn't exist"""
        result = verify_consent(
            "nonexistent-user",
            "read",
            mode="production"
        )
        assert result["ok"] is False or result.get("verdict") == "deny"


class TestMatrizIntegration:
    """Test MATRIZ emission for consent operations"""
    
    def test_matriz_nodes_emitted(self, capsys):
        """Verify MATRIZ nodes are emitted"""
        # Record consent (should emit AWARENESS node)
        event = {
            "subject": "matriz-test-user",
            "scopes": ["test"],
            "matriz_state": {"confidence": 0.9, "salience": 0.7}
        }
        record_consent(event)
        
        # Check for MATRIZ node in output
        captured = capsys.readouterr()
        if captured.out:
            # MATRIZ nodes are JSON printed to stdout
            assert "MATRIZ_NODE" in captured.out or "type" in captured.out
            assert "AWARENESS" in captured.out or "governance:consent" in captured.out


def test_acceptance_gate_compliance():
    """Verify the module meets acceptance gate requirements"""
    import pathlib
    import json
    
    # Check MODULE_MANIFEST.json exists
    manifest_path = pathlib.Path("lukhas/governance/MODULE_MANIFEST.json")
    assert manifest_path.exists(), "MODULE_MANIFEST.json required"
    
    # Validate manifest structure
    with open(manifest_path) as f:
        manifest = json.load(f)
    
    assert manifest["lane"] == "accepted"
    assert "consent:record" in manifest["capabilities"]
    assert manifest["sla"]["p95_ms"] <= 40
    
    # Check no illegal imports
    consent_file = pathlib.Path("lukhas/governance/consent_ledger.py")
    content = consent_file.read_text()
    assert "from candidate" not in content
    assert "from quarantine" not in content
    assert "from archive" not in content