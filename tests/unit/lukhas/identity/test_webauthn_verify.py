"""
Comprehensive test suite for WebAuthn assertion verification.

Tests cryptographic verification, challenge validation, replay attack prevention,
and error handling for WebAuthn authentication assertions.

Coverage target: 85%+
"""

import base64
import hashlib
import json
import struct
from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

import pytest
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, padding, rsa

from lukhas.identity.webauthn_verify import (
    CredentialNotFoundError,
    InvalidAssertionError,
    InvalidChallengeError,
    InvalidSignatureError,
    ReplayAttackError,
    VerificationError,
    VerificationResult,
    _base64url_decode,
    _constant_time_compare,
    _parse_authenticator_data,
    _parse_client_data_json,
    _verify_signature_es256,
    _verify_signature_rs256,
    verify_assertion,
)


# Test Fixtures and Helpers


def base64url_encode(data: bytes) -> str:
    """Encode bytes to base64url string without padding."""
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def create_ec_keypair():
    """Create an ES256 (P-256) key pair for testing."""
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()

    # Export public key as uncompressed point (0x04 + x + y)
    public_numbers = public_key.public_numbers()
    x_bytes = public_numbers.x.to_bytes(32, "big")
    y_bytes = public_numbers.y.to_bytes(32, "big")
    public_key_bytes = b"\x04" + x_bytes + y_bytes

    return private_key, public_key_bytes


def create_rsa_keypair():
    """Create an RS256 (RSA) key pair for testing."""
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()

    # Export public key as DER
    public_key_bytes = public_key.public_key_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    return private_key, public_key_bytes


def create_authenticator_data(
    rp_id: str = "example.com",
    flags: int = 0x05,  # UP=1, UV=1
    sign_count: int = 1,
) -> bytes:
    """Create authenticator data for testing."""
    rp_id_hash = hashlib.sha256(rp_id.encode()).digest()
    flags_byte = bytes([flags])
    counter_bytes = struct.pack(">I", sign_count)
    return rp_id_hash + flags_byte + counter_bytes


def create_client_data_json(
    challenge: str,
    origin: str = "https://example.com",
    type_: str = "webauthn.get",
) -> bytes:
    """Create clientDataJSON for testing."""
    data = {
        "type": type_,
        "challenge": challenge,
        "origin": origin,
    }
    return json.dumps(data).encode("utf-8")


def sign_assertion(
    private_key,
    authenticator_data: bytes,
    client_data_json: bytes,
    algorithm: str = "ES256",
) -> bytes:
    """Sign assertion data with private key."""
    client_data_hash = hashlib.sha256(client_data_json).digest()
    signed_data = authenticator_data + client_data_hash

    if algorithm == "ES256":
        signature = private_key.sign(signed_data, ec.ECDSA(hashes.SHA256()))
    else:  # RS256
        signature = private_key.sign(signed_data, padding.PKCS1v15(), hashes.SHA256())

    return signature


# Test Helper Functions


class TestBase64UrlDecode:
    """Tests for _base64url_decode function."""

    def test_decode_valid_no_padding(self):
        """Test decoding valid base64url string without padding."""
        encoded = "SGVsbG8"  # "Hello" in base64url
        result = _base64url_decode(encoded)
        assert result == b"Hello"

    def test_decode_valid_with_padding_needed(self):
        """Test decoding base64url string that needs padding."""
        encoded = "SGVsbG8gV29ybGQ"  # "Hello World" in base64url
        result = _base64url_decode(encoded)
        assert result == b"Hello World"

    def test_decode_empty_string(self):
        """Test decoding empty string."""
        result = _base64url_decode("")
        assert result == b""

    def test_decode_invalid_characters(self):
        """Test decoding with invalid characters raises error."""
        with pytest.raises(InvalidAssertionError, match="Failed to decode"):
            _base64url_decode("invalid@#$%")

    def test_decode_url_safe_characters(self):
        """Test decoding with URL-safe characters (-_ instead of +/)."""
        # Use characters that differ between base64 and base64url
        data = b"\xfb\xff\xfe"
        encoded = base64.urlsafe_b64encode(data).rstrip(b"=").decode()
        result = _base64url_decode(encoded)
        assert result == data


