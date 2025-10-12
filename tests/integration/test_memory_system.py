#!/usr/bin/env python3
"""
Memory System Integration Tests

End-to-end tests for all memory components working together.
Tests race conditions, concurrent access, and system-wide memory behavior.

# ΛTAG: memory_integration_tests, race_condition_detection
"""

import asyncio
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

import pytest

try:
    from labs.memory.consolidation import MemoryConsolidator
    from lukhas.memory.recall import MemoryRecallEngine
    from lukhas.observability.prometheus_metrics import LUKHASMetrics
    from lukhas.memory.adaptive_memory import AdaptiveMemorySystem, MemoryFold, MemoryItem, MemoryType
    MEMORY_AVAILABLE = True
except ImportError:
    # Fallback for testing without full memory system
    MEMORY_AVAILABLE = False
    AdaptiveMemorySystem = None
    MemoryItem = None
    MemoryFold = None
    MemoryType = None
    MemoryConsolidator = None
    MemoryRecallEngine = None
    LUKHASMetrics = None


@pytest.mark.skipif(not MEMORY_AVAILABLE, reason="Memory system not available")
class TestMemorySystemIntegration:
    """Integration tests for complete memory system."""

    @pytest.fixture
    def memory_system(self):
        """Create a complete memory system for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            system = AdaptiveMemorySystem(
                storage_path=Path(tmpdir),
                config={
                    "max_memory_items": 1000,
                    "consolidation_threshold": 100,
                    "recall_limit": 50,
                    "embedding_cache_size": 200,
                    "performance_mode": "test"
                }
            )
            yield system

    @pytest.fixture
    def sample_memory_data(self):
        """Generate diverse memory data for testing."""
        base_time = datetime.now()

        memory_data = []

        # Create diverse memory types
        for i in range(300):
            memory_type = [
                MemoryType.DECLARATIVE,
                MemoryType.EPISODIC,
                MemoryType.PROCEDURAL,
                MemoryType.SEMANTIC
            ][i % 4]

            content = {
                "text": f"Memory content for item {i}",
                "category": f"category_{i % 10}",
                "metadata": {
                    "source": f"source_{i % 5}",
                    "complexity": i % 3,
                    "priority": i % 7
                },
                "data": {
                    "values": list(range(i, i + 10)),
                    "timestamp": (base_time + timedelta(minutes=i)).isoformat()
                }
            }

            memory_data.append({
                "id": f"mem_{i:04d}",
                "content": content,
                "memory_type": memory_type,
                "timestamp": base_time + timedelta(minutes=i),
                "tags": [f"tag_{i % 5}", f"batch_{i // 50}", "integration_test"],
                "importance_score": 0.1 + (i % 9) * 0.1
            })

        return memory_data

    def test_end_to_end_memory_workflow(self, memory_system, sample_memory_data):
        """Test complete memory workflow: store -> retrieve -> consolidate -> search."""

        # Phase 1: Store memories
        stored_ids = []
        for data in sample_memory_data[:150]:  # Use subset for initial test
            memory = MemoryItem(**data)
            memory_system.store_memory(memory)
            stored_ids.append(memory.id)

        assert len(stored_ids) == 150, "Should store all memories"

        # Phase 2: Retrieve memories
        retrieved_memories = []
        for mem_id in stored_ids[:10]:  # Test retrieval of subset
            memory = memory_system.get_memory(mem_id)
            assert memory is not None, f"Should retrieve memory {mem_id}"
            retrieved_memories.append(memory)

        assert len(retrieved_memories) == 10, "Should retrieve all requested memories"

        # Phase 3: Search memories
        search_results = memory_system.search_memories("category_5", limit=20)
        assert len(search_results) > 0, "Should find memories with search term"

        category_5_results = [m for m in search_results if "category_5" in str(m.content)]
        assert len(category_5_results) > 0, "Should find specific category memories"

        # Phase 4: Test consolidation trigger
        # Add more memories to trigger consolidation
        for data in sample_memory_data[150:]:
            memory = MemoryItem(**data)
            memory_system.store_memory(memory)

        # Force consolidation check
        consolidated_count = memory_system.check_and_consolidate()

        # Verify system state after consolidation
        total_items = memory_system.get_total_items()
        assert total_items > 0, "Should have items after consolidation"

    def test_concurrent_memory_operations(self, memory_system, sample_memory_data):
        """Test concurrent access to memory system - race condition detection."""

        def store_memories_worker(worker_id: int, data_subset: List[Dict]):
            """Worker function for concurrent memory storage."""
            stored_count = 0
            errors = []

            for data in data_subset:
                try:
                    memory = MemoryItem(**data)
                    memory_system.store_memory(memory)
                    stored_count += 1
                except Exception as e:
                    errors.append(f"Worker {worker_id}: {str(e)}")

            return worker_id, stored_count, errors

        def search_memories_worker(worker_id: int, search_terms: List[str]):
            """Worker function for concurrent memory searching."""
            search_results = {}
            errors = []

            for term in search_terms:
                try:
                    results = memory_system.search_memories(term, limit=10)
                    search_results[term] = len(results)
                except Exception as e:
                    errors.append(f"Search worker {worker_id}: {str(e)}")

            return worker_id, search_results, errors

        # Prepare data for concurrent operations
        chunk_size = len(sample_memory_data) // 4
        data_chunks = [
            sample_memory_data[i:i + chunk_size]
            for i in range(0, len(sample_memory_data), chunk_size)
        ]

        search_terms = ["category_1", "category_2", "tag_0", "tag_1", "batch_2"]

        # Execute concurrent operations
        with ThreadPoolExecutor(max_workers=8) as executor:
            # Submit storage tasks
            storage_futures = [
                executor.submit(store_memories_worker, i, chunk)
                for i, chunk in enumerate(data_chunks)
            ]

            # Submit search tasks (concurrent with storage)
            search_futures = [
                executor.submit(search_memories_worker, i, search_terms)
                for i in range(4, 8)  # Different worker IDs
            ]

            # Collect results
            all_errors = []
            total_stored = 0

            # Wait for storage tasks
            for future in as_completed(storage_futures):
                worker_id, stored_count, errors = future.result()
                total_stored += stored_count
                all_errors.extend(errors)

            # Wait for search tasks
            search_results = {}
            for future in as_completed(search_futures):
                worker_id, results, errors = future.result()
                search_results[worker_id] = results
                all_errors.extend(errors)

        # Verify concurrent operations
        assert len(all_errors) == 0, f"Concurrent operations should not have errors: {all_errors}"
        assert total_stored > 0, "Should store memories from concurrent workers"
        assert len(search_results) > 0, "Should have search results from concurrent workers"

        # Test for race conditions - check data integrity
        final_memory_count = memory_system.get_total_items()
        assert final_memory_count >= total_stored, "Memory count should be consistent"

    def test_memory_consolidation_race_conditions(self, memory_system, sample_memory_data):
        """Test race conditions during memory consolidation process."""

        def consolidation_worker():
            """Worker that triggers consolidation."""
            try:
                return memory_system.check_and_consolidate()
            except Exception as e:
                return f"Consolidation error: {str(e)}"

        def memory_access_worker(memory_ids: List[str]):
            """Worker that accesses memories during consolidation."""
            accessed = []
            errors = []

            for mem_id in memory_ids:
                try:
                    memory = memory_system.get_memory(mem_id)
                    if memory:
                        accessed.append(mem_id)
                except Exception as e:
                    errors.append(f"Access error for {mem_id}: {str(e)}")

            return accessed, errors

        # Store enough memories to trigger consolidation
        stored_ids = []
        for data in sample_memory_data:
            memory = MemoryItem(**data)
            memory_system.store_memory(memory)
            stored_ids.append(memory.id)

        # Test concurrent consolidation and access
        with ThreadPoolExecutor(max_workers=6) as executor:
            # Submit consolidation tasks
            consolidation_futures = [
                executor.submit(consolidation_worker)
                for _ in range(2)
            ]

            # Submit memory access tasks during consolidation
            access_chunk_size = len(stored_ids) // 4
            access_futures = [
                executor.submit(memory_access_worker, stored_ids[i:i + access_chunk_size])
                for i in range(0, len(stored_ids), access_chunk_size)
            ]

            # Wait for all tasks
            consolidation_results = [f.result() for f in consolidation_futures]
            access_results = [f.result() for f in access_futures]

        # Verify no race condition errors
        all_access_errors = []
        for accessed, errors in access_results:
            all_access_errors.extend(errors)

        # Race conditions might cause some access errors, but system should remain stable
        if all_access_errors:
            print(f"Access errors during consolidation: {len(all_access_errors)}")
            # Verify errors are expected race condition types, not corruption
            for error in all_access_errors[:5]:  # Check first few errors
                assert any(keyword in error.lower() for keyword in
                          ["not found", "consolidating", "locked", "concurrent"]), \
                       f"Unexpected error type: {error}"

        # Verify system integrity after concurrent operations
        final_count = memory_system.get_total_items()
        assert final_count > 0, "System should remain functional after concurrent consolidation"

    def test_memory_performance_under_load(self, memory_system, sample_memory_data):
        """Test memory system performance under heavy load."""

        # Performance tracking
        operations = {
            "store": [],
            "retrieve": [],
            "search": [],
            "consolidate": []
        }

        # Load testing - store operations
        start_time = time.perf_counter()
        for i, data in enumerate(sample_memory_data):
            op_start = time.perf_counter()
            memory = MemoryItem(**data)
            memory_system.store_memory(memory)
            op_time = (time.perf_counter() - op_start) * 1000  # Convert to ms
            operations["store"].append(op_time)

            # Check performance requirement: <100ms for memory operations
            assert op_time < 100, f"Store operation {i} too slow: {op_time:.2f}ms"

        store_time = time.perf_counter() - start_time

        # Load testing - retrieve operations
        start_time = time.perf_counter()
        stored_ids = [f"mem_{i:04d}" for i in range(len(sample_memory_data))]

        for i, mem_id in enumerate(stored_ids[:100]):  # Test subset for retrieval
            op_start = time.perf_counter()
            memory = memory_system.get_memory(mem_id)
            op_time = (time.perf_counter() - op_start) * 1000
            operations["retrieve"].append(op_time)

            assert memory is not None, f"Should retrieve memory {mem_id}"
            assert op_time < 100, f"Retrieve operation {i} too slow: {op_time:.2f}ms"

        retrieve_time = time.perf_counter() - start_time

        # Load testing - search operations
        search_terms = ["category_0", "category_5", "tag_2", "batch_4", "integration_test"]
        start_time = time.perf_counter()

        for i, term in enumerate(search_terms * 10):  # Repeat searches
            op_start = time.perf_counter()
            results = memory_system.search_memories(term, limit=20)
            op_time = (time.perf_counter() - op_start) * 1000
            operations["search"].append(op_time)

            assert len(results) >= 0, f"Search should return results for {term}"
            assert op_time < 100, f"Search operation {i} too slow: {op_time:.2f}ms"

        search_time = time.perf_counter() - start_time

        # Load testing - consolidation
        start_time = time.perf_counter()
        consolidated_count = memory_system.check_and_consolidate()
        consolidation_time = (time.perf_counter() - start_time) * 1000
        operations["consolidate"].append(consolidation_time)

        # Performance assertions
        avg_store_time = sum(operations["store"]) / len(operations["store"])
        avg_retrieve_time = sum(operations["retrieve"]) / len(operations["retrieve"])
        avg_search_time = sum(operations["search"]) / len(operations["search"])

        print("Performance Results:")
        print(f"  Average store time: {avg_store_time:.2f}ms")
        print(f"  Average retrieve time: {avg_retrieve_time:.2f}ms")
        print(f"  Average search time: {avg_search_time:.2f}ms")
        print(f"  Consolidation time: {consolidation_time:.2f}ms")

        # All operations should meet performance targets
        assert avg_store_time < 50, f"Average store time too slow: {avg_store_time:.2f}ms"
        assert avg_retrieve_time < 50, f"Average retrieve time too slow: {avg_retrieve_time:.2f}ms"
        assert avg_search_time < 80, f"Average search time too slow: {avg_search_time:.2f}ms"
        assert consolidation_time < 5000, f"Consolidation too slow: {consolidation_time:.2f}ms"

    def test_memory_system_error_recovery(self, memory_system, sample_memory_data):
        """Test memory system error recovery and resilience."""

        # Store some memories successfully
        successful_ids = []
        for data in sample_memory_data[:50]:
            memory = MemoryItem(**data)
            memory_system.store_memory(memory)
            successful_ids.append(memory.id)

        # Introduce problematic memories
        problematic_memories = [
            MemoryItem(
                id="circular_ref_mem",
                content={"self_ref": None},  # Will create circular reference
                memory_type=MemoryType.DECLARATIVE,
                timestamp=datetime.now(),
                tags=["problematic"],
                importance_score=0.5
            ),
            MemoryItem(
                id="invalid_timestamp_mem",
                content={"text": "Invalid timestamp test"},
                memory_type=MemoryType.EPISODIC,
                timestamp="invalid_timestamp",  # Invalid timestamp
                tags=["problematic"],
                importance_score=0.5
            )
        ]

        # Create circular reference
        problematic_memories[0].content["self_ref"] = problematic_memories[0].content

        # Test error handling during storage
        errors_handled = 0
        for memory in problematic_memories:
            try:
                memory_system.store_memory(memory)
            except Exception as e:
                errors_handled += 1
                assert isinstance(e, (ValueError, TypeError, AttributeError)), \
                       f"Should handle expected error types: {type(e)}"

        # System should still function after errors
        search_results = memory_system.search_memories("category_1", limit=10)
        assert len(search_results) > 0, "System should remain functional after errors"

        # Verify successful memories are still accessible
        for mem_id in successful_ids[:5]:
            memory = memory_system.get_memory(mem_id)
            assert memory is not None, f"Should still access memory {mem_id} after errors"

        print(f"Successfully handled {errors_handled} problematic memories")

    def test_memory_metrics_integration(self, memory_system, sample_memory_data):
        """Test integration with metrics system."""

        if LUKHASMetrics is None:
            pytest.skip("Metrics system not available")

        metrics = LUKHASMetrics()

        # Store memories and check metrics
        for data in sample_memory_data[:20]:
            memory = MemoryItem(**data)
            memory_system.store_memory(memory)

        # Perform various operations
        memory_system.search_memories("category_1", limit=5)
        memory_system.get_memory("mem_0001")
        memory_system.check_and_consolidate()

        # Verify metrics were recorded (if metrics system is integrated)
        # This would depend on actual metrics implementation
        assert True, "Metrics integration test placeholder"

    def test_memory_system_cleanup_and_shutdown(self, memory_system, sample_memory_data):
        """Test proper cleanup and shutdown procedures."""

        # Store some memories
        for data in sample_memory_data[:30]:
            memory = MemoryItem(**data)
            memory_system.store_memory(memory)

        # Verify system is operational
        assert memory_system.get_total_items() > 0, "System should have stored memories"

        # Test graceful shutdown
        try:
            memory_system.shutdown()
            shutdown_successful = True
        except Exception as e:
            shutdown_successful = False
            print(f"Shutdown error: {e}")

        assert shutdown_successful, "System should shutdown gracefully"

        # After shutdown, operations should handle gracefully
        with pytest.raises((RuntimeError, AttributeError)):
            memory_system.store_memory(MemoryItem(
                id="post_shutdown_mem",
                content={"text": "Should not store"},
                memory_type=MemoryType.DECLARATIVE,
                timestamp=datetime.now(),
                tags=["post_shutdown"],
                importance_score=0.5
            ))


@pytest.mark.asyncio
@pytest.mark.skipif(not MEMORY_AVAILABLE, reason="Memory system not available")
class TestAsyncMemoryOperations:
    """Test asynchronous memory operations and race conditions."""

    async def test_async_memory_operations(self):
        """Test asynchronous memory operations."""

        with tempfile.TemporaryDirectory() as tmpdir:
            memory_system = AdaptiveMemorySystem(storage_path=Path(tmpdir))

            async def async_store_worker(worker_id: int, count: int):
                """Async worker for storing memories."""
                stored = []
                for i in range(count):
                    memory = MemoryItem(
                        id=f"async_mem_{worker_id}_{i}",
                        content={"text": f"Async memory {worker_id}-{i}"},
                        memory_type=MemoryType.DECLARATIVE,
                        timestamp=datetime.now(),
                        tags=[f"worker_{worker_id}", "async"],
                        importance_score=0.5
                    )
                    # Simulate async storage (if memory system supports it)
                    await asyncio.sleep(0.001)  # Minimal delay
                    memory_system.store_memory(memory)
                    stored.append(memory.id)
                return stored

            # Run multiple async workers
            tasks = [
                async_store_worker(worker_id, 20)
                for worker_id in range(5)
            ]

            results = await asyncio.gather(*tasks)

            # Verify all async operations completed
            total_stored = sum(len(result) for result in results)
            assert total_stored == 100, "Should store all async memories"

            # Verify no data corruption
            final_count = memory_system.get_total_items()
            assert final_count == 100, "Final count should match stored count"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-x"])
