"""
T4/0.01% Excellence Memory Compression

High-performance content compression with zstd, adaptive algorithms,
and comprehensive quality metrics for LUKHAS memory system.

Performance targets:
- Compression speed: >50MB/s
- Decompression speed: >200MB/s
- Compression ratio: >2.5x for text content
- Operation latency: <10ms p95 for <1MB content
"""

import asyncio
import hashlib
import io
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

try:
    import zstandard as zstd
    ZSTD_AVAILABLE = True
except ImportError:
    ZSTD_AVAILABLE = False

import bz2
import gzip

from core.logging import get_logger
from observability.metrics import get_metrics_collector

logger = get_logger(__name__)
metrics = get_metrics_collector()


class CompressionAlgorithm(Enum):
    """Supported compression algorithms"""
    ZSTD = "zstd"           # Zstandard - best balance
    GZIP = "gzip"           # Standard gzip
    BZIP2 = "bzip2"         # High compression ratio
    LZMA = "lzma"           # Maximum compression
    LZ4 = "lz4"             # Fastest compression
    NONE = "none"           # No compression


class CompressionLevel(Enum):
    """Compression level presets"""
    FASTEST = 1             # Speed optimized
    FAST = 3                # Good speed/ratio balance
    BALANCED = 6            # Default balanced
    GOOD = 9                # Better compression
    BEST = 12               # Maximum compression


@dataclass
class CompressionResult:
    """
    Result of compression operation.
    """
    success: bool = False
    error: Optional[str] = None

    # Data
    compressed_data: bytes = b''
    original_size: int = 0
    compressed_size: int = 0

    # Metadata
    algorithm: CompressionAlgorithm = CompressionAlgorithm.NONE
    level: int = 6
    checksum: str = ""

    # Performance
    compression_time_ms: float = 0.0
    compression_speed_mbps: float = 0.0

    @property
    def compression_ratio(self) -> float:
        """Calculate compression ratio"""
        if self.compressed_size == 0:
            return 0.0
        return self.original_size / self.compressed_size

    @property
    def space_saved_percent(self) -> float:
        """Calculate space saved percentage"""
        if self.original_size == 0:
            return 0.0
        return ((self.original_size - self.compressed_size) / self.original_size) * 100


@dataclass
class DecompressionResult:
    """
    Result of decompression operation.
    """
    success: bool = False
    error: Optional[str] = None

    # Data
    decompressed_data: bytes = b''
    decompressed_size: int = 0

    # Validation
    checksum_valid: bool = False

    # Performance
    decompression_time_ms: float = 0.0
    decompression_speed_mbps: float = 0.0


@dataclass
class CompressionStats:
    """
    Compression system statistics.
    """
    # Operations
    compression_operations: int = 0
    decompression_operations: int = 0
    compression_errors: int = 0
    decompression_errors: int = 0

    # Performance
    total_compression_time_ms: float = 0.0
    total_decompression_time_ms: float = 0.0
    avg_compression_speed_mbps: float = 0.0
    avg_decompression_speed_mbps: float = 0.0

    # Quality
    avg_compression_ratio: float = 0.0
    total_bytes_processed: int = 0
    total_bytes_saved: int = 0

    # Algorithm usage
    algorithm_usage: Dict[str, int] = field(default_factory=dict)
    level_usage: Dict[int, int] = field(default_factory=dict)

    @property
    def overall_space_savings_percent(self) -> float:
        """Calculate overall space savings"""
        if self.total_bytes_processed == 0:
            return 0.0
        return (self.total_bytes_saved / self.total_bytes_processed) * 100

    def update_from_compression(self, result: CompressionResult):
        """Update stats from compression result"""
        self.compression_operations += 1
        if result.success:
            self.total_compression_time_ms += result.compression_time_ms
            self.total_bytes_processed += result.original_size
            self.total_bytes_saved += (result.original_size - result.compressed_size)

            # Update averages
            self.avg_compression_speed_mbps = (
                (self.avg_compression_speed_mbps * (self.compression_operations - 1) +
                 result.compression_speed_mbps) / self.compression_operations
            )

            self.avg_compression_ratio = (
                (self.avg_compression_ratio * (self.compression_operations - 1) +
                 result.compression_ratio) / self.compression_operations
            )

            # Track algorithm usage
            algo_name = result.algorithm.value
            self.algorithm_usage[algo_name] = self.algorithm_usage.get(algo_name, 0) + 1
            self.level_usage[result.level] = self.level_usage.get(result.level, 0) + 1
        else:
            self.compression_errors += 1

    def update_from_decompression(self, result: DecompressionResult):
        """Update stats from decompression result"""
        self.decompression_operations += 1
        if result.success:
            self.total_decompression_time_ms += result.decompression_time_ms

            # Update average decompression speed
            self.avg_decompression_speed_mbps = (
                (self.avg_decompression_speed_mbps * (self.decompression_operations - 1) +
                 result.decompression_speed_mbps) / self.decompression_operations
            )
        else:
            self.decompression_errors += 1