class TestConstantTimeCompare:
    """Tests for _constant_time_compare function."""

    def test_equal_bytes(self):
        """Test comparing equal byte strings."""
        a = b"same_string"
        b = b"same_string"
        assert _constant_time_compare(a, b) is True

    def test_different_bytes(self):
        """Test comparing different byte strings."""
        a = b"string_one"
        b = b"string_two"
        assert _constant_time_compare(a, b) is False

    def test_different_lengths(self):
        """Test comparing byte strings of different lengths."""
        a = b"short"
        b = b"much_longer_string"
        assert _constant_time_compare(a, b) is False

    def test_empty_bytes(self):
        """Test comparing empty byte strings."""
        assert _constant_time_compare(b"", b"") is True

    def test_timing_safety(self):
        """Test uses hmac.compare_digest for timing safety."""
        # This test verifies we're using the secure comparison
        with patch("lukhas.identity.webauthn_verify.hmac.compare_digest") as mock_compare:
            mock_compare.return_value = True
            result = _constant_time_compare(b"test", b"test")
            assert result is True
            mock_compare.assert_called_once_with(b"test", b"test")


class TestParseAuthenticatorData:
    """Tests for _parse_authenticator_data function."""

    def test_parse_minimal_valid_data(self):
        """Test parsing minimal valid authenticator data (37 bytes)."""
        auth_data = create_authenticator_data(
            rp_id="example.com",
            flags=0x01,  # UP only
            sign_count=42,
        )

        result = _parse_authenticator_data(auth_data)

        assert result["sign_count"] == 42
        assert result["user_present"] is True
        assert result["user_verified"] is False
        assert result["backup_eligible"] is False
        assert result["backup_state"] is False
        assert len(result["rp_id_hash"]) == 32

    def test_parse_all_flags_set(self):
        """Test parsing with all flags set."""
        flags = 0x01 | 0x04 | 0x08 | 0x10  # UP, UV, BE, BS
        auth_data = create_authenticator_data(flags=flags)

        result = _parse_authenticator_data(auth_data)

        assert result["user_present"] is True
        assert result["user_verified"] is True
        assert result["backup_eligible"] is True
        assert result["backup_state"] is True

    def test_parse_with_extra_data(self):
        """Test parsing authenticator data with extensions (>37 bytes)."""
        auth_data = create_authenticator_data() + b"\x00\x01\x02\x03"
        result = _parse_authenticator_data(auth_data)
        assert result["sign_count"] == 1

    def test_parse_too_short(self):
        """Test parsing data that's too short raises error."""
        with pytest.raises(InvalidAssertionError, match="too short"):
            _parse_authenticator_data(b"too_short")

    def test_parse_exactly_36_bytes(self):
        """Test parsing data with exactly 36 bytes (1 byte short)."""
        auth_data = b"0" * 36
        with pytest.raises(InvalidAssertionError, match="too short"):
            _parse_authenticator_data(auth_data)

    def test_parse_counter_max_value(self):
        """Test parsing with maximum counter value."""
        auth_data = create_authenticator_data(sign_count=0xFFFFFFFF)
        result = _parse_authenticator_data(auth_data)
        assert result["sign_count"] == 0xFFFFFFFF

    def test_parse_counter_zero(self):
        """Test parsing with zero counter."""
        auth_data = create_authenticator_data(sign_count=0)
        result = _parse_authenticator_data(auth_data)
        assert result["sign_count"] == 0


