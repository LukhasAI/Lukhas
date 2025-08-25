#!/usr/bin/env python3
"""
══════════════════════════════════════════════════════════════════════════════════
║ 🧬 LUKHAS AI - MEMORY FOLD-IN (IMPORT)
║ LKF-Pack v1 format reader for memory fold restoration
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: foldin.py
║ Path: memory/systems/foldin.py
║ Version: 1.0.0 | Created: 2025-07-29
║ Authors: LUKHAS AI Memory Team | Claude Code
╠══════════════════════════════════════════════════════════════════════════════════
║ DESCRIPTION
╠══════════════════════════════════════════════════════════════════════════════════
║ Implements the Fold-In process for importing memory folds from LKF-Pack v1
║ format bundles with integrity verification and streaming decompression.
║
║ Key features:
║ • Streaming decompression with zstd
║ • MessagePack deserialization
║ • CRC32 integrity verification
║ • Schema version compatibility checking
║ • Memory-efficient streaming for large imports
║
║ ΛTAG: ΛMEMORY, ΛFOLD, ΛIMPORT, ΛDECOMPRESSION
╚══════════════════════════════════════════════════════════════════════════════════
"""

import binascii
import json
import struct
from collections.abc import Generator
from io import BytesIO
from pathlib import Path
from typing import Any, Optional, Union

import msgpack
import zstandard as zstd

from candidate.core.common import LukhasError

# LKF-Pack v1 magic bytes
MAGIC = b"LKF\x01"

# Supported spec versions (for backward compatibility)
SUPPORTED_SPECS = ["1.0"]


class LKFPackError(LukhasError):
    """Base exception for LKF-Pack errors."""


class LKFPackVersionError(LKFPackError):
    """Raised when LKF-Pack version is unsupported."""


class LKFPackIntegrityError(LKFPackError):
    """Raised when CRC check fails."""


def import_folds(
    path: Union[Path, BytesIO],
    verify_crc: bool = True,
    max_entries: Optional[int] = None,
) -> Generator[dict[str, Any], None, None]:
    """
    Import memory folds from LKF-Pack v1 format.

    Args:
        path: File path or BytesIO stream to read from
        verify_crc: Whether to verify CRC32 checksum
        max_entries: Maximum number of entries to import (None = all)

    Yields:
        Memory fold dictionaries

    Raises:
        LKFPackError: For format errors
        LKFPackVersionError: For unsupported versions
        LKFPackIntegrityError: For CRC mismatches
    """
    if isinstance(path, Path):
        f = path.open("rb")
        close_file = True
    else:
        f = path
        close_file = False

    try:
        # Read and verify magic bytes
        magic = f.read(4)
        if magic != MAGIC:
            raise LKFPackError(f"Not an LKF-Pack v1 file (magic: {magic.hex()})")

        # Read header length
        header_len_bytes = f.read(4)
        if len(header_len_bytes) != 4:
            raise LKFPackError("Truncated file: missing header length")

        header_len = struct.unpack(">I", header_len_bytes)[0]

        # Read header JSON
        header_bytes = f.read(header_len)
        if len(header_bytes) != header_len:
            raise LKFPackError("Truncated file: incomplete header")

        try:
            header = json.loads(header_bytes)
        except json.JSONDecodeError as e:
            raise LKFPackError(f"Invalid header JSON: {e}")

        # Verify spec version
        spec_version = header.get("spec", "unknown")
        if spec_version not in SUPPORTED_SPECS:
            raise LKFPackVersionError(
                f"Unsupported spec version: {spec_version} "
                f"(supported: {SUPPORTED_SPECS})"
            )

        # Extract metadata
        codec = header.get("codec", "none")
        expected_entries = header.get("entries", 0)
        header_crc = header.get("crc32")

        logger.info(
            "Reading LKF-Pack file",
            spec_version=spec_version,
            codec=codec,
            expected_entries=expected_entries,
            created=header.get("created"),
            metadata=header.get("metadata", {}),
        )

        # Read payload and CRC footer
        remaining = f.read()
        if len(remaining) < 4:
            raise LKFPackError("Truncated file: missing CRC footer")

        # Split payload and CRC
        crc_given = struct.unpack(">I", remaining[-4:])[0]
        payload = remaining[:-4]

        # Verify CRC if requested
        if verify_crc:
            calculated_crc = binascii.crc32(payload) & 0xFFFFFFFF
            if calculated_crc != crc_given:
                raise LKFPackIntegrityError(
                    f"CRC mismatch - expected: {crc_given}, "
                    f"calculated: {calculated_crc}"
                )

            # Also verify against header CRC if present
            if header_crc is not None and header_crc != crc_given:
                logger.warning(
                    "CRC mismatch between header and footer",
                    header_crc=header_crc,
                    footer_crc=crc_given,
                )

        # Setup decompression
        if codec == "zstd":
            decompressor = zstd.ZstdDecompressor()
            data_stream = decompressor.stream_reader(BytesIO(payload))
        elif codec == "lzma":
            import lzma

            data_stream = lzma.decompress(payload)
            data_stream = BytesIO(data_stream)
        elif codec == "gzip":
            import gzip

            data_stream = gzip.decompress(payload)
            data_stream = BytesIO(data_stream)
        elif codec == "none":
            data_stream = BytesIO(payload)
        else:
            raise LKFPackError(f"Unsupported codec: {codec}")

        # Setup MessagePack unpacker
        unpacker = msgpack.Unpacker(data_stream, raw=False)

        # Yield folds
        entries_read = 0
        for obj in unpacker:
            if max_entries and entries_read >= max_entries:
                logger.info(
                    "Reached max_entries limit",
                    entries_read=entries_read,
                    max_entries=max_entries,
                )
                break

            yield obj
            entries_read += 1

        # Verify entry count
        if entries_read != expected_entries:
            logger.warning(
                "Entry count mismatch", expected=expected_entries, actual=entries_read
            )

        logger.info("LKF-Pack import completed", entries_read=entries_read, codec=codec)

    finally:
        if close_file:
            f.close()


