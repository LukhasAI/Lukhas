# T4: code=UP035 | ticket=ruff-cleanup | owner=lukhas-cleanup-team | status=resolved
# reason: Modernizing deprecated typing imports to native Python 3.9+ types for QRG signing
# estimate: 5min | priority: high | dependencies: none

# core/qrg/signing.py
import base64
import json
from datetime import datetime
from hashlib import sha256
from typing import Optional

from core.qrg.model import QRGSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec

# NOTE: Use a KMS/HSM for production. This demo uses in-memory PEM keys.

def canonical_payload_hash(payload: dict) -> str:
    """Stable canonical JSON hash (sha256 hex)."""
    js = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return sha256(js.encode("utf-8")).hexdigest()

def generate_private_key() -> ec.EllipticCurvePrivateKey:
    return ec.generate_private_key(ec.SECP256R1(), default_backend())

def private_key_to_pem(priv: ec.EllipticCurvePrivateKey) -> bytes:
    return priv.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

def public_key_to_pem(pub: ec.EllipticCurvePublicKey) -> bytes:
    return pub.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

def load_private_key_pem(pem_bytes: bytes) -> ec.EllipticCurvePrivateKey:
    return serialization.load_pem_private_key(pem_bytes, password=None, backend=default_backend())

def load_public_key_pem(pem_bytes: bytes) -> ec.EllipticCurvePublicKey:
    return serialization.load_pem_public_key(pem_bytes, backend=default_backend())

def qrg_sign(payload: dict, priv_pem: bytes, consent_hash: Optional[str] = None) -> QRGSignature:
    priv = load_private_key_pem(priv_pem)
    payload_hash = canonical_payload_hash(payload)
    data = payload_hash.encode("utf-8")
    # Using deterministic ECDSA (RFC 6979) semantics provided by cryptography by default.
    signature = priv.sign(data, ec.ECDSA(hashes.SHA256()))
    sig_b64 = base64.b64encode(signature).decode("ascii")
    pub_pem = public_key_to_pem(priv.public_key()).decode("utf-8")
    return QRGSignature(
        algo="ecdsa-sha256",
        pubkey_pem=pub_pem,
        sig_b64=sig_b64,
        ts=datetime.utcnow().isoformat() + "Z",
        payload_hash=payload_hash,
        consent_hash=consent_hash,
    )

def qrg_verify(payload: dict, qrg: QRGSignature) -> bool:
    pub = load_public_key_pem(qrg.pubkey_pem.encode("utf-8"))
    expected_hash = canonical_payload_hash(payload)
    if expected_hash != qrg.payload_hash:
        return False
    signature = base64.b64decode(qrg.sig_b64.encode("ascii"))
    data = qrg.payload_hash.encode("utf-8")
    try:
        pub.verify(signature, data, ec.ECDSA(hashes.SHA256()))
        return True
    except Exception:
        return False
