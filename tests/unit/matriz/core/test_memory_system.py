#!/usr/bin/env python3
"""
Comprehensive tests for the MATRIZ Memory System.

Requirements:
- 100% test coverage for matriz/core/memory_system.py
- Test memory operations (store, retrieve, consolidate, decay)
- Test provenance tracking and MATRIZ node generation
- Test memory constraints and eviction policies
- Test performance with pytest-benchmark (50+ ops/sec)
- Test concurrency and thread safety
- Test persistence
"""

import os
import time
import uuid
import threading
import pytest
from matriz.core.memory_system import MemorySystem, MemoryType, MemoryPriority, MemoryQuery
from matriz.core.node_interface import CognitiveNode, NodeState, NodeTrigger


# Helper function to create a MemorySystem instance with specific parameters
def create_memory_system(**kwargs):
    """Factory function for creating MemorySystem instances for tests."""
    params = {
        "context_buffer_size": 10,
        "working_memory_size": 5,
        "episodic_memory_size": 20,
        "semantic_memory_size": 20,
        "decay_enabled": False,
        "consolidation_enabled": False,
    }
    params.update(kwargs)
    return MemorySystem(**params)

# Basic fixtures
@pytest.fixture
def memory_system():
    """Provides a default MemorySystem instance for tests."""
    return create_memory_system()

@pytest.fixture
def persisted_memory_system(tmp_path):
    """Provides a MemorySystem instance with a temporary persistence path."""
    db_path = tmp_path / "test_memory.json"
    return create_memory_system(persistence_path=str(db_path))

# Test data
def get_test_memory_content(text="test content"):
    """Returns a standard dictionary for memory content."""
    return {"data": text, "timestamp": time.time()}


