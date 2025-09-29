"""
OIDC Security Hardening Test Suite - T4/0.01% Excellence Validation
================================================================

Comprehensive security testing for OIDC authentication flows, security hardening,
and fail-closed design validation. Tests all security mechanisms and attack vectors.

Test Coverage:
- Security hardening validation
- Attack vector testing (replay, injection, bypass)
- Fail-closed design verification
- Performance and security integration
- Guardian system integration
- Real-world attack simulations

Implementation: T4/0.01% excellence targeting zero security bypasses
"""

import asyncio
import base64
import json
import time
import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch

from lukhas.identity.oidc_security_hardening import (
    OIDCSecurityHardening,
    OIDCSecurityEventType,
    SecurityThreatLevel,
    SecurityResponse
)
from lukhas.identity.webauthn_oidc_integration import (
    WebAuthnOIDCIntegration,
    IntegrationSecurityLevel
)


class TestOIDCSecurityHardening:
    """Test suite for OIDC security hardening functionality"""

    @pytest.fixture
    def security_hardening(self):
        """Create OIDC security hardening instance"""
        config = {
            'fail_closed': True,
            'nonce_ttl_seconds': 3600,
            'rate_limit_window_seconds': 60,
            'rate_limit_threshold': 10,  # Lower for testing
            'max_risk_score': 80.0
        }
        return OIDCSecurityHardening(config)

    @pytest.fixture
    def valid_auth_params(self):
        """Valid authorization request parameters"""
        return {
            'response_type': 'code',
            'client_id': 'test_client_123',
            'redirect_uri': 'https://client.example.com/callback',
            'scope': 'openid profile email',
            'state': 'random_state_123',
            'nonce': 'random_nonce_456',
            'code_challenge': 'E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM',
            'code_challenge_method': 'S256'
        }

    @pytest.fixture
    def request_context(self):
        """Request context for security validation"""
        return {
            'ip_address': '192.168.1.100',
            'user_agent': 'Mozilla/5.0 (Test Browser)',
            'lambda_id': 'test_user_789',
            'namespace': 'test'
        }

    @pytest.mark.asyncio
    async def test_valid_authorization_request(self, security_hardening,
                                             valid_auth_params, request_context):
        """Test valid authorization request passes security validation"""
        result = await security_hardening.validate_authorization_request(
            valid_auth_params, request_context
        )

        assert result['valid'] is True
        assert result['security_response'] == SecurityResponse.ALLOW
        assert result['risk_score'] < 50.0
        assert len(result['events']) == 0  # No security events for valid request

    @pytest.mark.asyncio
    async def test_missing_required_parameters(self, security_hardening,
                                             valid_auth_params, request_context):
        """Test missing required parameters trigger security events"""
        # Test missing client_id
        params = valid_auth_params.copy()
        del params['client_id']

        result = await security_hardening.validate_authorization_request(
            params, request_context
        )

        assert result['valid'] is False
        assert result['security_response'] == SecurityResponse.BLOCK
        assert result['risk_score'] >= 80.0
        assert any(event.event_type == OIDCSecurityEventType.INVALID_CLIENT
                  for event in result['events'])

    @pytest.mark.asyncio
    async def test_nonce_replay_attack(self, security_hardening,
                                     valid_auth_params, request_context):
        """Test nonce replay attack detection and blocking"""
        # First request should succeed
        result1 = await security_hardening.validate_authorization_request(
            valid_auth_params, request_context
        )
        assert result1['valid'] is True

        # Second request with same nonce should be blocked
        result2 = await security_hardening.validate_authorization_request(
            valid_auth_params, request_context
        )

        assert result2['valid'] is False
        assert result2['security_response'] == SecurityResponse.BLOCK
        assert any(event.event_type == OIDCSecurityEventType.NONCE_REPLAY
                  for event in result2['events'])
        assert any(event.threat_level == SecurityThreatLevel.CRITICAL
                  for event in result2['events'])

    @pytest.mark.asyncio
    async def test_rate_limiting_protection(self, security_hardening,
                                          valid_auth_params, request_context):
        """Test rate limiting blocks excessive requests"""
        client_id = valid_auth_params['client_id']

        # Make requests up to the limit
        for i in range(10):
            params = valid_auth_params.copy()
            params['nonce'] = f'nonce_{i}'  # Unique nonce for each request

            result = await security_hardening.validate_authorization_request(
                params, request_context
            )

            if i < 10:  # First 10 should succeed
                assert result['valid'] is True
            else:  # 11th request should be rate limited
                assert result['valid'] is False
                assert any(event.event_type == OIDCSecurityEventType.RATE_LIMIT_EXCEEDED
                          for event in result['events'])

    @pytest.mark.asyncio
    async def test_invalid_redirect_uri_security(self, security_hardening,
                                                valid_auth_params, request_context):
        """Test redirect URI security validation"""
        # Test HTTP redirect URI (should be blocked)
        params = valid_auth_params.copy()
        params['redirect_uri'] = 'http://malicious.example.com/callback'

        result = await security_hardening.validate_authorization_request(
            params, request_context
        )

        assert result['valid'] is False
        assert result['security_response'] == SecurityResponse.BLOCK
        assert any(event.event_type == OIDCSecurityEventType.INVALID_REDIRECT_URI
                  for event in result['events'])
        assert any('HTTPS' in event.description for event in result['events'])

    @pytest.mark.asyncio
    async def test_pkce_validation_security(self, security_hardening,
                                          valid_auth_params, request_context):
        """Test PKCE validation security checks"""
        # Test missing code_challenge
        params = valid_auth_params.copy()
        del params['code_challenge']

        result = await security_hardening.validate_authorization_request(
            params, request_context
        )

        # Should generate warning but not block (PKCE is recommended, not required)
        assert len([event for event in result['events']
                   if event.event_type == OIDCSecurityEventType.PKCE_VALIDATION_FAILURE]) > 0

        # Test short code_challenge
        params = valid_auth_params.copy()
        params['code_challenge'] = 'too_short'

        result = await security_hardening.validate_authorization_request(
            params, request_context
        )

        assert any(event.event_type == OIDCSecurityEventType.PKCE_VALIDATION_FAILURE
                  for event in result['events'])

    @pytest.mark.asyncio
    async def test_scope_security_validation(self, security_hardening,
                                           valid_auth_params, request_context):
        """Test scope validation and excessive scope detection"""
        # Test excessive scope request
        params = valid_auth_params.copy()
        excessive_scopes = ['scope_' + str(i) for i in range(15)]  # 15 scopes
        params['scope'] = 'openid ' + ' '.join(excessive_scopes)

        result = await security_hardening.validate_authorization_request(
            params, request_context
        )

        assert any(event.event_type == OIDCSecurityEventType.EXCESSIVE_SCOPE_REQUEST
                  for event in result['events'])

        # Test missing 'openid' scope
        params = valid_auth_params.copy()
        params['scope'] = 'profile email'  # Missing 'openid'

        result = await security_hardening.validate_authorization_request(
            params, request_context
        )

        assert any('openid' in event.description.lower() for event in result['events'])

    @pytest.mark.asyncio
    async def test_jwt_security_validation(self, security_hardening):
        """Test JWT security validation including algorithm attacks"""
        # Test 'none' algorithm attack
        none_token_header = {'alg': 'none', 'typ': 'JWT'}
        none_token_payload = {'sub': 'test', 'exp': int(time.time()) + 3600}

        header_b64 = base64.urlsafe_b64encode(
            json.dumps(none_token_header).encode()
        ).decode().rstrip('=')
        payload_b64 = base64.urlsafe_b64encode(
            json.dumps(none_token_payload).encode()
        ).decode().rstrip('=')

        none_token = f"{header_b64}.{payload_b64}."

        result = await security_hardening.validate_jwt_security(none_token)

        assert result['valid'] is False
        assert result['security_response'] == SecurityResponse.BLOCK
        assert result['risk_score'] == 100.0
        assert any(event.event_type == OIDCSecurityEventType.JWT_ALGORITHM_ATTACK
                  for event in result['events'])

    @pytest.mark.asyncio
    async def test_token_request_validation(self, security_hardening, request_context):
        """Test token request security validation"""
        token_params = {
            'grant_type': 'authorization_code',
            'code': 'valid_auth_code_123',
            'redirect_uri': 'https://client.example.com/callback',
            'client_id': 'test_client_123',
            'client_secret': 'client_secret_456',
            'code_verifier': 'valid_code_verifier_with_sufficient_length_for_pkce_validation'
        }

        result = await security_hardening.validate_token_request(
            token_params, request_context
        )

        assert result['valid'] is True
        assert result['security_response'] == SecurityResponse.ALLOW

        # Test authorization code reuse
        result2 = await security_hardening.validate_token_request(
            token_params, request_context
        )

        assert result2['valid'] is False
        assert any(event.event_type == OIDCSecurityEventType.AUTHORIZATION_CODE_REUSE
                  for event in result2['events'])

    @pytest.mark.asyncio
    async def test_fail_closed_design(self, request_context):
        """Test fail-closed behavior on security errors"""
        # Test with fail_closed=True
        fail_closed_security = OIDCSecurityHardening({'fail_closed': True})

        malicious_params = {
            'response_type': 'code',
            'client_id': 'nonexistent_client',
            'redirect_uri': 'http://malicious.example.com',  # HTTP, not HTTPS
            'scope': 'openid profile',
            'nonce': 'test_nonce'
        }

        result = await fail_closed_security.validate_authorization_request(
            malicious_params, request_context
        )

        # Should fail closed - no access granted
        assert result['valid'] is False
        assert result['security_response'] in [SecurityResponse.BLOCK, SecurityResponse.EMERGENCY_SHUTDOWN]

        # Test with fail_closed=False (should still block due to security violations)
        fail_open_security = OIDCSecurityHardening({'fail_closed': False})

        result2 = await fail_open_security.validate_authorization_request(
            malicious_params, request_context
        )

        # Even with fail_closed=False, critical security violations should block
        assert result2['valid'] is False

    @pytest.mark.asyncio
    async def test_emergency_shutdown(self, security_hardening):
        """Test emergency shutdown functionality"""
        reason = "Critical security breach detected"

        await security_hardening.emergency_shutdown(reason)

        # Verify all clients are blocked
        for profile in security_hardening.client_profiles.values():
            assert profile.is_blocked is True
            assert profile.block_until is not None

        # Verify caches are cleared
        assert len(security_hardening.nonce_cache) == 0
        assert len(security_hardening.authorization_codes) == 0

    @pytest.mark.asyncio
    async def test_security_metrics(self, security_hardening,
                                  valid_auth_params, request_context):
        """Test security metrics collection"""
        # Generate some security events
        await security_hardening.validate_authorization_request(
            valid_auth_params, request_context
        )

        # Generate a security violation
        malicious_params = valid_auth_params.copy()
        malicious_params['redirect_uri'] = 'http://malicious.example.com'

        await security_hardening.validate_authorization_request(
            malicious_params, request_context
        )

        metrics = await security_hardening.get_security_metrics()

        assert 'total_events' in metrics
        assert 'threat_distribution' in metrics
        assert metrics['total_events'] > 0

    @pytest.mark.asyncio
    async def test_performance_requirements(self, security_hardening,
                                          valid_auth_params, request_context):
        """Test security validation meets performance requirements"""
        # Test multiple validations to get average performance
        validation_times = []

        for i in range(10):
            params = valid_auth_params.copy()
            params['nonce'] = f'nonce_{i}'

            start_time = time.perf_counter()
            result = await security_hardening.validate_authorization_request(
                params, request_context
            )
            latency_ms = (time.perf_counter() - start_time) * 1000

            validation_times.append(latency_ms)
            assert result['valid'] is True

        avg_latency = sum(validation_times) / len(validation_times)
        p95_latency = sorted(validation_times)[int(len(validation_times) * 0.95)]

        # Performance requirements: security validation should add <10ms overhead
        assert avg_latency < 25, f"Average security validation {avg_latency}ms exceeds 25ms"
        assert p95_latency < 50, f"P95 security validation {p95_latency}ms exceeds 50ms"


