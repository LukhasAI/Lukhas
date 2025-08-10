#!/usr/bin/env python3
"""
Integration Test Suite for LUKHAS Dream System

Comprehensive integration tests for the complete dream system including
dream-memory integration, replay-reflection coordination, and system interoperability.
"""

from datetime import datetime
from unittest.mock import patch

import pytest

# Import all dream system components
from memory.core_memory.dream_integration import (
    DreamIntegrator,
    DreamType,
)
from memory.core_memory.reflection_engine import (
    MemoryReflector,
    ReflectionDepth,
    ReflectionType,
)
from memory.core_memory.replay_system import (
    MemoryReplayer,
    ReplayMode,
)

# Note: Legacy compatibility modules have been deprecated
# Direct imports from memory.core_memory modules should be used instead


class TestDreamSystemInteroperability:
    """Test interoperability between dream system components."""

    def setup_method(self):
        """Setup test fixtures."""
        self.dream_integrator = DreamIntegrator()
        self.memory_replayer = MemoryReplayer()
        self.memory_reflector = MemoryReflector()

        self.test_memory_ids = ["mem_001", "mem_002", "mem_003", "mem_004"]
        self.emotional_context = {"curiosity": 0.8, "satisfaction": 0.6}

    def test_dream_to_replay_integration(self):
        """Test using dream insights to create memory replay sequences."""
        # 1. Create and integrate a dream
        dream_id = self.dream_integrator.initiate_dream_formation(
            self.test_memory_ids, DreamType.MEMORY_CONSOLIDATION, self.emotional_context
        )

        # Add fragments
        fragments = [
            {"type": "connection", "insight": "Memory A relates to Memory B"},
            {"type": "pattern", "insight": "Learning progression detected"},
            {"type": "emotion", "insight": "Positive feedback loop"},
        ]

        for fragment in fragments:
            self.dream_integrator.add_dream_fragment(dream_id, fragment)

        # Integrate dream
        integration_result = self.dream_integrator.process_dream_integration(dream_id)
        assert integration_result["success"] is True

        # 2. Use dream's memory connections for replay sequence
        dream_session = self.dream_integrator.dream_archive[dream_id]
        connected_memories = list(dream_session.memory_fold_ids)

        # Create replay sequence from dream-connected memories
        sequence_id = self.memory_replayer.create_replay_sequence(
            connected_memories,
            ReplayMode.ASSOCIATIVE,  # Use associative mode for dream connections
        )

        assert sequence_id is not None

        # 3. Start replay session
        session_id = self.memory_replayer.start_replay_session(sequence_id)
        assert session_id is not None

        # 4. Verify replay includes dream-connected memories
        replayed_memories = []
        for _ in range(len(connected_memories)):
            memory = self.memory_replayer.get_next_memory(session_id)
            if memory is None:
                break
            replayed_memories.append(memory["memory_fold_id"])

        # Should replay memories connected by the dream
        assert len(replayed_memories) > 0
        for memory_id in replayed_memories:
            assert memory_id in connected_memories

    def test_reflection_on_dream_insights(self):
        """Test reflecting on dream-generated insights."""
        # 1. Create dream with insights
        dream_id = self.dream_integrator.initiate_dream_formation(
            self.test_memory_ids, DreamType.CREATIVE_SYNTHESIS
        )

        self.dream_integrator.add_dream_fragment(
            dream_id,
            {"type": "meta_insight", "content": "Learning pattern recognition"},
        )

        integration_result = self.dream_integrator.process_dream_integration(dream_id)
        insights = self.dream_integrator.get_dream_insights(dream_id)

        # 2. Use dream insights for reflection analysis
        # Mock memory data that would include dream insights
        dream_memory_data = [
            {
                "memory_id": "dream_memory_001",
                "content": {
                    "dream_insight": insight["insight"] for insight in insights
                },
                "timestamp": datetime.now().isoformat(),
                "emotional_state": self.emotional_context,
            }
        ]

        # 3. Initiate reflection on dream-influenced memories
        session_id = self.memory_reflector.initiate_reflection_session(
            self.test_memory_ids,
            [ReflectionType.META_LEARNING, ReflectionType.PATTERN_ANALYSIS],
        )

        # Process reflection
        reflection_result = self.memory_reflector.process_reflection_analysis(
            session_id
        )
        assert reflection_result["success"] is True

        # 4. Verify reflection insights complement dream insights
        reflection_insights = self.memory_reflector.get_insights_by_type(
            ReflectionType.META_LEARNING
        )
        assert len(reflection_insights) > 0

        # Both dream and reflection should contribute to understanding
        assert len(insights) > 0
        assert len(reflection_insights) > 0

    def test_replay_guided_dream_formation(self):
        """Test using replay patterns to guide dream formation."""
        # 1. Create memory replay to identify patterns
        sequence_id = self.memory_replayer.create_replay_sequence(
            self.test_memory_ids, ReplayMode.CHRONOLOGICAL
        )

        session_id = self.memory_replayer.start_replay_session(sequence_id)

        # Replay memories to identify temporal patterns
        replay_pattern = []
        for _ in range(len(self.test_memory_ids)):
            memory = self.memory_replayer.get_next_memory(session_id)
            if memory is None:
                break
            replay_pattern.append(
                {
                    "memory_id": memory["memory_fold_id"],
                    "emotional_state": memory["emotional_state"],
                    "position": memory["position"],
                }
            )

        # 2. Use replay patterns to inform dream formation
        # Extract emotional progression from replay
        emotional_progression = [mem["emotional_state"] for mem in replay_pattern]

        # Create dream focused on the discovered temporal pattern
        dream_id = self.dream_integrator.initiate_dream_formation(
            [mem["memory_id"] for mem in replay_pattern],
            DreamType.PROBLEM_SOLVING,
            {"pattern_recognition": 0.9},  # High focus on pattern
        )

        # Add fragment based on replay pattern
        self.dream_integrator.add_dream_fragment(
            dream_id,
            {
                "type": "temporal_pattern",
                "pattern": replay_pattern,
                "insight": "Chronological progression reveals learning curve",
            },
        )

        # 3. Verify dream integration
        integration_result = self.dream_integrator.process_dream_integration(dream_id)
        assert integration_result["success"] is True

        # Dream should have high integration score due to temporal coherence
        assert integration_result["integration_score"] > 0.5

    def test_comprehensive_memory_analysis_workflow(self):
        """Test complete workflow: Replay -> Dream -> Reflection -> Assessment."""
        # 1. REPLAY: Analyze memory sequence
        sequence_id = self.memory_replayer.create_replay_sequence(
            self.test_memory_ids, ReplayMode.EMOTIONAL
        )

        session_id = self.memory_replayer.start_replay_session(sequence_id)

        # Extract emotional patterns from replay
        emotional_sequence = []
        for _ in range(len(self.test_memory_ids)):
            memory = self.memory_replayer.get_next_memory(session_id)
            if memory is None:
                break
            emotional_sequence.append(memory["emotional_state"])

        # 2. DREAM: Create dream based on emotional patterns
        avg_valence = sum(
            state.get("valence", 0.5) for state in emotional_sequence
        ) / len(emotional_sequence)

        dream_id = self.dream_integrator.initiate_dream_formation(
            self.test_memory_ids,
            DreamType.EMOTIONAL_PROCESSING,
            {"emotional_intensity": avg_valence},
        )

        self.dream_integrator.add_dream_fragment(
            dream_id,
            {
                "type": "emotional_synthesis",
                "pattern": emotional_sequence,
                "insight": f"Average emotional valence: {avg_valence:.2f}",
            },
        )

        dream_result = self.dream_integrator.process_dream_integration(dream_id)

        # 3. REFLECTION: Reflect on combined replay and dream insights
        reflection_session_id = self.memory_reflector.initiate_reflection_session(
            self.test_memory_ids,
            [ReflectionType.EMOTIONAL_REFLECTION, ReflectionType.PATTERN_ANALYSIS],
            ReflectionDepth.META,
        )

        reflection_result = self.memory_reflector.process_reflection_analysis(
            reflection_session_id
        )

        # 4. ASSESSMENT: Generate comprehensive assessment
        assessment = self.memory_reflector.generate_self_assessment()
        optimization_recommendations = (
            self.memory_reflector.recommend_memory_optimization()
        )

        # 5. Verify integrated workflow results
        assert dream_result["success"] is True
        assert reflection_result["success"] is True
        assert assessment["total_insights"] > 0
        assert len(optimization_recommendations) >= 0

        # Verify cross-system coherence
        dream_insights = self.dream_integrator.get_dream_insights(dream_id)
        reflection_insights = self.memory_reflector.get_insights_by_type(
            ReflectionType.EMOTIONAL_REFLECTION
        )

        # Both systems should contribute complementary insights
        total_insights = len(dream_insights) + len(reflection_insights)
        assert total_insights > 0

        # Assessment should reflect multi-modal analysis
        assert "emotional_tendencies" in assessment
        assert assessment["meta_cognitive_awareness"] >= 0


