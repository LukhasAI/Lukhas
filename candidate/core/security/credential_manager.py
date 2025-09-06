"""
Secure Credential Management System for LUKHAS AI
================================================
Enterprise-grade credential management with encryption at rest,
secure storage, automatic rotation, and comprehensive audit trails.
Handles API keys, tokens, certificates, and other sensitive credentials.
"""

import json
import os
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

try:
    from .enhanced_crypto import CryptoAlgorithm, get_encryption_manager
    from .secure_logging import get_security_logger

    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

logger = get_security_logger(__name__) if CRYPTO_AVAILABLE else None


class CredentialType(Enum):
    """Types of credentials managed by the system"""

    API_KEY = "api_key"
    SECRET_TOKEN = "secret_token"
    PASSWORD = "password"
    CERTIFICATE = "certificate"
    PRIVATE_KEY = "private_key"
    DATABASE_URL = "database_url"
    OAUTH_SECRET = "oauth_secret"
    ENCRYPTION_KEY = "encryption_key"


class CredentialStatus(Enum):
    """Status of credentials"""

    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    PENDING_ROTATION = "pending_rotation"
    DEPRECATED = "deprecated"


@dataclass
class CredentialMetadata:
    """Metadata for credentials"""

    credential_id: str
    credential_type: CredentialType
    service_name: str
    environment: str  # dev, staging, prod
    owner: str
    created_at: datetime
    last_accessed: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    rotation_interval_days: Optional[int] = None
    status: CredentialStatus = CredentialStatus.ACTIVE
    tags: list[str] = field(default_factory=list)
    access_policy: dict[str, Any] = field(default_factory=dict)
    audit_trail: list[dict[str, Any]] = field(default_factory=list)

    def is_expired(self) -> bool:
        """Check if credential has expired"""
        if not self.expires_at:
            return False
        return datetime.now(timezone.utc) > self.expires_at

    def needs_rotation(self) -> bool:
        """Check if credential needs rotation"""
        if not self.rotation_interval_days:
            return False

        rotation_due = self.created_at + timedelta(days=self.rotation_interval_days)
        return datetime.now(timezone.utc) > rotation_due

    def add_audit_entry(self, action: str, details: Optional[dict[str, Any]] = None):
        """Add entry to audit trail"""
        entry = {"timestamp": datetime.now(timezone.utc).isoformat(), "action": action, "details": details or {}}
        self.audit_trail.append(entry)

        # Keep only last 100 entries
        if len(self.audit_trail) > 100:
            self.audit_trail = self.audit_trail[-100:]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "credential_id": self.credential_id,
            "credential_type": self.credential_type.value,
            "service_name": self.service_name,
            "environment": self.environment,
            "owner": self.owner,
            "created_at": self.created_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat() if self.last_accessed else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "rotation_interval_days": self.rotation_interval_days,
            "status": self.status.value,
            "tags": self.tags,
            "access_policy": self.access_policy,
            "audit_trail": self.audit_trail,
            "is_expired": self.is_expired(),
            "needs_rotation": self.needs_rotation(),
        }


