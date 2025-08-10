"""
Integration tests for Enterprise Authentication System
Tests for Agent 1 Task 3: identity/enterprise/auth.py integration
"""

import json
import sys
import tempfile
from pathlib import Path

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from identity.enterprise.auth import (
    AuthenticationMethod,
    AuthenticationResult,
    AuthenticationStatus,
    EnterpriseAuthenticationModule,
    EnterpriseUser,
    LDAPConfiguration,
    OAuthConfiguration,
    SAMLConfiguration,
    UserRole,
    get_enterprise_auth_config_template,
)


class TestEnterpriseAuthIntegration:
    """Test suite for enterprise authentication system integration"""

    def test_authentication_enums(self):
        """Test authentication enumeration completeness"""
        # Test AuthenticationMethod enum
        assert hasattr(AuthenticationMethod, "SAML_SSO")
        assert hasattr(AuthenticationMethod, "OAUTH2_OIDC")
        assert hasattr(AuthenticationMethod, "LDAP")
        assert hasattr(AuthenticationMethod, "ACTIVE_DIRECTORY")
        assert hasattr(AuthenticationMethod, "JWT_TOKEN")
        assert hasattr(AuthenticationMethod, "MFA_TOTP")
        assert hasattr(AuthenticationMethod, "MFA_SMS")
        assert hasattr(AuthenticationMethod, "MFA_EMAIL")
        assert hasattr(AuthenticationMethod, "CERTIFICATE")

        # Test UserRole enum
        assert hasattr(UserRole, "ADMIN")
        assert hasattr(UserRole, "MANAGER")
        assert hasattr(UserRole, "USER")
        assert hasattr(UserRole, "VIEWER")
        assert hasattr(UserRole, "AUDITOR")
        assert hasattr(UserRole, "DEVELOPER")
        assert hasattr(UserRole, "INTEGRATOR")

        # Test AuthenticationStatus enum
        assert hasattr(AuthenticationStatus, "SUCCESS")
        assert hasattr(AuthenticationStatus, "FAILED")
        assert hasattr(AuthenticationStatus, "MFA_REQUIRED")
        assert hasattr(AuthenticationStatus, "EXPIRED")
        assert hasattr(AuthenticationStatus, "LOCKED")
        assert hasattr(AuthenticationStatus, "SUSPENDED")

    def test_configuration_template(self):
        """Test configuration template generation"""
        config = get_enterprise_auth_config_template()

        assert isinstance(config, dict)
        assert "authentication_methods" in config
        assert "session_timeout_hours" in config
        assert "jwt_secret" in config
        assert "mfa_enabled" in config
        assert "providers" in config

        # Test provider configurations
        providers = config["providers"]
        assert "oauth" in providers
        assert "ldap" in providers
        assert "saml" in providers

        # Test OAuth config structure
        oauth_config = providers["oauth"]
        assert "client_id" in oauth_config
        assert "authorization_url" in oauth_config
        assert "token_url" in oauth_config

        # Test LDAP config structure
        ldap_config = providers["ldap"]
        assert "server_uri" in ldap_config
        assert "user_base_dn" in ldap_config
        assert "attribute_mapping" in ldap_config

    def test_enterprise_auth_module_initialization(self):
        """Test enterprise authentication module initialization"""
        # Test with default configuration
        auth_module = EnterpriseAuthenticationModule()

        assert hasattr(auth_module, "config")
        assert hasattr(auth_module, "encryption_key")
        assert hasattr(auth_module, "jwt_secret")
        assert hasattr(auth_module, "mfa_enabled")
        assert hasattr(auth_module, "active_sessions")
        assert hasattr(auth_module, "user_cache")

    def test_configuration_loading(self):
        """Test configuration loading from file"""
        # Create temporary config file
        test_config = {
            "authentication_methods": ["ldap", "oauth2_oidc"],
            "session_timeout_hours": 12,
            "mfa_enabled": False,
            "jwt_algorithm": "HS512",
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(test_config, f)
            config_path = f.name

        try:
            auth_module = EnterpriseAuthenticationModule(config_path)
            assert auth_module.config["session_timeout_hours"] == 12
            assert auth_module.config["mfa_enabled"] == False
            assert auth_module.config["jwt_algorithm"] == "HS512"
        finally:
            Path(config_path).unlink()

    def test_authentication_method_support(self):
        """Test authentication method handling"""
        auth_module = EnterpriseAuthenticationModule()

        # Test that authenticate_user method exists and has proper signature
        assert hasattr(auth_module, "authenticate_user")

        # Test method signature by inspecting
        import inspect

        sig = inspect.signature(auth_module.authenticate_user)
        params = list(sig.parameters.keys())

        assert "username" in params
        assert "authentication_method" in params

    def test_configuration_structures(self):
        """Test configuration data structure classes"""
        # Test SAMLConfiguration
        saml_config = SAMLConfiguration(
            entity_id="test-entity",
            sso_url="https://test.com/sso",
            sls_url="https://test.com/sls",
            x509_cert="test-cert",
            private_key="test-key",
            attribute_mapping={"username": "nameID"},
            name_id_format="email",
            sign_requests=True,
            encrypt_assertions=False,
        )

        assert saml_config.entity_id == "test-entity"
        assert saml_config.sign_requests == True

        # Test OAuthConfiguration
        oauth_config = OAuthConfiguration(
            client_id="test-client",
            client_secret="test-secret",
            authorization_url="https://test.com/auth",
            token_url="https://test.com/token",
            userinfo_url="https://test.com/userinfo",
            jwks_url="https://test.com/jwks",
            scope=["openid", "profile"],
            redirect_uri="https://app.com/callback",
            response_type="code",
            grant_type="authorization_code",
        )

        assert oauth_config.client_id == "test-client"
        assert "openid" in oauth_config.scope

        # Test LDAPConfiguration
        ldap_config = LDAPConfiguration(
            server_uri="ldaps://test.com:636",
            bind_dn="cn=admin,dc=test,dc=com",
            bind_password="password",
            user_base_dn="ou=users,dc=test,dc=com",
            user_filter="(uid={username})",
            group_base_dn="ou=groups,dc=test,dc=com",
            group_filter="(member={user_dn})",
            attribute_mapping={"username": "uid"},
            use_ssl=True,
            ca_cert_file=None,
            timeout=30,
        )

        assert ldap_config.use_ssl == True
        assert ldap_config.timeout == 30

    def test_enterprise_user_structure(self):
        """Test enterprise user data structure"""
        from datetime import datetime

        user = EnterpriseUser(
            user_id="test-123",
            username="testuser",
            email="test@example.com",
            display_name="Test User",
            department="IT",
            roles=[UserRole.USER, UserRole.DEVELOPER],
            lambda_id="lambda-abc-123",
            authentication_methods=[
                AuthenticationMethod.LDAP,
                AuthenticationMethod.MFA_TOTP,
            ],
            last_login=datetime.now(),
            created_at=datetime.now(),
            updated_at=datetime.now(),
            is_active=True,
            requires_mfa=True,
            ldap_dn="uid=testuser,ou=users,dc=company,dc=com",
            employee_id="EMP001",
            manager_id="MGR001",
            security_clearance="Level 2",
            attributes={"custom_field": "value"},
        )

        assert user.username == "testuser"
        assert UserRole.USER in user.roles
        assert user.requires_mfa == True
        assert user.attributes["custom_field"] == "value"

    def test_authentication_result_structure(self):
        """Test authentication result data structure"""
        from datetime import datetime

        result = AuthenticationResult(
            status=AuthenticationStatus.SUCCESS,
            user=None,  # Would contain EnterpriseUser in real scenario
            access_token="jwt-token-here",
            refresh_token="refresh-token",
            expires_at=datetime.now(),
            mfa_token=None,
            lambda_id="lambda-id",
            permissions=["read", "write"],
            session_id="session-123",
            error_message=None,
            metadata={"source": "ldap"},
        )

        assert result.status == AuthenticationStatus.SUCCESS
        assert result.access_token == "jwt-token-here"
        assert "read" in result.permissions
        assert result.metadata["source"] == "ldap"

    def test_core_method_availability(self):
        """Test that all core methods are available"""
        auth_module = EnterpriseAuthenticationModule()

        # Test public methods
        assert hasattr(auth_module, "authenticate_user")

        # Test private methods that are part of the integration
        assert hasattr(auth_module, "_load_config")
        assert hasattr(auth_module, "_initialize_encryption")
        assert hasattr(auth_module, "_load_authentication_providers")

    def test_integration_completeness(self):
        """Test that all required integration points are satisfied"""
        # Verify all required classes are importable
        classes_to_test = [
            AuthenticationMethod,
            UserRole,
            AuthenticationStatus,
            EnterpriseUser,
            AuthenticationResult,
            SAMLConfiguration,
            OAuthConfiguration,
            LDAPConfiguration,
            EnterpriseAuthenticationModule,
        ]

        for cls in classes_to_test:
            assert cls is not None

        # Verify function is importable
        assert callable(get_enterprise_auth_config_template)

    def test_session_management(self):
        """Test session management capabilities"""
        auth_module = EnterpriseAuthenticationModule()

        # Test session storage exists
        assert hasattr(auth_module, "active_sessions")
        assert isinstance(auth_module.active_sessions, dict)

        # Test user cache exists
        assert hasattr(auth_module, "user_cache")
        assert isinstance(auth_module.user_cache, dict)

    def test_security_features(self):
        """Test security feature availability"""
        auth_module = EnterpriseAuthenticationModule()

        # Test encryption is initialized
        assert hasattr(auth_module, "encryption_key")
        assert auth_module.encryption_key is not None

        # Test JWT configuration
        assert hasattr(auth_module, "jwt_secret")
        assert hasattr(auth_module, "jwt_algorithm")
        assert hasattr(auth_module, "token_expiry_hours")

        # Test MFA configuration
        assert hasattr(auth_module, "mfa_enabled")
        assert hasattr(auth_module, "mfa_required_roles")


if __name__ == "__main__":
    # Run basic integration test
    pytest.main([__file__, "-v"])