class TestParseClientDataJson:
    """Tests for _parse_client_data_json function."""

    def test_parse_valid_client_data(self):
        """Test parsing valid clientDataJSON."""
        client_data = create_client_data_json(
            challenge="test_challenge",
            origin="https://example.com",
        )

        result = _parse_client_data_json(client_data)

        assert result["type"] == "webauthn.get"
        assert result["challenge"] == "test_challenge"
        assert result["origin"] == "https://example.com"

    def test_parse_with_cross_origin(self):
        """Test parsing clientDataJSON with crossOrigin field."""
        data = {
            "type": "webauthn.get",
            "challenge": "challenge",
            "origin": "https://example.com",
            "crossOrigin": True,
        }
        client_data = json.dumps(data).encode()

        result = _parse_client_data_json(client_data)
        assert result["type"] == "webauthn.get"

    def test_parse_missing_type(self):
        """Test parsing without type field raises error."""
        data = {"challenge": "test", "origin": "https://example.com"}
        client_data = json.dumps(data).encode()

        with pytest.raises(InvalidAssertionError, match="Missing 'type'"):
            _parse_client_data_json(client_data)

    def test_parse_missing_challenge(self):
        """Test parsing without challenge field raises error."""
        data = {"type": "webauthn.get", "origin": "https://example.com"}
        client_data = json.dumps(data).encode()

        with pytest.raises(InvalidAssertionError, match="Missing 'challenge'"):
            _parse_client_data_json(client_data)

    def test_parse_missing_origin(self):
        """Test parsing without origin field raises error."""
        data = {"type": "webauthn.get", "challenge": "test"}
        client_data = json.dumps(data).encode()

        with pytest.raises(InvalidAssertionError, match="Missing 'origin'"):
            _parse_client_data_json(client_data)

    def test_parse_invalid_json(self):
        """Test parsing malformed JSON raises error."""
        with pytest.raises(InvalidAssertionError, match="Failed to parse"):
            _parse_client_data_json(b"not valid json{")

    def test_parse_non_utf8(self):
        """Test parsing non-UTF8 bytes raises error."""
        with pytest.raises(InvalidAssertionError):
            _parse_client_data_json(b"\xff\xfe invalid utf8")


class TestVerifySignatureES256:
    """Tests for _verify_signature_es256 function."""

    def test_verify_valid_signature_uncompressed_point(self):
        """Test verifying valid ES256 signature with uncompressed EC point."""
        private_key, public_key_bytes = create_ec_keypair()

        # Create signed data
        data = b"test data to sign"
        signature = private_key.sign(data, ec.ECDSA(hashes.SHA256()))

        # Should not raise
        _verify_signature_es256(public_key_bytes, data, signature)

    def test_verify_valid_signature_der_format(self):
        """Test verifying valid ES256 signature with DER public key."""
        private_key, _ = create_ec_keypair()
        public_key = private_key.public_key()

        # Export as DER
        public_key_der = public_key.public_key_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

        data = b"test data"
        signature = private_key.sign(data, ec.ECDSA(hashes.SHA256()))

        _verify_signature_es256(public_key_der, data, signature)

    def test_verify_invalid_signature(self):
        """Test verifying invalid signature raises error."""
        _, public_key_bytes = create_ec_keypair()

        data = b"test data"
        wrong_signature = b"0" * 64  # Invalid signature

        with pytest.raises(InvalidSignatureError, match="ES256 signature verification failed"):
            _verify_signature_es256(public_key_bytes, data, wrong_signature)

    def test_verify_wrong_data(self):
        """Test verifying signature with wrong data raises error."""
        private_key, public_key_bytes = create_ec_keypair()

        original_data = b"original data"
        different_data = b"different data"

        signature = private_key.sign(original_data, ec.ECDSA(hashes.SHA256()))

        with pytest.raises(InvalidSignatureError):
            _verify_signature_es256(public_key_bytes, different_data, signature)

    def test_verify_wrong_key(self):
        """Test verifying signature with wrong public key raises error."""
        private_key1, _ = create_ec_keypair()
        _, public_key2_bytes = create_ec_keypair()  # Different key pair

        data = b"test data"
        signature = private_key1.sign(data, ec.ECDSA(hashes.SHA256()))

        with pytest.raises(InvalidSignatureError):
            _verify_signature_es256(public_key2_bytes, data, signature)

    def test_verify_invalid_public_key_format(self):
        """Test verifying with invalid public key format raises error."""
        with pytest.raises(InvalidSignatureError, match="Unsupported public key format"):
            _verify_signature_es256(b"invalid_key", b"data", b"signature")

    def test_verify_truncated_public_key(self):
        """Test verifying with truncated public key raises error."""
        _, public_key_bytes = create_ec_keypair()
        truncated = public_key_bytes[:30]  # Too short

        with pytest.raises(InvalidSignatureError):
            _verify_signature_es256(truncated, b"data", b"signature")


