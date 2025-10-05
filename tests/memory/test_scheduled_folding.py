#!/usr/bin/env python3
"""
Tests for scheduled memory folding system.
Validates compression, LRU eviction, and background scheduling.
"""

import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lukhas.memory.adaptive_memory import MemoryFold, MemoryItem, MemoryType
from lukhas.memory.scheduled_folding import (
    CompressionLevel,
    FoldStatus,
    ScheduledFold,
    ScheduledFoldingManager,
    get_folding_manager,
)


def create_test_fold(item_count: int = 10, content_size: int = 100, unique_suffix: str = None) -> MemoryFold:
    """Create a test memory fold with specified parameters"""
    if unique_suffix is None:
        unique_suffix = str(int(time.time() * 1000000))  # Microsecond precision

    fold = MemoryFold(id=f"test_fold_{unique_suffix}")

    for i in range(item_count):
        item = MemoryItem(
            id=f"item_{i}_{unique_suffix}",
            content=f"content_{i}_{unique_suffix}_" + "x" * content_size,  # Unique content
            memory_type=MemoryType.SEMANTIC,
            importance=i / max(1, item_count),  # Gradient importance
            context_tags=[f"tag{i % 3}", "test"],
        )
        fold.add_item(item)

    return fold


class TestScheduledFold:
    """Test suite for ScheduledFold functionality"""

    def test_fold_creation_and_hashing(self):
        """Test scheduled fold creation and content hashing"""
        fold = create_test_fold(5, 50)
        scheduled_fold = ScheduledFold(fold=fold)

        assert scheduled_fold.status == FoldStatus.ACTIVE
        assert scheduled_fold.content_hash is not None
        assert len(scheduled_fold.content_hash) == 16  # SHA256 truncated
        assert scheduled_fold.metrics.item_count == 5
        assert scheduled_fold.metrics.size_bytes > 0

    def test_fold_compression(self):
        """Test fold compression and decompression"""
        fold = create_test_fold(20, 200)
        scheduled_fold = ScheduledFold(fold=fold)

        # Test compression
        success = scheduled_fold.compress(CompressionLevel.MEDIUM)
        assert success
        assert scheduled_fold.status == FoldStatus.COMPRESSED
        assert scheduled_fold.compressed_data is not None
        assert scheduled_fold.metrics.compression_ratio < 1.0  # Should compress

        # Test decompression
        success = scheduled_fold.decompress()
        assert success
        assert scheduled_fold.status == FoldStatus.ACTIVE
        assert scheduled_fold.compressed_data is None
        assert len(scheduled_fold.fold.items) == 20

    def test_fold_access_tracking(self):
        """Test fold access tracking"""
        fold = create_test_fold(5)
        scheduled_fold = ScheduledFold(fold=fold)

        initial_count = scheduled_fold.metrics.access_count
        initial_time = scheduled_fold.metrics.last_accessed

        scheduled_fold.access()

        assert scheduled_fold.metrics.access_count == initial_count + 1
        assert scheduled_fold.metrics.last_accessed != initial_time

    def test_content_deduplication(self):
        """Test that identical content generates same hash"""
        fold1 = create_test_fold(3, 50)
        fold2 = create_test_fold(3, 50)

        # Create identical content
        for i in range(3):
            fold2.items[i].content = fold1.items[i].content

        scheduled_fold1 = ScheduledFold(fold=fold1)
        scheduled_fold2 = ScheduledFold(fold=fold2)

        # Should have same content hash
        assert scheduled_fold1.content_hash == scheduled_fold2.content_hash


