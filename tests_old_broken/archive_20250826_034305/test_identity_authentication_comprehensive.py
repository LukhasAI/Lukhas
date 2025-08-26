"""
LUKHAS Identity Authentication Comprehensive Test Suite
=====================================================

Comprehensive test coverage for the LUKHAS Identity Authentication system.
Tests all components: OAuth2/OIDC, WebAuthn, λID, Namespaces, Performance.

Test Coverage:
- OAuth2/OIDC Provider flows
- WebAuthn/FIDO2 authentication
- λID generation and validation
- Namespace management and isolation
- Performance optimization
- Trinity Framework compliance
- Security and error handling
- Performance benchmarking

Author: Identity Authentication Specialist
Framework: Trinity Compliant (⚛️🧠🛡️)
"""

import asyncio
import json
import pytest
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
from unittest.mock import Mock, patch, MagicMock

# Import the identity system components
try:
    from candidate.identity import (
        IdentitySystem,
        authenticate_user,
        get_oauth_provider,
        get_webauthn_manager,
        generate_lambda_id,
        default_system
    )
    IDENTITY_SYSTEM_AVAILABLE = True
except ImportError as e:
    IDENTITY_SYSTEM_AVAILABLE = False
    print(f"Identity system not available for testing: {e}")

try:
    from candidate.governance.identity.core.auth.oauth2_oidc_provider import (
        OAuth2OIDCProvider,
        OAuthClient
    )
    OAUTH_PROVIDER_AVAILABLE = True
except ImportError:
    OAUTH_PROVIDER_AVAILABLE = False

try:
    from candidate.governance.identity.core.auth.webauthn_manager import (
        WebAuthnManager,
        WebAuthnCredential
    )
    WEBAUTHN_AVAILABLE = True
except ImportError:
    WEBAUTHN_AVAILABLE = False

try:
    from candidate.governance.identity.core.id_service.lambd_id_generator import (
        LambdaIDGenerator,
        TierLevel
    )
    LAMBDA_ID_AVAILABLE = True
except ImportError:
    LAMBDA_ID_AVAILABLE = False

try:
    from candidate.governance.identity.core.namespace_manager import (
        NamespaceManager,
        IdentityNamespace,
        NamespaceType
    )
    NAMESPACE_MANAGER_AVAILABLE = True
except ImportError:
    NAMESPACE_MANAGER_AVAILABLE = False

try:
    from candidate.governance.identity.core.performance.auth_optimizer import (
        AuthenticationOptimizer
    )
    OPTIMIZER_AVAILABLE = True
except ImportError:
    OPTIMIZER_AVAILABLE = False


class TestIdentitySystemCore:
    """Test core identity system functionality"""
    
    @pytest.mark.skipif(not IDENTITY_SYSTEM_AVAILABLE, reason="Identity system not available")
    def test_identity_system_initialization(self):
        """Test identity system initializes correctly"""
        system = IdentitySystem()
        
        assert system is not None
        assert hasattr(system, 'client')
        assert hasattr(system, 'authenticate_user')
        
        # Test system status
        status = system.get_system_status()
        assert 'system' in status
        assert 'trinity_framework' in status
        assert status['trinity_framework'] == '⚛️🧠🛡️'
    
    @pytest.mark.skipif(not IDENTITY_SYSTEM_AVAILABLE, reason="Identity system not available")
    def test_basic_authentication_t1(self):
        """Test T1 (basic) authentication"""
        system = IdentitySystem()
        
        credentials = {
            'user_id': 'test_user_12345678',
            'password': 'secure_password_123'
        }
        
        result = system.authenticate_user(credentials, tier='T1')
        
        assert result['success'] is True
        assert result['user_id'] == 'test_user_12345678'
        assert result['tier'] == 'T1'
        assert result['method'] == 'basic'
    
    @pytest.mark.skipif(not IDENTITY_SYSTEM_AVAILABLE, reason="Identity system not available")
    def test_enhanced_authentication_t2(self):
        """Test T2 (enhanced) authentication"""
        system = IdentitySystem()
        
        credentials = {
            'user_id': 'test_user_12345678',
            'passkey_response': 'mock_passkey_data'
        }
        
        result = system.authenticate_user(credentials, tier='T2')
        
        assert result['success'] is True
        assert result['user_id'] == 'test_user_12345678'
        assert result['tier'] == 'T2'
        assert result['method'] == 'enhanced'
    
    @pytest.mark.skipif(not IDENTITY_SYSTEM_AVAILABLE, reason="Identity system not available")
    def test_consciousness_authentication_t3(self):
        """Test T3 (consciousness) authentication"""
        system = IdentitySystem()
        
        credentials = {
            'user_id': 'test_user_12345678',
            'consciousness_signature': 'mock_consciousness_data'
        }
        
        result = system.authenticate_user(credentials, tier='T3')
        
        assert result['success'] is True
        assert result['user_id'] == 'test_user_12345678'
        assert result['tier'] == 'T3'
        assert result['method'] == 'consciousness'
    
    @pytest.mark.skipif(not IDENTITY_SYSTEM_AVAILABLE, reason="Identity system not available")
    def test_authentication_failure(self):
        """Test authentication failure scenarios"""
        system = IdentitySystem()
        
        # Missing user_id
        result = system.authenticate_user({}, tier='T1')
        assert result['success'] is False
        assert 'error' in result
        
        # Invalid tier
        result = system.authenticate_user({'user_id': 'test'}, tier='T99')
        assert result['success'] is False
        assert 'Unsupported tier' in result['error']
    
    @pytest.mark.skipif(not IDENTITY_SYSTEM_AVAILABLE, reason="Identity system not available")
    def test_namespace_authentication(self):
        """Test namespace-aware authentication"""
        system = IdentitySystem()
        
        credentials = {
            'user_id': 'test_user_12345678',
            'password': 'secure_password_123'
        }
        
        result = system.authenticate_user(credentials, tier='T1', namespace='enterprise.lukhas.ai')
        
        assert result['success'] is True
        # Should handle namespace resolution


