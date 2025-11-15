#!/usr/bin/env python3
"""
Safe Serialization Module
==========================
Provides secure alternatives to pickle deserialization to prevent
arbitrary code execution vulnerabilities.

This module implements HMAC-signed pickle serialization for trusted
internal state and JSON-based serialization for simple data structures.

Security Features:
- HMAC signature verification to detect tampering
- JSON serialization for simple, safe data types
- Clear separation between trusted and untrusted data
- Comprehensive error handling and validation

Usage:
    from lukhas.security.safe_serialization import (
        secure_pickle_dumps,
        secure_pickle_loads,
        safe_json_serialize,
        safe_json_deserialize,
    )

    # For trusted internal state (with HMAC protection)
    data = {"key": "value"}
    serialized = secure_pickle_dumps(data)
    restored = secure_pickle_loads(serialized)

    # For simple data structures (preferred when possible)
    json_data = safe_json_serialize(data)
    restored = safe_json_deserialize(json_data)

Author: LUKHAS AI Security Team
Created: 2025-11-15
"""

import json
import pickle
import hmac
import hashlib
import os
from typing import Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class SerializationSecurityError(Exception):
    """Raised when serialization security validation fails."""
    pass


# Load secret key from environment (for HMAC)
# In production, this should be set via environment variable
# For development, we use a default key (should be changed in production)
_SECRET_KEY = os.environ.get('LUKHAS_SERIALIZATION_KEY', 'default-dev-key-change-in-production').encode()


def safe_json_serialize(obj: Any) -> bytes:
    """
    Safely serialize object to JSON.

    This is the preferred method for serializing simple data structures
    (dicts, lists, strings, numbers, booleans, None).

    Args:
        obj: Object to serialize (must be JSON-compatible)

    Returns:
        JSON bytes

    Raises:
        TypeError: If object is not JSON-serializable

    Example:
        >>> data = {"key": "value", "numbers": [1, 2, 3]}
        >>> serialized = safe_json_serialize(data)
        >>> # Store or transmit serialized data safely
    """
    try:
        json_str = json.dumps(obj, ensure_ascii=False, indent=None)
        return json_str.encode('utf-8')
    except TypeError as e:
        logger.error(f"Failed to serialize object to JSON: {e}")
        raise TypeError(f"Object is not JSON-serializable: {e}")


def safe_json_deserialize(data: bytes) -> Any:
    """
    Safely deserialize JSON data.

    Args:
        data: JSON bytes

    Returns:
        Deserialized object

    Raises:
        ValueError: If data is not valid JSON

    Example:
        >>> serialized = b'{"key": "value"}'
        >>> obj = safe_json_deserialize(serialized)
        >>> assert obj == {"key": "value"}
    """
    try:
        json_str = data.decode('utf-8')
        return json.loads(json_str)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        logger.error(f"Failed to deserialize JSON data: {e}")
        raise ValueError(f"Invalid JSON data: {e}")


def secure_pickle_dumps(obj: Any, key: Optional[bytes] = None) -> bytes:
    """
    Serialize object with HMAC signature for integrity verification.

    IMPORTANT: Use only for trusted internal storage, never for untrusted sources.
    The HMAC signature protects against tampering but does not prevent arbitrary
    code execution if the signature is bypassed or the key is compromised.

    The returned bytes format is:
        [32-byte HMAC-SHA256 signature][pickled data]

    Args:
        obj: Object to serialize
        key: HMAC key (defaults to environment key)

    Returns:
        Signed pickle bytes (signature + pickled data)

    Example:
        >>> data = {"complex": object()}
        >>> signed = secure_pickle_dumps(data)
        >>> restored = secure_pickle_loads(signed)
    """
    if key is None:
        key = _SECRET_KEY

    # Serialize using highest protocol for efficiency
    pickled = pickle.dumps(obj, protocol=pickle.HIGHEST_PROTOCOL)

    # Generate HMAC signature
    signature = hmac.new(key, pickled, hashlib.sha256).digest()

    logger.debug(f"Serialized object with HMAC (size: {len(pickled)} bytes, signature: {signature[:8].hex()}...)")

    # Return signature + data
    return signature + pickled


def secure_pickle_loads(data: bytes, key: Optional[bytes] = None) -> Any:
    """
    Deserialize HMAC-signed pickle data with verification.

    SECURITY: This function verifies the HMAC signature before deserializing.
    If the signature is invalid, it raises SerializationSecurityError.
    Only use this for data from trusted sources (internal storage).

    Args:
        data: Signed pickle bytes (signature + pickled data)
        key: HMAC key (defaults to environment key)

    Returns:
        Deserialized object

    Raises:
        ValueError: If data is too short to contain valid signature
        SerializationSecurityError: If signature verification fails

    Example:
        >>> signed = secure_pickle_dumps({"key": "value"})
        >>> obj = secure_pickle_loads(signed)
    """
    if key is None:
        key = _SECRET_KEY

    # Validate data length
    if len(data) < 32:
        raise ValueError("Data too short to contain valid signature (minimum 32 bytes required)")

    # Extract signature and pickled data
    signature = data[:32]
    pickled = data[32:]

    # Verify HMAC signature
    expected_sig = hmac.new(key, pickled, hashlib.sha256).digest()
    if not hmac.compare_digest(signature, expected_sig):
        logger.error("HMAC signature verification failed - possible tampering detected")
        raise SerializationSecurityError(
            "HMAC signature verification failed - data may be tampered or corrupted"
        )

    logger.debug(f"Deserializing verified pickle (size: {len(pickled)} bytes)")

    # Deserialize after successful verification
    return pickle.loads(pickled)


