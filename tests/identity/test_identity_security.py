"""
🛡️ Identity Module Security Test Suite
======================================

Comprehensive security tests for LUKHAS Identity module authentication flows.
Tests security vulnerabilities, attack vectors, and Guardian Framework protection.

Trinity Framework: ⚛️ (Identity), 🧠 (Consciousness), 🛡️ (Guardian)
"""

import base64
import hashlib
import json
import os
import secrets

# Import system under test
import sys
import time
from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

identity_path = os.path.join(os.path.dirname(__file__), '..', '..', 'identity')
governance_path = os.path.join(os.path.dirname(__file__), '..', '..', 'governance', 'identity')
sys.path.extend([identity_path, governance_path])

try:
    from governance.identity.auth_backend.qr_entropy_generator import QREntropyGenerator
    from governance.identity.core.auth.oauth2_oidc_provider import OAuth2OIDCProvider
    from governance.identity.core.auth.webauthn_manager import WebAuthnManager
    from identity_core import AccessTier, IdentityCore
    COMPONENTS_AVAILABLE = True
except ImportError as e:
    COMPONENTS_AVAILABLE = False
    pytest.skip(f"Identity components not available: {e}", allow_module_level=True)


class SecurityTestUtils:
    """Utility class for security testing"""

    @staticmethod
    def generate_malicious_payloads():
        """Generate common malicious payloads for injection testing"""
        return [
            # XSS payloads
            '<script>alert("xss")</script>',
            'javascript:alert("xss")',
            '<img src=x onerror=alert("xss")>',
            '"><script>alert("xss")</script>',

            # SQL injection payloads
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "' UNION SELECT * FROM sensitive_data --",

            # Command injection payloads
            '; cat /etc/passwd',
            '| whoami',
            '$(cat /etc/passwd)',
            '`cat /etc/passwd`',

            # Path traversal payloads
            '../../../etc/passwd',
            '..\\..\\..\\windows\\system32\\config\\sam',
            '%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd',

            # LDAP injection payloads
            '*)(uid=*))(|(uid=*',
            '*)((|uid=*))',

            # NoSQL injection payloads
            '{"$ne": null}',
            '{"$regex": ".*"}',

            # Format string attacks
            '%x%x%x%x%x%x%x%x',
            '%p%p%p%p%p%p%p%p',

            # Buffer overflow attempts
            'A' * 10000,
            '\x00' * 1000,

            # Unicode attacks
            '\u003cscript\u003ealert("xss")\u003c/script\u003e',
            '\uff1cscript\uff1ealert("xss")\uff1c/script\uff1e'
        ]

    @staticmethod
    def generate_oversized_data():
        """Generate oversized data for boundary testing"""
        return {
            'large_string': 'X' * 100000,  # 100KB string
            'huge_json': json.dumps({'key': 'value' * 10000}),
            'binary_blob': secrets.token_bytes(50000),  # 50KB binary
            'unicode_flood': '🚀' * 50000,  # 50K unicode characters
        }

    @staticmethod
    def generate_timing_attack_tokens():
        """Generate tokens for timing attack testing"""
        valid_token = "LUKHAS-T3-" + "a" * 32
        invalid_tokens = [
            "LUKHAS-T3-" + "b" * 32,  # Similar length, different content
            "LUKHAS-T3-" + "a" * 31 + "b",  # One character different
            "LUKHAS-T3-" + "c" * 32,  # Completely different
            "LUKHAS-T3-" + "a" * 16 + "b" * 16,  # Half different
        ]
        return valid_token, invalid_tokens


