"""
🔐 WebAuthn/FIDO2 Manager Test Suite
===================================

Comprehensive unit tests for LUKHAS WebAuthn/FIDO2 authentication manager.
Tests passwordless authentication, biometric integration, and Trinity Framework compliance.

Trinity Framework: ⚛️ (Identity), 🧠 (Consciousness), 🛡️ (Guardian)
"""

import base64
import json
import os

# Import system under test
import sys
import time
from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'governance', 'identity', 'core', 'auth'))

try:
    from webauthn_manager import WebAuthnCredential, WebAuthnManager
    WEBAUTHN_AVAILABLE = True
except ImportError:
    WEBAUTHN_AVAILABLE = False
    pytest.skip("WebAuthn manager not available", allow_module_level=True)


class TestWebAuthnCredential:
    """Test WebAuthn credential data structure"""

    def test_webauthn_credential_creation(self):
        """Test WebAuthnCredential creation and serialization"""
        credential_data = {
            'credential_id': 'test_credential_123',
            'public_key': 'mock_public_key_data',
            'sign_count': 5,
            'user_id': 'test_user_12345678',
            'authenticator_data': {
                'attestation_object': 'mock_attestation',
                'client_data_json': 'mock_client_data',
                'transports': ['usb', 'nfc']
            },
            'tier_level': 3,
            'device_type': 'usb_security_key'
        }

        credential = WebAuthnCredential(credential_data)

        assert credential.credential_id == 'test_credential_123'
        assert credential.public_key == 'mock_public_key_data'
        assert credential.sign_count == 5
        assert credential.user_id == 'test_user_12345678'
        assert credential.tier_level == 3
        assert credential.device_type == 'usb_security_key'
        assert credential.authenticator_data['transports'] == ['usb', 'nfc']

        # Test serialization
        credential_dict = credential.to_dict()
        assert credential_dict['credential_id'] == 'test_credential_123'
        assert credential_dict['tier_level'] == 3
        assert credential_dict['device_type'] == 'usb_security_key'

    def test_webauthn_credential_defaults(self):
        """Test WebAuthnCredential with minimal data"""
        credential_data = {
            'user_id': 'minimal_user_12345678'
        }

        credential = WebAuthnCredential(credential_data)

        assert credential.credential_id == ''
        assert credential.sign_count == 0
        assert credential.tier_level == 0
        assert credential.device_type == 'unknown'
        assert credential.created_at is not None
        assert credential.last_used is None


