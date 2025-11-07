# owner: Jules-03
# tier: tier1
# module_uid: candidate.memory.systems.memory_manager
# criticality: P1

from unittest.mock import AsyncMock

import pytest
from memory.fakes.agimemory_fake import AGIMemoryFake
from memory.folds.fold_engine import MemoryType
from memory.systems.memory_manager import AdvancedMemoryManager


@pytest.fixture
def mock_base_memory_manager():
    """Fixture for a mocked base MemoryManager."""
    mock = AsyncMock()
    mock.retrieve.return_value = {"access_count": 0}
    return mock


@pytest.fixture
def mock_fold_engine():
    """Fixture for a mocked AGIMemory (fold engine)."""
    return AGIMemoryFake()


@pytest.fixture
def mock_emotional_oscillator():
    """Fixture for a mocked emotional oscillator."""
    mock = AsyncMock()
    mock.process_memory_emotion = AsyncMock()
    return mock


@pytest.fixture
def mock_qi_attention():
    """Fixture for a mocked quantum attention mechanism."""
    mock = AsyncMock()
    mock.score_memory_relevance = AsyncMock(return_value=0.5)
    return mock


@pytest.fixture
def advanced_memory_manager(mock_base_memory_manager, mock_fold_engine, mock_emotional_oscillator, mock_qi_attention):
    """Fixture for an AdvancedMemoryManager with mocked dependencies."""
    manager = AdvancedMemoryManager(
        base_memory_manager=mock_base_memory_manager,
        fold_engine_instance=mock_fold_engine,
        emotional_oscillator=mock_emotional_oscillator,
        qi_attention=mock_qi_attention,
    )
    return manager


@pytest.mark.tier1
@pytest.mark.memory
@pytest.mark.asyncio
class TestAdvancedMemoryManager:
    """Test suite for the AdvancedMemoryManager class."""

    async def test_initialization(self, advanced_memory_manager, mock_base_memory_manager, mock_fold_engine):
        """Test that the manager initializes correctly with mocked dependencies."""
        assert advanced_memory_manager.memory_manager == mock_base_memory_manager
        assert advanced_memory_manager.fold_engine == mock_fold_engine
        assert advanced_memory_manager.metrics["total_memories_managed"] == 0

    async def test_store_memory_with_emotional_context(self, advanced_memory_manager, mock_emotional_oscillator):
        """Test storing a memory with emotional context."""
        await advanced_memory_manager.store_memory(
            content="emotional content", memory_type=MemoryType.EMOTIONAL, emotional_context={"emotion": "joy"}
        )
        mock_emotional_oscillator.process_memory_emotion.assert_called_once()
        assert advanced_memory_manager.metrics["emotional_context_usage"] == 1

    async def test_retrieve_memory_not_found(self, advanced_memory_manager, mock_base_memory_manager):
        """Test retrieving a memory that does not exist."""
        mock_base_memory_manager.retrieve.return_value = None
        memory_data = await advanced_memory_manager.retrieve_memory("non_existent_id")
        assert memory_data is None

    async def test_search_memories_with_qi_attention(
        self, advanced_memory_manager, mock_fold_engine, mock_qi_attention
    ):
        """Test searching memories with the quantum attention mechanism."""
        mem_id = await advanced_memory_manager.store_memory(
            content="attention content", memory_type=MemoryType.SEMANTIC
        )

        mock_fold_engine.search_folds = AsyncMock(return_value=[mem_id])
        advanced_memory_manager.retrieve_memory = AsyncMock(return_value={"content": "attention content"})

        await advanced_memory_manager.search_memories("attention")
        mock_qi_attention.score_memory_relevance.assert_called_once()

    async def test_retrieve_by_unknown_emotion(self, advanced_memory_manager):
        """Test retrieving by an unknown emotion."""
        results = await advanced_memory_manager.retrieve_by_emotion("unknown_emotion")
        assert results == []

    async def test_consolidate_memories(self, advanced_memory_manager, mock_fold_engine):
        """Test the consolidate_memories method."""
        mock_fold_engine.consolidate_memories = AsyncMock(return_value={"status": "consolidated"})
        result = await advanced_memory_manager.consolidate_memories()
        assert result["status"] == "consolidated"

    async def test_optimize_memory_storage(self, advanced_memory_manager, mock_fold_engine):
        """Test the optimize_memory_storage method."""
        mock_fold_engine.consolidate_memories = AsyncMock(return_value={"status": "consolidated"})
        mock_fold_engine.optimize_storage = AsyncMock(return_value={"status": "optimized"})
        result = await advanced_memory_manager.optimize_memory_storage()
        assert result["consolidation_summary"]["status"] == "consolidated"
        assert result["fold_engine_optimization_status"]["status"] == "optimized"

    async def test_get_related_memories(self, advanced_memory_manager):
        """Test retrieving memories related by tags or content."""
        # Store two memories with a shared tag
        id1 = await advanced_memory_manager.store_memory(content="content one", tags=["shared_tag"])
        id2 = await advanced_memory_manager.store_memory(content="content two", tags=["shared_tag"])
        id3 = await advanced_memory_manager.store_memory(content="content three", tags=["other_tag"])

        # Mock the retrieve_memory to return the stored data
        async def mock_retrieve(mem_id):
            if mem_id == id1:
                return {"id": id1, "content": "content one", "tags": ["shared_tag"]}
            if mem_id == id2:
                return {"id": id2, "content": "content two", "tags": ["shared_tag"]}
            if mem_id == id3:
                return {"id": id3, "content": "content three", "tags": ["other_tag"]}
            return None

        advanced_memory_manager.retrieve_memory = AsyncMock(side_effect=mock_retrieve)

        related_memories = await advanced_memory_manager.get_related_memories(id1)

        assert len(related_memories) == 1
        related_ids = {mem["id"] for mem in related_memories}
        assert id2 in related_ids
        assert id3 not in related_ids

    def test_get_memory_statistics(self, advanced_memory_manager):
        """Test that memory statistics are reported correctly."""
        # The fold_engine mock (AGIMemoryFake) does not have get_status,
        # so this also tests the fallback path.
        stats = advanced_memory_manager.get_memory_statistics()

        assert stats["metrics"]["total_memories_managed"] == 0
        assert stats["cluster_count"] == 0
        assert stats["fold_engine_status"] == "N/A"
        assert stats["emotional_oscillator_connected"] is True
        assert stats["qi_attention_connected"] is True