class TestIdentityCoreSecurityValidation:
    """Security tests for IdentityCore component"""

    @pytest.fixture
    def identity_core(self):
        """Create identity core for security testing"""
        return IdentityCore(data_dir="security_test_data")

    @pytest.fixture
    def malicious_payloads(self):
        """Get malicious payloads for testing"""
        return SecurityTestUtils.generate_malicious_payloads()

    def test_token_validation_injection_resistance(self, identity_core, malicious_payloads):
        """Test token validation resistance to injection attacks"""
        print("🔒 Testing token validation injection resistance")

        for payload in malicious_payloads:
            # Test malicious token input
            is_valid, metadata = identity_core.validate_symbolic_token(payload)
            assert is_valid is False, f"Malicious token '{payload[:50]}...' was incorrectly validated"
            assert metadata is None, f"Metadata returned for malicious token '{payload[:50]}...'"

        print("✅ Token validation resistant to injection attacks")

    def test_token_validation_timing_attack_resistance(self, identity_core):
        """Test token validation resistance to timing attacks"""
        print("🕐 Testing timing attack resistance")

        # Create a valid token first
        valid_token = identity_core.create_token(
            'timing_test_user_12345678', AccessTier.T3, {'consent': True}
        )

        valid_token_base, invalid_tokens = SecurityTestUtils.generate_timing_attack_tokens()

        # Measure validation times for valid token
        valid_times = []
        for _ in range(50):
            start_time = time.perf_counter()
            identity_core.validate_symbolic_token(valid_token)
            end_time = time.perf_counter()
            valid_times.append(end_time - start_time)

        # Measure validation times for invalid tokens with varying similarity
        invalid_times = []
        for invalid_token in invalid_tokens:
            token_times = []
            for _ in range(50):
                start_time = time.perf_counter()
                identity_core.validate_symbolic_token(invalid_token)
                end_time = time.perf_counter()
                token_times.append(end_time - start_time)
            invalid_times.append(token_times)

        # Analyze timing patterns
        valid_avg = sum(valid_times) / len(valid_times)

        for i, times in enumerate(invalid_times):
            invalid_avg = sum(times) / len(times)
            time_ratio = abs(valid_avg - invalid_avg) / valid_avg

            # Timing differences should be minimal (< 20% variation)
            assert time_ratio < 0.2, f"Timing attack vulnerability detected: {time_ratio:.2%} variation for token {i}"

        print("✅ Token validation resistant to timing attacks")

    def test_user_metadata_sanitization(self, identity_core, malicious_payloads):
        """Test user metadata sanitization against malicious input"""
        print("🧹 Testing metadata sanitization")

        for payload in malicious_payloads:
            malicious_metadata = {
                'user_id': f'malicious_user_{payload}',
                'tier': f'T1{payload}',
                'consent': payload,
                'trinity_score': payload,
                'drift_score': payload,
                'cultural_profile': payload
            }

            # Should handle malicious metadata gracefully
            try:
                tier, permissions = identity_core.resolve_access_tier(malicious_metadata)

                # Should default to safe values
                assert tier == AccessTier.T1  # Safe default tier
                assert isinstance(permissions, dict)

            except Exception as e:
                # Exceptions are acceptable for malformed input, but should not crash
                assert "malicious" not in str(e).lower(), f"Error message reveals attack: {e}"

        print("✅ Metadata sanitization working correctly")

    def test_glyph_generation_security(self, identity_core):
        """Test identity glyph generation security"""
        print("✨ Testing glyph generation security")

        # Test with malicious seeds
        malicious_seeds = [
            '../../../etc/passwd',
            '<script>alert("xss")</script>',
            'A' * 10000,  # Very long seed
            '\x00\x01\x02\x03',  # Binary data
            '🚀💀🔥' * 1000  # Unicode flood
        ]

        for seed in malicious_seeds:
            glyphs = identity_core.generate_identity_glyph(seed)

            # Should always return valid glyphs regardless of input
            assert isinstance(glyphs, list)
            assert len(glyphs) >= 3
            assert all(isinstance(glyph, str) for glyph in glyphs)

            # Should not contain any raw malicious input
            glyph_str = ''.join(glyphs)
            assert '<script>' not in glyph_str
            assert '/etc/passwd' not in glyph_str

        print("✅ Glyph generation secure against malicious input")

    def test_token_entropy_validation(self, identity_core):
        """Test token entropy and randomness"""
        print("🎲 Testing token entropy validation")

        # Generate multiple tokens to analyze randomness
        tokens = []
        for i in range(1000):
            token = identity_core.create_token(
                f'entropy_test_user_{i:08d}',
                AccessTier.T2,
                {'consent': True}
            )
            tokens.append(token)

        # Extract random components from tokens
        random_parts = []
        for token in tokens:
            parts = token.split('-')
            if len(parts) >= 3:
                random_parts.append(parts[2])  # The random component

        # Test for uniqueness (no collisions)
        unique_parts = set(random_parts)
        collision_rate = (len(random_parts) - len(unique_parts)) / len(random_parts)
        assert collision_rate == 0, f"Token collision rate {collision_rate:.2%} detected"

        # Test entropy distribution (chi-square test on first bytes)
        if random_parts:
            first_chars = [part[0] if part else '0' for part in random_parts]
            char_counts = {}
            for char in first_chars:
                char_counts[char] = char_counts.get(char, 0) + 1

            # Should have reasonable distribution (not too skewed)
            max_count = max(char_counts.values())
            min_count = min(char_counts.values())
            skew_ratio = max_count / min_count if min_count > 0 else float('inf')

            # Allow some skew but not extreme bias
            assert skew_ratio < 5, f"Token entropy skew ratio {skew_ratio:.2f} too high"

        print("✅ Token entropy validation passed")

    def test_constitutional_validation_bypass_attempts(self, identity_core):
        """Test attempts to bypass constitutional validation"""
        print("🛡️ Testing constitutional validation bypass attempts")

        bypass_attempts = [
            # Null byte injection
            {'user_id': 'valid_user\x00malicious', 'tier': 'T3'},

            # Unicode normalization attacks
            {'user_id': 'valid_user\u200d\u200c', 'tier': 'T3'},

            # Mixed encoding
            {'user_id': 'valid_user%00', 'tier': 'T3'},

            # Case manipulation
            {'user_id': 'VaLiD_uSeR_12345678', 'tier': 't3'},

            # Excessive length
            {'user_id': 'x' * 1000000, 'tier': 'T3'},

            # Special characters
            {'user_id': 'user/../admin', 'tier': 'T5'},

            # JSON injection attempt
            {'user_id': '{"admin": true}', 'tier': 'T5'}
        ]

        for attempt in bypass_attempts:
            # Constitutional validation should catch these
            tier, permissions = identity_core.resolve_access_tier(attempt)

            # Should default to safe tier
            assert tier == AccessTier.T1, f"Bypass attempt succeeded: {attempt}"

            # Should not grant admin permissions
            assert not permissions.get('can_admin', False), f"Admin bypass detected: {attempt}"

        print("✅ Constitutional validation bypass attempts blocked")


