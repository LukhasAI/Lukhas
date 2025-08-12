"""
🔗 Identity Module Integration Test Suite
========================================

Comprehensive integration tests for LUKHAS Identity module component interactions.
Tests end-to-end authentication flows, cross-component communication, and Trinity Framework compliance.

Trinity Framework: ⚛️ (Identity), 🧠 (Consciousness), 🛡️ (Guardian)
"""

import asyncio
import base64
import json
import pytest
import secrets
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock

# Import system components under test
import sys
import os
identity_path = os.path.join(os.path.dirname(__file__), '..', '..', 'identity')
governance_path = os.path.join(os.path.dirname(__file__), '..', '..', 'governance', 'identity')
sys.path.extend([identity_path, governance_path])

try:
    from identity_core import IdentityCore, AccessTier
    from governance.identity.core.auth.webauthn_manager import WebAuthnManager
    from governance.identity.core.auth.oauth2_oidc_provider import OAuth2OIDCProvider
    from governance.identity.auth_backend.qr_entropy_generator import QREntropyGenerator
    COMPONENTS_AVAILABLE = True
except ImportError as e:
    COMPONENTS_AVAILABLE = False
    pytest.skip(f"Identity components not available: {e}", allow_module_level=True)


class TestIdentityModuleIntegration:
    """Integration tests for Identity module components"""
    
    @pytest.fixture
    def identity_system(self):
        """Create integrated identity system"""
        # Initialize core components
        identity_core = IdentityCore(data_dir="test_data")
        
        webauthn_config = {
            'rp_id': 'test.lukhas.ai',
            'rp_name': 'LUKHAS Test Integration',
            'origin': 'https://test.lukhas.ai'
        }
        webauthn_manager = WebAuthnManager(config=webauthn_config)
        
        oauth_config = {
            'issuer': 'https://test.lukhas.ai',
            'rp_id': 'test.lukhas.ai'
        }
        oauth_provider = OAuth2OIDCProvider(config=oauth_config)
        
        qr_generator = QREntropyGenerator()
        
        return {
            'identity_core': identity_core,
            'webauthn_manager': webauthn_manager,
            'oauth_provider': oauth_provider,
            'qr_generator': qr_generator
        }
    
    @pytest.fixture
    def test_user_data(self):
        """Test user data for integration scenarios"""
        return {
            'user_id': 'integration_test_user_12345678',
            'email': 'test@lukhas.ai',
            'display_name': 'Integration Test User',
            'tier': 3,
            'consent': True,
            'trinity_score': 0.8,
            'drift_score': 0.1
        }
    
    def test_end_to_end_user_registration_flow(self, identity_system, test_user_data):
        """Test complete user registration flow across components"""
        identity_core = identity_system['identity_core']
        webauthn_manager = identity_system['webauthn_manager']
        oauth_provider = identity_system['oauth_provider']
        qr_generator = identity_system['qr_generator']
        
        user_data = test_user_data
        
        # Step 1: Generate identity token
        start_time = time.time()
        token = identity_core.create_token(
            user_data['user_id'],
            AccessTier(f"T{user_data['tier']}"),
            {
                'consent': user_data['consent'],
                'trinity_score': user_data['trinity_score'],
                'drift_score': user_data['drift_score']
            }
        )
        token_creation_time = time.time() - start_time
        
        assert token.startswith(f"LUKHAS-T{user_data['tier']}-")
        assert token_creation_time < 0.1  # <100ms requirement
        
        # Step 2: Validate token and resolve permissions
        is_valid, token_metadata = identity_core.validate_symbolic_token(token)
        assert is_valid is True
        assert token_metadata['user_id'] == user_data['user_id']
        assert token_metadata['tier'] == f"T{user_data['tier']}"
        
        tier, permissions = identity_core.resolve_access_tier(token_metadata)
        assert tier == AccessTier(f"T{user_data['tier']}")
        assert permissions['can_use_consciousness'] is True  # T3+ permission
        
        # Step 3: Register WebAuthn credential
        webauthn_reg_result = webauthn_manager.generate_registration_options(
            user_data['user_id'],
            user_data['email'],
            user_data['display_name'],
            user_data['tier']
        )
        
        assert webauthn_reg_result['success'] is True
        assert webauthn_reg_result['guardian_approved'] is True
        
        # Step 4: Register OAuth2 client for user's applications
        client_registration = {
            'client_name': f"App for {user_data['display_name']}",
            'redirect_uris': ['https://userapp.example.com/callback'],
            'scope': 'openid profile email lukhas:identity:read'
        }
        
        oauth_client_result = oauth_provider.register_client(client_registration)
        assert 'error' not in oauth_client_result
        assert oauth_client_result['client_id'].startswith('lukhas_')
        
        # Step 5: Generate QR code for mobile authentication
        entropy_data = secrets.token_bytes(64)
        qr_session_id = f"mobile_auth_{user_data['user_id']}_{int(time.time())}"
        
        qr_result = qr_generator.generate_authentication_qr(
            qr_session_id,
            entropy_data,
            {
                'tier': user_data['tier'],
                'device_trust': 0.9,
                'max_scans': 3
            }
        )
        
        assert qr_result['success'] is True
        assert qr_result['constitutional_validated'] is True
        assert qr_result['layers_count'] == 3  # Steganography layers
        
        # Verify integration: All components should have consistent user data
        # Identity token should contain glyphs matching tier
        expected_glyphs = identity_core.TIER_GLYPHS[AccessTier(f"T{user_data['tier']}")]
        user_glyphs = token_metadata['glyphs']
        has_expected_glyph = any(glyph in expected_glyphs for glyph in user_glyphs)
        assert has_expected_glyph
        
        print(f"✅ End-to-end registration completed in {time.time() - start_time:.3f}s")
    
    def test_cross_component_authentication_flow(self, identity_system, test_user_data):
        """Test authentication flow across multiple components"""
        identity_core = identity_system['identity_core']
        webauthn_manager = identity_system['webauthn_manager']
        oauth_provider = identity_system['oauth_provider']
        
        user_data = test_user_data
        
        # Pre-setup: Create user token and WebAuthn credential
        token = identity_core.create_token(
            user_data['user_id'],
            AccessTier(f"T{user_data['tier']}"),
            {'consent': True, 'trinity_score': 0.8}
        )
        
        # Mock WebAuthn credential registration (simplified)
        from governance.identity.core.auth.webauthn_manager import WebAuthnCredential
        mock_credential = WebAuthnCredential({
            'credential_id': 'mock_credential_for_integration',
            'user_id': user_data['user_id'],
            'tier_level': user_data['tier'],
            'device_type': 'platform_authenticator',
            'public_key': 'mock_public_key_data'
        })
        webauthn_manager.credentials[user_data['user_id']] = [mock_credential]
        
        # Register OAuth client
        from governance.identity.core.auth.oauth2_oidc_provider import OAuthClient
        oauth_client = OAuthClient({
            'client_id': 'integration_test_client',
            'client_secret': 'integration_test_secret',
            'client_name': 'Integration Test Client',
            'redirect_uris': ['https://app.test.com/callback'],
            'allowed_scopes': ['openid', 'profile', 'email', 'lukhas:identity:read'],
            'grant_types': ['authorization_code'],
            'response_types': ['code'],
            'tier_level': user_data['tier']
        })
        oauth_provider.clients[oauth_client.client_id] = oauth_client
        
        # Authentication Flow Test
        start_time = time.time()
        
        # Step 1: Validate existing token
        is_valid, token_metadata = identity_core.validate_symbolic_token(token)
        assert is_valid is True
        
        # Step 2: WebAuthn authentication
        webauthn_auth_result = webauthn_manager.generate_authentication_options(
            user_data['user_id'], 
            user_data['tier']
        )
        assert webauthn_auth_result['success'] is True
        
        # Mock authentication response (in real scenario, this comes from authenticator)
        auth_id = webauthn_auth_result['authentication_id']
        pending_auth = webauthn_manager.pending_authentications[auth_id]
        
        mock_auth_response = {
            'id': 'mock_credential_for_integration',
            'response': {
                'clientDataJSON': base64.b64encode(json.dumps({
                    'type': 'webauthn.get',
                    'challenge': pending_auth['challenge_b64'],
                    'origin': 'https://test.lukhas.ai'
                }).encode()).decode(),
                'authenticatorData': base64.b64encode(b'mock_auth_data').decode(),
                'signature': base64.b64encode(b'mock_signature').decode()
            }
        }
        
        webauthn_verify_result = webauthn_manager.verify_authentication_response(
            auth_id, mock_auth_response
        )
        assert webauthn_verify_result['success'] is True
        assert webauthn_verify_result['user_id'] == user_data['user_id']
        
        # Step 3: OAuth2 authorization
        oauth_auth_request = {
            'client_id': oauth_client.client_id,
            'redirect_uri': 'https://app.test.com/callback',
            'response_type': 'code',
            'scope': 'openid profile email',
            'state': 'integration_test_state'
        }
        
        oauth_auth_result = oauth_provider.handle_authorization_request(
            oauth_auth_request, user_data['user_id'], user_data['tier']
        )
        
        assert 'error' not in oauth_auth_result
        assert 'code' in oauth_auth_result
        
        # Step 4: Token exchange
        auth_code = oauth_auth_result['code']
        token_request = {
            'grant_type': 'authorization_code',
            'code': auth_code,
            'redirect_uri': 'https://app.test.com/callback',
            'client_id': oauth_client.client_id,
            'client_secret': oauth_client.client_secret
        }
        
        token_result = oauth_provider.handle_token_request(token_request)
        
        assert 'error' not in token_result
        assert 'access_token' in token_result
        assert 'id_token' in token_result  # OpenID Connect
        
        total_auth_time = time.time() - start_time
        
        # Verify cross-component consistency
        # All components should recognize the same user with same permissions
        access_token = token_result['access_token']
        token_introspection = oauth_provider.introspect_token(access_token, oauth_client.client_id)
        
        assert token_introspection['active'] is True
        assert token_introspection['sub'] == user_data['user_id']
        assert token_introspection['lukhas_tier'] == user_data['tier']
        
        print(f"✅ Cross-component authentication completed in {total_auth_time:.3f}s")
    
    def test_tier_escalation_workflow(self, identity_system, test_user_data):
        """Test tier escalation workflow across components"""
        identity_core = identity_system['identity_core']
        webauthn_manager = identity_system['webauthn_manager']
        oauth_provider = identity_system['oauth_provider']
        
        user_data = test_user_data.copy()
        initial_tier = 2
        escalated_tier = 4
        
        # Step 1: Start with lower tier
        user_data['tier'] = initial_tier
        initial_token = identity_core.create_token(
            user_data['user_id'],
            AccessTier(f"T{initial_tier}"),
            {'consent': True, 'trinity_score': 0.6}
        )
        
        # Verify initial permissions
        _, initial_metadata = identity_core.validate_symbolic_token(initial_token)
        initial_tier_obj, initial_permissions = identity_core.resolve_access_tier(initial_metadata)
        
        assert initial_tier_obj == AccessTier(f"T{initial_tier}")
        assert initial_permissions['can_use_quantum'] is False  # T2 can't use quantum
        
        # Step 2: Simulate tier escalation (e.g., through Guardian approval)
        # In real system, this would involve Guardian validation and approval process
        escalated_metadata = initial_metadata.copy()
        escalated_metadata['tier'] = f"T{escalated_tier}"
        escalated_metadata['trinity_score'] = 0.9  # Higher Trinity score
        
        # Create new token with escalated tier
        escalated_token = identity_core.create_token(
            user_data['user_id'],
            AccessTier(f"T{escalated_tier}"),
            {
                'consent': True,
                'trinity_score': 0.9,
                'escalation_reason': 'guardian_approved',
                'escalated_from': f"T{initial_tier}",
                'escalated_at': datetime.utcnow().isoformat()
            }
        )
        
        # Step 3: Verify escalated permissions
        _, escalated_metadata = identity_core.validate_symbolic_token(escalated_token)
        escalated_tier_obj, escalated_permissions = identity_core.resolve_access_tier(escalated_metadata)
        
        assert escalated_tier_obj == AccessTier(f"T{escalated_tier}")
        assert escalated_permissions['can_use_quantum'] is True  # T4 can use quantum
        assert escalated_permissions['can_access_guardian'] is False  # Still not T5
        
        # Step 4: Verify WebAuthn requirements change with tier
        webauthn_reg_result = webauthn_manager.generate_registration_options(
            user_data['user_id'], user_data['email'], user_data['display_name'], escalated_tier
        )
        
        tier_requirements = webauthn_reg_result['tier_requirements']
        assert tier_requirements['user_verification'] is True  # Higher tier requires verification
        assert tier_requirements['platform_attachment'] == 'platform'  # Stricter requirements
        
        # Step 5: Verify OAuth scopes expand with tier
        tier_scopes = oauth_provider._get_allowed_scopes_for_tier(escalated_tier)
        initial_scopes = oauth_provider._get_allowed_scopes_for_tier(initial_tier)
        
        # Escalated tier should have more scopes
        assert len(tier_scopes) > len(initial_scopes)
        assert 'lukhas:enterprise' in tier_scopes
        assert 'lukhas:enterprise' not in initial_scopes
        
        print(f"✅ Tier escalation from T{initial_tier} to T{escalated_tier} validated")
    
    def test_security_incident_response_workflow(self, identity_system, test_user_data):
        """Test security incident response across components"""
        identity_core = identity_system['identity_core']
        webauthn_manager = identity_system['webauthn_manager']
        oauth_provider = identity_system['oauth_provider']
        qr_generator = identity_system['qr_generator']
        
        user_data = test_user_data
        
        # Setup: Create user with credentials and tokens
        token = identity_core.create_token(
            user_data['user_id'],
            AccessTier(f"T{user_data['tier']}"),
            {'consent': True, 'trinity_score': 0.8, 'drift_score': 0.1}
        )
        
        # Add WebAuthn credential
        from governance.identity.core.auth.webauthn_manager import WebAuthnCredential
        credential = WebAuthnCredential({
            'credential_id': 'security_test_credential',
            'user_id': user_data['user_id'],
            'tier_level': user_data['tier']
        })
        webauthn_manager.credentials[user_data['user_id']] = [credential]
        
        # Add OAuth access token
        access_token = f"lukhas_at_{secrets.token_urlsafe(32)}"
        oauth_provider.access_tokens[access_token] = {
            'client_id': 'test_client',
            'user_id': user_data['user_id'],
            'user_tier': user_data['tier'],
            'scope': ['openid', 'profile'],
            'issued_at': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(hours=1)).isoformat()
        }
        
        # Add active QR session
        qr_session_id = f"security_test_qr_{user_data['user_id']}"
        qr_result = qr_generator.generate_authentication_qr(
            qr_session_id, secrets.token_bytes(32)
        )
        assert qr_result['success'] is True
        
        # Simulate security incident: High drift score detected
        print("🚨 Simulating security incident: High drift score detected")
        
        # Step 1: Update user metadata with high drift score
        incident_metadata = {
            'user_id': user_data['user_id'],
            'tier': f"T{user_data['tier']}",
            'consent': True,
            'trinity_score': 0.8,
            'drift_score': 0.7,  # High drift - security concern
            'security_incident': True,
            'incident_type': 'high_drift_detected',
            'incident_timestamp': datetime.utcnow().isoformat()
        }
        
        # Step 2: Test Guardian validation (constitutional validation)
        # Should restrict permissions due to high drift
        with patch('logging.Logger.warning') as mock_warning:
            tier, permissions = identity_core.resolve_access_tier(incident_metadata)
            mock_warning.assert_called()  # Should log warning
        
        # Step 3: Revoke WebAuthn credential as security measure
        revoke_result = webauthn_manager.revoke_credential(
            user_data['user_id'], 'security_test_credential'
        )
        assert revoke_result['success'] is True
        assert len(webauthn_manager.credentials[user_data['user_id']]) == 0
        
        # Step 4: Invalidate OAuth tokens
        # In real system, would iterate through all user tokens
        del oauth_provider.access_tokens[access_token]
        
        # Verify token is no longer valid
        introspection = oauth_provider.introspect_token(access_token, 'test_client')
        assert introspection['active'] is False
        
        # Step 5: Invalidate QR sessions
        # QR generator should refuse new sessions for compromised user
        new_qr_result = qr_generator.generate_authentication_qr(
            f"post_incident_{user_data['user_id']}", 
            secrets.token_bytes(32),
            {'tier': user_data['tier'], 'security_incident': True}
        )
        
        # Should still succeed but with constitutional validation noting the incident
        assert new_qr_result['success'] is True
        assert new_qr_result['constitutional_validated'] is True
        
        # Step 6: Revoke existing identity token
        revoke_success = identity_core.revoke_token(token)
        assert revoke_success is True
        
        # Verify token is no longer valid
        is_valid, _ = identity_core.validate_symbolic_token(token)
        assert is_valid is False
        
        print("✅ Security incident response workflow completed")
    
    def test_performance_under_load(self, identity_system):
        """Test system performance under concurrent load"""
        identity_core = identity_system['identity_core']
        webauthn_manager = identity_system['webauthn_manager']
        oauth_provider = identity_system['oauth_provider']
        qr_generator = identity_system['qr_generator']
        
        num_users = 50
        operations_per_user = 5
        
        # Create test users
        test_users = []
        for i in range(num_users):
            user_data = {
                'user_id': f'load_test_user_{i:08d}',
                'email': f'loadtest{i}@lukhas.ai',
                'display_name': f'Load Test User {i}',
                'tier': (i % 5) + 1  # Distribute across tiers 1-5
            }
            test_users.append(user_data)
        
        # Test concurrent operations
        start_time = time.time()
        
        total_operations = 0
        failed_operations = 0
        operation_times = []
        
        for user in test_users:
            for op in range(operations_per_user):
                op_start = time.time()
                
                try:
                    # Operation 1: Create token
                    token = identity_core.create_token(
                        user['user_id'],
                        AccessTier(f"T{user['tier']}"),
                        {'consent': True, 'trinity_score': 0.7}
                    )
                    
                    # Operation 2: Validate token
                    is_valid, metadata = identity_core.validate_symbolic_token(token)
                    assert is_valid is True
                    
                    # Operation 3: WebAuthn registration options
                    webauthn_result = webauthn_manager.generate_registration_options(
                        user['user_id'], user['email'], user['display_name'], user['tier']
                    )
                    assert webauthn_result['success'] is True
                    
                    # Operation 4: OAuth client registration
                    if op == 0:  # Only register client once per user
                        client_reg = oauth_provider.register_client({
                            'client_name': f"App for {user['display_name']}",
                            'redirect_uris': [f"https://app{user['user_id']}.test.com/callback"]
                        })
                        assert 'error' not in client_reg
                    
                    # Operation 5: QR generation
                    qr_result = qr_generator.generate_authentication_qr(
                        f"load_test_{user['user_id']}_{op}",
                        secrets.token_bytes(32)
                    )
                    assert qr_result['success'] is True
                    
                    op_time = (time.time() - op_start) * 1000
                    operation_times.append(op_time)
                    
                except Exception as e:
                    failed_operations += 1
                    print(f"Operation failed for {user['user_id']}: {e}")
                
                total_operations += 1
        
        total_time = time.time() - start_time
        
        # Calculate performance metrics
        operation_times.sort()
        avg_time = sum(operation_times) / len(operation_times) if operation_times else 0
        p95_time = operation_times[int(0.95 * len(operation_times))] if operation_times else 0
        p99_time = operation_times[int(0.99 * len(operation_times))] if operation_times else 0
        
        success_rate = (total_operations - failed_operations) / total_operations * 100
        throughput = total_operations / total_time
        
        print(f"📊 Load Test Results:")
        print(f"  Total operations: {total_operations}")
        print(f"  Failed operations: {failed_operations}")
        print(f"  Success rate: {success_rate:.2f}%")
        print(f"  Total time: {total_time:.2f}s")
        print(f"  Throughput: {throughput:.2f} ops/sec")
        print(f"  Average latency: {avg_time:.2f}ms")
        print(f"  P95 latency: {p95_time:.2f}ms")
        print(f"  P99 latency: {p99_time:.2f}ms")
        
        # Performance assertions
        assert success_rate >= 99.0, f"Success rate {success_rate:.2f}% below threshold"
        assert p95_time < 500, f"P95 latency {p95_time:.2f}ms exceeds threshold"
        assert avg_time < 200, f"Average latency {avg_time:.2f}ms exceeds threshold"
        assert throughput > 50, f"Throughput {throughput:.2f} ops/sec below threshold"
    
    def test_trinity_framework_integration_validation(self, identity_system, test_user_data):
        """Test Trinity Framework integration across all components (⚛️🧠🛡️)"""
        identity_core = identity_system['identity_core']
        webauthn_manager = identity_system['webauthn_manager']
        oauth_provider = identity_system['oauth_provider']
        qr_generator = identity_system['qr_generator']
        
        user_data = test_user_data
        
        print("🔍 Testing Trinity Framework integration (⚛️🧠🛡️)")
        
        # ⚛️ Identity Framework Testing
        print("⚛️ Testing Identity Framework...")
        
        # Create identity token with symbolic representation
        token = identity_core.create_token(
            user_data['user_id'],
            AccessTier(f"T{user_data['tier']}"),
            {
                'consent': user_data['consent'],
                'trinity_score': user_data['trinity_score'],
                'cultural_profile': 'universal'
            }
        )
        
        # Verify identity integrity
        is_valid, metadata = identity_core.validate_symbolic_token(token)
        assert is_valid is True
        assert metadata['user_id'] == user_data['user_id']
        assert 'glyphs' in metadata
        
        # Generate identity glyphs
        glyphs = identity_core.generate_identity_glyph(user_data['user_id'])
        assert len(glyphs) >= 3
        assert any(g in ['⚛️', '🧠', '🛡️'] for g in glyphs)  # Trinity glyphs present
        
        # 🧠 Consciousness Framework Testing
        print("🧠 Testing Consciousness Framework...")
        
        # Test temporal awareness in all components
        webauthn_reg = webauthn_manager.generate_registration_options(
            user_data['user_id'], user_data['email'], user_data['display_name'], user_data['tier']
        )
        assert 'expires_at' in webauthn_reg
        expires_at = datetime.fromisoformat(webauthn_reg['expires_at'])
        assert expires_at > datetime.utcnow()
        
        # OAuth temporal awareness
        oauth_metadata = oauth_provider.get_authorization_endpoint_metadata()
        assert oauth_metadata['lukhas_consciousness_integration'] is True
        
        # QR code temporal awareness
        qr_result = qr_generator.generate_authentication_qr(
            f"trinity_test_{user_data['user_id']}", secrets.token_bytes(32)
        )
        assert 'expires_at' in qr_result
        qr_expires = datetime.fromisoformat(qr_result['expires_at'])
        assert qr_expires > datetime.utcnow()
        
        # 🛡️ Guardian Framework Testing
        print("🛡️ Testing Guardian Framework...")
        
        # Test Guardian validation in identity core
        high_drift_metadata = metadata.copy()
        high_drift_metadata['drift_score'] = 0.8
        
        with patch('logging.Logger.warning') as mock_warning:
            tier, permissions = identity_core.resolve_access_tier(high_drift_metadata)
            mock_warning.assert_called()  # Guardian should flag high drift
        
        # Test Guardian validation in WebAuthn
        guardian_result = webauthn_manager._constitutional_validation(
            user_data['user_id'], 'webauthn_registration', {'valid': 'data'}
        )
        assert guardian_result is True
        
        suspicious_result = webauthn_manager._constitutional_validation(
            user_data['user_id'], 'webauthn_registration', {'script': 'alert("xss")'}
        )
        assert suspicious_result is False
        
        # Test Guardian validation in OAuth
        oauth_guardian_result = oauth_provider._constitutional_validation(
            user_data['user_id'], 'oauth2_authorization', {
                'client_id': 'valid_client',
                'scopes': ['openid']
            }
        )
        assert oauth_guardian_result is True
        
        # Test Guardian validation in QR generator
        qr_guardian_result = qr_generator._constitutional_validation(
            {'session_id': user_data['user_id']}, secrets.token_bytes(32)
        )
        assert qr_guardian_result is True
        
        # Verify Trinity compliance indicators across components
        assert webauthn_reg['guardian_approved'] is True
        assert qr_result['constitutional_validated'] is True
        assert qr_result['guardian_approved'] is True
        
        # Test Trinity framework metadata consistency
        trinity_indicators = {
            'identity_core': '⚛️' in ''.join(metadata.get('glyphs', [])),
            'webauthn_manager': webauthn_reg.get('guardian_approved', False),
            'oauth_provider': oauth_metadata['lukhas_trinity_framework'] == '⚛️🧠🛡️',
            'qr_generator': qr_result.get('constitutional_validated', False)
        }
        
        for component, indicator in trinity_indicators.items():
            assert indicator, f"Trinity framework not properly integrated in {component}"
        
        print("✅ Trinity Framework integration validated across all components")
    
    def test_data_consistency_across_components(self, identity_system, test_user_data):
        """Test data consistency across all identity components"""
        identity_core = identity_system['identity_core']
        webauthn_manager = identity_system['webauthn_manager']
        oauth_provider = identity_system['oauth_provider']
        qr_generator = identity_system['qr_generator']
        
        user_data = test_user_data
        
        # Create user identity across all components
        token = identity_core.create_token(
            user_data['user_id'],
            AccessTier(f"T{user_data['tier']}"),
            {'consent': True, 'trinity_score': 0.8}
        )
        
        # Register WebAuthn credential
        webauthn_reg = webauthn_manager.generate_registration_options(
            user_data['user_id'], user_data['email'], user_data['display_name'], user_data['tier']
        )
        
        # Register OAuth client
        oauth_client = oauth_provider.register_client({
            'client_name': f"Consistency Test App for {user_data['display_name']}",
            'redirect_uris': ['https://consistency.test.com/callback']
        })
        
        # Generate QR code
        qr_session = f"consistency_test_{user_data['user_id']}"
        qr_result = qr_generator.generate_authentication_qr(
            qr_session, secrets.token_bytes(32), {'tier': user_data['tier']}
        )
        
        # Verify consistent user identification
        _, token_metadata = identity_core.validate_symbolic_token(token)
        assert token_metadata['user_id'] == user_data['user_id']
        assert token_metadata['tier'] == f"T{user_data['tier']}"
        
        # WebAuthn should store tier consistently
        webauthn_tier_reqs = webauthn_reg['tier_requirements']
        expected_tier_reqs = webauthn_manager.tier_requirements[user_data['tier']]
        assert webauthn_tier_reqs == expected_tier_reqs
        
        # OAuth should respect tier-based scopes
        allowed_scopes = oauth_provider._get_allowed_scopes_for_tier(user_data['tier'])
        tier_3_scopes = oauth_provider.tier_scope_mapping[user_data['tier']]  # Tier 3
        assert allowed_scopes == tier_3_scopes
        
        # QR code should embed tier information
        qr_session_data = qr_generator.active_codes[qr_session]
        assert qr_session_data['base_data']['user_tier'] == user_data['tier']
        
        # Verify timestamp consistency (all should be within reasonable time window)
        timestamps = [
            datetime.fromisoformat(token_metadata['created_at']),
            datetime.fromisoformat(webauthn_reg['expires_at']) - timedelta(minutes=5),  # Created 5min before expiry
            datetime.fromisoformat(qr_session_data['created_at'])
        ]
        
        time_window = timedelta(seconds=30)  # 30-second window for test execution
        earliest = min(timestamps)
        latest = max(timestamps)
        
        assert (latest - earliest) < time_window, "Timestamps not consistent across components"
        
        print("✅ Data consistency validated across all components")


