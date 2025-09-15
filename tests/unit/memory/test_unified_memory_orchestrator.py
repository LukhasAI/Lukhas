# owner: Jules-03
# tier: tier1
# module_uid: candidate.memory.core.unified_memory_orchestrator
# criticality: P0

import pytest
from candidate.memory.core.unified_memory_orchestrator import UnifiedMemoryOrchestrator, MemoryType, SleepStage


@pytest.fixture
def orchestrator():
    """Fixture for a clean UnifiedMemoryOrchestrator instance."""
    # We test with components disabled to focus on the orchestrator's own logic
    with pytest.MonkeyPatch.context() as m:
        m.setattr("candidate.memory.core.unified_memory_orchestrator.LUKHAS_COMPONENTS_AVAILABLE", False)
        m.setattr("candidate.memory.core.unified_memory_orchestrator.MEMORY_COMPONENTS_AVAILABLE", False)
        yield UnifiedMemoryOrchestrator()


@pytest.mark.tier1
@pytest.mark.memory
@pytest.mark.asyncio
class TestUnifiedMemoryOrchestrator:
    """Test suite for the UnifiedMemoryOrchestrator class."""

    async def test_initialization(self, orchestrator):
        """Test that the orchestrator initializes correctly."""
        assert orchestrator is not None
        assert orchestrator.hippocampal_capacity == 10000
        assert len(orchestrator.hippocampal_buffer) == 0
        assert len(orchestrator.neocortical_network) == 0

    async def test_encode_memory(self, orchestrator):
        """Test encoding a memory into the hippocampal buffer."""
        memory_id = await orchestrator.encode_memory(content="test memory", memory_type=MemoryType.EPISODIC)
        assert memory_id is not None
        assert len(orchestrator.hippocampal_buffer) == 1
        assert orchestrator.hippocampal_buffer[0].memory_id == memory_id
        assert orchestrator.hippocampal_buffer[0].content == "test memory"

    async def test_retrieve_from_hippocampus(self, orchestrator):
        """Test retrieving a memory from the hippocampal buffer."""
        await orchestrator.encode_memory(content="hippocampal memory", memory_type=MemoryType.EPISODIC)
        results = await orchestrator.retrieve_memory(query="hippocampal")
        assert len(results) > 0
        assert results[0][0].content == "hippocampal memory"

    async def test_consolidation(self, orchestrator):
        """Test the memory consolidation process."""
        memory_id = await orchestrator.encode_memory(
            content="to be consolidated", memory_type=MemoryType.SEMANTIC, importance=0.8
        )

        trace_to_consolidate = None
        for trace in orchestrator.hippocampal_buffer:
            if trace.memory_id == memory_id:
                trace.replay_count = 10  # Increased replay count
                trace_to_consolidate = trace
                break

        assert trace_to_consolidate is not None

        success = await orchestrator.consolidate_memory(memory_id, force=True)

        assert success
        assert memory_id in orchestrator.neocortical_network
        assert orchestrator.neocortical_network[memory_id].content == "to be consolidated"

    async def test_forget_memory(self, orchestrator):
        """Test forgetting a memory."""
        memory_id = await orchestrator.encode_memory(
            content="to be forgotten", memory_type=MemoryType.EPISODIC, importance=0.9
        )

        for trace in orchestrator.hippocampal_buffer:
            if trace.memory_id == memory_id:
                trace.replay_count = 10  # Increased replay count

        await orchestrator.consolidate_memory(memory_id, force=True)

        assert memory_id in orchestrator.neocortical_network

        forgotten = await orchestrator.forget_memory(memory_id, gradual=False)
        assert forgotten
        assert memory_id not in orchestrator.neocortical_network

    async def test_get_memory_statistics(self, orchestrator):
        """Test that memory statistics are reported correctly."""
        await orchestrator.encode_memory(content="stat test", memory_type=MemoryType.EPISODIC)
        stats = orchestrator.get_memory_statistics()
        assert stats["total_memories"] == 1
        assert stats["hippocampal_memories"] == 1
        assert stats["encoding_count"] == 1

    async def test_consolidation_fails_if_not_in_hippocampus(self, orchestrator):
        """Test that consolidation fails if the memory is not in the hippocampal buffer."""
        success = await orchestrator.consolidate_memory("non_existent_id", force=True)
        assert not success

    async def test_sleep_stage_impacts_consolidation(self, orchestrator):
        """Test that sleep stage impacts consolidation."""
        memory_id = await orchestrator.encode_memory(
            content="sleepy memory", memory_type=MemoryType.SEMANTIC, importance=0.8
        )

        for trace in orchestrator.hippocampal_buffer:
            if trace.memory_id == memory_id:
                trace.replay_count = 10

        await orchestrator.enter_sleep_stage(SleepStage.AWAKE)
        success_awake = await orchestrator.consolidate_memory(memory_id)
        assert not success_awake

        await orchestrator.enter_sleep_stage(SleepStage.NREM3)
        success_nrem3 = await orchestrator.consolidate_memory(memory_id)
        assert success_nrem3

    async def test_encoding_strength(self, orchestrator):
        """Test the encoding strength calculation."""
        strength1 = orchestrator._calculate_encoding_strength(importance=0.5, emotional_valence=0.8)
        strength2 = orchestrator._calculate_encoding_strength(importance=0.8, emotional_valence=0.2)
        assert strength1 > 0.5
        assert strength2 > 0.5

    async def test_pattern_separation(self, orchestrator):
        """Test the pattern separation mechanism."""
        mem1_id = await orchestrator.encode_memory(
            content="similar memory", memory_type=MemoryType.EPISODIC, semantic_links=["a", "b"]
        )
        mem2_id = await orchestrator.encode_memory(
            content="similar memory", memory_type=MemoryType.EPISODIC, semantic_links=["a", "b", "c"]
        )

        trace1 = orchestrator.hippocampal_buffer[0]
        trace2 = orchestrator.hippocampal_buffer[1]

        assert trace1.semantic_links != trace2.semantic_links
