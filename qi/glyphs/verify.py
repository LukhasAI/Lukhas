# path: qi/glyphs/verify.py
"""
LUKHAS AI GLYPH Verification System

Offline and online verification of cryptographic seals.
"""
from __future__ import annotations
import os, json, time, hashlib, base64
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

# Crypto imports
try:
    import nacl.signing
    import nacl.encoding
    _HAS_NACL = True
except ImportError:
    _HAS_NACL = False

from .seal import sha3_512, sha3_256, canonical

@dataclass
class VerificationResult:
    """Result of GLYPH seal verification"""
    valid: bool
    issuer: str
    model_id: str
    content_hash: str
    created_at: str
    jurisdiction: str
    errors: List[str]
    warnings: List[str]
    online_checked: bool = False
    revocation_status: Optional[str] = None

class GlyphVerifier:
    """GLYPH seal verification engine"""
    
    def __init__(self, jwks: Optional[Dict[str, Any]] = None):
        """Initialize with JWKS for key verification"""
        self.jwks = jwks or {}
        self.revocation_cache = {}
    
    def verify_seal(
        self, 
        content_bytes: bytes, 
        seal_data: Dict[str, Any], 
        signature_data: Dict[str, Any],
        online_check: bool = False
    ) -> VerificationResult:
        """
        Verify a GLYPH seal against content.
        
        Args:
            content_bytes: The original content that was sealed
            seal_data: The seal payload (from JSON)
            signature_data: The signature data
            online_check: Whether to perform online revocation/bundle checks
        
        Returns:
            VerificationResult with validation status
        """
        errors = []
        warnings = []
        
        try:
            # 1. Hash verification
            content_hash_error = self._verify_content_hash(content_bytes, seal_data)
            if content_hash_error:
                errors.append(content_hash_error)
            
            # 2. Signature verification
            sig_error = self._verify_signature(seal_data, signature_data)
            if sig_error:
                errors.append(sig_error)
            
            # 3. Temporal validity
            temporal_error = self._verify_temporal(seal_data)
            if temporal_error:
                errors.append(temporal_error)
            
            # 4. Format validation
            format_errors = self._verify_format(seal_data)
            errors.extend(format_errors)
            
            # 5. Online checks (optional)
            online_status = None
            if online_check:
                online_status, online_errors, online_warnings = self._verify_online(seal_data, signature_data)
                errors.extend(online_errors)
                warnings.extend(online_warnings)
            
            return VerificationResult(
                valid=len(errors) == 0,
                issuer=seal_data.get("issuer", ""),
                model_id=seal_data.get("model_id", ""),
                content_hash=seal_data.get("content_hash", ""),
                created_at=seal_data.get("created_at", ""),
                jurisdiction=seal_data.get("jurisdiction", ""),
                errors=errors,
                warnings=warnings,
                online_checked=online_check,
                revocation_status=online_status
            )
            
        except Exception as e:
            return VerificationResult(
                valid=False,
                issuer="",
                model_id="",
                content_hash="",
                created_at="",
                jurisdiction="",
                errors=[f"Verification failed: {str(e)}"],
                warnings=[],
                online_checked=online_check
            )
    
    def _verify_content_hash(self, content_bytes: bytes, seal_data: Dict[str, Any]) -> Optional[str]:
        """Verify content hash matches"""
        try:
            expected_hash = seal_data.get("content_hash", "")
            if not expected_hash.startswith("sha3-512:"):
                return "Invalid content hash format"
            
            expected_hex = expected_hash.split(":", 1)[1]
            actual_hex = sha3_512(content_bytes)
            
            if actual_hex != expected_hex:
                return "Content hash mismatch"
            
            return None
        except Exception as e:
            return f"Hash verification error: {str(e)}"
    
    def _verify_signature(self, seal_data: Dict[str, Any], signature_data: Dict[str, Any]) -> Optional[str]:
        """Verify cryptographic signature"""
        try:
            algorithm = signature_data.get("algorithm")
            signature_b64 = signature_data.get("signature")
            key_id = signature_data.get("key_id")
            
            if not all([algorithm, signature_b64, key_id]):
                return "Missing signature components"
            
            # Get canonical payload
            payload = canonical(seal_data)
            
            if algorithm == "ed25519":
                return self._verify_ed25519(payload, signature_b64, key_id)
            elif algorithm == "dilithium3":
                return self._verify_dilithium3(payload, signature_b64, key_id)
            else:
                return f"Unsupported signature algorithm: {algorithm}"
                
        except Exception as e:
            return f"Signature verification error: {str(e)}"
    
    def _verify_ed25519(self, payload: bytes, signature_b64: str, key_id: str) -> Optional[str]:
        """Verify Ed25519 signature"""
        if not _HAS_NACL:
            return "PyNaCl not available for Ed25519 verification"
        
        try:
            # Get public key from JWKS
            public_key_b64 = self._get_public_key(key_id)
            if not public_key_b64:
                return f"Public key not found for key_id: {key_id}"
            
            # Decode components
            signature_bytes = base64.b64decode(signature_b64)
            public_key_bytes = base64.b64decode(public_key_b64)
            
            # Verify signature
            verify_key = nacl.signing.VerifyKey(public_key_bytes)
            verify_key.verify(payload, signature_bytes)
            
            return None  # Success
            
        except nacl.exceptions.BadSignatureError:
            return "Invalid Ed25519 signature"
        except Exception as e:
            return f"Ed25519 verification error: {str(e)}"
    
    def _verify_dilithium3(self, payload: bytes, signature_b64: str, key_id: str) -> Optional[str]:
        """Verify Dilithium3 signature (placeholder for production)"""
        # TODO: Implement Dilithium3 verification
        return "Dilithium3 verification not implemented"
    
    def _verify_temporal(self, seal_data: Dict[str, Any]) -> Optional[str]:
        """Verify temporal validity (expiry, etc.)"""
        try:
            expiry_str = seal_data.get("expiry")
            if not expiry_str:
                return "Missing expiry timestamp"
            
            # Parse ISO 8601 timestamp
            import datetime
            expiry = datetime.datetime.fromisoformat(expiry_str.replace('Z', '+00:00'))
            now = datetime.datetime.now(datetime.timezone.utc)
            
            if now > expiry:
                return f"Seal expired at {expiry_str}"
            
            return None
            
        except Exception as e:
            return f"Temporal verification error: {str(e)}"
    
    def _verify_format(self, seal_data: Dict[str, Any]) -> List[str]:
        """Verify seal format and required fields"""
        errors = []
        
        required_fields = [
            "v", "content_hash", "media_type", "created_at", "issuer",
            "model_id", "policy_fingerprint", "jurisdiction", "proof_bundle",
            "expiry", "nonce"
        ]
        
        for field in required_fields:
            if field not in seal_data:
                errors.append(f"Missing required field: {field}")
        
        # Version check
        if seal_data.get("v") != "0.1":
            errors.append(f"Unsupported seal version: {seal_data.get('v')}")
        
        # Issuer format
        issuer = seal_data.get("issuer", "")
        if not issuer.startswith("lukhas://org/"):
            errors.append("Invalid issuer format (must be lukhas://org/<tenant>)")
        
        return errors
    
    def _verify_online(self, seal_data: Dict[str, Any], signature_data: Dict[str, Any]) -> tuple[Optional[str], List[str], List[str]]:
        """Perform online verification checks"""
        errors = []
        warnings = []
        revocation_status = None
        
        try:
            # Check revocation status
            key_id = signature_data.get("key_id")
            if key_id:
                revocation_status = self._check_revocation(key_id)
                if revocation_status == "revoked":
                    errors.append(f"Signing key {key_id} has been revoked")
            
            # Verify proof bundle (if accessible)
            proof_bundle = seal_data.get("proof_bundle")
            if proof_bundle:
                bundle_error = self._verify_proof_bundle(proof_bundle)
                if bundle_error:
                    warnings.append(f"Proof bundle verification: {bundle_error}")
            
        except Exception as e:
            warnings.append(f"Online verification error: {str(e)}")
        
        return revocation_status, errors, warnings
    
    def _get_public_key(self, key_id: str) -> Optional[str]:
        """Get public key from JWKS or cache"""
        # For development, use a hardcoded key
        if key_id == "dev-key-001":
            # This would normally come from JWKS endpoint
            return self.jwks.get(key_id)
        
        # TODO: Fetch from JWKS endpoint in production
        return self.jwks.get(key_id)
    
    def _check_revocation(self, key_id: str) -> Optional[str]:
        """Check if key is revoked"""
        # TODO: Check Certificate Revocation List (CRL)
        # For now, return not revoked
        return "valid"
    
    def _verify_proof_bundle(self, proof_bundle_url: str) -> Optional[str]:
        """Verify proof bundle contents"""
        # TODO: Fetch and validate proof bundle
        # Should contain expanded receipts, policy snapshots, etc.
        return None