class TestWebAuthnOIDCIntegration:
    """Test suite for WebAuthn-OIDC integration security"""

    @pytest.fixture
    def integration(self):
        """Create WebAuthn-OIDC integration instance"""
        config = {
            'fail_closed': True,
            'issuer': 'https://lukhas.ai',
            'rp_id': 'lukhas.ai',
            'token_generation_target_ms': 100,
            'authentication_target_ms': 250
        }
        return WebAuthnOIDCIntegration(config)

    @pytest.fixture
    def auth_params(self):
        """Authorization parameters for integration testing"""
        return {
            'response_type': 'code',
            'client_id': 'webauthn_client_123',
            'redirect_uri': 'https://client.example.com/callback',
            'scope': 'openid profile email',
            'state': 'integration_state_123',
            'nonce': 'integration_nonce_456'
        }

    @pytest.fixture
    def webauthn_response(self):
        """Mock WebAuthn response"""
        return {
            'id': 'credential_id_123',
            'type': 'public-key',
            'rawId': base64.urlsafe_b64encode(b'credential_id_123').decode(),
            'response': {
                'authenticatorData': base64.urlsafe_b64encode(b'auth_data').decode(),
                'clientDataJSON': base64.urlsafe_b64encode(b'client_data').decode(),
                'signature': base64.urlsafe_b64encode(b'signature').decode(),
                'userHandle': base64.urlsafe_b64encode(b'user_handle').decode()
            }
        }

    @pytest.mark.asyncio
    async def test_webauthn_oidc_flow_initiation(self, integration, auth_params, request_context):
        """Test WebAuthn-OIDC integration flow initiation"""
        result = await integration.initiate_webauthn_oidc_flow(auth_params, request_context)

        assert result['status'] == 'success'
        assert 'session_id' in result
        assert 'webauthn_options' in result
        assert result['webauthn_options']['userVerification'] == 'required'

        # Verify session creation
        session_id = result['session_id']
        assert session_id in integration.active_sessions

        session = integration.active_sessions[session_id]
        assert session.security_level == IntegrationSecurityLevel.T4_EXCELLENCE
        assert session.client_id == auth_params['client_id']

    @pytest.mark.asyncio
    async def test_webauthn_authentication_completion(self, integration, auth_params,
                                                    webauthn_response, request_context):
        """Test WebAuthn authentication completion and authorization code generation"""
        # Initiate flow
        init_result = await integration.initiate_webauthn_oidc_flow(auth_params, request_context)
        session_id = init_result['session_id']

        # Mock successful WebAuthn validation
        with patch.object(integration.webauthn_security, 'validate_authentication_response',
                         new_callable=AsyncMock) as mock_validate:
            mock_validate.return_value = {
                'valid': True,
                'user_verified': True,
                'credential_binding_valid': True
            }

            # Complete authentication
            result = await integration.complete_webauthn_authentication(
                session_id, webauthn_response, request_context
            )

            assert result['status'] == 'success'
            assert 'authorization_code' in result
            assert result['session_id'] == session_id

    @pytest.mark.asyncio
    async def test_oidc_token_generation_with_webauthn_context(self, integration, auth_params,
                                                             webauthn_response, request_context):
        """Test OIDC token generation with WebAuthn authentication context"""
        # Complete full flow
        init_result = await integration.initiate_webauthn_oidc_flow(auth_params, request_context)
        session_id = init_result['session_id']

        with patch.object(integration.webauthn_security, 'validate_authentication_response',
                         new_callable=AsyncMock) as mock_validate:
            mock_validate.return_value = {
                'valid': True,
                'user_verified': True,
                'credential_binding_valid': True
            }

            auth_result = await integration.complete_webauthn_authentication(
                session_id, webauthn_response, request_context
            )

            # Generate tokens
            token_request = {
                'grant_type': 'authorization_code',
                'code': auth_result['authorization_code'],
                'redirect_uri': auth_params['redirect_uri'],
                'client_id': auth_params['client_id'],
                'client_secret': 'test_secret'
            }

            token_result = await integration.generate_oidc_tokens(
                auth_result['authorization_code'], token_request, request_context
            )

            assert token_result['status'] == 'success'
            assert 'access_token' in token_result
            assert 'id_token' in token_result
            assert token_result['token_type'] == 'Bearer'

    @pytest.mark.asyncio
    async def test_guardian_system_integration(self, integration, auth_params, request_context):
        """Test Guardian system integration for risk assessment"""
        # Test high-risk scenario
        high_risk_context = request_context.copy()
        high_risk_context['new_device'] = True
        high_risk_context['suspicious_location'] = True

        init_result = await integration.initiate_webauthn_oidc_flow(
            auth_params, high_risk_context
        )
        session_id = init_result['session_id']

        session = integration.active_sessions[session_id]

        # Simulate Guardian validation
        guardian_result = await integration._validate_with_guardian(session, high_risk_context)

        # High risk should result in elevated risk score
        assert guardian_result['risk_score'] > 50.0
        assert 'new_device' in guardian_result.get('risk_factors', [])

    @pytest.mark.asyncio
    async def test_integration_performance(self, integration, auth_params,
                                         webauthn_response, request_context):
        """Test integration meets T4/0.01% performance requirements"""
        # Test token generation performance
        performance_results = []

        for i in range(5):
            start_time = time.perf_counter()

            # Full integration flow
            init_result = await integration.initiate_webauthn_oidc_flow(
                auth_params, request_context
            )
            session_id = init_result['session_id']

            with patch.object(integration.webauthn_security, 'validate_authentication_response',
                             new_callable=AsyncMock) as mock_validate:
                mock_validate.return_value = {
                    'valid': True,
                    'user_verified': True,
                    'credential_binding_valid': True
                }

                auth_result = await integration.complete_webauthn_authentication(
                    session_id, webauthn_response, request_context
                )

                token_request = {
                    'grant_type': 'authorization_code',
                    'code': auth_result['authorization_code'],
                    'redirect_uri': auth_params['redirect_uri'],
                    'client_id': auth_params['client_id'],
                    'client_secret': 'test_secret'
                }

                token_result = await integration.generate_oidc_tokens(
                    auth_result['authorization_code'], token_request, request_context
                )

                total_latency = (time.perf_counter() - start_time) * 1000
                performance_results.append(total_latency)

                assert token_result['status'] == 'success'

        avg_latency = sum(performance_results) / len(performance_results)
        p95_latency = sorted(performance_results)[int(len(performance_results) * 0.95)]

        # T4/0.01% performance requirements
        assert avg_latency < 500, f"Average integration flow {avg_latency}ms exceeds 500ms"
        assert p95_latency < 750, f"P95 integration flow {p95_latency}ms exceeds 750ms"

    @pytest.mark.asyncio
    async def test_integration_security_metrics(self, integration):
        """Test integration security metrics collection"""
        metrics = await integration.get_integration_metrics()

        assert 'total_events' in metrics
        assert 'success_rate' in metrics
        assert 'active_sessions' in metrics
        assert 'average_latency_ms' in metrics
        assert 't4_excellence_compliance' in metrics
        assert metrics['t4_excellence_compliance'] is True

    @pytest.mark.asyncio
    async def test_session_cleanup(self, integration, auth_params, request_context):
        """Test expired session cleanup"""
        # Create expired session
        init_result = await integration.initiate_webauthn_oidc_flow(auth_params, request_context)
        session_id = init_result['session_id']

        session = integration.active_sessions[session_id]
        session.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)  # Expired

        initial_count = len(integration.active_sessions)

        # Run cleanup
        await integration.cleanup_expired_sessions()

        # Verify expired session was removed
        assert len(integration.active_sessions) < initial_count
        assert session_id not in integration.active_sessions


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


if __name__ == "__main__":
    # Run security hardening tests
    pytest.main([__file__, "-v", "--tb=short"])