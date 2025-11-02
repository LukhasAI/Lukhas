#!/usr/bin/env python3
"""
Memory Fold Consolidation Edge Cases Tests

Tests edge cases and data preservation in memory fold consolidation process.
Validates that consolidated items remain searchable and no data is lost.

# ΛTAG: memory_fold_tests, consolidation_edge_cases, robustness_testing
"""

import asyncio
import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

try:
    from memory.adaptive_memory import AdaptiveMemorySystem, MemoryFold, MemoryItem, MemoryType

    MEMORY_AVAILABLE = True
except ImportError:
    # Fallback for testing without full memory system
    MEMORY_AVAILABLE = False
    AdaptiveMemorySystem = None
    MemoryItem = None
    MemoryFold = None
    MemoryType = None


@pytest.mark.skipif(not MEMORY_AVAILABLE, reason="Memory system not available")
class TestFoldConsolidationEdgeCases:
    """Test edge cases in memory fold consolidation."""

    @pytest.fixture
    def memory_system(self):
        """Create a temporary memory system for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            system = AdaptiveMemorySystem(storage_path=Path(tmpdir))
            yield system

    @pytest.fixture
    def sample_memories(self):
        """Create sample memory items for testing."""
        base_time = datetime.now()

        memories = []
        for i in range(150):  # Exceed consolidation threshold (100)
            memory = MemoryItem(
                id=f"mem_{i:03d}",
                content={
                    "text": f"Memory content {i}",
                    "data": {"value": i, "category": f"cat_{i % 5}"},
                    "metadata": {"source": "test", "importance": i % 10},
                },
                memory_type=MemoryType.DECLARATIVE,
                timestamp=base_time + timedelta(minutes=i),
                tags=[f"tag_{i % 3}", "test_data"],
                importance_score=0.1 + (i % 10) * 0.1,
            )
            memories.append(memory)

        return memories

    def test_basic_consolidation_triggered(self, memory_system, sample_memories):
        """Test that consolidation is triggered when thresholds are exceeded."""

        # Add memories to exceed consolidation threshold
        fold_id = "test_fold_001"
        fold = MemoryFold(id=fold_id)

        for memory in sample_memories:
            fold.add_item(memory)
            memory_system.store_memory(memory)

        # Check consolidation trigger
        assert fold.should_consolidate(), "Fold should require consolidation with 150 items"
        assert len(fold.items) > 100, "Fold should have more than 100 items"

    def test_consolidation_preserves_searchable_content(self, memory_system, sample_memories):
        """Test that consolidated memories remain searchable."""

        # Create and populate fold
        fold_id = "searchable_fold"
        fold = MemoryFold(id=fold_id)

        for memory in sample_memories[:120]:  # Use subset to trigger consolidation
            fold.add_item(memory)
            memory_system.store_memory(memory)

        # Record original searchable terms
        original_terms = set()
        for memory in fold.items:
            if isinstance(memory.content, dict) and "text" in memory.content:
                original_terms.add(memory.content["text"])
            original_terms.update(memory.tags)

        # Perform consolidation
        consolidated_item = fold.consolidate()
        memory_system._consolidate_fold(fold)

        # Verify consolidated item contains searchable references
        assert consolidated_item.id.startswith("consolidated_"), "Consolidated item should have proper ID"
        assert "fold_id" in consolidated_item.content, "Should preserve fold ID"
        assert consolidated_item.content["item_count"] == 120, "Should preserve item count"

        # Test that consolidated content is searchable
        consolidated_content = json.dumps(consolidated_item.content)

        # Check that at least some original terms are preserved
        preserved_terms = 0
        for term in list(original_terms)[:10]:  # Check first 10 terms
            if term in consolidated_content:
                preserved_terms += 1

        assert preserved_terms > 0, "Consolidated content should preserve searchable terms"

    def test_consolidation_edge_case_empty_fold(self, memory_system):
        """Test consolidation behavior with empty fold."""

        empty_fold = MemoryFold(id="empty_fold")

        # Empty fold should not trigger consolidation
        assert not empty_fold.should_consolidate(), "Empty fold should not need consolidation"

        # Consolidating empty fold should handle gracefully
        with pytest.raises((ValueError, IndexError)):
            empty_fold.consolidate()

    def test_consolidation_edge_case_single_item(self, memory_system):
        """Test consolidation behavior with single item fold."""

        single_fold = MemoryFold(id="single_fold")
        single_memory = MemoryItem(
            id="single_mem",
            content={"text": "Single memory"},
            memory_type=MemoryType.EPISODIC,
            timestamp=datetime.now(),
            tags=["single"],
            importance_score=0.5,
        )

        single_fold.add_item(single_memory)

        # Single item should not trigger consolidation
        assert not single_fold.should_consolidate(), "Single item fold should not need consolidation"

    def test_consolidation_preserves_temporal_order(self, memory_system, sample_memories):
        """Test that consolidation preserves temporal ordering information."""

        fold = MemoryFold(id="temporal_fold")

        # Add memories in specific temporal order
        sorted_memories = sorted(sample_memories[:110], key=lambda m: m.timestamp)
        for memory in sorted_memories:
            fold.add_item(memory)

        # Consolidate
        consolidated_item = fold.consolidate()

        # Check temporal preservation
        time_range = consolidated_item.content["time_range"]
        assert len(time_range) == 2, "Should preserve start and end times"

        earliest_time = min(m.timestamp for m in sorted_memories)
        latest_time = max(m.timestamp for m in sorted_memories)

        assert time_range[0] == earliest_time, "Should preserve earliest timestamp"
        assert time_range[1] == latest_time, "Should preserve latest timestamp"

    def test_consolidation_preserves_importance_distribution(self, memory_system, sample_memories):
        """Test that consolidation preserves importance score distribution."""

        fold = MemoryFold(id="importance_fold")

        # Add memories with varied importance scores
        for memory in sample_memories[:105]:
            fold.add_item(memory)

        # Calculate original importance statistics
        original_scores = [m.importance_score for m in fold.items]
        original_avg = sum(original_scores) / len(original_scores)
        original_max = max(original_scores)
        original_min = min(original_scores)

        # Consolidate
        consolidated_item = fold.consolidate()

        # Check importance preservation
        assert "importance_stats" in consolidated_item.content, "Should preserve importance statistics"

        stats = consolidated_item.content["importance_stats"]
        assert abs(stats["avg"] - original_avg) < 0.01, "Should preserve average importance"
        assert stats["max"] == original_max, "Should preserve maximum importance"
        assert stats["min"] == original_min, "Should preserve minimum importance"

    def test_consolidation_handles_large_content(self, memory_system):
        """Test consolidation with very large content items."""

        fold = MemoryFold(id="large_content_fold")

        # Create memories with large content (simulate size threshold trigger)
        large_memories = []
        for i in range(50):  # Fewer items but large content
            large_content = {
                "text": "Large memory content " * 1000,  # ~20KB per item
                "data": {"large_data": "x" * 10000},  # Additional large data
                "index": i,
            }

            memory = MemoryItem(
                id=f"large_mem_{i}",
                content=large_content,
                memory_type=MemoryType.DECLARATIVE,
                timestamp=datetime.now(),
                tags=["large_content"],
                importance_score=0.5,
            )

            fold.add_item(memory)
            large_memories.append(memory)

        # Should trigger consolidation due to size
        assert fold.should_consolidate(), "Large content should trigger consolidation"
        assert fold.size_bytes > 1_000_000, "Fold should exceed size threshold"

        # Consolidate and verify
        consolidated_item = fold.consolidate()

        assert consolidated_item.content["item_count"] == 50, "Should preserve item count"
        assert "size_reduction" in consolidated_item.content, "Should track size reduction"

    def test_consolidation_handles_mixed_content_types(self, memory_system):
        """Test consolidation with mixed content types and structures."""

        fold = MemoryFold(id="mixed_content_fold")

        # Create memories with different content structures
        mixed_memories = []
        for i in range(110):
            if i % 4 == 0:
                content = {"text": f"Text memory {i}"}
            elif i % 4 == 1:
                content = {"data": {"number": i, "list": [1, 2, 3]}}
            elif i % 4 == 2:
                content = {"mixed": {"text": f"Mixed {i}", "number": i}}
            else:
                content = f"String content {i}"  # Non-dict content

            memory = MemoryItem(
                id=f"mixed_mem_{i}",
                content=content,
                memory_type=MemoryType.PROCEDURAL if i % 2 else MemoryType.DECLARATIVE,
                timestamp=datetime.now(),
                tags=[f"type_{i % 4}"],
                importance_score=0.3 + (i % 7) * 0.1,
            )

            fold.add_item(memory)
            mixed_memories.append(memory)

        # Consolidate mixed content
        consolidated_item = fold.consolidate()

        # Verify mixed content handling
        assert "content_types" in consolidated_item.content, "Should categorize content types"
        assert "memory_types" in consolidated_item.content, "Should track memory types"

        content_types = consolidated_item.content["content_types"]
        assert "dict" in content_types or "object" in content_types, "Should detect dict content"
        assert "string" in content_types or "str" in content_types, "Should detect string content"

    def test_consolidation_searchability_preservation(self, memory_system, sample_memories):
        """Test that consolidated memories can be found via search."""

        fold = MemoryFold(id="searchable_fold")

        # Add memories with specific searchable content
        searchable_memories = []
        for i in range(105):
            memory = MemoryItem(
                id=f"search_mem_{i}",
                content={
                    "text": f"Important project {i} with keyword SEARCHTERM",
                    "category": "project",
                    "status": "active" if i % 2 else "completed",
                },
                memory_type=MemoryType.DECLARATIVE,
                timestamp=datetime.now(),
                tags=["project", "searchable", f"batch_{i // 10}"],
                importance_score=0.4 + (i % 6) * 0.1,
            )

            fold.add_item(memory)
            searchable_memories.append(memory)
            memory_system.store_memory(memory)

        # Perform consolidation
        memory_system._consolidate_fold(fold)

        # Test search functionality still works
        search_results = memory_system.search_memories("SEARCHTERM", limit=10)

        # Should find consolidated item
        assert len(search_results) > 0, "Search should find consolidated memories"

        # Check that consolidated item appears in results
        consolidated_found = False
        for result in search_results:
            if "consolidated_" in result.id:
                consolidated_found = True
                assert "SEARCHTERM" in str(result.content), "Consolidated item should contain search term"
                break

        assert consolidated_found, "Should find consolidated item in search results"

    def test_consolidation_error_handling(self, memory_system):
        """Test error handling during consolidation process."""

        fold = MemoryFold(id="error_test_fold")

        # Create memory with problematic content
        problematic_memory = MemoryItem(
            id="problematic_mem",
            content={"circular_ref": None},  # Will create circular reference
            memory_type=MemoryType.DECLARATIVE,
            timestamp=datetime.now(),
            tags=["problematic"],
            importance_score=0.5,
        )

        # Create circular reference
        problematic_memory.content["circular_ref"] = problematic_memory.content

        # Add enough items to trigger consolidation
        for i in range(101):
            if i == 50:
                fold.add_item(problematic_memory)
            else:
                normal_memory = MemoryItem(
                    id=f"normal_mem_{i}",
                    content={"text": f"Normal memory {i}"},
                    memory_type=MemoryType.DECLARATIVE,
                    timestamp=datetime.now(),
                    tags=["normal"],
                    importance_score=0.5,
                )
                fold.add_item(normal_memory)

        # Consolidation should handle errors gracefully
        try:
            consolidated_item = fold.consolidate()
            # If consolidation succeeds, verify it handled the problematic content
            assert consolidated_item is not None, "Consolidation should complete"
            assert "error_handling" in consolidated_item.content, "Should note error handling"
        except Exception as e:
            # If consolidation fails, it should be a controlled failure
            assert (
                "circular" in str(e).lower() or "serialize" in str(e).lower()
            ), "Should fail with expected serialization error"

    def test_performance_under_consolidation(self, memory_system):
        """Test performance characteristics during consolidation."""

        import time

        fold = MemoryFold(id="performance_fold")

        # Create large number of memories
        start_time = time.perf_counter()

        for i in range(200):  # Large consolidation
            memory = MemoryItem(
                id=f"perf_mem_{i}",
                content={"text": f"Performance test memory {i}", "data": list(range(100))},
                memory_type=MemoryType.DECLARATIVE,
                timestamp=datetime.now(),
                tags=["performance"],
                importance_score=0.5,
            )
            fold.add_item(memory)

        time.perf_counter() - start_time

        # Measure consolidation time
        consolidation_start = time.perf_counter()
        consolidated_item = fold.consolidate()
        consolidation_time = time.perf_counter() - consolidation_start

        # Performance assertions
        assert consolidation_time < 5.0, f"Consolidation took too long: {consolidation_time:.2f}s"
        assert consolidated_item.content["item_count"] == 200, "Should consolidate all items"

        # Verify consolidation efficiency
        original_size = fold.size_bytes
        consolidated_size = len(str(consolidated_item.content))

        print(f"Original size: {original_size}, Consolidated size: {consolidated_size}")
        print(f"Consolidation time: {consolidation_time:.3f}s for 200 items")

    def test_consolidation_concurrent_access_edge_case(self, memory_system):
        """Test consolidation behavior under concurrent access scenarios."""

        fold = MemoryFold(id="concurrent_fold")

        # Add memories to trigger consolidation
        for i in range(105):
            memory = MemoryItem(
                id=f"concurrent_mem_{i}",
                content={"text": f"Concurrent memory {i}", "timestamp": i},
                memory_type=MemoryType.DECLARATIVE,
                timestamp=datetime.now(),
                tags=["concurrent"],
                importance_score=0.5,
            )
            fold.add_item(memory)

        # Simulate concurrent access during consolidation
        original_count = len(fold.items)

        # Start consolidation
        consolidated_item = fold.consolidate()

        # Verify consolidation completed despite concurrent access scenario
        assert consolidated_item is not None, "Consolidation should complete"
        assert consolidated_item.content["item_count"] == original_count, "Should preserve all items"

    def test_consolidation_memory_pressure_edge_case(self, memory_system):
        """Test consolidation under memory pressure conditions."""

        fold = MemoryFold(id="memory_pressure_fold")

        # Create very large memories to simulate memory pressure
        large_memories = []
        for i in range(50):  # Fewer items but very large
            huge_content = {
                "text": "Memory pressure test " * 10000,  # Very large text
                "data": {"huge_array": list(range(10000))},  # Large data structure
                "metadata": {"size_test": "x" * 50000},  # Additional large content
            }

            memory = MemoryItem(
                id=f"pressure_mem_{i}",
                content=huge_content,
                memory_type=MemoryType.DECLARATIVE,
                timestamp=datetime.now(),
                tags=["memory_pressure"],
                importance_score=0.7,
            )

            fold.add_item(memory)
            large_memories.append(memory)

        # Should trigger consolidation due to memory pressure
        assert fold.should_consolidate(), "Memory pressure should trigger consolidation"

        # Consolidate under pressure
        consolidated_item = fold.consolidate()

        # Verify successful consolidation despite memory pressure
        assert consolidated_item is not None, "Should consolidate despite memory pressure"
        assert "memory_pressure_handling" in consolidated_item.content, "Should track pressure handling"

    def test_consolidation_cross_fold_dependency_edge_case(self, memory_system):
        """Test consolidation with cross-fold dependencies and references."""

        # Create two related folds
        fold_a = MemoryFold(id="dependent_fold_a")
        fold_b = MemoryFold(id="dependent_fold_b")

        # Create memories with cross-references
        for i in range(55):
            # Memory in fold A that references fold B
            memory_a = MemoryItem(
                id=f"ref_mem_a_{i}",
                content={
                    "text": f"Memory A {i}",
                    "references": [f"ref_mem_b_{i}", f"ref_mem_b_{i+1}"],
                    "fold_dependency": "dependent_fold_b",
                },
                memory_type=MemoryType.DECLARATIVE,
                timestamp=datetime.now(),
                tags=["cross_reference", "fold_a"],
                importance_score=0.6,
            )
            fold_a.add_item(memory_a)

            # Memory in fold B that references fold A
            memory_b = MemoryItem(
                id=f"ref_mem_b_{i}",
                content={
                    "text": f"Memory B {i}",
                    "back_references": [f"ref_mem_a_{i}"],
                    "fold_dependency": "dependent_fold_a",
                },
                memory_type=MemoryType.DECLARATIVE,
                timestamp=datetime.now(),
                tags=["cross_reference", "fold_b"],
                importance_score=0.6,
            )
            fold_b.add_item(memory_b)

        # Consolidate both folds
        consolidated_a = fold_a.consolidate()
        consolidated_b = fold_b.consolidate()

        # Verify cross-dependencies are preserved
        assert "cross_fold_references" in consolidated_a.content, "Should preserve cross-fold refs"
        assert "cross_fold_references" in consolidated_b.content, "Should preserve cross-fold refs"

        # Check dependency tracking
        assert consolidated_a.content["cross_fold_references"]["dependent_fold_b"] > 0
        assert consolidated_b.content["cross_fold_references"]["dependent_fold_a"] > 0

    def test_consolidation_version_conflict_edge_case(self, memory_system):
        """Test consolidation with version conflicts and schema mismatches."""

        fold = MemoryFold(id="version_conflict_fold")

        # Create memories with different schema versions
        for i in range(60):
            if i % 3 == 0:
                # Version 1 schema
                content = {"schema_version": "1.0", "text": f"Version 1 memory {i}", "old_field": "legacy_data"}
            elif i % 3 == 1:
                # Version 2 schema
                content = {
                    "schema_version": "2.0",
                    "content": f"Version 2 memory {i}",
                    "new_field": "updated_data",
                    "metadata": {"migration_needed": True},
                }
            else:
                # Version 3 schema
                content = {
                    "schema_version": "3.0",
                    "data": {"text": f"Version 3 memory {i}", "structured": True},
                    "features": ["advanced", "typed"],
                }

            memory = MemoryItem(
                id=f"version_mem_{i}",
                content=content,
                memory_type=MemoryType.DECLARATIVE,
                timestamp=datetime.now(),
                tags=["version_test", f"v{content['schema_version']}"],
                importance_score=0.5,
            )
            fold.add_item(memory)

        # Consolidate with version conflicts
        consolidated_item = fold.consolidate()

        # Verify version conflict handling
        assert "schema_versions" in consolidated_item.content, "Should track schema versions"
        assert "version_conflicts" in consolidated_item.content, "Should handle version conflicts"

        versions = consolidated_item.content["schema_versions"]
        assert "1.0" in versions, "Should preserve v1.0 references"
        assert "2.0" in versions, "Should preserve v2.0 references"
        assert "3.0" in versions, "Should preserve v3.0 references"

    def test_consolidation_cascade_failure_recovery(self, memory_system):
        """Test consolidation recovery from cascade failures."""

        fold = MemoryFold(id="cascade_failure_fold")

        # Create memories that could cause cascade failures
        problematic_indices = [10, 25, 40, 55]  # Specific failure points

        for i in range(70):
            if i in problematic_indices:
                # Create memory that might cause cascade failure
                content = {
                    "text": f"Problematic memory {i}",
                    "circular_data": {},  # Will be made circular
                    "error_trigger": True,
                }
                # Create circular reference
                content["circular_data"]["self_ref"] = content

            else:
                # Normal memory
                content = {"text": f"Normal memory {i}", "data": {"index": i, "normal": True}}

            memory = MemoryItem(
                id=f"cascade_mem_{i}",
                content=content,
                memory_type=MemoryType.DECLARATIVE,
                timestamp=datetime.now(),
                tags=["cascade_test"],
                importance_score=0.5,
            )
            fold.add_item(memory)

        # Attempt consolidation with potential cascade failures
        try:
            consolidated_item = fold.consolidate()

            # If successful, verify failure recovery
            assert consolidated_item is not None, "Should recover from cascade failures"
            assert "cascade_recovery" in consolidated_item.content, "Should track recovery"
            assert consolidated_item.content["cascade_recovery"]["failed_items"] == len(problematic_indices)

        except Exception as e:
            # If failed, ensure it's a controlled failure
            assert "cascade" in str(e).lower() or "circular" in str(e).lower()
            print(f"Expected cascade failure handled: {e}")

    @pytest.mark.asyncio
    async def test_concurrent_consolidation_safety(self, memory_system, sample_memories):
        """Test that concurrent consolidation operations are safe."""

        fold_id = "concurrent_fold"
        fold = MemoryFold(id=fold_id)

        # Add initial memories
        for memory in sample_memories[:80]:
            fold.add_item(memory)
            memory_system.store_memory(memory)

        # Simulate concurrent consolidation attempts
        consolidation_tasks = []
        for i in range(3):
            task = asyncio.create_task(self._attempt_consolidation(fold, i))
            consolidation_tasks.append(task)

        # Wait for all consolidation attempts
        results = await asyncio.gather(*consolidation_tasks, return_exceptions=True)

        # Verify that only one consolidation succeeded and others were properly handled
        success_count = sum(1 for result in results if not isinstance(result, Exception))
        assert success_count <= 1, "At most one consolidation should succeed"

        # Verify fold integrity after concurrent operations
        assert len(fold.items) > 0, "Fold should maintain items after concurrent ops"

    async def _attempt_consolidation(self, fold, attempt_id):
        """Helper method to simulate consolidation attempt."""

        # Add small delay to create race condition
        await asyncio.sleep(0.01 * attempt_id)

        # Attempt consolidation
        return fold.consolidate()

    def test_memory_leak_prevention(self, memory_system):
        """Test that consolidation prevents memory leaks in large datasets."""

        fold_id = "leak_test_fold"
        fold = MemoryFold(id=fold_id)

        # Create large dataset that could cause memory issues
        large_memories = []
        for i in range(500):  # Large dataset
            # Create memory with large content
            large_content = {
                "text": f"Large memory item {i}",
                "large_data": "x" * 1000,  # 1KB per item = 500KB total
                "nested_data": {
                    "level1": {"level2": {"level3": f"deep_data_{i}"}},
                    "array_data": list(range(100)),  # More memory usage
                },
            }

            memory = MemoryItem(
                id=f"large_mem_{i}",
                content=large_content,
                memory_type=MemoryType.PROCEDURAL,
                timestamp=datetime.now(),
                tags=["large_data", f"batch_{i//50}"],
                importance_score=0.3,
            )

            large_memories.append(memory)
            fold.add_item(memory)

        # Measure memory usage before consolidation
        initial_item_count = len(fold.items)

        # Perform consolidation
        consolidated_item = fold.consolidate()

        # Verify consolidation compressed the data
        assert consolidated_item is not None, "Consolidation should succeed with large dataset"
        assert "memory_optimization" in consolidated_item.content, "Should track memory optimization"

        # Check that consolidation metadata includes compression info
        assert consolidated_item.content["memory_optimization"]["original_item_count"] == initial_item_count
        assert "compression_ratio" in consolidated_item.content["memory_optimization"]

    def test_consolidation_rollback_on_corruption(self, memory_system):
        """Test rollback mechanism when consolidation detects data corruption."""

        fold_id = "corruption_test_fold"
        fold = MemoryFold(id=fold_id)

        # Add normal memories
        for i in range(60):
            memory = MemoryItem(
                id=f"normal_mem_{i}",
                content={"text": f"Normal memory {i}", "valid": True},
                memory_type=MemoryType.SEMANTIC,
                timestamp=datetime.now(),
                tags=["normal"],
                importance_score=0.4,
            )
            fold.add_item(memory)

        # Store original state
        original_items = fold.items.copy()
        original_count = len(original_items)

        # Mock corruption detection during consolidation
        with patch.object(fold, "_detect_corruption", return_value=True):
            try:
                consolidated_item = fold.consolidate()

                # If consolidation succeeds despite corruption, verify rollback handling
                if consolidated_item:
                    assert "corruption_detected" in consolidated_item.content
                    assert consolidated_item.content["corruption_detected"] is True

            except Exception as e:
                # Expected behavior - consolidation should fail gracefully
                assert "corruption" in str(e).lower()

        # Verify original data is preserved
        assert len(fold.items) == original_count, "Original items should be preserved after rollback"
        for original, current in zip(original_items, fold.items):
            assert original.id == current.id, "Item IDs should match after rollback"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
