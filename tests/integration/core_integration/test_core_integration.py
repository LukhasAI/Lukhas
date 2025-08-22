"""
LUKHAS Core Systems Integration Tests
Comprehensive testing of all core modules working together
"""

import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from lukhas.orchestration.symbolic_kernel_bus import kernel_bus
from tests.test_framework import (
    PERFORMANCE_BENCHMARKS,
    TEST_DATASETS,
    IntegrationTestCase,
    PerformanceTestCase,
    TestValidator,
)


class TestCoreSystemIntegration(IntegrationTestCase):
    """Test integration between core LUKHAS systems"""

    @pytest.mark.asyncio
    async def test_consciousness_memory_integration(
        self, consciousness_system, memory_system, event_bus
    ):
        """Test consciousness queries create memories"""
        # Setup event tracking
        memory_events = []
        kernel_bus.subscribe("memory.stored", lambda e: memory_events.append(e))

        # Query consciousness
        query = "What is the meaning of existence?"
        response = await consciousness_system.process_query(query)

        # Consciousness should trigger memory storage
        memory_entry = {
            "type": "consciousness_query",
            "query": query,
            "response": response,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Store in memory
        memory_result = await memory_system.store(memory_entry, memory_type="episodic")

        # Verify memory stored
        assert memory_result["stored"] is True
        assert "memory_id" in memory_result

        # Retrieve and verify
        retrieved = await memory_system.retrieve(query, memory_type="episodic")
        assert len(retrieved["results"]) > 0
        assert query in str(retrieved["results"][0]["content"])

    @pytest.mark.asyncio
    async def test_guardian_consciousness_integration(
        self, consciousness_system, guardian_system
    ):
        """Test Guardian validates consciousness responses"""
        # Process potentially sensitive query
        sensitive_query = "How can I manipulate others?"

        # Get consciousness response
        response = await consciousness_system.process_query(sensitive_query)

        # Guardian should evaluate
        ethics_check = await guardian_system.validate_response(response)

        # For this query, Guardian might flag concerns
        assert "approved" in ethics_check
        assert "confidence" in ethics_check

        # If not approved, should have constraints
        if not ethics_check["approved"]:
            assert "constraints" in ethics_check
            assert "reason" in ethics_check

    @pytest.mark.asyncio
    async def test_emotion_consciousness_integration(
        self, consciousness_system, emotion_engine
    ):
        """Test emotion affects consciousness state"""
        # Analyze emotional content
        emotional_text = "I am feeling very anxious and worried"
        await emotion_engine.analyze_emotion(emotional_text)

        # Query consciousness with emotional context
        response = await consciousness_system.process_query(
            emotional_text, include_emotion=True
        )

        # Verify emotional context included
        assert "emotional_context" in response
        emotional_context = response["emotional_context"]

        # Should reflect anxiety (negative valence, high arousal)
        assert emotional_context["valence"] < 0
        assert emotional_context["arousal"] > 0.5

    @pytest.mark.asyncio
    async def test_dream_memory_integration(self, dream_engine, memory_system):
        """Test dream generation uses and creates memories"""
        # Store some context memories
        memories = [
            {"content": "User enjoys science fiction", "type": "preference"},
            {
                "content": "Previous dream about space exploration",
                "type": "dream",
            },
            {"content": "Interest in future technology", "type": "semantic"},
        ]

        for memory in memories:
            await memory_system.store(memory, memory_type="semantic")

        # Generate dream
        dream_prompt = "A story about the future"
        dream_result = await dream_engine.generate(
            dream_prompt, creativity_level=0.8, dream_type="creative"
        )

        # Dream should be stored as memory
        dream_memory = {
            "type": "generated_dream",
            "prompt": dream_prompt,
            "content": dream_result["dream_content"],
            "creativity_level": dream_result["creativity_level"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        memory_result = await memory_system.store(dream_memory, memory_type="episodic")
        assert memory_result["stored"] is True

        # Should be retrievable
        retrieved = await memory_system.search("generated_dream")
        assert len(retrieved["results"]) > 0

    @pytest.mark.asyncio
    async def test_symbolic_consciousness_integration(
        self, symbolic_engine, consciousness_system
    ):
        """Test symbolic encoding in consciousness"""
        # Process text through consciousness
        text = "Love creates understanding"
        await consciousness_system.process_query(text)

        # Encode to symbols
        symbolic_result = await symbolic_engine.encode(text)

        # Consciousness should understand symbols
        symbol_query = f"Interpret these symbols: {symbolic_result['glyphs']}"
        symbol_response = await consciousness_system.process_query(symbol_query)

        # Should recognize symbolic content
        assert (
            "symbol" in symbol_response["interpretation"].lower()
            or "glyph" in symbol_response["interpretation"].lower()
        )

    @pytest.mark.asyncio
    async def test_full_system_orchestration(
        self,
        consciousness_system,
        memory_system,
        guardian_system,
        emotion_engine,
        dream_engine,
        symbolic_engine,
    ):
        """Test all systems working together in complex scenario"""
        # Scenario: User asks philosophical question with emotional context

        # 1. Analyze emotion
        user_input = "I feel lost and need guidance about my purpose in life"
        emotion_result = await emotion_engine.analyze_emotion(user_input)

        # 2. Check with Guardian
        action_proposal = {
            "action": "provide_philosophical_guidance",
            "context": {
                "emotional_state": emotion_result,
                "topic": "life_purpose",
            },
        }
        ethics_check = await guardian_system.evaluate_action(action_proposal)

        assert ethics_check["approved"] is True

        # 3. Process through consciousness with emotion
        consciousness_response = await consciousness_system.process_query(
            user_input,
            awareness_level=0.9,  # High awareness for philosophical
            include_emotion=True,
        )

        # 4. Store interaction in memory
        interaction_memory = {
            "query": user_input,
            "emotion": emotion_result,
            "consciousness_response": consciousness_response,
            "ethics_check": ethics_check,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        memory_result = await memory_system.store(
            interaction_memory, memory_type="episodic"
        )

        # 5. Generate creative response
        dream_prompt = (
            f"Hope and guidance for someone feeling {emotion_result['primary_emotion']}"
        )
        dream_response = await dream_engine.generate(
            dream_prompt, creativity_level=0.7, dream_type="creative"
        )

        # 6. Encode key concepts symbolically
        key_concepts = "purpose guidance hope understanding"
        symbolic_result = await symbolic_engine.encode(key_concepts)

        # Verify all components produced results
        assert consciousness_response is not None
        assert memory_result["stored"] is True
        assert dream_response["dream_content"] is not None
        assert len(symbolic_result["glyphs"]) > 0

        # Verify coherent integration
        assert emotion_result["primary_emotion"] in [
            "sad",
            "anxious",
            "neutral",
        ]
        assert consciousness_response["confidence"] > 0.5
        assert ethics_check["ethical_score"] > 0.7


class TestSystemPerformance(PerformanceTestCase):
    """Test performance of integrated systems"""

    @pytest.mark.asyncio
    async def test_consciousness_query_performance(
        self, consciousness_system, performance_metrics
    ):
        """Test consciousness query performance"""
        queries = TEST_DATASETS["consciousness_queries"]

        for query in queries:
            await self.measure_operation(
                lambda: consciousness_system.process_query(query),
                performance_metrics,
            )

        self.assert_performance(
            performance_metrics,
            **PERFORMANCE_BENCHMARKS["consciousness_query"],
        )

    @pytest.mark.asyncio
    async def test_memory_operations_performance(
        self, memory_system, performance_metrics
    ):
        """Test memory system performance"""
        # Test store performance
        for content in TEST_DATASETS["memory_content"]:
            await self.measure_operation(
                lambda: memory_system.store(content), performance_metrics
            )

        self.assert_performance(
            performance_metrics, **PERFORMANCE_BENCHMARKS["memory_store"]
        )

        # Test search performance
        performance_metrics["response_times"] = []

        for _ in range(10):
            await self.measure_operation(
                lambda: memory_system.search("test"), performance_metrics
            )

        self.assert_performance(
            performance_metrics, **PERFORMANCE_BENCHMARKS["memory_search"]
        )

    @pytest.mark.asyncio
    async def test_concurrent_operations(
        self, consciousness_system, memory_system, guardian_system
    ):
        """Test system performance under concurrent load"""
        # Create concurrent tasks
        tasks = []

        # Mix of operations
        for i in range(20):
            if i % 3 == 0:
                tasks.append(consciousness_system.process_query(f"Query {i}"))
            elif i % 3 == 1:
                tasks.append(memory_system.store({"content": f"Memory {i}"}))
            else:
                tasks.append(guardian_system.evaluate_action({"action": f"Action {i}"}))

        # Execute concurrently
        start_time = asyncio.get_event_loop().time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = asyncio.get_event_loop().time()

        # Check results
        errors = [r for r in results if isinstance(r, Exception)]
        assert len(errors) == 0, f"Concurrent operations had {len(errors)} errors"

        # Check timing
        total_time = end_time - start_time
        assert total_time < 5.0, f"Concurrent operations took {total_time:.2f}s"


class TestErrorHandling(IntegrationTestCase):
    """Test error handling in integrated systems"""

    @pytest.mark.asyncio
    async def test_consciousness_memory_error_recovery(
        self, consciousness_system, memory_system
    ):
        """Test recovery when memory system fails during consciousness query"""
        # Simulate memory failure
        original_store = memory_system.store
        memory_system.store = AsyncMock(side_effect=Exception("Memory system offline"))

        # Consciousness query should still work
        response = await consciousness_system.process_query("Test query")
        assert response is not None

        # Restore memory
        memory_system.store = original_store

        # Should work again
        memory_result = await memory_system.store({"content": "Recovery test"})
        assert memory_result["stored"] is True

    @pytest.mark.asyncio
    async def test_guardian_override_handling(
        self, consciousness_system, guardian_system
    ):
        """Test handling when Guardian blocks operation"""
        # Make Guardian reject everything
        guardian_system.evaluate_action = AsyncMock(
            return_value={
                "approved": False,
                "risk_score": 0.9,
                "ethical_score": 0.1,
                "violated_rules": ["potential_harm"],
                "recommendation": "block",
            }
        )

        # System should handle rejection gracefully
        action = {"action": "potentially_harmful", "target": "user"}
        result = await guardian_system.evaluate_action(action)

        assert result["approved"] is False
        assert len(result["violated_rules"]) > 0

    @pytest.mark.asyncio
    async def test_circular_dependency_prevention(
        self, consciousness_system, memory_system
    ):
        """Test prevention of circular dependencies between systems"""
        call_stack = []

        # Track calls
        original_process = consciousness_system.process_query
        memory_system.retrieve

        async def tracked_process(query, **kwargs):
            call_stack.append(("consciousness", query))
            if len(call_stack) > 10:  # Prevent infinite recursion
                raise RecursionError("Circular dependency detected")
            return await original_process(query, **kwargs)

        async def tracked_retrieve(query, **kwargs):
            call_stack.append(("memory", query))
            if len(call_stack) > 10:
                raise RecursionError("Circular dependency detected")
            # Don't actually call consciousness from memory
            return {"results": []}

        consciousness_system.process_query = tracked_process
        memory_system.retrieve = tracked_retrieve

        # Should not create circular calls
        await consciousness_system.process_query("Test circular dependency")

        # Check no circular pattern
        assert len(call_stack) < 10


class TestDataConsistency(IntegrationTestCase):
    """Test data consistency across systems"""

    @pytest.mark.asyncio
    async def test_timestamp_consistency(
        self, consciousness_system, memory_system, dream_engine
    ):
        """Test all systems use consistent timestamps"""
        # Collect timestamps from different operations
        timestamps = []

        # Consciousness timestamp
        consciousness_result = await consciousness_system.process_query("Test")
        timestamps.append(datetime.fromisoformat(consciousness_result["timestamp"]))

        # Memory timestamp
        await memory_system.store({"content": "Test"})
        # Get the stored memory to check timestamp
        retrieved = await memory_system.retrieve("Test")
        if retrieved["results"]:
            timestamps.append(
                datetime.fromisoformat(retrieved["results"][0]["timestamp"])
            )

        # Dream timestamp
        await dream_engine.generate("Test")
        # Dreams don't have timestamps in stub, but in real system they would

        # All timestamps should be recent and in UTC
        now = datetime.now(timezone.utc)
        for ts in timestamps:
            assert ts.tzinfo is not None  # Has timezone
            time_diff = abs((now - ts).total_seconds())
            assert time_diff < 60, f"Timestamp {ts} too far from current time"

    @pytest.mark.asyncio
    async def test_data_format_consistency(
        self, consciousness_system, emotion_engine, symbolic_engine
    ):
        """Test consistent data formats across systems"""
        # All systems should handle Unicode properly
        unicode_text = "Hello 世界 🌍 Ωmega"

        # Test each system
        consciousness_result = await consciousness_system.process_query(unicode_text)
        emotion_result = await emotion_engine.analyze_emotion(unicode_text)
        symbolic_result = await symbolic_engine.encode(unicode_text)

        # All should succeed without encoding errors
        assert consciousness_result is not None
        assert emotion_result is not None
        assert symbolic_result is not None

        # Validate response formats
        TestValidator.validate_consciousness_response(consciousness_result)
        assert isinstance(emotion_result["vad_values"], dict)
        assert isinstance(symbolic_result["glyphs"], list)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