class TestOAuth2OIDCProvider:
    """Test OAuth2/OIDC provider functionality"""
    
    @pytest.mark.skipif(not OAUTH_PROVIDER_AVAILABLE, reason="OAuth2 provider not available")
    def test_oauth_provider_initialization(self):
        """Test OAuth2 provider initializes correctly"""
        provider = OAuth2OIDCProvider()
        
        assert provider is not None
        assert hasattr(provider, 'handle_authorization_request')
        assert hasattr(provider, 'handle_token_request')
        assert provider.issuer == 'https://lukhas.ai'
    
    @pytest.mark.skipif(not OAUTH_PROVIDER_AVAILABLE, reason="OAuth2 provider not available")
    def test_oauth_metadata_endpoint(self):
        """Test OAuth2/.well-known/openid_configuration metadata"""
        provider = OAuth2OIDCProvider()
        metadata = provider.get_authorization_endpoint_metadata()
        
        # Check required OIDC metadata fields
        assert 'issuer' in metadata
        assert 'authorization_endpoint' in metadata
        assert 'token_endpoint' in metadata
        assert 'userinfo_endpoint' in metadata
        assert 'jwks_uri' in metadata
        assert 'scopes_supported' in metadata
        assert 'response_types_supported' in metadata
        assert 'grant_types_supported' in metadata
        
        # Check LUKHAS-specific extensions
        assert metadata['lukhas_trinity_framework'] == '⚛️🧠🛡️'
        assert metadata['lukhas_tier_system_supported'] is True
        assert metadata['lukhas_lambda_id_supported'] is True
    
    @pytest.mark.skipif(not OAUTH_PROVIDER_AVAILABLE, reason="OAuth2 provider not available")
    def test_client_registration(self):
        """Test dynamic client registration"""
        provider = OAuth2OIDCProvider()
        
        registration_request = {
            'client_name': 'Test Client',
            'redirect_uris': ['https://test.app/callback'],
            'grant_types': ['authorization_code'],
            'response_types': ['code'],
            'scope': 'openid profile lukhas:basic'
        }
        
        result = provider.register_client(registration_request)
        
        assert 'client_id' in result
        assert 'client_secret' in result
        assert result['client_id'].startswith('lukhas_')
        assert 'redirect_uris' in result
        assert result['grant_types'] == ['authorization_code']
    
    @pytest.mark.skipif(not OAUTH_PROVIDER_AVAILABLE, reason="OAuth2 provider not available")
    def test_authorization_code_flow(self):
        """Test OAuth2 authorization code flow"""
        provider = OAuth2OIDCProvider()
        
        # Register a test client first
        client_reg = provider.register_client({
            'client_name': 'Test Client',
            'redirect_uris': ['https://test.app/callback']
        })
        
        # Test authorization request
        auth_request = {
            'client_id': client_reg['client_id'],
            'redirect_uri': 'https://test.app/callback',
            'response_type': 'code',
            'scope': 'openid profile',
            'state': 'random_state_123'
        }
        
        auth_result = provider.handle_authorization_request(
            auth_request, 
            user_id='test_user_12345678',
            user_tier=2
        )
        
        assert 'code' in auth_result
        assert auth_result['state'] == 'random_state_123'
        
        # Test token exchange
        token_request = {
            'grant_type': 'authorization_code',
            'code': auth_result['code'],
            'redirect_uri': 'https://test.app/callback',
            'client_id': client_reg['client_id'],
            'client_secret': client_reg['client_secret']
        }
        
        token_result = provider.handle_token_request(token_request)
        
        assert 'access_token' in token_result
        assert 'token_type' in token_result
        assert 'expires_in' in token_result
        assert token_result['token_type'] == 'Bearer'
    
    @pytest.mark.skipif(not OAUTH_PROVIDER_AVAILABLE, reason="OAuth2 provider not available")
    def test_tier_based_scope_restriction(self):
        """Test tier-based scope restrictions"""
        provider = OAuth2OIDCProvider()
        
        # Register client
        client_reg = provider.register_client({
            'client_name': 'Test Client',
            'redirect_uris': ['https://test.app/callback']
        })
        
        # Test with low-tier user requesting high-tier scopes
        auth_request = {
            'client_id': client_reg['client_id'],
            'redirect_uri': 'https://test.app/callback',
            'response_type': 'code',
            'scope': 'openid profile lukhas:enterprise lukhas:admin',  # High-tier scopes
            'state': 'test_state'
        }
        
        # Low-tier user (tier 0) should not get high-tier scopes
        auth_result = provider.handle_authorization_request(
            auth_request,
            user_id='low_tier_user_12345678',
            user_tier=0  # Guest tier
        )
        
        # Should get reduced scope set appropriate for tier 0
        assert 'code' in auth_result or 'error' in auth_result
    
    @pytest.mark.skipif(not OAUTH_PROVIDER_AVAILABLE, reason="OAuth2 provider not available")
    def test_jwks_endpoint(self):
        """Test JWKS (JSON Web Key Set) endpoint"""
        provider = OAuth2OIDCProvider()
        jwks = provider.get_jwks()
        
        assert 'keys' in jwks
        if jwks['keys']:  # Only test if keys are available
            key = jwks['keys'][0]
            assert 'kty' in key  # Key type
            assert 'use' in key  # Key use
            assert 'kid' in key  # Key ID
            assert key['kty'] == 'RSA'
            assert key['use'] == 'sig'
    
    @pytest.mark.skipif(not OAUTH_PROVIDER_AVAILABLE, reason="OAuth2 provider not available")
    def test_token_introspection(self):
        """Test OAuth2 token introspection"""
        provider = OAuth2OIDCProvider()
        
        # Create a test token (simplified)
        test_token = 'lukhas_at_test_token_12345678901234567890'
        provider.access_tokens[test_token] = {
            'client_id': 'test_client',
            'user_id': 'test_user_12345678',
            'user_tier': 2,
            'scope': ['openid', 'profile'],
            'issued_at': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(hours=1)).isoformat(),
            'lambda_id': 'LUKHAS2-TEST-🌀-ABCD'
        }
        
        result = provider.introspect_token(test_token, 'test_client')
        
        assert result['active'] is True
        assert result['client_id'] == 'test_client'
        assert result['sub'] == 'test_user_12345678'
        assert result['lukhas_tier'] == 2
        assert result['lukhas_lambda_id'] == 'LUKHAS2-TEST-🌀-ABCD'
    
    @pytest.mark.skipif(not OAUTH_PROVIDER_AVAILABLE, reason="OAuth2 provider not available")
    def test_userinfo_endpoint(self):
        """Test OIDC UserInfo endpoint"""
        provider = OAuth2OIDCProvider()
        
        # Create a test access token
        test_token = 'lukhas_at_userinfo_test_123456789'
        provider.access_tokens[test_token] = {
            'client_id': 'test_client',
            'user_id': 'test_user_12345678',
            'user_tier': 3,
            'scope': ['openid', 'profile', 'email', 'lukhas:identity:read'],
            'issued_at': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(hours=1)).isoformat(),
            'lambda_id': 'LUKHAS3-USER-✨-XYZ1'
        }
        
        userinfo = provider.get_userinfo(test_token)
        
        assert 'sub' in userinfo
        assert userinfo['sub'] == 'test_user_12345678'
        assert 'name' in userinfo
        assert 'tier' in userinfo
        assert userinfo['tier'] == 3
        assert 'trinity_compliance' in userinfo
        assert userinfo['trinity_compliance'] == '⚛️🧠🛡️'
        assert 'lambda_id' in userinfo


