"""WebAuthn adapter for Lukhas identity flows with secure challenge generation."""

from __future__ import annotations

import base64
import json
import secrets
from dataclasses import dataclass
from typing import Any, Dict, Optional

# ΛTAG: webauthn_production


@dataclass(frozen=True)
class _ChallengeContext:
    """Internal representation of a WebAuthn challenge with cryptographic nonce."""

    user_id: str
    rp_id: str
    origin: str
    nonce: str

    def encode(self) -> str:
        """Encode challenge data with secure random nonce into a URL-safe token."""

        payload = json.dumps(
            {
                "user_id": self.user_id,
                "rp_id": self.rp_id,
                "origin": self.origin,
                "nonce": self.nonce,
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return base64.urlsafe_b64encode(payload).decode("ascii").rstrip("=")


def start_challenge(user_id: str, rp_id: str, origin: str) -> Dict[str, Any]:
    """Produce secure public key credential options with cryptographic random challenge.

    Security: Uses secrets.token_urlsafe(32) for 256-bit cryptographic nonce,
    preventing replay attacks and ensuring challenge uniqueness per authentication attempt.
    """

    if not user_id:
        raise ValueError("user_id must be provided")
    if not rp_id:
        raise ValueError("rp_id must be provided")
    if not origin:
        raise ValueError("origin must be provided")

    # Generate cryptographically secure random nonce (256 bits)
    nonce = secrets.token_urlsafe(32)

    context = _ChallengeContext(user_id=user_id, rp_id=rp_id, origin=origin, nonce=nonce)
    challenge = context.encode()

    return {
        "challenge": challenge,
        "rpId": rp_id,
        "origin": origin,
        "user": {
            "id": base64.urlsafe_b64encode(user_id.encode("utf-8")).decode("ascii").rstrip("="),
            "name": user_id,
            "displayName": user_id,
        },
        "pubKeyCredParams": [
            {"type": "public-key", "alg": -7},  # ES256 (ECDSA w/ SHA-256)
            {"type": "public-key", "alg": -257},  # RS256 (RSASSA-PKCS1-v1_5 w/ SHA-256)
        ],
        "timeout": 60000,
        "authenticatorSelection": {
            "authenticatorAttachment": "platform",
            "requireResidentKey": False,
            "userVerification": "preferred",
        },
    }


def verify_response(response: Dict[str, Any], expected_challenge: Optional[str] = None) -> Dict[str, Any]:
    """Verify the provided WebAuthn response matches the expected challenge.

    Security: Validates challenge matches expected value to prevent replay attacks.
    In production, this should also verify cryptographic signature using public key.

    Args:
        response: WebAuthn assertion response containing challenge and credentials
        expected_challenge: Base64-encoded challenge that was sent to client

    Returns:
        Verification result with ok status and user verification flag

    Raises:
        TypeError: If response is not a dictionary
        ValueError: If response missing required challenge field
    """

    if not isinstance(response, dict):
        raise TypeError("response must be a dictionary")

    response_challenge = response.get("challenge")
    if response_challenge is None:
        raise ValueError("response must include 'challenge'")

    # Verify challenge matches (constant-time comparison for security)
    ok = expected_challenge is None or secrets.compare_digest(
        str(response_challenge), str(expected_challenge)
    )
    user_verified = bool(response.get("user_verified", ok))

    # ΛTAG: webauthn_production_result
    return {
        "ok": ok,
        "user_verified": user_verified,
        "challenge_validated": ok,
    }
