"""
Tests for DNA Helix Memory Architecture
========================================
Verify immutability, temporal evolution, and causal chains.
"""

import numpy as np
import pytest

from candidate.memory.dna_helix import (
    CognitiveState,
    DNAHelixMemory,
    LinkType,
    MemoryLink,
    MemoryNode,
    NodeType,
    get_dna_memory,
)


class TestCognitiveState:
    """Test cognitive state operations"""

    def test_state_initialization(self):
        """Test default cognitive state values"""
        state = CognitiveState()
        assert state.confidence == 0.5
        assert state.valence == 0.0
        assert state.arousal == 0.5
        assert state.salience == 0.5
        assert state.novelty == 0.5
        assert state.urgency == 0.0
        assert state.shock_factor == 0.0

    def test_state_to_vector(self):
        """Test conversion to numpy vector"""
        state = CognitiveState(confidence=0.8, valence=0.5, arousal=0.7)
        vec = state.to_vector()
        assert isinstance(vec, np.ndarray)
        assert len(vec) == 7
        assert vec[0] == 0.8  # confidence
        assert vec[1] == 0.5  # valence
        assert vec[2] == 0.7  # arousal

    def test_state_entropy(self):
        """Test entropy calculation"""
        # Uniform state should have higher entropy
        uniform_state = CognitiveState(
            confidence=0.5,
            valence=0.5,
            arousal=0.5,
            salience=0.5,
            novelty=0.5,
            urgency=0.5,
            shock_factor=0.5,
        )

        # Extreme state should have lower entropy
        extreme_state = CognitiveState(
            confidence=1.0,
            valence=0.0,
            arousal=0.0,
            salience=0.0,
            novelty=0.0,
            urgency=0.0,
            shock_factor=0.0,
        )

        assert uniform_state.entropy() > extreme_state.entropy()


class TestMemoryNode:
    """Test memory node operations"""

    def test_node_creation(self):
        """Test creating a memory node"""
        node = MemoryNode(
            type=NodeType.MEMORY,
            content={"text": "Test memory"},
            state=CognitiveState(confidence=0.9),
        )

        assert node.type == NodeType.MEMORY
        assert node.content["text"] == "Test memory"
        assert node.state.confidence == 0.9
        assert node.id.startswith("node_")
        assert node.content_hash != ""

    def test_node_integrity(self):
        """Test node integrity verification"""
        node = MemoryNode(content={"data": "original"})

        # Should verify correctly
        assert node.verify_integrity() is True

        # Tampering with content should fail verification
        node.content_hash
        node.content["data"] = "tampered"
        assert node.verify_integrity() is False

        # Restore original content
        node.content["data"] = "original"
        assert node.verify_integrity() is True

    def test_node_evolution(self):
        """Test node evolution (immutable)"""
        original = MemoryNode(
            type=NodeType.DECISION,
            content={"decision": "original"},
            state=CognitiveState(confidence=0.5),
        )

        # Evolve to new node
        evolved = original.evolve(
            new_content={"decision": "evolved"},
            new_state=CognitiveState(confidence=0.9),
        )

        # Original should be unchanged
        assert original.content["decision"] == "original"
        assert original.state.confidence == 0.5

        # Evolved should have new values
        assert evolved.content["decision"] == "evolved"
        assert evolved.state.confidence == 0.9
        assert evolved.evolved_from == original.id

        # Original should record evolution
        assert evolved.id in original.evolves_to

    def test_node_importance(self):
        """Test importance calculation"""
        # Low importance node
        low_node = MemoryNode(state=CognitiveState(salience=0.1, confidence=0.1))

        # High importance node with connections
        high_node = MemoryNode(state=CognitiveState(salience=0.9, confidence=0.9))
        high_node.links = [
            MemoryLink("target1", LinkType.CAUSAL),
            MemoryLink("target2", LinkType.SEMANTIC),
        ]
        high_node.reflections = [{"type": "test"}]

        assert high_node.calculate_importance() > low_node.calculate_importance()


