# ΛTAG: api_validators

import hashlib
import os
import re
from typing import Optional


def validate_api_key(api_key: str) -> bool:
    """
    Validate the provided API key.

    Performs basic validation checks including format, length, and
    optional comparison against configured valid keys.

    Args:
        api_key: The API key to validate

    Returns:
        bool: True if the key passes validation, False otherwise
    """
    if not api_key or not isinstance(api_key, str):
        return False

    # Basic format validation
    api_key = api_key.strip()

    # Minimum length check (API keys should be sufficiently long)
    if len(api_key) < 16:
        return False

    # Maximum length check (prevent excessively long keys)
    if len(api_key) > 256:
        return False

    # Character set validation - allow alphanumeric and common API key chars
    if not re.match(r"^[a-zA-Z0-9_\-\.]+$", api_key):
        return False

    # Check against environment-configured valid keys if available
    valid_keys = _get_valid_api_keys()
    if valid_keys:
        # For security, compare hashes instead of plain text
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        return key_hash in valid_keys

    # If no specific keys configured, basic validation passed
    return True


def _get_valid_api_keys() -> Optional[set]:
    """
    Get valid API key hashes from environment configuration.

    Expects LUKHAS_API_KEY_HASHES environment variable with comma-separated
    SHA256 hashes of valid API keys.

    Returns:
        Set of valid API key hashes, or None if not configured
    """
    key_hashes_env = os.getenv("LUKHAS_API_KEY_HASHES")

    if not key_hashes_env:
        return None

    try:
        # Split comma-separated hashes and validate format
        hashes = set()
        for hash_str in key_hashes_env.split(","):
            hash_str = hash_str.strip()
            # Validate SHA256 hash format (64 hex characters)
            if re.match(r"^[a-fA-F0-9]{64}$", hash_str):
                hashes.add(hash_str.lower())

        return hashes if hashes else None

    except Exception:
        # If configuration is malformed, fall back to basic validation
        return None


def generate_api_key_hash(api_key: str) -> str:
    """
    Generate SHA256 hash of an API key for storage in configuration.

    Args:
        api_key: The plain text API key

    Returns:
        str: SHA256 hash of the API key
    """
    return hashlib.sha256(api_key.encode()).hexdigest()


def is_valid_api_key_format(api_key: str) -> bool:
    """
    Check if an API key meets basic format requirements without
    validating against configured keys.

    Args:
        api_key: The API key to check

    Returns:
        bool: True if format is valid, False otherwise
    """
    if not api_key or not isinstance(api_key, str):
        return False

    api_key = api_key.strip()

    # Length checks
    if not (16 <= len(api_key) <= 256):
        return False

    # Character set check
    if not re.match(r"^[a-zA-Z0-9_\-\.]+$", api_key):
        return False

    return True
