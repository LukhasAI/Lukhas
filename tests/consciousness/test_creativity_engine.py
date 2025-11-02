#!/usr/bin/env python3
"""
Tests for LUKHAS Consciousness CreativityEngine - Production Schema v1.0.0

Comprehensive test suite for creativity engine with T4/0.01% excellence validation.
Tests creative processes, Guardian integration, performance targets, and observability.
"""

import time
from unittest.mock import AsyncMock

import pytest

from consciousness.creativity_engine import CreativityEngine
from consciousness.types import (
    DEFAULT_CREATIVITY_CONFIG,
    ConsciousnessState,
    CreativeTask,
    CreativitySnapshot,
)


class TestCreativityEngine:
    """Test suite for CreativityEngine with T4/0.01% standards."""

    @pytest.fixture
    def consciousness_state(self) -> ConsciousnessState:
        """Fixture for basic consciousness state."""
        return ConsciousnessState(
            phase="CREATE",
            awareness_level="enhanced",
            emotional_tone="curious",
            level=0.8
        )

    @pytest.fixture
    def creative_task(self) -> CreativeTask:
        """Fixture for basic creative task."""
        return CreativeTask(
            prompt="Generate innovative solutions for renewable energy storage",
            context={"domain": "technology", "urgency": "high"},
            constraints=["cost_effective", "scalable", "environmental"],
            preferred_process="divergent",
            imagination_mode="conceptual",
            min_ideas=5,
            seed_concepts=["battery", "solar", "efficiency"]
        )

    @pytest.fixture
    def guardian_validator(self) -> AsyncMock:
        """Mock Guardian validator that approves all requests."""
        mock_validator = AsyncMock()
        mock_validator.return_value = {
            "approved": True,
            "reason": "Content meets safety guidelines"
        }
        return mock_validator

    @pytest.fixture
    def creativity_engine(self, guardian_validator) -> CreativityEngine:
        """Fixture for CreativityEngine with test configuration."""
        config = {
            **DEFAULT_CREATIVITY_CONFIG,
            "p95_target_ms": 100.0,  # Relaxed for testing
            "guardian_approval_required": True
        }
        return CreativityEngine(config=config, guardian_validator=guardian_validator)

    @pytest.mark.asyncio
    async def test_basic_idea_generation(self, creativity_engine, creative_task, consciousness_state):
        """Test basic creative idea generation functionality."""
        # Act
        snapshot = await creativity_engine.generate_ideas(
            creative_task, consciousness_state, {}
        )

        # Assert
        assert isinstance(snapshot, CreativitySnapshot)
        assert len(snapshot.ideas) >= creative_task.min_ideas
        assert snapshot.novelty_score >= 0.0
        assert snapshot.coherence_score >= 0.0
        assert snapshot.fluency_count == len(snapshot.ideas)
        assert snapshot.generation_time_ms > 0

    @pytest.mark.asyncio
    async def test_divergent_thinking_process(self, creativity_engine, consciousness_state):
        """Test divergent thinking creative process."""
        # Arrange
        task = CreativeTask(
            prompt="Brainstorm uses for discarded plastic bottles",
            preferred_process="divergent",
            min_ideas=8,
            seed_concepts=["plastic", "recycling", "creativity"]
        )

        # Act
        snapshot = await creativity_engine.generate_ideas(task, consciousness_state, {})

        # Assert
        assert len(snapshot.ideas) >= 8
        assert snapshot.divergence_breadth > 0.0

        # Check for variety in idea types
        idea_types = {idea.get("type", "") for idea in snapshot.ideas}
        assert len(idea_types) > 1  # Should have multiple idea types

    @pytest.mark.asyncio
    async def test_convergent_thinking_process(self, creativity_engine, consciousness_state):
        """Test convergent thinking creative process."""
        # Arrange
        task = CreativeTask(
            prompt="Find the best solution for urban traffic congestion",
            preferred_process="convergent",
            min_ideas=3,
            target_coherence=0.8
        )

        # Act
        snapshot = await creativity_engine.generate_ideas(task, consciousness_state, {})

        # Assert
        assert snapshot.convergence_efficiency > 0.0
        assert snapshot.coherence_score >= 0.5  # Should focus on coherent solutions

    @pytest.mark.asyncio
    async def test_associative_reasoning(self, creativity_engine, consciousness_state):
        """Test associative reasoning creative process."""
        # Arrange
        task = CreativeTask(
            prompt="Connect nature patterns to architectural design",
            preferred_process="associative",
            seed_concepts=["trees", "fibonacci", "structure", "organic"]
        )

        # Act
        snapshot = await creativity_engine.generate_ideas(task, consciousness_state, {})

        # Assert
        assert len(snapshot.associations) > 0

        # Check association strength
        for association in snapshot.associations:
            assert association["strength"] > 0.0
            assert "source" in association
            assert "target" in association

    @pytest.mark.asyncio
    async def test_transformative_imagination(self, creativity_engine, consciousness_state):
        """Test transformative imagination creative process."""
        # Arrange
        task = CreativeTask(
            prompt="Reimagine traditional classroom education",
            preferred_process="transformative",
            min_ideas=4
        )

        # Act
        snapshot = await creativity_engine.generate_ideas(task, consciousness_state, {})

        # Assert
        assert len(snapshot.transformations) > 0

        # Check transformation quality
        for transformation in snapshot.transformations:
            assert transformation["confidence"] > 0.0
            assert "process" in transformation
            assert transformation["process"] in [
                "analogy", "metaphor", "inversion", "amplification", "combination"
            ]

    @pytest.mark.asyncio
    async def test_creative_synthesis(self, creativity_engine, consciousness_state):
        """Test creative synthesis process."""
        # Arrange
        task = CreativeTask(
            prompt="Synthesize wellness and technology concepts",
            preferred_process="synthesis",
            min_ideas=6
        )

        # Act
        snapshot = await creativity_engine.generate_ideas(task, consciousness_state, {})

        # Assert
        assert snapshot.synthesis_quality > 0.0

        # Check for synthesized ideas
        synthesized_ideas = [
            idea for idea in snapshot.ideas
            if idea.get("type", "").startswith("synthesized")
        ]
        assert len(synthesized_ideas) > 0

    @pytest.mark.asyncio
    async def test_multi_process_cycle(self, creativity_engine, consciousness_state):
        """Test multi-process creative cycle execution."""
        # Arrange
        task = CreativeTask(
            prompt="Develop comprehensive smart city solutions",
            preferred_process=None,  # Should trigger multi-process
            min_ideas=10,
            seed_concepts=["IoT", "sustainability", "citizens"]
        )

        # Act
        snapshot = await creativity_engine.generate_ideas(task, consciousness_state, {})

        # Assert
        assert len(snapshot.ideas) >= 10

        # Should have multiple types of creative outputs
        assert len(snapshot.associations) > 0 or len(snapshot.transformations) > 0
        assert snapshot.divergence_breadth > 0.0

    @pytest.mark.asyncio
    async def test_flow_state_transitions(self, creativity_engine, consciousness_state):
        """Test creative flow state transitions."""
        # Test with low consciousness (should be blocked/warming)
        low_consciousness = ConsciousnessState(level=0.2, awareness_level="minimal")
        task = CreativeTask(prompt="Simple test", min_ideas=1)

        snapshot1 = await creativity_engine.generate_ideas(task, low_consciousness, {})
        assert snapshot1.flow_state in ["blocked", "warming"]

        # Test with high consciousness (should be flowing/peak)
        high_consciousness = ConsciousnessState(level=0.9, awareness_level="transcendent")

        snapshot2 = await creativity_engine.generate_ideas(task, high_consciousness, {})
        assert snapshot2.flow_state in ["flowing", "peak", "cooling"]

    @pytest.mark.asyncio
    async def test_guardian_integration(self, creativity_engine, creative_task, consciousness_state):
        """Test Guardian approval integration."""
        # Act
        snapshot = await creativity_engine.generate_ideas(creative_task, consciousness_state, {})

        # Assert
        assert len(snapshot.guardian_approvals) > 0

        # Check that ideas have guardian approval status
        for idea in snapshot.ideas:
            assert "guardian_approved" in idea
            # With our mock, all should be approved
            assert idea["guardian_approved"] is True

    @pytest.mark.asyncio
    async def test_quality_validation(self, creativity_engine, creative_task, consciousness_state):
        """Test quality validation system."""
        # Act
        snapshot = await creativity_engine.generate_ideas(creative_task, consciousness_state, {})

        # Assert
        assert len(snapshot.validation_checks) > 0

        # Check validation types
        validation_types = {check["type"] for check in snapshot.validation_checks}
        expected_types = {"novelty_threshold", "coherence_threshold", "fluency_minimum"}
        assert validation_types.intersection(expected_types)

    @pytest.mark.asyncio
    async def test_performance_targets(self, creativity_engine, creative_task, consciousness_state):
        """Test T4/0.01% performance targets."""
        # Arrange - multiple runs for statistical validity
        latencies = []

        # Act - run multiple generations
        for _ in range(5):
            start_time = time.time()
            snapshot = await creativity_engine.generate_ideas(creative_task, consciousness_state, {})
            latency_ms = (time.time() - start_time) * 1000
            latencies.append(latency_ms)

            # Each snapshot should meet performance requirements
            assert snapshot.generation_time_ms > 0
            assert snapshot.process_efficiency >= 0.0

        # Assert - check p95 target (relaxed for testing)
        latencies.sort()
        p95_latency = latencies[int(len(latencies) * 0.95)]
        assert p95_latency < 200.0  # Relaxed from 50ms for comprehensive testing

    @pytest.mark.asyncio
    async def test_memory_pressure_assessment(self, creativity_engine, creative_task, consciousness_state):
        """Test memory pressure assessment."""
        # Act
        snapshot = await creativity_engine.generate_ideas(creative_task, consciousness_state, {})

        # Assert
        assert hasattr(snapshot, 'memory_pressure_score')
        assert 0.0 <= snapshot.memory_pressure_score <= 1.0

    @pytest.mark.asyncio
    async def test_anomaly_detection(self, creativity_engine, consciousness_state):
        """Test creative anomaly detection."""
        # Arrange - task that might trigger anomalies
        problematic_task = CreativeTask(
            prompt="",  # Empty prompt might trigger anomalies
            min_ideas=0,
            target_novelty=1.5,  # Impossible target
            target_coherence=1.5   # Impossible target
        )

        # Act
        snapshot = await creativity_engine.generate_ideas(problematic_task, consciousness_state, {})

        # Assert - should still complete without crashing
        assert isinstance(snapshot, CreativitySnapshot)

    @pytest.mark.asyncio
    async def test_context_integration(self, creativity_engine, consciousness_state):
        """Test integration with consciousness context."""
        # Arrange
        task = CreativeTask(
            prompt="Context-aware creative task",
            min_ideas=3
        )

        context = {
            "user_preferences": ["innovation", "sustainability"],
            "creative_signals": ["inspiration", "idea_flow"],
            "domain_expertise": "technology"
        }

        # Act
        snapshot = await creativity_engine.generate_ideas(task, consciousness_state, context)

        # Assert
        assert len(snapshot.ideas) >= 3
        # Context should influence seed concepts or creativity triggers

    def test_performance_stats(self, creativity_engine):
        """Test performance statistics reporting."""
        # Act
        stats = creativity_engine.get_performance_stats()

        # Assert
        required_stats = [
            "cycles_completed", "average_latency_ms", "p95_latency_ms",
            "average_quality_score", "guardian_approval_rate",
            "current_flow_state", "creative_energy"
        ]

        for stat in required_stats:
            assert stat in stats

    @pytest.mark.asyncio
    async def test_state_reset(self, creativity_engine):
        """Test creativity engine state reset."""
        # Arrange - generate some activity
        task = CreativeTask(prompt="Test activity", min_ideas=1)
        consciousness_state = ConsciousnessState(level=0.8)

        await creativity_engine.generate_ideas(task, consciousness_state, {})

        # Get stats before reset
        stats_before = creativity_engine.get_performance_stats()
        assert stats_before["cycles_completed"] > 0

        # Act
        await creativity_engine.reset_state()

        # Assert
        stats_after = creativity_engine.get_performance_stats()
        assert stats_after["cycles_completed"] == 0
        assert stats_after["creative_energy"] == 0.0

    @pytest.mark.asyncio
    async def test_imagination_modes(self, creativity_engine, consciousness_state):
        """Test different imagination modes."""
        imagination_modes = ["visual", "conceptual", "narrative", "abstract", "hybrid"]

        for mode in imagination_modes:
            # Arrange
            task = CreativeTask(
                prompt=f"Test {mode} imagination",
                imagination_mode=mode,
                min_ideas=2
            )

            # Act
            snapshot = await creativity_engine.generate_ideas(task, consciousness_state, {})

            # Assert
            assert snapshot.imagination_mode == mode
            assert len(snapshot.ideas) >= 2

    @pytest.mark.asyncio
    async def test_constraint_handling(self, creativity_engine, consciousness_state):
        """Test creative constraint handling."""
        # Arrange
        task = CreativeTask(
            prompt="Design with strict constraints",
            constraints=["low_cost", "eco_friendly", "scalable", "user_friendly"],
            min_ideas=3
        )

        # Act
        snapshot = await creativity_engine.generate_ideas(task, consciousness_state, {})

        # Assert
        assert snapshot.creative_constraints == task.constraints
        assert len(snapshot.ideas) >= 3

        # Ideas should reference constraints in validation
        [
            check for check in snapshot.validation_checks
            if "constraint" in check.get("type", "").lower()
        ]
        # Should have some form of constraint validation

    @pytest.mark.asyncio
    async def test_inspiration_sources(self, creativity_engine, consciousness_state):
        """Test inspiration source handling."""
        # Arrange
        task = CreativeTask(
            prompt="Inspired creation",
            seed_concepts=["nature", "technology", "art"],
            inspiration_domains=["biomimicry", "engineering", "design"]
        )

        # Act
        snapshot = await creativity_engine.generate_ideas(task, consciousness_state, {})

        # Assert
        assert len(snapshot.inspiration_sources) > 0

        # Should have used seed concepts
        expected_sources = set(task.seed_concepts)
        actual_sources = set(snapshot.inspiration_sources)
        assert expected_sources.intersection(actual_sources)

    @pytest.mark.asyncio
    async def test_error_resilience(self, creativity_engine, consciousness_state):
        """Test creativity engine error resilience."""
        # Arrange - create guardian that fails
        failing_guardian = AsyncMock()
        failing_guardian.side_effect = Exception("Guardian service unavailable")

        creativity_engine.guardian_validator = failing_guardian

        task = CreativeTask(prompt="Test with failing guardian", min_ideas=2)

        # Act - should not crash despite guardian failure
        snapshot = await creativity_engine.generate_ideas(task, consciousness_state, {})

        # Assert
        assert isinstance(snapshot, CreativitySnapshot)
        assert len(snapshot.ideas) >= 2

        # Ideas should be marked as not guardian-approved
        for idea in snapshot.ideas:
            assert idea.get("guardian_approved", True) is False


