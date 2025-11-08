import pytest
from matriz.core.memory_system import MemorySystem, MemoryType, MemoryQuery, MemoryItem, MemoryPriority
import time
import os
import psutil

# Test fixtures
@pytest.fixture
def memory_system():
    """Provides a default MemorySystem instance for tests."""
    return MemorySystem()

@pytest.fixture
def small_memory_system():
    """Provides a MemorySystem with small capacity for testing eviction."""
    return MemorySystem(
        context_buffer_size=2,
        working_memory_size=2,
        episodic_memory_size=2,
        semantic_memory_size=2
    )

@pytest.fixture
def persistent_memory_system(tmp_path):
    """Provides a MemorySystem with a temporary persistence path."""
    db_path = tmp_path / "test_memory.json"
    return MemorySystem(persistence_path=str(db_path))

# 1. Initialization and Basic Functionality Tests
def test_initialization_default(memory_system):
    """Test that MemorySystem initializes with correct default values."""
    assert memory_system.tenant == "default"
    assert memory_system.context_buffer_size == 100
    assert memory_system.working_memory_size == 20
    assert memory_system.episodic_memory_size == 1000
    assert memory_system.semantic_memory_size == 5000
    assert memory_system.decay_enabled is True
    assert memory_system.consolidation_enabled is True
    assert memory_system.persistence_path is None

def test_initialization_custom():
    """Test that MemorySystem initializes with custom values."""
    ms = MemorySystem(
        tenant="test_tenant",
        context_buffer_size=10,
        working_memory_size=5,
        decay_enabled=False,
        consolidation_enabled=False
    )
    assert ms.tenant == "test_tenant"
    assert ms.context_buffer_size == 10
    assert ms.working_memory_size == 5
    assert ms.decay_enabled is False
    assert ms.consolidation_enabled is False

def test_process_invalid_operation(memory_system):
    """Test process() with an unknown operation."""
    input_data = {"operation": "non_existent_op"}
    result = memory_system.process(input_data)
    assert "error" in result["result"]
    assert "Unknown memory operation" in result["result"]["error"]
    assert result["confidence"] < 0.2
    assert result["matriz_node"]["state"]["risk"] > 0.5

def test_process_no_operation(memory_system):
    """Test process() with no operation specified."""
    result = memory_system.process({})
    assert "error" in result["result"]
    assert "No memory operation specified" in result["result"]["error"]
    assert result["confidence"] < 0.2

def test_validate_output(memory_system):
    """Test the validate_output method."""
    # Test a valid output
    input_data = {
        "operation": "store",
        "memory_type": "episodic",
        "content": {"q": "test"},
    }
    valid_output = memory_system.process(input_data)
    assert memory_system.validate_output(valid_output) is True

    # Test invalid outputs
    invalid_output_1 = valid_output.copy()
    del invalid_output_1["matriz_node"]
    assert memory_system.validate_output(invalid_output_1) is False

    invalid_output_2 = valid_output.copy()
    invalid_output_2["confidence"] = 1.1 # out of range
    assert memory_system.validate_output(invalid_output_2) is False

    invalid_output_3 = valid_output.copy()
    invalid_output_3["matriz_node"]["type"] = "INVALID_TYPE"
    assert memory_system.validate_output(invalid_output_3) is False

# 2. Core Memory Operations Tests
def test_store_memory_basic(memory_system):
    """Test basic memory storage."""
    mem_id = memory_system.store_memory({"data": "test"}, MemoryType.EPISODIC)
    assert mem_id in memory_system.episodic_memory
    assert memory_system.episodic_memory[mem_id].content["data"] == "test"
    assert memory_system.stats["total_stores"] == 1

def test_store_memory_priority_assignment(memory_system):
    """Test that priority is correctly assigned based on confidence."""
    mem_id_low = memory_system.store_memory({}, MemoryType.EPISODIC, confidence=0.4)
    assert memory_system.episodic_memory[mem_id_low].priority == MemoryPriority.LOW

    mem_id_medium = memory_system.store_memory({}, MemoryType.EPISODIC, confidence=0.6)
    assert memory_system.episodic_memory[mem_id_medium].priority == MemoryPriority.MEDIUM

    mem_id_high = memory_system.store_memory({}, MemoryType.EPISODIC, confidence=0.8)
    assert memory_system.episodic_memory[mem_id_high].priority == MemoryPriority.HIGH

    mem_id_critical = memory_system.store_memory({}, MemoryType.EPISODIC, confidence=0.95)
    assert memory_system.episodic_memory[mem_id_critical].priority == MemoryPriority.CRITICAL