class TestMemoryStoreAndRetrieve:
    """Tests for basic memory store and retrieve operations."""

    @pytest.mark.parametrize("memory_type", list(MemoryType))
    def test_store_memory_item(self, memory_system, memory_type):
        """Test storing a memory item in each memory type."""
        content = get_test_memory_content()
        memory_id = memory_system.store_memory(content, memory_type)

        assert isinstance(memory_id, str)
        stats = memory_system.get_memory_stats()
        assert stats["memory_counts"][memory_type.value] == 1
        assert stats["operations"]["total_stores"] == 1

    @pytest.mark.parametrize(
        "confidence, expected_priority",
        [
            (0.4, MemoryPriority.LOW),
            (0.6, MemoryPriority.MEDIUM),
            (0.8, MemoryPriority.HIGH),
            (0.95, MemoryPriority.CRITICAL),
        ],
    )
    def test_store_memory_item_with_priority(
        self, memory_system, confidence, expected_priority
    ):
        """Test that memory priority is set correctly based on confidence."""
        content = get_test_memory_content()
        memory_id = memory_system.store_memory(
            content, MemoryType.EPISODIC, confidence=confidence
        )
        retrieved = memory_system.episodic_memory[memory_id]
        assert retrieved.priority == expected_priority

    def test_retrieve_memory_item(self, memory_system):
        """Test retrieving a specific memory item."""
        content = get_test_memory_content("retrieve test")
        memory_system.store_memory(content, MemoryType.EPISODIC, tags={"test", "retrieve"})

        query = MemoryQuery(memory_types=[MemoryType.EPISODIC], tags={"test"})
        retrieved = memory_system.retrieve_memories(query)

        assert len(retrieved) == 1
        assert retrieved[0].content["data"] == "retrieve test"
        assert "retrieve" in retrieved[0].tags

    def test_retrieve_with_filters(self, memory_system):
        """Test retrieving with various filters."""
        ts = time.time()
        memory_system.store_memory(
            get_test_memory_content("item1"), MemoryType.EPISODIC, confidence=0.9, salience=0.8, tags={"a", "b"}
        )
        time.sleep(0.01)
        memory_system.store_memory(
            get_test_memory_content("item2"), MemoryType.SEMANTIC, confidence=0.5, salience=0.6, tags={"b", "c"}
        )

        # Filter by confidence
        query = MemoryQuery(min_confidence=0.85)
        assert len(memory_system.retrieve_memories(query)) == 1

        # Filter by salience
        query = MemoryQuery(min_salience=0.7)
        assert len(memory_system.retrieve_memories(query)) == 1

        # Filter by tags
        query = MemoryQuery(tags={"c"})
        assert len(memory_system.retrieve_memories(query)) == 1

        # Filter by time_range (no easy way to test without mocking time, so just basic check)
        query = MemoryQuery(time_range=(int(ts*1000) - 1000, int(time.time()*1000) + 1000))
        assert len(memory_system.retrieve_memories(query)) == 2

    def test_retrieve_updates_access_stats(self, memory_system):
        """Check that retrieval updates last_accessed and access_count."""
        memory_id = memory_system.store_memory(get_test_memory_content(), MemoryType.EPISODIC)

        initial_item = memory_system.episodic_memory[memory_id]
        initial_access_time = initial_item.last_accessed
        initial_access_count = initial_item.access_count
        assert initial_access_count == 0

        time.sleep(0.01) # Ensure timestamp changes
        memory_system.retrieve_memories(MemoryQuery(memory_types=[MemoryType.EPISODIC]))

        updated_item = memory_system.episodic_memory[memory_id]
        assert updated_item.last_accessed > initial_access_time
        assert updated_item.access_count == initial_access_count + 1

    def test_similarity_search(self, memory_system):
        """Test the simple similarity search."""
        memory_system.store_memory(get_test_memory_content("apple banana orange"), MemoryType.EPISODIC)
        memory_system.store_memory(get_test_memory_content("grape kiwi pineapple"), MemoryType.EPISODIC)

        query = MemoryQuery(query_text="orange apple", similarity_search=True)
        results = memory_system.retrieve_memories(query)
        assert len(results) == 1
        assert results[0].content["data"] == "apple banana orange"

        query_no_match = MemoryQuery(query_text="watermelon", similarity_search=True)
        assert not memory_system.retrieve_memories(query_no_match)

    def test_retrieve_non_existent(self, memory_system):
        """Test retrieving with a query that matches no memories."""
        query = MemoryQuery(tags={"nonexistent"})
        assert not memory_system.retrieve_memories(query)

    def test_process_store_operation(self, memory_system):
        """Test the process method for a 'store' operation."""
        input_data = {
            "operation": "store",
            "memory_type": "episodic",
            "content": get_test_memory_content("process store"),
            "tags": ["process"],
        }
        result = memory_system.process(input_data)

        assert memory_system.validate_output(result)
        assert result["result"]["status"] == "stored"
        assert result["confidence"] == 0.95
        assert "matriz_node" in result
        assert result["matriz_node"]["type"] == "MEMORY"
        assert result["matriz_node"]["state"]["operation"] == "store"
        assert len(memory_system.get_trace()) == 1

    def test_process_retrieve_operation(self, memory_system):
        """Test the process method for a 'retrieve' operation."""
        memory_system.store_memory(get_test_memory_content("process retrieve"), MemoryType.SEMANTIC, tags={"process"})

        input_data = {
            "operation": "retrieve",
            "query": {"tags": ["process"], "types": ["semantic"]},
        }
        result = memory_system.process(input_data)

        assert memory_system.validate_output(result)
        assert result["result"]["count"] == 1
        assert result["confidence"] == 0.9
        assert result["matriz_node"]["type"] == "MEMORY"
        assert result["matriz_node"]["state"]["operation"] == "retrieve"

    def test_process_invalid_operation(self, memory_system):
        """Test the process method with an unknown operation."""
        input_data = {"operation": "nonexistent_op"}
        result = memory_system.process(input_data)

        assert "error" in result["result"]
        assert "Unknown memory operation" in result["result"]["error"]
        assert result["confidence"] < 0.5
        assert result["matriz_node"]["state"]["operation"] == "error"

    def test_process_store_invalid_memory_type(self, memory_system):
        """Test storing with an invalid memory type defaults to episodic."""
        input_data = {"operation": "store", "memory_type": "invalid_type", "content": {}}
        result = memory_system.process(input_data)

        assert result["result"]["status"] == "stored"
        assert result["matriz_node"]["state"]["memory_type"] == "episodic"
        stats = memory_system.get_memory_stats()
        assert stats["memory_counts"]["episodic"] == 1


