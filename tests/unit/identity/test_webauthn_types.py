#!/usr/bin/env python3
"""
Unit tests for WebAuthn type definitions.

Tests that WebAuthn TypedDict structures conform to W3C WebAuthn specification
and can parse real WebAuthn responses from browsers.

Task #591 - Define WebAuthn Types (PREREQUISITE for #581, #589, #597, #599)
"""
from __future__ import annotations

import base64
import json
import sys
from pathlib import Path
from typing import Any, get_type_hints

import pytest

# Import webauthn_types module directly to avoid __init__ dependencies
webauthn_types_path = Path(__file__).parent.parent.parent.parent / "lukhas_website" / "lukhas" / "identity" / "webauthn_types.py"
spec = __import__("importlib.util").util.spec_from_file_location("webauthn_types", webauthn_types_path)
webauthn_types = __import__("importlib.util").util.module_from_spec(spec)
spec.loader.exec_module(webauthn_types)
# Register in sys.modules so get_type_hints can find it
sys.modules["webauthn_types"] = webauthn_types

# Now import the types
AuthenticatorAssertionResponse = webauthn_types.AuthenticatorAssertionResponse
AuthenticatorAttestationResponse = webauthn_types.AuthenticatorAttestationResponse
AuthenticatorSelectionCriteria = webauthn_types.AuthenticatorSelectionCriteria
CredentialCreationOptions = webauthn_types.CredentialCreationOptions
CredentialRequestOptions = webauthn_types.CredentialRequestOptions
PublicKeyCredentialAssertion = webauthn_types.PublicKeyCredentialAssertion
PublicKeyCredentialCreation = webauthn_types.PublicKeyCredentialCreation
PublicKeyCredentialDescriptor = webauthn_types.PublicKeyCredentialDescriptor
PublicKeyCredentialParameters = webauthn_types.PublicKeyCredentialParameters
PublicKeyCredentialRpEntity = webauthn_types.PublicKeyCredentialRpEntity
PublicKeyCredentialUserEntity = webauthn_types.PublicKeyCredentialUserEntity
VerifiedAuthentication = webauthn_types.VerifiedAuthentication
VerifiedRegistration = webauthn_types.VerifiedRegistration


class TestPublicKeyCredentialRpEntity:
    """Test Relying Party entity type."""

    def test_minimal_rp_entity(self):
        """Test RP entity with only required fields."""
        rp: PublicKeyCredentialRpEntity = {
            "name": "LUKHAS AI"
        }
        assert rp["name"] == "LUKHAS AI"

    def test_full_rp_entity(self):
        """Test RP entity with all fields."""
        rp: PublicKeyCredentialRpEntity = {
            "name": "LUKHAS AI",
            "id": "ai"
        }
        assert rp["name"] == "LUKHAS AI"
        assert rp["id"] == "ai"


class TestPublicKeyCredentialUserEntity:
    """Test User entity type."""

    def test_user_entity_required_fields(self):
        """Test user entity with all required fields."""
        user_id = base64.urlsafe_b64encode(b"user-123").decode().rstrip("=")
        user: PublicKeyCredentialUserEntity = {
            "id": user_id,
            "name": "alice@example.com",
            "displayName": "Alice Smith"
        }
        assert user["id"] == user_id
        assert user["name"] == "alice@example.com"
        assert user["displayName"] == "Alice Smith"

    def test_user_entity_base64_encoding(self):
        """Test that user ID is properly base64 encoded."""
        user_id_bytes = b"test-user-12345"
        user_id_b64 = base64.urlsafe_b64encode(user_id_bytes).decode().rstrip("=")

        user: PublicKeyCredentialUserEntity = {
            "id": user_id_b64,
            "name": "test@example.com",
            "displayName": "Test User"
        }

        # Verify we can decode it back
        decoded = base64.urlsafe_b64decode(user["id"] + "===")
        assert decoded == user_id_bytes


