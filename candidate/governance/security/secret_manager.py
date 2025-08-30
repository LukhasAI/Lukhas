#!/usr/bin/env python3
"""
LUKHAS Secret Management System
==============================
Centralized, secure secret management to eliminate hardcoded secrets.

This system addresses the 289 hardcoded secrets identified in the security audit
by providing a unified, secure way to handle all sensitive data.
"""

import base64
import json
import logging
import os
import secrets
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = logging.getLogger(__name__)


class SecretType(Enum):
    """Types of secrets managed by the system"""

    API_KEY = "api_key"
    DATABASE_URL = "database_url"
    ENCRYPTION_KEY = "encryption_key"
    JWT_SECRET = "jwt_secret"
    OAUTH_SECRET = "oauth_secret"
    WEBHOOK_SECRET = "webhook_secret"
    SERVICE_ACCOUNT = "service_account"
    CERTIFICATE = "certificate"


@dataclass
class SecretMetadata:
    """Metadata for a managed secret"""

    name: str
    secret_type: SecretType
    description: str
    rotation_days: int = 90
    created_at: str = None
    last_rotated: str = None
    environment: str = "production"


class SecretManager:
    """
    Secure secret management system for LUKHAS

    Features:
    - Environment variable integration
    - Encrypted local storage for development
    - Secret rotation support
    - Audit logging
    - Multiple environment support
    """

    def __init__(self, environment: str = None):
        self.environment = environment or os.getenv("LUKHAS_ENV", "development")
        self.secrets_cache = {}
        self._encryption_key = None
        self._initialize_encryption()

        # Load secrets configuration
        self._load_secret_registry()

        logger.info(f"SecretManager initialized for environment: {self.environment}")

    def _initialize_encryption(self):
        """Initialize encryption for local secret storage"""
        # Use a key derived from system-specific data
        master_key = os.getenv("LUKHAS_MASTER_KEY")
        if not master_key:
            # Generate a warning for production
            if self.environment == "production":
                logger.error("LUKHAS_MASTER_KEY not set in production environment!")
                raise ValueError("Master key required for production")

            # Use a derived key for development
            system_info = f"{os.getenv('USER', 'lukhas')}-{Path.home()}"
            master_key = base64.b64encode(system_info.encode()).decode()

        # Derive encryption key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"lukhas_secret_salt_v1",
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_key.encode()))
        self._encryption_key = Fernet(key)

    def _load_secret_registry(self):
        """Load the registry of managed secrets"""
        self.secret_registry = {
            "openai_api_key": SecretMetadata(
                name="openai_api_key",
                secret_type=SecretType.API_KEY,
                description="OpenAI API key for AI operations",
                rotation_days=30,
            ),
            "anthropic_api_key": SecretMetadata(
                name="anthropic_api_key",
                secret_type=SecretType.API_KEY,
                description="Anthropic API key for Claude operations",
            ),
            "lukhas_jwt_secret": SecretMetadata(
                name="lukhas_jwt_secret",
                secret_type=SecretType.JWT_SECRET,
                description="JWT signing secret for authentication",
            ),
            "database_url": SecretMetadata(
                name="database_url",
                secret_type=SecretType.DATABASE_URL,
                description="Database connection string",
            ),
            "lambda_id_encryption_key": SecretMetadata(
                name="lambda_id_encryption_key",
                secret_type=SecretType.ENCRYPTION_KEY,
                description="Encryption key for ΛiD system",
            ),
            "webhook_secret": SecretMetadata(
                name="webhook_secret",
                secret_type=SecretType.WEBHOOK_SECRET,
                description="Secret for webhook validation",
            ),
        }

    def get_secret(self, secret_name: str, default: str = None) -> Optional[str]:
        """
        Get a secret value securely

        Priority order:
        1. Environment variable
        2. Encrypted local storage
        3. Default value (only for non-production)
        """
        # Check cache first
        if secret_name in self.secrets_cache:
            return self.secrets_cache[secret_name]

        # Try environment variable first
        env_value = os.getenv(secret_name.upper())
        if env_value:
            self.secrets_cache[secret_name] = env_value
            return env_value

        # Try alternative environment variable patterns
        alt_patterns = [
            f"LUKHAS_{secret_name.upper()}",
            secret_name,
            secret_name.replace("_", "-").upper(),
        ]

        for pattern in alt_patterns:
            env_value = os.getenv(pattern)
            if env_value:
                self.secrets_cache[secret_name] = env_value
                return env_value

        # Try encrypted local storage
        local_value = self._get_local_secret(secret_name)
        if local_value:
            self.secrets_cache[secret_name] = local_value
            return local_value

        # Return default only in non-production environments
        if default and self.environment != "production":
            logger.warning(f"Using default value for secret: {secret_name}")
            return default

        # No secret found
        logger.error(f"Secret not found: {secret_name}")
        return None

    def set_secret(self, secret_name: str, value: str, metadata: SecretMetadata = None):
        """Set a secret value securely"""
        if not value:
            raise ValueError("Secret value cannot be empty")

        # Store in cache
        self.secrets_cache[secret_name] = value

        # Store encrypted locally for development
        if self.environment == "development":
            self._set_local_secret(secret_name, value)

        # Register metadata if provided
        if metadata:
            self.secret_registry[secret_name] = metadata

        logger.info(f"Secret set: {secret_name}")

    def _get_local_secret(self, secret_name: str) -> Optional[str]:
        """Get secret from encrypted local storage"""
        try:
            secrets_file = Path.home() / ".lukhas" / "secrets.enc"
            if not secrets_file.exists():
                return None

            encrypted_data = secrets_file.read_bytes()
            decrypted_data = self._encryption_key.decrypt(encrypted_data)
            secrets_dict = json.loads(decrypted_data.decode())

            return secrets_dict.get(secret_name)
        except Exception as e:
            logger.debug(f"Failed to read local secret {secret_name}: {e}")
            return None

    def _set_local_secret(self, secret_name: str, value: str):
        """Store secret in encrypted local storage"""
        try:
            secrets_dir = Path.home() / ".lukhas"
            secrets_dir.mkdir(exist_ok=True)
            secrets_file = secrets_dir / "secrets.enc"

            # Load existing secrets
            secrets_dict = {}
            if secrets_file.exists():
                try:
                    encrypted_data = secrets_file.read_bytes()
                    decrypted_data = self._encryption_key.decrypt(encrypted_data)
                    secrets_dict = json.loads(decrypted_data.decode())
                except Exception:
                    logger.warning("Failed to decrypt existing secrets, creating new file")

            # Update with new secret
            secrets_dict[secret_name] = value

            # Encrypt and save
            data_to_encrypt = json.dumps(secrets_dict).encode()
            encrypted_data = self._encryption_key.encrypt(data_to_encrypt)
            secrets_file.write_bytes(encrypted_data)

            # Set restrictive permissions
            secrets_file.chmod(0o600)

        except Exception as e:
            logger.error(f"Failed to store local secret {secret_name}: {e}")

    def generate_secret(self, secret_name: str, length: int = 32) -> str:
        """Generate a new random secret"""
        secret_value = secrets.token_urlsafe(length)
        self.set_secret(secret_name, secret_value)
        return secret_value

    def list_secrets(self) -> dict[str, SecretMetadata]:
        """List all registered secrets and their metadata"""
        return self.secret_registry.copy()

    def validate_secrets(self) -> dict[str, bool]:
        """Validate that all required secrets are available"""
        validation_results = {}

        for secret_name, _metadata in self.secret_registry.items():
            secret_value = self.get_secret(secret_name)
            validation_results[secret_name] = secret_value is not None

            if not secret_value:
                logger.warning(f"Missing required secret: {secret_name}")

        return validation_results

    def audit_secrets_usage(self) -> dict[str, Any]:
        """Generate an audit report of secrets usage"""
        return {
            "environment": self.environment,
            "registered_secrets": len(self.secret_registry),
            "cached_secrets": len(self.secrets_cache),
            "validation_results": self.validate_secrets(),
            "encryption_enabled": self._encryption_key is not None,
        }


