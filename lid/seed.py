"""Seed phrase entropy validation."""
import math
from collections import Counter
from typing import Optional


class SeedEntropyError(Exception):
    """Raised when seed phrase entropy is too low."""
    pass


def compute_entropy(seed_phrase: str) -> float:
    """
    Compute Shannon entropy of seed phrase.

    Args:
        seed_phrase: Seed phrase to analyze

    Returns:
        Shannon entropy in bits
    """
    if not seed_phrase:
        return 0.0

    # Count character frequencies
    counter = Counter(seed_phrase)
    length = len(seed_phrase)

    # Compute Shannon entropy
    entropy = 0.0
    for count in counter.values():
        probability = count / length
        entropy -= probability * math.log2(probability)

    return entropy


def validate_seed_entropy(
    seed_phrase: str,
    min_entropy: float = 3.0,
    allow_low_entropy: bool = False
) -> tuple[bool, float, Optional[str]]:
    """
    Validate seed phrase entropy.

    Args:
        seed_phrase: Seed phrase to validate
        min_entropy: Minimum acceptable entropy (bits)
        allow_low_entropy: If True, warn but don't deny

    Returns:
        Tuple of (is_valid, entropy, warning_message)

    Raises:
        SeedEntropyError: If entropy too low and not allowed
    """
    entropy = compute_entropy(seed_phrase)

    if entropy < min_entropy:
        message = f"Seed entropy ({entropy:.2f} bits) below threshold ({min_entropy} bits)"

        if allow_low_entropy:
            return (True, entropy, message)  # Warn but allow
        else:
            raise SeedEntropyError(message)  # Deny

    return (True, entropy, None)


if __name__ == "__main__":
    print("=== Seed Phrase Entropy Checker Demo ===\n")

    test_seeds = [
        "correct horse battery staple",
        "aaaaaaaa",
        "12345678",
        "p@ssw0rd!SecurePhrase123"
    ]

    for seed in test_seeds:
        entropy = compute_entropy(seed)
        print(f"Seed: '{seed}'")
        print(f"  Entropy: {entropy:.2f} bits")

        try:
            valid, ent, warning = validate_seed_entropy(seed, min_entropy=3.5)
            if warning:
                print(f"  ⚠️  Warning: {warning}")
            else:
                print(f"  ✓ Valid")
        except SeedEntropyError as e:
            print(f"  ❌ Denied: {e}")

        print()