def verify_compact_seal(compact_seal: str, content_bytes: bytes, jwks: Dict[str, Any] = None) -> VerificationResult:
    """
    Verify a compact GLYPH seal (from QR code or embedded data).
    
    Args:
        compact_seal: Base64-encoded compact seal
        content_bytes: Original content that was sealed
        jwks: JSON Web Key Set for signature verification
    
    Returns:
        VerificationResult
    """
    try:
        # Decode compact seal
        padded = compact_seal + '=' * (4 - len(compact_seal) % 4)
        decoded = base64.urlsafe_b64decode(padded)
        seal_package = json.loads(decoded.decode('utf-8'))
        
        seal_data = seal_package.get("seal", {})
        signature_data = seal_package.get("sig", {})
        
        # Verify
        verifier = GlyphVerifier(jwks)
        return verifier.verify_seal(content_bytes, seal_data, signature_data)
        
    except Exception as e:
        return VerificationResult(
            valid=False,
            issuer="",
            model_id="",
            content_hash="",
            created_at="",
            jurisdiction="",
            errors=[f"Compact seal decode error: {str(e)}"],
            warnings=[]
        )

# CLI Interface
def main():
    """CLI for verifying GLYPH seals"""
    import argparse
    
    parser = argparse.ArgumentParser(description="LUKHAS AI GLYPH Seal Verifier")
    parser.add_argument("content_file", help="Original content file")
    parser.add_argument("seal_file", help="Seal JSON file")
    parser.add_argument("--jwks", help="JWKS file for key verification")
    parser.add_argument("--online", action="store_true", help="Perform online verification")
    parser.add_argument("--compact", help="Verify compact seal (base64) instead of JSON")
    
    args = parser.parse_args()
    
    # Read content
    try:
        with open(args.content_file, 'rb') as f:
            content_bytes = f.read()
    except IOError as e:
        print(f"Error reading content file: {e}")
        return 1
    
    # Load JWKS if provided
    jwks = {}
    if args.jwks:
        try:
            with open(args.jwks, 'r') as f:
                jwks = json.load(f)
        except IOError as e:
            print(f"Error reading JWKS file: {e}")
            return 1
    
    # Verify seal
    if args.compact:
        with open(args.seal_file, 'r') as f:
            compact_seal = f.read().strip()
        result = verify_compact_seal(compact_seal, content_bytes, jwks)
    else:
        # Load seal JSON
        try:
            with open(args.seal_file, 'r') as f:
                seal_package = json.load(f)
        except IOError as e:
            print(f"Error reading seal file: {e}")
            return 1
        
        seal_data = seal_package.get("seal", {})
        signature_data = seal_package.get("signature", {})
        
        verifier = GlyphVerifier(jwks)
        result = verifier.verify_seal(content_bytes, seal_data, signature_data, args.online)
    
    # Output result
    print(f"Verification: {'✅ VALID' if result.valid else '❌ INVALID'}")
    print(f"Issuer: {result.issuer}")
    print(f"Model: {result.model_id}")
    print(f"Created: {result.created_at}")
    print(f"Jurisdiction: {result.jurisdiction}")
    
    if result.errors:
        print("\nErrors:")
        for error in result.errors:
            print(f"  ❌ {error}")
    
    if result.warnings:
        print("\nWarnings:")
        for warning in result.warnings:
            print(f"  ⚠️  {warning}")
    
    if result.online_checked:
        print(f"\nRevocation Status: {result.revocation_status}")
    
    return 0 if result.valid else 1

if __name__ == "__main__":
    exit(main())