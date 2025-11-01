"""
LUKHAS Core Security Module.

This module provides core security primitives and utilities for the LUKHAS system.
It includes type-safe encryption algorithm definitions, security utilities, and
foundational security infrastructure.

Constellation Framework: 🛡️ Guardian Excellence - Core Security
"""

from core.security.encryption_types import (
    ALGORITHM_METADATA,
    AlgorithmMetadata,
    EncryptionAlgorithm,
    SecurityLevel,
    get_algorithm_metadata,
    get_post_quantum_algorithms,
    get_recommended_algorithms,
    is_aead_algorithm,
    validate_algorithm_choice,
)

__all__ = [
    # Encryption types
    "EncryptionAlgorithm",
    "SecurityLevel",
    "AlgorithmMetadata",
    "ALGORITHM_METADATA",
    # Utility functions
    "get_algorithm_metadata",
    "get_recommended_algorithms",
    "get_post_quantum_algorithms",
    "is_aead_algorithm",
    "validate_algorithm_choice",
]