def test_retrieve_memories_simple(memory_system):
    """Test simple memory retrieval."""
    memory_system.store_memory({"text": "alpha"}, MemoryType.SEMANTIC, tags={"group1"})
    memory_system.store_memory({"text": "beta"}, MemoryType.EPISODIC, tags={"group2"})

    query = MemoryQuery(memory_types=[MemoryType.SEMANTIC])
    results = memory_system.retrieve_memories(query)

    assert len(results) == 1
    assert results[0].content["text"] == "alpha"
    assert memory_system.stats["total_retrievals"] == 1

def test_retrieve_memories_advanced_filters(memory_system):
    """Test advanced filtering capabilities of memory retrieval."""
    t1 = int(time.time() * 1000)
    memory_system.store_memory({"text": "gamma"}, MemoryType.EPISODIC, confidence=0.9, salience=0.9, tags={"test", "gamma"})
    time.sleep(0.01)
    memory_system.store_memory({"text": "delta"}, MemoryType.EPISODIC, confidence=0.4, salience=0.9, tags={"test", "delta"})
    time.sleep(0.01)
    t2 = int(time.time() * 1000)

    # Filter by confidence
    query_conf = MemoryQuery(min_confidence=0.5)
    assert len(memory_system.retrieve_memories(query_conf)) == 1

    # Filter by salience
    query_sal = MemoryQuery(min_salience=0.95)
    assert len(memory_system.retrieve_memories(query_sal)) == 0

    # Filter by tags
    query_tags = MemoryQuery(tags={"delta"})
    assert len(memory_system.retrieve_memories(query_tags)) == 1

    # Filter by time range
    query_time = MemoryQuery(time_range=(t1, t2))
    assert len(memory_system.retrieve_memories(query_time)) == 2

def test_similarity_search(memory_system):
    """Test the text-based similarity search."""
    memory_system.store_memory({"desc": "a quick brown fox"}, MemoryType.SEMANTIC)
    memory_system.store_memory({"desc": "a lazy dog"}, MemoryType.SEMANTIC)

    query = MemoryQuery(query_text="brown fox")
    results = memory_system.retrieve_memories(query)
    assert len(results) == 1
    assert results[0].content["desc"] == "a quick brown fox"

# 3. Memory Management and Maintenance Tests
def test_eviction_working_memory(small_memory_system):
    """Test that eviction works for working memory."""
    small_memory_system.store_memory({"item": 1}, MemoryType.WORKING, confidence=0.1)
    small_memory_system.store_memory({"item": 2}, MemoryType.WORKING, confidence=0.9)
    assert len(small_memory_system.working_memory) == 2

    # This should evict the item with the lowest confidence
    small_memory_system.store_memory({"item": 3}, MemoryType.WORKING, confidence=0.5)
    assert len(small_memory_system.working_memory) == 2

    remaining_confidences = [m.confidence for m in small_memory_system.working_memory.values()]
    assert 0.1 not in remaining_confidences
    assert small_memory_system.stats["evictions"] == 1

def test_eviction_episodic_memory(small_memory_system):
    """Test that eviction works for episodic memory."""
    small_memory_system.store_memory({"item": 1}, MemoryType.EPISODIC, confidence=0.1)
    small_memory_system.store_memory({"item": 2}, MemoryType.EPISODIC, confidence=0.9)
    small_memory_system.store_memory({"item": 3}, MemoryType.EPISODIC, confidence=0.5)
    assert len(small_memory_system.episodic_memory) == 2
    remaining_confidences = [m.confidence for m in small_memory_system.episodic_memory.values()]
    assert 0.1 not in remaining_confidences
    assert small_memory_system.stats["evictions"] == 1

def test_eviction_semantic_memory(small_memory_system):
    """Test that eviction works for semantic memory."""
    small_memory_system.store_memory({"item": 1}, MemoryType.SEMANTIC, confidence=0.1)
    small_memory_system.store_memory({"item": 2}, MemoryType.SEMANTIC, confidence=0.9)
    small_memory_system.store_memory({"item": 3}, MemoryType.SEMANTIC, confidence=0.5)
    assert len(small_memory_system.semantic_memory) == 2
    remaining_confidences = [m.confidence for m in small_memory_system.semantic_memory.values()]
    assert 0.1 not in remaining_confidences
    assert small_memory_system.stats["evictions"] == 1

def test_decay_memories(memory_system):
    """Test that memory decay reduces confidence and removes weak memories."""
    mem_id = memory_system.store_memory({"data": "to decay"}, MemoryType.EPISODIC, confidence=0.11)

    # Manually adjust time to simulate passage of time for decay
    # With confidence 0.11 and 2 hours passed, decay should be 0.11 - (0.01 * 2) = 0.09, which is < 0.1
    memory_system.episodic_memory[mem_id].last_accessed -= 2 * 3600 * 1000 # 2 hours ago

    decayed_count = memory_system.decay_memories()

    assert decayed_count > 0
    assert mem_id not in memory_system.episodic_memory # Should be removed as confidence drops
    assert memory_system.stats["decays"] > 0

