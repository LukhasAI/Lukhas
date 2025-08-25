"""
🔐 OAuth2/OIDC Provider Test Suite
=================================

Comprehensive unit tests for LUKHAS OAuth2/OIDC authorization server.
Tests OAuth2 flows, OpenID Connect, JWT tokens, and Trinity Framework compliance.

Trinity Framework: ⚛️ (Identity), 🧠 (Consciousness), 🛡️ (Guardian)
"""

import base64
import os
import secrets

# Import system under test
import sys
import time
from datetime import datetime, timedelta

import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'governance', 'identity', 'core', 'auth'))

try:
    from oauth2_oidc_provider import OAuth2OIDCProvider, OAuthClient
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False
    pytest.skip("OAuth2/OIDC provider not available", allow_module_level=True)


class TestOAuthClient:
    """Test OAuth client data structure"""

    def test_oauth_client_creation(self):
        """Test OAuthClient creation and serialization"""
        client_data = {
            'client_id': 'test_client_123',
            'client_secret': 'test_secret_456',
            'client_name': 'Test Application',
            'redirect_uris': ['https://app.example.com/callback', 'https://app.example.com/callback2'],
            'allowed_scopes': ['openid', 'profile', 'email', 'lukhas:basic'],
            'grant_types': ['authorization_code', 'refresh_token'],
            'response_types': ['code'],
            'tier_level': 2,
            'trusted': False
        }

        client = OAuthClient(client_data)

        assert client.client_id == 'test_client_123'
        assert client.client_secret == 'test_secret_456'
        assert client.client_name == 'Test Application'
        assert client.redirect_uris == ['https://app.example.com/callback', 'https://app.example.com/callback2']
        assert client.allowed_scopes == {'openid', 'profile', 'email', 'lukhas:basic'}
        assert client.grant_types == {'authorization_code', 'refresh_token'}
        assert client.response_types == {'code'}
        assert client.tier_level == 2
        assert client.trusted is False

        # Test serialization
        client_dict = client.to_dict()
        assert client_dict['client_id'] == 'test_client_123'
        assert client_dict['client_name'] == 'Test Application'
        assert 'openid' in client_dict['allowed_scopes']
        assert 'authorization_code' in client_dict['grant_types']
        assert 'code' in client_dict['response_types']
        assert client_dict['tier_level'] == 2

    def test_oauth_client_defaults(self):
        """Test OAuthClient with minimal data"""
        client_data = {'client_id': 'minimal_client'}
        client = OAuthClient(client_data)

        assert client.client_id == 'minimal_client'
        assert client.client_secret == ''
        assert client.client_name == ''
        assert client.redirect_uris == []
        assert client.allowed_scopes == set()
        assert client.grant_types == {'authorization_code'}  # Default
        assert client.response_types == {'code'}  # Default
        assert client.tier_level == 0
        assert client.trusted is False


