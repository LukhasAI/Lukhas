"""
Memory Compression
==================
This module provides utilities for compressing and decompressing memory data.
"""

import zlib
import json
from typing import Any, Dict

class MemoryCompressor:
    """
    A simulated system for compressing and decompressing memory chunks.
    """

    def compress(self, memory_chunk: Dict[str, Any]) -> bytes:
        """
        Compresses a memory chunk using zlib.
        """
        print("Compressing memory chunk...")
        # Serialize the data to JSON before compressing
        serialized_data = json.dumps(memory_chunk, sort_keys=True).encode('utf-8')
        compressed_data = zlib.compress(serialized_data)

        print(f"Compressed from {len(serialized_data)} to {len(compressed_data)} bytes")
        return compressed_data

    def decompress(self, compressed_data: bytes) -> Dict[str, Any]:
        """
        Decompresses a memory chunk using zlib.
        """
        print("Decompressing memory chunk...")
        decompressed_data = zlib.decompress(compressed_data)
        deserialized_data = json.loads(decompressed_data.decode('utf-8'))

        print(f"Decompressed from {len(compressed_data)} to {len(decompressed_data)} bytes")
        return deserialized_data