class AbstractCompressor(ABC):
    """
    Abstract base class for compression implementations.
    """

    @abstractmethod
    def compress(self, data: bytes, level: int = 6) -> CompressionResult:
        """Compress data"""
        pass

    @abstractmethod
    def decompress(
        self,
        compressed_data: bytes,
        expected_checksum: Optional[str] = None
    ) -> DecompressionResult:
        """Decompress data"""
        pass

    @property
    @abstractmethod
    def algorithm(self) -> CompressionAlgorithm:
        """Get algorithm identifier"""
        pass

    @property
    def max_level(self) -> int:
        """Maximum compression level"""
        return 9

    @property
    def min_level(self) -> int:
        """Minimum compression level"""
        return 1

    def _calculate_checksum(self, data: bytes) -> str:
        """Calculate SHA-256 checksum"""
        return hashlib.sha256(data).hexdigest()

    def _calculate_speed_mbps(self, bytes_processed: int, time_ms: float) -> float:
        """Calculate processing speed in MB/s"""
        if time_ms == 0:
            return 0.0
        mb_processed = bytes_processed / (1024 * 1024)
        seconds = time_ms / 1000
        return mb_processed / seconds


class ZstdCompressor(AbstractCompressor):
    """
    Zstandard compression implementation.
    """

    def __init__(self):
        if not ZSTD_AVAILABLE:
            raise ImportError("zstandard library not available")
        self.compressor = zstd.ZstdCompressor()
        self.decompressor = zstd.ZstdDecompressor()

    @property
    def algorithm(self) -> CompressionAlgorithm:
        return CompressionAlgorithm.ZSTD

    @property
    def max_level(self) -> int:
        return 22  # Zstd supports up to level 22

    def compress(self, data: bytes, level: int = 6) -> CompressionResult:
        """Compress data using Zstandard"""
        start_time = time.perf_counter()
        result = CompressionResult(
            original_size=len(data),
            algorithm=self.algorithm,
            level=level
        )

        try:
            # Clamp level to valid range
            level = max(self.min_level, min(level, self.max_level))

            # Create compressor with specific level
            compressor = zstd.ZstdCompressor(level=level)

            # Compress data
            compressed = compressor.compress(data)

            # Calculate metrics
            result.compressed_data = compressed
            result.compressed_size = len(compressed)
            result.checksum = self._calculate_checksum(data)
            result.compression_time_ms = (time.perf_counter() - start_time) * 1000
            result.compression_speed_mbps = self._calculate_speed_mbps(
                len(data), result.compression_time_ms
            )
            result.success = True

            logger.debug(
                "Zstd compression completed",
                original_size=result.original_size,
                compressed_size=result.compressed_size,
                ratio=result.compression_ratio,
                speed_mbps=result.compression_speed_mbps,
                level=level
            )

        except Exception as e:
            result.error = f"Zstd compression failed: {e}"
            logger.error("Zstd compression error", error=str(e))

        return result

    def decompress(
        self,
        compressed_data: bytes,
        expected_checksum: Optional[str] = None
    ) -> DecompressionResult:
        """Decompress Zstandard data"""
        start_time = time.perf_counter()
        result = DecompressionResult()

        try:
            # Decompress data
            decompressed = self.decompressor.decompress(compressed_data)

            # Calculate metrics
            result.decompressed_data = decompressed
            result.decompressed_size = len(decompressed)
            result.decompression_time_ms = (time.perf_counter() - start_time) * 1000
            result.decompression_speed_mbps = self._calculate_speed_mbps(
                len(decompressed), result.decompression_time_ms
            )

            # Validate checksum if provided
            if expected_checksum:
                actual_checksum = self._calculate_checksum(decompressed)
                result.checksum_valid = (actual_checksum == expected_checksum)
            else:
                result.checksum_valid = True

            result.success = True

        except Exception as e:
            result.error = f"Zstd decompression failed: {e}"
            logger.error("Zstd decompression error", error=str(e))

        return result


