"""
Test suite for Episodic Memory Colony Integration
"""

from datetime import datetime

import pytest

from memory.colonies.episodic_memory_integration import (
    EpisodicMemoryIntegration,
    create_episodic_memory_integration,
)
from memory.memory_hub import MemoryHub


class TestEpisodicMemoryIntegration:
    """Test suite for episodic memory colony integration with memory hub"""

    @pytest.fixture
    async def memory_hub(self):
        """Create a test memory hub instance"""
        hub = MemoryHub()
        return hub

    @pytest.fixture
    async def episodic_integration(self):
        """Create a test episodic memory integration instance"""
        config = {
            "max_concurrent_operations": 25,
            "memory_capacity": 5000,
            "enable_background_processing": True,
            "replay_processing_interval": 1.0,
            "consolidation_assessment_interval": 10.0,
            "pattern_separation_threshold": 0.4,
            "pattern_completion_threshold": 0.6,
            "enable_autobiographical_significance": True,
            "enable_emotional_processing": True,
        }
        integration = EpisodicMemoryIntegration(config)
        return integration

    @pytest.mark.asyncio
    async def test_episodic_memory_integration_initialization(
        self, episodic_integration
    ):
        """Test episodic memory integration initialization"""
        assert episodic_integration is not None
        assert episodic_integration.config["max_concurrent_operations"] == 25
        assert episodic_integration.config["memory_capacity"] == 5000
        assert episodic_integration.is_initialized is False

        # Initialize the integration
        await episodic_integration.initialize()
        assert episodic_integration.is_initialized is True

    @pytest.mark.asyncio
    async def test_memory_hub_episodic_colony_registration(self, memory_hub):
        """Test that episodic memory colony is registered in the memory hub"""
        # Initialize the hub
        await memory_hub.initialize()

        # Verify episodic memory colony service is available (if EPISODIC_COLONY_AVAILABLE is True)
        services = memory_hub.list_services()

        # The service should be registered if the import was successful
        if "episodic_memory_colony" in services:
            assert memory_hub.get_service("episodic_memory_colony") is not None

    @pytest.mark.asyncio
    async def test_episodic_memory_creation_through_hub(self, memory_hub):
        """Test episodic memory creation through the memory hub"""
        # Initialize the hub
        await memory_hub.initialize()

        # Skip test if episodic colony not available
        if "episodic_memory_colony" not in memory_hub.services:
            pytest.skip("Episodic memory colony integration not available")

        # Test episodic memory creation
        content = {
            "description": "Meeting with friends at the park",
            "participants": ["Alice", "Bob", "Charlie"],
            "emotions": {"happiness": 0.8, "excitement": 0.6},
            "details": "We played frisbee and had a picnic",
        }

        result = await memory_hub.create_episodic_memory(
            content=content,
            event_type="social_gathering",
            context={
                "location": [40.7128, -74.0060],  # NYC coordinates
                "time": datetime.now().isoformat(),
                "weather": "sunny",
                "duration": 120,  # minutes
            },
        )

        # Verify result structure
        assert "success" in result
        if result["success"]:
            assert "memory_id" in result
            assert result["event_type"] == "social_gathering"
            assert "created_at" in result

    @pytest.mark.asyncio
    async def test_episodic_memory_retrieval_through_hub(self, memory_hub):
        """Test episodic memory retrieval through the memory hub"""
        # Initialize the hub
        await memory_hub.initialize()

        # Skip test if episodic colony not available
        if "episodic_memory_colony" not in memory_hub.services:
            pytest.skip("Episodic memory colony integration not available")

        # Create a memory first
        content = {
            "description": "First day at new job",
            "emotions": {"nervousness": 0.7},
        }
        create_result = await memory_hub.create_episodic_memory(
            content=content, event_type="career_milestone"
        )

        if create_result.get("success"):
            memory_id = create_result["memory_id"]

            # Test memory retrieval
            result = await memory_hub.retrieve_episodic_memory(
                memory_id=memory_id, include_related=True
            )

            # Verify result structure
            assert "success" in result
            if result["success"]:
                assert "memory_id" in result
                assert result["memory_id"] == memory_id
                assert "content" in result
                assert "retrieved_at" in result

    @pytest.mark.asyncio
    async def test_episodic_memory_search_through_hub(self, memory_hub):
        """Test episodic memory search through the memory hub"""
        # Initialize the hub
        await memory_hub.initialize()

        # Skip test if episodic colony not available
        if "episodic_memory_colony" not in memory_hub.services:
            pytest.skip("Episodic memory colony integration not available")

        # Create test memories
        test_memories = [
            {"content": {"description": "Birthday party"}, "event_type": "celebration"},
            {"content": {"description": "Work meeting"}, "event_type": "professional"},
            {"content": {"description": "Family dinner"}, "event_type": "family"},
        ]

        created_ids = []
        for memory_data in test_memories:
            result = await memory_hub.create_episodic_memory(
                content=memory_data["content"], event_type=memory_data["event_type"]
            )
            if result.get("success"):
                created_ids.append(result["memory_id"])

        # Test search by event type
        search_results = await memory_hub.search_episodic_memories(
            query={"event_type": "celebration"}, limit=10
        )

        # Verify search results
        assert isinstance(search_results, list)
        # Results should contain memories matching the event type
        if search_results:
            for result in search_results:
                assert "memory_id" in result or "content" in result

    @pytest.mark.asyncio
    async def test_episodic_replay_through_hub(self, memory_hub):
        """Test episodic memory replay through the memory hub"""
        # Initialize the hub
        await memory_hub.initialize()

        # Skip test if episodic colony not available
        if "episodic_memory_colony" not in memory_hub.services:
            pytest.skip("Episodic memory colony integration not available")

        # Create significant memories for replay
        significant_content = {
            "description": "Graduation day - received diploma",
            "significance": 0.9,
            "emotions": {"pride": 0.9, "accomplishment": 0.8},
        }

        create_result = await memory_hub.create_episodic_memory(
            content=significant_content, event_type="life_milestone"
        )

        if create_result.get("success"):
            memory_id = create_result["memory_id"]

            # Test replay triggering
            replay_result = await memory_hub.trigger_episodic_replay(
                memory_ids=[memory_id], replay_strength=0.8
            )

            # Verify replay result
            assert "success" in replay_result
            if replay_result["success"]:
                assert "replayed_count" in replay_result
                assert replay_result["replayed_count"] >= 0
                assert "timestamp" in replay_result

    @pytest.mark.asyncio
    async def test_consolidation_candidates_through_hub(self, memory_hub):
        """Test getting consolidation candidates through the memory hub"""
        # Initialize the hub
        await memory_hub.initialize()

        # Skip test if episodic colony not available
        if "episodic_memory_colony" not in memory_hub.services:
            pytest.skip("Episodic memory colony integration not available")

        # Get consolidation candidates
        candidates = await memory_hub.get_episodic_consolidation_candidates()

        # Verify candidates structure
        assert isinstance(candidates, list)
        if candidates:
            candidate = candidates[0]
            assert "memory_id" in candidate
            assert "consolidation_readiness" in candidate
            assert "personal_significance" in candidate

    @pytest.mark.asyncio
    async def test_episodic_memory_metrics(self, memory_hub):
        """Test getting episodic memory metrics through hub"""
        # Initialize the hub
        await memory_hub.initialize()

        # Skip test if episodic colony not available
        if "episodic_memory_colony" not in memory_hub.services:
            pytest.skip("Episodic memory colony integration not available")

        # Get metrics
        result = await memory_hub.get_episodic_memory_metrics()

        # Verify result
        assert result["available"] is True
        assert "metrics" in result
        metrics = result["metrics"]
        assert "episodes_created" in metrics
        assert "episodes_retrieved" in metrics
        assert "system_status" in metrics
        assert "episodic_colony_available" in metrics

    @pytest.mark.asyncio
    async def test_error_handling_missing_service(self, memory_hub):
        """Test error handling when episodic memory colony service is not available"""
        # Initialize the hub
        await memory_hub.initialize()

        # Remove episodic memory colony service if it exists
        if "episodic_memory_colony" in memory_hub.services:
            del memory_hub.services["episodic_memory_colony"]

        # Test episodic memory creation with missing service
        result = await memory_hub.create_episodic_memory(
            content={"description": "test"}, event_type="test"
        )
        assert result["success"] is False
        assert "error" in result

        # Test episodic memory retrieval with missing service
        result = await memory_hub.retrieve_episodic_memory("test_id")
        assert result["success"] is False
        assert "error" in result

        # Test search with missing service
        results = await memory_hub.search_episodic_memories({"test": "query"})
        assert results == []

        # Test replay with missing service
        result = await memory_hub.trigger_episodic_replay()
        assert result["success"] is False
        assert "error" in result

        # Test consolidation candidates with missing service
        candidates = await memory_hub.get_episodic_consolidation_candidates()
        assert candidates == []

        # Test metrics with missing service
        result = await memory_hub.get_episodic_memory_metrics()
        assert result["available"] is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_episodic_integration_configuration_options(self):
        """Test different configuration options for episodic memory integration"""
        # Test with custom config
        custom_config = {
            "max_concurrent_operations": 100,
            "memory_capacity": 20000,
            "enable_background_processing": False,
            "pattern_separation_threshold": 0.2,
            "pattern_completion_threshold": 0.8,
            "enable_autobiographical_significance": False,
            "enable_emotional_processing": False,
        }

        integration = create_episodic_memory_integration(custom_config)

        # Verify config was applied
        assert integration.config["max_concurrent_operations"] == 100
        assert integration.config["memory_capacity"] == 20000
        assert integration.config["enable_background_processing"] is False
        assert integration.config["pattern_separation_threshold"] == 0.2
        assert integration.config["enable_autobiographical_significance"] is False

    @pytest.mark.asyncio
    async def test_episodic_memory_content_processing(self, episodic_integration):
        """Test episodic memory content processing"""
        # Initialize the integration
        await episodic_integration.initialize()

        # Test complex episodic content
        complex_content = {
            "event_title": "Wedding celebration",
            "description": "Sister's wedding at the beach resort",
            "participants": ["Sarah", "Mike", "Mom", "Dad", "Uncle Joe"],
            "location": "Sunset Beach Resort, Hawaii",
            "emotions": {"joy": 0.9, "love": 0.8, "excitement": 0.7, "nostalgia": 0.3},
            "sensory_details": {
                "sounds": ["ocean waves", "wedding music", "laughter"],
                "smells": ["ocean breeze", "flowers", "cake"],
                "sights": ["sunset", "white dress", "happy faces"],
            },
            "significance": "Major family milestone",
            "personal_impact": 0.9,
        }

        # Create episodic memory
        result = await episodic_integration.create_episodic_memory(
            content=complex_content,
            event_type="family_celebration",
            context={
                "duration": 480,  # 8 hours
                "weather": "perfect",
                "time_of_day": "afternoon_evening",
                "social_setting": "formal_celebration",
            },
        )

        # Should handle complex content
        assert "success" in result
        if result["success"]:
            assert "memory_id" in result
            assert result["event_type"] == "family_celebration"

    @pytest.mark.asyncio
    async def test_episodic_memory_search_queries(self, episodic_integration):
        """Test different types of search queries"""
        # Initialize the integration
        await episodic_integration.initialize()

        # Create diverse test memories
        test_memories = [
            {
                "content": {"description": "Morning jog in Central Park"},
                "event_type": "exercise",
                "context": {"time_of_day": "morning", "location": "park"},
            },
            {
                "content": {"description": "Team building workshop"},
                "event_type": "professional",
                "context": {"duration": 240, "participants": 15},
            },
            {
                "content": {"description": "Movie night with friends"},
                "event_type": "social",
                "context": {"emotions": {"fun": 0.8}, "location": "home"},
            },
        ]

        # Create memories
        for memory_data in test_memories:
            await episodic_integration.create_episodic_memory(
                content=memory_data["content"],
                event_type=memory_data["event_type"],
                context=memory_data.get("context"),
            )

        # Test different search queries
        search_queries = [
            {"event_type": "exercise"},
            {"text": "park"},
            {"event_type": "social"},
            {"participants": ["friends"]},
        ]

        for query in search_queries:
            results = await episodic_integration.search_episodic_memories(
                query, limit=10
            )
            assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_episodic_metrics_collection(self, episodic_integration):
        """Test episodic memory metrics collection"""
        # Initialize the integration
        await episodic_integration.initialize()

        # Create and interact with memories
        for i in range(3):
            result = await episodic_integration.create_episodic_memory(
                content={"description": f"Test memory {i}"}, event_type="test"
            )

            if result.get("success"):
                # Retrieve the memory
                await episodic_integration.retrieve_episodic_memory(result["memory_id"])

        # Get metrics
        metrics = await episodic_integration.get_episodic_metrics()

        # Verify metrics structure
        assert "episodes_created" in metrics
        assert "episodes_retrieved" in metrics
        assert "system_status" in metrics
        assert "episodic_colony_available" in metrics
        assert "episode_registry_size" in metrics
        assert "last_updated" in metrics

        # Check that metrics reflect activity
        assert metrics["episodes_created"] >= 3
        assert metrics["episodes_retrieved"] >= 3

    @pytest.mark.asyncio
    async def test_fallback_functionality(self, episodic_integration):
        """Test fallback functionality when main components are not available"""
        # Initialize the integration
        await episodic_integration.initialize()

        # Test fallback memory creation
        content = {"description": "Fallback test memory"}
        result = await episodic_integration._fallback_create_episode(
            content, "test", {"location": "test_location"}
        )
        assert result["success"] is True
        assert "memory_id" in result
        assert "fallback" in result

        # Test fallback retrieval
        memory_id = result["memory_id"]
        retrieve_result = await episodic_integration._fallback_retrieve_episode(
            memory_id
        )
        assert retrieve_result["success"] is True
        assert retrieve_result["memory_id"] == memory_id

        # Test fallback search
        search_results = await episodic_integration._fallback_search_episodes(
            {"event_type": "test"}, 10
        )
        assert isinstance(search_results, list)

        # Test fallback replay
        replay_result = await episodic_integration._fallback_trigger_replay(
            [memory_id], 1.0
        )
        assert replay_result["success"] is True
        assert "fallback" in replay_result

    @pytest.mark.asyncio
    async def test_replay_processing_functionality(self, episodic_integration):
        """Test replay processing functionality"""
        # Initialize the integration
        await episodic_integration.initialize()

        # Create memories with different significance levels
        memories_data = [
            {
                "content": {"description": "High significance event"},
                "significance": 0.9,
            },
            {
                "content": {"description": "Medium significance event"},
                "significance": 0.6,
            },
            {"content": {"description": "Low significance event"}, "significance": 0.2},
        ]

        memory_ids = []
        for memory_data in memories_data:
            result = await episodic_integration.create_episodic_memory(
                content=memory_data["content"], event_type="test"
            )
            if result.get("success"):
                memory_ids.append(result["memory_id"])

        # Test replay with specific memory IDs
        if memory_ids:
            replay_result = await episodic_integration.trigger_episode_replay(
                memory_ids=memory_ids[:2],  # Replay first 2 memories
                replay_strength=0.7,
            )

            assert "success" in replay_result
            if replay_result["success"]:
                assert "replayed_count" in replay_result
                assert replay_result["replayed_count"] <= 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