class TestWebAuthnSecurityValidation:
    """Security tests for WebAuthn/FIDO2 component"""

    @pytest.fixture
    def webauthn_manager(self):
        """Create WebAuthn manager for security testing"""
        config = {
            'rp_id': 'security.test.lukhas.ai',
            'rp_name': 'LUKHAS Security Test',
            'origin': 'https://security.test.lukhas.ai'
        }
        return WebAuthnManager(config=config)

    def test_webauthn_challenge_security(self, webauthn_manager):
        """Test WebAuthn challenge generation security"""
        print("🔐 Testing WebAuthn challenge security")

        challenges = []
        for i in range(1000):
            result = webauthn_manager.generate_registration_options(
                f'challenge_test_user_{i:08d}',
                f'test{i}@security.test',
                f'Test User {i}',
                2
            )

            assert result['success'] is True
            options = result['options']
            challenges.append(options['challenge'])

        # Test challenge uniqueness
        unique_challenges = set(challenges)
        assert len(unique_challenges) == len(challenges), "WebAuthn challenge collision detected"

        # Test challenge length and format
        for challenge in challenges[:10]:  # Sample first 10
            # Should be base64url encoded
            try:
                decoded = base64.urlsafe_b64decode(challenge + '===')
                assert len(decoded) >= 16, f"Challenge too short: {len(decoded)} bytes"
            except Exception:
                pytest.fail(f"Invalid challenge format: {challenge}")

        print("✅ WebAuthn challenges are cryptographically secure")

    def test_webauthn_origin_validation(self, webauthn_manager):
        """Test WebAuthn origin validation"""
        print("🌐 Testing WebAuthn origin validation")

        # Generate registration options
        reg_result = webauthn_manager.generate_registration_options(
            'origin_test_user_12345678',
            'origin@test.com',
            'Origin Test User',
            2
        )
        registration_id = reg_result['registration_id']

        # Test with malicious origins
        malicious_origins = [
            'https://evil.com',
            'http://security.test.lukhas.ai',  # Wrong protocol
            'https://security.test.lukhas.ai.evil.com',  # Subdomain attack
            'javascript:alert("xss")',
            'data:text/html,<script>alert("xss")</script>',
            'file:///etc/passwd',
            'ftp://malicious.com',
        ]

        for malicious_origin in malicious_origins:
            mock_response = {
                'id': 'test_credential_id',
                'response': {
                    'clientDataJSON': base64.b64encode(json.dumps({
                        'type': 'webauthn.create',
                        'challenge': webauthn_manager.pending_registrations[registration_id]['challenge_b64'],
                        'origin': malicious_origin
                    }).encode()).decode(),
                    'attestationObject': base64.b64encode(b'mock_attestation').decode(),
                    'publicKey': 'mock_public_key'
                }
            }

            result = webauthn_manager.verify_registration_response(registration_id, mock_response)
            assert result['success'] is False, f"Malicious origin accepted: {malicious_origin}"
            assert result['error'] == 'Origin mismatch', f"Wrong error for origin {malicious_origin}"

        print("✅ WebAuthn origin validation working correctly")

    def test_webauthn_replay_attack_protection(self, webauthn_manager):
        """Test WebAuthn replay attack protection"""
        print("🔄 Testing WebAuthn replay attack protection")

        user_id = 'replay_test_user_12345678'

        # Create mock credential
        from governance.identity.core.auth.webauthn_manager import WebAuthnCredential
        credential = WebAuthnCredential({
            'credential_id': 'replay_test_credential',
            'user_id': user_id,
            'tier_level': 2,
            'sign_count': 5  # Starting count
        })
        webauthn_manager.credentials[user_id] = [credential]

        # Generate authentication options
        auth_result = webauthn_manager.generate_authentication_options(user_id, 2)
        auth_id = auth_result['authentication_id']

        # Create valid authentication response
        pending_auth = webauthn_manager.pending_authentications[auth_id]
        valid_response = {
            'id': 'replay_test_credential',
            'response': {
                'clientDataJSON': base64.b64encode(json.dumps({
                    'type': 'webauthn.get',
                    'challenge': pending_auth['challenge_b64'],
                    'origin': 'https://security.test.lukhas.ai'
                }).encode()).decode(),
                'authenticatorData': base64.b64encode(b'mock_auth_data').decode(),
                'signature': base64.b64encode(b'mock_signature').decode()
            }
        }

        # First authentication should succeed
        verify_result = webauthn_manager.verify_authentication_response(auth_id, valid_response)
        assert verify_result['success'] is True
        assert verify_result['sign_count'] == 6  # Should increment

        # Generate new authentication for replay test
        auth_result2 = webauthn_manager.generate_authentication_options(user_id, 2)
        auth_id2 = auth_result2['authentication_id']

        # Attempt replay with old challenge (should fail)
        replay_response = valid_response.copy()
        result = webauthn_manager.verify_authentication_response(auth_id2, replay_response)
        assert result['success'] is False, "Replay attack succeeded"

        print("✅ WebAuthn replay attack protection working")

    def test_webauthn_tier_security_enforcement(self, webauthn_manager):
        """Test WebAuthn tier-based security enforcement"""
        print("🔒 Testing WebAuthn tier security enforcement")

        # Test each tier's security requirements
        for tier in range(6):  # Tiers 0-5
            user_id = f'tier_security_user_{tier}_12345678'

            reg_result = webauthn_manager.generate_registration_options(
                user_id, f'tier{tier}@test.com', f'Tier {tier} User', tier
            )

            options = reg_result['options']
            auth_selection = options['authenticatorSelection']
            tier_reqs = webauthn_manager.tier_requirements[tier]

            # Verify tier requirements are enforced
            if tier_reqs['user_verification']:
                assert auth_selection['userVerification'] == 'required'

            if tier >= 3:  # Higher tiers require platform attachment
                if 'authenticatorAttachment' in auth_selection:
                    assert auth_selection['authenticatorAttachment'] == 'platform'

            if tier >= 3:  # Higher tiers require direct attestation
                assert options['attestation'] == 'direct'

            if tier >= 4:  # Highest tiers get additional extensions
                assert options['extensions']['hmacCreateSecret'] is True

        print("✅ WebAuthn tier security enforcement working")