class GzipCompressor(AbstractCompressor):
    """
    Gzip compression implementation.
    """

    @property
    def algorithm(self) -> CompressionAlgorithm:
        return CompressionAlgorithm.GZIP

    def compress(self, data: bytes, level: int = 6) -> CompressionResult:
        """Compress data using gzip"""
        start_time = time.perf_counter()
        result = CompressionResult(
            original_size=len(data),
            algorithm=self.algorithm,
            level=level
        )

        try:
            # Clamp level to valid range
            level = max(self.min_level, min(level, self.max_level))

            # Compress using BytesIO
            buffer = io.BytesIO()
            with gzip.GzipFile(fileobj=buffer, mode='wb', compresslevel=level) as gz_file:
                gz_file.write(data)

            compressed = buffer.getvalue()

            # Calculate metrics
            result.compressed_data = compressed
            result.compressed_size = len(compressed)
            result.checksum = self._calculate_checksum(data)
            result.compression_time_ms = (time.perf_counter() - start_time) * 1000
            result.compression_speed_mbps = self._calculate_speed_mbps(
                len(data), result.compression_time_ms
            )
            result.success = True

        except Exception as e:
            result.error = f"Gzip compression failed: {e}"
            logger.error("Gzip compression error", error=str(e))

        return result

    def decompress(
        self,
        compressed_data: bytes,
        expected_checksum: Optional[str] = None
    ) -> DecompressionResult:
        """Decompress gzip data"""
        start_time = time.perf_counter()
        result = DecompressionResult()

        try:
            # Decompress using BytesIO
            buffer = io.BytesIO(compressed_data)
            with gzip.GzipFile(fileobj=buffer, mode='rb') as gz_file:
                decompressed = gz_file.read()

            # Calculate metrics
            result.decompressed_data = decompressed
            result.decompressed_size = len(decompressed)
            result.decompression_time_ms = (time.perf_counter() - start_time) * 1000
            result.decompression_speed_mbps = self._calculate_speed_mbps(
                len(decompressed), result.decompression_time_ms
            )

            # Validate checksum if provided
            if expected_checksum:
                actual_checksum = self._calculate_checksum(decompressed)
                result.checksum_valid = (actual_checksum == expected_checksum)
            else:
                result.checksum_valid = True

            result.success = True

        except Exception as e:
            result.error = f"Gzip decompression failed: {e}"
            logger.error("Gzip decompression error", error=str(e))

        return result


class Bz2Compressor(AbstractCompressor):
    """
    Bzip2 compression implementation.
    """

    @property
    def algorithm(self) -> CompressionAlgorithm:
        return CompressionAlgorithm.BZIP2

    def compress(self, data: bytes, level: int = 6) -> CompressionResult:
        """Compress data using bzip2"""
        start_time = time.perf_counter()
        result = CompressionResult(
            original_size=len(data),
            algorithm=self.algorithm,
            level=level
        )

        try:
            # Clamp level to valid range
            level = max(self.min_level, min(level, self.max_level))

            # Compress data
            compressed = bz2.compress(data, compresslevel=level)

            # Calculate metrics
            result.compressed_data = compressed
            result.compressed_size = len(compressed)
            result.checksum = self._calculate_checksum(data)
            result.compression_time_ms = (time.perf_counter() - start_time) * 1000
            result.compression_speed_mbps = self._calculate_speed_mbps(
                len(data), result.compression_time_ms
            )
            result.success = True

        except Exception as e:
            result.error = f"Bzip2 compression failed: {e}"
            logger.error("Bzip2 compression error", error=str(e))

        return result

    def decompress(
        self,
        compressed_data: bytes,
        expected_checksum: Optional[str] = None
    ) -> DecompressionResult:
        """Decompress bzip2 data"""
        start_time = time.perf_counter()
        result = DecompressionResult()

        try:
            # Decompress data
            decompressed = bz2.decompress(compressed_data)

            # Calculate metrics
            result.decompressed_data = decompressed
            result.decompressed_size = len(decompressed)
            result.decompression_time_ms = (time.perf_counter() - start_time) * 1000
            result.decompression_speed_mbps = self._calculate_speed_mbps(
                len(decompressed), result.decompression_time_ms
            )

            # Validate checksum if provided
            if expected_checksum:
                actual_checksum = self._calculate_checksum(decompressed)
                result.checksum_valid = (actual_checksum == expected_checksum)
            else:
                result.checksum_valid = True

            result.success = True

        except Exception as e:
            result.error = f"Bzip2 decompression failed: {e}"
            logger.error("Bzip2 decompression error", error=str(e))

        return result


