"""Compression bridge for the memory stack."""

from __future__ import annotations

from enum import Enum

__all__ = [
    "LZ4_AVAILABLE",
    "ZSTD_AVAILABLE",
    "AdaptiveCompressionManager",
    "Bz2Compressor",
    "CompressionAlgorithm",
    "CompressionResult",
    "CompressionStats",
    "GzipCompressor",
]

try:
    import zstandard as _zstd  # type: ignore

    ZSTD_AVAILABLE = True
except Exception:
    ZSTD_AVAILABLE = False

try:
    import lz4.frame as _lz4  # type: ignore

    LZ4_AVAILABLE = True
except Exception:
    LZ4_AVAILABLE = False


class CompressionAlgorithm(Enum):
    NONE = "none"
    LZ4 = "lz4"
    ZSTD = "zstd"


class AdaptiveCompressionManager:
    """Fallback adaptive compression manager."""

    def __init__(self, algorithm: CompressionAlgorithm = CompressionAlgorithm.NONE, threshold: int = 4096):
        self.algorithm = algorithm
        self.threshold = threshold

    def compress(self, data: bytes) -> bytes:
        return data

    def decompress(self, data: bytes) -> bytes:
        return data


class Bz2Compressor:
    """Fallback BZ2 compressor."""

    def compress(self, data: bytes) -> bytes:
        return data

    def decompress(self, data: bytes) -> bytes:
        return data


class CompressionResult(dict):
    """Fallback compression result payload."""


class CompressionStats(dict):
    """Fallback compression statistics container."""


class GzipCompressor:
    """Fallback Gzip compressor."""

    def compress(self, data: bytes) -> bytes:
        return data

    def decompress(self, data: bytes) -> bytes:
        return data