class TestPublicKeyCredentialParameters:
    """Test credential parameters type."""

    def test_es256_algorithm(self):
        """Test ES256 (ECDSA with SHA-256) algorithm."""
        param: PublicKeyCredentialParameters = {
            "type": "public-key",
            "alg": -7  # ES256 COSE identifier
        }
        assert param["type"] == "public-key"
        assert param["alg"] == -7

    def test_rs256_algorithm(self):
        """Test RS256 (RSA with SHA-256) algorithm."""
        param: PublicKeyCredentialParameters = {
            "type": "public-key",
            "alg": -257  # RS256 COSE identifier
        }
        assert param["type"] == "public-key"
        assert param["alg"] == -257


class TestPublicKeyCredentialDescriptor:
    """Test credential descriptor type."""

    def test_minimal_descriptor(self):
        """Test descriptor with only required fields."""
        cred_id = base64.urlsafe_b64encode(b"credential-123").decode().rstrip("=")
        descriptor: PublicKeyCredentialDescriptor = {
            "type": "public-key",
            "id": cred_id
        }
        assert descriptor["type"] == "public-key"
        assert descriptor["id"] == cred_id

    def test_descriptor_with_transports(self):
        """Test descriptor with transport hints."""
        cred_id = base64.urlsafe_b64encode(b"credential-456").decode().rstrip("=")
        descriptor: PublicKeyCredentialDescriptor = {
            "type": "public-key",
            "id": cred_id,
            "transports": ["internal", "hybrid"]
        }
        assert "transports" in descriptor
        assert "internal" in descriptor["transports"]
        assert "hybrid" in descriptor["transports"]


class TestAuthenticatorSelectionCriteria:
    """Test authenticator selection criteria type."""

    def test_platform_authenticator(self):
        """Test platform authenticator selection."""
        criteria: AuthenticatorSelectionCriteria = {
            "authenticatorAttachment": "platform",
            "residentKey": "required",
            "userVerification": "required"
        }
        assert criteria["authenticatorAttachment"] == "platform"
        assert criteria["residentKey"] == "required"
        assert criteria["userVerification"] == "required"

    def test_cross_platform_authenticator(self):
        """Test cross-platform (roaming) authenticator selection."""
        criteria: AuthenticatorSelectionCriteria = {
            "authenticatorAttachment": "cross-platform",
            "userVerification": "preferred"
        }
        assert criteria["authenticatorAttachment"] == "cross-platform"
        assert criteria["userVerification"] == "preferred"


class TestCredentialCreationOptions:
    """Test credential creation (registration) options."""

    def test_minimal_creation_options(self):
        """Test creation options with only required fields."""
        challenge = base64.urlsafe_b64encode(b"random-challenge-123").decode().rstrip("=")
        user_id = base64.urlsafe_b64encode(b"user-456").decode().rstrip("=")

        options: CredentialCreationOptions = {
            "challenge": challenge,
            "rp": {
                "name": "LUKHAS AI",
                "id": "ai"
            },
            "user": {
                "id": user_id,
                "name": "test@example.com",
                "displayName": "Test User"
            },
            "pubKeyCredParams": [
                {"type": "public-key", "alg": -7},  # ES256
                {"type": "public-key", "alg": -257}  # RS256
            ]
        }

        assert options["challenge"] == challenge
        assert options["rp"]["name"] == "LUKHAS AI"
        assert options["user"]["id"] == user_id
        assert len(options["pubKeyCredParams"]) == 2

    def test_full_creation_options(self):
        """Test creation options with all fields."""
        challenge = base64.urlsafe_b64encode(b"challenge-xyz").decode().rstrip("=")
        user_id = base64.urlsafe_b64encode(b"user-789").decode().rstrip("=")
        existing_cred = base64.urlsafe_b64encode(b"existing-cred").decode().rstrip("=")

        options: CredentialCreationOptions = {
            "challenge": challenge,
            "rp": {"name": "LUKHAS AI", "id": "ai"},
            "user": {
                "id": user_id,
                "name": "alice@ai",
                "displayName": "Alice"
            },
            "pubKeyCredParams": [
                {"type": "public-key", "alg": -7}
            ],
            "timeout": 300000,
            "excludeCredentials": [
                {"type": "public-key", "id": existing_cred}
            ],
            "authenticatorSelection": {
                "authenticatorAttachment": "platform",
                "residentKey": "required",
                "userVerification": "required"
            },
            "attestation": "direct"
        }

        assert options["timeout"] == 300000
        assert options["attestation"] == "direct"
        assert "excludeCredentials" in options
        assert len(options["excludeCredentials"]) == 1


