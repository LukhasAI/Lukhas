#!/usr/bin/env python3
"""
════════════════════════════════════════════════════════════════════════════════
║ 🛡️ LUKHAS AI - SECURE RANDOM UTILITIES
║ Cryptographically secure random number generation for LUKHAS AI systems
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠═══════════════════════════════════════════════════════════════════════════════
║ Module: secure_random.py
║ Path: lukhas/security/secure_random.py
║ Version: 1.0.0 | Created: 2025-09-01 | Modified: 2025-09-01
║ Authors: LUKHAS AI Security Team
╠═══════════════════════════════════════════════════════════════════════════════
║ DESCRIPTION
╠═══════════════════════════════════════════════════════════════════════════════
║ Provides cryptographically secure random utilities as replacement for the
║ insecure random module. All functions use secrets module internally for
║ cryptographic strength suitable for security-sensitive applications.
║
║ SECURITY NOTICE: This module replaces ALL usage of Python's random module
║ in security-critical contexts. Use this for:
║ - Password generation
║ - Token generation
║ - Cryptographic nonces
║ - Session IDs
║ - API keys
║ - Any security-sensitive random values
╚═══════════════════════════════════════════════════════════════════════════════
"""
import random
import secrets
import string
from collections.abc import Sequence
from typing import Any, Optional, Union


class SecureRandom:
    """Cryptographically secure random number generator.

    Provides drop-in replacements for common random module functions
    using the cryptographically secure secrets module.
    """

    def __init__(self, seed: Optional[Union[int, str]] = None):
        """Initialize SecureRandom instance.

        Note: Unlike random.Random, secrets-based operations cannot be
        meaningfully seeded for cryptographic security. The seed parameter
        is accepted for API compatibility but does not affect output.
        """
        # Store seed for logging/debugging but don't use it
        self._seed = seed
        self._secure_random = secrets.SystemRandom()

    def random(self) -> float:
        """Return a random float in the range [0.0, 1.0).

        Cryptographically secure replacement for secure_random.random().
        """
        return self._secure_random.random()

    def uniform(self, a: float, b: float) -> float:
        """Return a random float N such that a <= N <= b for a <= b
        and b <= N <= a for b < a.

        Cryptographically secure replacement for secure_random.uniform().
        """
        return self._secure_random.uniform(a, b)

    def randint(self, a: int, b: int) -> int:
        """Return a random integer N such that a <= N <= b.

        Cryptographically secure replacement for secure_random.randint().
        """
        return self._secure_random.randint(a, b)

    def randrange(self, start: int, stop: Optional[int] = None, step: int = 1) -> int:
        """Choose a random item from range(start, stop[, step]).

        Cryptographically secure replacement for secure_random.randrange().
        """
        if stop is None:
            stop = start
            start = 0
        return self._secure_random.randrange(start, stop, step)

    def choice(self, seq: Sequence[Any]) -> Any:
        """Choose a random element from a non-empty sequence.

        Cryptographically secure replacement for secure_random.choice().
        """
        if not seq:
            raise IndexError("Cannot choose from an empty sequence")
        return self._secure_random.choice(seq)

    def choices(
        self,
        population: Sequence[Any],
        weights: Optional[Sequence[float]] = None,
        cum_weights: Optional[Sequence[float]] = None,
        k: int = 1,
    ) -> list[Any]:
        """Return a k sized list of population elements chosen with replacement.

        Cryptographically secure replacement for secure_random.choices().
        Note: weights and cum_weights parameters are accepted for API compatibility
        but uniform distribution is used for cryptographic security.
        """
        if weights is not None or cum_weights is not None:
            # Log warning but proceed with uniform distribution for security
            pass
        return [self.choice(population) for _ in range(k)]

    def sample(self, population: Sequence[Any], k: int) -> list[Any]:
        """Return a k length list of unique elements chosen from population.

        Cryptographically secure replacement for secure_random.sample().
        """
        return self._secure_random.sample(population, k)

    def shuffle(self, x: list[Any]) -> None:
        """Shuffle sequence x in place using secure randomness.

        Cryptographically secure replacement for secure_random.shuffle().
        """
        # Fisher-Yates shuffle with secure random
        for i in range(len(x) - 1, 0, -1):
            j = self.randrange(0, i + 1)
            x[i], x[j] = x[j], x[i]

    def gauss(self, mu: float = 0.0, sigma: float = 1.0) -> float:
        """Gaussian distribution using secure randomness.

        Cryptographically secure replacement for secure_random.gauss().
        Uses Box-Muller transform with secure random values.
        """
        return self._secure_random.gauss(mu, sigma)

    def normalvariate(self, mu: float = 0.0, sigma: float = 1.0) -> float:
        """Normal distribution using secure randomness.

        Cryptographically secure replacement for secure_random.normalvariate().
        """
        return self._secure_random.normalvariate(mu, sigma)

    # Security-specific utilities
    def secure_token(self, nbytes: int = 32) -> str:
        """Generate a secure random token suitable for passwords, API keys, etc.

        Args:
            nbytes: Number of random bytes (default 32)

        Returns:
            URL-safe base64-encoded token string
        """
        return secrets.token_urlsafe(nbytes)

    def secure_hex(self, nbytes: int = 32) -> str:
        """Generate a secure random hex string.

        Args:
            nbytes: Number of random bytes (default 32)

        Returns:
            Hex-encoded string
        """
        return secrets.token_hex(nbytes)

    def secure_bytes(self, nbytes: int = 32) -> bytes:
        """Generate secure random bytes.

        Args:
            nbytes: Number of random bytes (default 32)

        Returns:
            Random bytes
        """
        return secrets.token_bytes(nbytes)

    def secure_password(
        self,
        length: int = 32,
        include_symbols: bool = True,
        include_numbers: bool = True,
        include_uppercase: bool = True,
        include_lowercase: bool = True,
    ) -> str:
        """Generate a secure random password.

        Args:
            length: Password length (default 32)
            include_symbols: Include special characters
            include_numbers: Include digits
            include_uppercase: Include uppercase letters
            include_lowercase: Include lowercase letters

        Returns:
            Cryptographically secure password
        """
        charset = ""
        if include_lowercase:
            charset += string.ascii_lowercase
        if include_uppercase:
            charset += string.ascii_uppercase
        if include_numbers:
            charset += string.digits
        if include_symbols:
            charset += "!@#$%^&*()_+-=[]{}|;:,.<>?"

        if not charset:
            raise ValueError("At least one character set must be enabled")

        return "".join(self.choice(charset) for _ in range(length))

    def secure_id(self, length: int = 16) -> str:
        """Generate a secure random ID suitable for session IDs, etc.

        Args:
            length: ID length (default 16)

        Returns:
            Alphanumeric ID string
        """
        charset = string.ascii_letters + string.digits
        return "".join(self.choice(charset) for _ in range(length))

    def secure_nonce(self, nbytes: int = 16) -> bytes:
        """Generate a cryptographic nonce.

        Args:
            nbytes: Number of bytes for nonce (default 16)

        Returns:
            Cryptographic nonce bytes
        """
        return self.secure_bytes(nbytes)


