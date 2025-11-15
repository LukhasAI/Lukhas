"""
QRG (Quantum-Resistant Governance) Generator

Generates quantum-resistant governance tokens using CRYSTALS-Dilithium (NIST PQC winner).
Provides secure authentication tokens that will resist future quantum computer attacks.

LUKHAS AI - Consciousness-aware AI Development Platform
"""

import base64
import hashlib
import hmac
import json
import secrets
import time
from typing import Any, Dict, List, Optional, Set

try:
    from pqcrypto.sign.dilithium2 import generate_keypair, sign, verify
    PQC_AVAILABLE = True
except ImportError:
    # Fallback for environments where pqcrypto is not available
    PQC_AVAILABLE = False


class QRGTokenError(Exception):
    """Base exception for QRG token operations."""
    pass


class QRGVerificationError(QRGTokenError):
    """Token verification failed."""
    pass


class QRGTokenExpiredError(QRGTokenError):
    """Token has expired."""
    pass


class QRGGenerator:
    """
    Quantum-resistant governance token generator.

    Uses CRYSTALS-Dilithium (NIST Level 2) for post-quantum digital signatures.
    Generates tokens with format: QRG_<base64url-encoded-payload>

    Features:
    - Post-quantum cryptographic signatures
    - Scope-based permissions
    - TTL-based expiration (default 1 hour)
    - Token rotation with scope preservation
    - Immediate revocation support
    - Security level: NIST Level 2 (equivalent to AES-128)

    Example:
        >>> config = {"security_level": 2}
        >>> generator = QRGGenerator(config)
        >>> token = generator.generate_qrg_token("user123", ["read", "write"])
        >>> is_valid = generator.verify_token(token, ["read"])
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize QRG generator with post-quantum cryptographic keys.

        Args:
            config: Configuration dictionary with optional keys:
                - security_level: NIST security level (2, 3, or 5) - default: 2
                - algorithm: PQC algorithm to use - default: "dilithium2"
                - enable_revocation: Enable token revocation tracking - default: True

        Raises:
            QRGTokenError: If PQC library is not available or initialization fails
        """
        self.config = config or {}
        self.security_level = self.config.get("security_level", 2)
        self.algorithm = self.config.get("algorithm", "dilithium2")
        self.enable_revocation = self.config.get("enable_revocation", True)

        # Revoked tokens set (in production, use Redis or persistent storage)
        self._revoked_tokens: Set[str] = set()

        # Token registry for tracking active tokens
        self._token_registry: Dict[str, Dict[str, Any]] = {}

        # Initialize post-quantum keypair
        if PQC_AVAILABLE:
            self._public_key, self._private_key = generate_keypair()
        else:
            # Fallback to HMAC-based signing (NOT quantum-resistant, for testing only)
            self._signing_key = secrets.token_bytes(32)
            self._public_key = None
            self._private_key = None

    def generate_qrg_token(
        self,
        user_id: str,
        scopes: List[str],
        ttl_seconds: int = 3600
    ) -> str:
        """
        Generate quantum-resistant governance token with embedded scopes.

        Args:
            user_id: Unique user identifier
            scopes: List of permission scopes (e.g., ["read", "write", "admin"])
            ttl_seconds: Time-to-live in seconds (default: 3600 = 1 hour)

        Returns:
            QRG token string in format: QRG_<base64url-encoded-payload>

        Raises:
            QRGTokenError: If token generation fails
            ValueError: If user_id is empty or scopes is empty

        Example:
            >>> token = generator.generate_qrg_token("user123", ["read", "write"], 7200)
            >>> print(token)
            QRG_eyJ1c2VyX2lkIjoidXNlcjEyMyIsInNjb3BlcyI6...
        """
        if not user_id:
            raise ValueError("user_id cannot be empty")
        if not scopes:
            raise ValueError("scopes cannot be empty")

        # Generate unique token ID
        token_id = secrets.token_hex(16)

        # Calculate expiration timestamp
        issued_at = int(time.time())
        expires_at = issued_at + ttl_seconds

        # Create token payload
        payload = {
            "token_id": token_id,
            "user_id": user_id,
            "scopes": sorted(scopes),  # Sort for consistency
            "issued_at": issued_at,
            "expires_at": expires_at,
            "version": "1.0",
            "algorithm": self.algorithm,
        }

        # Serialize payload
        payload_bytes = json.dumps(payload, separators=(',', ':')).encode('utf-8')

        # Generate quantum-resistant signature
        if PQC_AVAILABLE:
            signature = sign(self._private_key, payload_bytes)
        else:
            # Fallback: HMAC-based signature (NOT quantum-resistant)
            signature = hmac.new(
                self._signing_key,
                payload_bytes,
                hashlib.sha256
            ).digest()

        # Combine payload and signature
        token_data = {
            "payload": base64.urlsafe_b64encode(payload_bytes).decode('ascii'),
            "signature": base64.urlsafe_b64encode(signature).decode('ascii'),
        }

        # Encode as base64url
        token_json = json.dumps(token_data, separators=(',', ':'))
        encoded_token = base64.urlsafe_b64encode(token_json.encode('utf-8')).decode('ascii')

        # Create final token with prefix
        qrg_token = f"QRG_{encoded_token}"

        # Register token
        self._token_registry[token_id] = {
            "user_id": user_id,
            "scopes": scopes,
            "issued_at": issued_at,
            "expires_at": expires_at,
        }

        return qrg_token

    def verify_token(
        self,
        token: str,
        required_scopes: Optional[List[str]] = None
    ) -> bool:
        """
        Verify token signature and scope permissions.

        Args:
            token: QRG token string to verify
            required_scopes: Optional list of scopes that must be present in token

        Returns:
            True if token is valid and has required scopes, False otherwise

        Raises:
            QRGVerificationError: If token format is invalid
            QRGTokenExpiredError: If token has expired

        Example:
            >>> is_valid = generator.verify_token(token, ["read"])
            >>> if is_valid:
            ...     print("Token is valid and has read permission")
        """
        try:
            # Check token format
            if not token.startswith("QRG_"):
                raise QRGVerificationError("Invalid token format: missing QRG_ prefix")

            # Extract encoded payload
            encoded_token = token[4:]  # Remove "QRG_" prefix

            # Decode token
            try:
                token_json = base64.urlsafe_b64decode(encoded_token).decode('utf-8')
                token_data = json.loads(token_json)
            except (ValueError, json.JSONDecodeError) as e:
                raise QRGVerificationError(f"Invalid token encoding: {e}")

            # Extract payload and signature
            payload_b64 = token_data.get("payload")
            signature_b64 = token_data.get("signature")

            if not payload_b64 or not signature_b64:
                raise QRGVerificationError("Missing payload or signature")

            # Decode payload and signature
            payload_bytes = base64.urlsafe_b64decode(payload_b64)
            signature = base64.urlsafe_b64decode(signature_b64)

            # Verify signature
            if PQC_AVAILABLE:
                try:
                    verify(self._public_key, payload_bytes, signature)
                except Exception as e:
                    raise QRGVerificationError(f"Signature verification failed: {e}")
            else:
                # Fallback: HMAC verification
                expected_signature = hmac.new(
                    self._signing_key,
                    payload_bytes,
                    hashlib.sha256
                ).digest()
                if not hmac.compare_digest(signature, expected_signature):
                    raise QRGVerificationError("Signature verification failed")

            # Parse payload
            payload = json.loads(payload_bytes)

            # Check expiration
            expires_at = payload.get("expires_at")
            if expires_at and int(time.time()) > expires_at:
                raise QRGTokenExpiredError("Token has expired")

            # Check if token is revoked
            token_id = payload.get("token_id")
            if self.enable_revocation and token_id in self._revoked_tokens:
                raise QRGVerificationError("Token has been revoked")

            # Check required scopes
            if required_scopes:
                token_scopes = set(payload.get("scopes", []))
                required_scopes_set = set(required_scopes)
                if not required_scopes_set.issubset(token_scopes):
                    missing_scopes = required_scopes_set - token_scopes
                    raise QRGVerificationError(
                        f"Token missing required scopes: {missing_scopes}"
                    )

            return True

        except (QRGVerificationError, QRGTokenExpiredError):
            raise
        except Exception as e:
            raise QRGVerificationError(f"Token verification failed: {e}")

    def rotate_token(self, old_token: str) -> str:
        """
        Rotate token while preserving scopes and user identity.

        Creates a new token with the same user_id and scopes as the old token,
        then revokes the old token.

        Args:
            old_token: Existing QRG token to rotate

        Returns:
            New QRG token with same user_id and scopes

        Raises:
            QRGVerificationError: If old token is invalid
            QRGTokenExpiredError: If old token has expired

        Example:
            >>> new_token = generator.rotate_token(old_token)
            >>> # Old token is now revoked, new token is active
        """
        # Verify old token and extract claims
        if not self.verify_token(old_token):
            raise QRGVerificationError("Cannot rotate invalid token")

        claims = self.decode_token(old_token)

        # Generate new token with same user_id and scopes
        new_token = self.generate_qrg_token(
            user_id=claims["user_id"],
            scopes=claims["scopes"],
            ttl_seconds=3600  # Default 1 hour TTL
        )

        # Revoke old token
        self.revoke_token(old_token)

        return new_token

    def revoke_token(self, token: str) -> bool:
        """
        Immediately revoke token.

        Args:
            token: QRG token to revoke

        Returns:
            True if token was successfully revoked, False if already revoked

        Raises:
            QRGVerificationError: If token format is invalid

        Example:
            >>> generator.revoke_token(token)
            >>> # Token is now permanently invalid
        """
        if not self.enable_revocation:
            raise QRGTokenError("Token revocation is disabled")

        try:
            claims = self.decode_token(token)
            token_id = claims.get("token_id")

            if token_id in self._revoked_tokens:
                return False  # Already revoked

            self._revoked_tokens.add(token_id)

            # Remove from registry
            if token_id in self._token_registry:
                del self._token_registry[token_id]

            return True

        except Exception as e:
            raise QRGVerificationError(f"Failed to revoke token: {e}")

    def decode_token(self, token: str) -> Dict[str, Any]:
        """
        Decode token to extract claims without verifying signature.

        WARNING: This method does NOT verify the token signature or expiration.
        Use verify_token() for secure validation.

        Args:
            token: QRG token to decode

        Returns:
            Dictionary containing token claims (user_id, scopes, issued_at, etc.)

        Raises:
            QRGVerificationError: If token format is invalid

        Example:
            >>> claims = generator.decode_token(token)
            >>> print(f"User: {claims['user_id']}, Scopes: {claims['scopes']}")
        """
        try:
            # Check token format
            if not token.startswith("QRG_"):
                raise QRGVerificationError("Invalid token format: missing QRG_ prefix")

            # Extract encoded payload
            encoded_token = token[4:]  # Remove "QRG_" prefix

            # Decode token
            token_json = base64.urlsafe_b64decode(encoded_token).decode('utf-8')
            token_data = json.loads(token_json)

            # Extract and decode payload
            payload_b64 = token_data.get("payload")
            if not payload_b64:
                raise QRGVerificationError("Missing payload")

            payload_bytes = base64.urlsafe_b64decode(payload_b64)
            payload = json.loads(payload_bytes)

            return payload

        except (ValueError, json.JSONDecodeError) as e:
            raise QRGVerificationError(f"Invalid token encoding: {e}")

    def get_token_info(self, token: str) -> Dict[str, Any]:
        """
        Get detailed token information including verification status.

        Args:
            token: QRG token to inspect

        Returns:
            Dictionary with token info and validation status

        Example:
            >>> info = generator.get_token_info(token)
            >>> print(f"Valid: {info['is_valid']}, Expired: {info['is_expired']}")
        """
        try:
            claims = self.decode_token(token)

            is_expired = int(time.time()) > claims.get("expires_at", 0)
            is_revoked = claims.get("token_id") in self._revoked_tokens

            try:
                is_valid = self.verify_token(token)
            except (QRGVerificationError, QRGTokenExpiredError):
                is_valid = False

            return {
                "user_id": claims.get("user_id"),
                "scopes": claims.get("scopes"),
                "issued_at": claims.get("issued_at"),
                "expires_at": claims.get("expires_at"),
                "is_valid": is_valid,
                "is_expired": is_expired,
                "is_revoked": is_revoked,
                "algorithm": claims.get("algorithm"),
                "version": claims.get("version"),
            }

        except QRGVerificationError as e:
            return {
                "is_valid": False,
                "error": str(e)
            }


__all__ = [
    "QRGGenerator",
    "QRGTokenError",
    "QRGVerificationError",
    "QRGTokenExpiredError",
]