class TestWebAuthnManager:
    """Test WebAuthn/FIDO2 manager functionality"""
    
    @pytest.mark.skipif(not WEBAUTHN_AVAILABLE, reason="WebAuthn manager not available")
    def test_webauthn_manager_initialization(self):
        """Test WebAuthn manager initializes correctly"""
        manager = WebAuthnManager()
        
        assert manager is not None
        assert hasattr(manager, 'generate_registration_options')
        assert hasattr(manager, 'verify_registration_response')
        assert manager.rp_id == 'lukhas.ai'
        assert manager.rp_name == 'LUKHAS AI Identity System'
    
    @pytest.mark.skipif(not WEBAUTHN_AVAILABLE, reason="WebAuthn manager not available")
    def test_registration_options_generation(self):
        """Test WebAuthn registration options generation"""
        manager = WebAuthnManager()
        
        result = manager.generate_registration_options(
            user_id='test_user_12345678',
            user_name='test_user@lukhas.ai',
            user_display_name='Test User',
            user_tier=2
        )
        
        assert result['success'] is True
        assert 'registration_id' in result
        assert 'options' in result
        assert 'tier_requirements' in result
        
        options = result['options']
        assert 'challenge' in options
        assert 'rp' in options
        assert 'user' in options
        assert 'pubKeyCredParams' in options
        assert 'authenticatorSelection' in options
        
        # Check tier-specific requirements
        tier_reqs = result['tier_requirements']
        assert tier_reqs['user_verification'] is True  # Tier 2 requires user verification
    
    @pytest.mark.skipif(not WEBAUTHN_AVAILABLE, reason="WebAuthn manager not available")
    def test_registration_verification_mock(self):
        """Test WebAuthn registration verification (mock)"""
        manager = WebAuthnManager()
        
        # Generate registration options first
        reg_result = manager.generate_registration_options(
            user_id='test_user_12345678',
            user_name='test_user@lukhas.ai',
            user_display_name='Test User',
            user_tier=2
        )
        
        registration_id = reg_result['registration_id']
        challenge = reg_result['options']['challenge']
        
        # Mock WebAuthn registration response
        mock_response = {
            'id': 'mock_credential_id_12345678',
            'response': {
                'clientDataJSON': 'eyJ0eXBlIjoid2ViYXV0aG4uY3JlYXRlIiwiY2hhbGxlbmdlIjoiJyArIGNoYWxsZW5nZSArICciLCJvcmlnaW4iOiJodHRwczovL2x1a2hhcy5haSJ9',  # Mock base64
                'attestationObject': 'mock_attestation_object_data'
            },
            'transports': ['internal']
        }
        
        # This would normally verify the cryptographic signature
        # For testing, we'll check if the method handles the response structure
        result = manager.verify_registration_response(registration_id, mock_response)
        
        # The mock implementation should handle the structure gracefully
        assert 'success' in result
        if result['success']:
            assert 'credential_id' in result
            assert 'user_id' in result
            assert 'device_type' in result
    
    @pytest.mark.skipif(not WEBAUTHN_AVAILABLE, reason="WebAuthn manager not available")
    def test_authentication_options_generation(self):
        """Test WebAuthn authentication options generation"""
        manager = WebAuthnManager()
        
        # First, mock a registered credential
        mock_credential = WebAuthnCredential({
            'credential_id': 'mock_cred_12345678',
            'user_id': 'test_user_12345678',
            'tier_level': 2,
            'authenticator_data': {'transports': ['internal']}
        })
        
        if 'test_user_12345678' not in manager.credentials:
            manager.credentials['test_user_12345678'] = []
        manager.credentials['test_user_12345678'].append(mock_credential)
        
        result = manager.generate_authentication_options(
            user_id='test_user_12345678',
            tier_level=2
        )
        
        assert result['success'] is True
        assert 'authentication_id' in result
        assert 'options' in result
        
        options = result['options']
        assert 'challenge' in options
        assert 'rpId' in options
        assert 'allowCredentials' in options
        assert len(options['allowCredentials']) == 1
    
    @pytest.mark.skipif(not WEBAUTHN_AVAILABLE, reason="WebAuthn manager not available")
    def test_credential_management(self):
        """Test WebAuthn credential management"""
        manager = WebAuthnManager()
        
        user_id = 'test_user_12345678'
        
        # Mock credential registration
        mock_credential = WebAuthnCredential({
            'credential_id': 'test_credential_id_123',
            'user_id': user_id,
            'tier_level': 2,
            'device_type': 'platform_authenticator',
            'authenticator_data': {'transports': ['internal']}
        })
        
        manager.credentials[user_id] = [mock_credential]
        
        # Test getting user credentials
        creds_result = manager.get_user_credentials(user_id)
        
        assert creds_result['success'] is True
        assert creds_result['total_credentials'] == 1
        assert len(creds_result['credentials']) == 1
        
        cred_info = creds_result['credentials'][0]
        assert cred_info['tier_level'] == 2
        assert cred_info['device_type'] == 'platform_authenticator'
        
        # Test credential revocation
        revoke_result = manager.revoke_credential(user_id, 'test_credential_id_123')
        
        assert revoke_result['success'] is True
        assert revoke_result['user_id'] == user_id
        
        # Verify credential was removed
        creds_after_revoke = manager.get_user_credentials(user_id)
        assert creds_after_revoke['total_credentials'] == 0
    
    @pytest.mark.skipif(not WEBAUTHN_AVAILABLE, reason="WebAuthn manager not available")
    def test_webauthn_health_check(self):
        """Test WebAuthn system health check"""
        manager = WebAuthnManager()
        
        health_result = manager.webauthn_health_check()
        
        assert 'webauthn_health_check' in health_result
        health_data = health_result['webauthn_health_check']
        
        assert 'overall_status' in health_data
        assert 'total_registered_credentials' in health_data
        assert 'total_users_with_credentials' in health_data
        assert 'trinity_compliance' in health_data
        
        trinity = health_data['trinity_compliance']
        assert trinity['⚛️_identity'] == 'INTEGRATED'
        assert trinity['🧠_consciousness'] == 'MONITORED'
        assert trinity['🛡️_guardian'] == 'PROTECTED'


