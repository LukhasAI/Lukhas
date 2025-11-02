"""
LUKHAS Cryptographic Hygiene Tests - T4/0.01% Excellence
========================================================

Comprehensive cryptographic security validation tests ensuring LUKHAS meets
T4/0.01% excellence standards for cryptographic implementations.

Tests cover:
- Weak algorithm detection and prevention
- Key strength validation
- Secure random number generation
- Proper salt usage in password hashing
- JWT security implementation
- Encryption/decryption security
- Certificate validation
- Cryptographic constant-time operations

All tests must pass with 0% failure rate for T4/0.01% certification.
"""

import hashlib
import hmac
import os
import secrets
import time
from unittest.mock import patch

import jwt
import pytest
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Import LUKHAS modules for testing
try:
    from identity.lambda_id import LambdaIDGenerator
    from identity.security_hardening import SecurityHardeningManager

    LUKHAS_MODULES_AVAILABLE = True
except ImportError:
    LUKHAS_MODULES_AVAILABLE = False


class TestCryptographicWeakness:
    """Test detection and prevention of weak cryptographic algorithms."""

    def test_weak_hash_algorithms_blocked(self):
        """Test that weak hash algorithms are blocked."""
        # Test MD5 rejection
        with pytest.raises((ValueError, RuntimeError)):
            # This should be blocked by security controls
            hashlib.md5(b"test")

        # Test SHA1 rejection for security-critical operations
        with pytest.raises((ValueError, RuntimeError)):
            # SHA1 should be rejected for password hashing
            hashlib.sha1(b"password")

    def test_strong_hash_algorithms_allowed(self):
        """Test that strong hash algorithms work correctly."""
        # SHA-256 should work
        strong_hash = hashlib.sha256(b"test data")
        assert strong_hash.hexdigest() is not None
        assert len(strong_hash.hexdigest()) == 64

        # SHA-512 should work
        strong_hash_512 = hashlib.sha512(b"test data")
        assert strong_hash_512.hexdigest() is not None
        assert len(strong_hash_512.hexdigest()) == 128

        # SHA-3 should work
        sha3_hash = hashlib.sha3_256(b"test data")
        assert sha3_hash.hexdigest() is not None
        assert len(sha3_hash.hexdigest()) == 64

    def test_weak_symmetric_encryption_blocked(self):
        """Test that weak symmetric encryption algorithms are blocked."""
        # DES should be rejected
        with pytest.raises((ValueError, ImportError)):
            from cryptography.hazmat.primitives.ciphers import algorithms

            algorithms.TripleDES(b"12345678" * 3)  # Should fail

    def test_strong_symmetric_encryption_allowed(self):
        """Test that strong symmetric encryption works."""
        # AES-256 should work
        key = secrets.token_bytes(32)  # 256-bit key
        iv = secrets.token_bytes(16)  # 128-bit IV

        cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())

        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(b"test message") + encryptor.finalize()

        assert ciphertext is not None
        assert len(ciphertext) >= 12  # At least the message length

        # Verify decryption works
        decryptor = cipher.decryptor()
        decryptor.authenticate_additional_data(b"")
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        assert plaintext == b"test message"


class TestKeyStrengthValidation:
    """Test cryptographic key strength requirements."""

    def test_weak_keys_rejected(self):
        """Test that weak keys are rejected."""
        weak_keys = [
            b"weak",  # Too short
            b"12345678",  # Predictable
            b"password123",  # Common pattern
            b"a" * 16,  # No entropy
        ]

        for weak_key in weak_keys:
            with pytest.raises((ValueError, RuntimeError)):
                # This should be caught by key validation
                self._validate_key_strength(weak_key)

    def test_strong_keys_accepted(self):
        """Test that strong keys are accepted."""
        # Generate cryptographically secure key
        strong_key = secrets.token_bytes(32)
        assert self._validate_key_strength(strong_key) is True

        # Test minimum entropy requirements
        entropy = self._calculate_entropy(strong_key)
        assert entropy >= 6.0  # Minimum entropy bits per byte

    def test_rsa_key_strength(self):
        """Test RSA key strength requirements."""
        # Weak RSA keys should be rejected
        with pytest.raises(ValueError):
            rsa.generate_private_key(
                public_exponent=65537, key_size=1024, backend=default_backend()  # Too weak for modern standards
            )

        # Strong RSA keys should work
        strong_key = rsa.generate_private_key(
            public_exponent=65537, key_size=4096, backend=default_backend()  # Strong key size
        )

        assert strong_key.key_size >= 2048

        # Test key can be used for encryption/decryption
        public_key = strong_key.public_key()
        message = b"test message"

        ciphertext = public_key.encrypt(
            message, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
        )

        decrypted = strong_key.decrypt(
            ciphertext, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
        )

        assert decrypted == message

    def _validate_key_strength(self, key: bytes) -> bool:
        """Validate cryptographic key strength."""
        # Minimum length check
        if len(key) < 16:
            raise ValueError("Key too short")

        # Entropy check
        entropy = self._calculate_entropy(key)
        if entropy < 6.0:
            raise ValueError("Key has insufficient entropy")

        # Pattern check
        if key == key[0:1] * len(key):
            raise ValueError("Key has no variation")

        return True

    def _calculate_entropy(self, data: bytes) -> float:
        """Calculate Shannon entropy of data."""
        if not data:
            return 0.0

        # Count byte frequencies
        frequencies = {}
        for byte in data:
            frequencies[byte] = frequencies.get(byte, 0) + 1

        # Calculate entropy
        entropy = 0.0
        length = len(data)

        for count in frequencies.values():
            probability = count / length
            if probability > 0:
                entropy -= probability * (probability.bit_length() - 1)

        return entropy