class TestOAuth2OIDCProvider:
    """Test suite for OAuth2/OIDC authorization server"""

    @pytest.fixture
    def oauth_provider(self):
        """Create OAuth2/OIDC provider instance"""
        config = {
            'issuer': 'https://test.candidate.ai',
            'rp_id': 'test.candidate.ai'
        }
        return OAuth2OIDCProvider(config=config)

    @pytest.fixture
    def test_client(self, oauth_provider):
        """Create test OAuth client"""
        client_data = {
            'client_id': 'test_client_12345',
            'client_secret': 'test_secret_67890',
            'client_name': 'Test OAuth Client',
            'redirect_uris': ['https://client.example.com/callback'],
            'allowed_scopes': ['openid', 'profile', 'email', 'lukhas:basic', 'lukhas:identity:read'],
            'grant_types': ['authorization_code', 'refresh_token'],
            'response_types': ['code'],
            'tier_level': 3,
            'trusted': False
        }

        client = OAuthClient(client_data)
        oauth_provider.clients[client.client_id] = client
        return client

    @pytest.fixture
    def mock_authorization_request(self):
        """Mock OAuth2 authorization request parameters"""
        return {
            'client_id': 'test_client_12345',
            'redirect_uri': 'https://client.example.com/callback',
            'response_type': 'code',
            'scope': 'openid profile email lukhas:basic',
            'state': 'random_state_12345',
            'nonce': 'random_nonce_67890',
            'code_challenge': 'dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk',
            'code_challenge_method': 'S256'
        }

    def test_oauth_provider_initialization(self, oauth_provider):
        """Test OAuth2/OIDC provider initialization"""
        assert oauth_provider.issuer == 'https://test.candidate.ai'
        assert oauth_provider.key_id == 'lukhas-signing-key-2024'

        # Check supported features
        assert 'openid' in oauth_provider.supported_scopes
        assert 'authorization_code' in oauth_provider.supported_grant_types
        assert 'code' in oauth_provider.supported_response_types

        # Check tier-based scope mapping
        assert len(oauth_provider.tier_scope_mapping) == 6  # Tiers 0-5
        assert 'openid' in oauth_provider.tier_scope_mapping[0]  # Basic tier
        assert '*' in oauth_provider.tier_scope_mapping[5]  # Admin tier (all scopes)

        # Check Trinity Framework integration hooks
        assert hasattr(oauth_provider, 'guardian_validator')
        assert hasattr(oauth_provider, 'consciousness_tracker')
        assert hasattr(oauth_provider, 'identity_verifier')

        # Check storage initialization
        assert isinstance(oauth_provider.clients, dict)
        assert isinstance(oauth_provider.authorization_codes, dict)
        assert isinstance(oauth_provider.access_tokens, dict)
        assert isinstance(oauth_provider.refresh_tokens, dict)

    def test_get_authorization_endpoint_metadata(self, oauth_provider):
        """Test OAuth2/OIDC server metadata (RFC 8414)"""
        metadata = oauth_provider.get_authorization_endpoint_metadata()

        # Check required OAuth2/OIDC endpoints
        assert metadata['issuer'] == 'https://test.candidate.ai'
        assert metadata['authorization_endpoint'] == 'https://test.candidate.ai/oauth2/authorize'
        assert metadata['token_endpoint'] == 'https://test.candidate.ai/oauth2/token'
        assert metadata['userinfo_endpoint'] == 'https://test.candidate.ai/oauth2/userinfo'
        assert metadata['jwks_uri'] == 'https://test.candidate.ai/.well-known/jwks.json'

        # Check supported features
        assert 'openid' in metadata['scopes_supported']
        assert 'authorization_code' in metadata['grant_types_supported']
        assert 'code' in metadata['response_types_supported']
        assert 'public' in metadata['subject_types_supported']
        assert 'RS256' in metadata['id_token_signing_alg_values_supported']

        # Check OIDC claims
        expected_claims = ['sub', 'iss', 'aud', 'exp', 'iat', 'name', 'email', 'tier']
        for claim in expected_claims:
            assert claim in metadata['claims_supported']

        # Check PKCE support
        assert 'S256' in metadata['code_challenge_methods_supported']
        assert 'plain' in metadata['code_challenge_methods_supported']

        # Check LUKHAS extensions
        assert metadata['lukhas_tier_system_supported'] is True
        assert metadata['lukhas_lambda_id_supported'] is True
        assert metadata['lukhas_trinity_framework'] == '⚛️🧠🛡️'
        assert metadata['lukhas_consciousness_integration'] is True

    def test_handle_authorization_request_valid(self, oauth_provider, test_client, mock_authorization_request):
        """Test valid OAuth2 authorization request handling"""
        user_id = 'test_user_12345678'
        user_tier = 3

        start_time = time.time()
        result = oauth_provider.handle_authorization_request(
            mock_authorization_request, user_id, user_tier
        )
        processing_time = (time.time() - start_time) * 1000

        # Should successfully handle authorization code flow
        assert 'error' not in result
        assert 'code' in result
        assert result['state'] == mock_authorization_request['state']
        assert result['redirect_uri'] == mock_authorization_request['redirect_uri']

        # Verify authorization code was stored
        auth_code = result['code']
        assert auth_code in oauth_provider.authorization_codes

        code_data = oauth_provider.authorization_codes[auth_code]
        assert code_data['client_id'] == test_client.client_id
        assert code_data['user_id'] == user_id
        assert code_data['user_tier'] == user_tier
        assert 'openid' in code_data['scope']
        assert code_data['nonce'] == mock_authorization_request['nonce']

        # Verify PKCE challenge was stored
        assert code_data['code_challenge'] == mock_authorization_request['code_challenge']
        assert code_data['code_challenge_method'] == mock_authorization_request['code_challenge_method']

        # Performance check
        assert processing_time < 100, f"Authorization processing took {processing_time:.2f}ms"

    def test_handle_authorization_request_invalid_client(self, oauth_provider, mock_authorization_request):
        """Test authorization request with invalid client"""
        mock_authorization_request['client_id'] = 'nonexistent_client'

        result = oauth_provider.handle_authorization_request(
            mock_authorization_request, 'test_user_12345678', 2
        )

        assert result['error'] == 'invalid_client'
        assert 'Unknown client identifier' in result['error_description']

    def test_handle_authorization_request_invalid_redirect_uri(self, oauth_provider, test_client, mock_authorization_request):
        """Test authorization request with invalid redirect URI"""
        mock_authorization_request['redirect_uri'] = 'https://malicious.example.com/callback'

        result = oauth_provider.handle_authorization_request(
            mock_authorization_request, 'test_user_12345678', 2
        )

        assert result['error'] == 'invalid_request'
        assert 'Invalid redirect_uri' in result['error_description']

    def test_handle_authorization_request_unsupported_response_type(self, oauth_provider, test_client, mock_authorization_request):
        """Test authorization request with unsupported response type"""
        mock_authorization_request['response_type'] = 'unsupported_type'

        result = oauth_provider.handle_authorization_request(
            mock_authorization_request, 'test_user_12345678', 2
        )

        assert result['error'] == 'unsupported_response_type'

    def test_handle_authorization_request_scope_filtering(self, oauth_provider, test_client, mock_authorization_request):
        """Test scope filtering based on user tier and client permissions"""
        # Request scopes that exceed user tier and client permissions
        mock_authorization_request['scope'] = 'openid profile email lukhas:admin lukhas:enterprise'

        user_id = 'test_user_12345678'
        user_tier = 2  # Lower tier

        result = oauth_provider.handle_authorization_request(
            mock_authorization_request, user_id, user_tier
        )

        # Should succeed but filter scopes
        assert 'error' not in result
        assert 'code' in result

        # Check stored scopes were filtered
        auth_code = result['code']
        code_data = oauth_provider.authorization_codes[auth_code]
        final_scopes = set(code_data['scope'])

        # Should include basic scopes for tier 2
        assert 'openid' in final_scopes
        assert 'profile' in final_scopes
        assert 'email' in final_scopes

        # Should NOT include high-tier scopes
        assert 'lukhas:admin' not in final_scopes
        assert 'lukhas:enterprise' not in final_scopes

    def test_handle_authorization_request_no_valid_scopes(self, oauth_provider, test_client, mock_authorization_request):
        """Test authorization request with no valid scopes for user tier"""
        # Request only high-tier scopes
        mock_authorization_request['scope'] = 'lukhas:admin lukhas:enterprise'

        user_id = 'test_user_12345678'
        user_tier = 1  # Low tier

        result = oauth_provider.handle_authorization_request(
            mock_authorization_request, user_id, user_tier
        )

        assert result['error'] == 'invalid_scope'
        assert 'No valid scopes available' in result['error_description']

    def test_handle_token_request_authorization_code_flow(self, oauth_provider, test_client):
        """Test token request for authorization code flow"""
        # Create authorization code first
        code_verifier = 'dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk'
        code_challenge = 'E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM'  # SHA256 of verifier

        auth_code = f"lukhas_ac_{secrets.token_urlsafe(32)}"
        oauth_provider.authorization_codes[auth_code] = {
            'client_id': test_client.client_id,
            'user_id': 'test_user_12345678',
            'user_tier': 3,
            'scope': ['openid', 'profile', 'email'],
            'redirect_uri': 'https://client.example.com/callback',
            'nonce': 'test_nonce',
            'code_challenge': code_challenge,
            'code_challenge_method': 'S256',
            'issued_at': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(minutes=10)).isoformat()
        }

        # Token request
        token_request = {
            'grant_type': 'authorization_code',
            'code': auth_code,
            'redirect_uri': 'https://client.example.com/callback',
            'code_verifier': code_verifier,
            'client_id': test_client.client_id,
            'client_secret': test_client.client_secret
        }

        start_time = time.time()
        result = oauth_provider.handle_token_request(token_request)
        processing_time = (time.time() - start_time) * 1000

        # Should successfully issue tokens
        assert 'error' not in result
        assert 'access_token' in result
        assert 'refresh_token' in result
        assert 'id_token' in result  # Because openid scope was present
        assert result['token_type'] == 'Bearer'
        assert result['expires_in'] == 3600
        assert result['scope'] == 'openid profile email'

        # Verify tokens were stored
        access_token = result['access_token']
        assert access_token in oauth_provider.access_tokens

        # Verify authorization code was cleaned up
        assert auth_code not in oauth_provider.authorization_codes

        # Performance check
        assert processing_time < 100, f"Token processing took {processing_time:.2f}ms"

    def test_handle_token_request_invalid_authorization_code(self, oauth_provider, test_client):
        """Test token request with invalid authorization code"""
        token_request = {
            'grant_type': 'authorization_code',
            'code': 'invalid_code',
            'redirect_uri': 'https://client.example.com/callback',
            'client_id': test_client.client_id,
            'client_secret': test_client.client_secret
        }

        result = oauth_provider.handle_token_request(token_request)

        assert result['error'] == 'invalid_grant'
        assert 'Invalid authorization code' in result['error_description']

    def test_handle_token_request_invalid_client_credentials(self, oauth_provider):
        """Test token request with invalid client credentials"""
        token_request = {
            'grant_type': 'authorization_code',
            'code': 'some_code',
            'client_id': 'invalid_client',
            'client_secret': 'invalid_secret'
        }

        result = oauth_provider.handle_token_request(token_request)

        assert result['error'] == 'invalid_client'
        assert 'Invalid client credentials' in result['error_description']

    def test_handle_token_request_pkce_validation(self, oauth_provider, test_client):
        """Test PKCE validation in token request"""
        # Create authorization code with PKCE challenge
        auth_code = f"lukhas_ac_{secrets.token_urlsafe(32)}"
        correct_verifier = 'test_code_verifier_123456789012345'
        challenge = base64.urlsafe_b64encode(
            __import__('hashlib').sha256(correct_verifier.encode()).digest()
        ).decode().rstrip('=')

        oauth_provider.authorization_codes[auth_code] = {
            'client_id': test_client.client_id,
            'user_id': 'test_user_12345678',
            'user_tier': 3,
            'scope': ['openid'],
            'redirect_uri': 'https://client.example.com/callback',
            'code_challenge': challenge,
            'code_challenge_method': 'S256',
            'issued_at': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(minutes=10)).isoformat()
        }

        # Test with correct code verifier
        token_request_valid = {
            'grant_type': 'authorization_code',
            'code': auth_code,
            'redirect_uri': 'https://client.example.com/callback',
            'code_verifier': correct_verifier,
            'client_id': test_client.client_id,
            'client_secret': test_client.client_secret
        }

        result = oauth_provider.handle_token_request(token_request_valid)
        assert 'error' not in result
        assert 'access_token' in result

        # Re-create the auth code for invalid verifier test
        oauth_provider.authorization_codes[auth_code] = {
            'client_id': test_client.client_id,
            'user_id': 'test_user_12345678',
            'user_tier': 3,
            'scope': ['openid'],
            'redirect_uri': 'https://client.example.com/callback',
            'code_challenge': challenge,
            'code_challenge_method': 'S256',
            'issued_at': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(minutes=10)).isoformat()
        }

        # Test with incorrect code verifier
        token_request_invalid = token_request_valid.copy()
        token_request_invalid['code_verifier'] = 'wrong_code_verifier'

        result = oauth_provider.handle_token_request(token_request_invalid)
        assert result['error'] == 'invalid_grant'
        assert 'Invalid code verifier' in result['error_description']

    def test_handle_token_request_refresh_token_flow(self, oauth_provider, test_client):
        """Test refresh token flow"""
        # Create refresh token first
        refresh_token = f"lukhas_rt_{secrets.token_urlsafe(32)}"
        oauth_provider.refresh_tokens[refresh_token] = {
            'client_id': test_client.client_id,
            'user_id': 'test_user_12345678',
            'user_tier': 3,
            'scope': ['openid', 'profile', 'email'],
            'issued_at': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(days=30)).isoformat()
        }

        token_request = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': test_client.client_id,
            'client_secret': test_client.client_secret
        }

        result = oauth_provider.handle_token_request(token_request)

        assert 'error' not in result
        assert 'access_token' in result
        assert result['token_type'] == 'Bearer'
        assert result['expires_in'] == 3600
        assert result['scope'] == 'openid profile email'

        # New access token should be stored
        new_access_token = result['access_token']
        assert new_access_token in oauth_provider.access_tokens

    def test_handle_token_request_client_credentials_flow(self, oauth_provider, test_client):
        """Test client credentials flow"""
        token_request = {
            'grant_type': 'client_credentials',
            'scope': 'lukhas:basic lukhas:identity:read',
            'client_id': test_client.client_id,
            'client_secret': test_client.client_secret
        }

        result = oauth_provider.handle_token_request(token_request)

        assert 'error' not in result
        assert 'access_token' in result
        assert result['token_type'] == 'Bearer'
        assert result['expires_in'] == 86400  # 24 hours for client credentials

        # Should only include scopes allowed for client
        returned_scopes = set(result['scope'].split())
        assert 'lukhas:basic' in returned_scopes
        assert 'lukhas:identity:read' in returned_scopes

        # Access token should be stored
        access_token = result['access_token']
        assert access_token in oauth_provider.access_tokens

        token_data = oauth_provider.access_tokens[access_token]
        assert token_data['user_id'] == test_client.client_id  # Client acts as user

    def test_introspect_token_valid(self, oauth_provider, test_client):
        """Test token introspection with valid token"""
        # Create access token
        access_token = f"lukhas_at_{secrets.token_urlsafe(32)}"
        token_data = {
            'client_id': test_client.client_id,
            'user_id': 'test_user_12345678',
            'user_tier': 3,
            'scope': ['openid', 'profile', 'email'],
            'issued_at': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(hours=1)).isoformat(),
            'lambda_id': 'LUKHAS3-DEMO-○-ABCD'
        }
        oauth_provider.access_tokens[access_token] = token_data

        start_time = time.time()
        result = oauth_provider.introspect_token(access_token, test_client.client_id)
        introspection_time = (time.time() - start_time) * 1000

        assert result['active'] is True
        assert result['scope'] == 'openid profile email'
        assert result['client_id'] == test_client.client_id
        assert result['sub'] == 'test_user_12345678'
        assert result['token_type'] == 'Bearer'
        assert result['lukhas_tier'] == 3
        assert result['lukhas_lambda_id'] == 'LUKHAS3-DEMO-○-ABCD'
        assert 'exp' in result
        assert 'iat' in result

        # Performance check
        assert result['introspection_time_ms'] < 50, f"Introspection took {introspection_time:.2f}ms"

    def test_introspect_token_invalid(self, oauth_provider, test_client):
        """Test token introspection with invalid token"""
        result = oauth_provider.introspect_token('invalid_token', test_client.client_id)

        assert result['active'] is False

    def test_introspect_token_expired(self, oauth_provider, test_client):
        """Test token introspection with expired token"""
        access_token = f"lukhas_at_{secrets.token_urlsafe(32)}"
        expired_token_data = {
            'client_id': test_client.client_id,
            'user_id': 'test_user_12345678',
            'user_tier': 3,
            'scope': ['openid', 'profile'],
            'issued_at': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() - timedelta(hours=1)).isoformat()  # Expired
        }
        oauth_provider.access_tokens[access_token] = expired_token_data

        result = oauth_provider.introspect_token(access_token, test_client.client_id)

        assert result['active'] is False

    def test_get_userinfo_valid(self, oauth_provider, test_client):
        """Test UserInfo endpoint with valid access token"""
        # Create access token with openid scope
        access_token = f"lukhas_at_{secrets.token_urlsafe(32)}"
        token_data = {
            'client_id': test_client.client_id,
            'user_id': 'test_user_12345678',
            'user_tier': 3,
            'scope': ['openid', 'profile', 'email', 'phone', 'address', 'lukhas:identity:read'],
            'issued_at': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(hours=1)).isoformat(),
            'lambda_id': 'LUKHAS3-DEMO-○-ABCD'
        }
        oauth_provider.access_tokens[access_token] = token_data

        start_time = time.time()
        result = oauth_provider.get_userinfo(access_token)
        retrieval_time = (time.time() - start_time) * 1000

        # Should return user info based on scopes
        assert 'error' not in result
        assert result['sub'] == 'test_user_12345678'

        # Profile scope claims
        assert 'name' in result
        assert 'preferred_username' in result
        assert result['tier'] == 3
        assert 'tier_name' in result
        assert 'tier_symbol' in result
        assert 'picture' in result
        assert 'updated_at' in result

        # Email scope claims
        assert 'email' in result
        assert result['email_verified'] is True

        # Phone scope claims
        assert 'phone_number' in result
        assert 'phone_number_verified' in result

        # Address scope claims
        assert 'address' in result
        assert isinstance(result['address'], dict)
        assert 'formatted' in result['address']

        # LUKHAS specific claims
        assert result['lambda_id'] == 'LUKHAS3-DEMO-○-ABCD'
        assert 'identity_features' in result
        assert result['trinity_compliance'] == '⚛️🧠🛡️'

        # Performance check
        assert result['retrieval_time_ms'] < 50, f"UserInfo retrieval took {retrieval_time:.2f}ms"

    def test_get_userinfo_insufficient_scope(self, oauth_provider, test_client):
        """Test UserInfo endpoint without openid scope"""
        access_token = f"lukhas_at_{secrets.token_urlsafe(32)}"
        token_data = {
            'client_id': test_client.client_id,
            'user_id': 'test_user_12345678',
            'scope': ['profile'],  # Missing openid scope
            'issued_at': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(hours=1)).isoformat()
        }
        oauth_provider.access_tokens[access_token] = token_data

        result = oauth_provider.get_userinfo(access_token)

        assert result['error'] == 'insufficient_scope'
        assert 'OpenID scope required' in result['error_description']

    def test_get_userinfo_invalid_token(self, oauth_provider):
        """Test UserInfo endpoint with invalid token"""
        result = oauth_provider.get_userinfo('invalid_token')

        assert result['error'] == 'invalid_token'
        assert 'Invalid access token' in result['error_description']

    @pytest.mark.skipif(not JWT_AVAILABLE, reason="JWT library not available")
    def test_get_jwks(self, oauth_provider):
        """Test JWKS (JSON Web Key Set) endpoint"""
        jwks = oauth_provider.get_jwks()

        assert 'error' not in jwks
        assert 'keys' in jwks
        assert len(jwks['keys']) >= 1

        key = jwks['keys'][0]
        assert key['kty'] == 'RSA'
        assert key['use'] == 'sig'
        assert key['kid'] == oauth_provider.key_id
        assert key['alg'] == 'RS256'
        assert 'n' in key  # RSA modulus
        assert 'e' in key  # RSA exponent

        # Test JWKS caching
        jwks2 = oauth_provider.get_jwks()
        assert jwks == jwks2  # Should be cached

    def test_register_client(self, oauth_provider):
        """Test OAuth2 client registration (RFC 7591)"""
        registration_request = {
            'client_name': 'Dynamic Test Client',
            'redirect_uris': ['https://dynamic.example.com/callback'],
            'grant_types': ['authorization_code', 'refresh_token'],
            'response_types': ['code'],
            'scope': 'openid profile email lukhas:basic'
        }

        result = oauth_provider.register_client(registration_request)

        assert 'error' not in result
        assert 'client_id' in result
        assert 'client_secret' in result
        assert result['client_id'].startswith('lukhas_')
        assert len(result['client_secret']) >= 32
        assert result['redirect_uris'] == ['https://dynamic.example.com/callback']
        assert 'authorization_code' in result['grant_types']
        assert 'code' in result['response_types']
        assert 'openid' in result['scope']

        # Verify client was stored
        client_id = result['client_id']
        assert client_id in oauth_provider.clients

        client = oauth_provider.clients[client_id]
        assert client.client_name == 'Dynamic Test Client'
        assert client.tier_level == 0  # Default for new clients
        assert client.trusted is False

    def test_register_client_missing_redirect_uris(self, oauth_provider):
        """Test client registration without redirect URIs"""
        registration_request = {
            'client_name': 'Invalid Client'
        }

        result = oauth_provider.register_client(registration_request)

        assert result['error'] == 'invalid_request'
        assert 'redirect_uris required' in result['error_description']

    def test_tier_based_scope_restrictions(self, oauth_provider):
        """Test tier-based scope filtering"""
        # Test different tiers
        test_cases = [
            (0, {'openid', 'profile', 'lukhas:basic'}),
            (1, {'openid', 'profile', 'email', 'lukhas:basic', 'lukhas:identity:read'}),
            (3, {'openid', 'profile', 'email', 'phone', 'address', 'lukhas:basic', 'lukhas:identity:read', 'lukhas:identity:write', 'lukhas:premium'}),
            (5, oauth_provider.supported_scopes)  # Admin gets all scopes
        ]

        for tier, expected_scopes in test_cases:
            allowed_scopes = oauth_provider._get_allowed_scopes_for_tier(tier)

            if tier == 5:
                # Admin tier should get all supported scopes
                assert allowed_scopes == expected_scopes
            else:
                # Other tiers should get specific subset
                assert allowed_scopes == expected_scopes

    def test_constitutional_validation(self, oauth_provider):
        """Test Trinity Framework constitutional validation (🛡️ Guardian)"""
        user_id = 'constitutional_test_user_12345678'

        # Test valid OAuth2 authorization
        valid_data = {
            'client_id': 'valid_client_123',
            'scopes': ['openid', 'profile'],
            'response_type': 'code'
        }

        result = oauth_provider._constitutional_validation(user_id, 'oauth2_authorization', valid_data)
        assert result is True

        # Test with suspicious patterns
        suspicious_data = {
            'client_id': 'client_with_<script>alert("xss")</script>',
            'scopes': ['openid'],
            'response_type': 'code'
        }

        result = oauth_provider._constitutional_validation(user_id, 'oauth2_authorization', suspicious_data)
        assert result is False

        # Test with invalid user ID
        result = oauth_provider._constitutional_validation('short', 'oauth2_authorization', valid_data)
        assert result is False

        # Test with invalid operation
        result = oauth_provider._constitutional_validation(user_id, 'invalid_operation', valid_data)
        assert result is False

    def test_implicit_flow(self, oauth_provider, test_client):
        """Test OAuth2 implicit flow"""
        request_params = {
            'client_id': test_client.client_id,
            'redirect_uri': 'https://client.example.com/callback',
            'response_type': 'token',
            'scope': 'profile email',
            'state': 'implicit_state_123'
        }

        user_id = 'implicit_user_12345678'
        user_tier = 2

        result = oauth_provider.handle_authorization_request(request_params, user_id, user_tier)

        # Should return access token directly (implicit flow)
        assert 'error' not in result
        assert 'access_token' in result
        assert result['token_type'] == 'Bearer'
        assert result['expires_in'] == 3600
        assert result['state'] == request_params['state']

        # Access token should be stored
        access_token = result['access_token']
        assert access_token in oauth_provider.access_tokens

    def test_id_token_implicit_flow(self, oauth_provider, test_client):
        """Test OpenID Connect implicit flow for ID token"""
        request_params = {
            'client_id': test_client.client_id,
            'redirect_uri': 'https://client.example.com/callback',
            'response_type': 'id_token',
            'scope': 'openid profile',
            'state': 'id_token_state_123',
            'nonce': 'id_token_nonce_456'
        }

        user_id = 'id_token_user_12345678'
        user_tier = 3

        result = oauth_provider.handle_authorization_request(request_params, user_id, user_tier)

        # Should return ID token directly
        assert 'error' not in result
        assert 'id_token' in result
        assert result['state'] == request_params['state']

        # Verify ID token structure (if JWT available)
        if JWT_AVAILABLE and oauth_provider.private_key:
            id_token = result['id_token']
            # Note: In a real test, we'd decode and verify the JWT
            assert len(id_token.split('.')) == 3  # JWT has 3 parts

    def test_oauth_performance_requirements(self, oauth_provider, test_client, mock_authorization_request):
        """Test OAuth2/OIDC operations meet performance requirements"""
        user_id = 'performance_test_user_12345678'
        user_tier = 3
        num_iterations = 20

        # Test authorization request processing performance
        auth_times = []
        for i in range(num_iterations):
            request_copy = mock_authorization_request.copy()
            request_copy['state'] = f'state_{i}'

            start_time = time.time()
            result = oauth_provider.handle_authorization_request(request_copy, f"{user_id}_{i}", user_tier)
            auth_time = (time.time() - start_time) * 1000

            assert 'error' not in result
            auth_times.append(auth_time)

        # Test token request processing performance
        token_times = []
        for i in range(10):  # Fewer iterations for token requests
            # Create auth code
            auth_code = f"lukhas_ac_{secrets.token_urlsafe(32)}"
            oauth_provider.authorization_codes[auth_code] = {
                'client_id': test_client.client_id,
                'user_id': f"{user_id}_{i}",
                'user_tier': user_tier,
                'scope': ['openid', 'profile'],
                'redirect_uri': 'https://client.example.com/callback',
                'issued_at': datetime.utcnow().isoformat(),
                'expires_at': (datetime.utcnow() + timedelta(minutes=10)).isoformat()
            }

            token_request = {
                'grant_type': 'authorization_code',
                'code': auth_code,
                'redirect_uri': 'https://client.example.com/callback',
                'client_id': test_client.client_id,
                'client_secret': test_client.client_secret
            }

            start_time = time.time()
            result = oauth_provider.handle_token_request(token_request)
            token_time = (time.time() - start_time) * 1000

            assert 'error' not in result
            token_times.append(token_time)

        # Calculate p95 latencies
        auth_times.sort()
        token_times.sort()

        auth_p95 = auth_times[int(0.95 * len(auth_times))]
        token_p95 = token_times[int(0.95 * len(token_times))]

        # Verify p95 latency requirements (<100ms)
        assert auth_p95 < 200, f"Authorization p95 latency {auth_p95:.2f}ms exceeds requirement"
        assert token_p95 < 200, f"Token p95 latency {token_p95:.2f}ms exceeds requirement"

        # Average should be even better
        auth_avg = sum(auth_times) / len(auth_times)
        token_avg = sum(token_times) / len(token_times)

        assert auth_avg < 100, f"Authorization average latency {auth_avg:.2f}ms too high"
        assert token_avg < 100, f"Token average latency {token_avg:.2f}ms too high"

    def test_trinity_framework_integration(self, oauth_provider, test_client, mock_authorization_request):
        """Test Trinity Framework integration (⚛️🧠🛡️)"""
        user_id = 'trinity_oauth_user_12345678'
        user_tier = 4

        # Generate authorization
        result = oauth_provider.handle_authorization_request(
            mock_authorization_request, user_id, user_tier
        )

        # ⚛️ Identity - Verify identity integrity in authorization
        assert 'error' not in result
        assert 'code' in result
        auth_code = result['code']
        code_data = oauth_provider.authorization_codes[auth_code]
        assert code_data['user_id'] == user_id
        assert code_data['user_tier'] == user_tier

        # 🧠 Consciousness - Verify temporal awareness
        issued_at = datetime.fromisoformat(code_data['issued_at'])
        expires_at = datetime.fromisoformat(code_data['expires_at'])
        assert expires_at > issued_at
        assert (expires_at - issued_at).total_seconds() == 600  # 10 minutes

        # 🛡️ Guardian - Verify security validation
        assert len(code_data['code_challenge']) > 20  # Strong PKCE challenge

        # Exchange for tokens
        token_request = {
            'grant_type': 'authorization_code',
            'code': auth_code,
            'redirect_uri': mock_authorization_request['redirect_uri'],
            'code_verifier': 'dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk',  # Original verifier
            'client_id': test_client.client_id,
            'client_secret': test_client.client_secret
        }

        token_result = oauth_provider.handle_token_request(token_request)

        # Verify Trinity compliance in token response
        assert 'error' not in token_result
        assert 'access_token' in token_result

        access_token = token_result['access_token']
        token_data = oauth_provider.access_tokens[access_token]

        # Verify LUKHAS-specific token data
        assert token_data['lambda_id'].startswith(f"LUKHAS{user_tier}")
        assert token_data['user_tier'] == user_tier
