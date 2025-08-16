# path: qi/glyphs/seal.py
"""
LUKHAS AI GLYPH Cryptographic Seal v0.1

Portable, cryptographically sealed attestations bound to AI artifacts.
Verifiable offline (QR/embedded) and online (proof bundle URL).
"""
from __future__ import annotations
import os, json, time, hashlib, secrets, base64
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any, List

# Crypto dependencies
try:
    import nacl.signing
    import nacl.encoding
    _HAS_NACL = True
except ImportError:
    _HAS_NACL = False

# For production: Dilithium3 support (placeholder)
try:
    # import pqcrypto.sign.dilithium3 as dilithium
    _HAS_DILITHIUM = False  # Not implemented yet
except ImportError:
    _HAS_DILITHIUM = False

@dataclass 
class GlyphSeal:
    """Minimal GLYPH Cryptographic Seal payload (v0.1)"""
    v: str                          # version "0.1"
    content_hash: str               # "sha3-512:<hex>"
    media_type: str                 # "text/plain", "image/png", etc.
    created_at: str                 # ISO 8601 UTC timestamp
    issuer: str                     # "lukhas://org/<tenant-id>"
    model_id: str                   # "lukhas-qiv2.0"
    policy_fingerprint: str         # "sha3-256:<hex>"
    jurisdiction: str               # "eu", "us", "global"
    proof_bundle: str               # URL to expanded proof bundle
    expiry: str                     # ISO 8601 UTC timestamp
    nonce: str                      # base64 random nonce
    prev: Optional[str] = None      # prior seal id for chains/threads
    calib_ref: Optional[Dict[str, float]] = None  # {"temp":1.08,"ece":0.041}

@dataclass
class GlyphSignature:
    """Cryptographic signature over canonical seal"""
    algorithm: str                  # "ed25519" | "dilithium3"
    signature: str                  # base64-encoded signature
    key_id: str                     # key identifier for JWKS lookup
    chain: Optional[List[str]] = None  # additional signatures (device, consent)

def sha3_512(data: bytes) -> str:
    """SHA3-512 hash (hex)"""
    return hashlib.sha3_512(data).hexdigest()

def sha3_256(data: bytes) -> str:
    """SHA3-256 hash (hex)"""
    return hashlib.sha3_256(data).hexdigest()

def canonical(obj: Dict[str, Any]) -> bytes:
    """
    JSON Canonicalization Scheme (JCS) for deterministic signing.
    Sorts keys, no extra whitespace.
    """
    return json.dumps(obj, separators=(",", ":"), sort_keys=True, ensure_ascii=False).encode("utf-8")

def generate_nonce() -> str:
    """Generate cryptographically secure base64 nonce"""
    return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('ascii').rstrip('=')

def current_timestamp() -> str:
    """Current UTC timestamp in ISO 8601 format"""
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def expiry_timestamp(ttl_days: int) -> str:
    """Expiry timestamp TTL days from now"""
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() + ttl_days * 86400))

