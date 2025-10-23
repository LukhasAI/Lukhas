"""Deterministic WebAuthn adapter stub for Lukhas identity flows."""

from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from typing import Any, Dict, Optional

# ΛTAG: webauthn_stub


@dataclass(frozen=True)
class _ChallengeContext:
    """Internal representation of a deterministic challenge."""

    user_id: str
    rp_id: str
    origin: str

    def encode(self) -> str:
        """Encode challenge data into a URL-safe token."""

        payload = json.dumps(
            {
                "user_id": self.user_id,
                "rp_id": self.rp_id,
                "origin": self.origin,
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return base64.urlsafe_b64encode(payload).decode("ascii").rstrip("=")


def start_challenge(user_id: str, rp_id: str, origin: str) -> Dict[str, Any]:
    """Produce deterministic public key credential options."""

    if not user_id:
        raise ValueError("user_id must be provided")
    if not rp_id:
        raise ValueError("rp_id must be provided")
    if not origin:
        raise ValueError("origin must be provided")

    context = _ChallengeContext(user_id=user_id, rp_id=rp_id, origin=origin)
    challenge = context.encode()

    # TODO: replace deterministic encoding with secure random challenge in production
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
            {"type": "public-key", "alg": -7},
        ],
        "timeout": 60000,
    }


def verify_response(response: Dict[str, Any], expected_challenge: Optional[str] = None) -> Dict[str, Any]:
    """Verify the provided response matches the deterministic challenge."""

    if not isinstance(response, dict):
        raise TypeError("response must be a dictionary")

    response_challenge = response.get("challenge")
    if response_challenge is None:
        raise ValueError("response must include 'challenge'")

    ok = expected_challenge is None or response_challenge == expected_challenge
    user_verified = bool(response.get("user_verified", ok))

    # ΛTAG: webauthn_stub_result
    return {
        "ok": ok,
        "user_verified": user_verified,
    }