class TestLegacyCompatibility:
    """Test backward compatibility with legacy import paths."""

    def test_lukhas_dreams_compatibility(self):
        """Test lukhas_dreams compatibility module."""
        # Should be able to import from legacy path
        assert hasattr(lukhas_dreams, "DreamIntegrator")
        assert hasattr(lukhas_dreams, "get_dream_integrator")
        assert hasattr(lukhas_dreams, "initiate_dream")
        assert hasattr(lukhas_dreams, "add_fragment")
        assert hasattr(lukhas_dreams, "integrate_dream")

        # Should work the same as new imports
        integrator = lukhas_dreams.get_dream_integrator()
        assert isinstance(integrator, DreamIntegrator)

        # Test legacy function interface
        dream_id = lukhas_dreams.initiate_dream(["mem_001", "mem_002"])
        assert dream_id is not None

        success = lukhas_dreams.add_fragment(dream_id, {"test": "content"})
        assert success is True

        result = lukhas_dreams.integrate_dream(dream_id)
        assert result["success"] is True

    def test_lukhas_replayer_compatibility(self):
        """Test lukhas_replayer compatibility module."""
        # Should be able to import from legacy path
        assert hasattr(lukhas_replayer, "MemoryReplayer")
        assert hasattr(lukhas_replayer, "get_memory_replayer")
        assert hasattr(lukhas_replayer, "create_sequence")
        assert hasattr(lukhas_replayer, "start_session")
        assert hasattr(lukhas_replayer, "get_next")

        # Should work the same as new imports
        replayer = lukhas_replayer.get_memory_replayer()
        assert isinstance(replayer, MemoryReplayer)

        # Test legacy function interface
        sequence_id = lukhas_replayer.create_sequence(["mem_001", "mem_002"])
        assert sequence_id is not None

        session_id = lukhas_replayer.start_session(sequence_id)
        assert session_id is not None

        memory = lukhas_replayer.get_next(session_id)
        assert memory is not None

    def test_lukhas_reflector_compatibility(self):
        """Test lukhas_reflector compatibility module."""
        # Should be able to import from legacy path
        assert hasattr(lukhas_reflector, "MemoryReflector")
        assert hasattr(lukhas_reflector, "get_memory_reflector")
        assert hasattr(lukhas_reflector, "initiate_reflection")
        assert hasattr(lukhas_reflector, "process_reflection")
        assert hasattr(lukhas_reflector, "get_self_assessment")

        # Should work the same as new imports
        reflector = lukhas_reflector.get_memory_reflector()
        assert isinstance(reflector, MemoryReflector)

        # Test legacy function interface
        session_id = lukhas_reflector.initiate_reflection(["mem_001", "mem_002"])
        assert session_id is not None

        result = lukhas_reflector.process_reflection(session_id)
        assert result["success"] is True

        assessment = lukhas_reflector.get_self_assessment()
        assert isinstance(assessment, dict)

    def test_cross_compatibility_integration(self):
        """Test integration using legacy compatibility modules."""
        # Use legacy modules for complete workflow

        # 1. Create dream using legacy interface
        dream_id = lukhas_dreams.initiate_dream(
            ["mem_001", "mem_002"], "creative_synthesis"
        )
        lukhas_dreams.add_fragment(dream_id, {"legacy": "test"})
        dream_result = lukhas_dreams.integrate_dream(dream_id)

        # 2. Create replay using legacy interface
        sequence_id = lukhas_replayer.create_sequence(
            ["mem_001", "mem_002"], "chronological"
        )
        session_id = lukhas_replayer.start_session(sequence_id)
        memory = lukhas_replayer.get_next(session_id)

        # 3. Create reflection using legacy interface
        reflection_session_id = lukhas_reflector.initiate_reflection(
            ["mem_001", "mem_002"]
        )
        reflection_result = lukhas_reflector.process_reflection(reflection_session_id)

        # All should work together seamlessly
        assert dream_result["success"] is True
        assert memory is not None
        assert reflection_result["success"] is True


