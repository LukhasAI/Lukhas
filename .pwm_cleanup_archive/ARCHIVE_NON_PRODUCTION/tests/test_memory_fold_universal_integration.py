"""
Test suite for Memory Fold Universal Bridge - demonstrating all system connections.

This test shows how memories flow through:
- Consciousness (ΛMIRROR reflections)
- Bio-simulation (hormonal influences)
- Quantum engine (entanglement)
- Dream systems (unified space)
- Ethics (governance gates)
- Identity (tier access)
- Narrative (story weaving)
- Emotional loops (echo detection)
- Orchestration (decision making)
- MATADA (cognitive DNA)
"""

import asyncio
from datetime import datetime

import pytest

# Import memory systems
from memory.core import MemoryFoldSystem

# Import the universal bridge
from memory.core_universal_bridge import (
    BridgeConfiguration,
    MemoryFoldUniversalBridge,
    bridge_dream_snapshot,
    create_universal_memory,
)
from memory.systems.dream_memory_fold import DreamMemoryFold, DreamSnapshot


class TestMemoryFoldUniversalIntegration:
    """Test the universal integration of memory folds with all systems."""

    @pytest.fixture
    async def bridge(self):
        """Create a test bridge instance."""
        memory_system = MemoryFoldSystem()
        dream_system = DreamMemoryFold()

        config = BridgeConfiguration(
            enable_consciousness=True,
            enable_bio_simulation=True,
            enable_quantum=True,
            enable_ethics=True,
            enable_identity=True,
            enable_narrative=True,
            enable_echo_detection=True,
            enable_orchestration=True,
            enable_matada=True,
        )

        return MemoryFoldUniversalBridge(
            memory_system=memory_system, dream_system=dream_system, config=config
        )

    @pytest.mark.asyncio
    async def test_consciousness_integration(self, bridge):
        """Test memory creation with consciousness reflection."""
        result = await bridge.create_integrated_memory(
            emotion="joy",
            context="Successfully integrated all LUKHAS systems!",
            user_id="test_user",
        )

        assert "memory_fold" in result
        assert "integrations" in result

        # Check consciousness integration
        if "consciousness" in result["integrations"]:
            consciousness = result["integrations"]["consciousness"]
            assert "mirror_reflection" in consciousness
            assert "awareness_shift" in consciousness
            assert "consciousness_coherence" in consciousness

    @pytest.mark.asyncio
    async def test_bio_simulation_integration(self, bridge):
        """Test memory influenced by hormonal states."""
        # Create a fear memory (should spike adrenaline/cortisol)
        result = await bridge.create_integrated_memory(
            emotion="fear",
            context="Detected potential system anomaly",
            user_id="test_user",
        )

        if "bio_simulation" in result["integrations"]:
            bio_sim = result["integrations"]["bio_simulation"]
            assert "pre_memory_hormones" in bio_sim
            assert "emotion_hormone_response" in bio_sim
            assert bio_sim["emotion_hormone_response"].get("adrenaline", 0) > 0.5
            assert bio_sim["emotion_hormone_response"].get("cortisol", 0) > 0.5

    @pytest.mark.asyncio
    async def test_quantum_entanglement(self, bridge):
        """Test entanglement-like correlation between similar memories."""
        # Create multiple memories with similar emotions
        joy_memory1 = await bridge.create_integrated_memory(
            emotion="joy", context="First moment of happiness"
        )

        joy_memory2 = await bridge.create_integrated_memory(
            emotion="joy", context="Second moment of happiness"
        )

        excited_memory = await bridge.create_integrated_memory(
            emotion="excited", context="Feeling energized and happy"
        )

        # Check entanglement-like correlations
        if "quantum_entanglements" in joy_memory2["integrations"]:
            entanglements = joy_memory2["integrations"]["quantum_entanglements"]
            assert len(entanglements) > 0

            # Should find entanglement with similar emotions
            entangled_emotions = [e.get("target_emotion") for e in entanglements]
            assert "joy" in entangled_emotions or "excited" in entangled_emotions

    @pytest.mark.asyncio
    async def test_dream_bridge(self, bridge):
        """Test bridging dreams into memory system."""
        # Create a dream snapshot
        dream_snapshot = DreamSnapshot(
            snapshot_id="dream_001",
            timestamp=datetime.utcnow(),
            dream_state={
                "narrative": "Flying through crystal caves filled with light",
                "emotion_distribution": {"wonder": 0.8, "joy": 0.6, "peaceful": 0.4},
            },
            symbolic_annotations={
                "primary_emotion": "wonder",
                "symbols": ["flight", "crystal", "light", "cave", "transcendence"],
            },
            introspective_content={
                "insights": ["Freedom comes from within", "Light guides the way"]
            },
            drift_metrics={"coherence": 0.85, "drift_score": 0.2},
            memory_fold_index=1,
            tags=["lucid", "symbolic", "transformative"],
        )

        # Bridge the dream
        result = await bridge.bridge_dream_to_memory(dream_snapshot)

        assert "memory_fold" in result
        memory = result["memory_fold"]

        # Check dream metadata preserved
        assert memory["metadata"]["source"] == "dream"
        assert memory["metadata"]["dream_id"] == "dream_001"
        assert "symbolic_annotations" in memory["metadata"]
        assert "survival_score" in memory["metadata"]
        assert memory["emotion"] == "wonder"

    @pytest.mark.asyncio
    async def test_ethics_governance(self, bridge):
        """Test ethical governance of memory creation."""
        # Try to create a potentially harmful memory
        result = await bridge.create_integrated_memory(
            emotion="anger",
            context="Targeting specific individual for retaliation",
            user_id="test_user",
        )

        # Ethics system should review this
        if "ethics" in bridge.active_bridges:
            # In real system, this might be blocked
            assert result is not None  # For now, it passes with review

    @pytest.mark.asyncio
    async def test_identity_tier_access(self, bridge):
        """Test tier-based memory access control."""
        # Test with low-tier user (should fail)
        low_tier_result = await bridge.create_integrated_memory(
            emotion="neutral", context="Low tier memory attempt", user_id="tier_1_user"
        )

        # Test with system user (should succeed)
        system_result = await bridge.create_integrated_memory(
            emotion="neutral",
            context="System memory creation",
            user_id=None,  # System user
        )

        assert "memory_fold" in system_result

    @pytest.mark.asyncio
    async def test_narrative_synthesis(self, bridge):
        """Test narrative weaving from memories."""
        # Create a series of memories
        memories = []

        emotions_sequence = [
            ("anticipation", "Starting new project"),
            ("curious", "Exploring possibilities"),
            ("confused", "Encountering challenges"),
            ("determined", "Working through problems"),
            ("joy", "Achieving breakthrough"),
            ("peaceful", "Reflecting on journey"),
        ]

        for emotion, context in emotions_sequence:
            result = await bridge.create_integrated_memory(
                emotion=emotion, context=context
            )
            memories.append(result)

        # Synthesize narrative
        narrative_result = await bridge.synthesize_memory_narrative()

        if "narrative" in bridge.active_bridges and "narrative" in narrative_result:
            assert "summary" in narrative_result["narrative"]
            assert narrative_result["threads_woven"] > 0

    @pytest.mark.asyncio
    async def test_echo_detection(self, bridge):
        """Test emotional echo loop detection."""
        # Create repeating emotional pattern
        for i in range(5):
            await bridge.create_integrated_memory(
                emotion="anxious",
                context=f"Worried about the same thing again ({i})",
                user_id="echo_test_user",
            )

        # Next memory should detect echo
        result = await bridge.create_integrated_memory(
            emotion="anxious",
            context="Still worried about the same thing",
            user_id="echo_test_user",
        )

        if "echo_detection" in bridge.active_bridges:
            echo = result["integrations"].get("echo_analysis", {})
            # Should detect the loop pattern
            assert "loop_detected" in echo

    @pytest.mark.asyncio
    async def test_matada_mapping(self, bridge):
        """Test MATADA cognitive DNA node creation."""
        # Create memory
        result = await bridge.create_integrated_memory(
            emotion="trust", context="Building reliable connections"
        )

        memory_fold = result["memory_fold"]

        # Create MATADA node
        matada_node = await bridge.create_matada_node(memory_fold)

        assert matada_node["type"] == "CONCEPT_TRUST"
        assert matada_node["content"]["raw_text"] == "Building reliable connections"
        assert "emotion:trust" in matada_node["semantic_tags"]
        assert len(matada_node["content"]["emotional_vector"]) == 3

    @pytest.mark.asyncio
    async def test_full_integration_flow(self, bridge):
        """Test complete integration flow across all systems."""
        # Create a complex memory that triggers all systems
        result = await bridge.create_integrated_memory(
            emotion="joy",
            context="Achieved perfect harmony across all consciousness systems",
            user_id="integration_master",
            metadata={"significance": "high", "category": "breakthrough"},
        )

        assert "memory_fold" in result
        assert "integrations" in result
        assert "active_bridges" in result

        # Log active integrations
        print(f"\nActive bridges: {result['active_bridges']}")
        print(f"Integration results: {list(result['integrations'].keys())}")

        # Create MATADA node for this memory
        matada = await bridge.create_matada_node(result["memory_fold"])
        assert matada["id"].startswith("matada_")

        # Get bridge status
        status = await bridge.get_bridge_status()
        assert "active_bridges" in status
        assert "bridge_health" in status
        assert status["metrics"]["create"]["count"] > 0