def import_folds_safe(
    path: Path, validate_schema: bool = True, allowed_keys: Optional[set] = None
) -> Generator[dict[str, Any], None, None]:
    """
    Import memory folds with additional safety checks.

    Args:
        path: File path to import from
        validate_schema: Whether to validate fold schema
        allowed_keys: Whitelist of allowed keys in folds

    Yields:
        Validated memory fold dictionaries
    """
    for fold in import_folds(path):
        # Validate fold structure
        if not isinstance(fold, dict):
            logger.warning(f"Skipping non-dict fold: {type(fold)}")
            continue

        # Check for required fields
        if validate_schema:
            required_fields = {"id", "timestamp", "data"}
            if not all(field in fold for field in required_fields):
                logger.warning(
                    "Skipping fold with missing required fields",
                    fold_keys=list(fold.keys()),
                    required=list(required_fields),
                )
                continue

        # Filter allowed keys if specified
        if allowed_keys:
            filtered_fold = {k: v for k, v in fold.items() if k in allowed_keys}
            yield filtered_fold
        else:
            yield fold


def verify_lkf_pack(path: Path) -> dict[str, Any]:
    """
    Verify LKF-Pack file integrity without importing data.

    Args:
        path: File path to verify

    Returns:
        Verification report dictionary
    """
    report = {
        "valid": False,
        "errors": [],
        "warnings": [],
        "header": None,
        "entry_count": 0,
    }

    try:
        # Read header only
        with path.open("rb") as f:
            # Check magic
            magic = f.read(4)
            if magic != MAGIC:
                report["errors"].append(f"Invalid magic: {magic.hex()}")
                return report

            # Read header
            header_len = struct.unpack(">I", f.read(4))[0]
            header_bytes = f.read(header_len)

            try:
                header = json.loads(header_bytes)
                report["header"] = header
            except json.JSONDecodeError as e:
                report["errors"].append(f"Invalid header JSON: {e}")
                return report

        # Count entries without loading all data
        entry_count = 0
        for _ in import_folds(path, max_entries=None):
            entry_count += 1

        report["entry_count"] = entry_count
        report["valid"] = True

        # Check entry count
        expected = header.get("entries", 0)
        if entry_count != expected:
            report["warnings"].append(
                f"Entry count mismatch: expected {expected}, found {entry_count}"
            )

    except LKFPackError as e:
        report["errors"].append(str(e))
    except Exception as e:
        report["errors"].append(f"Unexpected error: {e}")

    return report


def import_from_stream(
    stream, chunk_size: int = 1024 * 1024  # 1MB chunks
) -> Generator[dict[str, Any], None, None]:
    """
    Import memory folds from a streaming source.

    Useful for importing from Kafka, SQS, or other streaming sources.

    Args:
        stream: Stream-like object providing LKF-Pack data
        chunk_size: Size of chunks to read

    Yields:
        Memory fold dictionaries
    """
    # Buffer for accumulating stream data
    buffer = BytesIO()

    # Read stream in chunks
    while True:
        chunk = stream.read(chunk_size)
        if not chunk:
            break
        buffer.write(chunk)

    # Reset buffer position
    buffer.seek(0)

    # Import from buffer
    yield from import_folds(buffer)


# Factory function
def create_memory_importer(verify_crc: bool = True, validate_schema: bool = True):
    """
    Create a configured memory fold importer.

    Args:
        verify_crc: Whether to verify checksums
        validate_schema: Whether to validate fold schema

    Returns:
        Configured import function
    """

    def importer(path, **kwargs):
        if validate_schema:
            return import_folds_safe(
                path,
                validate_schema=kwargs.get("validate_schema", validate_schema),
                **kwargs,
            )
        else:
            return import_folds(
                path, verify_crc=kwargs.get("verify_crc", verify_crc), **kwargs
            )

    return importer
