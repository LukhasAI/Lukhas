"""
Test suite for LUKHAS memory compression system.

Validates compression algorithms, adaptive selection, performance metrics,
and benchmarking with T4/0.01% excellence standards.
"""

import time
from unittest.mock import Mock

import numpy as np
import pytest

from labs.memory.compression import (
    ZSTD_AVAILABLE,
    AdaptiveCompressionManager,
    Bz2Compressor,
    CompressionAlgorithm,
    CompressionResult,
    CompressionStats,
    GzipCompressor,
)

# Only test Zstd if available
if ZSTD_AVAILABLE:
    from labs.memory.compression import ZstdCompressor


class TestCompressionResult:
    """Test compression result data structures"""

    def test_compression_result_properties(self):
        """Test compression result calculated properties"""
        result = CompressionResult(
            success=True,
            original_size=1000,
            compressed_size=250
        )

        assert result.compression_ratio == 4.0
        assert result.space_saved_percent == 75.0

    def test_compression_result_zero_sizes(self):
        """Test compression result with zero sizes"""
        result = CompressionResult()
        assert result.compression_ratio == 0.0
        assert result.space_saved_percent == 0.0


class TestCompressionStats:
    """Test compression statistics tracking"""

    def setup_method(self):
        """Setup test environment"""
        self.stats = CompressionStats()

    def test_initial_stats(self):
        """Test initial statistics state"""
        assert self.stats.compression_operations == 0
        assert self.stats.decompression_operations == 0
        assert self.stats.overall_space_savings_percent == 0.0

    def test_stats_update_from_compression(self):
        """Test statistics update from compression result"""
        result = CompressionResult(
            success=True,
            original_size=1000,
            compressed_size=400,
            compression_time_ms=50.0,
            compression_speed_mbps=20.0,
            algorithm=CompressionAlgorithm.GZIP,
            level=6
        )

        self.stats.update_from_compression(result)

        assert self.stats.compression_operations == 1
        assert self.stats.total_bytes_processed == 1000
        assert self.stats.total_bytes_saved == 600
        assert self.stats.overall_space_savings_percent == 60.0
        assert self.stats.avg_compression_ratio == 2.5
        assert self.stats.algorithm_usage["gzip"] == 1

    def test_stats_update_from_failed_compression(self):
        """Test statistics update from failed compression"""
        result = CompressionResult(success=False)

        self.stats.update_from_compression(result)

        assert self.stats.compression_operations == 1
        assert self.stats.compression_errors == 1


class TestGzipCompressor:
    """Test Gzip compression implementation"""

    def setup_method(self):
        """Setup test environment"""
        self.compressor = GzipCompressor()

    def test_algorithm_property(self):
        """Test algorithm property"""
        assert self.compressor.algorithm == CompressionAlgorithm.GZIP

    def test_compression_basic(self):
        """Test basic compression"""
        data = b"This is test data for compression. " * 50
        result = self.compressor.compress(data, level=6)

        assert result.success is True
        assert result.original_size == len(data)
        assert result.compressed_size < result.original_size
        assert result.compression_ratio > 1.0
        assert result.compression_time_ms > 0
        assert len(result.checksum) == 64  # SHA-256 hex length

    def test_compression_empty_data(self):
        """Test compression of empty data"""
        result = self.compressor.compress(b"", level=6)
        assert result.success is True
        assert result.original_size == 0

    def test_compression_levels(self):
        """Test different compression levels"""
        data = b"Compression level test data. " * 100

        result_fast = self.compressor.compress(data, level=1)
        result_best = self.compressor.compress(data, level=9)

        assert result_fast.success is True
        assert result_best.success is True
        # Best compression should achieve better ratio (usually)
        # Note: For small data, this may not always hold

    def test_decompression_basic(self):
        """Test basic decompression"""
        data = b"Test data for compression and decompression cycle"

        # Compress first
        compress_result = self.compressor.compress(data)
        assert compress_result.success is True

        # Then decompress
        decompress_result = self.compressor.decompress(
            compress_result.compressed_data,
            compress_result.checksum
        )

        assert decompress_result.success is True
        assert decompress_result.decompressed_data == data
        assert decompress_result.checksum_valid is True
        assert decompress_result.decompression_time_ms > 0

    def test_decompression_invalid_data(self):
        """Test decompression of invalid data"""
        result = self.compressor.decompress(b"invalid compressed data")
        assert result.success is False
        assert "decompression failed" in result.error.lower()

    def test_checksum_validation(self):
        """Test checksum validation during decompression"""
        data = b"Checksum validation test"

        compress_result = self.compressor.compress(data)

        # Valid checksum
        decompress_result = self.compressor.decompress(
            compress_result.compressed_data,
            compress_result.checksum
        )
        assert decompress_result.checksum_valid is True

        # Invalid checksum
        decompress_result = self.compressor.decompress(
            compress_result.compressed_data,
            "invalid_checksum"
        )
        assert decompress_result.checksum_valid is False

    def test_performance_calculation(self):
        """Test performance metrics calculation"""
        data = b"Performance test data" * 1000
        result = self.compressor.compress(data)

        assert result.compression_speed_mbps > 0
        assert result.compression_time_ms > 0