# Global secret manager instance
_secret_manager = None


def get_secret_manager() -> SecretManager:
    """Get the global secret manager instance"""
    global _secret_manager
    if _secret_manager is None:
        _secret_manager = SecretManager()
    return _secret_manager


def get_secret(secret_name: str, default: str = None) -> Optional[str]:
    """Convenience function to get a secret"""
    return get_secret_manager().get_secret(secret_name, default)


def set_secret(secret_name: str, value: str):
    """Convenience function to set a secret"""
    get_secret_manager().set_secret(secret_name, value)


class SecureConfig:
    """
    Configuration class that automatically uses SecretManager for sensitive values

    Usage:
        config = SecureConfig({
            "api_key": "SECURE:openai_api_key",
            "database_url": "SECURE:database_url",
            "debug": True
        })
    """

    def __init__(self, config_dict: dict[str, Any]):
        self.secret_manager = get_secret_manager()
        self._config = {}

        for key, value in config_dict.items():
            if isinstance(value, str) and value.startswith("SECURE:"):
                # This is a secret reference
                secret_name = value[7:]  # Remove "SECURE:" prefix
                secret_value = self.secret_manager.get_secret(secret_name)
                if secret_value is None:
                    raise ValueError(f"Required secret not found: {secret_name}")
                self._config[key] = secret_value
            else:
                self._config[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value"""
        return self._config.get(key, default)

    def __getitem__(self, key: str) -> Any:
        return self._config[key]

    def __contains__(self, key: str) -> bool:
        return key in self._config


def main():
    """Demo the secret management system"""
    print("🔐 LUKHAS Secret Management System")
    print("=" * 40)

    # Initialize secret manager
    secret_manager = get_secret_manager()

    # Show audit report
    audit = secret_manager.audit_secrets_usage()
    print("\n📊 Security Audit:")
    print(f"Environment: {audit['environment']}")
    print(f"Registered secrets: {audit['registered_secrets']}")
    print("Validation results:")
    for secret_name, is_valid in audit["validation_results"].items():
        status = "✅" if is_valid else "❌"
        print(f"  {status} {secret_name}")

    # Demo secure configuration
    print("\n🛡️ Secure Configuration Example:")
    try:
        SecureConfig(
            {
                "api_key": "SECURE:openai_api_key",  # Will try to get from env/storage
                "debug": True,
                "timeout": 30,
            }
        )
        print("✅ Configuration loaded successfully")
    except ValueError as e:
        print(f"❌ Configuration error: {e}")

    print("\n💡 To fix hardcoded secrets:")
    print("1. Set environment variables: export OPENAI_API_KEY='your-key'")
    print("2. Use get_secret() function instead of hardcoded values")
    print("3. Use SecureConfig class for configuration management")


if __name__ == "__main__":
    main()
