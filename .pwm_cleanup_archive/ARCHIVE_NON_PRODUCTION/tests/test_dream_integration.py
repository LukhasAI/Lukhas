#!/usr/bin/env python3
"""
Test Suite for LUKHAS Dream Integration System

Comprehensive tests for dream formation, memory linking, fragment processing,
and integration analysis capabilities.
"""

from unittest.mock import patch

import pytest

# Import the dream integration system
from memory.core_memory.dream_integration import (
    DreamIntegrator,
    DreamMemoryLinker,
    DreamState,
    DreamType,
    add_fragment,
    get_dream_integrator,
    get_dream_status,
    initiate_dream,
    integrate_dream,
)


class TestDreamMemoryLinker:
    """Test suite for DreamMemoryLinker functionality."""

    def setup_method(self):
        """Setup test fixtures."""
        self.linker = DreamMemoryLinker()
        self.test_dream_id = "dream_test_001"
        self.test_memory_ids = ["memory_001", "memory_002", "memory_003"]

    def test_create_memory_link(self):
        """Test creating bidirectional memory-dream links."""
        # Test successful link creation
        result = self.linker.create_memory_link(
            self.test_dream_id, self.test_memory_ids[0], 0.8
        )

        assert result is True
        assert self.test_dream_id in self.linker.active_links
        assert self.test_memory_ids[0] in self.linker.active_links[self.test_dream_id]

        # Test link strength storage
        link_key = f"{self.test_dream_id}:{self.test_memory_ids[0]}"
        assert link_key in self.linker.link_strength_cache
        assert self.linker.link_strength_cache[link_key] == 0.8

    def test_get_linked_memories(self):
        """Test retrieval of linked memories with strengths."""
        # Create multiple links
        self.linker.create_memory_link(self.test_dream_id, self.test_memory_ids[0], 0.9)
        self.linker.create_memory_link(self.test_dream_id, self.test_memory_ids[1], 0.7)
        self.linker.create_memory_link(self.test_dream_id, self.test_memory_ids[2], 0.5)

        # Get linked memories
        linked_memories = self.linker.get_linked_memories(self.test_dream_id)

        # Should be sorted by strength descending
        assert len(linked_memories) == 3
        assert linked_memories[0] == (self.test_memory_ids[0], 0.9)
        assert linked_memories[1] == (self.test_memory_ids[1], 0.7)
        assert linked_memories[2] == (self.test_memory_ids[2], 0.5)

    def test_find_related_dreams(self):
        """Test finding dreams related to a specific memory."""
        dream_ids = ["dream_001", "dream_002", "dream_003"]
        memory_id = "memory_shared"

        # Create links from multiple dreams to same memory
        for dream_id in dream_ids:
            self.linker.create_memory_link(dream_id, memory_id, 0.6)

        # Find related dreams
        related_dreams = self.linker.find_related_dreams(memory_id)

        assert len(related_dreams) == 3
        assert all(dream_id in related_dreams for dream_id in dream_ids)

    def test_empty_links(self):
        """Test behavior with no links."""
        # Test getting links for non-existent dream
        linked_memories = self.linker.get_linked_memories("non_existent_dream")
        assert linked_memories == []

        # Test finding related dreams for non-existent memory
        related_dreams = self.linker.find_related_dreams("non_existent_memory")
        assert related_dreams == []


