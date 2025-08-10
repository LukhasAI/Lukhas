"""Basic tests for LUKHAS memory module."""

from datetime import datetime
from time import sleep

from memory.basic import (
    InMemoryStore,
    MemoryEntry,
    MemoryManager,
    recall,
    remember,
    search,
)
from memory.basic import memory_manager as global_memory_manager


class TestMemoryEntry:
    """Test MemoryEntry class."""

    def test_memory_entry_creation(self):
        """Test creating a memory entry."""
        content = "Test memory"
        metadata = {"type": "test", "importance": 5}

        entry = MemoryEntry(content, metadata)

        assert entry.content == content
        assert entry.metadata == metadata
        assert entry.id is not None
        assert isinstance(entry.created_at, datetime)
        assert entry.accessed_at == entry.created_at
        assert entry.access_count == 0

    def test_memory_entry_access(self):
        """Test accessing a memory entry."""
        entry = MemoryEntry("test")
        original_time = entry.accessed_at
        original_count = entry.access_count

        # Small delay to ensure time difference
        sleep(0.01)
        entry.access()

        assert entry.accessed_at > original_time
        assert entry.access_count == original_count + 1

    def test_memory_entry_serialization(self):
        """Test converting memory entry to/from dict."""
        content = {"data": "complex content", "numbers": [1, 2, 3]}
        metadata = {"source": "test"}

        entry = MemoryEntry(content, metadata)
        entry.access()  # Change some values

        # Convert to dict
        data = entry.to_dict()

        assert data["id"] == entry.id
        assert data["content"] == entry.content
        assert data["metadata"] == entry.metadata
        assert data["access_count"] == 1

        # Convert back from dict
        restored_entry = MemoryEntry.from_dict(data)

        assert restored_entry.id == entry.id
        assert restored_entry.content == entry.content
        assert restored_entry.metadata == entry.metadata
        assert restored_entry.access_count == entry.access_count
        assert restored_entry.created_at == entry.created_at
        assert restored_entry.accessed_at == entry.accessed_at


class TestInMemoryStore:
    """Test InMemoryStore implementation."""

    def setup_method(self):
        """Set up test with fresh store."""
        self.store = InMemoryStore()

    def test_store_and_retrieve(self):
        """Test storing and retrieving memory entries."""
        entry = MemoryEntry("test content", {"tag": "test"})

        # Store entry
        memory_id = self.store.store(entry)
        assert memory_id == entry.id

        # Retrieve entry
        retrieved = self.store.retrieve(memory_id)
        assert retrieved is not None
        assert retrieved.id == entry.id
        assert retrieved.content == entry.content
        assert retrieved.access_count == 1  # Should increment on retrieval

    def test_retrieve_nonexistent(self):
        """Test retrieving non-existent memory."""
        result = self.store.retrieve("nonexistent-id")
        assert result is None

    def test_search_functionality(self):
        """Test searching through memories."""
        # Add test memories
        entries = [
            MemoryEntry("The quick brown fox"),
            MemoryEntry("A lazy dog sleeps"),
            MemoryEntry("Brown bear in forest"),
            MemoryEntry("Fox hunting at night"),
        ]

        for entry in entries:
            self.store.store(entry)

        # Search for "fox"
        results = self.store.search("fox", limit=10)
        assert len(results) == 2

        # Should find entries containing "fox"
        contents = [r.content for r in results]
        assert "The quick brown fox" in contents
        assert "Fox hunting at night" in contents

        # Test case insensitive search
        results = self.store.search("BROWN", limit=10)
        assert len(results) == 2

    def test_search_limit(self):
        """Test search result limiting."""
        # Add many test memories
        for i in range(10):
            self.store.store(MemoryEntry(f"test content {i}"))

        results = self.store.search("test", limit=5)
        assert len(results) == 5

    def test_list_all(self):
        """Test listing all memories."""
        # Add test memories
        entries = []
        for i in range(5):
            entry = MemoryEntry(f"content {i}")
            entries.append(entry)
            self.store.store(entry)

        all_memories = self.store.list_all()
        assert len(all_memories) == 5

        # Should be sorted by creation time (newest first)
        for i in range(4):
            assert all_memories[i].created_at >= all_memories[i + 1].created_at

    def test_list_all_limit(self):
        """Test listing memories with limit."""
        # Add more memories than limit
        for i in range(10):
            self.store.store(MemoryEntry(f"content {i}"))

        limited = self.store.list_all(limit=3)
        assert len(limited) == 3

    def test_delete_memory(self):
        """Test deleting a memory."""
        entry = MemoryEntry("to be deleted")
        memory_id = self.store.store(entry)

        # Verify it exists
        assert self.store.retrieve(memory_id) is not None

        # Delete it
        success = self.store.delete(memory_id)
        assert success is True

        # Verify it's gone
        assert self.store.retrieve(memory_id) is None

    def test_delete_nonexistent(self):
        """Test deleting non-existent memory."""
        success = self.store.delete("nonexistent-id")
        assert success is False

    def test_clear_and_size(self):
        """Test clearing store and size tracking."""
        # Add some memories
        for i in range(5):
            self.store.store(MemoryEntry(f"content {i}"))

        assert self.store.size() == 5

        # Clear all
        self.store.clear()
        assert self.store.size() == 0
        assert len(self.store.list_all()) == 0