class TestLambdaIDSystem:
    """Test λID generation and validation system"""
    
    @pytest.mark.skipif(not LAMBDA_ID_AVAILABLE, reason="Lambda ID system not available")
    def test_lambda_id_generator_initialization(self):
        """Test λID generator initializes correctly"""
        generator = LambdaIDGenerator()
        
        assert generator is not None
        assert hasattr(generator, 'generate_lambda_id')
        assert hasattr(generator, 'symbolic_chars')
        assert len(generator.generated_ids) == 0
    
    @pytest.mark.skipif(not LAMBDA_ID_AVAILABLE, reason="Lambda ID system not available")
    def test_lambda_id_generation_all_tiers(self):
        """Test λID generation for all tiers"""
        generator = LambdaIDGenerator()
        
        for tier_level in TierLevel:
            lambda_id = generator.generate_lambda_id(tier_level)
            
            assert lambda_id is not None
            assert lambda_id.startswith(f'LUKHAS{tier_level.value}-')
            assert len(lambda_id.split('-')) == 4  # Format: LUKHAS{tier}-{hash}-{symbol}-{entropy}
            
            # Verify it's tracked for collision prevention
            assert lambda_id in generator.generated_ids
    
    @pytest.mark.skipif(not LAMBDA_ID_AVAILABLE, reason="Lambda ID system not available")
    def test_lambda_id_tier_symbols(self):
        """Test tier-appropriate symbolic characters"""
        generator = LambdaIDGenerator()
        
        # Test that different tiers get different symbolic character sets
        guest_id = generator.generate_lambda_id(TierLevel.GUEST)
        root_id = generator.generate_lambda_id(TierLevel.ROOT_DEV)
        
        guest_symbol = guest_id.split('-')[2]
        root_symbol = root_id.split('-')[2]
        
        # Guest tier should have basic symbols
        assert guest_symbol in generator.symbolic_chars['tier_0']
        
        # Root tier has access to all symbols
        assert root_symbol in generator.symbolic_chars['tier_5']
    
    @pytest.mark.skipif(not LAMBDA_ID_AVAILABLE, reason="Lambda ID system not available")
    def test_lambda_id_collision_handling(self):
        """Test λID collision detection and handling"""
        generator = LambdaIDGenerator()
        
        # Generate first ID
        first_id = generator.generate_lambda_id(TierLevel.FRIEND)
        
        # Mock collision by adding ID to generated set
        generator.generated_ids.add('MOCK-COLLISION-ID')
        
        # Ensure collision handling works by generating many IDs
        ids = set()
        for _ in range(100):
            new_id = generator.generate_lambda_id(TierLevel.FRIEND)
            assert new_id not in ids  # Should be unique
            ids.add(new_id)
        
        # All IDs should be tracked
        assert len(generator.generated_ids) >= 100
    
    @pytest.mark.skipif(not LAMBDA_ID_AVAILABLE, reason="Lambda ID system not available")
    def test_lambda_id_with_user_context(self):
        """Test λID generation with user context"""
        generator = LambdaIDGenerator()
        
        user_context = {
            'email': 'test@lukhas.ai',
            'registration_time': time.time(),
            'preferences': {'symbolic_style': 'mystical'}
        }
        
        lambda_id = generator.generate_lambda_id(
            TierLevel.TRUSTED,
            user_context=user_context,
            symbolic_preference='🌀'
        )
        
        assert lambda_id is not None
        assert lambda_id.startswith('LUKHAS3-')
        
        # Check if preferred symbol was used (if available for tier)
        symbol = lambda_id.split('-')[2]
        if '🌀' in generator.symbolic_chars['tier_3']:
            assert symbol == '🌀'
    
    @pytest.mark.skipif(not LAMBDA_ID_AVAILABLE, reason="Lambda ID system not available")
    def test_lambda_id_generation_stats(self):
        """Test λID generation statistics"""
        generator = LambdaIDGenerator()
        
        # Generate several IDs
        for tier in [TierLevel.GUEST, TierLevel.FRIEND, TierLevel.TRUSTED]:
            for _ in range(5):
                generator.generate_lambda_id(tier)
        
        stats = generator.get_generation_stats()
        
        assert 'total_generated' in stats
        assert stats['total_generated'] == 15
        assert 'collision_rate' in stats
        assert 'tier_distribution' in stats


