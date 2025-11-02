#!/usr/bin/env python3
"""
LUKHAS API Optimization - Secrets Management

Secure handling of sensitive configuration values with encryption,
key rotation, and secure storage capabilities.

# ΛTAG: security_infrastructure, secrets_management, encryption_handling
"""

import base64
import hashlib
import json
import logging
import os
import secrets
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = logging.getLogger(__name__)


@dataclass
class SecretMetadata:
    """Metadata for stored secrets"""
    name: str
    created_at: str
    expires_at: Optional[str] = None
    rotated_at: Optional[str] = None
    access_count: int = 0
    last_accessed: Optional[str] = None
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


@dataclass
class SecretEntry:
    """Complete secret entry with metadata"""
    metadata: SecretMetadata
    encrypted_value: str
    salt: str
    algorithm: str = "PBKDF2-FERNET"


class SecretsManager:
    """Secure secrets management with encryption and rotation"""

    def __init__(self,
                 master_key: Optional[str] = None,
                 secrets_dir: Path = Path("config/secrets"),
                 auto_rotate_days: int = 90):
        """
        Initialize secrets manager

        Args:
            master_key: Master encryption key (optional, will be derived)
            secrets_dir: Directory for storing encrypted secrets
            auto_rotate_days: Days before auto-rotation is recommended
        """
        self.secrets_dir = Path(secrets_dir)
        self.secrets_dir.mkdir(parents=True, exist_ok=True)
        self.auto_rotate_days = auto_rotate_days

        # Initialize encryption
        self.master_key = master_key or self._get_or_create_master_key()
        self.cipher = self._create_cipher(self.master_key)

        # Load existing secrets
        self.secrets_db = self._load_secrets_db()

        # Setup logging
        logging.basicConfig(level=logging.INFO)

    def _get_or_create_master_key(self) -> str:
        """Get master key from environment or create new one"""

        # Try environment variable first
        master_key = os.getenv("LUKHAS_MASTER_KEY")
        if master_key:
            return master_key

        # Try key file
        key_file = self.secrets_dir / ".master_key"
        if key_file.exists():
            try:
                with open(key_file, "rb") as f:
                    return f.read().decode()
            except Exception as e:
                logger.warning(f"Failed to read master key file: {e}")

        # Generate new key
        logger.info("Generating new master key")
        new_key = Fernet.generate_key().decode()

        # Save to file (secure permissions)
        try:
            with open(key_file, "wb") as f:
                f.write(new_key.encode())
            os.chmod(key_file, 0o600)  # Owner read/write only
            logger.info(f"Master key saved to {key_file}")
        except Exception as e:
            logger.warning(f"Failed to save master key file: {e}")

        # Print key for environment variable
        print(f"🔑 Generated master key: {new_key}")
        print(f"💡 Set environment variable: export LUKHAS_MASTER_KEY='{new_key}'")

        return new_key

    def _create_cipher(self, key: str) -> Fernet:
        """Create Fernet cipher from key"""
        try:
            return Fernet(key.encode())
        except Exception:
            # If key is not proper Fernet key, derive one
            password = key.encode()
            salt = b"lukhas_api_optimization_salt"  # Fixed salt for consistency
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key_bytes = base64.urlsafe_b64encode(kdf.derive(password))
            return Fernet(key_bytes)

    def _load_secrets_db(self) -> Dict[str, SecretEntry]:
        """Load secrets database from file"""
        db_file = self.secrets_dir / "secrets.db"
        if not db_file.exists():
            return {}

        try:
            with open(db_file) as f:
                data = json.load(f)

            secrets_db = {}
            for name, entry_data in data.items():
                metadata = SecretMetadata(**entry_data["metadata"])
                entry = SecretEntry(
                    metadata=metadata,
                    encrypted_value=entry_data["encrypted_value"],
                    salt=entry_data["salt"],
                    algorithm=entry_data.get("algorithm", "PBKDF2-FERNET")
                )
                secrets_db[name] = entry

            return secrets_db

        except Exception as e:
            logger.error(f"Failed to load secrets database: {e}")
            return {}

    def _save_secrets_db(self):
        """Save secrets database to file"""
        db_file = self.secrets_dir / "secrets.db"

        data = {}
        for name, entry in self.secrets_db.items():
            data[name] = {
                "metadata": asdict(entry.metadata),
                "encrypted_value": entry.encrypted_value,
                "salt": entry.salt,
                "algorithm": entry.algorithm
            }

        try:
            with open(db_file, "w") as f:
                json.dump(data, f, indent=2)
            os.chmod(db_file, 0o600)  # Owner read/write only

        except Exception as e:
            logger.error(f"Failed to save secrets database: {e}")
            raise

    def store_secret(self,
                    name: str,
                    value: str,
                    expires_days: Optional[int] = None,
                    tags: Optional[List[str]] = None) -> bool:
        """
        Store a secret securely

        Args:
            name: Secret name/identifier
            value: Secret value to encrypt
            expires_days: Days until expiration (optional)
            tags: Tags for categorization

        Returns:
            True if successful
        """
        try:
            # Generate salt for this secret
            salt = secrets.token_hex(16)

            # Encrypt the value
            encrypted_value = self.cipher.encrypt(value.encode())
            encrypted_b64 = base64.b64encode(encrypted_value).decode()

            # Create metadata
            created_at = datetime.utcnow().isoformat()
            expires_at = None
            if expires_days:
                expires_at = (datetime.utcnow() + timedelta(days=expires_days)).isoformat()

            metadata = SecretMetadata(
                name=name,
                created_at=created_at,
                expires_at=expires_at,
                tags=tags or []
            )

            # Create entry
            entry = SecretEntry(
                metadata=metadata,
                encrypted_value=encrypted_b64,
                salt=salt
            )

            # Store in database
            self.secrets_db[name] = entry
            self._save_secrets_db()

            logger.info(f"Secret '{name}' stored successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to store secret '{name}': {e}")
            return False

    def get_secret(self, name: str) -> Optional[str]:
        """
        Retrieve and decrypt a secret

        Args:
            name: Secret name/identifier

        Returns:
            Decrypted secret value or None
        """
        if name not in self.secrets_db:
            logger.warning(f"Secret '{name}' not found")
            return None

        entry = self.secrets_db[name]

        # Check expiration
        if entry.metadata.expires_at:
            expires_at = datetime.fromisoformat(entry.metadata.expires_at)
            if datetime.utcnow() > expires_at:
                logger.warning(f"Secret '{name}' has expired")
                return None

        try:
            # Decrypt the value
            encrypted_bytes = base64.b64decode(entry.encrypted_value.encode())
            decrypted_value = self.cipher.decrypt(encrypted_bytes).decode()

            # Update access metadata
            entry.metadata.access_count += 1
            entry.metadata.last_accessed = datetime.utcnow().isoformat()
            self._save_secrets_db()

            return decrypted_value

        except Exception as e:
            logger.error(f"Failed to decrypt secret '{name}': {e}")
            return None

    def rotate_secret(self, name: str, new_value: str) -> bool:
        """
        Rotate a secret to a new value

        Args:
            name: Secret name/identifier  
            new_value: New secret value

        Returns:
            True if successful
        """
        if name not in self.secrets_db:
            logger.warning(f"Secret '{name}' not found for rotation")
            return False

        try:
            entry = self.secrets_db[name]

            # Generate new salt
            salt = secrets.token_hex(16)

            # Encrypt new value
            encrypted_value = self.cipher.encrypt(new_value.encode())
            encrypted_b64 = base64.b64encode(encrypted_value).decode()

            # Update entry
            entry.encrypted_value = encrypted_b64
            entry.salt = salt
            entry.metadata.rotated_at = datetime.utcnow().isoformat()

            self._save_secrets_db()

            logger.info(f"Secret '{name}' rotated successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to rotate secret '{name}': {e}")
            return False

    def delete_secret(self, name: str) -> bool:
        """
        Delete a secret

        Args:
            name: Secret name/identifier

        Returns:
            True if successful
        """
        if name not in self.secrets_db:
            logger.warning(f"Secret '{name}' not found for deletion")
            return False

        try:
            del self.secrets_db[name]
            self._save_secrets_db()

            logger.info(f"Secret '{name}' deleted successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to delete secret '{name}': {e}")
            return False

    def list_secrets(self, tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        List all secrets with metadata

        Args:
            tags: Filter by tags (optional)

        Returns:
            List of secret metadata
        """
        secrets_list = []

        for name, entry in self.secrets_db.items():
            # Filter by tags if specified
            if tags and not any(tag in entry.metadata.tags for tag in tags):
                continue

            # Check if needs rotation
            needs_rotation = False
            if entry.metadata.created_at:
                created_at = datetime.fromisoformat(entry.metadata.created_at)
                age_days = (datetime.utcnow() - created_at).days
                needs_rotation = age_days >= self.auto_rotate_days

            # Check if expired
            is_expired = False
            if entry.metadata.expires_at:
                expires_at = datetime.fromisoformat(entry.metadata.expires_at)
                is_expired = datetime.utcnow() > expires_at

            secrets_list.append({
                "name": name,
                "created_at": entry.metadata.created_at,
                "expires_at": entry.metadata.expires_at,
                "rotated_at": entry.metadata.rotated_at,
                "access_count": entry.metadata.access_count,
                "last_accessed": entry.metadata.last_accessed,
                "tags": entry.metadata.tags,
                "needs_rotation": needs_rotation,
                "is_expired": is_expired
            })

        return secrets_list

    def export_secrets_for_env(self,
                              environment: str = "production",
                              format: str = "env") -> str:
        """
        Export secrets for deployment environment

        Args:
            environment: Target environment
            format: Export format ('env', 'yaml', 'json')

        Returns:
            Formatted secrets for deployment
        """
        env_secrets = {}

        for name, entry in self.secrets_db.items():
            # Skip expired secrets
            if entry.metadata.expires_at:
                expires_at = datetime.fromisoformat(entry.metadata.expires_at)
                if datetime.utcnow() > expires_at:
                    continue

            # Get secret value
            secret_value = self.get_secret(name)
            if secret_value:
                env_name = f"LUKHAS_SECRET_{name.upper()}"
                env_secrets[env_name] = secret_value

        if format == "env":
            lines = []
            for key, value in env_secrets.items():
                # Escape quotes in value
                escaped_value = value.replace('"', '\\"')
                lines.append(f'{key}="{escaped_value}"')
            return "\n".join(lines)

        elif format == "yaml":
            import yaml
            return yaml.dump(env_secrets, default_flow_style=False)

        elif format == "json":
            return json.dumps(env_secrets, indent=2)

        else:
            raise ValueError(f"Unsupported format: {format}")

    def import_secrets_from_env(self, prefix: str = "LUKHAS_SECRET_") -> int:
        """
        Import secrets from environment variables

        Args:
            prefix: Environment variable prefix

        Returns:
            Number of secrets imported
        """
        imported_count = 0

        for key, value in os.environ.items():
            if key.startswith(prefix):
                secret_name = key[len(prefix):].lower()

                # Store secret with environment tag
                if self.store_secret(secret_name, value, tags=["environment", "auto-imported"]):
                    imported_count += 1
                    logger.info(f"Imported secret from environment: {secret_name}")

        return imported_count

    def validate_secrets(self) -> Dict[str, Any]:
        """
        Validate all secrets and return status

        Returns:
            Validation results
        """
        total_secrets = len(self.secrets_db)
        expired_secrets = []
        rotation_needed = []
        accessible_secrets = 0

        for name, entry in self.secrets_db.items():
            # Check expiration
            if entry.metadata.expires_at:
                expires_at = datetime.fromisoformat(entry.metadata.expires_at)
                if datetime.utcnow() > expires_at:
                    expired_secrets.append(name)
                    continue

            # Check if needs rotation
            if entry.metadata.created_at:
                created_at = datetime.fromisoformat(entry.metadata.created_at)
                age_days = (datetime.utcnow() - created_at).days
                if age_days >= self.auto_rotate_days:
                    rotation_needed.append(name)

            # Test accessibility
            try:
                test_value = self.get_secret(name)
                if test_value:
                    accessible_secrets += 1
            except Exception:
                pass

        return {
            "total_secrets": total_secrets,
            "accessible_secrets": accessible_secrets,
            "expired_secrets": expired_secrets,
            "rotation_needed": rotation_needed,
            "expired_count": len(expired_secrets),
            "rotation_count": len(rotation_needed),
            "health_score": (accessible_secrets / total_secrets * 100) if total_secrets > 0 else 100
        }

    def generate_api_key(self,
                        name: str,
                        length: int = 32,
                        expires_days: Optional[int] = None) -> Tuple[str, str]:
        """
        Generate a secure API key

        Args:
            name: Name for the API key
            length: Key length in bytes
            expires_days: Days until expiration

        Returns:
            Tuple of (api_key, key_id)
        """
        # Generate secure random key
        api_key = secrets.token_urlsafe(length)

        # Generate key ID (first 8 chars of hash)
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        key_id = key_hash[:8]

        # Store the key
        full_name = f"api_key_{name}_{key_id}"
        self.store_secret(
            full_name,
            api_key,
            expires_days=expires_days,
            tags=["api_key", name]
        )

        logger.info(f"Generated API key for '{name}' with ID: {key_id}")
        return api_key, key_id

    def verify_api_key(self, api_key: str, name: str) -> bool:
        """
        Verify an API key

        Args:
            api_key: API key to verify
            name: Name associated with the key

        Returns:
            True if key is valid
        """
        # Generate key ID from provided key
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        key_id = key_hash[:8]

        # Look up stored key
        full_name = f"api_key_{name}_{key_id}"
        stored_key = self.get_secret(full_name)

        return stored_key == api_key if stored_key else False


# Global secrets manager instance
_secrets_manager: Optional[SecretsManager] = None

def get_secrets_manager() -> SecretsManager:
    """Get global secrets manager instance"""
    global _secrets_manager
    if _secrets_manager is None:
        _secrets_manager = SecretsManager()
    return _secrets_manager


def store_secret(name: str, value: str, **kwargs) -> bool:
    """Store a secret using global manager"""
    return get_secrets_manager().store_secret(name, value, **kwargs)


def get_secret(name: str) -> Optional[str]:
    """Get a secret using global manager"""
    return get_secrets_manager().get_secret(name)


def generate_api_key(name: str, **kwargs) -> Tuple[str, str]:
    """Generate API key using global manager"""
    return get_secrets_manager().generate_api_key(name, **kwargs)


if __name__ == "__main__":
    """CLI interface for secrets management"""
    import argparse

    parser = argparse.ArgumentParser(description="LUKHAS API Optimization Secrets Manager")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Store secret
    store_parser = subparsers.add_parser("store", help="Store a secret")
    store_parser.add_argument("name", help="Secret name")
    store_parser.add_argument("value", help="Secret value")
    store_parser.add_argument("--expires-days", type=int, help="Days until expiration")
    store_parser.add_argument("--tags", nargs="+", help="Tags for categorization")

    # Get secret
    get_parser = subparsers.add_parser("get", help="Get a secret")
    get_parser.add_argument("name", help="Secret name")

    # List secrets
    list_parser = subparsers.add_parser("list", help="List secrets")
    list_parser.add_argument("--tags", nargs="+", help="Filter by tags")
    list_parser.add_argument("--format", choices=["table", "json"], default="table")

    # Rotate secret
    rotate_parser = subparsers.add_parser("rotate", help="Rotate a secret")
    rotate_parser.add_argument("name", help="Secret name")
    rotate_parser.add_argument("new_value", help="New secret value")

    # Delete secret
    delete_parser = subparsers.add_parser("delete", help="Delete a secret")
    delete_parser.add_argument("name", help="Secret name")

    # Generate API key
    apikey_parser = subparsers.add_parser("generate-api-key", help="Generate API key")
    apikey_parser.add_argument("name", help="API key name")
    apikey_parser.add_argument("--expires-days", type=int, help="Days until expiration")

    # Export secrets
    export_parser = subparsers.add_parser("export", help="Export secrets for deployment")
    export_parser.add_argument("--format", choices=["env", "yaml", "json"], default="env")
    export_parser.add_argument("--environment", default="production")

    # Import from environment
    import_parser = subparsers.add_parser("import-env", help="Import from environment variables")
    import_parser.add_argument("--prefix", default="LUKHAS_SECRET_")

    # Validate secrets
    validate_parser = subparsers.add_parser("validate", help="Validate all secrets")

    # Generate master key
    keygen_parser = subparsers.add_parser("generate-key", help="Generate master key")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        exit(1)

    # Initialize secrets manager
    manager = SecretsManager()

    if args.command == "store":
        success = manager.store_secret(
            args.name,
            args.value,
            expires_days=args.expires_days,
            tags=args.tags
        )
        print("✅ Secret stored successfully" if success else "❌ Failed to store secret")

    elif args.command == "get":
        value = manager.get_secret(args.name)
        if value:
            print(value)
        else:
            print(f"❌ Secret '{args.name}' not found")
            exit(1)

    elif args.command == "list":
        secrets_list = manager.list_secrets(tags=args.tags)

        if args.format == "json":
            print(json.dumps(secrets_list, indent=2))
        else:
            if not secrets_list:
                print("No secrets found")
            else:
                print(f"{'Name':<20} {'Created':<20} {'Expires':<20} {'Needs Rotation':<15}")
                print("-" * 80)
                for secret in secrets_list:
                    name = secret["name"][:19]
                    created = secret["created_at"][:19] if secret["created_at"] else "N/A"
                    expires = secret["expires_at"][:19] if secret["expires_at"] else "Never"
                    rotation = "Yes" if secret["needs_rotation"] else "No"
                    print(f"{name:<20} {created:<20} {expires:<20} {rotation:<15}")

    elif args.command == "rotate":
        success = manager.rotate_secret(args.name, args.new_value)
        print("✅ Secret rotated successfully" if success else "❌ Failed to rotate secret")

    elif args.command == "delete":
        success = manager.delete_secret(args.name)
        print("✅ Secret deleted successfully" if success else "❌ Failed to delete secret")

    elif args.command == "generate-api-key":
        api_key, key_id = manager.generate_api_key(
            args.name,
            expires_days=args.expires_days
        )
        print("Generated API Key:")
        print(f"Key ID: {key_id}")
        print(f"API Key: {api_key}")
        print("💡 Store this key securely - it cannot be retrieved again!")

    elif args.command == "export":
        exported = manager.export_secrets_for_env(
            environment=args.environment,
            format=args.format
        )
        print(exported)

    elif args.command == "import-env":
        count = manager.import_secrets_from_env(prefix=args.prefix)
        print(f"✅ Imported {count} secrets from environment variables")

    elif args.command == "validate":
        results = manager.validate_secrets()
        print("Secrets Validation Results:")
        print(f"Total secrets: {results['total_secrets']}")
        print(f"Accessible secrets: {results['accessible_secrets']}")
        print(f"Expired secrets: {results['expired_count']}")
        print(f"Need rotation: {results['rotation_count']}")
        print(f"Health score: {results['health_score']:.1f}%")

        if results["expired_secrets"]:
            print(f"\nExpired secrets: {', '.join(results['expired_secrets'])}")
        if results["rotation_needed"]:
            print(f"\nRotation needed: {', '.join(results['rotation_needed'])}")

    elif args.command == "generate-key":
        new_key = Fernet.generate_key().decode()
        print(f"Generated master key: {new_key}")
        print(f"💡 Set environment variable: export LUKHAS_MASTER_KEY='{new_key}'")