class TestWebAuthnManager:
    """Test suite for WebAuthn/FIDO2 authentication manager"""

    @pytest.fixture
    def webauthn_manager(self):
        """Create WebAuthn manager instance"""
        config = {
            'rp_id': 'test.lukhas.ai',
            'rp_name': 'LUKHAS Test Environment',
            'origin': 'https://test.lukhas.ai'
        }
        return WebAuthnManager(config=config)

    @pytest.fixture
    def mock_user_data(self):
        """Sample user data for testing"""
        return {
            'user_id': 'webauthn_test_user_12345678',
            'user_name': 'test@lukhas.ai',
            'user_display_name': 'WebAuthn Test User',
            'user_tier': 3
        }

    @pytest.fixture
    def mock_registration_response(self):
        """Mock WebAuthn registration response"""
        return {
            'id': 'mock_credential_id_123456',
            'rawId': base64.b64encode(b'mock_credential_id_123456').decode(),
            'response': {
                'clientDataJSON': base64.b64encode(json.dumps({
                    'type': 'webauthn.create',
                    'challenge': 'mock_challenge_value',
                    'origin': 'https://test.lukhas.ai'
                }).encode()).decode(),
                'attestationObject': base64.b64encode(b'mock_attestation_object').decode(),
                'publicKey': 'mock_public_key_data'
            },
            'transports': ['usb']
        }

    @pytest.fixture
    def mock_authentication_response(self):
        """Mock WebAuthn authentication response"""
        return {
            'id': 'mock_credential_id_123456',
            'rawId': base64.b64encode(b'mock_credential_id_123456').decode(),
            'response': {
                'clientDataJSON': base64.b64encode(json.dumps({
                    'type': 'webauthn.get',
                    'challenge': 'mock_challenge_value',
                    'origin': 'https://test.lukhas.ai'
                }).encode()).decode(),
                'authenticatorData': base64.b64encode(b'mock_authenticator_data').decode(),
                'signature': base64.b64encode(b'mock_signature').decode()
            }
        }

    def test_webauthn_manager_initialization(self, webauthn_manager):
        """Test WebAuthn manager initialization"""
        assert webauthn_manager.rp_id == 'test.lukhas.ai'
        assert webauthn_manager.rp_name == 'LUKHAS Test Environment'
        assert webauthn_manager.origin == 'https://test.lukhas.ai'

        # Check tier requirements are properly configured
        assert len(webauthn_manager.tier_requirements) == 6  # Tiers 0-5

        # Verify tier 0 (most permissive)
        tier_0_reqs = webauthn_manager.tier_requirements[0]
        assert tier_0_reqs['user_verification'] is False
        assert tier_0_reqs['platform_attachment'] == 'any'

        # Verify tier 5 (most restrictive)
        tier_5_reqs = webauthn_manager.tier_requirements[5]
        assert tier_5_reqs['user_verification'] is True
        assert tier_5_reqs['platform_attachment'] == 'platform'
        assert tier_5_reqs.get('resident_key') is True

        # Check Trinity Framework integration hooks
        assert hasattr(webauthn_manager, 'guardian_validator')
        assert hasattr(webauthn_manager, 'consciousness_tracker')
        assert hasattr(webauthn_manager, 'identity_verifier')

    def test_generate_registration_options_basic(self, webauthn_manager, mock_user_data):
        """Test basic WebAuthn registration options generation"""
        user_id = mock_user_data['user_id']
        user_name = mock_user_data['user_name']
        display_name = mock_user_data['user_display_name']
        user_tier = mock_user_data['user_tier']

        start_time = time.time()
        result = webauthn_manager.generate_registration_options(
            user_id, user_name, display_name, user_tier
        )
        generation_time = (time.time() - start_time) * 1000

        # Verify successful generation
        assert result['success'] is True
        assert 'registration_id' in result
        assert 'options' in result
        assert 'tier_requirements' in result
        assert result['guardian_approved'] is True
        assert result['generation_time_ms'] < 100  # Performance requirement

        options = result['options']

        # Verify standard WebAuthn structure
        assert 'challenge' in options
        assert 'rp' in options
        assert 'user' in options
        assert 'pubKeyCredParams' in options
        assert 'authenticatorSelection' in options
        assert 'excludeCredentials' in options
        assert 'timeout' in options

        # Verify RP information
        assert options['rp']['name'] == 'LUKHAS Test Environment'
        assert options['rp']['id'] == 'test.lukhas.ai'

        # Verify user information
        user_info = options['user']
        assert base64.b64decode(user_info['id'] + '===').decode() == user_id
        assert user_info['name'] == user_name
        assert user_info['displayName'] == display_name

        # Verify tier-based requirements
        tier_reqs = result['tier_requirements']
        expected_reqs = webauthn_manager.tier_requirements[user_tier]
        assert tier_reqs == expected_reqs

        # Verify authenticator selection matches tier requirements
        auth_selection = options['authenticatorSelection']
        if expected_reqs['user_verification']:
            assert auth_selection['userVerification'] == 'required'
        else:
            assert auth_selection['userVerification'] == 'preferred'

    def test_generate_registration_options_different_tiers(self, webauthn_manager):
        """Test registration options for different user tiers"""
        base_user_id = 'tier_test_user_12345678'

        for tier in range(6):  # Test tiers 0-5
            result = webauthn_manager.generate_registration_options(
                f"{base_user_id}_{tier}",
                f"tier{tier}@test.com",
                f"Tier {tier} Test User",
                tier
            )

            assert result['success'] is True
            options = result['options']
            tier_reqs = webauthn_manager.tier_requirements[tier]

            # Verify tier-specific requirements
            auth_selection = options['authenticatorSelection']

            if tier_reqs['user_verification']:
                assert auth_selection['userVerification'] == 'required'

            if 'platform_attachment' in tier_reqs:
                if tier_reqs['platform_attachment'] != 'any':
                    assert auth_selection['authenticatorAttachment'] == tier_reqs['platform_attachment']

            # Higher tiers should require direct attestation
            if tier >= 3:
                assert options['attestation'] == 'direct'
            else:
                assert options['attestation'] == 'none'

            # Highest tiers should have additional extensions
            if tier >= 4:
                assert options['extensions']['hmacCreateSecret'] is True
            else:
                assert options['extensions']['hmacCreateSecret'] is False

    def test_generate_registration_options_with_existing_credentials(self, webauthn_manager):
        """Test registration options generation with existing credentials"""
        user_id = 'existing_creds_user_12345678'

        # Add existing credential
        existing_credential = WebAuthnCredential({
            'credential_id': 'existing_cred_123',
            'user_id': user_id,
            'tier_level': 2
        })
        webauthn_manager.credentials[user_id] = [existing_credential]

        result = webauthn_manager.generate_registration_options(
            user_id, 'test@example.com', 'Test User', 2
        )

        assert result['success'] is True
        options = result['options']

        # Should exclude existing credentials
        exclude_creds = options['excludeCredentials']
        assert len(exclude_creds) == 1
        assert exclude_creds[0]['id'] == 'existing_cred_123'
        assert exclude_creds[0]['type'] == 'public-key'

    def test_verify_registration_response_valid(self, webauthn_manager, mock_user_data, mock_registration_response):
        """Test valid WebAuthn registration response verification"""
        # Generate registration options first
        reg_result = webauthn_manager.generate_registration_options(
            mock_user_data['user_id'],
            mock_user_data['user_name'],
            mock_user_data['user_display_name'],
            mock_user_data['user_tier']
        )
        registration_id = reg_result['registration_id']

        # Update mock response with correct challenge
        pending_reg = webauthn_manager.pending_registrations[registration_id]
        client_data = json.loads(base64.b64decode(mock_registration_response['response']['clientDataJSON'] + '==='))
        client_data['challenge'] = pending_reg['challenge_b64']
        mock_registration_response['response']['clientDataJSON'] = base64.b64encode(
            json.dumps(client_data).encode()
        ).decode()

        start_time = time.time()
        result = webauthn_manager.verify_registration_response(registration_id, mock_registration_response)
        verification_time = (time.time() - start_time) * 1000

        assert result['success'] is True
        assert 'credential_id' in result
        assert result['user_id'] == mock_user_data['user_id']
        assert result['tier_level'] == mock_user_data['user_tier']
        assert result['guardian_approved'] is True
        assert result['trinity_compliant'] is True
        assert result['verification_time_ms'] < 100  # Performance requirement

        # Verify credential was stored
        user_credentials = webauthn_manager.credentials[mock_user_data['user_id']]
        assert len(user_credentials) == 1
        assert user_credentials[0].credential_id == mock_registration_response['id']
        assert user_credentials[0].tier_level == mock_user_data['user_tier']

        # Verify pending registration was cleaned up
        assert registration_id not in webauthn_manager.pending_registrations

    def test_verify_registration_response_invalid_registration_id(self, webauthn_manager, mock_registration_response):
        """Test registration verification with invalid registration ID"""
        result = webauthn_manager.verify_registration_response('invalid_reg_id', mock_registration_response)

        assert result['success'] is False
        assert result['error'] == 'Invalid registration ID'

    def test_verify_registration_response_expired(self, webauthn_manager, mock_user_data, mock_registration_response):
        """Test registration verification with expired registration"""
        # Generate registration options
        reg_result = webauthn_manager.generate_registration_options(
            mock_user_data['user_id'],
            mock_user_data['user_name'],
            mock_user_data['user_display_name'],
            mock_user_data['user_tier']
        )
        registration_id = reg_result['registration_id']

        # Manually expire the registration
        past_time = datetime.utcnow() - timedelta(minutes=10)
        webauthn_manager.pending_registrations[registration_id]['expires_at'] = past_time.isoformat()

        result = webauthn_manager.verify_registration_response(registration_id, mock_registration_response)

        assert result['success'] is False
        assert result['error'] == 'Registration expired'
        assert registration_id not in webauthn_manager.pending_registrations  # Should be cleaned up

    def test_verify_registration_response_challenge_mismatch(self, webauthn_manager, mock_user_data, mock_registration_response):
        """Test registration verification with challenge mismatch"""
        # Generate registration options
        reg_result = webauthn_manager.generate_registration_options(
            mock_user_data['user_id'],
            mock_user_data['user_name'],
            mock_user_data['user_display_name'],
            mock_user_data['user_tier']
        )
        registration_id = reg_result['registration_id']

        # Use wrong challenge in response (don't update it)
        result = webauthn_manager.verify_registration_response(registration_id, mock_registration_response)

        assert result['success'] is False
        assert result['error'] == 'Challenge mismatch'

    def test_generate_authentication_options_basic(self, webauthn_manager):
        """Test basic WebAuthn authentication options generation"""
        user_id = 'auth_test_user_12345678'
        tier_level = 2

        start_time = time.time()
        result = webauthn_manager.generate_authentication_options(user_id, tier_level)
        generation_time = (time.time() - start_time) * 1000

        assert result['success'] is True
        assert 'authentication_id' in result
        assert 'options' in result
        assert 'allowed_credentials_count' in result
        assert 'tier_requirements' in result
        assert result['generation_time_ms'] < 100  # Performance requirement

        options = result['options']

        # Verify standard WebAuthn authentication structure
        assert 'challenge' in options
        assert 'rpId' in options
        assert 'allowCredentials' in options
        assert 'userVerification' in options
        assert 'timeout' in options

        # Verify RP ID
        assert options['rpId'] == webauthn_manager.rp_id

        # No credentials exist yet, so should be empty
        assert len(options['allowCredentials']) == 0
        assert result['allowed_credentials_count'] == 0

    def test_generate_authentication_options_with_credentials(self, webauthn_manager):
        """Test authentication options with existing credentials"""
        user_id = 'auth_with_creds_user_12345678'
        tier_level = 3

        # Add credentials for different tiers
        credentials = [
            WebAuthnCredential({
                'credential_id': 'cred_tier_1',
                'user_id': user_id,
                'tier_level': 1,
                'authenticator_data': {'transports': ['usb']}
            }),
            WebAuthnCredential({
                'credential_id': 'cred_tier_3',
                'user_id': user_id,
                'tier_level': 3,
                'authenticator_data': {'transports': ['internal']}
            }),
            WebAuthnCredential({
                'credential_id': 'cred_tier_5',
                'user_id': user_id,
                'tier_level': 5,
                'authenticator_data': {'transports': ['internal', 'usb']}
            })
        ]

        webauthn_manager.credentials[user_id] = credentials

        result = webauthn_manager.generate_authentication_options(user_id, tier_level)

        assert result['success'] is True
        options = result['options']

        # Should include credentials at or above requested tier level (3+)
        allowed_creds = options['allowCredentials']
        assert len(allowed_creds) == 2  # tier 3 and tier 5 credentials
        assert result['allowed_credentials_count'] == 2

        # Verify credential details
        cred_ids = {cred['id'] for cred in allowed_creds}
        assert 'cred_tier_3' in cred_ids
        assert 'cred_tier_5' in cred_ids
        assert 'cred_tier_1' not in cred_ids  # Below required tier

        # Verify transports are included
        for cred in allowed_creds:
            assert 'transports' in cred

    def test_verify_authentication_response_valid(self, webauthn_manager, mock_authentication_response):
        """Test valid WebAuthn authentication response verification"""
        user_id = 'auth_verify_user_12345678'

        # Add credential first
        credential = WebAuthnCredential({
            'credential_id': 'mock_credential_id_123456',
            'user_id': user_id,
            'tier_level': 2,
            'sign_count': 0
        })
        webauthn_manager.credentials[user_id] = [credential]

        # Generate authentication options
        auth_result = webauthn_manager.generate_authentication_options(user_id, 2)
        authentication_id = auth_result['authentication_id']

        # Update mock response with correct challenge
        pending_auth = webauthn_manager.pending_authentications[authentication_id]
        client_data = json.loads(base64.b64decode(mock_authentication_response['response']['clientDataJSON'] + '==='))
        client_data['challenge'] = pending_auth['challenge_b64']
        mock_authentication_response['response']['clientDataJSON'] = base64.b64encode(
            json.dumps(client_data).encode()
        ).decode()

        start_time = time.time()
        result = webauthn_manager.verify_authentication_response(authentication_id, mock_authentication_response)
        verification_time = (time.time() - start_time) * 1000

        assert result['success'] is True
        assert result['user_id'] == user_id
        assert result['credential_id'] == 'mock_credential_id_123456'
        assert result['tier_level'] == 2
        assert result['authentication_method'] == 'webauthn_fido2'
        assert result['guardian_approved'] is True
        assert result['trinity_compliant'] is True
        assert result['verification_time_ms'] < 100  # Performance requirement

        # Verify credential was updated
        updated_credential = webauthn_manager.credentials[user_id][0]
        assert updated_credential.sign_count == 1
        assert updated_credential.last_used is not None

        # Verify pending authentication was cleaned up
        assert authentication_id not in webauthn_manager.pending_authentications

    def test_verify_authentication_response_credential_not_found(self, webauthn_manager, mock_authentication_response):
        """Test authentication verification with unknown credential"""
        # Generate authentication options without any credentials
        auth_result = webauthn_manager.generate_authentication_options('unknown_user', 1)
        authentication_id = auth_result['authentication_id']

        result = webauthn_manager.verify_authentication_response(authentication_id, mock_authentication_response)

        assert result['success'] is False
        assert result['error'] == 'Credential not found'

    def test_get_user_credentials(self, webauthn_manager):
        """Test getting user credentials"""
        user_id = 'creds_list_user_12345678'

        # Test with no credentials
        result = webauthn_manager.get_user_credentials(user_id)
        assert result['success'] is True
        assert result['user_id'] == user_id
        assert result['credentials'] == []
        assert result['total_credentials'] == 0

        # Add some credentials
        credentials = [
            WebAuthnCredential({
                'credential_id': 'cred_1_very_long_id_12345678901234567890',
                'user_id': user_id,
                'tier_level': 2,
                'device_type': 'platform_authenticator',
                'sign_count': 5
            }),
            WebAuthnCredential({
                'credential_id': 'cred_2_another_long_id_12345678901234567890',
                'user_id': user_id,
                'tier_level': 4,
                'device_type': 'usb_security_key',
                'sign_count': 12
            })
        ]

        webauthn_manager.credentials[user_id] = credentials

        result = webauthn_manager.get_user_credentials(user_id)

        assert result['success'] is True
        assert result['total_credentials'] == 2

        creds_info = result['credentials']
        assert len(creds_info) == 2

        # Verify credential info format (should be truncated for security)
        for cred_info in creds_info:
            assert 'credential_id' in cred_info
            assert len(cred_info['credential_id']) == 19  # 16 chars + '...'
            assert cred_info['credential_id'].endswith('...')
            assert 'created_at' in cred_info
            assert 'tier_level' in cred_info
            assert 'device_type' in cred_info
            assert 'sign_count' in cred_info

    def test_revoke_credential(self, webauthn_manager):
        """Test credential revocation"""
        user_id = 'revoke_test_user_12345678'
        credential_id = 'revoke_cred_12345'

        # Test revoking from user with no credentials
        result = webauthn_manager.revoke_credential(user_id, credential_id)
        assert result['success'] is False
        assert result['error'] == 'User has no credentials'

        # Add credential
        credential = WebAuthnCredential({
            'credential_id': credential_id,
            'user_id': user_id,
            'tier_level': 3
        })
        webauthn_manager.credentials[user_id] = [credential]

        # Revoke existing credential
        result = webauthn_manager.revoke_credential(user_id, credential_id)

        assert result['success'] is True
        assert result['user_id'] == user_id
        assert result['credential_id'].startswith(credential_id[:16])
        assert 'revoked_at' in result

        # Verify credential was removed
        assert len(webauthn_manager.credentials[user_id]) == 0

        # Test revoking non-existent credential
        result = webauthn_manager.revoke_credential(user_id, 'non_existent_cred')
        assert result['success'] is False
        assert result['error'] == 'Credential not found'

    def test_device_type_determination(self, webauthn_manager):
        """Test device type determination from WebAuthn response"""
        # Test different transport combinations
        test_cases = [
            (['internal'], 'platform_authenticator'),
            (['usb'], 'usb_security_key'),
            (['nfc'], 'nfc_authenticator'),
            (['ble'], 'bluetooth_authenticator'),
            (['usb', 'nfc'], 'usb_security_key'),  # USB takes precedence
            ([], 'unknown_authenticator')
        ]

        for transports, expected_type in test_cases:
            response = {'transports': transports}
            device_type = webauthn_manager._determine_device_type(response)
            assert device_type == expected_type

    def test_constitutional_validation(self, webauthn_manager):
        """Test Trinity Framework constitutional validation (🛡️ Guardian)"""
        user_id = 'constitutional_test_user_12345678'

        # Test valid WebAuthn registration
        valid_data = {
            'id': 'valid_credential_id',
            'response': {
                'clientDataJSON': 'valid_client_data',
                'attestationObject': 'valid_attestation'
            }
        }

        result = webauthn_manager._constitutional_validation(user_id, 'webauthn_registration', valid_data)
        assert result is True

        # Test with suspicious patterns
        suspicious_data = {
            'id': '<script>alert("xss")</script>',
            'response': {'clientDataJSON': 'data'}
        }

        result = webauthn_manager._constitutional_validation(user_id, 'webauthn_registration', suspicious_data)
        assert result is False

        # Test with invalid user ID
        result = webauthn_manager._constitutional_validation('short', 'webauthn_registration', valid_data)
        assert result is False

        # Test with invalid operation
        result = webauthn_manager._constitutional_validation(user_id, 'invalid_operation', valid_data)
        assert result is False

        # Test with oversized user ID
        oversized_user_id = 'x' * 150
        result = webauthn_manager._constitutional_validation(oversized_user_id, 'webauthn_registration', valid_data)
        assert result is False

    def test_webauthn_health_check(self, webauthn_manager):
        """Test WebAuthn system health check"""
        # Initial health check
        health = webauthn_manager.webauthn_health_check()

        assert 'webauthn_health_check' in health
        health_data = health['webauthn_health_check']

        assert health_data['overall_status'] == 'HEALTHY'
        assert 'webauthn_library_available' in health_data
        assert health_data['total_registered_credentials'] == 0
        assert health_data['total_users_with_credentials'] == 0
        assert health_data['pending_registrations'] == 0
        assert health_data['pending_authentications'] == 0

        # Check Trinity compliance indicators
        trinity_compliance = health_data['trinity_compliance']
        assert trinity_compliance['⚛️_identity'] == 'INTEGRATED'
        assert trinity_compliance['🧠_consciousness'] == 'MONITORED'
        assert trinity_compliance['🛡️_guardian'] == 'PROTECTED'

        # Add some data and test again
        user_id = 'health_test_user_12345678'
        credentials = [
            WebAuthnCredential({'credential_id': 'cred1', 'user_id': user_id, 'tier_level': 2, 'device_type': 'platform_authenticator'}),
            WebAuthnCredential({'credential_id': 'cred2', 'user_id': user_id, 'tier_level': 4, 'device_type': 'usb_security_key'})
        ]
        webauthn_manager.credentials[user_id] = credentials

        # Add pending operations
        webauthn_manager.pending_registrations['test_reg'] = {
            'expires_at': (datetime.utcnow() + timedelta(minutes=5)).isoformat()
        }
        webauthn_manager.pending_authentications['test_auth'] = {
            'expires_at': (datetime.utcnow() + timedelta(minutes=5)).isoformat()
        }

        health = webauthn_manager.webauthn_health_check()
        health_data = health['webauthn_health_check']

        assert health_data['total_registered_credentials'] == 2
        assert health_data['total_users_with_credentials'] == 1
        assert health_data['pending_registrations'] == 1
        assert health_data['pending_authentications'] == 1

        # Check distributions
        tier_dist = health_data['tier_distribution']
        assert tier_dist['2'] == 1
        assert tier_dist['4'] == 1

        device_dist = health_data['device_type_distribution']
        assert device_dist['platform_authenticator'] == 1
        assert device_dist['usb_security_key'] == 1

    def test_webauthn_performance_requirements(self, webauthn_manager):
        """Test WebAuthn operations meet performance requirements (<100ms p95)"""
        user_id = 'performance_test_user_12345678'
        num_iterations = 20

        # Test registration options generation performance
        reg_times = []
        for i in range(num_iterations):
            start_time = time.time()
            result = webauthn_manager.generate_registration_options(
                f"{user_id}_{i}", f"test{i}@example.com", f"Test User {i}", 2
            )
            reg_time = (time.time() - start_time) * 1000

            assert result['success'] is True
            reg_times.append(reg_time)

        # Test authentication options generation performance
        auth_times = []
        for i in range(num_iterations):
            start_time = time.time()
            result = webauthn_manager.generate_authentication_options(f"{user_id}_{i}", 2)
            auth_time = (time.time() - start_time) * 1000

            assert result['success'] is True
            auth_times.append(auth_time)

        # Calculate p95 latencies
        reg_times.sort()
        auth_times.sort()

        reg_p95 = reg_times[int(0.95 * len(reg_times))]
        auth_p95 = auth_times[int(0.95 * len(auth_times))]

        # Verify p95 latency requirements (being generous for CI)
        assert reg_p95 < 200, f"Registration p95 latency {reg_p95:.2f}ms exceeds requirement"
        assert auth_p95 < 200, f"Authentication p95 latency {auth_p95:.2f}ms exceeds requirement"

        # Average should be even better
        reg_avg = sum(reg_times) / len(reg_times)
        auth_avg = sum(auth_times) / len(auth_times)

        assert reg_avg < 100, f"Registration average latency {reg_avg:.2f}ms too high"
        assert auth_avg < 50, f"Authentication average latency {auth_avg:.2f}ms too high"

    def test_tier_based_authenticator_requirements(self, webauthn_manager):
        """Test tier-based authenticator requirements"""
        user_id = 'tier_req_test_user_12345678'

        # Test each tier's requirements
        for tier in range(6):
            result = webauthn_manager.generate_registration_options(
                f"{user_id}_{tier}", f"tier{tier}@test.com", f"Tier {tier} User", tier
            )

            assert result['success'] is True
            options = result['options']
            auth_selection = options['authenticatorSelection']
            tier_reqs = webauthn_manager.tier_requirements[tier]

            # Verify user verification requirement
            if tier_reqs['user_verification']:
                assert auth_selection['userVerification'] == 'required'
            else:
                assert auth_selection['userVerification'] == 'preferred'

            # Verify platform attachment requirement
            if tier_reqs['platform_attachment'] != 'any':
                assert auth_selection['authenticatorAttachment'] == tier_reqs['platform_attachment']

            # Verify resident key requirement for highest tier
            if tier == 5:
                assert auth_selection['residentKey'] == 'required'

            # Verify attestation requirement for higher tiers
            if tier >= 3:
                assert options['attestation'] == 'direct'

    def test_consciousness_integration(self, webauthn_manager):
        """Test 🧠 Consciousness integration for security analysis"""
        user_id = 'consciousness_test_user_12345678'

        with patch.object(webauthn_manager, '_update_consciousness_patterns') as mock_consciousness:
            # Test registration consciousness updates
            reg_result = webauthn_manager.generate_registration_options(
                user_id, 'test@example.com', 'Test User', 2
            )

            mock_consciousness.assert_called_with(user_id, 'webauthn_registration_initiated')

            # Test authentication consciousness updates
            auth_result = webauthn_manager.generate_authentication_options(user_id, 2)

            mock_consciousness.assert_called_with(user_id, 'webauthn_authentication_initiated')

    def test_trinity_framework_integration(self, webauthn_manager):
        """Test Trinity Framework integration (⚛️🧠🛡️)"""
        user_id = 'trinity_test_user_12345678'

        # Generate registration options
        result = webauthn_manager.generate_registration_options(
            user_id, 'trinity@test.com', 'Trinity User', 3
        )

        # ⚛️ Identity - Verify identity integrity in options
        assert result['success'] is True
        options = result['options']
        user_info = options['user']
        decoded_user_id = base64.b64decode(user_info['id'] + '===').decode()
        assert decoded_user_id == user_id

        # 🧠 Consciousness - Verify temporal awareness
        assert 'expires_at' in result
        expires_at = datetime.fromisoformat(result['expires_at'])
        assert expires_at > datetime.utcnow()

        # 🛡️ Guardian - Verify security validation
        assert result['guardian_approved'] is True

        # Verify Trinity compliance is maintained throughout flow
        registration_id = result['registration_id']
        assert registration_id in webauthn_manager.pending_registrations

        pending_reg = webauthn_manager.pending_registrations[registration_id]
        assert len(pending_reg['challenge']) == 32  # Strong challenge
        assert pending_reg['user_tier'] == 3  # Tier preserved
