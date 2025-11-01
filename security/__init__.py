"""Security module public interface."""

from .encryption_manager import (
    DecryptionResult,
    EncryptionAlgorithm,
    EncryptionManager,
    EncryptionResult,
    EncryptionError,
    KeyMetadata,
    KeyType,
    KeyUsage,
    create_encryption_manager,
)

__all__ = [
    "create_encryption_manager",
    "EncryptionManager",
    "EncryptionAlgorithm",
    "EncryptionResult",
    "DecryptionResult",
    "EncryptionError",
    "KeyType",
    "KeyUsage",
    "KeyMetadata",
]

__version__ = "0.1.0"