class TestOAuth2SecurityValidation:
    """Security tests for OAuth2/OIDC component"""

    @pytest.fixture
    def oauth_provider(self):
        """Create OAuth provider for security testing"""
        config = {
            'issuer': 'https://security.test.lukhas.ai',
            'rp_id': 'security.test.lukhas.ai'
        }
        return OAuth2OIDCProvider(config=config)

    @pytest.fixture
    def test_client(self, oauth_provider):
        """Create test OAuth client"""
        from governance.identity.core.auth.oauth2_oidc_provider import OAuthClient
        client = OAuthClient({
            'client_id': 'security_test_client',
            'client_secret': 'security_test_secret',
            'redirect_uris': ['https://secureapp.test.com/callback'],
            'allowed_scopes': ['openid', 'profile', 'email'],
            'grant_types': ['authorization_code'],
            'response_types': ['code']
        })
        oauth_provider.clients[client.client_id] = client
        return client

    def test_oauth_redirect_uri_validation(self, oauth_provider, test_client):
        """Test OAuth redirect URI validation against open redirects"""
        print("🔗 Testing OAuth redirect URI validation")

        malicious_redirects = [
            'https://evil.com/steal-tokens',
            'javascript:alert("xss")',
            'data:text/html,<script>alert("xss")</script>',
            'https://secureapp.test.com.evil.com/callback',
            'http://secureapp.test.com/callback',  # Wrong protocol
            'https://secureapp.test.com:8080/callback',  # Wrong port
            'https://secureapp.test.com/callback/../admin',  # Path traversal
            'file:///etc/passwd',
            'ftp://malicious.com/callback'
        ]

        for malicious_redirect in malicious_redirects:
            auth_request = {
                'client_id': test_client.client_id,
                'redirect_uri': malicious_redirect,
                'response_type': 'code',
                'scope': 'openid',
                'state': 'test_state'
            }

            result = oauth_provider.handle_authorization_request(
                auth_request, 'security_test_user_12345678', 2
            )

            assert result['error'] == 'invalid_request', f"Malicious redirect accepted: {malicious_redirect}"
            assert 'Invalid redirect_uri' in result['error_description']

        print("✅ OAuth redirect URI validation blocking malicious redirects")

    def test_oauth_pkce_security(self, oauth_provider, test_client):
        """Test OAuth PKCE (Proof Key for Code Exchange) security"""
        print("🔑 Testing OAuth PKCE security")

        # Generate authorization with PKCE
        code_verifier = 'test_code_verifier_' + secrets.token_urlsafe(32)
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).decode().rstrip('=')

        auth_request = {
            'client_id': test_client.client_id,
            'redirect_uri': 'https://secureapp.test.com/callback',
            'response_type': 'code',
            'scope': 'openid',
            'state': 'test_state',
            'code_challenge': code_challenge,
            'code_challenge_method': 'S256'
        }

        auth_result = oauth_provider.handle_authorization_request(
            auth_request, 'pkce_test_user_12345678', 2
        )

        assert 'error' not in auth_result
        auth_code = auth_result['code']

        # Test various PKCE bypass attempts
        bypass_attempts = [
            # Wrong code verifier
            {
                'grant_type': 'authorization_code',
                'code': auth_code,
                'redirect_uri': 'https://secureapp.test.com/callback',
                'code_verifier': 'wrong_verifier',
                'client_id': test_client.client_id,
                'client_secret': test_client.client_secret
            },

            # Missing code verifier
            {
                'grant_type': 'authorization_code',
                'code': auth_code,
                'redirect_uri': 'https://secureapp.test.com/callback',
                'client_id': test_client.client_id,
                'client_secret': test_client.client_secret
            },

            # Empty code verifier
            {
                'grant_type': 'authorization_code',
                'code': auth_code,
                'redirect_uri': 'https://secureapp.test.com/callback',
                'code_verifier': '',
                'client_id': test_client.client_id,
                'client_secret': test_client.client_secret
            }
        ]

        for attempt in bypass_attempts:
            result = oauth_provider.handle_token_request(attempt)
            assert result['error'] in ['invalid_request', 'invalid_grant'], f"PKCE bypass succeeded: {attempt}"

        print("✅ OAuth PKCE security preventing bypass attempts")

    def test_oauth_scope_injection_attacks(self, oauth_provider, test_client):
        """Test OAuth scope injection and privilege escalation"""
        print("🎯 Testing OAuth scope injection attacks")

        # Test scope injection attempts
        malicious_scopes = [
            'openid profile email lukhas:admin',  # Privilege escalation
            'openid profile email; DROP TABLE users',  # SQL injection
            'openid profile email<script>alert("xss")</script>',  # XSS
            'openid profile email\nContent-Type: text/html\n\n<script>alert("xss")</script>',  # Header injection
            'openid profile email lukhas:* lukhas:admin lukhas:root',  # Wildcard abuse
            '../../../etc/passwd',  # Path traversal
            'openid profile email lukhas:enterprise lukhas:quantum lukhas:god_mode',  # Made-up scopes
        ]

        for malicious_scope in malicious_scopes:
            auth_request = {
                'client_id': test_client.client_id,
                'redirect_uri': 'https://secureapp.test.com/callback',
                'response_type': 'code',
                'scope': malicious_scope,
                'state': 'injection_test'
            }

            # Should either reject or sanitize scopes
            result = oauth_provider.handle_authorization_request(
                auth_request, 'scope_injection_user_12345678', 1  # Low tier user
            )

            if 'error' not in result:
                # If accepted, verify dangerous scopes were filtered
                auth_code = result['code']
                code_data = oauth_provider.authorization_codes[auth_code]
                final_scopes = set(code_data['scope'])

                # Should not contain admin or high-privilege scopes
                assert 'lukhas:admin' not in final_scopes
                assert 'lukhas:enterprise' not in final_scopes
                assert 'lukhas:quantum' not in final_scopes
                assert '<script>' not in ' '.join(final_scopes)

        print("✅ OAuth scope injection attacks blocked")

    def test_oauth_state_parameter_security(self, oauth_provider, test_client):
        """Test OAuth state parameter CSRF protection"""
        print("🛡️ Testing OAuth state parameter CSRF protection")

        # Test state parameter handling
        auth_request = {
            'client_id': test_client.client_id,
            'redirect_uri': 'https://secureapp.test.com/callback',
            'response_type': 'code',
            'scope': 'openid',
            'state': 'secure_random_state_12345'
        }

        result = oauth_provider.handle_authorization_request(
            auth_request, 'state_test_user_12345678', 2
        )

        # State should be returned unchanged
        assert result['state'] == auth_request['state']

        # Test malicious state injection
        malicious_states = [
            '<script>alert("xss")</script>',
            'javascript:alert("xss")',
            '\nLocation: https://evil.com\n\n',  # HTTP response splitting
            '../../../etc/passwd',
            'state with\nnewlines\nfor\ninjection'
        ]

        for malicious_state in malicious_states:
            malicious_request = auth_request.copy()
            malicious_request['state'] = malicious_state

            result = oauth_provider.handle_authorization_request(
                malicious_request, 'state_injection_user_12345678', 2
            )

            # Should handle malicious state safely
            if 'error' not in result:
                # State should be properly encoded/sanitized
                returned_state = result.get('state', '')
                assert '<script>' not in returned_state
                assert 'javascript:' not in returned_state
                assert '\n' not in returned_state

        print("✅ OAuth state parameter CSRF protection working")


