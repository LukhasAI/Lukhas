#!/usr/bin/env python3
"""
WebAuthn Assertion Verification System

Implements cryptographic verification of WebAuthn authentication assertions
with support for ES256 (ECDSA P-256) and RS256 (RSA) signature algorithms.
Provides phishing-resistant authentication with replay attack prevention.

Constellation Framework: Identity ⚛️ pillar
Task: #599 - WebAuthn assertion verification implementation

Security Properties:
- Cryptographic signature verification (ES256, RS256)
- Constant-time challenge comparison (timing attack prevention)
- Sign counter validation (replay attack prevention)
- Origin validation (phishing prevention)
- Type validation (ceremony type verification)

IMPORTANT: This module handles security-critical operations. Any modifications
must be reviewed for cryptographic correctness and timing safety.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import struct
from typing import Any, Dict

from cryptography.exceptions import InvalidSignature as CryptoInvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, padding, rsa
from typing_extensions import NotRequired, TypedDict

from lukhas.identity.webauthn_credential import WebAuthnCredential

# Verification result types

class VerificationResult(TypedDict):
    """Result of assertion verification with detailed outcome.

    This type extends the VerifiedAuthentication type from webauthn_types.py
    with additional fields for error handling and user identification.
    """
    success: bool
    user_id: str
    credential_id: str
    new_sign_count: int
    error: NotRequired[str]
    user_verified: NotRequired[bool]
    backup_eligible: NotRequired[bool]
    backup_state: NotRequired[bool]


# Custom exceptions for verification failures

class VerificationError(Exception):
    """Base class for verification errors."""
    pass


class InvalidSignatureError(VerificationError):
    """Signature verification failed."""
    pass


class InvalidChallengeError(VerificationError):
    """Challenge doesn't match expected value."""
    pass


class ReplayAttackError(VerificationError):
    """Sign counter didn't increment (possible replay attack)."""
    pass


class InvalidAssertionError(VerificationError):
    """Malformed or invalid assertion data."""
    pass


class CredentialNotFoundError(VerificationError):
    """Credential doesn't exist in storage."""
    pass


# Helper functions

def _base64url_decode(data: str) -> bytes:
    """Decode base64url-encoded string to bytes.

    Args:
        data: Base64url-encoded string (without padding)

    Returns:
        Decoded bytes

    Raises:
        InvalidAssertionError: If decoding fails
    """
    try:
        # Add padding if needed
        padding_needed = (4 - len(data) % 4) % 4
        padded = data + ('=' * padding_needed)
        return base64.urlsafe_b64decode(padded)
    except Exception as e:
        raise InvalidAssertionError(f"Failed to decode base64url data: {e}")


def _constant_time_compare(a: bytes, b: bytes) -> bool:
    """Compare two byte strings in constant time.

    Prevents timing attacks by ensuring comparison takes the same time
    regardless of where the first difference occurs.

    Args:
        a: First byte string
        b: Second byte string

    Returns:
        True if equal, False otherwise
    """
    return hmac.compare_digest(a, b)


def _parse_authenticator_data(auth_data: bytes) -> Dict[str, Any]:
    """Parse authenticator data structure.

    Authenticator data structure (minimum 37 bytes):
    - rpIdHash (32 bytes): SHA-256 hash of RP ID
    - flags (1 byte): Bit flags
    - signCount (4 bytes): Big-endian unsigned 32-bit integer
    - attestedCredentialData (optional): Only present during registration
    - extensions (optional): CBOR-encoded extensions

    Args:
        auth_data: Raw authenticator data bytes

    Returns:
        Dictionary with parsed fields: rp_id_hash, flags, sign_count,
        user_present, user_verified, backup_eligible, backup_state

    Raises:
        InvalidAssertionError: If data is malformed
    """
    if len(auth_data) < 37:
        raise InvalidAssertionError(
            f"Authenticator data too short: {len(auth_data)} bytes (minimum 37)"
        )

    # Extract fields
    rp_id_hash = auth_data[0:32]
    flags_byte = auth_data[32]
    sign_count = struct.unpack('>I', auth_data[33:37])[0]

    # Parse flags (bit 0 = UP, bit 2 = UV, bit 3 = BE, bit 4 = BS)
    user_present = bool(flags_byte & 0x01)
    user_verified = bool(flags_byte & 0x04)
    backup_eligible = bool(flags_byte & 0x08)
    backup_state = bool(flags_byte & 0x10)

    return {
        'rp_id_hash': rp_id_hash,
        'flags': flags_byte,
        'sign_count': sign_count,
        'user_present': user_present,
        'user_verified': user_verified,
        'backup_eligible': backup_eligible,
        'backup_state': backup_state,
    }