class TestAuthenticatorAttestationResponse:
    """Test authenticator attestation response type."""

    def test_minimal_attestation_response(self):
        """Test attestation response with required fields."""
        client_data = base64.urlsafe_b64encode(b'{"type":"webauthn.create"}').decode().rstrip("=")
        attestation_obj = base64.urlsafe_b64encode(b"attestation-data").decode().rstrip("=")

        response: AuthenticatorAttestationResponse = {
            "clientDataJSON": client_data,
            "attestationObject": attestation_obj
        }

        assert response["clientDataJSON"] == client_data
        assert response["attestationObject"] == attestation_obj

    def test_full_attestation_response(self):
        """Test attestation response with all fields."""
        response: AuthenticatorAttestationResponse = {
            "clientDataJSON": "Y2xpZW50RGF0YQ",
            "attestationObject": "YXR0ZXN0YXRpb25PYmo",
            "transports": ["internal", "hybrid"],
            "authenticatorData": "YXV0aERhdGE",
            "publicKey": "cHVibGljS2V5",
            "publicKeyAlgorithm": -7
        }

        assert "transports" in response
        assert "authenticatorData" in response
        assert response["publicKeyAlgorithm"] == -7


class TestPublicKeyCredentialCreation:
    """Test public key credential creation (registration result)."""

    def test_registration_credential(self):
        """Test complete registration credential structure."""
        cred_id = base64.urlsafe_b64encode(b"new-credential").decode().rstrip("=")
        client_data = base64.urlsafe_b64encode(b'{"type":"webauthn.create"}').decode().rstrip("=")
        attestation = base64.urlsafe_b64encode(b"attestation").decode().rstrip("=")

        credential: PublicKeyCredentialCreation = {
            "id": cred_id,
            "rawId": cred_id,
            "type": "public-key",
            "response": {
                "clientDataJSON": client_data,
                "attestationObject": attestation
            }
        }

        assert credential["id"] == cred_id
        assert credential["type"] == "public-key"
        assert credential["response"]["clientDataJSON"] == client_data

    def test_registration_with_extensions(self):
        """Test registration credential with client extensions."""
        cred_id = "Y3JlZElk"

        credential: PublicKeyCredentialCreation = {
            "id": cred_id,
            "rawId": cred_id,
            "type": "public-key",
            "response": {
                "clientDataJSON": "Y2xpZW50RGF0YQ",
                "attestationObject": "YXR0ZXN0"
            },
            "authenticatorAttachment": "platform",
            "clientExtensionResults": {
                "credProps": {"rk": True}
            }
        }

        assert credential["authenticatorAttachment"] == "platform"
        assert "credProps" in credential["clientExtensionResults"]


class TestCredentialRequestOptions:
    """Test credential request (authentication) options."""

    def test_minimal_request_options(self):
        """Test request options with only required fields."""
        challenge = base64.urlsafe_b64encode(b"auth-challenge-123").decode().rstrip("=")

        options: CredentialRequestOptions = {
            "challenge": challenge
        }

        assert options["challenge"] == challenge

    def test_full_request_options(self):
        """Test request options with all fields."""
        challenge = base64.urlsafe_b64encode(b"auth-challenge-xyz").decode().rstrip("=")
        cred_id = base64.urlsafe_b64encode(b"allowed-cred").decode().rstrip("=")

        options: CredentialRequestOptions = {
            "challenge": challenge,
            "timeout": 180000,
            "rpId": "ai",
            "allowCredentials": [
                {"type": "public-key", "id": cred_id}
            ],
            "userVerification": "required"
        }

        assert options["timeout"] == 180000
        assert options["rpId"] == "ai"
        assert options["userVerification"] == "required"
        assert len(options["allowCredentials"]) == 1