class TestQRSecurityValidation:
    """Security tests for QR code generation component"""

    @pytest.fixture
    def qr_generator(self):
        """Create QR generator for security testing"""
        return QREntropyGenerator()

    def test_qr_steganography_detection_resistance(self, qr_generator):
        """Test QR steganography resistance to detection"""
        print("🔍 Testing QR steganography detection resistance")

        # Generate QR codes with and without steganography
        session_base = "detection_test_session"

        # QR without steganography (comparison baseline)
        normal_qr = qr_generator.generate_authentication_qr(
            f"{session_base}_normal", b"normal_entropy"
        )

        # QR with steganography
        stego_qr = qr_generator.generate_authentication_qr(
            f"{session_base}_stego", b"stego_entropy_with_hidden_data"
        )

        assert normal_qr['success'] is True
        assert stego_qr['success'] is True

        # Both should have similar metadata structure
        assert stego_qr['entropy_embedded'] is True
        assert stego_qr['layers_count'] == 3

        # Steganographic QR should not obviously reveal hidden data
        stego_image_data = base64.b64decode(stego_qr['qr_image_b64'])

        # Should not contain raw entropy data
        assert b"stego_entropy_with_hidden_data" not in stego_image_data
        assert b"hidden_data" not in stego_image_data

        print("✅ QR steganography resistant to basic detection")

    def test_qr_session_security(self, qr_generator):
        """Test QR session security and session fixation resistance"""
        print("🔐 Testing QR session security")

        # Test session ID collision resistance
        session_ids = set()
        for i in range(1000):
            result = qr_generator.generate_authentication_qr(
                f"collision_test_{i}", secrets.token_bytes(32)
            )

            assert result['success'] is True
            session_id = result['session_id']

            # Should not have collisions
            assert session_id not in session_ids, f"Session ID collision: {session_id}"
            session_ids.add(session_id)

        # Test session fixation resistance
        fixed_session_id = "attacker_controlled_session_12345"

        result = qr_generator.generate_authentication_qr(
            fixed_session_id, secrets.token_bytes(32)
        )

        # Should accept the session ID but validate it securely
        assert result['success'] is True

        # Test session validation with tampered data
        scan_data = json.dumps({
            'challenge': 'tampered_challenge',
            'session_id': fixed_session_id
        })

        is_valid = qr_generator.validate_qr_scan(fixed_session_id, scan_data)
        assert is_valid is False, "Session validation accepted tampered challenge"

        print("✅ QR session security preventing fixation attacks")

    def test_qr_constitutional_validation_security(self, qr_generator):
        """Test QR constitutional validation security"""
        print("🛡️ Testing QR constitutional validation security")

        malicious_qr_data = [
            # Script injection
            {'session_id': '<script>alert("xss")</script>'},

            # SQL injection
            {'session_id': "'; DROP TABLE sessions; --"},

            # Command injection
            {'session_id': '; cat /etc/passwd'},

            # Path traversal
            {'session_id': '../../../etc/passwd'},

            # Oversized data
            {'session_id': 'X' * 100000},

            # Binary injection
            {'session_id': '\x00\x01\x02\x03'}
        ]

        for malicious_data in malicious_qr_data:
            # Constitutional validation should block these
            is_valid = qr_generator._constitutional_validation(
                malicious_data, b"test_entropy"
            )

            assert is_valid is False, f"Constitutional validation bypassed: {malicious_data}"

        # Test with oversized entropy
        oversized_entropy = b"X" * 10000  # 10KB entropy
        valid_qr_data = {'session_id': 'valid_session_12345678'}

        is_valid = qr_generator._constitutional_validation(
            valid_qr_data, oversized_entropy
        )

        assert is_valid is False, "Constitutional validation accepted oversized entropy"

        print("✅ QR constitutional validation blocking attacks")