class SecureCredentialManager:
    """
    Secure credential management with encryption, rotation, and audit trails
    Replaces hardcoded credentials and insecure storage practices
    """

    def __init__(self, storage_path: Optional[str] = None):
        """Initialize credential manager"""
        if not CRYPTO_AVAILABLE:
            raise ImportError("Enhanced crypto module required")

        # Storage configuration
        self.storage_path = Path(storage_path or os.getenv("LUKHAS_CREDENTIALS_PATH", "data/credentials"))
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Encryption manager
        self.crypto = get_encryption_manager()

        # In-memory credential metadata cache
        self.credentials: dict[str, CredentialMetadata] = {}

        # Load existing credentials
        self._load_credentials()

        # Security settings
        self.max_access_attempts = 3
        self.access_attempt_window_minutes = 15
        self.failed_access_attempts: dict[str, list[datetime]] = {}

        logger.info(f"Secure credential manager initialized with storage: {self.storage_path}")

    async def store_credential(
        self,
        service_name: str,
        credential_type: CredentialType,
        credential_value: Union[str, bytes],
        environment: str = "prod",
        owner: str = "system",
        expires_at: Optional[datetime] = None,
        rotation_interval_days: Optional[int] = None,
        tags: Optional[list[str]] = None,
        access_policy: Optional[dict[str, Any]] = None,
    ) -> str:
        """Store credential securely"""

        credential_id = self._generate_credential_id(service_name, credential_type)

        # Convert to bytes if string
        if isinstance(credential_value, str):
            credential_value = credential_value.encode("utf-8")

        # Encrypt credential
        encrypted_data, encryption_key_id = await self.crypto.encrypt(
            credential_value, purpose=f"credential_{credential_id}"
        )

        # Create metadata
        metadata = CredentialMetadata(
            credential_id=credential_id,
            credential_type=credential_type,
            service_name=service_name,
            environment=environment,
            owner=owner,
            created_at=datetime.now(timezone.utc),
            expires_at=expires_at,
            rotation_interval_days=rotation_interval_days,
            tags=tags or [],
            access_policy=access_policy or {},
        )

        metadata.add_audit_entry(
            "CREATED", {"encryption_key_id": encryption_key_id, "environment": environment, "owner": owner}
        )

        # Store encrypted credential
        credential_file = self.storage_path / f"{credential_id}.enc"
        with open(credential_file, "wb") as f:
            # Store encryption key ID + encrypted data
            header = json.dumps(
                {"encryption_key_id": encryption_key_id, "algorithm": "enhanced_crypto", "version": "1.0"}
            ).encode()

            f.write(len(header).to_bytes(4, "big"))  # Header length
            f.write(header)  # Header
            f.write(encrypted_data)  # Encrypted credential

        # Store metadata
        metadata_file = self.storage_path / f"{credential_id}.meta"
        with open(metadata_file, "w") as f:
            json.dump(metadata.to_dict(), f, indent=2)

        # Cache metadata
        self.credentials[credential_id] = metadata

        logger.info(f"Stored credential {credential_id} for {service_name}")
        return credential_id

    async def retrieve_credential(self, credential_id: str, requester: str = "system") -> Optional[bytes]:
        """Retrieve credential securely"""

        # Check access permissions
        if not await self._check_access_permission(credential_id, requester):
            logger.warning(f"Access denied for credential {credential_id} by {requester}")
            return None

        # Check rate limiting
        if not self._check_rate_limit(credential_id):
            logger.warning(f"Rate limit exceeded for credential {credential_id}")
            return None

        metadata = self.credentials.get(credential_id)
        if not metadata:
            logger.error(f"Credential not found: {credential_id}")
            return None

        # Check credential status
        if metadata.status != CredentialStatus.ACTIVE:
            logger.warning(f"Credential {credential_id} is not active: {metadata.status}")
            return None

        if metadata.is_expired():
            logger.warning(f"Credential {credential_id} has expired")
            metadata.status = CredentialStatus.EXPIRED
            await self._update_metadata(credential_id, metadata)
            return None

        try:
            # Load encrypted credential
            credential_file = self.storage_path / f"{credential_id}.enc"
            if not credential_file.exists():
                logger.error(f"Credential file not found: {credential_file}")
                return None

            with open(credential_file, "rb") as f:
                # Read header
                header_len = int.from_bytes(f.read(4), "big")
                header_data = f.read(header_len)
                header = json.loads(header_data.decode())

                # Read encrypted data
                encrypted_data = f.read()

            # Decrypt credential
            decrypted_data = await self.crypto.decrypt(encrypted_data, header["encryption_key_id"])

            # Update access tracking
            metadata.last_accessed = datetime.now(timezone.utc)
            metadata.add_audit_entry("ACCESSED", {"requester": requester})
            await self._update_metadata(credential_id, metadata)

            logger.info(f"Retrieved credential {credential_id} for {requester}")
            return decrypted_data

        except Exception as e:
            logger.error(f"Failed to retrieve credential {credential_id}: {e}")
            self._record_access_failure(credential_id)
            return None

    async def rotate_credential(self, credential_id: str, new_value: Union[str, bytes]) -> bool:
        """Rotate credential to new value"""

        metadata = self.credentials.get(credential_id)
        if not metadata:
            logger.error(f"Credential not found for rotation: {credential_id}")
            return False

        try:
            # Store old credential as backup
            old_file = self.storage_path / f"{credential_id}.enc"
            backup_file = self.storage_path / f"{credential_id}.backup_{int(datetime.now().timestamp())}"
            if old_file.exists():
                old_file.rename(backup_file)

            # Convert to bytes if string
            if isinstance(new_value, str):
                new_value = new_value.encode("utf-8")

            # Encrypt new credential
            encrypted_data, encryption_key_id = await self.crypto.encrypt(
                new_value, purpose=f"credential_{credential_id}_rotated"
            )

            # Store new encrypted credential
            with open(old_file, "wb") as f:
                header = json.dumps(
                    {"encryption_key_id": encryption_key_id, "algorithm": "enhanced_crypto", "version": "1.0"}
                ).encode()

                f.write(len(header).to_bytes(4, "big"))
                f.write(header)
                f.write(encrypted_data)

            # Update metadata
            metadata.created_at = datetime.now(timezone.utc)
            metadata.status = CredentialStatus.ACTIVE
            metadata.add_audit_entry(
                "ROTATED", {"new_encryption_key_id": encryption_key_id, "backup_file": str(backup_file.name)}
            )

            await self._update_metadata(credential_id, metadata)

            logger.info(f"Rotated credential {credential_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to rotate credential {credential_id}: {e}")
            return False

    async def revoke_credential(self, credential_id: str, reason: str = "manual_revocation") -> bool:
        """Revoke credential"""

        metadata = self.credentials.get(credential_id)
        if not metadata:
            logger.error(f"Credential not found for revocation: {credential_id}")
            return False

        # Update status
        metadata.status = CredentialStatus.REVOKED
        metadata.add_audit_entry("REVOKED", {"reason": reason})

        # Move credential file to revoked directory
        revoked_dir = self.storage_path / "revoked"
        revoked_dir.mkdir(exist_ok=True)

        credential_file = self.storage_path / f"{credential_id}.enc"
        if credential_file.exists():
            credential_file.rename(revoked_dir / f"{credential_id}.enc")

        await self._update_metadata(credential_id, metadata)

        logger.info(f"Revoked credential {credential_id}: {reason}")
        return True

    def list_credentials(
        self,
        environment: Optional[str] = None,
        service_name: Optional[str] = None,
        credential_type: Optional[CredentialType] = None,
        include_inactive: bool = False,
    ) -> list[dict[str, Any]]:
        """List credentials with filtering"""

        results = []
        for metadata in self.credentials.values():
            # Apply filters
            if environment and metadata.environment != environment:
                continue
            if service_name and metadata.service_name != service_name:
                continue
            if credential_type and metadata.credential_type != credential_type:
                continue
            if not include_inactive and metadata.status != CredentialStatus.ACTIVE:
                continue

            # Return metadata (excluding sensitive audit trail)
            credential_info = metadata.to_dict()
            credential_info["audit_trail"] = len(metadata.audit_trail)  # Just count
            results.append(credential_info)

        return results

    def get_credentials_needing_rotation(self) -> list[str]:
        """Get list of credentials that need rotation"""
        return [
            cred_id
            for cred_id, metadata in self.credentials.items()
            if metadata.needs_rotation() and metadata.status == CredentialStatus.ACTIVE
        ]

    def get_expired_credentials(self) -> list[str]:
        """Get list of expired credentials"""
        return [cred_id for cred_id, metadata in self.credentials.items() if metadata.is_expired()]

    async def cleanup_old_credentials(self, days_old: int = 90) -> int:
        """Clean up old revoked/expired credentials"""

        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_old)
        cleaned_count = 0

        for cred_id, metadata in list(self.credentials.items()):
            if (
                metadata.status in [CredentialStatus.REVOKED, CredentialStatus.EXPIRED]
                and metadata.created_at < cutoff_date
            ):

                # Remove files
                for ext in [".enc", ".meta"]:
                    file_path = self.storage_path / f"{cred_id}{ext}"
                    if file_path.exists():
                        file_path.unlink()

                # Remove from cache
                del self.credentials[cred_id]
                cleaned_count += 1

                logger.info(f"Cleaned up old credential: {cred_id}")

        return cleaned_count

    # Internal methods

    def _load_credentials(self):
        """Load credential metadata from storage"""
        if not self.storage_path.exists():
            return

        for meta_file in self.storage_path.glob("*.meta"):
            try:
                with open(meta_file) as f:
                    data = json.load(f)

                # Reconstruct metadata object
                metadata = CredentialMetadata(
                    credential_id=data["credential_id"],
                    credential_type=CredentialType(data["credential_type"]),
                    service_name=data["service_name"],
                    environment=data["environment"],
                    owner=data["owner"],
                    created_at=datetime.fromisoformat(data["created_at"]),
                    last_accessed=datetime.fromisoformat(data["last_accessed"]) if data.get("last_accessed") else None,
                    expires_at=datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None,
                    rotation_interval_days=data.get("rotation_interval_days"),
                    status=CredentialStatus(data.get("status", "active")),
                    tags=data.get("tags", []),
                    access_policy=data.get("access_policy", {}),
                    audit_trail=data.get("audit_trail", []),
                )

                self.credentials[metadata.credential_id] = metadata

            except Exception as e:
                logger.error(f"Failed to load credential metadata from {meta_file}: {e}")

    async def _update_metadata(self, credential_id: str, metadata: CredentialMetadata):
        """Update credential metadata"""
        metadata_file = self.storage_path / f"{credential_id}.meta"
        with open(metadata_file, "w") as f:
            json.dump(metadata.to_dict(), f, indent=2)

        self.credentials[credential_id] = metadata

    async def _check_access_permission(self, credential_id: str, requester: str) -> bool:
        """Check if requester has permission to access credential"""
        metadata = self.credentials.get(credential_id)
        if not metadata:
            return False

        # Check access policy
        access_policy = metadata.access_policy
        if not access_policy:
            return True  # No policy = allow all

        allowed_users = access_policy.get("allowed_users", [])
        if allowed_users and requester not in allowed_users:
            return False

        denied_users = access_policy.get("denied_users", [])
        return requester not in denied_users

    def _check_rate_limit(self, credential_id: str) -> bool:
        """Check rate limiting for credential access"""
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(minutes=self.access_attempt_window_minutes)

        # Clean old attempts
        if credential_id in self.failed_access_attempts:
            self.failed_access_attempts[credential_id] = [
                attempt for attempt in self.failed_access_attempts[credential_id] if attempt > cutoff
            ]

        # Check if under limit
        attempts = len(self.failed_access_attempts.get(credential_id, []))
        return attempts < self.max_access_attempts

    def _record_access_failure(self, credential_id: str):
        """Record failed access attempt"""
        now = datetime.now(timezone.utc)

        if credential_id not in self.failed_access_attempts:
            self.failed_access_attempts[credential_id] = []

        self.failed_access_attempts[credential_id].append(now)

    def _generate_credential_id(self, service_name: str, credential_type: CredentialType) -> str:
        """Generate unique credential ID"""
        timestamp = int(datetime.now().timestamp())
        random_part = secrets.token_hex(8)
        return f"{service_name}_{credential_type.value}_{timestamp}_{random_part}"