class TestMemoryManager:
    """Test MemoryManager class."""

    def setup_method(self):
        """Set up test with fresh manager."""
        self.manager = MemoryManager()

    def test_remember_and_recall(self):
        """Test basic remember/recall functionality."""
        content = "Important information"
        metadata = {"importance": 10}

        # Remember something
        memory_id = self.manager.remember(content, metadata)
        assert memory_id is not None

        # Recall it
        recalled = self.manager.recall(memory_id)
        assert recalled == content

        # Recall full entry
        entry = self.manager.recall_entry(memory_id)
        assert entry is not None
        assert entry.content == content
        assert entry.metadata == metadata

    def test_recall_nonexistent(self):
        """Test recalling non-existent memory."""
        result = self.manager.recall("nonexistent")
        assert result is None

    def test_search_memories(self):
        """Test searching through memories."""
        # Add test memories
        self.manager.remember("Python programming")
        self.manager.remember("JavaScript coding")
        self.manager.remember("Python data science")

        # Search for Python
        results = self.manager.search_memories("Python")
        assert len(results) == 2

        contents = [r.content for r in results]
        assert "Python programming" in contents
        assert "Python data science" in contents

    def test_recent_memories(self):
        """Test getting recent memories."""
        # Add memories with small delays
        memories = []
        for i in range(3):
            memory_id = self.manager.remember(f"memory {i}")
            memories.append(memory_id)
            sleep(0.01)  # Small delay

        recent = self.manager.recent_memories(limit=2)
        assert len(recent) == 2

        # Should be in reverse chronological order (newest first)
        assert recent[0].content == "memory 2"
        assert recent[1].content == "memory 1"

    def test_forget_memory(self):
        """Test forgetting (deleting) a memory."""
        memory_id = self.manager.remember("temporary memory")

        # Verify it exists
        assert self.manager.recall(memory_id) is not None

        # Forget it
        success = self.manager.forget(memory_id)
        assert success is True

        # Verify it's gone
        assert self.manager.recall(memory_id) is None

    def test_memory_stats(self):
        """Test getting memory statistics."""
        # Start with empty stats
        stats = self.manager.memory_stats()
        assert stats["total_memories"] == 0

        # Add some memories and access them
        id1 = self.manager.remember("memory 1")
        id2 = self.manager.remember("memory 2")

        # Access memories multiple times
        self.manager.recall(id1)
        self.manager.recall(id1)
        self.manager.recall(id2)

        stats = self.manager.memory_stats()
        assert stats["total_memories"] == 2
        assert stats["total_accesses"] == 3
        assert stats["avg_accesses"] == 1.5
        assert stats["oldest_memory"] is not None
        assert stats["newest_memory"] is not None


class TestGlobalFunctions:
    """Test global memory functions."""

    def setup_method(self):
        """Clear global memory manager."""
        if hasattr(global_memory_manager.store, "clear"):
            global_memory_manager.store.clear()

    def test_global_remember_recall(self):
        """Test global remember/recall functions."""
        content = "Global memory test"

        memory_id = remember(content, {"source": "test"})
        assert memory_id is not None

        recalled = recall(memory_id)
        assert recalled == content

    def test_global_search(self):
        """Test global search function."""
        remember("Test content alpha")
        remember("Test content beta")
        remember("Different content")

        results = search("Test content")
        assert len(results) == 2

        contents = [r.content for r in results]
        assert "Test content alpha" in contents
        assert "Test content beta" in contents


class TestMemoryIntegration:
    """Integration tests for memory system."""

    def test_memory_workflow(self):
        """Test complete memory workflow."""
        manager = MemoryManager()

        # Remember information
        work_id = manager.remember("Work on project X", {"priority": "high"})
        personal_id = manager.remember("Call mom", {"priority": "personal"})
        research_id = manager.remember(
            "Read about AI memory systems", {"priority": "research"}
        )

        # Access some memories
        manager.recall(work_id)
        manager.recall(work_id)  # Access twice
        manager.recall(research_id)

        # Search for priorities
        high_priority = manager.search_memories("project")
        assert len(high_priority) == 1
        assert high_priority[0].metadata["priority"] == "high"

        # Get recent memories
        recent = manager.recent_memories(limit=3)
        assert len(recent) == 3

        # Check stats
        stats = manager.memory_stats()
        assert stats["total_memories"] == 3
        assert (
            stats["total_accesses"] == 4
        )  # work_id accessed twice, research_id once, personal_id once during creation

        # Forget one memory
        success = manager.forget(personal_id)
        assert success

        # Verify it's gone
        assert manager.recall(personal_id) is None

        # Stats should update
        stats = manager.memory_stats()
        assert stats["total_memories"] == 2

    def test_memory_with_complex_data(self):
        """Test memory with complex data structures."""
        manager = MemoryManager()

        complex_data = {
            "user": {"name": "Alice", "age": 30},
            "preferences": ["coffee", "books", "hiking"],
            "history": [
                {"action": "login", "timestamp": "2024-01-01"},
                {"action": "search", "query": "memory systems"},
            ],
        }

        memory_id = manager.remember(complex_data, {"type": "user_profile"})

        recalled = manager.recall(memory_id)
        assert recalled == complex_data
        assert recalled["user"]["name"] == "Alice"
        assert "coffee" in recalled["preferences"]

    def test_memory_persistence_simulation(self):
        """Test memory entry serialization (simulating persistence)."""
        manager = MemoryManager()

        # Create and store a memory
        original_content = {"data": "test", "numbers": [1, 2, 3]}
        memory_id = manager.remember(original_content, {"test": True})

        # Get the entry and serialize it
        entry = manager.recall_entry(memory_id)
        serialized = entry.to_dict()

        # Simulate loading from storage
        restored_entry = MemoryEntry.from_dict(serialized)

        # Verify restoration
        assert restored_entry.content == original_content
        assert restored_entry.metadata == {"test": True}
        assert restored_entry.id == memory_id