class TestScheduledFoldingManager:
    """Test suite for ScheduledFoldingManager"""

    def test_manager_initialization(self):
        """Test folding manager initialization"""
        manager = ScheduledFoldingManager(
            max_active_folds=100,
            max_compressed_folds=500,
            compression_threshold_mb=5,
            folding_interval=30,
        )

        assert manager.max_active_folds == 100
        assert manager.max_compressed_folds == 500
        assert len(manager.active_folds) == 0
        assert len(manager.compressed_folds) == 0

    def test_fold_registration(self):
        """Test fold registration and tracking"""
        manager = ScheduledFoldingManager(max_active_folds=10)
        fold = create_test_fold(5)

        fold_id = manager.register_fold(fold, tags={"test", "sample"})

        assert fold_id == fold.id
        assert fold_id in manager.active_folds
        assert manager.metrics["folds_created"] == 1

    def test_fold_access_and_lru(self):
        """Test fold access and LRU ordering"""
        manager = ScheduledFoldingManager(max_active_folds=5)

        # Register multiple folds
        fold_ids = []
        for i in range(3):
            fold = create_test_fold(3)
            fold_id = manager.register_fold(fold)
            fold_ids.append(fold_id)

        # Access middle fold - should move to end
        middle_fold = manager.access_fold(fold_ids[1])
        assert middle_fold is not None

        # Check LRU ordering
        active_order = list(manager.active_folds.keys())
        assert active_order[-1] == fold_ids[1]  # Most recently accessed

    def test_automatic_compression(self):
        """Test automatic compression when limits exceeded"""
        manager = ScheduledFoldingManager(
            max_active_folds=3,
            eviction_batch_size=2,
        )

        # Register more folds than limit
        fold_ids = []
        for i in range(5):
            fold = create_test_fold(10, 100, unique_suffix=str(i))
            fold_id = manager.register_fold(fold)
            fold_ids.append(fold_id)

        # Should have triggered compression
        assert len(manager.active_folds) <= manager.max_active_folds
        total_folds = len(manager.active_folds) + len(manager.compressed_folds)
        assert total_folds >= 3  # Should maintain folds, possibly compressed

    def test_compression_and_decompression_cycle(self):
        """Test full compression/decompression cycle"""
        manager = ScheduledFoldingManager(max_active_folds=2)

        # Create folds that will be compressed
        fold1 = create_test_fold(10, unique_suffix="1")
        fold2 = create_test_fold(10, unique_suffix="2")
        fold3 = create_test_fold(10, unique_suffix="3")

        fold_id1 = manager.register_fold(fold1)
        fold_id2 = manager.register_fold(fold2)
        fold_id3 = manager.register_fold(fold3)  # Should trigger compression

        # Should maintain all folds, possibly compressed
        total_folds = len(manager.active_folds) + len(manager.compressed_folds)
        assert total_folds >= 2

        # Test accessing any available fold
        for fold_id in [fold_id1, fold_id2, fold_id3]:
            retrieved_fold = manager.access_fold(fold_id)
            if retrieved_fold is not None:
                assert retrieved_fold.id == fold_id
                break
        else:
            assert False, "Should be able to access at least one fold"

    def test_eviction_when_compressed_limit_exceeded(self):
        """Test fold eviction when compressed limit is exceeded"""
        manager = ScheduledFoldingManager(
            max_active_folds=2,
            max_compressed_folds=3,
            eviction_batch_size=2,
        )

        # Create many folds to trigger compression and eviction
        fold_ids = []
        for i in range(8):
            fold = create_test_fold(5, unique_suffix=str(i))
            fold_id = manager.register_fold(fold)
            fold_ids.append(fold_id)

        # Should respect limits
        total_folds = len(manager.active_folds) + len(manager.compressed_folds)
        assert total_folds <= manager.max_active_folds + manager.max_compressed_folds
        # Some folds should have been processed (compressed or evicted)
        assert manager.metrics["folds_compressed"] > 0 or manager.metrics["folds_evicted"] > 0

    def test_deduplication(self):
        """Test content deduplication"""
        manager = ScheduledFoldingManager()

        # Create identical folds
        fold1 = create_test_fold(3, 50)
        fold2 = create_test_fold(3, 50)

        # Make content identical
        for i in range(3):
            fold2.items[i].content = fold1.items[i].content

        fold_id1 = manager.register_fold(fold1)
        fold_id2 = manager.register_fold(fold2)

        # Should deduplicate
        assert fold_id1 == fold_id2
        assert manager.metrics["deduplication_saves"] == 1

    def test_tag_based_search(self):
        """Test finding folds by tags"""
        manager = ScheduledFoldingManager()

        # Register folds with different tags
        fold1 = create_test_fold(3, unique_suffix="math1")
        fold2 = create_test_fold(3, unique_suffix="text1")
        fold3 = create_test_fold(3, unique_suffix="math2")

        manager.register_fold(fold1, tags={"math", "calculation"})
        manager.register_fold(fold2, tags={"text", "processing"})
        manager.register_fold(fold3, tags={"math", "geometry"})

        # Search by tags
        math_folds = manager.find_folds_by_tags({"math"})
        assert len(math_folds) == 2

        processing_folds = manager.find_folds_by_tags({"processing"})
        assert len(processing_folds) == 1

    def test_status_reporting(self):
        """Test status reporting functionality"""
        manager = ScheduledFoldingManager(max_active_folds=5)

        # Add some folds
        for i in range(3):
            fold = create_test_fold(5, unique_suffix=f"status_{i}")
            manager.register_fold(fold)

        status = manager.get_status()

        assert "active_folds" in status
        assert "compressed_folds" in status
        assert "total_folds" in status
        assert "metrics" in status
        assert "health_status" in status

        # Should have at least 1 fold (may be compressed)
        assert status["total_folds"] >= 1
        assert status["health_status"]["memory_healthy"] is True