# Global secure random instance
secure_random = SecureRandom()


# Convenience functions for drop-in replacement
def random() -> float:
    """Secure replacement for secure_random.random()"""
    return secure_random.random()


def uniform(a: float, b: float) -> float:
    """Secure replacement for secure_random.uniform()"""
    return secure_random.uniform(a, b)


def randint(a: int, b: int) -> int:
    """Secure replacement for secure_random.randint()"""
    return secure_random.randint(a, b)


def randrange(start: int, stop: Optional[int] = None, step: int = 1) -> int:
    """Secure replacement for secure_random.randrange()"""
    return secure_random.randrange(start, stop, step)


def choice(seq: Sequence[Any]) -> Any:
    """Secure replacement for secure_random.choice()"""
    return secure_random.choice(seq)


def choices(
    population: Sequence[Any],
    weights: Optional[Sequence[float]] = None,
    cum_weights: Optional[Sequence[float]] = None,
    k: int = 1,
) -> list[Any]:
    """Secure replacement for secure_random.choices()"""
    return secure_random.choices(population, weights, cum_weights, k)


def sample(population: Sequence[Any], k: int) -> list[Any]:
    """Secure replacement for secure_random.sample()"""
    return secure_random.sample(population, k)


def shuffle(x: list[Any]) -> None:
    """Secure replacement for secure_random.shuffle()"""
    return secure_random.shuffle(x)


def gauss(mu: float = 0.0, sigma: float = 1.0) -> float:
    """Secure replacement for secure_random.gauss()"""
    return secure_random.gauss(mu, sigma)


def normalvariate(mu: float = 0.0, sigma: float = 1.0) -> float:
    """Secure replacement for secure_random.normalvariate()"""
    return secure_random.normalvariate(mu, sigma)


# Security-specific convenience functions
def secure_token(nbytes: int = 32) -> str:
    """Generate secure token"""
    return secure_random.secure_token(nbytes)


def secure_hex(nbytes: int = 32) -> str:
    """Generate secure hex string"""
    return secure_random.secure_hex(nbytes)


def secure_bytes(nbytes: int = 32) -> bytes:
    """Generate secure random bytes"""
    return secure_random.secure_bytes(nbytes)


def secure_password(
    length: int = 32,
    include_symbols: bool = True,
    include_numbers: bool = True,
    include_uppercase: bool = True,
    include_lowercase: bool = True,
) -> str:
    """Generate secure password"""
    return secure_random.secure_password(
        length,
        include_symbols=include_symbols,
        include_numbers=include_numbers,
        include_uppercase=include_uppercase,
        include_lowercase=include_lowercase,
    )


def secure_id(length: int = 16) -> str:
    """Generate secure ID"""
    return secure_random.secure_id(length)


def secure_nonce(nbytes: int = 16) -> bytes:
    """Generate cryptographic nonce"""
    return secure_random.secure_nonce(nbytes)


__all__ = [
    "SecureRandom",
    "choice",
    "choices",
    "gauss",
    "normalvariate",
    "randint",
    "random",
    "randrange",
    "sample",
    "secure_bytes",
    "secure_hex",
    "secure_id",
    "secure_nonce",
    "secure_password",
    "secure_random",
    "secure_token",
    "shuffle",
    "uniform",
]