class TestVerifySignatureRS256:
    """Tests for _verify_signature_rs256 function."""

    def test_verify_valid_signature(self):
        """Test verifying valid RS256 signature."""
        private_key, public_key_bytes = create_rsa_keypair()

        data = b"test data to sign"
        signature = private_key.sign(data, padding.PKCS1v15(), hashes.SHA256())

        # Should not raise
        _verify_signature_rs256(public_key_bytes, data, signature)

    def test_verify_invalid_signature(self):
        """Test verifying invalid RS256 signature raises error."""
        _, public_key_bytes = create_rsa_keypair()

        data = b"test data"
        wrong_signature = b"0" * 256  # Invalid signature

        with pytest.raises(InvalidSignatureError, match="RS256 signature verification failed"):
            _verify_signature_rs256(public_key_bytes, data, wrong_signature)

    def test_verify_wrong_data(self):
        """Test verifying signature with wrong data raises error."""
        private_key, public_key_bytes = create_rsa_keypair()

        original_data = b"original data"
        different_data = b"different data"

        signature = private_key.sign(original_data, padding.PKCS1v15(), hashes.SHA256())

        with pytest.raises(InvalidSignatureError):
            _verify_signature_rs256(public_key_bytes, different_data, signature)

    def test_verify_ec_key_as_rsa(self):
        """Test verifying with EC key when expecting RSA raises error."""
        _, ec_public_key_bytes = create_ec_keypair()

        with pytest.raises(InvalidSignatureError):
            _verify_signature_rs256(ec_public_key_bytes, b"data", b"signature")

    def test_verify_invalid_public_key(self):
        """Test verifying with invalid public key raises error."""
        with pytest.raises(InvalidSignatureError):
            _verify_signature_rs256(b"not_a_key", b"data", b"signature")