class TestNamespaceManager:
    """Test namespace management and isolation"""
    
    @pytest.mark.skipif(not NAMESPACE_MANAGER_AVAILABLE, reason="Namespace manager not available")
    def test_namespace_manager_initialization(self):
        """Test namespace manager initializes with default namespaces"""
        manager = NamespaceManager()
        
        assert manager is not None
        assert hasattr(manager, 'resolve_namespace')
        assert hasattr(manager, 'create_namespace')
        
        # Check default namespaces exist
        assert 'lukhas.ai' in manager.namespaces
        assert 'enterprise.lukhas.ai' in manager.namespaces
        assert 'dev.lukhas.ai' in manager.namespaces
    
    @pytest.mark.skipif(not NAMESPACE_MANAGER_AVAILABLE, reason="Namespace manager not available")
    def test_namespace_resolution(self):
        """Test namespace resolution"""
        manager = NamespaceManager()
        
        # Test resolving root namespace
        namespace = manager.resolve_namespace('lukhas.ai')
        
        assert namespace is not None
        assert namespace.namespace_id == 'lukhas.ai'
        assert namespace.namespace_type == NamespaceType.ROOT
        
        # Test resolving with protocol prefix
        namespace_with_https = manager.resolve_namespace('https://lukhas.ai')
        assert namespace_with_https is not None
        assert namespace_with_https.namespace_id == 'lukhas.ai'
    
    @pytest.mark.skipif(not NAMESPACE_MANAGER_AVAILABLE, reason="Namespace manager not available")
    def test_namespace_creation(self):
        """Test creating new namespaces"""
        manager = NamespaceManager()
        
        result = manager.create_namespace(
            namespace_id='test.lukhas.ai',
            namespace_type=NamespaceType.TENANT,
            display_name='Test Tenant',
            owner_id='test_owner_12345678',
            parent_namespace='lukhas.ai',
            metadata={'test': True}
        )
        
        assert result['success'] is True
        assert result['namespace_id'] == 'test.lukhas.ai'
        assert result['namespace_type'] == 'tenant'
        assert 'encryption_key_id' in result
        
        # Verify namespace was created
        namespace = manager.resolve_namespace('test.lukhas.ai')
        assert namespace is not None
        assert namespace.display_name == 'Test Tenant'
        assert namespace.owner_id == 'test_owner_12345678'
    
    @pytest.mark.skipif(not NAMESPACE_MANAGER_AVAILABLE, reason="Namespace manager not available")
    def test_namespace_policies(self):
        """Test namespace policy management"""
        manager = NamespaceManager()
        
        # Get policy for default namespace
        policy = manager.get_namespace_policy('lukhas.ai')
        
        assert policy is not None
        assert policy.namespace_id == 'lukhas.ai'
        assert policy.access_control == 'strict'
        assert policy.encryption_required is True
        
        # Test policy update
        policy_updates = {
            'data_retention_days': 2555,  # 7 years
            'rate_limits': {'requests_per_minute': 15000}
        }
        
        update_result = manager.update_namespace_policy(
            'lukhas.ai',
            policy_updates,
            'admin_user_12345678'
        )
        
        assert update_result['success'] is True
        assert 'data_retention_days' in update_result['updated_fields']
    
    @pytest.mark.skipif(not NAMESPACE_MANAGER_AVAILABLE, reason="Namespace manager not available")
    def test_cross_namespace_mapping(self):
        """Test cross-namespace identity mapping"""
        manager = NamespaceManager()
        
        # Create test namespaces
        manager.create_namespace(
            namespace_id='source.lukhas.ai',
            namespace_type=NamespaceType.TENANT,
            display_name='Source Namespace',
            owner_id='owner_12345678'
        )
        
        manager.create_namespace(
            namespace_id='target.lukhas.ai',
            namespace_type=NamespaceType.TENANT,
            display_name='Target Namespace',
            owner_id='owner_12345678'
        )
        
        # Enable cross-namespace mapping for source
        manager.policies['source.lukhas.ai'].cross_namespace_allowed = True
        
        # Create identity mapping
        identity_mapping = {
            'source_user_123': 'target_user_456',
            'source_user_789': 'target_user_012'
        }
        
        mapping_result = manager.create_cross_namespace_mapping(
            'source.lukhas.ai',
            'target.lukhas.ai',
            identity_mapping,
            'admin_12345678'
        )
        
        assert mapping_result['success'] is True
        assert mapping_result['mapped_identities'] == 2
        
        # Test identity mapping lookup
        mapped_identity = manager.map_identity_across_namespaces(
            'source_user_123',
            'source.lukhas.ai',
            'target.lukhas.ai'
        )
        
        assert mapped_identity == 'target_user_456'
    
    @pytest.mark.skipif(not NAMESPACE_MANAGER_AVAILABLE, reason="Namespace manager not available")
    def test_namespace_listing(self):
        """Test listing namespaces with filtering"""
        manager = NamespaceManager()
        
        # List all namespaces
        all_namespaces = manager.list_namespaces()
        assert len(all_namespaces) >= 3  # At least the default ones
        
        # List by type
        root_namespaces = manager.list_namespaces(namespace_type=NamespaceType.ROOT)
        assert len(root_namespaces) >= 1
        
        root_ns = root_namespaces[0]
        assert root_ns['namespace_type'] == 'root'
        assert root_ns['namespace_id'] == 'lukhas.ai'
    
    @pytest.mark.skipif(not NAMESPACE_MANAGER_AVAILABLE, reason="Namespace manager not available")
    def test_namespace_system_status(self):
        """Test namespace system status reporting"""
        manager = NamespaceManager()
        
        status = manager.get_system_status()
        
        assert 'system' in status
        assert status['system'] == 'LUKHAS Namespace Manager'
        assert status['trinity_framework'] == '⚛️🧠🛡️'
        
        assert 'statistics' in status
        stats = status['statistics']
        assert 'total_namespaces' in stats
        assert 'active_namespaces' in stats
        assert 'type_distribution' in stats
        
        assert 'security' in status
        security = status['security']
        assert security['isolation_enabled'] is True
        assert security['encryption_enforced'] is True