class TestMemoryManagement:
    """Tests for memory management, including eviction, decay, and consolidation."""

    def test_working_memory_eviction(self, memory_system):
        """Test that the least important item is evicted from working memory."""
        # Fill working memory to capacity
        for i in range(memory_system.working_memory_size):
            memory_system.store_memory(
                get_test_memory_content(f"item {i}"),
                MemoryType.WORKING,
                confidence=0.5,
                salience=0.5,
            )

        # Add one more item with higher importance
        memory_system.store_memory(
            get_test_memory_content("important item"),
            MemoryType.WORKING,
            confidence=0.9,
            salience=0.9,
        )

        assert len(memory_system.working_memory) == memory_system.working_memory_size
        assert any(
            "important item" in v.content["data"] for v in memory_system.working_memory.values()
        )

    def test_episodic_memory_eviction(self, memory_system):
        """Test eviction from episodic memory."""
        # Fill memory almost to capacity with normal items
        for i in range(memory_system.episodic_memory_size - 1):
            memory_system.store_memory(
                get_test_memory_content(f"item {i}"),
                MemoryType.EPISODIC,
                confidence=0.5,
                salience=0.5,
            )

        # Add a low-importance item that should be evicted
        eviction_candidate_id = memory_system.store_memory(
            get_test_memory_content("to be evicted"),
            MemoryType.EPISODIC,
            confidence=0.1,
            salience=0.1,
        )

        # Now memory is full. Add one more high-importance item to trigger eviction.
        important_item_id = memory_system.store_memory(
            get_test_memory_content("important"),
            MemoryType.EPISODIC,
            confidence=0.9,
            salience=0.9,
        )

        assert len(memory_system.episodic_memory) == memory_system.episodic_memory_size
        assert eviction_candidate_id not in memory_system.episodic_memory
        assert important_item_id in memory_system.episodic_memory

    def test_memory_decay(self):
        """Test the memory decay mechanism."""
        memory_system = create_memory_system(decay_enabled=True)
        content = get_test_memory_content()
        memory_id = memory_system.store_memory(
            content, MemoryType.EPISODIC, confidence=0.8, salience=0.8
        )

        # Manually set last_accessed to simulate time passing (e.g., 2 hours ago)
        two_hours_ago = int(time.time() * 1000) - 2 * 3600 * 1000
        memory_system.episodic_memory[memory_id].last_accessed = two_hours_ago

        decayed_count = memory_system.decay_memories()
        assert decayed_count == 0  # Should not be removed yet

        decayed_item = memory_system.episodic_memory[memory_id]
        assert decayed_item.confidence < 0.8
        assert decayed_item.salience < 0.8

    def test_memory_decay_removal(self):
        """Test that decay removes memories with very low confidence."""
        memory_system = create_memory_system(decay_enabled=True)
        memory_id = memory_system.store_memory(
            get_test_memory_content(), MemoryType.EPISODIC, confidence=0.11
        )

        # Simulate a long time passing
        far_in_the_past = int(time.time() * 1000) - 10 * 3600 * 1000
        memory_system.episodic_memory[memory_id].last_accessed = far_in_the_past

        decayed_count = memory_system.decay_memories()
        assert decayed_count == 1
        assert memory_id not in memory_system.episodic_memory

    def test_memory_consolidation(self):
        """Test the memory consolidation mechanism."""
        memory_system = create_memory_system(consolidation_enabled=True)

        # Create a memory item that meets consolidation criteria
        past_timestamp = int(time.time() * 1000) - 25 * 3600 * 1000 # 25 hours ago
        memory_id = memory_system.store_memory(get_test_memory_content(), MemoryType.EPISODIC)

        item = memory_system.episodic_memory[memory_id]
        item.access_count = 5
        item.confidence = 0.7
        item.created_timestamp = past_timestamp

        consolidated_count = memory_system.consolidate_memories()

        assert consolidated_count == 1
        assert memory_id not in memory_system.episodic_memory
        assert memory_id in memory_system.consolidated_memory

        consolidated_item = memory_system.consolidated_memory[memory_id]
        rule = memory_system.consolidation_rules
        assert consolidated_item.confidence == 0.7 + rule.priority_boost

    def test_clear_memory_type(self, memory_system):
        """Test clearing all memories of a specific type."""
        memory_system.store_memory(get_test_memory_content(), MemoryType.SEMANTIC)
        memory_system.store_memory(get_test_memory_content(), MemoryType.SEMANTIC)

        assert memory_system.get_memory_stats()["memory_counts"]["semantic"] == 2
        cleared_count = memory_system.clear_memory_type(MemoryType.SEMANTIC)

        assert cleared_count == 2
        assert memory_system.get_memory_stats()["memory_counts"]["semantic"] == 0