class TestCrossComponentSecurityIntegration:
    """Security tests across multiple identity components"""

    @pytest.fixture
    def security_system(self):
        """Create integrated system for cross-component security testing"""
        identity_core = IdentityCore(data_dir="security_integration_test")

        webauthn_config = {
            'rp_id': 'security.lukhas.ai',
            'rp_name': 'LUKHAS Security Test',
            'origin': 'https://security.lukhas.ai'
        }
        webauthn_manager = WebAuthnManager(config=webauthn_config)

        oauth_config = {
            'issuer': 'https://security.lukhas.ai',
            'rp_id': 'security.lukhas.ai'
        }
        oauth_provider = OAuth2OIDCProvider(config=oauth_config)

        qr_generator = QREntropyGenerator()

        return {
            'identity_core': identity_core,
            'webauthn_manager': webauthn_manager,
            'oauth_provider': oauth_provider,
            'qr_generator': qr_generator
        }

    def test_privilege_escalation_attack_chain(self, security_system):
        """Test privilege escalation attack chain across components"""
        print("⛓️ Testing privilege escalation attack chain")

        identity_core = security_system['identity_core']
        oauth_provider = security_system['oauth_provider']

        # Create low-privilege user
        low_priv_token = identity_core.create_token(
            'low_priv_user_12345678',
            AccessTier.T1,
            {'consent': True, 'trinity_score': 0.3}
        )

        # Verify low privileges
        is_valid, metadata = identity_core.validate_symbolic_token(low_priv_token)
        tier, permissions = identity_core.resolve_access_tier(metadata)

        assert tier == AccessTier.T1
        assert not permissions['can_admin']
        assert not permissions['can_access_guardian']

        # Attempt privilege escalation via OAuth scope manipulation
        from governance.identity.core.auth.oauth2_oidc_provider import OAuthClient
        client = OAuthClient({
            'client_id': 'escalation_client',
            'client_secret': 'escalation_secret',
            'redirect_uris': ['https://app.test.com/callback'],
            'allowed_scopes': ['openid', 'profile'],  # Limited scopes
            'grant_types': ['authorization_code'],
            'response_types': ['code']
        })
        oauth_provider.clients[client.client_id] = client

        # Try to request admin scopes
        auth_request = {
            'client_id': client.client_id,
            'redirect_uri': 'https://app.test.com/callback',
            'response_type': 'code',
            'scope': 'openid profile lukhas:admin lukhas:enterprise',  # Privilege escalation attempt
            'state': 'escalation_test'
        }

        result = oauth_provider.handle_authorization_request(
            auth_request, 'low_priv_user_12345678', 1  # Tier 1 user
        )

        if 'error' not in result:
            # If authorization succeeds, check that dangerous scopes were filtered
            auth_code = result['code']
            code_data = oauth_provider.authorization_codes[auth_code]
            final_scopes = set(code_data['scope'])

            assert 'lukhas:admin' not in final_scopes
            assert 'lukhas:enterprise' not in final_scopes

        print("✅ Privilege escalation attack chain blocked")

    def test_session_hijacking_resistance(self, security_system):
        """Test session hijacking resistance across components"""
        print("🕵️ Testing session hijacking resistance")

        identity_core = security_system['identity_core']
        qr_generator = security_system['qr_generator']

        # Create legitimate user session
        legitimate_token = identity_core.create_token(
            'legitimate_user_12345678',
            AccessTier.T3,
            {'consent': True, 'trinity_score': 0.8}
        )

        # Create QR session for legitimate user
        qr_result = qr_generator.generate_authentication_qr(
            'legitimate_qr_session', secrets.token_bytes(32)
        )

        # Attempt session hijacking by modifying identifiers
        hijacked_tokens = [
            legitimate_token.replace('legitimate_user', 'hijacker_user'),
            legitimate_token[:-5] + 'HIJAC',  # Modify end of token
            'LUKHAS-T5-' + legitimate_token.split('-')[2],  # Escalate tier
        ]

        for hijacked_token in hijacked_tokens:
            is_valid, metadata = identity_core.validate_symbolic_token(hijacked_token)
            assert is_valid is False, f"Session hijacking succeeded with token: {hijacked_token[:50]}..."

        # Attempt QR session hijacking
        legitimate_session_id = qr_result['session_id']
        code_data = qr_generator.active_codes[legitimate_session_id]

        # Try to validate with wrong challenge
        hijack_scan_data = json.dumps({
            'challenge': 'hijacked_challenge',
            'session_id': legitimate_session_id
        })

        is_valid = qr_generator.validate_qr_scan(legitimate_session_id, hijack_scan_data)
        assert is_valid is False, "QR session hijacking succeeded"

        print("✅ Session hijacking resistance working")

    def test_trinity_framework_security_coordination(self, security_system):
        """Test Trinity Framework security coordination (⚛️🧠🛡️)"""
        print("🛡️ Testing Trinity Framework security coordination")

        identity_core = security_system['identity_core']
        webauthn_manager = security_system['webauthn_manager']
        oauth_provider = security_system['oauth_provider']
        qr_generator = security_system['qr_generator']

        # ⚛️ Identity Security: Test identity integrity
        malicious_identity = 'malicious_user_<script>alert("xss")</script>'

        # All components should reject malicious identities
        with patch('logging.Logger.warning') as mock_warning:
            tier, permissions = identity_core.resolve_access_tier({
                'user_id': malicious_identity,
                'tier': 'T5',
                'drift_score': 0.9  # High drift should trigger Guardian
            })
            mock_warning.assert_called()  # Should log warning

        # 🧠 Consciousness Security: Test temporal validation
        expired_metadata = {
            'user_id': 'temporal_test_user_12345678',
            'tier': 'T3',
            'timestamp': (datetime.utcnow() - timedelta(hours=2)).isoformat()  # Old timestamp
        }

        # WebAuthn should reject expired operations
        reg_result = webauthn_manager.generate_registration_options(
            'expired_user_12345678', 'test@example.com', 'Test User', 3
        )
        reg_id = reg_result['registration_id']

        # Manually expire the registration
        webauthn_manager.pending_registrations[reg_id]['expires_at'] = (
            datetime.utcnow() - timedelta(minutes=10)
        ).isoformat()

        mock_response = {
            'id': 'test_cred',
            'response': {
                'clientDataJSON': base64.b64encode(b'{}').decode(),
                'attestationObject': base64.b64encode(b'mock').decode()
            }
        }

        verify_result = webauthn_manager.verify_registration_response(reg_id, mock_response)
        assert verify_result['success'] is False
        assert verify_result['error'] == 'Registration expired'

        # 🛡️ Guardian Security: Test constitutional validation across all components
        malicious_data = {
            'session_id': '<script>alert("guardian_bypass")</script>',
            'client_id': 'evil_client_<script>',
            'user_id': 'admin"; DROP TABLE users; --'
        }

        # All components should have constitutional validation
        assert not identity_core._validate_symbolic_integrity({
            'user_id': malicious_data['user_id'],
            'tier': 'T5',
            'glyphs': ['⚛️']
        })

        assert not webauthn_manager._constitutional_validation(
            malicious_data['user_id'], 'webauthn_registration', {}
        )

        assert not oauth_provider._constitutional_validation(
            malicious_data['user_id'], 'oauth2_authorization', {
                'client_id': malicious_data['client_id']
            }
        )

        assert not qr_generator._constitutional_validation(
            {'session_id': malicious_data['session_id']}, b"test"
        )

        print("✅ Trinity Framework security coordination working")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