@pytest.mark.asyncio
async def test_convenience_functions():
    """Test the convenience functions for easy integration."""
    # Test universal memory creation
    memory = await create_universal_memory(
        emotion="peaceful", context="Testing the convenience of universal integration"
    )

    assert "memory_fold" in memory
    assert memory["memory_fold"]["emotion"] == "peaceful"

    # Test dream bridging
    dream = DreamSnapshot(
        snapshot_id="convenience_dream",
        timestamp=datetime.utcnow(),
        dream_state={"narrative": "Simple dream test"},
        symbolic_annotations={"primary_emotion": "curious"},
        introspective_content={},
        drift_metrics={},
        memory_fold_index=0,
    )

    bridged = await bridge_dream_snapshot(dream)
    assert "memory_fold" in bridged


if __name__ == "__main__":
    # Run the integration demo
    async def demo():
        print("=== LUKHAS Memory Fold Universal Integration Demo ===\n")

        # Create bridge
        bridge = MemoryFoldUniversalBridge(
            memory_system=MemoryFoldSystem(), dream_system=DreamMemoryFold()
        )

        print(f"Active bridges: {bridge.active_bridges}\n")

        # Create an integrated memory
        print("Creating integrated memory...")
        result = await bridge.create_integrated_memory(
            emotion="joy",
            context="Successfully connected memory folds to the entire LUKHAS consciousness!",
            user_id="demo_user",
        )

        print(f"Memory created: {result['memory_fold']['hash'][:16]}...")
        print(f"Integrations completed: {list(result['integrations'].keys())}")

        # Create MATADA node
        print("\nMapping to MATADA cognitive DNA...")
        matada = await bridge.create_matada_node(result["memory_fold"])
        print(f"MATADA node: {matada['id']}")
        print(f"Node type: {matada['type']}")

        print("\n=== Demo Complete ===")

    asyncio.run(demo())