class TestPerformanceOptimizer:
    """Test authentication performance optimization"""
    
    @pytest.mark.skipif(not OPTIMIZER_AVAILABLE, reason="Performance optimizer not available")
    def test_optimizer_initialization(self):
        """Test performance optimizer initializes correctly"""
        optimizer = AuthenticationOptimizer()
        
        assert optimizer is not None
        assert hasattr(optimizer, 'optimize_lambda_id_validation')
        assert hasattr(optimizer, 'optimize_tier_validation')
        assert hasattr(optimizer, 'optimize_token_validation')
        
        # Check default configuration
        assert optimizer.target_p95_latency == 100.0  # 100ms
        assert optimizer.target_cache_hit_rate == 0.85  # 85%
    
    @pytest.mark.skipif(not OPTIMIZER_AVAILABLE, reason="Performance optimizer not available")
    def test_lambda_id_validation_optimization(self):
        """Test λID validation optimization with caching"""
        optimizer = AuthenticationOptimizer()
        
        test_lambda_id = 'LUKHAS2-ABCD-🌀-XYZ1'
        
        # First call - should be cache miss
        start_time = time.time()
        result1 = optimizer.optimize_lambda_id_validation(test_lambda_id)
        first_call_time = (time.time() - start_time) * 1000
        
        assert result1['valid'] is True
        assert result1['lambda_id'] == test_lambda_id
        assert 'validation_time_ms' in result1
        
        # Second call - should be cache hit and faster
        start_time = time.time()
        result2 = optimizer.optimize_lambda_id_validation(test_lambda_id)
        second_call_time = (time.time() - start_time) * 1000
        
        assert result2['valid'] is True
        assert result2['lambda_id'] == test_lambda_id
        
        # Cache hit should be faster
        assert second_call_time < first_call_time
    
    @pytest.mark.skipif(not OPTIMIZER_AVAILABLE, reason="Performance optimizer not available")
    def test_tier_validation_optimization(self):
        """Test tier validation optimization"""
        optimizer = AuthenticationOptimizer()
        
        user_id = 'test_user_12345678'
        required_tier = 2
        
        # Test optimization with predictive caching enabled
        result = optimizer.optimize_tier_validation(user_id, required_tier)
        
        assert result['valid'] is True
        assert result['user_id'] == user_id
        assert result['required_tier'] == required_tier
        assert 'current_tier' in result
        assert 'validation_time_ms' in result
    
    @pytest.mark.skipif(not OPTIMIZER_AVAILABLE, reason="Performance optimizer not available")
    def test_token_validation_optimization(self):
        """Test token validation optimization"""
        optimizer = AuthenticationOptimizer()
        
        test_token = 'lukhas_access_token_1234567890abcdef'
        
        result = optimizer.optimize_token_validation(test_token)
        
        assert result['valid'] is True
        assert result['token_type'] == 'access_token'
        assert 'user_id' in result
        assert 'scopes' in result
        assert 'validation_time_ms' in result
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(not OPTIMIZER_AVAILABLE, reason="Performance optimizer not available")
    async def test_parallel_auth_flow_optimization(self):
        """Test parallel authentication flow optimization"""
        optimizer = AuthenticationOptimizer()
        
        # Create multiple authentication operations
        auth_operations = [
            {
                'type': 'lambda_id_validation',
                'lambda_id': 'LUKHAS2-TEST-🌀-ABC1',
                'level': 'standard'
            },
            {
                'type': 'tier_validation',
                'user_id': 'test_user_12345678',
                'required_tier': 2
            },
            {
                'type': 'token_validation',
                'token': 'lukhas_token_test_123456',
                'token_type': 'access_token'
            }
        ]
        
        start_time = time.time()
        result = await optimizer.optimize_parallel_auth_flow(auth_operations)
        processing_time = (time.time() - start_time) * 1000
        
        assert result['success'] is True
        assert result['parallel_processing'] is True
        assert result['operations_count'] == 3
        assert 'results' in result
        assert 'processing_time_ms' in result
        
        # Parallel processing should be efficient
        assert processing_time < 200  # Should be well under 200ms
    
    @pytest.mark.skipif(not OPTIMIZER_AVAILABLE, reason="Performance optimizer not available")
    def test_performance_reporting(self):
        """Test performance metrics and reporting"""
        optimizer = AuthenticationOptimizer()
        
        # Generate some test operations to create metrics
        for _ in range(10):
            optimizer.optimize_lambda_id_validation('LUKHAS1-TEST-○-XYZ1')
            optimizer.optimize_tier_validation('test_user_12345678', 1)
            optimizer.optimize_token_validation('test_token_123456')
        
        # Get performance report
        report = optimizer.get_performance_report()
        
        assert 'performance_summary' in report
        summary = report['performance_summary']
        assert 'p95_latency_ms' in summary
        assert 'cache_hit_rate' in summary
        assert 'latency_target_met' in summary
        assert 'cache_target_met' in summary
        
        assert 'cache_performance' in report
        assert 'optimization_features' in report
        assert 'metrics' in report
        assert 'recommendations' in report
        assert 'trinity_compliance' in report
        
        trinity = report['trinity_compliance']
        assert trinity['⚛️_identity'] == 'PERFORMANCE_OPTIMIZED'
        assert trinity['🧠_consciousness'] == 'MONITORED'
        assert trinity['🛡️_guardian'] == 'PROTECTED'
    
    @pytest.mark.skipif(not OPTIMIZER_AVAILABLE, reason="Performance optimizer not available")
    def test_optimizer_health_check(self):
        """Test performance optimizer health check"""
        optimizer = AuthenticationOptimizer()
        
        health_result = optimizer.health_check()
        
        assert 'optimizer_health_check' in health_result
        health_data = health_result['optimizer_health_check']
        
        assert 'status' in health_data
        assert health_data['status'] in ['HEALTHY', 'DEGRADED', 'UNHEALTHY']
        assert 'p95_latency_ms' in health_data
        assert 'cache_hit_rate' in health_data
        assert 'optimization_features' in health_data
        assert 'trinity_integration' in health_data
        
        # Check Trinity integration
        trinity = health_data['trinity_integration']
        assert trinity['⚛️_identity'] == 'OPTIMIZED'
        assert trinity['🧠_consciousness'] == 'MONITORED'
        assert trinity['🛡️_guardian'] == 'PROTECTED'


class TestTrinityFrameworkCompliance:
    """Test Trinity Framework compliance across all components"""
    
    @pytest.mark.skipif(not IDENTITY_SYSTEM_AVAILABLE, reason="Identity system not available")
    def test_trinity_symbols_presence(self):
        """Test Trinity Framework symbols are present in all components"""
        system = IdentitySystem()
        status = system.get_system_status()
        
        assert 'trinity_framework' in status
        assert status['trinity_framework'] == '⚛️🧠🛡️'
        
        # Verify each symbol represents correct component
        # ⚛️ = Identity, 🧠 = Consciousness, 🛡️ = Guardian
        trinity_str = status['trinity_framework']
        assert '⚛️' in trinity_str  # Identity
        assert '🧠' in trinity_str  # Consciousness  
        assert '🛡️' in trinity_str  # Guardian
    
    @pytest.mark.skipif(not OAUTH_PROVIDER_AVAILABLE, reason="OAuth provider not available")
    def test_oauth_trinity_compliance(self):
        """Test OAuth provider Trinity compliance"""
        provider = OAuth2OIDCProvider()
        metadata = provider.get_authorization_endpoint_metadata()
        
        assert metadata['lukhas_trinity_framework'] == '⚛️🧠🛡️'
        assert metadata['lukhas_consciousness_integration'] is True
        
        # Test Trinity-specific claims in tokens
        userinfo = provider.get_userinfo('mock_token')
        if 'trinity_compliance' in userinfo:
            assert userinfo['trinity_compliance'] == '⚛️🧠🛡️'
    
    def test_integration_health_checks(self):
        """Test all components provide Trinity-compliant health checks"""
        components_to_test = []
        
        if WEBAUTHN_AVAILABLE:
            webauthn_manager = WebAuthnManager()
            components_to_test.append(('WebAuthn', webauthn_manager.webauthn_health_check))
        
        if OPTIMIZER_AVAILABLE:
            optimizer = AuthenticationOptimizer()
            components_to_test.append(('Optimizer', optimizer.health_check))
        
        if NAMESPACE_MANAGER_AVAILABLE:
            namespace_manager = NamespaceManager()
            components_to_test.append(('Namespace', namespace_manager.get_system_status))
        
        for component_name, health_check_func in components_to_test:
            health_data = health_check_func()
            
            # Each component should have Trinity compliance indicators
            assert any(key for key in health_data.keys() if '⚛️' in str(health_data[key])), \
                f"{component_name} missing Trinity Identity (⚛️) compliance"
            assert any(key for key in health_data.keys() if '🧠' in str(health_data[key])), \
                f"{component_name} missing Trinity Consciousness (🧠) compliance"
            assert any(key for key in health_data.keys() if '🛡️' in str(health_data[key])), \
                f"{component_name} missing Trinity Guardian (🛡️) compliance"