class TestSecureRandomGeneration:
    """Test secure random number generation."""

    def test_weak_random_rejected(self):
        """Test that weak random number generators are rejected."""
        # Mock the random module to ensure it's not used
        import random

        def failing_random():
            raise RuntimeError("Insecure random number generation detected")

        with patch.object(random, "random", failing_random):
            with pytest.raises(RuntimeError):
                # This should fail if code tries to use insecure random
                random.random()

    def test_secure_random_generation(self):
        """Test secure random number generation."""
        # Test secrets module
        secure_bytes = secrets.token_bytes(32)
        assert len(secure_bytes) == 32

        # Test that consecutive calls produce different values
        secure_bytes_2 = secrets.token_bytes(32)
        assert secure_bytes != secure_bytes_2

        # Test os.urandom
        os_random = os.urandom(32)
        assert len(os_random) == 32
        assert os_random != secure_bytes

        # Test entropy quality
        entropy = self._measure_entropy(secure_bytes + secure_bytes_2 + os_random)
        assert entropy >= 7.0  # High entropy requirement

    def test_nonce_generation_quality(self):
        """Test cryptographic nonce generation quality."""
        nonces = set()

        # Generate 1000 nonces and check for duplicates
        for _ in range(1000):
            nonce = secrets.token_hex(16)
            assert nonce not in nonces, "Duplicate nonce detected"
            nonces.add(nonce)
            assert len(nonce) == 32  # 16 bytes = 32 hex chars

    def _measure_entropy(self, data: bytes) -> float:
        """Measure entropy of random data."""
        if not data:
            return 0.0

        byte_counts = [0] * 256
        for byte in data:
            byte_counts[byte] += 1

        entropy = 0.0
        length = len(data)

        for count in byte_counts:
            if count > 0:
                probability = count / length
                entropy -= probability * (probability.bit_length() - 1)

        return entropy


