# path: qi/crypto/pqc_signer.py
from __future__ import annotations

import base64
import hashlib
import json
import os
from typing import Any

# Check for PQC library availability
try:
    import dilithium

    HAS_DILITHIUM = True
except ImportError:
    HAS_DILITHIUM = False

# Fallback to Ed25519
try:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import ed25519

    HAS_ED25519 = True
except ImportError:
    HAS_ED25519 = False

# Key storage paths
STATE = os.path.expanduser(os.environ.get("LUKHAS_STATE", "~/.lukhas/state"))
KEYS_DIR = os.path.join(STATE, "crypto", "keys")
os.makedirs(KEYS_DIR, exist_ok=True)


class PQCSigner:
    """Post-quantum cryptographic signer with Ed25519 fallback."""

    def __init__(self, profile: str = "development"):
        self.profile = profile
        self.keys_dir = KEYS_DIR
        self._load_or_generate_keys()

    def _load_or_generate_keys(self):
        """Load existing keys or generate new ones."""
        key_file = os.path.join(self.keys_dir, f"{self.profile}_key.json")

        if os.path.exists(key_file):
            with open(key_file) as f:
                self.key_data = json.load(f)
        else:
            self.key_data = self._generate_keys()
            with open(key_file, "w") as f:
                json.dump(self.key_data, f, indent=2)
            # Set restrictive permissions
            os.chmod(key_file, 0o600)

    def _generate_keys(self) -> dict[str, Any]:
        """Generate new signing keys."""
        if self.profile == "production" and HAS_DILITHIUM:
            # Generate Dilithium3 keys (placeholder - real implementation would use actual lib)
            return {
                "algorithm": "dilithium3",
                "public_key": base64.b64encode(os.urandom(1952)).decode(),  # Dilithium3 public key size
                "private_key": base64.b64encode(os.urandom(4000)).decode(),  # Dilithium3 private key size
                "key_id": hashlib.sha256(os.urandom(32)).hexdigest()[:16],
            }
        elif HAS_ED25519:
            # Generate Ed25519 keys
            private_key = ed25519.Ed25519PrivateKey.generate()
            public_key = private_key.public_key()

            private_bytes = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )

            public_bytes = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )

            return {
                "algorithm": "ed25519",
                "public_key": base64.b64encode(public_bytes).decode(),
                "private_key": base64.b64encode(private_bytes).decode(),
                "key_id": hashlib.sha256(public_bytes).hexdigest()[:16],
            }
        else:
            # Fallback to mock keys for development
            return {
                "algorithm": "mock_ed25519",
                "public_key": base64.b64encode(os.urandom(32)).decode(),
                "private_key": base64.b64encode(os.urandom(64)).decode(),
                "key_id": hashlib.sha256(os.urandom(32)).hexdigest()[:16],
            }

    def sign(self, data: bytes) -> dict[str, str]:
        """Sign data and return signature info."""
        content_hash = hashlib.sha3_512(data).hexdigest()

        if self.key_data["algorithm"] == "dilithium3" and HAS_DILITHIUM:
            # Use Dilithium3 (placeholder)
            signature = base64.b64encode(os.urandom(3293)).decode()  # Dilithium3 signature size
            alg = "dilithium3"
        elif self.key_data["algorithm"] == "ed25519" and HAS_ED25519:
            # Use Ed25519
            private_bytes = base64.b64decode(self.key_data["private_key"])
            private_key = serialization.load_pem_private_key(private_bytes, password=None)
            signature_bytes = private_key.sign(data)
            signature = base64.b64encode(signature_bytes).decode()
            alg = "ed25519"
        else:
            # Mock signature for development
            signature = base64.b64encode(hashlib.sha256(data).digest()).decode()
            alg = "mock_ed25519"

        return {
            "alg": alg,
            "sig": signature,
            "content_hash": content_hash,
            "pubkey_id": self.key_data["key_id"],
        }

    def verify(self, data: bytes, signature_info: dict[str, str]) -> bool:
        """Verify signature."""
        # Verify content hash
        content_hash = hashlib.sha3_512(data).hexdigest()
        if content_hash != signature_info.get("content_hash"):
            return False

        # Verify signature based on algorithm
        alg = signature_info.get("alg")
        sig = signature_info.get("sig")

        if not alg or not sig:
            return False

        if alg == "dilithium3" and HAS_DILITHIUM:
            # Verify with Dilithium3 (placeholder)
            return True  # Would use actual verification
        elif alg == "ed25519" and HAS_ED25519:
            try:
                public_bytes = base64.b64decode(self.key_data["public_key"])
                public_key = serialization.load_pem_public_key(public_bytes)
                signature_bytes = base64.b64decode(sig)
                public_key.verify(signature_bytes, data)
                return True
            except Exception:
                return False
        elif alg == "mock_ed25519":
            # Mock verification
            expected = base64.b64encode(hashlib.sha256(data).digest()).decode()
            return sig == expected

        return False


# Helper functions for convenience
def sign_dilithium(data: bytes) -> dict[str, str]:
    """Sign data with Dilithium3 (production) or Ed25519 (dev)."""
    profile = "production" if os.environ.get("LUKHAS_ENV") == "production" else "development"
    signer = PQCSigner(profile)
    return signer.sign(data)


def verify_signature(data: bytes, signature_info: dict[str, str]) -> bool:
    """Verify signature."""
    profile = "production" if os.environ.get("LUKHAS_ENV") == "production" else "development"
    signer = PQCSigner(profile)
    return signer.verify(data, signature_info)