class TestMemoryLink:
    """Test memory link operations"""

    def test_link_creation(self):
        """Test creating memory links"""
        link = MemoryLink(
            target_node_id="node_123",
            link_type=LinkType.CAUSAL,
            weight=2.0,
            bidirectional=True,
        )

        assert link.target_node_id == "node_123"
        assert link.link_type == LinkType.CAUSAL
        assert link.weight == 2.0
        assert link.bidirectional is True

    def test_link_strengthen_weaken(self):
        """Test link strength changes"""
        link = MemoryLink("target", LinkType.TEMPORAL)
        original_weight = link.weight

        # Strengthen
        link.strengthen(1.5)
        assert link.weight > original_weight

        # Weaken
        link.weaken(0.5)
        assert link.weight < original_weight

        # Should have bounds
        for _ in range(100):
            link.strengthen(2.0)
        assert link.weight <= 10.0

        for _ in range(100):
            link.weaken(0.1)
        assert link.weight >= 0.01


class TestDNAHelixMemory:
    """Test DNA helix memory system"""

    def test_memory_initialization(self):
        """Test memory system initialization"""
        memory = DNAHelixMemory(max_nodes=100, decay_rate=0.05)

        assert memory.max_nodes == 100
        assert memory.decay_rate == 0.05
        assert len(memory.nodes) == 0
        assert len(memory.spatial_strand) == 0
        assert len(memory.temporal_strand) == 0

    def test_add_node(self):
        """Test adding nodes to memory"""
        memory = DNAHelixMemory()

        node = MemoryNode(
            type=NodeType.EMOTION,
            content={"emotion": "happy"},
            tags={"positive", "social"},
        )

        node_id = memory.add_node(node)

        assert node_id in memory.nodes
        assert NodeType.EMOTION in memory.type_index
        assert node_id in memory.type_index[NodeType.EMOTION]
        assert "positive" in memory.tag_index
        assert node_id in memory.tag_index["positive"]

    def test_create_link(self):
        """Test creating links between nodes"""
        memory = DNAHelixMemory()

        node1 = MemoryNode(content={"id": 1})
        node2 = MemoryNode(content={"id": 2})

        id1 = memory.add_node(node1)
        id2 = memory.add_node(node2)

        # Create unidirectional link
        success = memory.create_link(id1, id2, LinkType.CAUSAL, weight=2.0)
        assert success is True
        assert len(memory.nodes[id1].links) == 1
        assert memory.nodes[id1].links[0].target_node_id == id2

        # Create bidirectional link
        node3 = MemoryNode(content={"id": 3})
        id3 = memory.add_node(node3)

        memory.create_link(id1, id3, LinkType.SEMANTIC, bidirectional=True)
        assert len(memory.nodes[id1].links) == 2
        assert len(memory.nodes[id3].links) == 1

    def test_retrieve_by_similarity(self):
        """Test similarity-based retrieval"""
        memory = DNAHelixMemory()

        # Add nodes with different states
        happy_node = MemoryNode(
            content={"mood": "happy"},
            state=CognitiveState(valence=0.9, arousal=0.7),
        )
        sad_node = MemoryNode(
            content={"mood": "sad"},
            state=CognitiveState(valence=-0.9, arousal=0.3),
        )
        neutral_node = MemoryNode(
            content={"mood": "neutral"},
            state=CognitiveState(valence=0.0, arousal=0.5),
        )

        memory.add_node(happy_node)
        memory.add_node(sad_node)
        memory.add_node(neutral_node)

        # Query for happy state
        query = CognitiveState(valence=0.8, arousal=0.8)
        results = memory.retrieve_by_similarity(query, top_k=2)

        assert len(results) == 2
        assert results[0].content["mood"] == "happy"  # Most similar

    def test_trace_causal_chain(self):
        """Test tracing causal chains"""
        memory = DNAHelixMemory()

        # Create evolution chain
        node1 = MemoryNode(content={"version": 1})
        id1 = memory.add_node(node1)

        node2 = node1.evolve({"version": 2}, CognitiveState(confidence=0.6))
        id2 = memory.add_node(node2)

        node3 = node2.evolve({"version": 3}, CognitiveState(confidence=0.8))
        id3 = memory.add_node(node3)

        # Trace chain backwards
        chain = memory.trace_causal_chain(id3, max_depth=10)

        assert len(chain) == 3
        assert chain[0] == id3
        assert chain[1] == id2
        assert chain[2] == id1

    def test_decay_application(self):
        """Test temporal decay on links"""
        memory = DNAHelixMemory(decay_rate=0.1)

        node1 = MemoryNode()
        node2 = MemoryNode()

        id1 = memory.add_node(node1)
        id2 = memory.add_node(node2)

        memory.create_link(id1, id2, LinkType.TEMPORAL, weight=1.0)
        original_weight = memory.nodes[id1].links[0].weight

        # Apply decay
        memory.apply_decay()

        new_weight = memory.nodes[id1].links[0].weight
        assert new_weight < original_weight
        assert new_weight == original_weight * 0.9  # 1 - decay_rate

    def test_memory_statistics(self):
        """Test memory statistics"""
        memory = DNAHelixMemory()

        # Add diverse nodes
        for i in range(5):
            node = MemoryNode(
                type=NodeType.MEMORY if i % 2 == 0 else NodeType.DECISION,
                content={"index": i},
                state=CognitiveState(confidence=0.5 + i * 0.1),
            )
            memory.add_node(node)

        stats = memory.get_statistics()

        assert stats["total_nodes"] == 5
        assert NodeType.MEMORY in stats["node_types"]
        assert NodeType.DECISION in stats["node_types"]
        assert "avg_importance" in stats
        assert "memory_entropy" in stats

    def test_singleton_instance(self):
        """Test singleton memory instance"""
        memory1 = get_dna_memory()
        memory2 = get_dna_memory()

        assert memory1 is memory2  # Same instance

        # Add node through one instance
        node = MemoryNode(content={"test": "singleton"})
        memory1.add_node(node)

        # Should be visible in other reference
        assert len(memory2.nodes) > 0