def test_consolidation(memory_system):
    """Test that important memories get consolidated."""
    # Create a candidate for consolidation
    mem_id = memory_system.store_memory(
        {"event": "important meeting"},
        MemoryType.EPISODIC,
        confidence=0.7,
    )

    # Simulate conditions for consolidation
    mem_item = memory_system.episodic_memory[mem_id]
    mem_item.access_count = 5
    mem_item.created_timestamp -= 25 * 3600 * 1000 # 25 hours ago

    consolidated_count = memory_system.consolidate_memories()
    assert consolidated_count == 1
    assert mem_id not in memory_system.episodic_memory
    assert mem_id in memory_system.consolidated_memory
    assert memory_system.stats["consolidations"] == 1

def test_clear_memory_type(memory_system):
    """Test clearing a specific type of memory."""
    memory_system.store_memory({"data": "test1"}, MemoryType.EPISODIC)
    memory_system.store_memory({"data": "test2"}, MemoryType.SEMANTIC)

    assert len(memory_system.episodic_memory) == 1

    cleared_count = memory_system.clear_memory_type(MemoryType.EPISODIC)

    assert cleared_count == 1
    assert len(memory_system.episodic_memory) == 0
    assert len(memory_system.semantic_memory) == 1 # Ensure other types are unaffected


# 4. Persistence Tests
def test_save_and_load_memories(persistent_memory_system):
    """Test saving memories to and loading from a file."""
    path = persistent_memory_system.persistence_path

    # Store some data
    persistent_memory_system.store_memory({"data": "one"}, MemoryType.SEMANTIC)
    persistent_memory_system.store_memory({"data": "two"}, MemoryType.EPISODIC)

    # Explicitly save
    persistent_memory_system._save_memories()

    assert os.path.exists(path)

    # Create a new instance to load the data
    new_ms = MemorySystem(persistence_path=path)
    assert len(new_ms.semantic_memory) == 1
    assert len(new_ms.episodic_memory) == 1

    query = MemoryQuery(query_text="one")
    assert len(new_ms.retrieve_memories(query)) > 0

# 5. Performance and Constraint Tests
def test_throughput_store(benchmark):
    """Benchmark the store_memory operation."""
    ms = MemorySystem()

    def store_op():
        ms.store_memory({"data": "benchmark"}, MemoryType.EPISODIC)

    benchmark(store_op)
    # The benchmark framework will calculate ops/sec, which should be > 50

def test_throughput_retrieve(benchmark):
    """Benchmark the retrieve_memories operation."""
    ms = MemorySystem()
    ms.store_memory({"text": "find me"}, MemoryType.SEMANTIC)
    query = MemoryQuery(query_text="find me")

    benchmark(ms.retrieve_memories, query)
    # The benchmark framework will calculate ops/sec, which should be > 50

def test_memory_constraint():
    """Test that the memory system stays within its memory limits."""
    # This is a high-level test; precise memory usage can be tricky to assert
    process = psutil.Process(os.getpid())
    mem_before = process.memory_info().rss / (1024 * 1024) # in MB

    ms = MemorySystem(episodic_memory_size=5000, semantic_memory_size=5000)

    for i in range(10000): # Store 10,000 items
        ms.store_memory({"id": i, "payload": "A" * 100}, MemoryType.EPISODIC if i % 2 == 0 else MemoryType.SEMANTIC)

    mem_after = process.memory_info().rss / (1024 * 1024)
    mem_used = mem_after - mem_before

    print(f"Memory used by system: {mem_used:.2f} MB")

    # Allow a generous buffer, as other parts of the test runner also use memory
    assert mem_used < 100

# 6. Provenance and Architectural Tests
def test_provenance_chaining():
    """Test that a sequence of operations creates a coherent provenance chain."""
    ms = MemorySystem()

    # 1. Store a fact
    store_result = ms.process({
        "operation": "store",
        "memory_type": "semantic",
        "content": {"fact": "sky is blue"},
        "trace_id": "trace-123"
    })
    store_node = store_result["matriz_node"]
    assert store_node["provenance"]["trace_id"] == "trace-123"

    # 2. Retrieve related info
    retrieve_result = ms.process({
        "operation": "retrieve",
        "query": {"text": "sky"},
        "trace_id": "trace-123"
    })
    retrieve_node = retrieve_result["matriz_node"]
    assert retrieve_node["provenance"]["trace_id"] == "trace-123"

    # Check that a trace can be reconstructed
    trace = ms.get_trace()
    assert len(trace) == 2
    assert all(node["provenance"]["trace_id"] == "trace-123" for node in trace)