class TestProvenanceAndMatrizNodes:
    """Tests for MATRIZ node generation and provenance tracking."""

    def test_matriz_node_validation_utility(self, memory_system):
        """Test the validate_matriz_node utility with valid and invalid nodes."""
        input_data = {"operation": "store", "content": {}, "memory_type": "episodic"}
        result = memory_system.process(input_data)

        # Test with a valid node
        valid_node = result["matriz_node"]
        assert memory_system.validate_matriz_node(valid_node)

        # Test with invalid nodes
        invalid_node_no_state = valid_node.copy()
        del invalid_node_no_state["state"]
        assert not memory_system.validate_matriz_node(invalid_node_no_state)

        invalid_node_bad_confidence = valid_node.copy()
        invalid_node_bad_confidence["state"] = {"confidence": 1.1, "salience": 0.5}
        assert not memory_system.validate_matriz_node(invalid_node_bad_confidence)

    def test_process_operations_generate_valid_nodes(self, memory_system):
        """Ensure all process operations generate valid MATRIZ nodes."""
        operations = [
            {"operation": "store", "memory_type": "working", "content": {}},
            {"operation": "retrieve", "query": {}},
            {"operation": "consolidate"},
            {"operation": "decay"},
            {"operation": "stats"},
        ]
        for op in operations:
            result = memory_system.process(op)
            assert memory_system.validate_output(result), f"Output validation failed for {op['operation']}"
            assert memory_system.validate_matriz_node(result["matriz_node"]), f"Node validation failed for {op['operation']}"
            assert result["matriz_node"]["type"] == "MEMORY"

    def test_trace_id_propagation(self, memory_system):
        """Test that trace_id is correctly propagated to the MATRIZ node."""
        trace_id = f"test-trace-{uuid.uuid4()}"
        input_data = {"operation": "store", "content": {}, "memory_type": "episodic", "trace_id": trace_id}
        result = memory_system.process(input_data)

        assert result["matriz_node"]["provenance"]["trace_id"] == trace_id

    def test_deterministic_hash_for_trace_id(self, memory_system):
        """Test that a deterministic hash is used as trace_id when not provided."""
        input_data = {"operation": "store", "content": {"a": 1}, "memory_type": "episodic"}
        result1 = memory_system.process(input_data)

        input_data_same = {"operation": "store", "content": {"a": 1}, "memory_type": "episodic"}
        result2 = memory_system.process(input_data_same)

        assert result1["matriz_node"]["provenance"]["trace_id"] == result2["matriz_node"]["provenance"]["trace_id"]

    def test_error_response_generation(self, memory_system):
        """Test that error responses are structured correctly with a valid MATRIZ node."""
        input_data = {"operation": ""} # Invalid operation
        result = memory_system.process(input_data)

        assert memory_system.validate_output(result)
        assert "error" in result["result"]
        error_node = result["matriz_node"]
        assert error_node["state"]["risk"] > 0.5
        assert error_node["reflections"][0]["reflection_type"] == "regret"