@pytest.mark.integration
class TestDNAMemoryIntegration:
    """Integration tests for DNA memory with other systems"""

    def test_memory_with_evolution_chain(self):
        """Test complex evolution chain with reflections"""
        memory = DNAHelixMemory()

        # Initial decision
        decision = MemoryNode(
            type=NodeType.DECISION,
            content={"action": "explore", "confidence": 0.5},
            state=CognitiveState(confidence=0.5, urgency=0.3),
        )
        decision_id = memory.add_node(decision)

        # Reflect on decision
        decision.add_reflection(
            "regret",
            "low confidence",
            {"confidence": 0.5},
            {"confidence": 0.3},
        )

        # Evolve based on outcome
        outcome = decision.evolve(
            {"action": "explore", "result": "success", "confidence": 0.8},
            CognitiveState(confidence=0.8, valence=0.7),
        )
        outcome_id = memory.add_node(outcome)

        # Create causal link
        memory.create_link(decision_id, outcome_id, LinkType.CAUSAL, weight=3.0)

        # Verify chain
        chain = memory.trace_causal_chain(outcome_id)
        assert len(chain) == 2
        assert memory.nodes[decision_id].reflections[0]["type"] == "regret"

    def test_memory_capacity_management(self):
        """Test memory cleanup when at capacity"""
        memory = DNAHelixMemory(max_nodes=10)

        # Add nodes beyond capacity
        for i in range(15):
            node = MemoryNode(
                content={"index": i},
                state=CognitiveState(
                    salience=(0.1 if i < 5 else 0.9),  # First 5 have low importance
                    confidence=0.1 if i < 5 else 0.9,
                ),
            )
            memory.add_node(node)

        # Should maintain max capacity
        assert len(memory.nodes) <= memory.max_nodes

        # Low importance nodes should be removed
        remaining_indices = [node.content["index"] for node in memory.nodes.values()]

        # Higher index (more important) nodes should remain
        assert all(idx >= 5 for idx in remaining_indices)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