class TestSystemPerformanceIntegration:
    """Test performance characteristics of integrated dream system."""

    def setup_method(self):
        """Setup performance test fixtures."""
        self.dream_integrator = DreamIntegrator({"max_active_dreams": 10})
        self.memory_replayer = MemoryReplayer({"max_active_sessions": 10})
        self.memory_reflector = MemoryReflector({"max_active_sessions": 5})

    def test_concurrent_operations(self):
        """Test concurrent operations across all dream system components."""
        # Create multiple dreams, replays, and reflections concurrently
        memory_sets = [
            [f"set1_mem_{i}" for i in range(5)],
            [f"set2_mem_{i}" for i in range(5)],
            [f"set3_mem_{i}" for i in range(5)],
        ]

        # Start concurrent operations
        dream_ids = []
        sequence_ids = []
        reflection_session_ids = []

        for memory_set in memory_sets:
            # Start dream
            dream_id = self.dream_integrator.initiate_dream_formation(memory_set)
            dream_ids.append(dream_id)

            # Start replay
            sequence_id = self.memory_replayer.create_replay_sequence(memory_set)
            if sequence_id:
                session_id = self.memory_replayer.start_replay_session(sequence_id)
                sequence_ids.append(session_id)

            # Start reflection
            reflection_id = self.memory_reflector.initiate_reflection_session(
                memory_set
            )
            reflection_session_ids.append(reflection_id)

        # Process all operations
        for dream_id in dream_ids:
            self.dream_integrator.add_dream_fragment(dream_id, {"concurrent": "test"})
            result = self.dream_integrator.process_dream_integration(dream_id)
            assert result["success"] is True

        for session_id in sequence_ids:
            memory = self.memory_replayer.get_next_memory(session_id)
            assert memory is not None

        for reflection_id in reflection_session_ids:
            result = self.memory_reflector.process_reflection_analysis(reflection_id)
            assert result["success"] is True

        # Verify system status remains healthy
        dream_status = self.dream_integrator.get_system_status()
        replay_status = self.memory_replayer.get_system_status()
        reflection_status = self.memory_reflector.get_system_status()

        assert dream_status["system_status"] == "operational"
        assert replay_status["system_status"] == "operational"
        assert reflection_status["system_status"] == "operational"

    def test_large_scale_memory_processing(self):
        """Test processing large memory sets across all components."""
        # Create large memory set
        large_memory_set = [f"large_mem_{i:04d}" for i in range(100)]

        # Test dream integration with large set
        dream_id = self.dream_integrator.initiate_dream_formation(
            large_memory_set[:50],  # Use subset for dream
            DreamType.MEMORY_CONSOLIDATION,
        )

        # Add multiple fragments
        for i in range(10):
            self.dream_integrator.add_dream_fragment(
                dream_id, {"fragment": i, "content": f"Large scale fragment {i}"}
            )

        dream_result = self.dream_integrator.process_dream_integration(dream_id)
        assert dream_result["success"] is True

        # Test replay with large set
        sequence_id = self.memory_replayer.create_replay_sequence(large_memory_set)
        assert sequence_id is not None

        session_id = self.memory_replayer.start_replay_session(sequence_id)
        assert session_id is not None

        # Replay first 20 memories
        replayed_count = 0
        for _ in range(20):
            memory = self.memory_replayer.get_next_memory(session_id)
            if memory is None:
                break
            replayed_count += 1

        assert replayed_count > 0

        # Test reflection with large set
        reflection_session_id = self.memory_reflector.initiate_reflection_session(
            large_memory_set[:30]  # Use subset for reflection
        )

        reflection_result = self.memory_reflector.process_reflection_analysis(
            reflection_session_id
        )
        assert reflection_result["success"] is True

        # All systems should handle large scale data
        assert dream_result["memory_connections"] == 50
        assert reflection_result["insights_generated"] > 0

    def test_memory_efficiency(self):
        """Test memory efficiency of integrated operations."""
        # Create operations that share memory references
        shared_memory_ids = ["shared_001", "shared_002", "shared_003"]

        # Multiple dreams referencing same memories
        dream_ids = []
        for i in range(3):
            dream_id = self.dream_integrator.initiate_dream_formation(
                shared_memory_ids, DreamType.MEMORY_CONSOLIDATION
            )
            dream_ids.append(dream_id)

        # Multiple replay sessions on same memories
        sequence_id = self.memory_replayer.create_replay_sequence(shared_memory_ids)
        replay_session_ids = []
        for i in range(3):
            session_id = self.memory_replayer.start_replay_session(sequence_id)
            if session_id:
                replay_session_ids.append(session_id)

        # Multiple reflections on same memories
        reflection_session_ids = []
        for i in range(2):  # Limited by reflector capacity
            session_id = self.memory_reflector.initiate_reflection_session(
                shared_memory_ids
            )
            reflection_session_ids.append(session_id)

        # Process all operations
        for dream_id in dream_ids:
            self.dream_integrator.add_dream_fragment(dream_id, {"shared": "memory"})
            result = self.dream_integrator.process_dream_integration(dream_id)
            assert result["success"] is True

        for session_id in replay_session_ids:
            memory = self.memory_replayer.get_next_memory(session_id)
            assert memory is not None

        for session_id in reflection_session_ids:
            result = self.memory_reflector.process_reflection_analysis(session_id)
            assert result["success"] is True

        # Systems should efficiently handle shared memory references
        # Memory linking should be optimized
        dream_links = self.dream_integrator.memory_linker.active_links
        assert len(dream_links) > 0