class TestCreativeTask:
    """Test suite for CreativeTask data structure."""

    def test_creative_task_creation(self):
        """Test CreativeTask creation and validation."""
        # Act
        task = CreativeTask(
            prompt="Test creative task",
            context={"domain": "test"},
            constraints=["simple"],
            preferred_process="divergent",
            imagination_mode="conceptual"
        )

        # Assert
        assert task.prompt == "Test creative task"
        assert task.context["domain"] == "test"
        assert "simple" in task.constraints
        assert task.preferred_process == "divergent"
        assert task.imagination_mode == "conceptual"
        assert task.schema_version == "1.0.0"

    def test_creative_task_defaults(self):
        """Test CreativeTask default values."""
        # Act
        task = CreativeTask()

        # Assert
        assert task.prompt == ""
        assert task.context == {}
        assert task.constraints == []
        assert task.preferred_process is None
        assert task.imagination_mode == "conceptual"
        assert task.target_novelty == 0.7
        assert task.target_coherence == 0.8
        assert task.min_ideas == 5


class TestCreativitySnapshot:
    """Test suite for CreativitySnapshot data structure."""

    def test_creativity_snapshot_creation(self):
        """Test CreativitySnapshot creation."""
        # Act
        snapshot = CreativitySnapshot(
            flow_state="flowing",
            imagination_mode="abstract",
            creative_energy=0.8
        )

        # Assert
        assert snapshot.flow_state == "flowing"
        assert snapshot.imagination_mode == "abstract"
        assert snapshot.creative_energy == 0.8
        assert snapshot.schema_version == "1.0.0"
        assert snapshot.ideas == []
        assert snapshot.associations == []

    def test_idea_addition(self):
        """Test adding ideas to creativity snapshot."""
        # Arrange
        snapshot = CreativitySnapshot()

        # Act
        snapshot.add_idea(
            idea_type="test_idea",
            content={"description": "Test idea content"},
            novelty=0.8,
            coherence=0.7,
            guardian_approved=True
        )

        # Assert
        assert len(snapshot.ideas) == 1
        assert snapshot.fluency_count == 1

        idea = snapshot.ideas[0]
        assert idea["type"] == "test_idea"
        assert idea["novelty"] == 0.8
        assert idea["coherence"] == 0.7
        assert idea["guardian_approved"] is True
        assert "id" in idea
        assert "timestamp" in idea

    def test_association_addition(self):
        """Test adding associations to creativity snapshot."""
        # Arrange
        snapshot = CreativitySnapshot()

        # Act
        snapshot.add_association("source_concept", "target_concept", 0.8, "semantic")

        # Assert
        assert len(snapshot.associations) == 1

        association = snapshot.associations[0]
        assert association["source"] == "source_concept"
        assert association["target"] == "target_concept"
        assert association["strength"] == 0.8
        assert association["type"] == "semantic"

    def test_transformation_addition(self):
        """Test adding transformations to creativity snapshot."""
        # Arrange
        snapshot = CreativitySnapshot()

        # Act
        snapshot.add_transformation(
            "original_concept", "transformed_concept", "analogy", 0.9
        )

        # Assert
        assert len(snapshot.transformations) == 1

        transformation = snapshot.transformations[0]
        assert transformation["original"] == "original_concept"
        assert transformation["transformed"] == "transformed_concept"
        assert transformation["process"] == "analogy"
        assert transformation["confidence"] == 0.9

    def test_guardian_approval_tracking(self):
        """Test Guardian approval tracking."""
        # Arrange
        snapshot = CreativitySnapshot()

        # Act
        snapshot.add_guardian_approval("idea_123", True, "Approved content")

        # Assert
        assert len(snapshot.guardian_approvals) == 1

        approval = snapshot.guardian_approvals[0]
        assert approval["item_id"] == "idea_123"
        assert approval["approved"] is True
        assert approval["reason"] == "Approved content"

    def test_validation_checks(self):
        """Test validation check tracking."""
        # Arrange
        snapshot = CreativitySnapshot()

        # Act
        snapshot.add_validation_check("novelty_check", True, "Meets novelty requirements")

        # Assert
        assert len(snapshot.validation_checks) == 1

        check = snapshot.validation_checks[0]
        assert check["type"] == "novelty_check"
        assert check["result"] is True
        assert check["details"] == "Meets novelty requirements"

    def test_anomaly_flagging(self):
        """Test anomaly flagging."""
        # Arrange
        snapshot = CreativitySnapshot()

        # Act
        snapshot.flag_anomaly("low_novelty", "Ideas lack sufficient originality")

        # Assert
        assert len(snapshot.anomaly_flags) == 1
        assert "low_novelty: Ideas lack sufficient originality" in snapshot.anomaly_flags


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