class GlyphSigner:
    """GLYPH seal creation and signing"""
    
    def __init__(self, signing_key: Optional[bytes] = None, key_id: str = "dev-key-001"):
        """Initialize with signing key (Ed25519 for dev, Dilithium3 for prod)"""
        self.key_id = key_id
        
        if signing_key:
            if _HAS_NACL:
                self.signing_key = nacl.signing.SigningKey(signing_key)
            else:
                raise RuntimeError("PyNaCl required for Ed25519 signing")
        else:
            # Generate ephemeral dev key
            if _HAS_NACL:
                self.signing_key = nacl.signing.SigningKey.generate()
            else:
                raise RuntimeError("PyNaCl required for key generation")
    
    def get_public_key(self) -> str:
        """Get base64-encoded public key"""
        if _HAS_NACL and hasattr(self.signing_key, 'verify_key'):
            return base64.b64encode(bytes(self.signing_key.verify_key)).decode('ascii')
        return ""
    
    def create_seal(
        self, *,
        content_bytes: bytes,
        media_type: str,
        issuer: str,
        model_id: str,
        policy_fingerprint: str,
        jurisdiction: str = "global",
        proof_bundle: str,
        ttl_days: int = 365,
        calib_ref: Optional[Dict[str, float]] = None,
        prev: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a cryptographically sealed GLYPH attestation.
        
        Returns:
            {
                "seal": <GlyphSeal dict>,
                "signature": <GlyphSignature dict>,
                "compact": <base64 encoded seal+sig for QR>
            }
        """
        now = current_timestamp()
        exp = expiry_timestamp(ttl_days)
        
        seal = GlyphSeal(
            v="0.1",
            content_hash=f"sha3-512:{sha3_512(content_bytes)}",
            media_type=media_type,
            created_at=now,
            issuer=issuer,
            model_id=model_id,
            policy_fingerprint=policy_fingerprint,
            jurisdiction=jurisdiction,
            proof_bundle=proof_bundle,
            expiry=exp,
            nonce=generate_nonce(),
            prev=prev,
            calib_ref=calib_ref
        )
        
        # Create canonical payload for signing
        seal_dict = asdict(seal)
        # Remove None values for compact representation
        seal_dict = {k: v for k, v in seal_dict.items() if v is not None}
        
        payload = canonical(seal_dict)
        
        # Sign with Ed25519 (dev) or Dilithium3 (prod)
        signature = self._sign_payload(payload)
        
        # Create compact representation for QR codes
        compact_data = {
            "seal": seal_dict,
            "sig": asdict(signature)
        }
        compact = base64.urlsafe_b64encode(
            json.dumps(compact_data, separators=(",", ":")).encode('utf-8')
        ).decode('ascii').rstrip('=')
        
        return {
            "seal": seal_dict,
            "signature": asdict(signature),
            "compact": compact
        }
    
    def _sign_payload(self, payload: bytes) -> GlyphSignature:
        """Sign canonical payload with configured key"""
        if not _HAS_NACL:
            raise RuntimeError("Cryptographic library not available")
        
        # Sign with Ed25519
        signature_bytes = self.signing_key.sign(payload).signature
        signature_b64 = base64.b64encode(signature_bytes).decode('ascii')
        
        return GlyphSignature(
            algorithm="ed25519",
            signature=signature_b64,
            key_id=self.key_id
        )

def policy_fingerprint_from_files(policy_root: str, overlays: str = None) -> str:
    """
    Generate deterministic policy fingerprint from policy pack files.
    
    Args:
        policy_root: Path to policy pack root (e.g., "qi/safety/policy_packs/global")
        overlays: Optional overlay directory
    
    Returns:
        "sha3-256:<hex>" fingerprint of policy state
    """
    import glob
    
    # Collect all policy files
    files_to_hash = []
    
    # Core policy files
    for pattern in ["policy.yaml", "mappings.yaml", "tests/*.yaml"]:
        files_to_hash.extend(glob.glob(os.path.join(policy_root, pattern)))
    
    # Overlay files if specified
    if overlays and os.path.exists(overlays):
        for pattern in ["*.yaml", "*.json"]:
            files_to_hash.extend(glob.glob(os.path.join(overlays, pattern)))
    
    # Sort for deterministic order
    files_to_hash.sort()
    
    # Hash file contents
    hasher = hashlib.sha3_256()
    for filepath in files_to_hash:
        try:
            with open(filepath, 'rb') as f:
                hasher.update(f.read())
        except (IOError, OSError):
            # Skip unreadable files
            continue
    
    return f"sha3-256:{hasher.hexdigest()}"

# Production HSM/KMS integration placeholder
class HSMSigner(GlyphSigner):
    """Production signer using HSM/KMS for key management"""
    
    def __init__(self, hsm_config: Dict[str, str]):
        """Initialize with HSM configuration"""
        self.hsm_config = hsm_config
        self.key_id = hsm_config.get("key_id", "prod-hsm-001")
        # TODO: Initialize HSM connection
        super().__init__(key_id=self.key_id)
    
    def _sign_payload(self, payload: bytes) -> GlyphSignature:
        """Sign using HSM/KMS (placeholder for production)"""
        # TODO: Implement HSM signing
        # For now, fall back to local signing
        return super()._sign_payload(payload)

# CLI Interface
def main():
    """CLI for creating GLYPH seals"""
    import argparse
    
    parser = argparse.ArgumentParser(description="LUKHAS AI GLYPH Seal Creator")
    parser.add_argument("content_file", help="File to seal")
    parser.add_argument("--issuer", required=True, help="Issuer ID (lukhas://org/<tenant>)")
    parser.add_argument("--model-id", required=True, help="Model identifier")
    parser.add_argument("--policy-root", required=True, help="Policy pack root directory")
    parser.add_argument("--overlays", help="Policy overlay directory")
    parser.add_argument("--jurisdiction", default="global", help="Jurisdiction")
    parser.add_argument("--proof-bundle", required=True, help="Proof bundle URL")
    parser.add_argument("--ttl-days", type=int, default=365, help="Seal validity days")
    parser.add_argument("--output", help="Output file for seal JSON")
    parser.add_argument("--qr", help="Output QR code PNG file")
    
    args = parser.parse_args()
    
    # Read content
    try:
        with open(args.content_file, 'rb') as f:
            content_bytes = f.read()
    except IOError as e:
        print(f"Error reading content file: {e}")
        return 1
    
    # Determine media type
    import mimetypes
    media_type, _ = mimetypes.guess_type(args.content_file)
    if not media_type:
        media_type = "application/octet-stream"
    
    # Generate policy fingerprint
    policy_fp = policy_fingerprint_from_files(args.policy_root, args.overlays)
    
    # Create signer and seal
    signer = GlyphSigner()
    result = signer.create_seal(
        content_bytes=content_bytes,
        media_type=media_type,
        issuer=args.issuer,
        model_id=args.model_id,
        policy_fingerprint=policy_fp,
        jurisdiction=args.jurisdiction,
        proof_bundle=args.proof_bundle,
        ttl_days=args.ttl_days
    )
    
    # Output seal
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"Seal written to {args.output}")
    else:
        print(json.dumps(result, indent=2))
    
    # Generate QR code if requested
    if args.qr:
        try:
            import qrcode
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(result["compact"])
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            img.save(args.qr)
            print(f"QR code saved to {args.qr}")
        except ImportError:
            print("qrcode library not available for QR generation")
    
    return 0

if __name__ == "__main__":
    exit(main())