def save_secure_pickle(obj: Any, filepath: Path, key: Optional[bytes] = None) -> None:
    """
    Save object to file with HMAC signature.

    Args:
        obj: Object to save
        filepath: Path to output file
        key: HMAC key (defaults to environment key)

    Raises:
        IOError: If file cannot be written

    Example:
        >>> save_secure_pickle({"data": "value"}, Path("data.pkl"))
    """
    data = secure_pickle_dumps(obj, key)

    # Ensure parent directory exists
    filepath.parent.mkdir(parents=True, exist_ok=True)

    filepath.write_bytes(data)
    logger.info(f"Saved secure pickle to {filepath} ({len(data)} bytes)")


def load_secure_pickle(filepath: Path, key: Optional[bytes] = None) -> Any:
    """
    Load HMAC-signed pickle from file.

    Args:
        filepath: Path to input file
        key: HMAC key (defaults to environment key)

    Returns:
        Deserialized object

    Raises:
        FileNotFoundError: If file does not exist
        SerializationSecurityError: If signature verification fails

    Example:
        >>> obj = load_secure_pickle(Path("data.pkl"))
    """
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    data = filepath.read_bytes()
    obj = secure_pickle_loads(data, key)

    logger.info(f"Loaded secure pickle from {filepath} ({len(data)} bytes)")
    return obj


# Convenience functions for common use cases

def serialize_for_storage(obj: Any, prefer_json: bool = True) -> tuple[bytes, str]:
    """
    Intelligently serialize object, preferring JSON when possible.

    Args:
        obj: Object to serialize
        prefer_json: Try JSON first if True

    Returns:
        Tuple of (serialized_data, format_type)
        format_type is either "json" or "pickle"

    Example:
        >>> data, fmt = serialize_for_storage({"key": "value"})
        >>> assert fmt == "json"
    """
    if prefer_json:
        try:
            serialized = safe_json_serialize(obj)
            return serialized, "json"
        except TypeError:
            # Fall back to pickle for complex objects
            logger.debug("JSON serialization failed, falling back to secure pickle")
            serialized = secure_pickle_dumps(obj)
            return serialized, "pickle"
    else:
        serialized = secure_pickle_dumps(obj)
        return serialized, "pickle"


def deserialize_from_storage(data: bytes, format_type: str) -> Any:
    """
    Deserialize data based on format type.

    Args:
        data: Serialized data
        format_type: Either "json" or "pickle"

    Returns:
        Deserialized object

    Raises:
        ValueError: If format_type is unknown

    Example:
        >>> serialized, fmt = serialize_for_storage({"key": "value"})
        >>> obj = deserialize_from_storage(serialized, fmt)
    """
    if format_type == "json":
        return safe_json_deserialize(data)
    elif format_type == "pickle":
        return secure_pickle_loads(data)
    else:
        raise ValueError(f"Unknown format type: {format_type}")


# Module version and metadata
__version__ = "1.0.0"
__all__ = [
    'SerializationSecurityError',
    'safe_json_serialize',
    'safe_json_deserialize',
    'secure_pickle_dumps',
    'secure_pickle_loads',
    'save_secure_pickle',
    'load_secure_pickle',
    'serialize_for_storage',
    'deserialize_from_storage',
]


if __name__ == "__main__":
    # Basic self-test
    print("Testing safe_serialization module...")

    # Test JSON serialization
    test_data = {"key": "value", "numbers": [1, 2, 3]}
    json_bytes = safe_json_serialize(test_data)
    restored = safe_json_deserialize(json_bytes)
    assert restored == test_data, "JSON round-trip failed"
    print("✓ JSON serialization works")

    # Test secure pickle
    pickle_bytes = secure_pickle_dumps(test_data)
    restored = secure_pickle_loads(pickle_bytes)
    assert restored == test_data, "Pickle round-trip failed"
    print("✓ Secure pickle works")

    # Test tampering detection
    try:
        tampered = b'X' * 32 + pickle_bytes[32:]
        secure_pickle_loads(tampered)
        print("✗ Tampering detection FAILED")
    except SerializationSecurityError:
        print("✓ Tampering detection works")

    print("\nAll basic tests passed!")
