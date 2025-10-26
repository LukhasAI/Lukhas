"""
Post-Quantum Cryptography (PQC) signing module for registry checkpoints.

Implements Dilithium2 signature scheme for quantum-resistant checkpoint provenance.
Falls back to HMAC in development environments where liboqs is unavailable.

MATRIZ-007: PQC Migration
Status: Week 1 - Initial Implementation
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
from pathlib import Path
from typing import Optional, Tuple

# Try to import liboqs for PQC support
PQC_AVAILABLE = False
oqs = None

try:
    # Redirect stderr to suppress auto-installation messages
    import sys
    import io
    _stderr = sys.stderr
    sys.stderr = io.StringIO()

    try:
        import oqs as _oqs_module
        # Test if it actually works
        _oqs_module.sig.get_enabled_algorithms()
        PQC_AVAILABLE = True
        oqs = _oqs_module
    finally:
        sys.stderr = _stderr
except Exception:
    # Any error during import or testing means PQC not available
    PQC_AVAILABLE = False
    oqs = None


class PQCSigner:
    """
    Dilithium2 signer for registry checkpoints.

    Features:
    - Quantum-resistant Dilithium2 signatures when liboqs available
    - HMAC fallback for development environments
    - Key generation and management
    - Signature verification
    """

    def __init__(
        self,
        key_path: Optional[Path] = None,
        public_key_path: Optional[Path] = None,
        fallback_hmac_key: Optional[str] = None
    ):
        """
        Initialize PQC signer.

        Args:
            key_path: Path to Dilithium2 private key file
            public_key_path: Path to Dilithium2 public key file
            fallback_hmac_key: HMAC key for fallback mode (development only)
        """
        self.key_path = key_path
        self.public_key_path = public_key_path
        self.fallback_hmac_key = fallback_hmac_key or "dev-hmac-key"
        self.pqc_available = PQC_AVAILABLE

        # Load or generate keys
        if self.pqc_available:
            self._load_or_generate_keys()

    def _load_or_generate_keys(self) -> None:
        """Load existing keys or generate new Dilithium2 keypair."""
        if self.key_path and self.key_path.exists() and self.public_key_path and self.public_key_path.exists():
            # Load existing keys
            self.private_key = self.key_path.read_bytes()
            self.public_key = self.public_key_path.read_bytes()
        else:
            # Generate new keypair
            with oqs.Signature("Dilithium2") as signer:
                self.public_key = signer.generate_keypair()
                self.private_key = signer.export_secret_key()

                # Save keys if paths provided
                if self.key_path:
                    self.key_path.parent.mkdir(parents=True, exist_ok=True)
                    self.key_path.write_bytes(self.private_key)
                    self.key_path.chmod(0o600)  # Restrict permissions

                if self.public_key_path:
                    self.public_key_path.parent.mkdir(parents=True, exist_ok=True)
                    self.public_key_path.write_bytes(self.public_key)

    def sign(self, data: bytes) -> bytes:
        """
        Sign data with Dilithium2 or HMAC fallback.

        Args:
            data: Data to sign

        Returns:
            Signature bytes (Dilithium2 if available, HMAC hex otherwise)
        """
        if self.pqc_available and hasattr(self, 'private_key'):
            # PQC signing with Dilithium2
            with oqs.Signature("Dilithium2", secret_key=self.private_key) as signer:
                signature = signer.sign(data)
                return signature
        else:
            # Fallback to HMAC for development
            signature_hex = hmac.new(
                self.fallback_hmac_key.encode(),
                data,
                hashlib.sha256
            ).hexdigest()
            return signature_hex.encode()

    def verify(self, data: bytes, signature: bytes) -> bool:
        """
        Verify signature with Dilithium2 or HMAC fallback.

        Args:
            data: Original data
            signature: Signature to verify

        Returns:
            True if signature is valid
        """
        if self.pqc_available and hasattr(self, 'public_key'):
            # PQC verification with Dilithium2
            try:
                with oqs.Signature("Dilithium2") as verifier:
                    is_valid = verifier.verify(data, signature, self.public_key)
                    return is_valid
            except Exception:
                return False
        else:
            # Fallback to HMAC verification
            try:
                expected_sig = hmac.new(
                    self.fallback_hmac_key.encode(),
                    data,
                    hashlib.sha256
                ).hexdigest()
                return hmac.compare_digest(expected_sig, signature.decode())
            except Exception:
                return False

    def get_signature_info(self) -> dict:
        """
        Get information about current signature scheme.

        Returns:
            Dict with scheme, status, and key info
        """
        if self.pqc_available and hasattr(self, 'public_key'):
            return {
                "scheme": "Dilithium2",
                "status": "pqc_active",
                "quantum_resistant": True,
                "public_key_size": len(self.public_key),
                "algorithm": "NIST PQC Dilithium2"
            }
        else:
            return {
                "scheme": "HMAC-SHA256",
                "status": "fallback",
                "quantum_resistant": False,
                "warning": "Development fallback - not production ready"
            }


def create_registry_signer(
    registry_root: Path,
    force_hmac: bool = False
) -> PQCSigner:
    """
    Factory function to create a PQC signer for registry checkpoints.

    Args:
        registry_root: Root directory for registry files
        force_hmac: Force HMAC fallback even if PQC available

    Returns:
        Configured PQCSigner instance
    """
    # Key paths
    key_dir = registry_root / ".pqc_keys"
    private_key_path = key_dir / "dilithium2_private.key"
    public_key_path = key_dir / "dilithium2_public.key"

    # Get HMAC key from environment for fallback
    hmac_key = os.environ.get("REGISTRY_HMAC_KEY", "test-key-please-rotate")

    # Create signer (will use HMAC if PQC not available or forced)
    if force_hmac or not PQC_AVAILABLE:
        return PQCSigner(
            key_path=None,  # Don't use PQC keys
            public_key_path=None,
            fallback_hmac_key=hmac_key
        )

    return PQCSigner(
        key_path=private_key_path,
        public_key_path=public_key_path,
        fallback_hmac_key=hmac_key
    )


# Example usage for testing
if __name__ == "__main__":
    import tempfile

    # Create signer
    with tempfile.TemporaryDirectory() as tmpdir:
        signer = create_registry_signer(Path(tmpdir))

        # Test signing and verification
        test_data = b"Test registry checkpoint data"
        signature = signer.sign(test_data)
        is_valid = signer.verify(test_data, signature)

        info = signer.get_signature_info()
        print(f"Signature scheme: {info['scheme']}")
        print(f"Quantum resistant: {info['quantum_resistant']}")
        print(f"Signature valid: {is_valid}")
        print(f"Signature size: {len(signature)} bytes")
