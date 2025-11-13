#!/usr/bin/env python3
"""
Type-safe encryption algorithm definitions and metadata.

This module provides type-safe encryption algorithm selection and comprehensive
metadata for each supported algorithm. It prevents string typos and provides
algorithm-specific parameters for correct usage across the LUKHAS security system.

Key Features:
- Type-safe EncryptionAlgorithm enum
- Comprehensive AlgorithmMetadata for each algorithm
- Support for current and post-quantum algorithms
- Algorithm-specific parameters (key size, nonce size, tag size)
- Security level indicators
- Performance characteristics

Constellation Framework: 🛡️ Guardian Excellence - Encryption Types

Related Issues:
- #614: Define EncryptionAlgorithm Enum (P2 - PREREQUISITE for #613)

Example Usage:
    >>> from core.security.encryption_types import EncryptionAlgorithm, ALGORITHM_METADATA
    >>>
    >>> # Type-safe algorithm selection
    >>> algorithm = EncryptionAlgorithm.AES_256_GCM
    >>>
    >>> # Get algorithm metadata
    >>> metadata = ALGORITHM_METADATA[algorithm]
    >>> print(f"Key size: {metadata.key_size} bits")
    >>> print(f"Nonce size: {metadata.nonce_size} bytes")
    >>> print(f"Post-quantum resistant: {metadata.pq_resistant}")
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class EncryptionAlgorithm(str, Enum):
    """
    Type-safe encryption algorithm enumeration.

    Supported Algorithms:
    - AES_256_GCM: AES-256 in GCM mode (recommended for most use cases)
    - CHACHA20_POLY1305: ChaCha20-Poly1305 (excellent for mobile/embedded)
    - AES_256_CBC: AES-256 in CBC mode (legacy support)
    - KYBER768: Post-quantum KEM (future-ready, experimental)
    - KYBER1024: Post-quantum KEM with higher security (future-ready, experimental)

    All algorithms provide authenticated encryption (AEAD) except where noted.
    """

    # Current production algorithms
    AES_256_GCM = "aes-256-gcm"
    CHACHA20_POLY1305 = "chacha20-poly1305"

    # Legacy support (use with caution)
    AES_256_CBC = "aes-256-cbc"

    # Post-quantum ready (experimental)
    KYBER768 = "kyber768"
    KYBER1024 = "kyber1024"


class SecurityLevel(str, Enum):
    """Security level classification for algorithms."""

    LEGACY = "legacy"  # Deprecated, use only for backward compatibility
    STANDARD = "standard"  # Current industry standard
    HIGH = "high"  # High security, recommended for sensitive data
    POST_QUANTUM = "post-quantum"  # Quantum-resistant algorithms


@dataclass(frozen=True)
class AlgorithmMetadata:
    """
    Comprehensive metadata for encryption algorithms.

    Attributes:
        name: Human-readable algorithm name
        key_size: Key size in bits
        nonce_size: Nonce/IV size in bytes
        tag_size: Authentication tag size in bytes (for AEAD)
        block_size: Block size in bytes (None for stream ciphers)
        pq_resistant: Whether the algorithm is post-quantum resistant
        security_level: Security classification level
        aead: Whether this is an Authenticated Encryption with Associated Data algorithm
        recommended: Whether this algorithm is recommended for new implementations
        description: Brief description of the algorithm and use cases
        performance_tier: Relative performance (higher is faster)
    """

    name: str
    key_size: int  # bits
    nonce_size: int  # bytes
    tag_size: int  # bytes (for AEAD)
    block_size: int | None  # bytes (None for stream ciphers)
    pq_resistant: bool
    security_level: SecurityLevel
    aead: bool
    recommended: bool
    description: str
    performance_tier: int  # 1-5, where 5 is fastest


# Comprehensive algorithm metadata registry
ALGORITHM_METADATA: dict[EncryptionAlgorithm, AlgorithmMetadata] = {
    EncryptionAlgorithm.AES_256_GCM: AlgorithmMetadata(
        name="AES-256-GCM",
        key_size=256,
        nonce_size=12,  # 96 bits recommended for GCM
        tag_size=16,  # 128 bits
        block_size=16,  # 128-bit blocks
        pq_resistant=False,
        security_level=SecurityLevel.STANDARD,
        aead=True,
        recommended=True,
        description=(
            "AES-256 in Galois/Counter Mode. Provides authenticated encryption "
            "with excellent hardware acceleration on modern CPUs (AES-NI). "
            "Recommended for most use cases requiring strong security and performance."
        ),
        performance_tier=5,  # Excellent with hardware acceleration
    ),

    EncryptionAlgorithm.CHACHA20_POLY1305: AlgorithmMetadata(
        name="ChaCha20-Poly1305",
        key_size=256,
        nonce_size=12,  # 96 bits
        tag_size=16,  # 128 bits
        block_size=None,  # Stream cipher
        pq_resistant=False,
        security_level=SecurityLevel.STANDARD,
        aead=True,
        recommended=True,
        description=(
            "ChaCha20 stream cipher with Poly1305 MAC. Excellent performance "
            "on devices without AES hardware acceleration (mobile, IoT, embedded). "
            "Used by TLS 1.3 and modern protocols. Recommended for mobile and "
            "resource-constrained environments."
        ),
        performance_tier=4,  # Excellent software performance
    ),

    EncryptionAlgorithm.AES_256_CBC: AlgorithmMetadata(
        name="AES-256-CBC",
        key_size=256,
        nonce_size=16,  # 128-bit IV
        tag_size=0,  # No authentication (use HMAC separately)
        block_size=16,  # 128-bit blocks
        pq_resistant=False,
        security_level=SecurityLevel.LEGACY,
        aead=False,
        recommended=False,
        description=(
            "AES-256 in Cipher Block Chaining mode. Legacy algorithm without "
            "built-in authentication. Vulnerable to padding oracle attacks if "
            "not implemented carefully. Use AES-GCM instead for new implementations. "
            "Maintained only for backward compatibility."
        ),
        performance_tier=3,  # Good with hardware, but requires separate MAC
    ),

    EncryptionAlgorithm.KYBER768: AlgorithmMetadata(
        name="Kyber768",
        key_size=768,  # Equivalent classical security bits (approximate)
        nonce_size=32,  # Public key randomness
        tag_size=0,  # KEM operation (encapsulation provides integrity)
        block_size=None,  # Not applicable to KEMs
        pq_resistant=True,
        security_level=SecurityLevel.POST_QUANTUM,
        aead=False,  # KEM, not AEAD (use with symmetric AEAD)
        recommended=False,  # Experimental, awaiting NIST standardization
        description=(
            "CRYSTALS-Kyber768 post-quantum Key Encapsulation Mechanism (KEM). "
            "NIST PQC standard finalist providing security against quantum attacks. "
            "Use for key exchange, then use symmetric AEAD for data encryption. "
            "Security level roughly equivalent to AES-192. Currently experimental."
        ),
        performance_tier=2,  # Moderate performance, computationally intensive
    ),

    EncryptionAlgorithm.KYBER1024: AlgorithmMetadata(
        name="Kyber1024",
        key_size=1024,  # Equivalent classical security bits (approximate)
        nonce_size=32,  # Public key randomness
        tag_size=0,  # KEM operation
        block_size=None,  # Not applicable to KEMs
        pq_resistant=True,
        security_level=SecurityLevel.POST_QUANTUM,
        aead=False,  # KEM, not AEAD (use with symmetric AEAD)
        recommended=False,  # Experimental, awaiting NIST standardization
        description=(
            "CRYSTALS-Kyber1024 post-quantum Key Encapsulation Mechanism (KEM). "
            "Higher security variant providing security roughly equivalent to AES-256. "
            "Use for high-security applications requiring quantum resistance. "
            "Use for key exchange, then use symmetric AEAD for data encryption. "
            "Currently experimental."
        ),
        performance_tier=1,  # Lower performance due to larger parameters
    ),
}


def get_algorithm_metadata(algorithm: EncryptionAlgorithm) -> AlgorithmMetadata:
    """
    Get metadata for a specific encryption algorithm.

    Args:
        algorithm: The encryption algorithm to get metadata for

    Returns:
        AlgorithmMetadata for the specified algorithm

    Raises:
        KeyError: If the algorithm is not found in the metadata registry

    Example:
        >>> metadata = get_algorithm_metadata(EncryptionAlgorithm.AES_256_GCM)
        >>> print(f"Recommended: {metadata.recommended}")
    """
    return ALGORITHM_METADATA[algorithm]


def get_recommended_algorithms() -> list[EncryptionAlgorithm]:
    """
    Get list of recommended algorithms for new implementations.

    Returns:
        List of recommended EncryptionAlgorithm values

    Example:
        >>> recommended = get_recommended_algorithms()
        >>> print([algo.value for algo in recommended])
        ['aes-256-gcm', 'chacha20-poly1305']
    """
    return [
        algo
        for algo, metadata in ALGORITHM_METADATA.items()
        if metadata.recommended
    ]


def get_post_quantum_algorithms() -> list[EncryptionAlgorithm]:
    """
    Get list of post-quantum resistant algorithms.

    Returns:
        List of post-quantum EncryptionAlgorithm values

    Example:
        >>> pq_algos = get_post_quantum_algorithms()
        >>> print([algo.value for algo in pq_algos])
        ['kyber768', 'kyber1024']
    """
    return [
        algo
        for algo, metadata in ALGORITHM_METADATA.items()
        if metadata.pq_resistant
    ]


def is_aead_algorithm(algorithm: EncryptionAlgorithm) -> bool:
    """
    Check if an algorithm provides Authenticated Encryption with Associated Data.

    Args:
        algorithm: The encryption algorithm to check

    Returns:
        True if the algorithm is AEAD, False otherwise

    Example:
        >>> is_aead_algorithm(EncryptionAlgorithm.AES_256_GCM)
        True
        >>> is_aead_algorithm(EncryptionAlgorithm.AES_256_CBC)
        False
    """
    return ALGORITHM_METADATA[algorithm].aead


def validate_algorithm_choice(
    algorithm: EncryptionAlgorithm,
    require_aead: bool = True,
    allow_legacy: bool = False,
) -> tuple[bool, str | None]:
    """
    Validate an algorithm choice against security requirements.

    Args:
        algorithm: The algorithm to validate
        require_aead: Whether to require AEAD algorithms
        allow_legacy: Whether to allow legacy algorithms

    Returns:
        Tuple of (is_valid, error_message)
        If valid, error_message is None

    Example:
        >>> valid, error = validate_algorithm_choice(
        ...     EncryptionAlgorithm.AES_256_CBC,
        ...     require_aead=True,
        ...     allow_legacy=False
        ... )
        >>> print(valid)
        False
        >>> print(error)
        'Algorithm aes-256-cbc is not AEAD'
    """
    try:
        metadata = ALGORITHM_METADATA[algorithm]
    except KeyError:
        return False, f"Unknown algorithm: {algorithm.value}"

    # Check AEAD requirement
    if require_aead and not metadata.aead:
        return False, f"Algorithm {algorithm.value} is not AEAD"

    # Check legacy restriction
    if not allow_legacy and metadata.security_level == SecurityLevel.LEGACY:
        return (
            False,
            f"Algorithm {algorithm.value} is legacy and not recommended. "
            f"Use {get_recommended_algorithms()[0].value} instead."
        )

    return True, None


__all__ = [
    "ALGORITHM_METADATA",
    "AlgorithmMetadata",
    "EncryptionAlgorithm",
    "SecurityLevel",
    "get_algorithm_metadata",
    "get_post_quantum_algorithms",
    "get_recommended_algorithms",
    "is_aead_algorithm",
    "validate_algorithm_choice",
]
