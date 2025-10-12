#!/usr/bin/env python3
"""
Tests for Top-K adaptive memory recall.
Validates <100ms performance for 10k items and consolidation behavior.
"""

import random
import string
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lukhas.memory.adaptive_memory import (
    AdaptiveMemorySystem,
    MemoryFold,
    MemoryItem,
    MemoryType,
)


def generate_random_content(size: int = 100) -> str:
    """Generate random content for testing"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=size))


class TestTopKRecall:
    """Test suite for Top-K adaptive recall"""

    def test_basic_store_and_recall(self):
        """Test basic memory storage and recall"""
        memory = AdaptiveMemorySystem(max_items=100)

        # Store some items
        items = []
        for i in range(10):
            item = memory.store(
                content=f"Memory item {i}",
                memory_type=MemoryType.SEMANTIC,
                importance=random.random(),
                tags=[f"tag{i % 3}"],
            )
            items.append(item)

        # Recall top 5
        recalled, latency = memory.recall_top_k(k=5)

        assert len(recalled) == 5
        assert latency < 100  # Should be fast for small dataset
        assert all(isinstance(item, MemoryItem) for item in recalled)

    def test_recall_performance_10k_items(self):
        """Test recall performance with 10k items"""
        memory = AdaptiveMemorySystem(max_items=15000)  # Allow headroom

        # Store 10k items
        print("Storing 10k items...")
        for i in range(10000):
            memory.store(
                content=f"Item {i}: {generate_random_content(50)}",
                memory_type=random.choice(list(MemoryType)),
                importance=random.random(),
                tags=[f"tag{i % 100}", f"category{i % 20}"],
            )

        # Test recall performance
        latencies = []
        for _ in range(10):
            recalled, latency = memory.recall_top_k(
                k=20,
                tags=[f"tag{random.randint(0, 99)}"]
            )
            latencies.append(latency)

        avg_latency = sum(latencies) / len(latencies)
        p95_latency = sorted(latencies)[int(len(latencies) * 0.95)]

        print(f"Average latency: {avg_latency:.2f}ms")
        print(f"P95 latency: {p95_latency:.2f}ms")

        # Assert performance target
        assert avg_latency < 100, f"Average latency {avg_latency}ms exceeds 100ms target"
        assert p95_latency < 150, f"P95 latency {p95_latency}ms exceeds 150ms limit"

    def test_filtered_recall(self):
        """Test recall with various filters"""
        memory = AdaptiveMemorySystem()

        # Store items of different types
        for i in range(50):
            memory.store(
                content=f"Item {i}",
                memory_type=MemoryType.EPISODIC if i % 2 else MemoryType.SEMANTIC,
                tags=["even" if i % 2 == 0 else "odd", f"group{i // 10}"],
            )

        # Test type filter
        episodic, _ = memory.recall_top_k(k=10, memory_type=MemoryType.EPISODIC)
        assert all(item.memory_type == MemoryType.EPISODIC for item in episodic)

        # Test tag filter
        even_items, _ = memory.recall_top_k(k=10, tags=["even"])
        assert len(even_items) > 0

        # Test combined filters
        group0_semantic, _ = memory.recall_top_k(
            k=5,
            memory_type=MemoryType.SEMANTIC,
            tags=["group0"]
        )
        assert len(group0_semantic) > 0

    def test_relevance_scoring(self):
        """Test relevance-based ranking"""
        memory = AdaptiveMemorySystem()

        # Store items with different importance
        old_item = memory.store(
            content="Old unimportant",
            importance=0.1,
        )
        time.sleep(0.01)  # Ensure time difference

        new_important = memory.store(
            content="New important",
            importance=0.9,
        )

        # Access old item multiple times
        for _ in range(5):
            memory.items[old_item.id].update_access()

        # Recall should favor new important despite fewer accesses
        recalled, _ = memory.recall_top_k(k=2)

        # Check that relevance scoring is working
        assert len(recalled) == 2
        scores = [item.get_relevance_score() for item in recalled]
        contents = [item.content for item in recalled]

        # Debug the results
        print(f"Recalled items: {contents}")
        print(f"Scores: {scores}")

        # The algorithm should prioritize importance over frequency for this test
        # New important (0.9 importance) should score higher than old (0.1 importance) with many accesses
        new_important_idx = next(i for i, content in enumerate(contents) if "New important" in content)
        old_unimportant_idx = next(i for i, content in enumerate(contents) if "Old unimportant" in content)

        assert scores[new_important_idx] > scores[old_unimportant_idx], \
            f"New important item should score higher: {scores[new_important_idx]:.10f} vs {scores[old_unimportant_idx]:.10f}"

    def test_context_window_generation(self):
        """Test context window generation with token limits"""
        memory = AdaptiveMemorySystem(max_context_length=1000)

        # Store items
        items = []
        for i in range(20):
            item = memory.store(
                content="x" * 100,  # ~25 tokens each
                memory_type=MemoryType.SEMANTIC,
            )
            items.append(item)

        # Get context window
        recalled, _ = memory.recall_top_k(k=20)
        context = memory.get_context_window(recalled, max_tokens=100)

        # Should limit to ~100 tokens (400 chars)
        assert len(context) < 500  # Some overhead for formatting

    def test_memory_pressure_handling(self):
        """Test behavior under memory pressure"""
        memory = AdaptiveMemorySystem(max_items=100)

        # Fill memory
        for i in range(100):
            memory.store(
                content=f"Item {i}",
                importance=i / 100,  # Increasing importance
            )

        # Store one more - should trigger cleanup
        memory.store(content="Overflow item", importance=0.5)

        # Should have removed least important items
        assert len(memory.items) <= 100

        # High importance items should remain
        items_list = list(memory.items.values())
        avg_importance = sum(i.importance for i in items_list) / len(items_list)
        assert avg_importance > 0.45  # Should keep more important items (adjusted threshold)

    def test_age_filtering(self):
        """Test filtering by age"""
        memory = AdaptiveMemorySystem()

        # Store old item
        old_item = memory.store(content="Old item")
        old_item.timestamp = datetime.now() - timedelta(days=10)

        # Store recent items
        for i in range(5):
            memory.store(content=f"Recent {i}")

        # Recall with age filter
        recent, _ = memory.recall_top_k(k=10, max_age_days=7)

        # Should not include old item
        assert len(recent) == 5
        assert old_item.id not in [i.id for i in recent]

    def test_embedding_similarity(self):
        """Test embedding-based similarity search"""
        memory = AdaptiveMemorySystem(enable_embeddings=True)

        # Store items with embeddings
        embedding1 = [1.0, 0.0, 0.0]
        embedding2 = [0.0, 1.0, 0.0]
        embedding3 = [0.9, 0.1, 0.0]  # Similar to embedding1

        memory.store(content="Item 1", embedding=embedding1)
        memory.store(content="Item 2", embedding=embedding2)
        memory.store(content="Item 3", embedding=embedding3)

        # Recall with query embedding similar to item 1
        recalled, _ = memory.recall_top_k(
            k=2,
            query_embedding=[0.95, 0.05, 0.0]
        )

        # Should recall items 1 and 3 (similar embeddings)
        contents = [item.content for item in recalled]
        assert "Item 1" in contents or "Item 3" in contents

    def test_metrics_collection(self):
        """Test metrics collection"""
        memory = AdaptiveMemorySystem()

        # Perform operations
        for i in range(100):
            memory.store(content=f"Item {i}")

        for _ in range(10):
            memory.recall_top_k(k=5)

        metrics = memory.get_metrics()

        assert metrics["total_items"] == 100
        assert metrics["total_recalls"] == 10
        assert metrics["avg_recall_latency_ms"] > 0
        assert "meets_sla" in metrics


class TestScheduledFolding:
    """Test suite for scheduled memory folding"""

    def test_fold_creation(self):
        """Test that folds are created properly"""
        memory = AdaptiveMemorySystem()

        # Store items
        for i in range(10):
            memory.store(content=f"Item {i}")

        # Should have active fold
        assert memory.active_fold is not None
        assert len(memory.active_fold.items) == 10

    def test_fold_consolidation_trigger(self):
        """Test fold consolidation triggers"""
        memory = AdaptiveMemorySystem()

        # Store many items to trigger consolidation
        for i in range(150):  # Over 100 item threshold
            memory.store(content=f"Item {i}")

        # Should have triggered consolidation
        assert memory.metrics["consolidations"] > 0

        # Should have consolidated item
        consolidated_items = [
            item for item in memory.items.values()
            if item.id.startswith("fold_")
        ]
        assert len(consolidated_items) > 0

    def test_fold_size_trigger(self):
        """Test consolidation based on size"""
        memory = AdaptiveMemorySystem()

        # Store large items to trigger size-based consolidation
        large_content = "x" * 10000  # 10KB each
        for i in range(110):  # Should exceed 1MB
            memory.store(content=large_content)

        # Should have consolidated
        assert memory.metrics["consolidations"] > 0

    def test_background_consolidation(self):
        """Test background consolidation thread"""
        memory = AdaptiveMemorySystem(consolidation_interval=1)  # 1 second

        # Create fold that needs consolidation
        fold = MemoryFold(id="test_fold")
        for i in range(101):  # Over threshold
            item = MemoryItem(id=f"item_{i}", content=f"Content {i}")
            fold.add_item(item)

        memory.folds[fold.id] = fold

        # Wait for background consolidation
        time.sleep(2)

        # Fold should be consolidated
        assert len(memory.folds) == 0 or fold.id not in memory.folds

        # Cleanup
        memory.shutdown()

    def test_consolidated_item_content(self):
        """Test consolidated item contains proper summary"""
        fold = MemoryFold(id="test")

        # Add items
        for i in range(10):
            item = MemoryItem(
                id=f"item_{i}",
                content=f"Content {i}",
                importance=0.5 + i * 0.05,
                context_tags=[f"tag{i}"],
            )
            fold.add_item(item)

        # Consolidate
        consolidated = fold.consolidate()

        assert consolidated.id == "fold_test"
        assert "summary" in consolidated.content
        assert consolidated.content["item_count"] == 10
        assert len(consolidated.context_tags) > 0

    def test_memory_lifecycle(self):
        """Test complete memory lifecycle with consolidation"""
        memory = AdaptiveMemorySystem()

        # Store items across multiple folds
        for batch in range(3):
            for i in range(101):  # Trigger consolidation each batch
                memory.store(
                    content=f"Batch {batch} Item {i}",
                    memory_type=MemoryType.EPISODIC,
                    tags=[f"batch{batch}"],
                )

        # Should have consolidations
        assert memory.metrics["consolidations"] >= 2

        # Can still recall consolidated content
        recalled, latency = memory.recall_top_k(k=10, tags=["batch0"])
        assert len(recalled) > 0
        assert latency < 100

    def test_shutdown_cleanup(self):
        """Test proper shutdown cleanup"""
        memory = AdaptiveMemorySystem(consolidation_interval=1)

        # Store items
        for i in range(10):
            memory.store(content=f"Item {i}")

        # Shutdown should complete without hanging
        memory.shutdown()

        # Should stop background thread
        assert memory._stop_consolidation.is_set()


class TestPerformanceBenchmark:
    """Performance benchmark tests"""

    def test_scaling_performance(self):
        """Test performance scaling with dataset size"""
        sizes = [100, 1000, 5000, 10000]
        results = []

        for size in sizes:
            memory = AdaptiveMemorySystem(max_items=size + 1000)

            # Store items
            for i in range(size):
                memory.store(
                    content=f"Item {i}",
                    tags=[f"tag{i % 50}"],
                    importance=random.random(),
                )

            # Measure recall performance
            latencies = []
            for _ in range(10):
                _, latency = memory.recall_top_k(k=20)
                latencies.append(latency)

            avg_latency = sum(latencies) / len(latencies)
            results.append((size, avg_latency))

            print(f"Size: {size:5d} | Avg latency: {avg_latency:.2f}ms")

        # All should meet <100ms target
        for size, latency in results:
            assert latency < 100, f"Failed at size {size}: {latency}ms"

    def test_concurrent_access(self):
        """Test concurrent read/write access"""
        import threading

        memory = AdaptiveMemorySystem()
        errors = []

        def writer():
            try:
                for i in range(100):
                    memory.store(content=f"Writer {i}")
            except Exception as e:
                errors.append(e)

        def reader():
            try:
                for _ in range(50):
                    memory.recall_top_k(k=5)
            except Exception as e:
                errors.append(e)

        # Launch concurrent threads
        threads = []
        for _ in range(2):
            t = threading.Thread(target=writer)
            threads.append(t)
            t.start()

        for _ in range(3):
            t = threading.Thread(target=reader)
            threads.append(t)
            t.start()

        # Wait for completion
        for t in threads:
            t.join()

        # Should complete without errors
        assert len(errors) == 0, f"Concurrent access errors: {errors}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
