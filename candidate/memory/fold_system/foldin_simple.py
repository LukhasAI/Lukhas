#!/usr/bin/env python3
"""
Simple version of foldin without external dependencies
"""
import gzip
import json
import struct
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any

# Magic bytes for LKF-Pack format
MAGIC = b"LKF\x01"


async def import_folds(path: str) -> AsyncIterator[dict[str, Any]]:
    """Import memory folds from file"""
    path_obj = Path(path)

    with path_obj.open("rb") as f:
        # Read magic
        magic = f.read(4)
        if magic != MAGIC:
            raise ValueError(f"Invalid file format, expected {MAGIC}, got {magic}")

        # Read size
        size = struct.unpack(">I", f.read(4))[0]

        # Read compressed data
        compressed = f.read(size)

        # Decompress
        json_data = gzip.decompress(compressed)

        # Parse
        data = json.loads(json_data)

        # Yield folds
        for fold in data.get("folds", []):
            yield fold


def verify_lkf_pack(path: str) -> bool:
    """Verify LKF pack file"""
    try:
        path_obj = Path(path)
        with path_obj.open("rb") as f:
            magic = f.read(4)
            return magic == MAGIC
    except BaseException:
        return False