class TestVerifyAssertion:
    """Tests for main verify_assertion function."""

    @pytest.fixture
    def valid_es256_assertion(self):
        """Create a valid ES256 assertion for testing."""
        private_key, public_key_bytes = create_ec_keypair()

        challenge = "test_challenge_123"
        rp_id = "example.com"
        origin = "https://example.com"

        authenticator_data = create_authenticator_data(rp_id=rp_id, sign_count=1)
        client_data_json = create_client_data_json(challenge, origin)
        signature = sign_assertion(private_key, authenticator_data, client_data_json)

        assertion = {
            "id": "credential_123",
            "response": {
                "clientDataJSON": base64url_encode(client_data_json),
                "authenticatorData": base64url_encode(authenticator_data),
                "signature": base64url_encode(signature),
            },
        }

        credential = {
            "user_id": "user_456",
            "credential_id": "credential_123",
            "public_key": base64url_encode(public_key_bytes),
            "counter": 0,
        }

        return {
            "assertion": assertion,
            "credential": credential,
            "challenge": challenge,
            "origin": origin,
            "rp_id": rp_id,
        }

    def test_verify_valid_assertion(self, valid_es256_assertion):
        """Test verifying a valid assertion succeeds."""
        data = valid_es256_assertion

        result = verify_assertion(
            assertion=data["assertion"],
            credential=data["credential"],
            expected_challenge=data["challenge"],
            expected_origin=data["origin"],
            expected_rp_id=data["rp_id"],
        )

        assert result["success"] is True
        assert result["user_id"] == "user_456"
        assert result["credential_id"] == "credential_123"
        assert result["new_sign_count"] == 1
        assert "error" not in result

    def test_verify_with_user_verified_flag(self, valid_es256_assertion):
        """Test verification includes user_verified flag when set."""
        data = valid_es256_assertion

        # Recreate with UV flag
        private_key, _ = create_ec_keypair()
        authenticator_data = create_authenticator_data(flags=0x05)  # UP + UV
        client_data_json = create_client_data_json(data["challenge"], data["origin"])
        signature = sign_assertion(private_key, authenticator_data, client_data_json)

        data["assertion"]["response"]["authenticatorData"] = base64url_encode(authenticator_data)
        data["assertion"]["response"]["signature"] = base64url_encode(signature)
        data["credential"]["public_key"] = base64url_encode(
            ec.generate_private_key(ec.SECP256R1()).public_key().public_key_bytes(
                encoding=serialization.Encoding.DER,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
        )

        # For this test, we'll skip actual signature verification
        # since we're testing flag extraction
        with patch("lukhas.identity.webauthn_verify._verify_signature_es256"):
            result = verify_assertion(
                assertion=data["assertion"],
                credential=data["credential"],
                expected_challenge=data["challenge"],
                expected_origin=data["origin"],
                expected_rp_id=data["rp_id"],
            )

            assert result["success"] is True
            assert result.get("user_verified") is True

    def test_verify_missing_response_field(self, valid_es256_assertion):
        """Test verification fails with missing response field."""
        data = valid_es256_assertion
        assertion = {"id": "credential_123"}  # Missing response

        result = verify_assertion(
            assertion=assertion,
            credential=data["credential"],
            expected_challenge=data["challenge"],
            expected_origin=data["origin"],
            expected_rp_id=data["rp_id"],
        )

        assert result["success"] is False
        assert "Missing 'response'" in result["error"]

    def test_verify_missing_client_data_json(self, valid_es256_assertion):
        """Test verification fails with missing clientDataJSON."""
        data = valid_es256_assertion
        assertion = {
            "id": "credential_123",
            "response": {
                "authenticatorData": "data",
                "signature": "sig",
            },
        }

        result = verify_assertion(
            assertion=assertion,
            credential=data["credential"],
            expected_challenge=data["challenge"],
            expected_origin=data["origin"],
            expected_rp_id=data["rp_id"],
        )

        assert result["success"] is False
        assert "Missing 'clientDataJSON'" in result["error"]

    def test_verify_wrong_type(self, valid_es256_assertion):
        """Test verification fails with wrong ceremony type."""
        data = valid_es256_assertion

        # Create clientDataJSON with wrong type
        client_data_json = create_client_data_json(
            data["challenge"],
            data["origin"],
            type_="webauthn.create",  # Wrong type
        )

        data["assertion"]["response"]["clientDataJSON"] = base64url_encode(client_data_json)

        result = verify_assertion(
            assertion=data["assertion"],
            credential=data["credential"],
            expected_challenge=data["challenge"],
            expected_origin=data["origin"],
            expected_rp_id=data["rp_id"],
        )

        assert result["success"] is False
        assert "Invalid type" in result["error"]

    def test_verify_wrong_origin(self, valid_es256_assertion):
        """Test verification fails with wrong origin."""
        data = valid_es256_assertion

        result = verify_assertion(
            assertion=data["assertion"],
            credential=data["credential"],
            expected_challenge=data["challenge"],
            expected_origin="https://evil.com",  # Wrong origin
            expected_rp_id=data["rp_id"],
        )

        assert result["success"] is False
        assert "Origin mismatch" in result["error"]

    def test_verify_wrong_challenge(self, valid_es256_assertion):
        """Test verification fails with wrong challenge."""
        data = valid_es256_assertion

        result = verify_assertion(
            assertion=data["assertion"],
            credential=data["credential"],
            expected_challenge="wrong_challenge",  # Wrong challenge
            expected_origin=data["origin"],
            expected_rp_id=data["rp_id"],
        )

        assert result["success"] is False
        assert "Challenge verification failed" in result["error"]

    def test_verify_replay_attack_detection(self, valid_es256_assertion):
        """Test verification detects replay attacks via sign counter."""
        data = valid_es256_assertion

        # Set credential counter higher than assertion counter
        data["credential"]["counter"] = 10  # Higher than assertion's counter (1)

        result = verify_assertion(
            assertion=data["assertion"],
            credential=data["credential"],
            expected_challenge=data["challenge"],
            expected_origin=data["origin"],
            expected_rp_id=data["rp_id"],
        )

        assert result["success"] is False
        assert "Sign counter did not increment" in result["error"]

    def test_verify_counter_equal_not_allowed(self, valid_es256_assertion):
        """Test verification fails when counter doesn't increment."""
        data = valid_es256_assertion

        # Set credential counter equal to assertion counter
        data["credential"]["counter"] = 1  # Same as assertion

        result = verify_assertion(
            assertion=data["assertion"],
            credential=data["credential"],
            expected_challenge=data["challenge"],
            expected_origin=data["origin"],
            expected_rp_id=data["rp_id"],
        )

        assert result["success"] is False
        assert "Sign counter did not increment" in result["error"]

    def test_verify_first_use_with_zero_counter(self, valid_es256_assertion):
        """Test verification allows zero counter on first use."""
        data = valid_es256_assertion
        private_key, public_key_bytes = create_ec_keypair()

        # Create assertion with counter=0
        authenticator_data = create_authenticator_data(sign_count=0)
        client_data_json = create_client_data_json(data["challenge"], data["origin"])
        signature = sign_assertion(private_key, authenticator_data, client_data_json)

        data["assertion"]["response"]["authenticatorData"] = base64url_encode(authenticator_data)
        data["assertion"]["response"]["signature"] = base64url_encode(signature)
        data["credential"]["public_key"] = base64url_encode(public_key_bytes)
        data["credential"]["counter"] = 0

        result = verify_assertion(
            assertion=data["assertion"],
            credential=data["credential"],
            expected_challenge=data["challenge"],
            expected_origin=data["origin"],
            expected_rp_id=data["rp_id"],
        )

        assert result["success"] is True
        assert result["new_sign_count"] == 0

    def test_verify_wrong_rp_id(self, valid_es256_assertion):
        """Test verification fails with wrong RP ID."""
        data = valid_es256_assertion

        result = verify_assertion(
            assertion=data["assertion"],
            credential=data["credential"],
            expected_challenge=data["challenge"],
            expected_origin=data["origin"],
            expected_rp_id="wrong.com",  # Wrong RP ID
        )

        assert result["success"] is False
        assert "RP ID hash mismatch" in result["error"]

    def test_verify_user_not_present(self, valid_es256_assertion):
        """Test verification fails when user presence flag not set."""
        data = valid_es256_assertion
        private_key, public_key_bytes = create_ec_keypair()

        # Create with UP flag not set
        authenticator_data = create_authenticator_data(flags=0x00)
        client_data_json = create_client_data_json(data["challenge"], data["origin"])
        signature = sign_assertion(private_key, authenticator_data, client_data_json)

        data["assertion"]["response"]["authenticatorData"] = base64url_encode(authenticator_data)
        data["assertion"]["response"]["signature"] = base64url_encode(signature)
        data["credential"]["public_key"] = base64url_encode(public_key_bytes)

        result = verify_assertion(
            assertion=data["assertion"],
            credential=data["credential"],
            expected_challenge=data["challenge"],
            expected_origin=data["origin"],
            expected_rp_id=data["rp_id"],
        )

        assert result["success"] is False
        assert "User presence flag not set" in result["error"]

    def test_verify_invalid_signature(self, valid_es256_assertion):
        """Test verification fails with invalid signature."""
        data = valid_es256_assertion

        # Replace signature with garbage
        data["assertion"]["response"]["signature"] = base64url_encode(b"0" * 64)

        result = verify_assertion(
            assertion=data["assertion"],
            credential=data["credential"],
            expected_challenge=data["challenge"],
            expected_origin=data["origin"],
            expected_rp_id=data["rp_id"],
        )

        assert result["success"] is False
        assert "Signature verification failed" in result["error"]

    def test_verify_rs256_fallback(self):
        """Test verification falls back to RS256 if ES256 fails."""
        private_key, public_key_bytes = create_rsa_keypair()

        challenge = "test_challenge"
        rp_id = "example.com"
        origin = "https://example.com"

        authenticator_data = create_authenticator_data(rp_id=rp_id, sign_count=1)
        client_data_json = create_client_data_json(challenge, origin)
        signature = sign_assertion(private_key, authenticator_data, client_data_json, "RS256")

        assertion = {
            "id": "cred",
            "response": {
                "clientDataJSON": base64url_encode(client_data_json),
                "authenticatorData": base64url_encode(authenticator_data),
                "signature": base64url_encode(signature),
            },
        }

        credential = {
            "user_id": "user",
            "credential_id": "cred",
            "public_key": base64url_encode(public_key_bytes),
            "counter": 0,
        }

        result = verify_assertion(
            assertion=assertion,
            credential=credential,
            expected_challenge=challenge,
            expected_origin=origin,
            expected_rp_id=rp_id,
        )

        assert result["success"] is True

    def test_verify_malformed_base64(self, valid_es256_assertion):
        """Test verification handles malformed base64 gracefully."""
        data = valid_es256_assertion

        data["assertion"]["response"]["signature"] = "not@valid#base64!"

        result = verify_assertion(
            assertion=data["assertion"],
            credential=data["credential"],
            expected_challenge=data["challenge"],
            expected_origin=data["origin"],
            expected_rp_id=data["rp_id"],
        )

        assert result["success"] is False
        assert "error" in result

    def test_verify_includes_backup_flags(self, valid_es256_assertion):
        """Test verification includes backup flags when set."""
        data = valid_es256_assertion
        private_key, public_key_bytes = create_ec_keypair()

        # Set backup flags
        flags = 0x01 | 0x08 | 0x10  # UP + BE + BS
        authenticator_data = create_authenticator_data(flags=flags)
        client_data_json = create_client_data_json(data["challenge"], data["origin"])
        signature = sign_assertion(private_key, authenticator_data, client_data_json)

        data["assertion"]["response"]["authenticatorData"] = base64url_encode(authenticator_data)
        data["assertion"]["response"]["signature"] = base64url_encode(signature)
        data["credential"]["public_key"] = base64url_encode(public_key_bytes)

        result = verify_assertion(
            assertion=data["assertion"],
            credential=data["credential"],
            expected_challenge=data["challenge"],
            expected_origin=data["origin"],
            expected_rp_id=data["rp_id"],
        )

        assert result["success"] is True
        assert result.get("backup_eligible") is True
        assert result.get("backup_state") is True


class TestExceptionHierarchy:
    """Tests for exception classes."""

    def test_verification_error_base_class(self):
        """Test VerificationError is base class for all verification errors."""
        assert issubclass(InvalidSignatureError, VerificationError)
        assert issubclass(InvalidChallengeError, VerificationError)
        assert issubclass(ReplayAttackError, VerificationError)
        assert issubclass(InvalidAssertionError, VerificationError)
        assert issubclass(CredentialNotFoundError, VerificationError)

    def test_exceptions_are_raisable(self):
        """Test all exceptions can be raised and caught."""
        with pytest.raises(InvalidSignatureError):
            raise InvalidSignatureError("test")

        with pytest.raises(InvalidChallengeError):
            raise InvalidChallengeError("test")

        with pytest.raises(ReplayAttackError):
            raise ReplayAttackError("test")

        with pytest.raises(InvalidAssertionError):
            raise InvalidAssertionError("test")

        with pytest.raises(CredentialNotFoundError):
            raise CredentialNotFoundError("test")

    def test_catch_with_base_class(self):
        """Test exceptions can be caught with base VerificationError."""
        with pytest.raises(VerificationError):
            raise InvalidSignatureError("test")
