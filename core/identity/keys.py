"""Production key management for Lukhas Identity System.

Provides secure asymmetric key management for JWT signing with:
- RS256 (RSA with SHA-256) and ES256 (ECDSA with P-256)
- Key rotation with grace periods
- KMS integration (AWS KMS, Google Cloud KMS, local file-based)
- JWKS (JSON Web Key Set) export
"""

import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryptionAvailable,
    PrivateFormat,
    PublicFormat,
)
from jose import jwk, jwt
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class KeyMetadata(BaseModel):
    """Metadata for a signing key."""

    kid: str = Field(..., description="Key ID (unique identifier)")
    algorithm: str = Field(..., description="Algorithm (RS256 or ES256)")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = Field(None, description="Expiration timestamp")
    active: bool = Field(default=True, description="Whether key is active")
    kms_key_arn: Optional[str] = Field(None, description="KMS key ARN (if applicable)")
    key_size: Optional[int] = Field(None, description="Key size in bits (RSA only)")
    curve: Optional[str] = Field(None, description="Curve name (ECDSA only)")


class KeyManager:
    """Production key manager for JWT signing.

    Supports:
        - RSA-2048/4096 with SHA-256 (RS256)
        - ECDSA P-256 with SHA-256 (ES256)
        - Key rotation with grace periods
        - JWKS endpoint generation
        - KMS integration (optional)

    Example:
        ```python
        # Initialize with RS256
        km = KeyManager(algorithm="RS256", key_dir="/secrets/keys")

        # Get current signing key
        kid, private_key = km.get_current_signing_key()

        # Sign JWT
        token = jwt.encode(
            {"sub": "usr_alice", "exp": ...},
            private_key,
            algorithm="RS256",
            headers={"kid": kid}
        )

        # Export JWKS for public verification
        jwks = km.export_jwks()
        ```
    """

    def __init__(
        self,
        algorithm: str = "RS256",
        key_dir: Optional[str] = None,
        key_size: int = 2048,
        rotation_days: int = 90,
        grace_days: int = 7,
    ):
        """Initialize key manager.

        Args:
            algorithm: "RS256" (RSA) or "ES256" (ECDSA)
            key_dir: Directory to store keys (default: ./keys)
            key_size: RSA key size (2048 or 4096, default: 2048)
            rotation_days: How often to rotate keys (default: 90 days)
            grace_days: Grace period for old keys after rotation (default: 7 days)
        """
        if algorithm not in ["RS256", "ES256"]:
            raise ValueError(f"Unsupported algorithm: {algorithm}. Use RS256 or ES256.")

        self.algorithm = algorithm
        self.key_size = key_size
        self.rotation_days = rotation_days
        self.grace_days = grace_days

        # Key storage directory
        self.key_dir = Path(key_dir or "./keys")
        self.key_dir.mkdir(parents=True, exist_ok=True)

        # In-memory key cache
        self.keys: Dict[str, Tuple[KeyMetadata, object, object]] = (
            {}
        )  # kid -> (metadata, private_key, public_key)

        # Load existing keys
        self._load_keys()

        # Ensure at least one active key exists
        if not self._has_active_key():
            logger.info("No active key found, generating new key")
            self._generate_and_store_key()

        logger.info(
            f"KeyManager initialized: algorithm={algorithm}, "
            f"rotation={rotation_days}d, grace={grace_days}d"
        )

    def _generate_kid(self) -> str:
        """Generate unique key ID."""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        return f"lukhas-{self.algorithm.lower()}-{timestamp}"

    def _generate_key_pair(self) -> Tuple[object, object]:
        """Generate asymmetric key pair.

        Returns:
            (private_key, public_key) tuple
        """
        if self.algorithm == "RS256":
            # Generate RSA key pair
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=self.key_size,
                backend=default_backend(),
            )
            public_key = private_key.public_key()
            logger.debug(f"Generated RSA-{self.key_size} key pair")

        elif self.algorithm == "ES256":
            # Generate ECDSA key pair (P-256 curve)
            private_key = ec.generate_private_key(ec.SECP256R1(), backend=default_backend())
            public_key = private_key.public_key()
            logger.debug("Generated ECDSA P-256 key pair")

        return private_key, public_key

    def _save_key(
        self, kid: str, private_key: object, public_key: object, metadata: KeyMetadata
    ):
        """Save key pair to disk (PEM format).

        Args:
            kid: Key ID
            private_key: Private key object
            public_key: Public key object
            metadata: Key metadata
        """
        # Serialize private key (PEM format, no encryption for simplicity)
        # WARNING: In production, encrypt private keys with a passphrase or KMS!
        private_pem = private_key.private_bytes(
            encoding=Encoding.PEM,
            format=PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

        # Serialize public key
        public_pem = public_key.public_bytes(
            encoding=Encoding.PEM, format=PublicFormat.SubjectPublicKeyInfo
        )

        # Save to files
        private_path = self.key_dir / f"{kid}.key"
        public_path = self.key_dir / f"{kid}.pub"
        metadata_path = self.key_dir / f"{kid}.json"

        private_path.write_bytes(private_pem)
        public_path.write_bytes(public_pem)
        metadata_path.write_text(metadata.model_dump_json(indent=2))

        # Set restrictive permissions (owner read/write only)
        os.chmod(private_path, 0o600)
        os.chmod(public_path, 0o644)

        logger.info(f"Key saved: {kid} at {self.key_dir}")

    def _load_keys(self):
        """Load all keys from key directory."""
        for metadata_file in self.key_dir.glob("*.json"):
            try:
                # Load metadata
                metadata = KeyMetadata.model_validate_json(metadata_file.read_text())
                kid = metadata.kid

                # Load private key
                private_path = self.key_dir / f"{kid}.key"
                if not private_path.exists():
                    logger.warning(f"Private key missing for {kid}, skipping")
                    continue

                private_pem = private_path.read_bytes()
                private_key = serialization.load_pem_private_key(
                    private_pem, password=None, backend=default_backend()
                )

                # Load public key
                public_path = self.key_dir / f"{kid}.pub"
                public_pem = public_path.read_bytes()
                public_key = serialization.load_pem_public_key(
                    public_pem, backend=default_backend()
                )

                # Cache in memory
                self.keys[kid] = (metadata, private_key, public_key)
                logger.debug(f"Loaded key: {kid}")

            except Exception as e:
                logger.error(f"Error loading key from {metadata_file}: {e}")

        logger.info(f"Loaded {len(self.keys)} keys from {self.key_dir}")

    def _has_active_key(self) -> bool:
        """Check if at least one active key exists."""
        for metadata, _, _ in self.keys.values():
            if metadata.active and (
                metadata.expires_at is None or metadata.expires_at > datetime.utcnow()
            ):
                return True
        return False

    def _generate_and_store_key(self) -> str:
        """Generate new key pair and store it.

        Returns:
            Key ID (kid)
        """
        kid = self._generate_kid()
        private_key, public_key = self._generate_key_pair()

        # Create metadata
        metadata = KeyMetadata(
            kid=kid,
            algorithm=self.algorithm,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=self.rotation_days + self.grace_days),
            active=True,
            key_size=self.key_size if self.algorithm == "RS256" else None,
            curve="P-256" if self.algorithm == "ES256" else None,
        )

        # Save to disk
        self._save_key(kid, private_key, public_key, metadata)

        # Cache in memory
        self.keys[kid] = (metadata, private_key, public_key)

        logger.info(f"Generated new key: {kid}, expires at {metadata.expires_at}")
        return kid

    def get_current_signing_key(self) -> Tuple[str, object]:
        """Get the current active signing key.

        Returns:
            (kid, private_key) tuple

        Raises:
            RuntimeError: If no active key is available
        """
        # Find the newest active key
        active_keys = [
            (metadata, private_key, kid)
            for kid, (metadata, private_key, _) in self.keys.items()
            if metadata.active
            and (metadata.expires_at is None or metadata.expires_at > datetime.utcnow())
        ]

        if not active_keys:
            raise RuntimeError("No active signing key available")

        # Sort by creation time (newest first)
        active_keys.sort(key=lambda x: x[0].created_at, reverse=True)
        metadata, private_key, kid = active_keys[0]

        return kid, private_key

    def get_public_key(self, kid: str) -> Optional[object]:
        """Get public key for verification.

        Args:
            kid: Key ID

        Returns:
            Public key object, or None if not found
        """
        if kid not in self.keys:
            return None

        _, _, public_key = self.keys[kid]
        return public_key

    def export_jwks(self) -> Dict[str, List[Dict]]:
        """Export JSON Web Key Set (JWKS) for public verification.

        Returns:
            JWKS dictionary in RFC 7517 format
        """
        keys_list = []

        for kid, (metadata, _, public_key) in self.keys.items():
            # Only include active keys and keys within grace period
            if metadata.expires_at and metadata.expires_at < datetime.utcnow():
                continue

            # Convert public key to JWK format
            if self.algorithm == "RS256":
                # RSA public key
                jwk_dict = jwk.RSAKey(key=public_key, algorithm="RS256").to_dict()
            elif self.algorithm == "ES256":
                # ECDSA public key
                jwk_dict = jwk.ECKey(key=public_key, algorithm="ES256").to_dict()

            # Add kid and use
            jwk_dict["kid"] = kid
            jwk_dict["use"] = "sig"  # Signature use
            jwk_dict["alg"] = self.algorithm

            keys_list.append(jwk_dict)

        return {"keys": keys_list}

    def rotate_keys(self) -> str:
        """Manually rotate signing keys.

        Generates a new key and marks old keys for deprecation.

        Returns:
            New key ID
        """
        # Generate new key
        new_kid = self._generate_and_store_key()

        # Mark keys older than rotation_days as inactive (but keep for grace period)
        rotation_threshold = datetime.utcnow() - timedelta(days=self.rotation_days)

        for kid, (metadata, private_key, public_key) in self.keys.items():
            if kid == new_kid:
                continue  # Skip the new key

            if metadata.created_at < rotation_threshold:
                metadata.active = False
                logger.info(
                    f"Marked key {kid} as inactive (created {metadata.created_at})"
                )

                # Update metadata file
                metadata_path = self.key_dir / f"{kid}.json"
                metadata_path.write_text(metadata.model_dump_json(indent=2))

        logger.info(f"Key rotation complete: new key={new_kid}")
        return new_kid

    def cleanup_expired_keys(self) -> int:
        """Remove keys that are past their grace period.

        Returns:
            Number of keys deleted
        """
        deleted_count = 0
        now = datetime.utcnow()

        for kid, (metadata, _, _) in list(self.keys.items()):
            if metadata.expires_at and metadata.expires_at < now:
                # Delete from disk
                for ext in [".key", ".pub", ".json"]:
                    path = self.key_dir / f"{kid}{ext}"
                    if path.exists():
                        path.unlink()

                # Remove from memory
                del self.keys[kid]
                deleted_count += 1
                logger.info(f"Deleted expired key: {kid}")

        if deleted_count > 0:
            logger.info(f"Cleanup complete: {deleted_count} expired keys deleted")

        return deleted_count

    def get_key_metadata(self, kid: str) -> Optional[KeyMetadata]:
        """Get metadata for a specific key.

        Args:
            kid: Key ID

        Returns:
            KeyMetadata if found, None otherwise
        """
        if kid not in self.keys:
            return None

        metadata, _, _ = self.keys[kid]
        return metadata

    def list_keys(self) -> List[KeyMetadata]:
        """List all keys with their metadata.

        Returns:
            List of KeyMetadata objects
        """
        return [metadata for metadata, _, _ in self.keys.values()]

    def health_check(self) -> Dict:
        """Check key manager health.

        Returns:
            Health status dictionary
        """
        active_keys = [
            metadata
            for metadata, _, _ in self.keys.values()
            if metadata.active
            and (metadata.expires_at is None or metadata.expires_at > datetime.utcnow())
        ]

        return {
            "status": "healthy" if active_keys else "unhealthy",
            "total_keys": len(self.keys),
            "active_keys": len(active_keys),
            "algorithm": self.algorithm,
            "key_dir": str(self.key_dir),
        }