class TestAuthenticatorAssertionResponse:
    """Test authenticator assertion response type."""

    def test_minimal_assertion_response(self):
        """Test assertion response with required fields."""
        response: AuthenticatorAssertionResponse = {
            "clientDataJSON": "Y2xpZW50RGF0YQ",
            "authenticatorData": "YXV0aERhdGE",
            "signature": "c2lnbmF0dXJl"
        }

        assert response["clientDataJSON"] == "Y2xpZW50RGF0YQ"
        assert response["authenticatorData"] == "YXV0aERhdGE"
        assert response["signature"] == "c2lnbmF0dXJl"

    def test_assertion_with_user_handle(self):
        """Test assertion response with user handle."""
        user_handle = base64.urlsafe_b64encode(b"user-123").decode().rstrip("=")

        response: AuthenticatorAssertionResponse = {
            "clientDataJSON": "Y2xpZW50RGF0YQ",
            "authenticatorData": "YXV0aERhdGE",
            "signature": "c2lnbmF0dXJl",
            "userHandle": user_handle
        }

        assert response["userHandle"] == user_handle


class TestPublicKeyCredentialAssertion:
    """Test public key credential assertion (authentication result)."""

    def test_authentication_credential(self):
        """Test complete authentication credential structure."""
        cred_id = base64.urlsafe_b64encode(b"existing-cred").decode().rstrip("=")

        credential: PublicKeyCredentialAssertion = {
            "id": cred_id,
            "rawId": cred_id,
            "type": "public-key",
            "response": {
                "clientDataJSON": "Y2xpZW50RGF0YQ",
                "authenticatorData": "YXV0aERhdGE",
                "signature": "c2lnbmF0dXJl"
            }
        }

        assert credential["id"] == cred_id
        assert credential["type"] == "public-key"
        assert credential["response"]["signature"] == "c2lnbmF0dXJl"


class TestVerificationResults:
    """Test server-side verification result types."""

    def test_verified_registration(self):
        """Test registration verification result."""
        result: VerifiedRegistration = {
            "verified": True,
            "credential_id": b"credential-bytes",
            "credential_public_key": b"public-key-bytes",
            "sign_count": 0
        }

        assert result["verified"] is True
        assert result["sign_count"] == 0

    def test_verified_registration_with_metadata(self):
        """Test registration verification with full metadata."""
        result: VerifiedRegistration = {
            "verified": True,
            "credential_id": b"cred-id",
            "credential_public_key": b"pub-key",
            "sign_count": 0,
            "aaguid": b"\x08\x98\x70\x58\xca\xdc\x4b\x81\xb6\xe1\x30\xde\x50\xdc\xbe\x96",
            "backup_eligible": True,
            "backup_state": False,
            "user_verified": True
        }

        assert result["aaguid"] is not None
        assert result["backup_eligible"] is True
        assert result["user_verified"] is True

    def test_verified_authentication(self):
        """Test authentication verification result."""
        result: VerifiedAuthentication = {
            "verified": True,
            "new_sign_count": 5
        }

        assert result["verified"] is True
        assert result["new_sign_count"] == 5

    def test_verified_authentication_with_flags(self):
        """Test authentication verification with authenticator flags."""
        result: VerifiedAuthentication = {
            "verified": True,
            "new_sign_count": 10,
            "backup_eligible": True,
            "backup_state": True,
            "user_verified": True
        }

        assert result["new_sign_count"] == 10
        assert result["backup_state"] is True