class TestBz2Compressor:
    """Test Bzip2 compression implementation"""

    def setup_method(self):
        """Setup test environment"""
        self.compressor = Bz2Compressor()

    def test_algorithm_property(self):
        """Test algorithm property"""
        assert self.compressor.algorithm == CompressionAlgorithm.BZIP2

    def test_compression_and_decompression_cycle(self):
        """Test complete compression/decompression cycle"""
        data = b"Bzip2 test data for compression cycle testing. " * 20

        # Compress
        compress_result = self.compressor.compress(data, level=6)
        assert compress_result.success is True
        assert compress_result.compressed_size < compress_result.original_size

        # Decompress
        decompress_result = self.compressor.decompress(
            compress_result.compressed_data,
            compress_result.checksum
        )
        assert decompress_result.success is True
        assert decompress_result.decompressed_data == data


@pytest.mark.skipif(not ZSTD_AVAILABLE, reason="zstandard library not available")
class TestZstdCompressor:
    """Test Zstandard compression implementation"""

    def setup_method(self):
        """Setup test environment"""
        self.compressor = ZstdCompressor()

    def test_algorithm_property(self):
        """Test algorithm property"""
        assert self.compressor.algorithm == CompressionAlgorithm.ZSTD

    def test_max_level(self):
        """Test maximum compression level"""
        assert self.compressor.max_level == 22

    def test_compression_high_level(self):
        """Test compression with high level"""
        data = b"Zstd high compression level test data. " * 100

        result = self.compressor.compress(data, level=15)
        assert result.success is True
        assert result.level == 15

    def test_level_clamping(self):
        """Test compression level clamping"""
        data = b"Level clamping test"

        # Test level too high
        result = self.compressor.compress(data, level=50)
        assert result.success is True
        assert result.level == 22  # Clamped to max

        # Test level too low
        result = self.compressor.compress(data, level=-5)
        assert result.success is True
        assert result.level == 1  # Clamped to min