def _parse_client_data_json(client_data_json: bytes) -> Dict[str, Any]:
    """Parse and validate client data JSON.

    Client data JSON contains:
    - type: "webauthn.get" for authentication
    - challenge: Base64url-encoded challenge
    - origin: Origin of the request
    - crossOrigin (optional): Whether cross-origin

    Args:
        client_data_json: UTF-8 encoded client data JSON

    Returns:
        Dictionary with parsed fields: type, challenge, origin

    Raises:
        InvalidAssertionError: If JSON is malformed or missing required fields
    """
    import json

    try:
        data = json.loads(client_data_json.decode('utf-8'))
    except Exception as e:
        raise InvalidAssertionError(f"Failed to parse clientDataJSON: {e}")

    # Validate required fields
    if 'type' not in data:
        raise InvalidAssertionError("Missing 'type' field in clientDataJSON")
    if 'challenge' not in data:
        raise InvalidAssertionError("Missing 'challenge' field in clientDataJSON")
    if 'origin' not in data:
        raise InvalidAssertionError("Missing 'origin' field in clientDataJSON")

    return {
        'type': data['type'],
        'challenge': data['challenge'],
        'origin': data['origin'],
    }


def _verify_signature_es256(
    public_key_bytes: bytes,
    signed_data: bytes,
    signature: bytes
) -> None:
    """Verify ECDSA signature using ES256 (P-256 curve with SHA-256).

    Args:
        public_key_bytes: Base64url-decoded public key bytes
        signed_data: Data that was signed (authenticatorData + clientDataHash)
        signature: Base64url-decoded signature bytes

    Raises:
        InvalidSignatureError: If signature verification fails
    """
    try:
        # Parse public key (expecting raw COSE format or DER)
        # For WebAuthn, public key is typically in COSE format
        # We'll handle both formats

        try:
            # Try parsing as DER first
            public_key = serialization.load_der_public_key(public_key_bytes)
        except Exception:
            # If DER fails, try parsing as COSE key (common in WebAuthn)
            # COSE EC2 key format for P-256:
            # - First byte might be 0x04 (uncompressed point indicator)
            # - Followed by X coordinate (32 bytes) and Y coordinate (32 bytes)
            if len(public_key_bytes) == 65 and public_key_bytes[0] == 0x04:
                # Uncompressed EC point format
                x = int.from_bytes(public_key_bytes[1:33], 'big')
                y = int.from_bytes(public_key_bytes[33:65], 'big')
                public_key = ec.EllipticCurvePublicNumbers(
                    x=x,
                    y=y,
                    curve=ec.SECP256R1()
                ).public_key()
            else:
                raise InvalidSignatureError("Unsupported public key format")

        # Verify signature
        if not isinstance(public_key, ec.EllipticCurvePublicKey):
            raise InvalidSignatureError("Public key is not an EC key")

        public_key.verify(
            signature,
            signed_data,
            ec.ECDSA(hashes.SHA256())
        )
    except CryptoInvalidSignature:
        raise InvalidSignatureError("ES256 signature verification failed")
    except Exception as e:
        raise InvalidSignatureError(f"ES256 verification error: {e}")