class AdaptiveCompressionManager:
    """
    Adaptive compression manager that selects optimal algorithms and levels
    based on content characteristics and performance requirements.
    """

    def __init__(self, enable_adaptive: bool = True):
        self.enable_adaptive = enable_adaptive
        self.stats = CompressionStats()

        # Initialize compressors
        self.compressors = {
            CompressionAlgorithm.GZIP: GzipCompressor(),
            CompressionAlgorithm.BZIP2: Bz2Compressor()
        }

        # Add Zstd if available
        if ZSTD_AVAILABLE:
            self.compressors[CompressionAlgorithm.ZSTD] = ZstdCompressor()

        # Content type hints for algorithm selection
        self.content_hints = {
            'text': CompressionAlgorithm.ZSTD if ZSTD_AVAILABLE else CompressionAlgorithm.GZIP,
            'json': CompressionAlgorithm.ZSTD if ZSTD_AVAILABLE else CompressionAlgorithm.GZIP,
            'xml': CompressionAlgorithm.BZIP2,  # XML compresses well with bzip2
            'binary': CompressionAlgorithm.GZIP,
            'default': CompressionAlgorithm.ZSTD if ZSTD_AVAILABLE else CompressionAlgorithm.GZIP
        }

        # Performance thresholds for adaptive selection
        self.size_thresholds = {
            'small': 1024,        # <1KB - fast compression
            'medium': 1024 * 100, # <100KB - balanced
            'large': 1024 * 1024  # >1MB - maximum compression
        }

        logger.info(
            "Compression manager initialized",
            algorithms_available=list(self.compressors.keys()),
            zstd_available=ZSTD_AVAILABLE,
            adaptive_enabled=enable_adaptive
        )

    def _select_algorithm_and_level(
        self,
        data: bytes,
        content_type: Optional[str] = None,
        priority: str = "balanced"  # "speed", "balanced", "ratio"
    ) -> Tuple[CompressionAlgorithm, int]:
        """
        Select optimal compression algorithm and level.

        Args:
            data: Data to be compressed
            content_type: Hint about content type
            priority: Optimization priority

        Returns:
            Tuple of (algorithm, compression_level)
        """
        data_size = len(data)

        if not self.enable_adaptive:
            # Use default algorithm and level
            default_algo = self.content_hints.get('default')
            return default_algo, 6

        # Select algorithm based on content type hint
        if content_type and content_type in self.content_hints:
            algorithm = self.content_hints[content_type]
        else:
            # Analyze content to guess type
            try:
                data_str = data.decode('utf-8', errors='ignore')[:1000]
                if data_str.strip().startswith('{') or data_str.strip().startswith('['):
                    algorithm = self.content_hints['json']
                elif data_str.strip().startswith('<'):
                    algorithm = self.content_hints['xml']
                elif all(ord(c) < 128 for c in data_str[:100]):
                    algorithm = self.content_hints['text']
                else:
                    algorithm = self.content_hints['binary']
            except Exception as e:
                algorithm = self.content_hints['default']

        # Ensure algorithm is available
        if algorithm not in self.compressors:
            algorithm = CompressionAlgorithm.GZIP

        # Select compression level based on size and priority
        if priority == "speed":
            if data_size < self.size_thresholds['small']:
                level = 1
            elif data_size < self.size_thresholds['medium']:
                level = 3
            else:
                level = 1  # Large files - prioritize speed
        elif priority == "ratio":
            if data_size < self.size_thresholds['small']:
                level = 6  # Small files don't benefit much from max compression
            elif data_size < self.size_thresholds['medium']:
                level = 9
            else:
                level = 9  # Large files - maximum compression
        else:  # balanced
            if data_size < self.size_thresholds['small']:
                level = 3
            elif data_size < self.size_thresholds['medium']:
                level = 6
            else:
                level = 6

        # Adjust level based on algorithm capabilities
        compressor = self.compressors[algorithm]
        level = max(compressor.min_level, min(level, compressor.max_level))

        return algorithm, level

    async def compress_async(
        self,
        data: Union[str, bytes],
        content_type: Optional[str] = None,
        algorithm: Optional[CompressionAlgorithm] = None,
        level: Optional[int] = None,
        priority: str = "balanced"
    ) -> CompressionResult:
        """
        Compress data asynchronously with adaptive algorithm selection.

        Args:
            data: Data to compress (string or bytes)
            content_type: Content type hint for algorithm selection
            algorithm: Force specific algorithm (overrides adaptive selection)
            level: Force specific compression level
            priority: Optimization priority ("speed", "balanced", "ratio")

        Returns:
            CompressionResult with compressed data and metrics
        """
        # Convert string to bytes if needed
        if isinstance(data, str):
            data_bytes = data.encode('utf-8')
        else:
            data_bytes = data

        # Select algorithm and level if not specified
        if algorithm is None or level is None:
            selected_algo, selected_level = self._select_algorithm_and_level(
                data_bytes, content_type, priority
            )
            if algorithm is None:
                algorithm = selected_algo
            if level is None:
                level = selected_level

        # Get compressor
        if algorithm not in self.compressors:
            return CompressionResult(
                error=f"Unsupported compression algorithm: {algorithm}",
                original_size=len(data_bytes)
            )

        compressor = self.compressors[algorithm]

        # Run compression in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            compressor.compress,
            data_bytes,
            level
        )

        # Update statistics
        self.stats.update_from_compression(result)

        # Record metrics
        if result.success:
            metrics.record_histogram(
                "compression_duration_ms",
                result.compression_time_ms,
                tags={"algorithm": algorithm.value}
            )
            metrics.record_histogram(
                "compression_ratio",
                result.compression_ratio,
                tags={"algorithm": algorithm.value}
            )
            metrics.record_gauge(
                "compression_speed_mbps",
                result.compression_speed_mbps,
                tags={"algorithm": algorithm.value}
            )
            metrics.increment_counter(
                "compression_operations_total",
                tags={"algorithm": algorithm.value, "result": "success"}
            )
        else:
            metrics.increment_counter(
                "compression_operations_total",
                tags={"algorithm": algorithm.value, "result": "error"}
            )

        logger.debug(
            "Compression completed",
            algorithm=algorithm.value,
            level=level,
            original_size=result.original_size,
            compressed_size=result.compressed_size,
            ratio=result.compression_ratio,
            speed_mbps=result.compression_speed_mbps,
            success=result.success
        )

        return result

    async def decompress_async(
        self,
        compressed_data: bytes,
        algorithm: CompressionAlgorithm,
        expected_checksum: Optional[str] = None
    ) -> DecompressionResult:
        """
        Decompress data asynchronously.

        Args:
            compressed_data: Compressed data bytes
            algorithm: Compression algorithm used
            expected_checksum: Expected checksum for validation

        Returns:
            DecompressionResult with decompressed data and metrics
        """
        # Get compressor
        if algorithm not in self.compressors:
            return DecompressionResult(
                error=f"Unsupported compression algorithm: {algorithm}"
            )

        compressor = self.compressors[algorithm]

        # Run decompression in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            compressor.decompress,
            compressed_data,
            expected_checksum
        )

        # Update statistics
        self.stats.update_from_decompression(result)

        # Record metrics
        if result.success:
            metrics.record_histogram(
                "decompression_duration_ms",
                result.decompression_time_ms,
                tags={"algorithm": algorithm.value}
            )
            metrics.record_gauge(
                "decompression_speed_mbps",
                result.decompression_speed_mbps,
                tags={"algorithm": algorithm.value}
            )
            metrics.increment_counter(
                "decompression_operations_total",
                tags={"algorithm": algorithm.value, "result": "success"}
            )
        else:
            metrics.increment_counter(
                "decompression_operations_total",
                tags={"algorithm": algorithm.value, "result": "error"}
            )

        return result

    def compress_sync(
        self,
        data: Union[str, bytes],
        content_type: Optional[str] = None,
        algorithm: Optional[CompressionAlgorithm] = None,
        level: Optional[int] = None,
        priority: str = "balanced"
    ) -> CompressionResult:
        """
        Synchronous compression wrapper.
        """
        # Convert string to bytes if needed
        if isinstance(data, str):
            data_bytes = data.encode('utf-8')
        else:
            data_bytes = data

        # Select algorithm and level if not specified
        if algorithm is None or level is None:
            selected_algo, selected_level = self._select_algorithm_and_level(
                data_bytes, content_type, priority
            )
            if algorithm is None:
                algorithm = selected_algo
            if level is None:
                level = selected_level

        # Get compressor
        if algorithm not in self.compressors:
            return CompressionResult(
                error=f"Unsupported compression algorithm: {algorithm}",
                original_size=len(data_bytes)
            )

        compressor = self.compressors[algorithm]
        result = compressor.compress(data_bytes, level)

        # Update statistics
        self.stats.update_from_compression(result)

        return result

    def decompress_sync(
        self,
        compressed_data: bytes,
        algorithm: CompressionAlgorithm,
        expected_checksum: Optional[str] = None
    ) -> DecompressionResult:
        """
        Synchronous decompression wrapper.
        """
        if algorithm not in self.compressors:
            return DecompressionResult(
                error=f"Unsupported compression algorithm: {algorithm}"
            )

        compressor = self.compressors[algorithm]
        result = compressor.decompress(compressed_data, expected_checksum)

        # Update statistics
        self.stats.update_from_decompression(result)

        return result

    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive compression statistics"""
        stats_dict = {
            "operations": {
                "compression_operations": self.stats.compression_operations,
                "decompression_operations": self.stats.decompression_operations,
                "compression_errors": self.stats.compression_errors,
                "decompression_errors": self.stats.decompression_errors
            },
            "performance": {
                "avg_compression_speed_mbps": self.stats.avg_compression_speed_mbps,
                "avg_decompression_speed_mbps": self.stats.avg_decompression_speed_mbps,
                "total_compression_time_ms": self.stats.total_compression_time_ms,
                "total_decompression_time_ms": self.stats.total_decompression_time_ms
            },
            "quality": {
                "avg_compression_ratio": self.stats.avg_compression_ratio,
                "total_bytes_processed": self.stats.total_bytes_processed,
                "total_bytes_saved": self.stats.total_bytes_saved,
                "space_savings_percent": self.stats.overall_space_savings_percent
            },
            "usage": {
                "algorithm_usage": self.stats.algorithm_usage,
                "level_usage": self.stats.level_usage
            },
            "configuration": {
                "adaptive_enabled": self.enable_adaptive,
                "available_algorithms": [algo.value for algo in self.compressors.keys()],
                "zstd_available": ZSTD_AVAILABLE
            }
        }

        return stats_dict

    async def benchmark_algorithms(
        self,
        test_data: bytes,
        algorithms: Optional[List[CompressionAlgorithm]] = None,
        levels: Optional[List[int]] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Benchmark different algorithms and levels for given data.

        Args:
            test_data: Test data for benchmarking
            algorithms: Algorithms to test (default: all available)
            levels: Compression levels to test (default: [1, 6, 9])

        Returns:
            Benchmark results dictionary
        """
        if algorithms is None:
            algorithms = list(self.compressors.keys())

        if levels is None:
            levels = [1, 6, 9]

        results = {}

        for algorithm in algorithms:
            if algorithm not in self.compressors:
                continue

            compressor = self.compressors[algorithm]
            algorithm_results = {}

            for level in levels:
                # Clamp level to valid range
                level = max(compressor.min_level, min(level, compressor.max_level))

                # Test compression
                compression_result = await self.compress_async(
                    test_data,
                    algorithm=algorithm,
                    level=level
                )

                if compression_result.success:
                    # Test decompression
                    decompression_result = await self.decompress_async(
                        compression_result.compressed_data,
                        algorithm,
                        compression_result.checksum
                    )

                    algorithm_results[f"level_{level}"] = {
                        "compression": {
                            "success": compression_result.success,
                            "ratio": compression_result.compression_ratio,
                            "speed_mbps": compression_result.compression_speed_mbps,
                            "time_ms": compression_result.compression_time_ms,
                            "space_saved_percent": compression_result.space_saved_percent
                        },
                        "decompression": {
                            "success": decompression_result.success,
                            "speed_mbps": decompression_result.decompression_speed_mbps,
                            "time_ms": decompression_result.decompression_time_ms,
                            "checksum_valid": decompression_result.checksum_valid
                        }
                    }
                else:
                    algorithm_results[f"level_{level}"] = {
                        "compression": {"success": False, "error": compression_result.error},
                        "decompression": {"success": False}
                    }

            results[algorithm.value] = algorithm_results

        logger.info(
            "Algorithm benchmarking completed",
            test_data_size=len(test_data),
            algorithms_tested=len(algorithms),
            levels_tested=len(levels)
        )

        return results