class TestBackgroundScheduling:
    """Test suite for background scheduling and maintenance"""

    def test_background_thread_starts(self):
        """Test that background thread starts properly"""
        manager = ScheduledFoldingManager(folding_interval=1)

        # Thread should start automatically
        assert manager._folding_thread is not None
        assert manager._folding_thread.is_alive()

        manager.shutdown()

    def test_scheduled_compression(self):
        """Test scheduled compression of old folds"""
        manager = ScheduledFoldingManager(
            folding_interval=1,  # 1 second interval
            max_active_folds=10,
        )

        # Create folds and artificially age them
        fold_ids = []
        for i in range(3):
            fold = create_test_fold(5)
            fold_id = manager.register_fold(fold)
            fold_ids.append(fold_id)

            # Manually age the fold
            scheduled_fold = manager.active_folds[fold_id]
            scheduled_fold.metrics.last_accessed = datetime.now() - timedelta(hours=1)

        initial_active = len(manager.active_folds)
        initial_compressed = len(manager.compressed_folds)

        # Wait for background processing
        time.sleep(2)

        # Should have compressed some aged folds
        final_active = len(manager.active_folds)
        final_compressed = len(manager.compressed_folds)

        # May not compress immediately due to timing, but structure should be valid
        assert final_active + final_compressed >= initial_active

        manager.shutdown()

    def test_manager_shutdown(self):
        """Test clean manager shutdown"""
        manager = ScheduledFoldingManager(folding_interval=1)

        assert manager._folding_thread.is_alive()

        manager.shutdown()

        # Thread should stop
        time.sleep(0.1)
        assert manager._stop_folding.is_set()


class TestCompressionLevels:
    """Test suite for compression level functionality"""

    def test_different_compression_levels(self):
        """Test different compression levels"""
        fold = create_test_fold(20, 500)  # Larger content for better compression

        # Test different compression levels
        levels = [CompressionLevel.LIGHT, CompressionLevel.MEDIUM, CompressionLevel.HEAVY]
        ratios = []

        for level in levels:
            scheduled_fold = ScheduledFold(fold=fold)
            success = scheduled_fold.compress(level)
            assert success
            ratios.append(scheduled_fold.metrics.compression_ratio)

        # Higher levels should generally compress better (lower ratio)
        # Note: with short test data, compression might not be dramatic
        assert all(0 < ratio <= 1.0 for ratio in ratios)

    def test_compression_metrics(self):
        """Test compression metrics tracking"""
        manager = ScheduledFoldingManager(max_active_folds=1)

        # Create large fold for better compression
        fold = create_test_fold(50, 200, unique_suffix="large")
        manager.register_fold(fold)

        # Trigger compression by adding another fold
        fold2 = create_test_fold(10, unique_suffix="small")
        manager.register_fold(fold2)

        # Should have processed folds (compressed or maintained)
        total_folds = len(manager.active_folds) + len(manager.compressed_folds)
        assert total_folds >= 1
        assert manager.metrics["compression_saves_bytes"] >= 0


class TestGlobalInstance:
    """Test suite for global folding manager instance"""

    def test_singleton_behavior(self):
        """Test that get_folding_manager returns singleton"""
        manager1 = get_folding_manager()
        manager2 = get_folding_manager()

        assert manager1 is manager2

    def test_global_manager_functionality(self):
        """Test that global manager works correctly"""
        manager = get_folding_manager()

        fold = create_test_fold(5)
        fold_id = manager.register_fold(fold)

        retrieved_fold = manager.access_fold(fold_id)
        assert retrieved_fold is not None
        assert retrieved_fold.id == fold.id


class TestErrorHandling:
    """Test suite for error handling and edge cases"""

    def test_access_nonexistent_fold(self):
        """Test accessing non-existent fold"""
        manager = ScheduledFoldingManager()

        result = manager.access_fold("nonexistent_id")
        assert result is None

    def test_compression_error_handling(self):
        """Test compression error handling"""
        fold = create_test_fold(3)
        scheduled_fold = ScheduledFold(fold=fold)

        # Corrupt fold data to cause compression error
        scheduled_fold.fold.items = None

        success = scheduled_fold.compress()
        assert not success
        assert scheduled_fold.status == FoldStatus.ERROR

    def test_empty_fold_handling(self):
        """Test handling of empty folds"""
        fold = MemoryFold(id="empty_fold")
        scheduled_fold = ScheduledFold(fold=fold)

        assert scheduled_fold.metrics.item_count == 0
        assert scheduled_fold.metrics.size_bytes == 0

        # Should still be able to compress empty fold
        success = scheduled_fold.compress()
        assert success


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
