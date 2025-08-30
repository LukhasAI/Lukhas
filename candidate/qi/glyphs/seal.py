# path: qi/glyphs/seal.py
"""
LUKHAS GLYPH Seal Creation

Cryptographically sealed provenance with canonical JSON and COSE signatures.
"""

from __future__ import annotations

import base64
import hashlib
import json
import time
import uuid
from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class GlyphSeal:
    """GLYPH seal data structure."""

    v: str
    content_hash: str
    media_type: str
    created_at: str
    issuer: str
    model_id: str
    policy_fingerprint: str
    jurisdiction: str
    proof_bundle: str
    expiry: str
    nonce: str
    prev: str | None = None
    calib_ref: dict[str, float] | None = None


def sha3_512(data: bytes) -> str:
    """Compute SHA3-512 hash."""
    return hashlib.sha3_512(data).hexdigest()


def sha3_256(data: bytes) -> str:
    """Compute SHA3-256 hash."""
    return hashlib.sha3_256(data).hexdigest()


def canonicalize(obj: dict[str, Any]) -> bytes:
    """Canonical JSON serialization (deterministic)."""
    # Remove None values
    cleaned = {k: v for k, v in obj.items() if v is not None}
    # Deterministic JSON with sorted keys
    return json.dumps(cleaned, separators=(",", ":"), sort_keys=True).encode("utf-8")


def generate_nonce() -> str:
    """Generate cryptographic nonce."""
    return base64.urlsafe_b64encode(uuid.uuid4().bytes).decode("ascii").rstrip("=")


def make_seal(
    *,
    content_bytes: bytes,
    media_type: str,
    issuer: str,
    model_id: str,
    policy_bytes: bytes,
    jurisdiction: str,
    proof_bundle: str,
    ttl_days: int = 365,
    calib_ref: dict[str, float] | None = None,
    prev: str | None = None,
) -> dict[str, Any]:
    """
    Create a GLYPH seal for content.

    Args:
        content_bytes: The content to seal
        media_type: MIME type of content
        issuer: Issuer identifier (lukhas://org/...)
        model_id: Model that generated the content
        policy_bytes: Policy configuration bytes
        jurisdiction: Jurisdiction code
        proof_bundle: URL to proof bundle
        ttl_days: Time to live in days
        calib_ref: Optional calibration reference
        prev: Previous seal hash for chaining

    Returns:
        Dict with 'seal' and 'sig' keys
    """
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    exp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() + ttl_days * 86400))

    seal = GlyphSeal(
        v="0.1",
        content_hash=f"sha3-512:{sha3_512(content_bytes)}",
        media_type=media_type,
        created_at=now,
        issuer=issuer,
        model_id=model_id,
        policy_fingerprint=f"sha3-256:{sha3_256(policy_bytes)}",
        jurisdiction=jurisdiction,
        proof_bundle=proof_bundle,
        expiry=exp,
        nonce=generate_nonce(),
        prev=prev,
        calib_ref=calib_ref,
    )

    # Canonical payload for signing
    seal_dict = asdict(seal)
    payload = canonicalize(seal_dict)

    # Sign with PQC
    from qi.crypto.pqc_signer import sign_dilithium

    sig_info = sign_dilithium(payload)

    # Convert signature to COSE format
    cose_sig = {
        "protected": base64.urlsafe_b64encode(
            json.dumps(
                {"alg": sig_info["alg"], "kid": sig_info.get("pubkey_id", "default")}
            ).encode()
        )
        .decode()
        .rstrip("="),
        "signature": sig_info["sig"],
    }

    return {"seal": json.loads(payload.decode()), "sig": cose_sig}


def verify_seal(seal_bytes: bytes, sig: dict[str, Any], content_bytes: bytes | None = None) -> bool:
    """
    Verify a GLYPH seal.

    Args:
        seal_bytes: Canonical JSON bytes of seal
        sig: COSE signature structure
        content_bytes: Optional content to verify hash against

    Returns:
        True if valid, False otherwise
    """
    try:
        seal = json.loads(seal_bytes.decode())

        # Verify content hash if provided
        if content_bytes:
            expected_hash = f"sha3-512:{sha3_512(content_bytes)}"
            if seal.get("content_hash") != expected_hash:
                return False

        # Verify signature
        from qi.crypto.pqc_signer import verify_signature

        # Decode COSE protected header
        protected = json.loads(
            base64.urlsafe_b64decode(sig["protected"] + "=" * (4 - len(sig["protected"]) % 4))
        )

        sig_info = {
            "alg": protected["alg"],
            "sig": sig["signature"],
            "content_hash": sha3_512(seal_bytes),
            "pubkey_id": protected.get("kid"),
        }

        return verify_signature(seal_bytes, sig_info)

    except Exception:
        return False