class TestAdaptiveCompressionManager:
    """Test adaptive compression management"""

    def setup_method(self):
        """Setup test environment"""
        self.manager = AdaptiveCompressionManager(enable_adaptive=True)

    def test_manager_initialization(self):
        """Test manager initialization"""
        assert len(self.manager.compressors) >= 2  # At least gzip and bzip2
        assert CompressionAlgorithm.GZIP in self.manager.compressors
        assert CompressionAlgorithm.BZIP2 in self.manager.compressors

    def test_algorithm_selection_by_content_type(self):
        """Test algorithm selection based on content type"""
        data = b"Small test data"

        # Test different content type hints
        algo_text, level = self.manager._select_algorithm_and_level(
            data, content_type="text", priority="balanced"
        )
        algo_xml, _ = self.manager._select_algorithm_and_level(
            data, content_type="xml", priority="balanced"
        )

        # XML should prefer bzip2
        assert algo_xml == CompressionAlgorithm.BZIP2

    def test_algorithm_selection_by_size(self):
        """Test algorithm selection based on data size"""
        small_data = b"small"
        large_data = b"x" * (2 * 1024 * 1024)  # 2MB

        _, level_small = self.manager._select_algorithm_and_level(
            small_data, priority="speed"
        )
        _, level_large = self.manager._select_algorithm_and_level(
            large_data, priority="speed"
        )

        # Both should prioritize speed, but levels may differ
        assert level_small >= 1
        assert level_large >= 1

    def test_priority_settings(self):
        """Test different priority settings"""
        data = b"Priority test data" * 100

        _, level_speed = self.manager._select_algorithm_and_level(
            data, priority="speed"
        )
        _, level_ratio = self.manager._select_algorithm_and_level(
            data, priority="ratio"
        )
        _, level_balanced = self.manager._select_algorithm_and_level(
            data, priority="balanced"
        )

        # Speed should generally use lower levels
        # Ratio should generally use higher levels
        assert level_speed <= level_balanced
        assert level_ratio >= level_balanced

    @pytest.mark.asyncio
    async def test_async_compression(self):
        """Test asynchronous compression"""
        data = "Async compression test data. " * 50

        result = await self.manager.compress_async(
            data,
            content_type="text",
            priority="balanced"
        )

        assert result.success is True
        assert result.original_size > 0
        assert result.compressed_size > 0
        assert result.compression_time_ms > 0

    @pytest.mark.asyncio
    async def test_async_decompression(self):
        """Test asynchronous decompression"""
        data = "Async decompression test data. " * 30

        # Compress first
        compress_result = await self.manager.compress_async(data)
        assert compress_result.success is True

        # Then decompress
        decompress_result = await self.manager.decompress_async(
            compress_result.compressed_data,
            compress_result.algorithm,
            compress_result.checksum
        )

        assert decompress_result.success is True
        assert decompress_result.decompressed_data.decode('utf-8') == data

    def test_sync_compression(self):
        """Test synchronous compression"""
        data = "Sync compression test"

        result = self.manager.compress_sync(data)
        assert result.success is True

    def test_sync_decompression(self):
        """Test synchronous decompression"""
        data = "Sync decompression test"

        compress_result = self.manager.compress_sync(data)
        decompress_result = self.manager.decompress_sync(
            compress_result.compressed_data,
            compress_result.algorithm,
            compress_result.checksum
        )

        assert decompress_result.success is True
        assert decompress_result.decompressed_data.decode('utf-8') == data

    @pytest.mark.asyncio
    async def test_force_algorithm(self):
        """Test forcing specific algorithm"""
        data = "Force algorithm test"

        result = await self.manager.compress_async(
            data,
            algorithm=CompressionAlgorithm.GZIP,
            level=9
        )

        assert result.success is True
        assert result.algorithm == CompressionAlgorithm.GZIP
        assert result.level == 9

    @pytest.mark.asyncio
    async def test_unsupported_algorithm(self):
        """Test unsupported algorithm handling"""
        # This test assumes LZMA is not implemented in our test suite
        result = await self.manager.compress_async(
            "test",
            algorithm=CompressionAlgorithm.LZMA
        )
        assert result.success is False
        assert "Unsupported compression algorithm" in result.error

    def test_statistics_tracking(self):
        """Test statistics tracking in manager"""
        data = "Statistics test data"

        # Perform operations
        self.manager.compress_sync(data)
        stats = self.manager.get_statistics()

        assert stats["operations"]["compression_operations"] == 1
        assert stats["quality"]["total_bytes_processed"] > 0
        assert "available_algorithms" in stats["configuration"]

    @pytest.mark.asyncio
    async def test_benchmark_algorithms(self):
        """Test algorithm benchmarking"""
        test_data = b"Benchmark test data for compression algorithms. " * 50

        # Benchmark available algorithms
        results = await self.manager.benchmark_algorithms(
            test_data,
            algorithms=[CompressionAlgorithm.GZIP, CompressionAlgorithm.BZIP2],
            levels=[1, 6, 9]
        )

        assert "gzip" in results
        assert "bzip2" in results

        for algo_results in results.values():
            for level_results in algo_results.values():
                assert "compression" in level_results
                assert "decompression" in level_results

    def test_non_adaptive_mode(self):
        """Test non-adaptive mode"""
        manager = AdaptiveCompressionManager(enable_adaptive=False)

        data = b"Non-adaptive test"
        algo, level = manager._select_algorithm_and_level(data, content_type="xml")

        # Should use default algorithm regardless of content type
        expected_default = (
            CompressionAlgorithm.ZSTD if ZSTD_AVAILABLE
            else CompressionAlgorithm.GZIP
        )
        assert algo == expected_default

    @pytest.mark.asyncio
    async def test_performance_targets(self):
        """Test compression performance targets"""
        data = "Performance target test data. " * 100

        start_time = time.perf_counter()
        result = await self.manager.compress_async(data, priority="speed")
        duration = time.perf_counter() - start_time

        assert result.success is True
        # Target: <10ms p95 for <1MB content (relaxed for test environment)
        assert duration < 1.0  # 1 second timeout for test
        assert result.compression_speed_mbps > 0

    @pytest.mark.asyncio
    async def test_content_type_detection(self):
        """Test automatic content type detection"""
        json_data = '{"test": "data", "number": 42}'
        xml_data = '<root><test>data</test></root>'

        # Test JSON detection
        result_json = await self.manager.compress_async(json_data)
        assert result_json.success is True

        # Test XML detection
        result_xml = await self.manager.compress_async(xml_data)
        assert result_xml.success is True

    def test_error_handling(self):
        """Test error handling in compression operations"""
        # Test with mock compressor that always fails
        mock_compressor = Mock()
        mock_compressor.compress.return_value = CompressionResult(
            success=False,
            error="Mock compression error"
        )

        self.manager.compressors[CompressionAlgorithm.GZIP] = mock_compressor

        result = self.manager.compress_sync("test", algorithm=CompressionAlgorithm.GZIP)
        assert result.success is False
        assert "Mock compression error" in result.error


@pytest.mark.asyncio
async def test_integration_compression_with_vector_documents():
    """Integration test with vector document compression"""
    import json

    from lukhas.memory.backends.base import VectorDocument

    # Create a vector document
    doc = VectorDocument(
        id="compression-test-doc",
        content="This is test content for vector document compression",
        embedding=np.random.random(384).astype(np.float32),
        metadata={"test": True, "compression": "enabled"}
    )

    # Convert to JSON for compression
    doc_json = json.dumps(doc.to_dict())

    manager = AdaptiveCompressionManager()

    # Compress document
    result = await manager.compress_async(
        doc_json,
        content_type="json",
        priority="balanced"
    )

    assert result.success is True
    assert result.compression_ratio > 1.0

    # Decompress and verify
    decompress_result = await manager.decompress_async(
        result.compressed_data,
        result.algorithm,
        result.checksum
    )

    assert decompress_result.success is True
    reconstructed_doc_data = json.loads(decompress_result.decompressed_data.decode('utf-8'))
    assert reconstructed_doc_data["id"] == "compression-test-doc"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
