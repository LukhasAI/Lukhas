"""Glyph hashing utilities.

#REVIVED_25_07_2025

Provides symbolic glyph hashing and entropy delta computation.
"""

from __future__ import annotations

import hashlib
from typing import Optional


# ΛTAG: glyph_hash

def compute_glyph_hash(glyph: str, salt: Optional[str] = None) -> str:
    """Return SHA-256 hash for the given glyph with optional salt."""
    text = (salt or "") + glyph
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def entropy_delta(prev_hash: str, new_hash: str) -> float:
    """Simple Hamming distance between two hex digests normalized to [0,1]."""
    if len(prev_hash) != len(new_hash):
        raise ValueError("Hash lengths differ")
    distance = sum(ch1 != ch2 for ch1, ch2 in zip(prev_hash, new_hash))
    return distance / len(prev_hash)


__all__ = ["compute_glyph_hash", "entropy_delta"]
