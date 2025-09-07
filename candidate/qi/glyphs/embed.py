# path: qi/glyphs/embed.py
"""
GLYPH Seal Embedding

Embed and extract GLYPH seals in various media formats.
"""
from consciousness.qi import qi
from typing import Dict
import streamlit as st

from __future__ import annotations

import base64
import json
import re
import struct
import zlib
from typing import Any


# PNG chunk utilities
def _crc32(data: bytes) -> int:
    """Calculate CRC32 for PNG chunk."""
    return zlib.crc32(data) & 0xFFFFFFFF


def _make_png_chunk(chunk_type: bytes, data: bytes) -> bytes:
    """Create a PNG chunk."""
    length = struct.pack(">I", len(data))
    crc = struct.pack(">I", _crc32(chunk_type + data))
    return length + chunk_type + data + crc


def _parse_png_chunks(png_bytes: bytes) -> list[tuple[bytes, bytes]]:
    """Parse PNG chunks."""
    chunks = []
    if png_bytes[:8] != b"\x89PNG\r\n\x1a\n":
        return chunks

    pos = 8
    while pos < len(png_bytes):
        if pos + 8 > len(png_bytes):
            break

        length = struct.unpack(">I", png_bytes[pos : pos + 4])[0]
        pos += 4

        if pos + 4 + length + 4 > len(png_bytes):
            break

        chunk_type = png_bytes[pos : pos + 4]
        pos += 4

        data = png_bytes[pos : pos + length]
        pos += length

        # Skip CRC
        pos += 4

        chunks.append((chunk_type, data))

        if chunk_type == b"IEND":
            break

    return chunks


def embed_in_png(png_bytes: bytes, seal: dict[str, Any], sig: dict[str, Any]) -> bytes:
    """
    Embed GLYPH seal in PNG using iTXt chunk.

    Args:
        png_bytes: Original PNG data
        seal: Seal dictionary
        sig: Signature dictionary

    Returns:
        PNG with embedded seal
    """
    # Parse existing chunks
    chunks = _parse_png_chunks(png_bytes)
    if not chunks:
        raise ValueError("Invalid PNG data")

    # Create seal JSON
    seal_data = json.dumps({"seal": seal, "sig": sig}, separators=(",", ":"))

    # Create iTXt chunk
    # Format: keyword\0compression_flag\0compression_method\0language\0translated_keyword\0text
    keyword = b"lukhas.glyph"
    compression_flag = b"\x00"  # No compression
    compression_method = b"\x00"
    language = b""
    translated_keyword = b""
    text = seal_data.encode("utf-8")

    itxt_data = (
        keyword
        + b"\x00"
        + compression_flag
        + compression_method
        + language
        + b"\x00"
        + translated_keyword
        + b"\x00"
        + text
    )

    itxt_chunk = _make_png_chunk(b"iTXt", itxt_data)

    # Rebuild PNG with seal chunk before IEND
    result = b"\x89PNG\r\n\x1a\n"

    for chunk_type, data in chunks:
        if chunk_type == b"IEND":
            # Insert our chunk before IEND
            result += itxt_chunk

        # Recreate original chunk
        result += _make_png_chunk(chunk_type, data)

    return result


def extract_from_png(png_bytes: bytes) -> dict[str, Any] | None:
    """
    Extract GLYPH seal from png_itxt chunk.

    Args:
        png_bytes: PNG data

    Returns:
        Dict with 'seal' and 'sig' keys, or None if not found
    """
    chunks = _parse_png_chunks(png_bytes)

    for chunk_type, data in chunks:
        if chunk_type == b"iTXt":
            # Parse iTXt data
            parts = data.split(b"\x00", 5)
            if len(parts) >= 6:
                keyword = parts[0]
                if keyword == b"lukhas.glyph":
                    # Text is in the last part
                    text = parts[5].decode("utf-8")
                    try:
                        return json.loads(text)
                    except json.JSONDecodeError:
                        continue

    return None


def embed_in_text(text_bytes: bytes, seal: dict[str, Any], sig: dict[str, Any]) -> bytes:
    """
    Embed GLYPH seal in text using front-matter.

    Args:
        text_bytes: Original text data
        seal: Seal dictionary
        sig: Signature dictionary

    Returns:
        Text with embedded seal
    """
    # Create compact representation
    seal_data = {"seal": seal, "sig": sig}

    # Encode as base64 for clean embedding
    seal_b64 = base64.b64encode(json.dumps(seal_data, separators=(",", ":")).encode("utf-8")).decode("ascii")

    # Create front-matter block
    front_matter = f"""---
X-Lukhas-Glyph: {seal_b64}
---

"""

    return front_matter.encode("utf-8") + text_bytes


def extract_from_text(text_bytes: bytes) -> dict[str, Any] | None:
    """
    Extract GLYPH seal from text front-matter.

    Args:
        text_bytes: Text data

    Returns:
        Dict with 'seal' and 'sig' keys, or None if not found
    """
    try:
        text = text_bytes.decode("utf-8", errors="ignore")

        # Look for front-matter block
        match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
        if not match:
            return None

        front_matter = match.group(1)

        # Look for X-Lukhas-Glyph header
        glyph_match = re.search(r"^X-Lukhas-Glyph:\s*(.+)$", front_matter, re.MULTILINE)
        if not glyph_match:
            return None

        seal_b64 = glyph_match.group(1).strip()

        # Decode base64
        seal_json = base64.b64decode(seal_b64).decode("utf-8")
        return json.loads(seal_json)

    except Exception:
        return None


def embed_qr_data(seal: dict[str, Any], sig: dict[str, Any]) -> str:
    """
    Create compact QR-friendly representation.

    Uses base45 encoding for efficiency in QR codes.

    Args:
        seal: Seal dictionary
        sig: Signature dictionary

    Returns:
        Base45-encoded string suitable for QR codes
    """
    # Create minimal representation
    minimal = {
        "v": seal["v"],
        "h": seal["content_hash"][-16:],  # Last 16 chars of hash
        "i": seal["issuer"].replace("lukhas://org/", ""),
        "m": seal["model_id"],
        "j": seal["jurisdiction"],
        "p": seal["proof_bundle"],
        "n": seal["nonce"],
        "s": sig["signature"][-32:],  # Truncated signature for QR
    }

    # Convert to compact JSON
    compact = json.dumps(minimal, separators=(",", ":"))

    # Base45 encode (more efficient for QR than base64)
    # For now use base64 as base45 requires additional library
    return base64.b64encode(compact.encode("utf-8")).decode("ascii")


def parse_qr_data(qr_data: str) -> dict[str, Any] | None:
    """
    Parse QR code data back to seal components.

    Args:
        qr_data: Base45/64 encoded QR data

    Returns:
        Dict with minimal seal info, or None if invalid
    """
    try:
        # Decode base64 (would be base45 in production)
        compact = base64.b64decode(qr_data).decode("utf-8")
        minimal = json.loads(compact)

        # Reconstruct partial seal for verification
        return {
            "version": minimal["v"],
            "content_hash_suffix": minimal["h"],
            "issuer": f"lukhas://org/{minimal['i']}",
            "model_id": minimal["m"],
            "jurisdiction": minimal["j"],
            "proof_bundle": minimal["p"],
            "nonce": minimal["n"],
            "signature_suffix": minimal["s"],
        }
    except Exception:
        return None