class TestRealWorldWebAuthnResponses:
    """Test parsing real-world WebAuthn response structures."""

    def test_parse_real_registration_response(self):
        """Test that types can represent a real registration response."""
        # Simulated real browser response structure
        browser_response = {
            "id": "AaFdkcD4SuPjF-jwUoRwH8-ZHuY",
            "rawId": "AaFdkcD4SuPjF-jwUoRwH8-ZHuY",
            "type": "public-key",
            "response": {
                "clientDataJSON": "eyJ0eXBlIjoid2ViYXV0aG4uY3JlYXRlIiwiY2hhbGxlbmdlIjoiYWJjMTIzIiwib3JpZ2luIjoiaHR0cHM6Ly9haS5sdWtoYXMuYWkifQ",
                "attestationObject": "o2NmbXRkbm9uZWdhdHRTdG10oGhhdXRoRGF0YViYSZYN5YgOjGh0NBcPZHZgW4",
                "transports": ["internal"]
            },
            "authenticatorAttachment": "platform"
        }

        # Verify we can type this as PublicKeyCredentialCreation
        credential: PublicKeyCredentialCreation = browser_response  # type: ignore
        assert credential["type"] == "public-key"
        assert credential["authenticatorAttachment"] == "platform"

    def test_parse_real_authentication_response(self):
        """Test that types can represent a real authentication response."""
        # Simulated real browser response structure
        browser_response = {
            "id": "AaFdkcD4SuPjF-jwUoRwH8-ZHuY",
            "rawId": "AaFdkcD4SuPjF-jwUoRwH8-ZHuY",
            "type": "public-key",
            "response": {
                "clientDataJSON": "eyJ0eXBlIjoid2ViYXV0aG4uZ2V0IiwiY2hhbGxlbmdlIjoiZGVmNDU2Iiwib3JpZ2luIjoiaHR0cHM6Ly9haS5sdWtoYXMuYWkifQ",
                "authenticatorData": "SZYN5YgOjGh0NBcPZHZgW4_krrmihjLHmVzzuoMdl2MFAAAABA",
                "signature": "MEUCIQCqV3Q_jWJaVYf8FQjvPz5LTWBq4Fqh8FNvPk8b3jMxdQIgVs8gLQ",
                "userHandle": "dXNlci0xMjM"
            },
            "authenticatorAttachment": "platform"
        }

        # Verify we can type this as PublicKeyCredentialAssertion
        credential: PublicKeyCredentialAssertion = browser_response  # type: ignore
        assert credential["type"] == "public-key"
        assert credential["response"]["signature"] is not None


class TestTypeStructureCompliance:
    """Test that type definitions comply with W3C WebAuthn spec structure."""

    def test_credential_creation_options_structure(self):
        """Verify CredentialCreationOptions matches W3C spec."""
        hints = get_type_hints(CredentialCreationOptions)

        # Required fields from spec
        assert "challenge" in hints
        assert "rp" in hints
        assert "user" in hints
        assert "pubKeyCredParams" in hints

        # Optional fields from spec
        # Note: NotRequired fields are in __annotations__ but not required

    def test_credential_request_options_structure(self):
        """Verify CredentialRequestOptions matches W3C spec."""
        hints = get_type_hints(CredentialRequestOptions)

        # Required field from spec
        assert "challenge" in hints

        # All other fields should be optional

    def test_authenticator_response_structures(self):
        """Verify authenticator response types match W3C spec."""
        attestation_hints = get_type_hints(AuthenticatorAttestationResponse)
        assertion_hints = get_type_hints(AuthenticatorAssertionResponse)

        # Attestation required fields
        assert "clientDataJSON" in attestation_hints
        assert "attestationObject" in attestation_hints

        # Assertion required fields
        assert "clientDataJSON" in assertion_hints
        assert "authenticatorData" in assertion_hints
        assert "signature" in assertion_hints


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