@pytest.mark.asyncio
class TestAsyncIdentityOperations:
    """Test asynchronous identity operations and concurrent access"""
    
    @pytest.fixture
    async def async_identity_system(self):
        """Create identity system for async testing"""
        # In real implementation, these would be async-capable versions
        identity_core = IdentityCore(data_dir="async_test_data")
        return {'identity_core': identity_core}
    
    async def test_concurrent_token_operations(self, async_identity_system):
        """Test concurrent token creation and validation"""
        identity_core = async_identity_system['identity_core']
        
        num_concurrent_users = 20
        
        async def create_and_validate_token(user_index):
            user_id = f'concurrent_user_{user_index:08d}'
            tier = AccessTier(f"T{(user_index % 5) + 1}")
            
            # Create token
            token = identity_core.create_token(
                user_id, tier, {'consent': True, 'trinity_score': 0.7}
            )
            
            # Validate token
            is_valid, metadata = identity_core.validate_symbolic_token(token)
            
            assert is_valid is True
            assert metadata['user_id'] == user_id
            assert metadata['tier'] == tier.value
            
            return {'user_id': user_id, 'token': token, 'metadata': metadata}
        
        # Run concurrent operations
        tasks = [create_and_validate_token(i) for i in range(num_concurrent_users)]
        results = await asyncio.gather(*tasks)
        
        # Verify all operations succeeded
        assert len(results) == num_concurrent_users
        
        # Verify no data corruption
        user_ids = {r['metadata']['user_id'] for r in results}
        assert len(user_ids) == num_concurrent_users  # All unique
        
        # Verify tokens are unique
        tokens = {r['token'] for r in results}
        assert len(tokens) == num_concurrent_users  # All unique
        
        print(f"✅ {num_concurrent_users} concurrent token operations completed successfully")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])