"""Glyph model with integrity hash."""
import base64
import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class Glyph:
    """Glyph with integrity verification."""

    symbol: str
    """The glyph symbol or identifier"""

    meaning: str
    """Semantic meaning"""

    properties: Dict[str, Any] = field(default_factory=dict)
    """Additional properties"""

    def to_canonical_json(self) -> str:
        """
        Convert to canonical JSON representation.

        Returns:
            Canonical JSON string (sorted keys, no whitespace)
        """
        data = {
            "symbol": self.symbol,
            "meaning": self.meaning,
            "properties": self.properties
        }
        return json.dumps(data, sort_keys=True, separators=(',', ':'))

    def hash(self) -> str:
        """
        Compute integrity hash over canonical JSON.

        Returns:
            Base64-encoded SHA256 hash
        """
        canonical = self.to_canonical_json()
        hash_bytes = hashlib.sha256(canonical.encode()).digest()
        return base64.b64encode(hash_bytes).decode()

    def verify_hash(self, expected_hash: str) -> bool:
        """
        Verify glyph integrity against expected hash.

        Args:
            expected_hash: Expected hash value

        Returns:
            True if hash matches
        """
        return self.hash() == expected_hash


if __name__ == "__main__":
    print("=== Glyph Integrity Hash Demo ===\n")

    glyph = Glyph(
        symbol="⚛",
        meaning="consciousness_core",
        properties={"attractor": 0.8, "repeller": 0.2}
    )

    print(f"Glyph: {glyph.symbol} ({glyph.meaning})")
    print(f"Canonical JSON: {glyph.to_canonical_json()}")

    hash_value = glyph.hash()
    print(f"Integrity hash: {hash_value}")

    # Verify
    print(f"Verification: {glyph.verify_hash(hash_value)}")

    # Modify and show hash changes
    glyph.properties["attractor"] = 0.9
    new_hash = glyph.hash()
    print(f"\nAfter modification: {new_hash}")
    print(f"Hashes match: {hash_value == new_hash}")