class TestSystemErrorRecovery:
    """Test error recovery and resilience in integrated operations."""

    def setup_method(self):
        """Setup error recovery test fixtures."""
        self.dream_integrator = DreamIntegrator()
        self.memory_replayer = MemoryReplayer()
        self.memory_reflector = MemoryReflector()

    def test_cascading_error_isolation(self):
        """Test that errors in one component don't cascade to others."""
        memory_ids = ["error_test_001", "error_test_002"]

        # Start normal operations in all components
        dream_id = self.dream_integrator.initiate_dream_formation(memory_ids)
        sequence_id = self.memory_replayer.create_replay_sequence(memory_ids)
        session_id = self.memory_replayer.start_replay_session(sequence_id)
        reflection_id = self.memory_reflector.initiate_reflection_session(memory_ids)

        # Simulate error in dream system
        with patch.object(
            self.dream_integrator,
            "process_dream_integration",
            return_value={"success": False, "error": "Simulated error"},
        ):
            dream_result = self.dream_integrator.process_dream_integration(dream_id)
            assert dream_result["success"] is False

        # Other systems should continue working normally
        memory = self.memory_replayer.get_next_memory(session_id)
        assert memory is not None

        reflection_result = self.memory_reflector.process_reflection_analysis(
            reflection_id
        )
        assert reflection_result["success"] is True

        # Systems should remain operational
        replay_status = self.memory_replayer.get_system_status()
        reflection_status = self.memory_reflector.get_system_status()
        assert replay_status["system_status"] == "operational"
        assert reflection_status["system_status"] == "operational"

    def test_graceful_degradation(self):
        """Test graceful degradation under resource constraints."""
        # Fill systems to capacity
        memory_ids = ["degradation_test"]

        # Fill dream integrator to capacity
        dream_ids = []
        for i in range(10):  # Exceed normal capacity
            dream_id = self.dream_integrator.initiate_dream_formation(
                [f"dream_mem_{i}"]
            )
            if dream_id:
                dream_ids.append(dream_id)

        # Fill memory replayer to capacity
        sequence_id = self.memory_replayer.create_replay_sequence(memory_ids)
        session_ids = []
        for i in range(15):  # Exceed normal capacity
            session_id = self.memory_replayer.start_replay_session(sequence_id)
            if session_id:
                session_ids.append(session_id)

        # Systems should gracefully handle capacity limits
        # Additional requests should fail gracefully, not crash
        overflow_dream_id = self.dream_integrator.initiate_dream_formation(["overflow"])
        overflow_session_id = self.memory_replayer.start_replay_session(sequence_id)

        # Should return None for capacity exceeded, not crash
        if self.dream_integrator.max_active_dreams <= len(dream_ids):
            assert overflow_dream_id is None

        # Systems should remain operational despite capacity limits
        dream_status = self.dream_integrator.get_system_status()
        replay_status = self.memory_replayer.get_system_status()

        assert dream_status["system_status"] == "operational"
        assert replay_status["system_status"] == "operational"