class TestDreamIntegrator:
    """Test suite for main DreamIntegrator functionality."""

    def setup_method(self):
        """Setup test fixtures."""
        self.config = {
            "max_active_dreams": 3,
            "formation_threshold": 0.6,
            "integration_timeout": 1800,
        }
        self.integrator = DreamIntegrator(self.config)
        self.test_memory_ids = ["mem_001", "mem_002", "mem_003"]
        self.emotional_context = {"curiosity": 0.8, "satisfaction": 0.6}

    def test_initialization(self):
        """Test DreamIntegrator initialization."""
        assert self.integrator.max_active_dreams == 3
        assert self.integrator.dream_formation_threshold == 0.6
        assert self.integrator.integration_timeout == 1800
        assert len(self.integrator.active_dreams) == 0
        assert len(self.integrator.dream_archive) == 0

    def test_initiate_dream_formation(self):
        """Test dream formation initiation."""
        # Test successful dream formation
        dream_id = self.integrator.initiate_dream_formation(
            self.test_memory_ids, DreamType.MEMORY_CONSOLIDATION, self.emotional_context
        )

        assert dream_id is not None
        assert dream_id in self.integrator.active_dreams

        # Verify dream session properties
        dream_session = self.integrator.active_dreams[dream_id]
        assert dream_session.dream_type == DreamType.MEMORY_CONSOLIDATION
        assert dream_session.state == DreamState.FORMING
        assert dream_session.memory_fold_ids == set(self.test_memory_ids)
        assert dream_session.emotional_signature == self.emotional_context

        # Verify metrics updated
        assert self.integrator.dreams_created == 1

    def test_dream_capacity_limit(self):
        """Test dream formation when at capacity."""
        # Fill up to capacity
        for i in range(self.config["max_active_dreams"]):
            dream_id = self.integrator.initiate_dream_formation([f"mem_{i}"])
            assert dream_id is not None

        # Try to create one more - should fail
        overflow_dream_id = self.integrator.initiate_dream_formation(["mem_overflow"])
        assert overflow_dream_id is None
        assert len(self.integrator.active_dreams) == self.config["max_active_dreams"]

    def test_add_dream_fragment(self):
        """Test adding fragments to dreams."""
        # Create a dream first
        dream_id = self.integrator.initiate_dream_formation(self.test_memory_ids)
        assert dream_id is not None

        # Add a fragment
        fragment_content = {
            "type": "symbolic_connection",
            "content": "Memory patterns showing learning progression",
            "confidence": 0.8,
        }

        result = self.integrator.add_dream_fragment(
            dream_id,
            fragment_content,
            memory_sources=["mem_001", "mem_002"],
            emotional_intensity=0.7,
        )

        assert result is True

        # Verify fragment was added
        dream_session = self.integrator.active_dreams[dream_id]
        assert len(dream_session.fragments) == 1
        assert dream_session.state == DreamState.ACTIVE

        fragment = dream_session.fragments[0]
        assert fragment.content == fragment_content
        assert fragment.emotional_intensity == 0.7
        assert fragment.memory_sources == ["mem_001", "mem_002"]

    def test_add_fragment_to_nonexistent_dream(self):
        """Test adding fragment to non-existent dream."""
        result = self.integrator.add_dream_fragment(
            "non_existent_dream", {"test": "content"}
        )
        assert result is False

    def test_process_dream_integration(self):
        """Test complete dream integration process."""
        # Create dream with fragments
        dream_id = self.integrator.initiate_dream_formation(self.test_memory_ids)

        # Add multiple fragments
        fragments = [
            {"type": "pattern", "content": "Recurring behavior X"},
            {"type": "insight", "content": "Connection between A and B"},
            {"type": "emotion", "content": "Positive reinforcement loop"},
        ]

        for fragment_content in fragments:
            self.integrator.add_dream_fragment(dream_id, fragment_content)

        # Process integration
        result = self.integrator.process_dream_integration(dream_id)

        # Verify successful integration
        assert result["success"] is True
        assert result["dream_id"] == dream_id
        assert result["fragments_processed"] == 3
        assert result["memory_connections"] == len(self.test_memory_ids)
        assert "integration_score" in result
        assert "insights_count" in result

        # Verify dream moved to archive
        assert dream_id not in self.integrator.active_dreams
        assert dream_id in self.integrator.dream_archive

        # Verify metrics updated
        assert self.integrator.dreams_integrated == 1

    def test_integration_nonexistent_dream(self):
        """Test integration of non-existent dream."""
        result = self.integrator.process_dream_integration("non_existent_dream")
        assert result["success"] is False
        assert "error" in result

    def test_get_dream_insights(self):
        """Test retrieving dream insights."""
        # Create and integrate a dream
        dream_id = self.integrator.initiate_dream_formation(self.test_memory_ids)
        self.integrator.add_dream_fragment(dream_id, {"high_emotion": True})
        integration_result = self.integrator.process_dream_integration(dream_id)

        # Get insights
        insights = self.integrator.get_dream_insights(dream_id)

        # Should have insights generated during integration
        assert len(insights) > 0
        assert all("type" in insight for insight in insights)
        assert all("confidence" in insight for insight in insights)

    def test_find_dreams_by_memory(self):
        """Test finding dreams associated with specific memory."""
        memory_id = "target_memory"

        # Create multiple dreams with the target memory
        dream_ids = []
        for i in range(3):
            dream_id = self.integrator.initiate_dream_formation(
                [memory_id, f"other_mem_{i}"]
            )
            dream_ids.append(dream_id)

        # Find dreams by memory
        associated_dreams = self.integrator.find_dreams_by_memory(memory_id)

        assert len(associated_dreams) == 3
        assert all(
            dream_info["dream_id"] in dream_ids for dream_info in associated_dreams
        )

    def test_get_system_status(self):
        """Test system status reporting."""
        # Create some dreams to have meaningful status
        dream_id1 = self.integrator.initiate_dream_formation(["mem_1"])
        dream_id2 = self.integrator.initiate_dream_formation(["mem_2"])
        self.integrator.process_dream_integration(dream_id1)

        status = self.integrator.get_system_status()

        # Verify status structure
        assert status["system_status"] == "operational"
        assert status["module_version"] == "1.0.0"
        assert status["active_dreams"] == 1  # One still active
        assert status["archived_dreams"] == 1  # One integrated
        assert status["max_capacity"] == 3

        # Verify metrics
        metrics = status["metrics"]
        assert metrics["dreams_created"] == 2
        assert metrics["dreams_integrated"] == 1
        assert metrics["integration_failures"] == 0
        assert "success_rate" in metrics

        # Verify configuration
        config = status["configuration"]
        assert config["formation_threshold"] == 0.6
        assert config["integration_timeout"] == 1800
        assert config["max_active_dreams"] == 3


