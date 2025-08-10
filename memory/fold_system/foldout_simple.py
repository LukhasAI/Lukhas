#!/usr/bin/env python3
"""
Simple version of foldout without external dependencies
"""

import asyncio
import binascii
import gzip
import json
import struct
from collections.abc import Iterable
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

# Magic bytes for LKF-Pack format
MAGIC = b"LKF\x01"


async def export_folds(
    folds: Iterable[Dict[str, Any]], path: str, codec: str = "gzip"
) -> Dict[str, Any]:
    """Export memory folds using built-in compression"""

    # Convert to list to count
    folds_list = list(folds)

    # Prepare data
    data = {
        "version": "1.0",
        "created": datetime.utcnow().isoformat() + "Z",
        "entries": len(folds_list),
        "folds": folds_list,
    }

    # Serialize to JSON
    json_data = json.dumps(data, separators=(",", ":")).encode("utf-8")

    # Compress
    if codec == "gzip":
        compressed = gzip.compress(json_data)
    else:
        compressed = json_data

    # Write file
    path_obj = Path(path)
    with path_obj.open("wb") as f:
        f.write(MAGIC)
        f.write(struct.pack(">I", len(compressed)))
        f.write(compressed)

        # CRC32
        crc = binascii.crc32(compressed) & 0xFFFFFFFF
        f.write(struct.pack(">I", crc))

    return {
        "entries": len(folds_list),
        "compressed_size": len(compressed),
        "uncompressed_size": len(json_data),
        "compression_ratio": len(compressed) / len(json_data) if json_data else 1.0,
    }


def create_fold_bundle(folds, bundle_name, output_dir, **kwargs):
    """Create a memory fold bundle"""
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"{bundle_name}_{timestamp}.lkf"
    output_path = Path(output_dir) / filename

    # Use async export
    stats = asyncio.run(export_folds(folds, str(output_path)))

    return output_path