def _verify_signature_rs256(
    public_key_bytes: bytes,
    signed_data: bytes,
    signature: bytes
) -> None:
    """Verify RSA signature using RS256 (RSA with SHA-256).

    Args:
        public_key_bytes: Base64url-decoded public key bytes (DER format)
        signed_data: Data that was signed (authenticatorData + clientDataHash)
        signature: Base64url-decoded signature bytes

    Raises:
        InvalidSignatureError: If signature verification fails
    """
    try:
        # Parse public key (DER format)
        public_key = serialization.load_der_public_key(public_key_bytes)

        if not isinstance(public_key, rsa.RSAPublicKey):
            raise InvalidSignatureError("Public key is not an RSA key")

        # Verify signature using PKCS#1 v1.5 padding
        public_key.verify(
            signature,
            signed_data,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
    except CryptoInvalidSignature:
        raise InvalidSignatureError("RS256 signature verification failed")
    except Exception as e:
        raise InvalidSignatureError(f"RS256 verification error: {e}")


# Main verification function

def verify_assertion(
    assertion: Dict[str, Any],
    credential: WebAuthnCredential,
    expected_challenge: str,
    expected_origin: str,
    expected_rp_id: str
) -> VerificationResult:
    """Verify a WebAuthn authentication assertion.

    Performs complete cryptographic verification of a WebAuthn assertion:
    1. Validates assertion structure and decodes fields
    2. Verifies challenge matches expected value (constant-time)
    3. Verifies origin and type in clientDataJSON
    4. Reconstructs signed data (authenticatorData + clientDataHash)
    5. Verifies signature using stored public key
    6. Validates sign counter incremented (prevents replay attacks)

    Args:
        assertion: WebAuthn assertion object with fields:
            - response.clientDataJSON: Base64url-encoded client data
            - response.authenticatorData: Base64url-encoded authenticator data
            - response.signature: Base64url-encoded signature
            - id or rawId: Credential ID (should match credential.credential_id)
        credential: Stored credential from WebAuthnCredentialStore
        expected_challenge: Expected challenge (base64url-encoded)
        expected_origin: Expected origin (e.g., "https://example.com")
        expected_rp_id: Expected Relying Party ID (e.g., "example.com")

    Returns:
        VerificationResult with success=True and user_id, credential_id,
        new_sign_count on success. On failure, success=False with error message.

    Raises:
        InvalidAssertionError: If assertion structure is invalid
        InvalidChallengeError: If challenge doesn't match
        InvalidSignatureError: If signature verification fails
        ReplayAttackError: If sign counter didn't increment

    Example:
        ```python
        result = verify_assertion(
            assertion={
                "id": "credential_id",
                "response": {
                    "clientDataJSON": "eyJ0eXBlIjoid2ViYXV0aG4uZ2V0...",
                    "authenticatorData": "SZYN5YgOjGh0NBcPZHZgW4...",
                    "signature": "MEUCIQD...",
                }
            },
            credential=stored_credential,
            expected_challenge="random_challenge_base64url",
            expected_origin="https://example.com",
            expected_rp_id="example.com"
        )

        if result["success"]:
            # Update credential counter in storage
            store.update_credential(
                result["credential_id"],
                {"counter": result["new_sign_count"]}
            )
        ```
    """
    try:
        # Step 1: Extract and validate assertion structure
        if 'response' not in assertion:
            raise InvalidAssertionError("Missing 'response' field in assertion")

        response = assertion['response']
        required_fields = ['clientDataJSON', 'authenticatorData', 'signature']
        for field in required_fields:
            if field not in response:
                raise InvalidAssertionError(f"Missing '{field}' in assertion response")

        # Decode base64url fields
        client_data_json_bytes = _base64url_decode(response['clientDataJSON'])
        authenticator_data_bytes = _base64url_decode(response['authenticatorData'])
        signature_bytes = _base64url_decode(response['signature'])

        # Step 2: Parse and validate clientDataJSON
        client_data = _parse_client_data_json(client_data_json_bytes)

        # Verify type is "webauthn.get"
        if client_data['type'] != 'webauthn.get':
            raise InvalidAssertionError(
                f"Invalid type: {client_data['type']} (expected 'webauthn.get')"
            )

        # Verify origin
        if client_data['origin'] != expected_origin:
            raise InvalidAssertionError(
                f"Origin mismatch: {client_data['origin']} != {expected_origin}"
            )

        # Step 3: Verify challenge (constant-time comparison)
        received_challenge = client_data['challenge']
        if not _constant_time_compare(
            received_challenge.encode('utf-8'),
            expected_challenge.encode('utf-8')
        ):
            raise InvalidChallengeError(
                "Challenge verification failed (constant-time comparison)"
            )

        # Step 4: Parse authenticator data
        auth_data = _parse_authenticator_data(authenticator_data_bytes)

        # Verify RP ID hash
        expected_rp_id_hash = hashlib.sha256(expected_rp_id.encode('utf-8')).digest()
        if not _constant_time_compare(auth_data['rp_id_hash'], expected_rp_id_hash):
            raise InvalidAssertionError("RP ID hash mismatch")

        # Verify user presence
        if not auth_data['user_present']:
            raise InvalidAssertionError("User presence flag not set")

        # Step 5: Validate sign counter (replay attack prevention)
        new_sign_count = auth_data['sign_count']
        stored_counter = credential['counter']

        # Counter MUST increment (strict inequality prevents replay attacks)
        # Note: Counter of 0 is allowed on first authentication if credential
        # was registered with counter 0
        if stored_counter > 0 and new_sign_count <= stored_counter:
            raise ReplayAttackError(
                f"Sign counter did not increment: {new_sign_count} <= {stored_counter} "
                f"(possible cloned authenticator or replay attack)"
            )

        # Step 6: Reconstruct signed data
        # Signed data = authenticatorData + SHA-256(clientDataJSON)
        client_data_hash = hashlib.sha256(client_data_json_bytes).digest()
        signed_data = authenticator_data_bytes + client_data_hash

        # Step 7: Verify signature
        public_key_bytes = _base64url_decode(credential['public_key'])

        # Try ES256 first (most common), then RS256 as fallback
        signature_verified = False
        last_error = None

        try:
            _verify_signature_es256(public_key_bytes, signed_data, signature_bytes)
            signature_verified = True
        except InvalidSignatureError as e:
            last_error = e
            # Try RS256 as fallback
            try:
                _verify_signature_rs256(public_key_bytes, signed_data, signature_bytes)
                signature_verified = True
                last_error = None
            except InvalidSignatureError as e2:
                last_error = e2

        if not signature_verified:
            raise InvalidSignatureError(
                f"Signature verification failed for both ES256 and RS256: {last_error}"
            )

        # Step 8: Build success result
        result: VerificationResult = {
            'success': True,
            'user_id': credential['user_id'],
            'credential_id': credential['credential_id'],
            'new_sign_count': new_sign_count,
        }

        # Add optional flags
        if auth_data['user_verified']:
            result['user_verified'] = True
        if auth_data['backup_eligible']:
            result['backup_eligible'] = True
        if auth_data['backup_state']:
            result['backup_state'] = True

        return result

    except (
        InvalidAssertionError,
        InvalidChallengeError,
        InvalidSignatureError,
        ReplayAttackError
    ) as e:
        # Return failure result with error message
        # Note: credential info included to allow caller to update metadata
        return {
            'success': False,
            'user_id': credential.get('user_id', ''),
            'credential_id': credential.get('credential_id', ''),
            'new_sign_count': credential.get('counter', 0),
            'error': str(e),
        }
    except Exception as e:
        # Unexpected error - wrap in InvalidAssertionError
        return {
            'success': False,
            'user_id': credential.get('user_id', ''),
            'credential_id': credential.get('credential_id', ''),
            'new_sign_count': credential.get('counter', 0),
            'error': f"Unexpected verification error: {e}",
        }


__all__ = [
    # Main verification function
    'verify_assertion',

    # Result types
    'VerificationResult',

    # Exceptions
    'VerificationError',
    'InvalidSignatureError',
    'InvalidChallengeError',
    'ReplayAttackError',
    'InvalidAssertionError',
    'CredentialNotFoundError',
]