class TestDreamTypes:
    """Test suite for dream type handling."""

    def setup_method(self):
        """Setup test fixtures."""
        self.integrator = DreamIntegrator()

    def test_different_dream_types(self):
        """Test creation of different dream types."""
        dream_types = [
            DreamType.MEMORY_CONSOLIDATION,
            DreamType.CREATIVE_SYNTHESIS,
            DreamType.PROBLEM_SOLVING,
            DreamType.EMOTIONAL_PROCESSING,
            DreamType.SYMBOLIC_INTEGRATION,
        ]

        created_dreams = []
        for dream_type in dream_types:
            dream_id = self.integrator.initiate_dream_formation(["mem_001"], dream_type)
            assert dream_id is not None
            created_dreams.append(dream_id)

            # Verify dream type
            dream_session = self.integrator.active_dreams[dream_id]
            assert dream_session.dream_type == dream_type

        assert len(created_dreams) == len(dream_types)
        assert len(set(created_dreams)) == len(dream_types)  # All unique


class TestModuleLevelInterface:
    """Test module-level interface functions."""

    def setup_method(self):
        """Setup test fixtures."""
        # Reset the default integrator
        from memory.core_memory.dream_integration import (
            default_dream_integrator,
        )

        default_dream_integrator.__init__()

    def test_get_dream_integrator(self):
        """Test getting default dream integrator."""
        integrator = get_dream_integrator()
        assert isinstance(integrator, DreamIntegrator)

    def test_initiate_dream_module_function(self):
        """Test module-level dream initiation."""
        dream_id = initiate_dream(
            ["mem_001", "mem_002"], "memory_consolidation", {"curiosity": 0.7}
        )

        assert dream_id is not None

        # Verify dream was created
        integrator = get_dream_integrator()
        assert dream_id in integrator.active_dreams

    def test_initiate_dream_invalid_type(self):
        """Test module-level function with invalid dream type."""
        dream_id = initiate_dream(["mem_001"], "invalid_dream_type")
        assert dream_id is None

    def test_add_fragment_module_function(self):
        """Test module-level fragment addition."""
        # Create dream first
        dream_id = initiate_dream(["mem_001"])
        assert dream_id is not None

        # Add fragment
        result = add_fragment(dream_id, {"test": "content"})
        assert result is True

    def test_integrate_dream_module_function(self):
        """Test module-level dream integration."""
        # Create and add fragment to dream
        dream_id = initiate_dream(["mem_001"])
        add_fragment(dream_id, {"test": "content"})

        # Integrate dream
        result = integrate_dream(dream_id)
        assert result["success"] is True
        assert result["dream_id"] == dream_id

    def test_get_dream_status_module_function(self):
        """Test module-level status function."""
        status = get_dream_status()
        assert isinstance(status, dict)
        assert "system_status" in status
        assert "module_version" in status


class TestDreamStates:
    """Test dream state transitions."""

    def setup_method(self):
        """Setup test fixtures."""
        self.integrator = DreamIntegrator()

    def test_dream_state_progression(self):
        """Test normal dream state progression."""
        # Create dream - should start in FORMING state
        dream_id = self.integrator.initiate_dream_formation(["mem_001"])
        dream_session = self.integrator.active_dreams[dream_id]
        assert dream_session.state == DreamState.FORMING

        # Add fragment - should transition to ACTIVE
        self.integrator.add_dream_fragment(dream_id, {"content": "test"})
        assert dream_session.state == DreamState.ACTIVE

        # Integrate dream - should transition to INTEGRATING then ARCHIVED
        self.integrator.process_dream_integration(dream_id)

        # Dream should now be archived
        archived_dream = self.integrator.dream_archive[dream_id]
        assert archived_dream.state == DreamState.ARCHIVED
        assert archived_dream.completed_at is not None


