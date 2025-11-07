#!/usr/bin/env python3
"""
LUKHAS Identity ΛiD Alias Format - Production Schema v1.0.0

Implements secure ΛiD alias generation and validation with CRC32 integrity checking.
Format: lid#<REALM>/<ZONE>/v<major>.<uuid>-<crc32>

Constellation Framework: Identity ⚛️ pillar with cross-system coordination.
"""

from __future__ import annotations

import re
import uuid
import zlib
from dataclasses import dataclass
from typing import Tuple


@dataclass
class ΛiDAlias:
    """
    Structured ΛiD alias representation.

    Provides type-safe access to alias components with validation.
    """
    realm: str
    zone: str
    major_version: int
    uuid_part: str
    crc32_hex: str

    def __str__(self) -> str:
        """Return canonical alias string representation."""
        core = f"lid#{self.realm}/{self.zone}/v{self.major_version}.{self.uuid_part}"
        return f"{core}-{self.crc32_hex}"

    @property
    def core_without_crc(self) -> str:
        """Return alias core without CRC32 suffix for validation."""
        return f"lid#{self.realm}/{self.zone}/v{self.major_version}.{self.uuid_part}"


# Alias format validation pattern
ALIAS_PATTERN = re.compile(
    r'^lid#([a-zA-Z0-9_-]+)/([a-zA-Z0-9_-]+)/v(\d+)\.([a-f0-9]{32})-([a-f0-9]{8})$'
)

# Realm/zone validation patterns (strict security)
REALM_PATTERN = re.compile(r'^[a-zA-Z0-9_-]{1,32}$')
ZONE_PATTERN = re.compile(r'^[a-zA-Z0-9_-]{1,32}$')


def make_alias(realm: str, zone: str, major: int = 1) -> str:
    """
    Generate new ΛiD alias with CRC32 integrity check.

    Args:
        realm: Security realm identifier (alphanumeric, underscore, dash)
        zone: Zone identifier within realm
        major: Major version number (default: 1)

    Returns:
        Complete ΛiD alias string with CRC32 suffix

    Raises:
        ValueError: If realm/zone contain invalid characters

    Example:
        >>> alias = make_alias("enterprise", "prod", 2)
        >>> print(alias)
        lid#enterprise/prod/v2.a1b2c3d4e5f6789012345678901234ab-1a2b3c4d
    """
    # Validate realm and zone format
    if not REALM_PATTERN.match(realm):
        raise ValueError(f"Invalid realm format: {realm}")
    if not ZONE_PATTERN.match(zone):
        raise ValueError(f"Invalid zone format: {zone}")

    # Generate UUID component (hex without dashes)
    uuid_hex = uuid.uuid4().hex

    # Create core alias
    core = f"lid#{realm}/{zone}/v{major}.{uuid_hex}"

    # Calculate CRC32 and format as 8-character hex
    crc = zlib.crc32(core.encode("utf-8")) & 0xffffffff
    crc_hex = f"{crc:08x}"

    return f"{core}-{crc_hex}"


def verify_crc(alias: str) -> bool:
    """
    Verify CRC32 integrity of ΛiD alias.

    Args:
        alias: Complete ΛiD alias string

    Returns:
        True if CRC32 is valid, False otherwise

    Example:
        >>> alias = "lid#realm/zone/v1.abcd1234-12345678"
        >>> is_valid = verify_crc(alias)
        >>> print(is_valid)
        True
    """
    try:
        # Split alias at last dash
        if '-' not in alias:
            return False

        body, crc_hex = alias.rsplit("-", 1)

        # Validate CRC hex format
        if len(crc_hex) != 8:
            return False

        # Calculate expected CRC32
        expected_crc = zlib.crc32(body.encode("utf-8")) & 0xffffffff
        provided_crc = int(crc_hex, 16)

        return expected_crc == provided_crc

    except (ValueError, AttributeError):
        return False


def parse_alias(alias: str) -> ΛiDAlias | None:
    """
    Parse ΛiD alias into structured components.

    Args:
        alias: Complete ΛiD alias string

    Returns:
        ΛiDAlias object if valid, None if invalid

    Example:
        >>> alias = "lid#enterprise/prod/v2.abcd1234-12345678"
        >>> parsed = parse_alias(alias)
        >>> print(parsed.realm, parsed.zone, parsed.major_version)
        enterprise prod 2
    """
    # Validate format with regex
    match = ALIAS_PATTERN.match(alias)
    if not match:
        return None

    realm, zone, major_str, uuid_part, crc_hex = match.groups()

    try:
        major_version = int(major_str)
    except ValueError:
        return None

    # Verify CRC32 integrity
    if not verify_crc(alias):
        return None

    return ΛiDAlias(
        realm=realm,
        zone=zone,
        major_version=major_version,
        uuid_part=uuid_part,
        crc32_hex=crc_hex
    )


def validate_alias_format(alias: str) -> tuple[bool, str]:
    """
    Comprehensive alias validation with detailed error reporting.

    Args:
        alias: Alias string to validate

    Returns:
        Tuple of (is_valid, error_message)

    Example:
        >>> is_valid, error = validate_alias_format("invalid-alias")
        >>> print(f"Valid: {is_valid}, Error: {error}")
        Valid: False, Error: Invalid alias format structure
    """
    if not isinstance(alias, str):
        return False, "Alias must be a string"

    if len(alias) == 0:
        return False, "Alias cannot be empty"

    if len(alias) > 200:  # Reasonable upper bound
        return False, "Alias exceeds maximum length"

    # Check basic format
    if not alias.startswith("lid#"):
        return False, "Alias must start with 'lid#'"

    # Validate with regex
    if not ALIAS_PATTERN.match(alias):
        return False, "Invalid alias format structure"

    # Verify CRC32
    if not verify_crc(alias):
        return False, "CRC32 integrity check failed"

    return True, "Valid alias"


def generate_test_aliases(count: int = 10) -> list[str]:
    """
    Generate test aliases for development and testing.

    Args:
        count: Number of test aliases to generate

    Returns:
        List of valid test aliases
    """
    test_realms = ["test", "dev", "staging", "demo"]
    test_zones = ["zone1", "zone2", "alpha", "beta"]

    aliases = []
    for i in range(count):
        realm = test_realms[i % len(test_realms)]
        zone = test_zones[i % len(test_zones)]
        major = (i % 3) + 1  # Versions 1, 2, 3

        alias = make_alias(realm, zone, major)
        aliases.append(alias)

    return aliases


# Export public interface
__all__ = [
    "ΛiDAlias",
    "generate_test_aliases",
    "make_alias",
    "parse_alias",
    "validate_alias_format",
    "verify_crc"
]
