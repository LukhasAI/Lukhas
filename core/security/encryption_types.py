"""Encryption algorithm definitions and metadata for core security."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Iterable


class EncryptionAlgorithm(str, Enum):
    """Supported encryption algorithms for the core security module."""

    AES_256_GCM = "aes-256-gcm"
    CHACHA20_POLY1305 = "chacha20-poly1305"
    AES_256_CBC = "aes-256-cbc"

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.value


@dataclass(frozen=True)
class AlgorithmMetadata:
    """Metadata describing how to use an encryption algorithm."""

    key_size: int
    nonce_size: int
    tag_size: int
    is_aead: bool
    description: str


ALGORITHM_METADATA: Dict[EncryptionAlgorithm, AlgorithmMetadata] = {
    EncryptionAlgorithm.AES_256_GCM: AlgorithmMetadata(
        key_size=32,
        nonce_size=12,
        tag_size=16,
        is_aead=True,
        description="AES in Galois/Counter Mode with 256-bit keys",
    ),
    EncryptionAlgorithm.CHACHA20_POLY1305: AlgorithmMetadata(
        key_size=32,
        nonce_size=12,
        tag_size=16,
        is_aead=True,
        description="ChaCha20 stream cipher with Poly1305 authentication",
    ),
    EncryptionAlgorithm.AES_256_CBC: AlgorithmMetadata(
        key_size=32,
        nonce_size=16,
        tag_size=0,
        is_aead=False,
        description="AES in CBC mode without authentication",
    ),
}


def normalize_algorithm(value: EncryptionAlgorithm | str) -> EncryptionAlgorithm:
    """Return a canonical :class:`EncryptionAlgorithm` from ``value``."""

    if isinstance(value, EncryptionAlgorithm):
        return value
    try:
        return EncryptionAlgorithm(value.lower())
    except ValueError as exc:  # pragma: no cover - defensive programming
        raise ValueError(f"Unsupported encryption algorithm: {value!r}") from exc


def get_algorithm_metadata(algorithm: EncryptionAlgorithm | str) -> AlgorithmMetadata:
    """Return metadata for ``algorithm``.

    Parameters
    ----------
    algorithm:
        Either an :class:`EncryptionAlgorithm` instance or a string value
        corresponding to one of the enum members.
    """

    normalized = normalize_algorithm(algorithm)
    try:
        return ALGORITHM_METADATA[normalized]
    except KeyError as exc:  # pragma: no cover - defensive programming
        raise ValueError(f"Metadata not defined for algorithm: {normalized}") from exc


def validate_algorithm_choice(
    algorithm: EncryptionAlgorithm | str,
    *,
    require_aead: bool = False,
    allowed: Iterable[EncryptionAlgorithm] | None = None,
) -> EncryptionAlgorithm:
    """Validate that ``algorithm`` is supported.

    Parameters
    ----------
    algorithm:
        Algorithm to validate. Can be an enum member or its string value.
    require_aead:
        When ``True`` the function enforces that the algorithm offers
        authenticated encryption (AEAD).  A :class:`ValueError` is raised for
        non-AEAD algorithms.
    allowed:
        Optional iterable restricting the allowed algorithms. When provided the
        normalized algorithm must appear in the iterable.
    """

    normalized = normalize_algorithm(algorithm)
    if allowed is not None and normalized not in set(allowed):
        raise ValueError(f"Algorithm {normalized.value} is not permitted in this context")

    metadata = get_algorithm_metadata(normalized)
    if require_aead and not metadata.is_aead:
        raise ValueError(
            f"Algorithm {normalized.value} does not provide authenticated encryption"
        )
    return normalized