class TestDreamFragments:
    """Test dream fragment functionality."""

    def setup_method(self):
        """Setup test fixtures."""
        self.integrator = DreamIntegrator()
        self.dream_id = self.integrator.initiate_dream_formation(["mem_001"])

    def test_fragment_properties(self):
        """Test dream fragment property handling."""
        fragment_content = {
            "type": "insight",
            "description": "Connection discovered between concepts A and B",
            "confidence": 0.85,
        }

        result = self.integrator.add_dream_fragment(
            self.dream_id,
            fragment_content,
            memory_sources=["mem_001", "mem_002"],
            emotional_intensity=0.9,
        )

        assert result is True

        # Verify fragment properties
        dream_session = self.integrator.active_dreams[self.dream_id]
        fragment = dream_session.fragments[0]

        assert fragment.content == fragment_content
        assert fragment.memory_sources == ["mem_001", "mem_002"]
        assert fragment.emotional_intensity == 0.9
        assert fragment.symbolic_weight > 0  # Should calculate symbolic weight
        assert fragment.integration_status == "pending"
        assert fragment.timestamp is not None

    def test_multiple_fragments(self):
        """Test handling multiple fragments in a dream."""
        fragment_contents = [
            {"type": "pattern", "content": "Recurring theme X"},
            {"type": "emotion", "content": "Positive association"},
            {"type": "insight", "content": "Novel connection Y-Z"},
        ]

        # Add multiple fragments
        for content in fragment_contents:
            result = self.integrator.add_dream_fragment(self.dream_id, content)
            assert result is True

        # Verify all fragments stored
        dream_session = self.integrator.active_dreams[self.dream_id]
        assert len(dream_session.fragments) == 3

        # Verify fragment order preserved
        for i, fragment in enumerate(dream_session.fragments):
            assert fragment.content == fragment_contents[i]


class TestErrorHandling:
    """Test error handling and edge cases."""

    def setup_method(self):
        """Setup test fixtures."""
        self.integrator = DreamIntegrator()

    def test_empty_memory_list(self):
        """Test dream formation with empty memory list."""
        dream_id = self.integrator.initiate_dream_formation([])

        # Should still create dream but with empty memory set
        assert dream_id is not None
        dream_session = self.integrator.active_dreams[dream_id]
        assert len(dream_session.memory_fold_ids) == 0

    def test_none_memory_list(self):
        """Test dream formation with None memory list."""
        # The function catches exceptions and returns None instead of raising
        result = self.integrator.initiate_dream_formation(None)
        assert result is None

    def test_invalid_emotional_context(self):
        """Test dream formation with invalid emotional context."""
        # The function will fail with invalid emotional context
        dream_id = self.integrator.initiate_dream_formation(
            ["mem_001"], emotional_context="invalid"  # Should be dict
        )

        # Expect None since the function catches the exception
        assert dream_id is None

    def test_integration_with_no_fragments(self):
        """Test integrating dream with no fragments."""
        dream_id = self.integrator.initiate_dream_formation(["mem_001"])

        # Integrate without adding fragments
        result = self.integrator.process_dream_integration(dream_id)

        assert result["success"] is True
        assert result["fragments_processed"] == 0
        # Should still generate some insights even without fragments


class TestPerformanceAndScaling:
    """Test performance characteristics and scaling behavior."""

    def setup_method(self):
        """Setup test fixtures."""
        self.integrator = DreamIntegrator({"max_active_dreams": 50})

    def test_large_memory_set(self):
        """Test dream formation with large memory set."""
        large_memory_set = [f"mem_{i:04d}" for i in range(100)]

        dream_id = self.integrator.initiate_dream_formation(large_memory_set)
        assert dream_id is not None

        dream_session = self.integrator.active_dreams[dream_id]
        assert len(dream_session.memory_fold_ids) == 100

    def test_many_fragments(self):
        """Test dream with many fragments."""
        dream_id = self.integrator.initiate_dream_formation(["mem_001"])

        # Add many fragments
        num_fragments = 50
        for i in range(num_fragments):
            result = self.integrator.add_dream_fragment(
                dream_id, {"fragment_id": i, "content": f"Fragment {i}"}
            )
            assert result is True

        # Verify all fragments stored
        dream_session = self.integrator.active_dreams[dream_id]
        assert len(dream_session.fragments) == num_fragments

        # Test integration performance with many fragments
        result = self.integrator.process_dream_integration(dream_id)
        assert result["success"] is True
        assert result["fragments_processed"] == num_fragments

    def test_concurrent_dream_operations(self):
        """Test handling multiple dreams concurrently."""
        # Create multiple dreams
        dream_ids = []
        for i in range(10):
            dream_id = self.integrator.initiate_dream_formation([f"mem_set_{i}"])
            dream_ids.append(dream_id)

        # Add fragments to each
        for dream_id in dream_ids:
            self.integrator.add_dream_fragment(dream_id, {"test": "concurrent"})

        # Integrate all dreams
        integration_results = []
        for dream_id in dream_ids:
            result = self.integrator.process_dream_integration(dream_id)
            integration_results.append(result)

        # Verify all integrations successful
        assert all(result["success"] for result in integration_results)
        assert len(self.integrator.dream_archive) == 10