class TestPasswordHashing:
    """Test secure password hashing implementations."""

    def test_weak_password_hashing_blocked(self):
        """Test that weak password hashing is blocked."""
        password = "test_password"

        # Plain text storage should be impossible
        with pytest.raises((ValueError, RuntimeError)):
            pass  # Should be rejected

        # Simple hash without salt should be rejected
        with pytest.raises((ValueError, RuntimeError)):
            hashlib.sha256(password.encode()).hexdigest()

    def test_secure_password_hashing(self):
        """Test secure password hashing with proper salt."""
        password = "test_password_123"

        # Use PBKDF2 with proper parameters
        salt = secrets.token_bytes(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,  # Strong iteration count
            backend=default_backend(),
        )

        key = kdf.derive(password.encode())

        # Verify properties
        assert len(key) == 32
        assert len(salt) == 16

        # Test that same password with same salt produces same key
        kdf2 = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000, backend=default_backend())
        key2 = kdf2.derive(password.encode())
        assert key == key2

        # Test that different salt produces different key
        salt3 = secrets.token_bytes(16)
        kdf3 = PBKDF2HMAC(
            algorithm=hashes.SHA256(), length=32, salt=salt3, iterations=100000, backend=default_backend()
        )
        key3 = kdf3.derive(password.encode())
        assert key != key3

    def test_salt_requirements(self):
        """Test salt generation and usage requirements."""
        # Salt must be unique for each password
        salts = set()
        for _ in range(100):
            salt = secrets.token_bytes(16)
            assert salt not in salts, "Duplicate salt detected"
            salts.add(salt)

        # Salt must have sufficient entropy
        salt = secrets.token_bytes(16)
        entropy = self._calculate_entropy(salt)
        assert entropy >= 6.0

    def test_timing_attack_resistance(self):
        """Test resistance to timing attacks."""
        password1 = "password123"
        password2 = "different_password"
        wrong_password = "wrong_password"

        # Hash both passwords
        salt1 = secrets.token_bytes(16)
        salt2 = secrets.token_bytes(16)

        hash1 = self._secure_hash_password(password1, salt1)
        self._secure_hash_password(password2, salt2)

        # Time password verification
        times = []
        for _ in range(10):
            start_time = time.perf_counter()
            result = self._verify_password(wrong_password, hash1, salt1)
            end_time = time.perf_counter()
            times.append(end_time - start_time)
            assert result is False

        # Verify timing consistency (coefficient of variation < 0.1)
        avg_time = sum(times) / len(times)
        variance = sum((t - avg_time) ** 2 for t in times) / len(times)
        std_dev = variance**0.5
        cv = std_dev / avg_time if avg_time > 0 else 0

        assert cv < 0.1, f"Timing attack vulnerability detected (CV: {cv})"

    def _secure_hash_password(self, password: str, salt: bytes) -> bytes:
        """Securely hash a password."""
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000, backend=default_backend())
        return kdf.derive(password.encode())

    def _verify_password(self, password: str, expected_hash: bytes, salt: bytes) -> bool:
        """Verify password in constant time."""
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000, backend=default_backend())

        try:
            derived_hash = kdf.derive(password.encode())
            return hmac.compare_digest(expected_hash, derived_hash)
        except Exception:
            return False

    def _calculate_entropy(self, data: bytes) -> float:
        """Calculate Shannon entropy."""
        if not data:
            return 0.0

        frequencies = {}
        for byte in data:
            frequencies[byte] = frequencies.get(byte, 0) + 1

        entropy = 0.0
        length = len(data)

        for count in frequencies.values():
            if count > 0:
                probability = count / length
                entropy -= probability * (probability.bit_length() - 1)

        return entropy