# Global credential manager instance
_credential_manager: Optional[SecureCredentialManager] = None


def get_credential_manager() -> SecureCredentialManager:
    """Get global credential manager instance"""
    global _credential_manager
    if _credential_manager is None:
        _credential_manager = SecureCredentialManager()
    return _credential_manager


# Convenience functions for common operations
async def store_api_key(service_name: str, api_key: str, environment: str = "prod") -> str:
    """Store API key securely"""
    manager = get_credential_manager()
    return await manager.store_credential(
        service_name=service_name,
        credential_type=CredentialType.API_KEY,
        credential_value=api_key,
        environment=environment,
        rotation_interval_days=90,  # Rotate every 90 days
    )


async def get_api_key(service_name: str, environment: str = "prod") -> Optional[str]:
    """Retrieve API key"""
    manager = get_credential_manager()

    # Find credential ID
    credentials = manager.list_credentials(
        service_name=service_name, credential_type=CredentialType.API_KEY, environment=environment
    )

    if not credentials:
        logger.warning(f"No API key found for {service_name} in {environment}")
        return None

    # Get most recent active credential
    active_creds = [c for c in credentials if c["status"] == "active"]
    if not active_creds:
        logger.warning(f"No active API key found for {service_name} in {environment}")
        return None

    latest_cred = max(active_creds, key=lambda x: x["created_at"])

    # Retrieve credential value
    credential_data = await manager.retrieve_credential(latest_cred["credential_id"])
    if credential_data:
        return credential_data.decode("utf-8")

    return None