# Test fixtures and utilities
@pytest.fixture
def dream_integrator():
    """Fixture providing a fresh DreamIntegrator instance."""
    return DreamIntegrator(
        {
            "max_active_dreams": 5,
            "formation_threshold": 0.7,
            "integration_timeout": 3600,
        }
    )


@pytest.fixture
def sample_memory_ids():
    """Fixture providing sample memory IDs."""
    return ["memory_001", "memory_002", "memory_003", "memory_004"]


@pytest.fixture
def sample_emotional_context():
    """Fixture providing sample emotional context."""
    return {"curiosity": 0.8, "satisfaction": 0.6, "engagement": 0.7}


# Integration tests
class TestDreamSystemIntegration:
    """Integration tests for the complete dream system."""

    def test_complete_dream_lifecycle(
        self, dream_integrator, sample_memory_ids, sample_emotional_context
    ):
        """Test complete dream lifecycle from formation to integration."""
        # 1. Initiate dream formation
        dream_id = dream_integrator.initiate_dream_formation(
            sample_memory_ids, DreamType.CREATIVE_SYNTHESIS, sample_emotional_context
        )
        assert dream_id is not None

        # 2. Add multiple fragments
        fragments = [
            {
                "type": "pattern",
                "content": "Cyclical behavior pattern",
                "confidence": 0.8,
            },
            {
                "type": "insight",
                "content": "Novel connection between domains",
                "confidence": 0.9,
            },
            {
                "type": "emotion",
                "content": "Positive reinforcement detected",
                "confidence": 0.7,
            },
        ]

        for fragment in fragments:
            success = dream_integrator.add_dream_fragment(dream_id, fragment)
            assert success is True

        # 3. Process integration
        integration_result = dream_integrator.process_dream_integration(dream_id)
        assert integration_result["success"] is True
        assert integration_result["fragments_processed"] == 3

        # 4. Verify insights generated
        insights = dream_integrator.get_dream_insights(dream_id)
        assert len(insights) > 0

        # 5. Verify dream archived properly
        assert dream_id in dream_integrator.dream_archive
        assert dream_id not in dream_integrator.active_dreams

        # 6. Verify system status updated
        status = dream_integrator.get_system_status()
        assert status["metrics"]["dreams_created"] == 1
        assert status["metrics"]["dreams_integrated"] == 1

    def test_memory_linking_integration(self, dream_integrator):
        """Test integration between dream system and memory linking."""
        memory_ids = ["mem_A", "mem_B", "mem_C"]

        # Create dream
        dream_id = dream_integrator.initiate_dream_formation(memory_ids)

        # Verify memory links created
        linked_memories = dream_integrator.memory_linker.get_linked_memories(dream_id)
        assert len(linked_memories) == 3

        # Verify bidirectional linking
        for memory_id in memory_ids:
            related_dreams = dream_integrator.memory_linker.find_related_dreams(
                memory_id
            )
            assert dream_id in related_dreams

    def test_system_recovery_after_errors(self, dream_integrator):
        """Test system recovery after various error conditions."""
        # Create a dream
        dream_id = dream_integrator.initiate_dream_formation(["mem_001"])

        # Simulate error during fragment addition (mock failure)
        with patch.object(dream_integrator, "add_dream_fragment", return_value=False):
            result = dream_integrator.add_dream_fragment(dream_id, {"test": "content"})
            assert result is False

        # System should still be operational
        status = dream_integrator.get_system_status()
        assert status["system_status"] == "operational"

        # Should still be able to add fragments normally
        result = dream_integrator.add_dream_fragment(dream_id, {"recovery": "test"})
        assert result is True


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v", "--tb=short"])
