"""WebAuthn Integration Tests for Lambda ID

These tests verify the WebAuthn integration interface contracts.
Since WebAuthn requires complex setup, we test the interface behavior
without requiring the full WebAuthn implementation to be active.
"""
import os
import pytest
from candidate.identity import lambda_id


class TestWebAuthnIntegration:
    """Test WebAuthn functionality interface in Lambda ID"""
    
    def test_authenticate_dry_run(self):
        """Test authentication in dry_run mode (default)"""
        result = lambda_id.authenticate("test_user")
        assert result["ok"] is True
        assert result["user"]["lid"] == "test_user"
        assert result["method"] == "dry_run"
    
    def test_authenticate_with_mode_dry_run(self):
        """Test authentication with explicit dry_run mode"""
        result = lambda_id.authenticate("test_user", mode="dry_run")
        assert result["ok"] is True
        assert result["user"]["lid"] == "test_user"
        assert result["method"] == "dry_run"
    
    def test_authenticate_invalid_lid(self):
        """Test authentication with invalid lid"""
        # Too short
        result = lambda_id.authenticate("ab", mode="dry_run")
        assert result["ok"] is False
        assert result["reason"] == "invalid_lid"
        
        # Empty
        result = lambda_id.authenticate("", mode="dry_run")
        assert result["ok"] is False
        assert result["reason"] == "invalid_lid"
        
        # Non-string (should handle gracefully)
        result = lambda_id.authenticate(None, mode="dry_run")
        assert result["ok"] is False
        assert result["reason"] == "invalid_lid"
    
    def test_register_passkey_dry_run(self):
        """Test passkey registration in dry_run mode"""
        result = lambda_id.register_passkey(
            "user_123",
            "john_doe",
            "John Doe",
            mode="dry_run"
        )
        assert result["ok"] is True
        assert result["status"] == "registration_initiated(dry_run)"
    
    def test_register_passkey_with_tier(self):
        """Test passkey registration with tier parameter"""
        result = lambda_id.register_passkey(
            "user_123",
            "john_doe",
            "John Doe",
            mode="dry_run",
            tier=5
        )
        assert result["ok"] is True
        assert result["status"] == "registration_initiated(dry_run)"
    
    def test_verify_passkey_dry_run(self):
        """Test passkey verification in dry_run mode"""
        result = lambda_id.verify_passkey(
            "reg_123",
            {"attestation": "mock_data"},
            mode="dry_run"
        )
        assert result["ok"] is True
        assert result["status"] == "verified(dry_run)"
    
    def test_list_credentials_dry_run(self):
        """Test listing credentials in dry_run mode"""
        result = lambda_id.list_credentials("user_123", mode="dry_run")
        assert result["ok"] is True
        assert result["credentials"] == []
        assert result["total"] == 0
    
    def test_revoke_credential_dry_run(self):
        """Test revoking credential in dry_run mode"""
        result = lambda_id.revoke_credential(
            "user_123",
            "cred_456",
            mode="dry_run"
        )
        assert result["ok"] is True
        assert result["status"] == "revoked(dry_run)"
    
    def test_authenticate_webauthn_inactive(self):
        """Test that WebAuthn auth falls back to dry_run when inactive"""
        # Even with WebAuthn credential, should fall back to dry_run
        credential = {
            "type": "webauthn",
            "authentication_id": "auth_123",
            "response": {"authenticatorData": "..."}
        }
        
        result = lambda_id.authenticate(
            "test_user",
            credential=credential,
            mode="live"  # Even in live mode
        )
        
        # Should fall back to dry_run since WEBAUTHN_ACTIVE is false
        assert result["ok"] is True
        assert result["method"] == "dry_run"
    
    def test_matriz_instrumentation(self):
        """Test that all methods have MATRIZ instrumentation"""
        # Check that decorators are applied (they wrap the function)
        assert hasattr(lambda_id.authenticate, "__wrapped__")
        assert hasattr(lambda_id.register_passkey, "__wrapped__")
        assert hasattr(lambda_id.verify_passkey, "__wrapped__")
        assert hasattr(lambda_id.list_credentials, "__wrapped__")
        assert hasattr(lambda_id.revoke_credential, "__wrapped__")
    
    def test_all_methods_default_to_dry_run(self):
        """Test that all methods default to dry_run mode"""
        # Authenticate
        result = lambda_id.authenticate("user_test")
        assert result["ok"] is True
        
        # Register
        result = lambda_id.register_passkey("u1", "uname", "User Name")
        assert result["ok"] is True
        assert "dry_run" in result["status"]
        
        # Verify
        result = lambda_id.verify_passkey("reg_id", {})
        assert result["ok"] is True
        assert "dry_run" in result["status"]
        
        # List
        result = lambda_id.list_credentials("u1")
        assert result["ok"] is True
        assert result["total"] == 0
        
        # Revoke
        result = lambda_id.revoke_credential("u1", "cred1")
        assert result["ok"] is True
        assert "dry_run" in result["status"]
    
    def test_module_manifest_capabilities(self):
        """Verify that MODULE_MANIFEST.json has been updated with new capabilities"""
        import json
        import pathlib
        
        manifest_path = pathlib.Path("lukhas/identity/MODULE_MANIFEST.json")
        assert manifest_path.exists()
        
        with open(manifest_path) as f:
            manifest = json.load(f)
        
        # Check new capabilities are present
        expected_capabilities = [
            "identity:auth",
            "identity:lambda-id",
            "identity:register",
            "identity:passkey",
            "identity:list",
            "identity:revoke"
        ]
        
        for cap in expected_capabilities:
            assert cap in manifest["capabilities"], f"Missing capability: {cap}"
        
        # Check MATRIZ emit points
        expected_emit_points = [
            "authenticate",
            "register_passkey",
            "verify_passkey",
            "list_credentials",
            "revoke_credential"
        ]
        
        for point in expected_emit_points:
            assert point in manifest["matriz_emit_points"], f"Missing emit point: {point}"