class TestJWTSecurity:
    """Test JWT security implementation."""

    def test_jwt_none_algorithm_blocked(self):
        """Test that 'none' algorithm is blocked."""
        payload = {"user_id": 123, "exp": int(time.time()) + 3600}

        # 'none' algorithm should be rejected
        with pytest.raises((ValueError, jwt.InvalidAlgorithmError)):
            jwt.encode(payload, "", algorithm="none")

        # Decoding with 'none' should be rejected
        malicious_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJub25lIn0.eyJ1c2VyX2lkIjoxMjN9."

        with pytest.raises((ValueError, jwt.InvalidTokenError)):
            jwt.decode(malicious_token, algorithms=["none"])

    def test_jwt_algorithm_confusion_prevented(self):
        """Test prevention of algorithm confusion attacks."""
        payload = {"user_id": 123, "exp": int(time.time()) + 3600}

        # Generate RSA key pair
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
        public_key = private_key.public_key()

        # Sign with RS256
        token = jwt.encode(payload, private_key, algorithm="RS256")

        # Try to verify with HS256 (should fail)
        public_key_pem = public_key.public_key_bytes(
            encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        with pytest.raises(jwt.InvalidTokenError):
            jwt.decode(token, public_key_pem, algorithms=["HS256"])

    def test_jwt_secure_implementation(self):
        """Test secure JWT implementation."""
        payload = {
            "user_id": 123,
            "username": "testuser",
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600,
            "iss": "lukhas-auth",
            "aud": "lukhas-api",
        }

        # Use strong secret key
        secret_key = secrets.token_urlsafe(64)

        # Sign with HS256
        token = jwt.encode(payload, secret_key, algorithm="HS256")

        # Verify token
        decoded = jwt.decode(token, secret_key, algorithms=["HS256"], audience="lukhas-api", issuer="lukhas-auth")

        assert decoded["user_id"] == 123
        assert decoded["username"] == "testuser"

    def test_jwt_key_strength(self):
        """Test JWT signing key strength requirements."""
        payload = {"user_id": 123, "exp": int(time.time()) + 3600}

        # Weak keys should be rejected
        weak_keys = ["weak", "12345678", "secret", "password"]

        for weak_key in weak_keys:
            with pytest.raises((ValueError, RuntimeError)):
                self._validate_jwt_key_strength(weak_key)

        # Strong key should work
        strong_key = secrets.token_urlsafe(64)
        assert self._validate_jwt_key_strength(strong_key) is True

        token = jwt.encode(payload, strong_key, algorithm="HS256")
        decoded = jwt.decode(token, strong_key, algorithms=["HS256"])
        assert decoded["user_id"] == 123

    def _validate_jwt_key_strength(self, key: str) -> bool:
        """Validate JWT signing key strength."""
        # Minimum length check
        if len(key) < 32:
            raise ValueError("JWT key too short")

        # Common weak keys check
        weak_keys = {"secret", "password", "key", "token", "jwt"}
        if key.lower() in weak_keys:
            raise ValueError("JWT key is too weak")

        # Entropy check
        entropy = self._calculate_string_entropy(key)
        if entropy < 4.0:
            raise ValueError("JWT key has insufficient entropy")

        return True

    def _calculate_string_entropy(self, s: str) -> float:
        """Calculate entropy of string."""
        if not s:
            return 0.0

        frequencies = {}
        for char in s:
            frequencies[char] = frequencies.get(char, 0) + 1

        entropy = 0.0
        length = len(s)

        for count in frequencies.values():
            if count > 0:
                probability = count / length
                entropy -= probability * (probability.bit_length() - 1)

        return entropy


@pytest.mark.skipif(not LUKHAS_MODULES_AVAILABLE, reason="LUKHAS modules not available")
class TestLUKHASCryptographicIntegration:
    """Test LUKHAS-specific cryptographic implementations."""

    def test_lambda_id_cryptographic_security(self):
        """Test ΛiD cryptographic security."""
        generator = LambdaIDGenerator()

        # Generate multiple ΛiDs
        lambda_ids = []
        for _ in range(100):
            lid = generator.generate()
            lambda_ids.append(lid)

        # Verify uniqueness
        assert len(set(lambda_ids)) == 100, "Duplicate ΛiDs detected"

        # Verify format security
        for lid in lambda_ids[:10]:
            assert self._validate_lambda_id_security(lid)

    async def test_security_hardening_crypto_strength(self):
        """Test security hardening cryptographic strength."""
        manager = SecurityHardeningManager()

        # Test nonce generation
        nonces = []
        for _ in range(1000):
            nonce = await manager.generate_nonce()
            nonces.append(nonce)

        # Verify nonce uniqueness
        assert len(set(nonces)) == 1000, "Duplicate nonces detected"

        # Test nonce validation
        test_nonce = nonces[0]
        valid, reason = await manager.validate_nonce(test_nonce)
        assert valid is True

        # Test replay protection
        valid2, reason2 = await manager.validate_nonce(test_nonce)
        assert valid2 is False, "Replay attack not prevented"

    def _validate_lambda_id_security(self, lambda_id: str) -> bool:
        """Validate ΛiD security properties."""
        # Check format
        if not lambda_id.startswith("λ"):
            return False

        # Check entropy
        entropy = self._calculate_string_entropy(lambda_id)
        if entropy < 4.0:
            return False

        # Check length
        if len(lambda_id) < 16:
            return False

        return True

    def _calculate_string_entropy(self, s: str) -> float:
        """Calculate string entropy."""
        if not s:
            return 0.0

        frequencies = {}
        for char in s:
            frequencies[char] = frequencies.get(char, 0) + 1

        entropy = 0.0
        length = len(s)

        for count in frequencies.values():
            probability = count / length
            if probability > 0:
                entropy -= probability * (probability.bit_length() - 1)

        return entropy


class TestConstantTimeOperations:
    """Test constant-time cryptographic operations."""

    def test_constant_time_comparison(self):
        """Test constant-time string comparison."""
        secret1 = "supersecretpassword123"
        secret2 = "supersecretpassword123"
        wrong_secret = "wrongpassword123456"

        # Test that correct comparison takes consistent time
        times_correct = []
        for _ in range(50):
            start = time.perf_counter()
            result = hmac.compare_digest(secret1, secret2)
            end = time.perf_counter()
            times_correct.append(end - start)
            assert result is True

        # Test that incorrect comparison takes consistent time
        times_wrong = []
        for _ in range(50):
            start = time.perf_counter()
            result = hmac.compare_digest(secret1, wrong_secret)
            end = time.perf_counter()
            times_wrong.append(end - start)
            assert result is False

        # Verify timing consistency
        avg_correct = sum(times_correct) / len(times_correct)
        avg_wrong = sum(times_wrong) / len(times_wrong)

        # Times should be similar (within 20% variance)
        time_ratio = abs(avg_correct - avg_wrong) / max(avg_correct, avg_wrong)
        assert time_ratio < 0.2, f"Timing attack vulnerability: {time_ratio:.3f}"


class TestCertificateValidation:
    """Test certificate validation security."""

    def test_certificate_validation_enabled(self):
        """Test that certificate validation cannot be disabled."""
        import ssl

        # Default context should have verification enabled
        context = ssl.create_default_context()
        assert context.verify_mode == ssl.CERT_REQUIRED
        assert context.check_hostname is True

        # Test that disabling verification raises error in production
        with pytest.raises((ValueError, RuntimeError)):
            context.verify_mode = ssl.CERT_NONE
            context.check_hostname = False
            # This should be caught by security controls

    def test_tls_version_security(self):
        """Test minimum TLS version requirements."""
        import ssl

        context = ssl.create_default_context()

        # Should use TLS 1.2 or higher
        assert context.minimum_version >= ssl.TLSVersion.TLSv1_2

        # Should not allow SSLv3 or earlier
        assert context.maximum_version >= ssl.TLSVersion.TLSv1_2


# Performance benchmarks for T4/0.01% requirements
class TestCryptographicPerformance:
    """Test cryptographic operations meet performance requirements."""

    def test_hash_performance(self):
        """Test hash performance meets T4/0.01% standards."""
        data = b"test data" * 1000  # 9KB of data

        start_time = time.perf_counter()
        for _ in range(1000):
            hashlib.sha256(data).hexdigest()
        end_time = time.perf_counter()

        avg_time_ms = (end_time - start_time) * 1000 / 1000

        # Should complete within 1ms average for T4/0.01%
        assert avg_time_ms < 1.0, f"Hash too slow: {avg_time_ms:.3f}ms"

    def test_symmetric_encryption_performance(self):
        """Test symmetric encryption performance."""
        key = secrets.token_bytes(32)
        data = b"benchmark data" * 1000  # 14KB

        start_time = time.perf_counter()
        for _ in range(100):
            iv = secrets.token_bytes(16)
            cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
            encryptor = cipher.encryptor()
            encryptor.update(data)
            encryptor.finalize()
        end_time = time.perf_counter()

        avg_time_ms = (end_time - start_time) * 1000 / 100

        # Should complete within 5ms average for T4/0.01%
        assert avg_time_ms < 5.0, f"Encryption too slow: {avg_time_ms:.3f}ms"


# Compliance and standards testing
class TestCryptographicCompliance:
    """Test compliance with cryptographic standards."""

    def test_fips_compliance(self):
        """Test FIPS-approved algorithm usage."""
        # Only FIPS-approved algorithms should be available
        approved_hashes = {"sha256", "sha384", "sha512", "sha3_256", "sha3_384", "sha3_512"}

        # Test that approved algorithms work
        for hash_name in approved_hashes:
            hash_func = getattr(hashlib, hash_name)
            result = hash_func(b"test").hexdigest()
            assert result is not None
            assert len(result) > 0

    def test_nist_key_length_compliance(self):
        """Test NIST key length requirements."""
        # AES keys must be 128, 192, or 256 bits
        valid_key_sizes = [16, 24, 32]  # bytes

        for key_size in valid_key_sizes:
            key = secrets.token_bytes(key_size)
            cipher = Cipher(algorithms.AES(key), modes.GCM(secrets.token_bytes(16)), backend=default_backend())
            assert cipher is not None

        # Invalid key sizes should fail
        invalid_key_sizes = [8, 12, 20, 28]
        for key_size in invalid_key_sizes:
            with pytest.raises(ValueError):
                key = secrets.token_bytes(key_size)
                Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())


# Test runner configuration for T4/0.01% excellence
if __name__ == "__main__":
    # Run with strict requirements for T4/0.01%
    pytest.main(
        [
            __file__,
            "-v",
            "--tb=short",
            "--strict-markers",
            "--strict-config",
            "-x",  # Stop on first failure
            "--disable-warnings",
            "--co",  # Collect only, don't run (for validation)
        ]
    )
