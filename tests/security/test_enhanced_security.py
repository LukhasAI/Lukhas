"""
Test suite for enhanced security implementation
Tests real cryptography, MFA, and secure authentication
"""

import pytest
import asyncio
import json
import secrets
from datetime import datetime, timedelta, timezone
from core.security.enhanced_crypto import EnhancedEncryptionManager, get_encryption_manager
from core.security.enhanced_auth import EnhancedAuthenticationSystem, get_auth_system
from core.security.security_integration import SecurityIntegration, get_security_integration


class TestEnhancedCrypto:
    """Test enhanced cryptography"""
    
    @pytest.fixture
    def crypto_manager(self):
        """Get crypto manager instance"""
        return EnhancedEncryptionManager()
        
    @pytest.mark.asyncio
    async def test_aes_encryption(self, crypto_manager):
        """Test AES-256-GCM encryption"""
        # Test data
        plaintext = b"This is sensitive LUKHAS data"
        
        # Encrypt
        ciphertext, key_id = await crypto_manager.encrypt(
            plaintext,
            purpose='data',
            algorithm='AES-256-GCM'
        )
        
        # Verify it's actually encrypted
        assert ciphertext != plaintext
        assert len(ciphertext) > len(plaintext)  # Includes nonce and tag
        assert key_id is not None
        
        # Decrypt
        decrypted = await crypto_manager.decrypt(ciphertext, key_id)
        assert decrypted == plaintext
        
    @pytest.mark.asyncio
    async def test_chacha20_encryption(self, crypto_manager):
        """Test ChaCha20-Poly1305 encryption"""
        plaintext = b"High-speed encryption test"
        
        # Encrypt
        ciphertext, key_id = await crypto_manager.encrypt(
            plaintext,
            purpose='session',
            algorithm='ChaCha20-Poly1305'
        )
        
        assert ciphertext != plaintext
        assert key_id is not None
        
        # Decrypt
        decrypted = await crypto_manager.decrypt(ciphertext, key_id)
        assert decrypted == plaintext
        
    @pytest.mark.asyncio
    async def test_authenticated_encryption(self, crypto_manager):
        """Test AEAD with associated data"""
        plaintext = b"Secret message"
        associated_data = b"metadata:important"
        
        # Encrypt with associated data
        ciphertext, key_id = await crypto_manager.encrypt(
            plaintext,
            purpose='data',
            algorithm='AES-256-GCM',
            associated_data=associated_data
        )
        
        # Decrypt with correct associated data
        decrypted = await crypto_manager.decrypt(
            ciphertext,
            key_id,
            associated_data=associated_data
        )
        assert decrypted == plaintext
        
        # Decrypt with wrong associated data should fail
        with pytest.raises(Exception):
            await crypto_manager.decrypt(
                ciphertext,
                key_id,
                associated_data=b"wrong_metadata"
            )
            
    @pytest.mark.asyncio
    async def test_json_encryption(self, crypto_manager):
        """Test JSON data encryption"""
        data = {
            'user_id': 'test_user',
            'sensitive_data': 'personality_core',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        # Encrypt JSON
        ciphertext_b64, key_id = await crypto_manager.encrypt_json(data, 'personality')
        
        assert isinstance(ciphertext_b64, str)
        assert key_id is not None
        
        # Decrypt JSON
        decrypted_data = await crypto_manager.decrypt_json(ciphertext_b64, key_id)
        assert decrypted_data == data
        
    def test_key_derivation(self, crypto_manager):
        """Test key derivation functions"""
        password = "secure_password_123"
        salt = crypto_manager.generate_salt()
        
        # PBKDF2
        key1 = crypto_manager.derive_key_pbkdf2(password, salt)
        assert len(key1) == 32  # 256 bits
        
        # Same password and salt should produce same key
        key2 = crypto_manager.derive_key_pbkdf2(password, salt)
        assert key1 == key2
        
        # Different salt should produce different key
        different_salt = crypto_manager.generate_salt()
        key3 = crypto_manager.derive_key_pbkdf2(password, different_salt)
        assert key1 != key3
        
        # Scrypt (memory-hard)
        scrypt_key = crypto_manager.derive_key_scrypt(password, salt)
        assert len(scrypt_key) == 32
        assert scrypt_key != key1  # Different algorithm
        
    @pytest.mark.asyncio
    async def test_key_rotation(self, crypto_manager):
        """Test key rotation"""
        # Encrypt with current key
        plaintext = b"Test data"
        ciphertext1, key_id1 = await crypto_manager.encrypt(plaintext, 'data')
        
        # Rotate keys
        await crypto_manager.rotate_keys('data')
        
        # New encryption should use new key
        ciphertext2, key_id2 = await crypto_manager.encrypt(plaintext, 'data')
        assert key_id1 != key_id2
        assert ciphertext1 != ciphertext2  # Different keys produce different ciphertext
        
        # Old ciphertext should still decrypt
        decrypted1 = await crypto_manager.decrypt(ciphertext1, key_id1)
        assert decrypted1 == plaintext
        
        # New ciphertext should decrypt
        decrypted2 = await crypto_manager.decrypt(ciphertext2, key_id2)
        assert decrypted2 == plaintext
        
    def test_constant_time_compare(self, crypto_manager):
        """Test constant-time comparison"""
        # Equal values
        a = b"secret_key_123"
        b = b"secret_key_123"
        assert crypto_manager.constant_time_compare(a, b) is True
        
        # Different values
        c = b"different_key"
        assert crypto_manager.constant_time_compare(a, c) is False


class TestEnhancedAuth:
    """Test enhanced authentication"""
    
    @pytest.fixture
    def auth_system(self):
        """Get auth system instance"""
        return EnhancedAuthenticationSystem()
        
    def test_jwt_generation(self, auth_system):
        """Test JWT token generation"""
        user_id = "test_user"
        claims = {'role': 'admin', 'scope': ['read', 'write']}
        
        # Generate token
        token = auth_system.generate_jwt(user_id, claims)
        assert token is not None
        assert len(token) > 100  # JWT tokens are long
        
        # Verify token
        payload = auth_system.verify_jwt(token)
        assert payload is not None
        assert payload['user_id'] == user_id
        assert payload['role'] == 'admin'
        assert payload['scope'] == ['read', 'write']
        assert 'exp' in payload
        assert 'iat' in payload
        assert 'jti' in payload
        
    def test_jwt_expiry(self, auth_system):
        """Test JWT expiration"""
        # Generate token with short expiry
        auth_system.jwt_expiry_hours = 0.0001  # Very short for testing
        
        user_id = "test_user"
        token = auth_system.generate_jwt(user_id)
        
        # Verify immediately
        payload = auth_system.verify_jwt(token)
        assert payload is not None
        
        # Wait for expiry
        import time
        time.sleep(1)
        
        # Should be expired
        payload = auth_system.verify_jwt(token)
        assert payload is None
        
    def test_jwt_revocation(self, auth_system):
        """Test JWT revocation"""
        user_id = "test_user"
        token = auth_system.generate_jwt(user_id)
        
        # Verify token works
        payload = auth_system.verify_jwt(token)
        assert payload is not None
        jti = payload['jti']
        
        # Revoke token
        auth_system.revoke_jwt(jti)
        
        # Token should no longer verify
        payload = auth_system.verify_jwt(token)
        assert payload is None
        
    @pytest.mark.asyncio
    async def test_session_management(self, auth_system):
        """Test session creation and validation"""
        user_id = "test_user"
        ip_address = "192.168.1.1"
        user_agent = "TestClient/1.0"
        
        # Create session
        session = await auth_system.create_session(user_id, ip_address, user_agent)
        assert session is not None
        assert session.user_id == user_id
        assert session.ip_address == ip_address
        assert session.mfa_verified is False
        
        # Validate session
        validated = await auth_system.validate_session(session.session_id)
        assert validated is not None
        assert validated.user_id == user_id
        
        # Terminate session
        await auth_system.terminate_session(session.session_id)
        
        # Should no longer validate
        validated = await auth_system.validate_session(session.session_id)
        assert validated is None
        
    @pytest.mark.asyncio
    async def test_totp_mfa(self, auth_system):
        """Test TOTP-based MFA"""
        user_id = "test_user"
        
        # Setup TOTP
        setup_data = await auth_system.setup_totp(user_id)
        assert 'secret' in setup_data
        assert 'qr_code' in setup_data
        assert 'backup_codes' in setup_data
        assert len(setup_data['backup_codes']) == auth_system.backup_code_count
        
        # Generate valid TOTP code
        import pyotp
        totp = pyotp.TOTP(setup_data['secret'])
        valid_code = totp.now()
        
        # Verify valid code
        is_valid = await auth_system.verify_totp(user_id, valid_code)
        assert is_valid is True
        
        # Verify invalid code
        is_valid = await auth_system.verify_totp(user_id, "000000")
        assert is_valid is False
        
    @pytest.mark.asyncio
    async def test_sms_mfa(self, auth_system):
        """Test SMS-based MFA"""
        user_id = "test_user"
        phone = "+1234567890"
        
        # Setup SMS MFA
        success = await auth_system.setup_sms_mfa(user_id, phone)
        assert success is True
        
        # Get code from pending (in real system, would be sent via SMS)
        key = f"sms:{user_id}"
        pending = auth_system.pending_mfa.get(key)
        assert pending is not None
        correct_code = pending['code']
        
        # Verify correct code
        is_valid = await auth_system.verify_sms_code(user_id, correct_code)
        assert is_valid is True
        
        # Code should be cleared after use
        assert key not in auth_system.pending_mfa
        
        # Setup again for invalid test
        await auth_system.setup_sms_mfa(user_id, phone)
        
        # Verify incorrect code
        is_valid = await auth_system.verify_sms_code(user_id, "000000")
        assert is_valid is False
        
    @pytest.mark.asyncio
    async def test_backup_codes(self, auth_system):
        """Test backup code functionality"""
        user_id = "test_user"
        
        # Setup TOTP with backup codes
        setup_data = await auth_system.setup_totp(user_id)
        backup_codes = setup_data['backup_codes']
        
        # Use a backup code
        is_valid = await auth_system.verify_backup_code(user_id, backup_codes[0])
        assert is_valid is True
        
        # Same code should not work again
        is_valid = await auth_system.verify_backup_code(user_id, backup_codes[0])
        assert is_valid is False
        
        # Other backup codes should still work
        is_valid = await auth_system.verify_backup_code(user_id, backup_codes[1])
        assert is_valid is True
        
    @pytest.mark.asyncio
    async def test_rate_limiting(self, auth_system):
        """Test authentication rate limiting"""
        identifier = "test_user"
        
        # Should not be rate limited initially
        allowed = await auth_system.check_rate_limit(identifier)
        assert allowed is True
        
        # Record multiple failed attempts
        for _ in range(auth_system.max_login_attempts):
            await auth_system.record_failed_attempt(identifier)
            
        # Should now be rate limited
        allowed = await auth_system.check_rate_limit(identifier)
        assert allowed is False
        
        # Clear attempts
        await auth_system.clear_failed_attempts(identifier)
        
        # Should no longer be rate limited
        allowed = await auth_system.check_rate_limit(identifier)
        assert allowed is True
        
    def test_api_key_management(self, auth_system):
        """Test API key generation and verification"""
        user_id = "test_user"
        scopes = ['read', 'write', 'execute']
        
        # Generate API key
        key_id, key_secret = auth_system.generate_api_key(user_id, scopes)
        assert key_id is not None
        assert key_secret is not None
        assert len(key_secret) > 30
        
        # Verify valid key
        asyncio.run(self._verify_api_key(auth_system, key_id, key_secret, user_id, scopes))
        
        # Verify invalid key
        asyncio.run(self._verify_invalid_api_key(auth_system, key_id))
        
    async def _verify_api_key(self, auth_system, key_id, key_secret, user_id, scopes):
        """Helper to verify API key"""
        key_data = await auth_system.verify_api_key(key_id, key_secret)
        assert key_data is not None
        assert key_data['user_id'] == user_id
        assert key_data['scopes'] == scopes
        
    async def _verify_invalid_api_key(self, auth_system, key_id):
        """Helper to verify invalid API key"""
        key_data = await auth_system.verify_api_key(key_id, "wrong_secret")
        assert key_data is None


class TestSecurityIntegration:
    """Test integrated security system"""
    
    @pytest.fixture
    async def security(self):
        """Get security integration instance"""
        integration = SecurityIntegration()
        await integration.initialize()
        return integration
        
    @pytest.mark.asyncio
    async def test_module_encryption_hooks(self, security):
        """Test module-specific encryption hooks"""
        # Test memory encryption
        memory_hook = security.module_hooks['memory']
        memory_data = {'content': 'test memory', 'emotion': 'neutral'}
        
        ciphertext, key_id = await memory_hook(memory_data, 'general')
        assert ciphertext is not None
        assert key_id is not None
        
        # Test identity encryption
        identity_hook = security.module_hooks['identity']
        identity_data = {'user_id': 'test', 'biometric_hash': 'xyz123'}
        
        encrypted, key_id = await identity_hook(identity_data)
        assert encrypted is not None
        assert key_id is not None
        
    @pytest.mark.asyncio
    async def test_secure_session_creation(self, security):
        """Test secure session with MFA requirement"""
        user_id = "test_user"
        credentials = {
            'auth_token': 'valid_token_123456789',
            'ip_address': '192.168.1.1',
            'user_agent': 'TestClient/1.0'
        }
        
        # Create session
        result = await security.create_secure_session(user_id, credentials)
        assert result is not None
        
        # Should require MFA setup or verification
        if 'mfa_setup_required' in result:
            assert result['mfa_required'] is True
            assert result['mfa_setup_required'] is True
        else:
            assert result['mfa_required'] is True
            assert 'mfa_methods' in result
            
    @pytest.mark.asyncio
    async def test_request_validation(self, security):
        """Test request validation with security checks"""
        # Create valid JWT
        jwt_token = security.auth.generate_jwt('test_user', {
            'mfa_verified': True,
            'session_id': 'test_session'
        })
        
        # Test valid request
        request_data = {
            'authorization': f'Bearer {jwt_token}',
            'operation': 'read_data',
            'data': {'query': 'test'}
        }
        
        is_valid, error = await security.validate_request(request_data)
        assert is_valid is True
        assert error is None
        
        # Test request without MFA for sensitive operation
        jwt_no_mfa = security.auth.generate_jwt('test_user', {
            'mfa_verified': False,
            'session_id': 'test_session'
        })
        
        sensitive_request = {
            'authorization': f'Bearer {jwt_no_mfa}',
            'operation': 'modify_consciousness',
            'data': {'change': 'test'}
        }
        
        is_valid, error = await security.validate_request(sensitive_request)
        assert is_valid is False
        assert 'MFA required' in error
        
    @pytest.mark.asyncio
    async def test_api_key_validation(self, security):
        """Test API key validation in requests"""
        # Generate API key
        user_id = "api_user"
        key_id, key_secret = security.auth.generate_api_key(
            user_id,
            ['read', 'write']
        )
        
        # Test valid API key request
        request_data = {
            'authorization': f'ApiKey {key_id}:{key_secret}',
            'operation': 'read_data',
            'data': {'query': 'test'}
        }
        
        is_valid, error = await security.validate_request(request_data)
        assert is_valid is True
        
        # Test API key without required scope
        admin_request = {
            'authorization': f'ApiKey {key_id}:{key_secret}',
            'operation': 'admin_action',
            'data': {'action': 'test'}
        }
        
        is_valid, error = await security.validate_request(admin_request)
        assert is_valid is False
        assert 'missing required scope' in error
        
    @pytest.mark.asyncio
    async def test_xor_replacement(self, security):
        """Test that XOR encryption is properly replaced"""
        # Test data
        test_data = b"Sensitive LUKHAS personality data"
        
        # Should NOT use XOR
        ciphertext, key_id = await security.crypto.encrypt(test_data)
        
        # Verify it's not simple XOR (XOR would preserve length)
        assert len(ciphertext) > len(test_data)
        
        # Verify it's properly encrypted
        decrypted = await security.crypto.decrypt(ciphertext, key_id)
        assert decrypted == test_data
        
        # Test that it's not reversible without key
        with pytest.raises(Exception):
            await security.crypto.decrypt(ciphertext, "wrong_key_id")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])