# Example usage and testing
async def example_usage():
    """Example usage of credential manager"""
    print("🔐 Secure Credential Management Example")
    print("=" * 50)

    # Create credential manager
    manager = get_credential_manager()

    # Store some test credentials
    openai_key_id = await manager.store_credential(
        service_name="openai",
        credential_type=CredentialType.API_KEY,
        credential_value="sk-test-key-1234567890abcdef",
        environment="test",
        rotation_interval_days=30,
        tags=["ai", "language-model"],
    )
    print(f"✅ Stored OpenAI API key: {openai_key_id}")

    # Store database URL
    db_url_id = await manager.store_credential(
        service_name="postgres",
        credential_type=CredentialType.DATABASE_URL,
        credential_value="postgresql://user:pass@localhost:5432/lukhas",
        environment="dev",
        access_policy={"allowed_users": ["system", "dev-team"]},
    )
    print(f"✅ Stored database URL: {db_url_id}")

    # Retrieve credentials
    openai_key = await manager.retrieve_credential(openai_key_id)
    if openai_key:
        print(f"✅ Retrieved OpenAI key: {openai_key.decode()[:20]}...")

    # Test convenience functions
    await store_api_key("anthropic", "sk-ant-test-key", "test")
    anthropic_key = await get_api_key("anthropic", "test")
    if anthropic_key:
        print(f"✅ Retrieved Anthropic key via convenience function: {anthropic_key[:20]}...")

    # List credentials
    all_creds = manager.list_credentials()
    print(f"📋 Total credentials: {len(all_creds)}")

    # Test rotation
    success = await manager.rotate_credential(openai_key_id, "sk-new-rotated-key-9876543210")
    print(f"🔄 Key rotation: {'✅ Success' if success else '❌ Failed'}")

    print("\n✅ Credential management test completed")


if __name__ == "__main__":
    import asyncio

    asyncio.run(example_usage())