class TestDataConsistency:
    """Test data consistency across dream system components."""

    def setup_method(self):
        """Setup data consistency test fixtures."""
        self.dream_integrator = DreamIntegrator()
        self.memory_replayer = MemoryReplayer()
        self.memory_reflector = MemoryReflector()

    def test_memory_reference_consistency(self):
        """Test consistency of memory references across components."""
        memory_ids = ["consistency_001", "consistency_002", "consistency_003"]

        # Create operations referencing same memories
        dream_id = self.dream_integrator.initiate_dream_formation(memory_ids)
        sequence_id = self.memory_replayer.create_replay_sequence(memory_ids)
        reflection_id = self.memory_reflector.initiate_reflection_session(memory_ids)

        # Process operations
        self.dream_integrator.add_dream_fragment(dream_id, {"consistency": "test"})
        dream_result = self.dream_integrator.process_dream_integration(dream_id)

        session_id = self.memory_replayer.start_replay_session(sequence_id)
        replayed_memories = []
        for _ in range(len(memory_ids)):
            memory = self.memory_replayer.get_next_memory(session_id)
            if memory:
                replayed_memories.append(memory["memory_fold_id"])

        reflection_result = self.memory_reflector.process_reflection_analysis(
            reflection_id
        )

        # Verify memory references are consistent
        dream_session = self.dream_integrator.dream_archive[dream_id]
        dream_memory_refs = dream_session.memory_fold_ids

        reflection_session = self.memory_reflector.completed_sessions[reflection_id]
        reflection_memory_refs = reflection_session.target_memories

        # All should reference the same memory set
        assert dream_memory_refs == set(memory_ids)
        assert reflection_memory_refs == set(memory_ids)
        assert set(replayed_memories) == set(memory_ids) or len(
            replayed_memories
        ) == len(memory_ids)

    def test_temporal_consistency(self):
        """Test temporal consistency across operations."""
        memory_ids = ["temporal_001", "temporal_002"]

        # Record start time
        start_time = datetime.now()

        # Create operations
        dream_id = self.dream_integrator.initiate_dream_formation(memory_ids)
        sequence_id = self.memory_replayer.create_replay_sequence(memory_ids)
        reflection_id = self.memory_reflector.initiate_reflection_session(memory_ids)

        # Process with delays to ensure temporal ordering
        import time

        time.sleep(0.01)  # Small delay

        self.dream_integrator.add_dream_fragment(dream_id, {"temporal": "test"})
        dream_result = self.dream_integrator.process_dream_integration(dream_id)

        session_id = self.memory_replayer.start_replay_session(sequence_id)
        reflection_result = self.memory_reflector.process_reflection_analysis(
            reflection_id
        )

        # Record end time
        end_time = datetime.now()

        # Verify temporal consistency
        dream_session = self.dream_integrator.dream_archive[dream_id]
        reflection_session = self.memory_reflector.completed_sessions[reflection_id]

        dream_start = datetime.fromisoformat(dream_session.started_at)
        dream_end = datetime.fromisoformat(dream_session.completed_at)
        reflection_start = datetime.fromisoformat(reflection_session.started_at)
        reflection_end = datetime.fromisoformat(reflection_session.completed_at)

        # All timestamps should be within test execution window
        assert start_time <= dream_start <= end_time
        assert start_time <= dream_end <= end_time
        assert start_time <= reflection_start <= end_time
        assert start_time <= reflection_end <= end_time

        # Completion should be after start
        assert dream_end >= dream_start
        assert reflection_end >= reflection_start