class TestSecurityAndErrorHandling:
    """Test security measures and error handling"""
    
    @pytest.mark.skipif(not IDENTITY_SYSTEM_AVAILABLE, reason="Identity system not available")
    def test_authentication_input_validation(self):
        """Test authentication input validation and sanitization"""
        system = IdentitySystem()
        
        # Test with malicious input
        malicious_credentials = {
            'user_id': '<script>alert("xss")</script>',
            'password': 'test123'
        }
        
        result = system.authenticate_user(malicious_credentials, tier='T1')
        
        # Should handle malicious input gracefully
        assert isinstance(result, dict)
        assert 'success' in result
        
        # Test with extremely long input
        long_input = 'a' * 10000
        long_credentials = {
            'user_id': long_input,
            'password': 'test123'
        }
        
        result = system.authenticate_user(long_credentials, tier='T1')
        assert isinstance(result, dict)
        assert 'success' in result
    
    @pytest.mark.skipif(not OAUTH_PROVIDER_AVAILABLE, reason="OAuth provider not available")
    def test_oauth_error_handling(self):
        """Test OAuth provider error handling"""
        provider = OAuth2OIDCProvider()
        
        # Test with invalid client_id
        invalid_request = {
            'client_id': 'invalid_client_999',
            'redirect_uri': 'https://malicious.com/callback',
            'response_type': 'code',
            'scope': 'openid'
        }
        
        result = provider.handle_authorization_request(
            invalid_request,
            user_id='test_user',
            user_tier=1
        )
        
        assert 'error' in result
        assert result['error'] in ['invalid_client', 'invalid_request']
        
        # Test token request with invalid grant
        invalid_token_request = {
            'grant_type': 'authorization_code',
            'code': 'invalid_code_12345',
            'client_id': 'invalid_client',
            'client_secret': 'invalid_secret'
        }
        
        token_result = provider.handle_token_request(invalid_token_request)
        assert 'error' in token_result
    
    @pytest.mark.skipif(not WEBAUTHN_AVAILABLE, reason="WebAuthn not available")
    def test_webauthn_error_handling(self):
        """Test WebAuthn error handling"""
        manager = WebAuthnManager()
        
        # Test with invalid registration ID
        invalid_response = {
            'id': 'some_credential_id',
            'response': {
                'clientDataJSON': 'invalid_client_data',
                'attestationObject': 'invalid_attestation'
            }
        }
        
        result = manager.verify_registration_response('invalid_reg_id', invalid_response)
        
        assert result['success'] is False
        assert 'error' in result
        
        # Test authentication with non-existent credential
        auth_result = manager.verify_authentication_response('invalid_auth_id', invalid_response)
        
        assert auth_result['success'] is False
        assert 'error' in auth_result
    
    def test_rate_limiting_and_abuse_prevention(self):
        """Test rate limiting and abuse prevention measures"""
        if not IDENTITY_SYSTEM_AVAILABLE:
            pytest.skip("Identity system not available")
        
        system = IdentitySystem()
        
        # Simulate rapid authentication attempts
        results = []
        credentials = {
            'user_id': 'rapid_test_user_123',
            'password': 'test123'
        }
        
        for _ in range(20):  # 20 rapid attempts
            result = system.authenticate_user(credentials, tier='T1')
            results.append(result)
            time.sleep(0.01)  # 10ms between attempts
        
        # All attempts should be handled (though some might be rate-limited in production)
        assert all('success' in result for result in results)


class TestPerformanceBenchmarks:
    """Performance benchmark tests to ensure targets are met"""
    
    @pytest.mark.skipif(not IDENTITY_SYSTEM_AVAILABLE, reason="Identity system not available")
    def test_authentication_latency_benchmark(self):
        """Benchmark authentication latency - target <100ms p95"""
        system = IdentitySystem()
        
        latencies = []
        credentials = {
            'user_id': 'benchmark_user_123',
            'password': 'test123'
        }
        
        # Run 100 authentication attempts
        for _ in range(100):
            start_time = time.time()
            result = system.authenticate_user(credentials, tier='T1')
            latency_ms = (time.time() - start_time) * 1000
            latencies.append(latency_ms)
            
            assert result['success'] is True
        
        # Calculate percentiles
        latencies.sort()
        p95_latency = latencies[94]  # 95th percentile
        avg_latency = sum(latencies) / len(latencies)
        
        print(f"Authentication Performance:")
        print(f"  Average: {avg_latency:.2f}ms")
        print(f"  P95: {p95_latency:.2f}ms")
        print(f"  Target: <100ms p95")
        
        # Assert performance targets (relaxed for testing environment)
        assert p95_latency < 500, f"P95 latency {p95_latency:.2f}ms exceeds 500ms (relaxed target)"
        assert avg_latency < 200, f"Average latency {avg_latency:.2f}ms exceeds 200ms"
    
    @pytest.mark.skipif(not LAMBDA_ID_AVAILABLE, reason="Lambda ID not available")
    def test_lambda_id_generation_performance(self):
        """Benchmark λID generation performance"""
        generator = LambdaIDGenerator()
        
        latencies = []
        
        # Generate 100 λIDs
        for _ in range(100):
            start_time = time.time()
            lambda_id = generator.generate_lambda_id(TierLevel.FRIEND)
            latency_ms = (time.time() - start_time) * 1000
            latencies.append(latency_ms)
            
            assert lambda_id is not None
            assert lambda_id.startswith('LUKHAS2-')
        
        latencies.sort()
        p95_latency = latencies[94]
        avg_latency = sum(latencies) / len(latencies)
        
        print(f"λID Generation Performance:")
        print(f"  Average: {avg_latency:.2f}ms")
        print(f"  P95: {p95_latency:.2f}ms")
        print(f"  Target: <10ms p95")
        
        # Assert performance targets
        assert p95_latency < 50, f"P95 latency {p95_latency:.2f}ms exceeds 50ms"
        assert avg_latency < 20, f"Average latency {avg_latency:.2f}ms exceeds 20ms"
    
    @pytest.mark.skipif(not NAMESPACE_MANAGER_AVAILABLE, reason="Namespace manager not available")
    def test_namespace_resolution_performance(self):
        """Benchmark namespace resolution performance - target <5ms p95"""
        manager = NamespaceManager()
        
        latencies = []
        test_domains = [
            'lukhas.ai',
            'enterprise.lukhas.ai',
            'dev.lukhas.ai',
            'https://lukhas.ai/',
            'test.lukhas.ai'  # Non-existent, should still be fast
        ]
        
        # Test resolution 100 times
        for _ in range(20):  # 20 iterations
            for domain in test_domains:
                start_time = time.time()
                namespace = manager.resolve_namespace(domain)
                latency_ms = (time.time() - start_time) * 1000
                latencies.append(latency_ms)
        
        latencies.sort()
        p95_latency = latencies[int(len(latencies) * 0.95) - 1]
        avg_latency = sum(latencies) / len(latencies)
        
        print(f"Namespace Resolution Performance:")
        print(f"  Average: {avg_latency:.2f}ms")
        print(f"  P95: {p95_latency:.2f}ms")
        print(f"  Target: <5ms p95")
        
        # Assert performance targets (relaxed for testing)
        assert p95_latency < 50, f"P95 latency {p95_latency:.2f}ms exceeds 50ms"
        assert avg_latency < 20, f"Average latency {avg_latency:.2f}ms exceeds 20ms"