def test_context_preservation(memory_system):
    """Test that related information can be retrieved to form a context."""
    # Store a general concept
    memory_system.store_memory(
        {"concept": "color", "value": "blue"},
        MemoryType.SEMANTIC,
        tags={"general_knowledge"}
    )
    # Store a specific event
    memory_system.store_memory(
        {"event": "observed sky", "color": "blue"},
        MemoryType.EPISODIC,
        tags={"observation"}
    )

    # Retrieve memories related to "blue"
    query = MemoryQuery(query_text="blue", memory_types=[MemoryType.SEMANTIC, MemoryType.EPISODIC])
    results = memory_system.retrieve_memories(query)

    assert len(results) == 2
    # This demonstrates that both the general concept and the specific episode
    # can be retrieved together, preserving the full context.
    types_found = {res.memory_type for res in results}
    assert MemoryType.SEMANTIC in types_found
    assert MemoryType.EPISODIC in types_found

# 7. Additional Coverage Tests
def test_filter_memories_edge_cases(memory_system):
    """Test edge cases for memory filtering."""
    memory_system.store_memory({"text": "tagged"}, MemoryType.EPISODIC, tags={"unique_tag"})

    # Test filtering by a tag that doesn't exist
    query_no_match = MemoryQuery(tags={"non_existent_tag"})
    assert len(memory_system.retrieve_memories(query_no_match)) == 0

    # Test time range where no memories fall within
    future_time = int(time.time() * 1000) + 10000
    query_time_no_match = MemoryQuery(time_range=(future_time, future_time + 1000))
    assert len(memory_system.retrieve_memories(query_time_no_match)) == 0

def test_calculate_similarity_edge_cases(memory_system):
    """Test edge cases for similarity calculation."""
    # Test with empty query text
    assert memory_system._calculate_similarity("", {"content": "some data"}) == 0.0

    # Test with empty content
    assert memory_system._calculate_similarity("query", {}) == 0.0

    # Test with no word overlap
    assert memory_system._calculate_similarity("one two", {"content": "three four"}) == 0.0

def test_maybe_trigger_decay(mocker):
    """Test the time-based trigger for decay."""
    ms = MemorySystem()
    mocker.patch.object(ms, 'decay_memories')

    # Simulate time passing
    mocker.patch('time.time', return_value=ms.last_decay + 3601)
    ms._maybe_trigger_decay()
    ms.decay_memories.assert_called_once()

def test_maybe_trigger_consolidation(mocker):
    """Test the time-based trigger for consolidation."""
    ms = MemorySystem()
    mocker.patch.object(ms, 'consolidate_memories')

    # Simulate time passing
    mocker.patch('time.time', return_value=ms.last_consolidation + 86401)
    ms._maybe_trigger_consolidation()
    ms.consolidate_memories.assert_called_once()

def test_persistence_load_error(mocker, tmp_path):
    """Test error handling when loading persisted data fails."""
    db_path = tmp_path / "bad_memory.json"
    with open(db_path, "w") as f:
        f.write("invalid json")

    mocker.patch('builtins.print')
    MemorySystem(persistence_path=str(db_path))
    print.assert_called_with(mocker.ANY)

def test_persistence_save_error(mocker, persistent_memory_system):
    """Test error handling when saving memories fails."""
    mocker.patch('builtins.open', mocker.mock_open())
    open.side_effect = IOError("Failed to write")

    mocker.patch('builtins.print')
    persistent_memory_system._save_memories()
    print.assert_called_with(mocker.ANY)

def test_process_invalid_memory_type(memory_system):
    """Test process() with an invalid memory_type."""
    input_data = {
        "operation": "store",
        "memory_type": "non_existent_type",
        "content": {"q": "test"}
    }
    result = memory_system.process(input_data)
    # The system defaults to EPISODIC, so the operation should still succeed.
    assert "error" not in result["result"]
    assert "memory_id" in result["result"]
    assert len(memory_system.episodic_memory) == 1

def test_process_all_operations(memory_system):
    """Test all process operations to ensure they run without errors."""
    memory_system.store_memory({"q": "test"}, MemoryType.EPISODIC)

    operations = [
        {"operation": "retrieve", "query": {"text": "test"}},
        {"operation": "consolidate"},
        {"operation": "decay"},
        {"operation": "stats"},
    ]

    for op in operations:
        result = memory_system.process(op)
        assert "error" not in result["result"]

def test_clear_all_memory_types(memory_system):
    """Test clearing all memory types."""
    for mem_type in MemoryType:
        # Context buffer is a deque, handle separately
        if mem_type == MemoryType.CONTEXT:
            memory_system.store_memory({"data": "test"}, mem_type)
            assert len(memory_system.context_buffer) > 0
            memory_system.clear_memory_type(mem_type)
            assert len(memory_system.context_buffer) == 0
        else:
            memory_system.store_memory({"data": "test"}, mem_type)
            store = getattr(memory_system, f"{mem_type.value}_memory")
            assert len(store) > 0
            memory_system.clear_memory_type(mem_type)
            assert len(store) == 0