# Test fixtures and utilities
@pytest.fixture
def integrated_dream_system():
    """Fixture providing integrated dream system components."""
    return {
        "dream_integrator": DreamIntegrator(),
        "memory_replayer": MemoryReplayer(),
        "memory_reflector": MemoryReflector(),
    }


@pytest.fixture
def sample_memory_dataset():
    """Fixture providing comprehensive memory dataset."""
    return {
        "learning_memories": [f"learn_mem_{i:03d}" for i in range(20)],
        "emotional_memories": [f"emotion_mem_{i:03d}" for i in range(15)],
        "pattern_memories": [f"pattern_mem_{i:03d}" for i in range(10)],
        "creative_memories": [f"creative_mem_{i:03d}" for i in range(12)],
    }


# End-to-End Integration Tests
class TestEndToEndIntegration:
    """Comprehensive end-to-end integration tests."""

    def test_complete_cognitive_cycle(
        self, integrated_dream_system, sample_memory_dataset
    ):
        """Test complete cognitive processing cycle using all dream system components."""
        dream_integrator = integrated_dream_system["dream_integrator"]
        memory_replayer = integrated_dream_system["memory_replayer"]
        memory_reflector = integrated_dream_system["memory_reflector"]

        learning_memories = sample_memory_dataset["learning_memories"][:5]

        # Phase 1: Memory Replay Analysis
        sequence_id = memory_replayer.create_replay_sequence(
            learning_memories, ReplayMode.CHRONOLOGICAL
        )
        session_id = memory_replayer.start_replay_session(sequence_id)

        # Extract temporal patterns
        temporal_patterns = []
        for _ in range(len(learning_memories)):
            memory = memory_replayer.get_next_memory(session_id)
            if memory:
                temporal_patterns.append(
                    {
                        "id": memory["memory_fold_id"],
                        "position": memory["position"],
                        "emotional_state": memory["emotional_state"],
                    }
                )

        # Phase 2: Dream Formation Based on Patterns
        avg_emotional_state = {}
        if temporal_patterns:
            # Calculate average emotional state
            for key in temporal_patterns[0]["emotional_state"]:
                avg_emotional_state[key] = sum(
                    pattern["emotional_state"][key] for pattern in temporal_patterns
                ) / len(temporal_patterns)

        dream_id = dream_integrator.initiate_dream_formation(
            learning_memories, DreamType.MEMORY_CONSOLIDATION, avg_emotional_state
        )

        # Add insights from temporal analysis
        dream_integrator.add_dream_fragment(
            dream_id,
            {
                "type": "temporal_analysis",
                "patterns": temporal_patterns,
                "insight": "Learning progression shows consistent improvement",
            },
        )

        dream_result = dream_integrator.process_dream_integration(dream_id)

        # Phase 3: Reflection on Integrated Knowledge
        reflection_session_id = memory_reflector.initiate_reflection_session(
            learning_memories,
            [ReflectionType.PATTERN_ANALYSIS, ReflectionType.META_LEARNING],
            ReflectionDepth.META,
        )

        reflection_result = memory_reflector.process_reflection_analysis(
            reflection_session_id
        )

        # Phase 4: Comprehensive Assessment
        dream_insights = dream_integrator.get_dream_insights(dream_id)
        reflection_insights = memory_reflector.get_insights_by_type(
            ReflectionType.PATTERN_ANALYSIS
        )
        self_assessment = memory_reflector.generate_self_assessment()
        optimization_recommendations = memory_reflector.recommend_memory_optimization()

        # Verification: All phases should complete successfully
        assert len(temporal_patterns) > 0
        assert dream_result["success"] is True
        assert reflection_result["success"] is True
        assert len(dream_insights) > 0
        assert len(reflection_insights) > 0
        assert self_assessment["total_insights"] > 0

        # Verification: Cross-system coherence
        total_system_insights = len(dream_insights) + len(reflection_insights)
        assert total_system_insights >= 2  # At least one from each system

        # Verification: System health after complete cycle
        dream_status = dream_integrator.get_system_status()
        replay_status = memory_replayer.get_system_status()
        reflection_status = memory_reflector.get_system_status()

        assert dream_status["system_status"] == "operational"
        assert replay_status["system_status"] == "operational"
        assert reflection_status["system_status"] == "operational"

        # Return comprehensive results for further analysis
        return {
            "temporal_patterns": temporal_patterns,
            "dream_insights": dream_insights,
            "reflection_insights": reflection_insights,
            "self_assessment": self_assessment,
            "optimization_recommendations": optimization_recommendations,
            "system_status": {
                "dream": dream_status,
                "replay": replay_status,
                "reflection": reflection_status,
            },
        }


if __name__ == "__main__":
    # Run the integration tests
    pytest.main([__file__, "-v", "--tb=short", "--durations=10"])