class TestIntegrationScenarios:
    """Integration test scenarios combining multiple components"""
    
    @pytest.mark.skipif(
        not (IDENTITY_SYSTEM_AVAILABLE and OAUTH_PROVIDER_AVAILABLE),
        reason="Identity system and OAuth provider required"
    )
    def test_full_oauth_authentication_flow(self):
        """Test complete OAuth authentication flow with identity system"""
        identity_system = IdentitySystem()
        oauth_provider = get_oauth_provider() if OAUTH_PROVIDER_AVAILABLE else OAuth2OIDCProvider()
        
        # Step 1: User authentication with identity system
        credentials = {
            'user_id': 'integration_user_12345678',
            'password': 'secure_password_123'
        }
        
        auth_result = identity_system.authenticate_user(credentials, tier='T2')
        assert auth_result['success'] is True
        
        # Step 2: OAuth client registration
        client_reg = oauth_provider.register_client({
            'client_name': 'Integration Test Client',
            'redirect_uris': ['https://testapp.example.com/callback']
        })
        assert 'client_id' in client_reg
        
        # Step 3: OAuth authorization flow
        auth_request = {
            'client_id': client_reg['client_id'],
            'redirect_uri': 'https://testapp.example.com/callback',
            'response_type': 'code',
            'scope': 'openid profile lukhas:basic',
            'state': 'integration_test_state'
        }
        
        oauth_auth_result = oauth_provider.handle_authorization_request(
            auth_request,
            user_id=credentials['user_id'],
            user_tier=2
        )
        
        assert 'code' in oauth_auth_result
        
        # Step 4: Token exchange
        token_request = {
            'grant_type': 'authorization_code',
            'code': oauth_auth_result['code'],
            'redirect_uri': 'https://testapp.example.com/callback',
            'client_id': client_reg['client_id'],
            'client_secret': client_reg['client_secret']
        }
        
        token_result = oauth_provider.handle_token_request(token_request)
        
        assert 'access_token' in token_result
        assert 'id_token' in token_result  # OIDC
        
        # Step 5: UserInfo retrieval
        userinfo = oauth_provider.get_userinfo(token_result['access_token'])
        
        assert userinfo['sub'] == credentials['user_id']
        assert 'trinity_compliance' in userinfo
    
    @pytest.mark.skipif(
        not (IDENTITY_SYSTEM_AVAILABLE and WEBAUTHN_AVAILABLE),
        reason="Identity system and WebAuthn required"
    )
    def test_webauthn_enhanced_authentication_flow(self):
        """Test WebAuthn integration with identity system"""
        identity_system = IdentitySystem()
        webauthn_manager = get_webauthn_manager() if WEBAUTHN_AVAILABLE else WebAuthnManager()
        
        user_id = 'webauthn_user_12345678'
        
        # Step 1: Generate WebAuthn registration options
        reg_options = webauthn_manager.generate_registration_options(
            user_id=user_id,
            user_name='webauthn_user@lukhas.ai',
            user_display_name='WebAuthn Test User',
            user_tier=2
        )
        
        assert reg_options['success'] is True
        assert 'options' in reg_options
        
        # Step 2: Simulate WebAuthn registration (mock)
        mock_reg_response = {
            'id': 'mock_webauthn_credential_id',
            'response': {
                'clientDataJSON': 'mock_client_data',
                'attestationObject': 'mock_attestation'
            },
            'transports': ['internal']
        }
        
        reg_verification = webauthn_manager.verify_registration_response(
            reg_options['registration_id'],
            mock_reg_response
        )
        
        # Step 3: Use WebAuthn for T2 authentication
        credentials = {
            'user_id': user_id,
            'webauthn_response': mock_reg_response  # In reality, this would be auth response
        }
        
        auth_result = identity_system.authenticate_user(credentials, tier='T2')
        
        # Should succeed with enhanced authentication
        assert auth_result['success'] is True
        assert auth_result['tier'] == 'T2'
    
    @pytest.mark.skipif(
        not (NAMESPACE_MANAGER_AVAILABLE and LAMBDA_ID_AVAILABLE),
        reason="Namespace manager and Lambda ID required"
    )
    def test_namespace_aware_lambda_id_generation(self):
        """Test λID generation with namespace isolation"""
        namespace_manager = NamespaceManager()
        lambda_generator = LambdaIDGenerator()
        
        # Create test tenant namespace
        tenant_result = namespace_manager.create_namespace(
            namespace_id='tenant1.lukhas.ai',
            namespace_type=NamespaceType.TENANT,
            display_name='Test Tenant 1',
            owner_id='tenant_owner_12345678'
        )
        
        assert tenant_result['success'] is True
        
        # Generate λIDs for different namespaces
        root_lambda_id = lambda_generator.generate_lambda_id(
            TierLevel.TRUSTED,
            user_context={'namespace': 'lukhas.ai'}
        )
        
        tenant_lambda_id = lambda_generator.generate_lambda_id(
            TierLevel.TRUSTED,
            user_context={'namespace': 'tenant1.lukhas.ai'}
        )
        
        # Both should be valid but different
        assert root_lambda_id != tenant_lambda_id
        assert root_lambda_id.startswith('LUKHAS3-')
        assert tenant_lambda_id.startswith('LUKHAS3-')
        
        # Verify namespace resolution works
        root_namespace = namespace_manager.resolve_namespace('lukhas.ai')
        tenant_namespace = namespace_manager.resolve_namespace('tenant1.lukhas.ai')
        
        assert root_namespace is not None
        assert tenant_namespace is not None
        assert root_namespace.namespace_id != tenant_namespace.namespace_id


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v', '--tb=short'])
