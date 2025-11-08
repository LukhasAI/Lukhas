"""
Unit tests for the MATRIZ Memory System.
"""
import time
from unittest.mock import patch

import pytest
from matriz.core.memory_system import MemoryItem, MemoryQuery, MemorySystem, MemoryType


@pytest.fixture
def memory_system():
    """Provides a fresh MemorySystem instance for each test."""
    with patch("matriz.core.memory_system.MemorySystem._load_memories"), \
         patch("matriz.core.memory_system.MemorySystem._save_memories"):
        yield MemorySystem()


class TestMemorySystem:
    def test_initialization(self, memory_system):
        """Test that the memory system initializes correctly."""
        assert memory_system is not None

    def test_store_and_retrieve_episodic_memory(self, memory_system):
        """Test storing and retrieving an episodic memory."""
        content = {"question": "what is the capital of france", "answer": "paris"}
        memory_id = memory_system.store_memory(content, MemoryType.EPISODIC)
        assert memory_id is not None

        query = MemoryQuery(memory_types=[MemoryType.EPISODIC])
        results = memory_system.retrieve_memories(query)
        assert len(results) == 1
        assert results[0].content == content

    def test_memory_decay(self, memory_system):
        """Test that memories decay over time."""
        memory_id = memory_system.store_memory({"a": 1}, MemoryType.EPISODIC, confidence=0.1)
        memory_item = memory_system.episodic_memory[memory_id]
        memory_item.last_accessed = int(time.time() * 1000) - 3600 * 1000 * 24  # 1 day ago
        memory_item.confidence = 0.05 # Ensure it will be decayed

        decayed_count = memory_system.decay_memories()
        assert decayed_count == 1
        assert memory_id not in memory_system.episodic_memory

    def test_memory_consolidation(self, memory_system):
        """Test that memories are consolidated correctly."""
        memory_id = memory_system.store_memory({"a": 1}, MemoryType.EPISODIC, confidence=0.7)
        memory_item = memory_system.episodic_memory[memory_id]
        memory_item.access_count = 5
        memory_item.created_timestamp = int(time.time() * 1000) - 3600 * 1000 * 48  # 2 days ago

        consolidated_count = memory_system.consolidate_memories()
        assert consolidated_count == 1
        assert memory_id not in memory_system.episodic_memory
        assert memory_id in memory_system.consolidated_memory

    def test_working_memory_eviction(self, memory_system):
        """Test that the least important item is evicted from working memory."""
        memory_system.working_memory_size = 2
        memory_system.store_memory({"a": 1}, MemoryType.WORKING, confidence=0.9)
        memory_system.store_memory({"b": 2}, MemoryType.WORKING, confidence=0.2)
        memory_system.store_memory({"c": 3}, MemoryType.WORKING, confidence=0.5)

        assert len(memory_system.working_memory) == 2
        contents = [m.content for m in memory_system.working_memory.values()]
        assert {"b": 2} not in contents

    def test_retrieve_multiple_memory_types(self, memory_system):
        """Test retrieving from multiple memory types at once."""
        memory_system.store_memory({"a": 1}, MemoryType.EPISODIC)
        memory_system.store_memory({"b": 2}, MemoryType.SEMANTIC)
        memory_system.store_memory({"c": 3}, MemoryType.WORKING)

        query = MemoryQuery(memory_types=[MemoryType.EPISODIC, MemoryType.SEMANTIC])
        results = memory_system.retrieve_memories(query)
        assert len(results) == 2

    def test_filter_by_confidence(self, memory_system):
        """Test filtering memories by confidence."""
        memory_system.store_memory({"a": 1}, MemoryType.EPISODIC, confidence=0.4)
        memory_system.store_memory({"b": 2}, MemoryType.EPISODIC, confidence=0.8)

        query = MemoryQuery(memory_types=[MemoryType.EPISODIC], min_confidence=0.5)
        results = memory_system.retrieve_memories(query)
        assert len(results) == 1
        assert results[0].content == {"b": 2}

    def test_filter_by_salience(self, memory_system):
        """Test filtering memories by salience."""
        memory_system.store_memory({"a": 1}, MemoryType.EPISODIC, salience=0.3)
        memory_system.store_memory({"b": 2}, MemoryType.EPISODIC, salience=0.9)

        query = MemoryQuery(memory_types=[MemoryType.EPISODIC], min_salience=0.5)
        results = memory_system.retrieve_memories(query)
        assert len(results) == 1
        assert results[0].content == {"b": 2}

    def test_filter_by_tags(self, memory_system):
        """Test filtering memories by tags."""
        memory_system.store_memory({"a": 1}, MemoryType.EPISODIC, tags={"urgent", "test"})
        memory_system.store_memory({"b": 2}, MemoryType.EPISODIC, tags={"general"})

        query = MemoryQuery(memory_types=[MemoryType.EPISODIC], tags={"urgent"})
        results = memory_system.retrieve_memories(query)
        assert len(results) == 1
        assert results[0].content == {"a": 1}

    def test_similarity_search(self, memory_system):
        """Test the similarity search functionality."""
        memory_system.store_memory({"text": "the quick brown fox"}, MemoryType.EPISODIC)
        memory_system.store_memory({"text": "a lazy dog"}, MemoryType.EPISODIC)

        query = MemoryQuery(memory_types=[MemoryType.EPISODIC], query_text="brown fox")
        results = memory_system.retrieve_memories(query)
        assert len(results) == 1
        assert results[0].content == {"text": "the quick brown fox"}

    def test_compression(self, memory_system):
        """Test that memory content is compressed and decompressed correctly."""
        content = {"data": "some compressible data " * 100}
        memory_id = memory_system.store_memory(content, MemoryType.EPISODIC, compress=True)

        # Check that the stored content is compressed (bytes)
        raw_memory_item = memory_system.episodic_memory[memory_id]
        assert isinstance(raw_memory_item.content, bytes)
        assert raw_memory_item.compressed is True

        # Check that the retrieved content is decompressed (dict)
        query = MemoryQuery(memory_types=[MemoryType.EPISODIC])
        results = memory_system.retrieve_memories(query)
        assert len(results) == 1
        assert results[0].content == content

    def test_store_and_retrieve_semantic_memory(self, memory_system):
        """Test storing and retrieving a semantic memory."""
        content = {"concept": "python", "definition": "a programming language"}
        memory_id = memory_system.store_memory(content, MemoryType.SEMANTIC)
        assert memory_id is not None

        query = MemoryQuery(memory_types=[MemoryType.SEMANTIC])
        results = memory_system.retrieve_memories(query)
        assert len(results) == 1
        assert results[0].content == content

    def test_store_and_retrieve_working_memory(self, memory_system):
        """Test storing and retrieving a working memory."""
        content = {"task": "testing", "status": "in progress"}
        memory_id = memory_system.store_memory(content, MemoryType.WORKING)
        assert memory_id is not None

        query = MemoryQuery(memory_types=[MemoryType.WORKING])
        results = memory_system.retrieve_memories(query)
        assert len(results) == 1
        assert results[0].content == content
