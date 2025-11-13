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
    "DecryptionResult",
    "EncryptionAlgorithm",
    "EncryptionError",
    "EncryptionManager",
    "EncryptionResult",
    "KeyMetadata",
    "KeyType",
    "KeyUsage",
    "create_encryption_manager",
]

__version__ = "0.1.0"