class TestPerformanceAndConcurrency:
    """Tests for performance, concurrency, and memory constraints."""

    def test_store_throughput(self, benchmark):
        """Benchmark the store_memory operation."""
        ms = create_memory_system()
        content = get_test_memory_content()

        def store_op():
            ms.store_memory(content, MemoryType.EPISODIC)

        benchmark(store_op)
        assert benchmark.stats.stats.ops > 50  # Check for 50+ ops/sec

    def test_retrieve_throughput(self, benchmark):
        """Benchmark the retrieve_memories operation."""
        ms = create_memory_system()
        ms.store_memory(get_test_memory_content(), MemoryType.EPISODIC, tags={"perf"})
        query = MemoryQuery(tags={"perf"})

        benchmark(ms.retrieve_memories, query)
        assert benchmark.stats.stats.ops > 50

    def test_thread_safety(self):
        """Test concurrent read/write operations from multiple threads."""
        ms = create_memory_system()
        num_threads = 10
        ops_per_thread = 50
        errors = []

        def worker(thread_id):
            for i in range(ops_per_thread):
                try:
                    if i % 2 == 0:
                        ms.store_memory(
                            get_test_memory_content(f"thread-{thread_id}-item-{i}"),
                            MemoryType.EPISODIC,
                        )
                    else:
                        ms.retrieve_memories(MemoryQuery(limit=5))
                except Exception as e:
                    errors.append(e)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(num_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors
        total_stores = num_threads * (ops_per_thread // 2)
        assert ms.get_memory_stats()["operations"]["total_stores"] == total_stores

    def test_memory_usage_constraint(self):
        """Test that memory usage stays within a reasonable limit."""
        # This is a proxy test, as precise memory measurement is complex.
        # It ensures the system doesn't grow uncontrollably.
        # In a real-world scenario, a more robust tool like memory-profiler would be used.
        ms = MemorySystem(
            episodic_memory_size=10000, # Large capacity to store more objects
            semantic_memory_size=10000
        )

        # Store a large number of reasonably sized objects
        num_items = 20000
        for i in range(num_items):
            ms.store_memory(
                {"id": i, "data": "x" * 100, "nested": {"a": [1,2,3]}}, # ~150-200 bytes
                MemoryType.EPISODIC
            )

        # Check that capacity limits are still respected
        assert len(ms.episodic_memory) <= ms.episodic_memory_size

        # A true memory usage test is outside the scope of pytest alone,
        # but we can confirm that the number of objects is bounded.
        # The 100MB constraint would be enforced by infrastructure/monitoring.
        # This test primarily ensures eviction logic works at a large scale.
        total_memories = sum(ms.get_memory_stats()["memory_counts"].values())
        assert total_memories <= (ms.episodic_memory_size + ms.semantic_memory_size +
                                   ms.working_memory_size + ms.context_buffer_size)


class TestPersistence:
    """Tests for saving and loading memory to/from a file."""

    def test_save_and_load_memories(self, tmp_path):
        """Test that memories can be saved to a file and reloaded."""
        db_path = tmp_path / "test_persistence.json"

        # Create an instance and populate it with data
        ms1 = create_memory_system(persistence_path=str(db_path))
        ms1.store_memory(get_test_memory_content("ep1"), MemoryType.EPISODIC)
        ms1.store_memory(get_test_memory_content("sem1"), MemoryType.SEMANTIC)

        # Save memories by deleting the object
        del ms1

        # Create a new instance that should load the persisted data
        ms2 = create_memory_system(persistence_path=str(db_path))

        # Check that the data was loaded correctly
        stats = ms2.get_memory_stats()
        assert stats["memory_counts"]["episodic"] == 1
        assert stats["memory_counts"]["semantic"] == 1

        retrieved = ms2.retrieve_memories(MemoryQuery(query_text="ep1"))
        assert len(retrieved) == 1
        assert retrieved[0].content["data"] == "ep1"

    def test_load_non_existent_file(self, tmp_path):
        """Test that loading from a non-existent file does not raise an error."""
        db_path = tmp_path / "non_existent.json"
        ms = create_memory_system(persistence_path=str(db_path))

        # Should initialize with empty memories
        assert sum(ms.get_memory_stats()["memory_counts"].values()) == 0

    def test_persistence_on_destruction(self, tmp_path):
        """Verify that the __del__ method saves memories."""
        db_path = tmp_path / "del_test.json"
        ms = create_memory_system(persistence_path=str(db_path))
        ms.store_memory(get_test_memory_content("del test"), MemoryType.WORKING)

        # This should trigger the __del__ method and save the memory
        del ms

        assert db_path.exists()

        # Verify content was saved
        ms_reloaded = create_memory_system(persistence_path=str(db_path))
        assert ms_reloaded.get_memory_stats()["memory_counts"]["working"] == 1


class TestEdgeCasesAndCoverage:
    """Tests for edge cases and to achieve 100% test coverage."""

    def test_process_exception_handling(self, memory_system, mocker):
        """Test that the process method handles exceptions gracefully."""
        mocker.patch.object(memory_system, "_handle_store_operation", side_effect=Exception("mock error"))
        input_data = {"operation": "store", "content": {}}
        result = memory_system.process(input_data)

        assert "error" in result["result"]
        assert "Memory operation failed: mock error" in result["result"]["error"]

    @pytest.mark.parametrize(
        "invalid_output",
        [
            {"result": {}, "confidence": 0.9, "matriz_node": {}}, # Missing processing_time
            {"result": {}, "confidence": "bad", "matriz_node": {}, "processing_time": 0.1}, # bad confidence type
            {"result": {}, "confidence": 1.1, "matriz_node": {}, "processing_time": 0.1}, # bad confidence value
        ]
    )
    def test_validate_output_failures(self, memory_system, invalid_output):
        """Test validate_output with various invalid inputs."""
        assert not memory_system.validate_output(invalid_output)

    def test_eviction_from_empty_memory(self, memory_system):
        """Test that eviction methods don't fail on empty memory stores."""
        memory_system._evict_from_working_memory()
        memory_system._evict_from_episodic_memory()
        memory_system._evict_from_semantic_memory()
        # No assertions needed, just confirming no exceptions are raised.

    def test_persistence_with_no_path(self):
        """Test that save/load methods do nothing if persistence_path is None."""
        ms = create_memory_system(persistence_path=None)
        ms._save_memories() # Should not raise an error
        ms._load_memories() # Should not raise an error

    def test_similarity_with_empty_inputs(self, memory_system):
        """Test _calculate_similarity with empty inputs."""
        assert memory_system._calculate_similarity("", {"a": "b"}) == 0.0
        assert memory_system._calculate_similarity("test", {}) == 0.0

    def test_automatic_decay_trigger(self, memory_system, mocker):
        """Test that decay is automatically triggered after a time interval."""
        mock_decay = mocker.patch.object(memory_system, "decay_memories")
        memory_system.decay_enabled = True

        # Simulate time passing beyond the 1-hour threshold
        mocker.patch("time.time", return_value=memory_system.last_decay + 3601)

        memory_system.store_memory(get_test_memory_content(), MemoryType.EPISODIC)
        mock_decay.assert_called_once()

    def test_automatic_consolidation_trigger(self, memory_system, mocker):
        """Test that consolidation is automatically triggered after a time interval."""
        mock_consolidate = mocker.patch.object(memory_system, "consolidate_memories")
        memory_system.consolidation_enabled = True

        # Simulate time passing beyond the 24-hour threshold
        mocker.patch("time.time", return_value=memory_system.last_consolidation + 86401)

        memory_system.store_memory(get_test_memory_content(), MemoryType.EPISODIC)
        mock_consolidate.assert_called_once()

    def test_validate_output_exception(self, memory_system):
        """Test the try-except block in validate_output."""
        assert not memory_system.validate_output({"result": None}) # Should trigger exception

    def test_validate_output_matriz_node(self, memory_system):
        """Test MATRIZ node validation in validate_output."""
        input_data = {"operation": "stats"}
        result = memory_system.process(input_data)

        # Test with an invalid node type
        result["matriz_node"]["type"] = "INVALID_TYPE"
        assert not memory_system.validate_output(result)

    def test_filter_memories_no_similarity_search(self, memory_system):
        """Test _filter_memories without similarity search."""
        memory_system.store_memory(get_test_memory_content("text"), MemoryType.EPISODIC)
        query = MemoryQuery(query_text="text", similarity_search=False)
        # This branch is not hit if similarity_search is True.
        # This test is to cover that branch. After the fix, it should now find the item.
        assert len(memory_system.retrieve_memories(query)) == 1

    def test_process_no_operation(self, memory_system):
        """Test process method with no operation specified."""
        result = memory_system.process({})
        assert "error" in result["result"]
        assert "No memory operation specified" in result["result"]["error"]


class TestCoverageFinishing:
    """A final set of tests to reach 100% coverage."""

    def test_store_with_auto_maintenance(self, mocker):
        """Test that store_memory can trigger automatic maintenance."""
        ms = create_memory_system(decay_enabled=True, consolidation_enabled=True)
        mocker.patch.object(ms, "_maybe_trigger_decay")
        mocker.patch.object(ms, "_maybe_trigger_consolidation")

        ms.store_memory(get_test_memory_content(), MemoryType.EPISODIC)

        ms._maybe_trigger_decay.assert_called_once()
        ms._maybe_trigger_consolidation.assert_called_once()

    def test_consolidation_from_working_memory(self):
        """Test consolidation of an item from working memory."""
        ms = create_memory_system(consolidation_enabled=True)
        past_timestamp = int(time.time() * 1000) - 25 * 3600 * 1000
        memory_id = ms.store_memory(get_test_memory_content(), MemoryType.WORKING)

        item = ms.working_memory[memory_id]
        item.access_count = 5
        item.confidence = 0.7
        item.created_timestamp = past_timestamp

        consolidated_count = ms.consolidate_memories()
        assert consolidated_count == 1
        assert memory_id not in ms.working_memory
        assert memory_id in ms.consolidated_memory

    def test_decay_from_semantic_memory(self):
        """Test decay of an item from semantic memory."""
        ms = create_memory_system(decay_enabled=True)
        memory_id = ms.store_memory(
            get_test_memory_content(), MemoryType.SEMANTIC, confidence=0.11
        )
        far_in_the_past = int(time.time() * 1000) - 10 * 3600 * 1000
        ms.semantic_memory[memory_id].last_accessed = far_in_the_past

        decayed_count = ms.decay_memories()
        assert decayed_count == 1
        assert memory_id not in ms.semantic_memory

    def test_semantic_memory_eviction(self, memory_system):
        """Test eviction from semantic memory."""
        for i in range(memory_system.semantic_memory_size):
            memory_system.store_memory(get_test_memory_content(f"sem {i}"), MemoryType.SEMANTIC)

        eviction_candidate_id = list(memory_system.semantic_memory.keys())[0]

        memory_system.store_memory(
            get_test_memory_content("important sem"), MemoryType.SEMANTIC, confidence=0.99
        )

        assert len(memory_system.semantic_memory) == memory_system.semantic_memory_size
        assert eviction_candidate_id not in memory_system.semantic_memory

    def test_process_retrieve_with_time_range(self, memory_system):
        """Test retrieve via process with a time_range filter."""
        start_ts = int(time.time() * 1000)
        memory_system.store_memory(get_test_memory_content(), MemoryType.EPISODIC)
        end_ts = int(time.time() * 1000)

        input_data = {
            "operation": "retrieve",
            "query": {"time_range": (start_ts, end_ts)}
        }
        result = memory_system.process(input_data)
        assert result["result"]["count"] == 1

    def test_process_retrieve_with_bad_memory_type(self, memory_system):
        """Test retrieve via process with an invalid memory type in the query."""
        input_data = {
            "operation": "retrieve",
            "query": {"types": ["non_existent_type"]}
        }
        with pytest.raises(ValueError):
            memory_system.process(input_data)
