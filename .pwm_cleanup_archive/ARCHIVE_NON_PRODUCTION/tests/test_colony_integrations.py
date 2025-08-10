"""
Comprehensive test suite for colony integrations
Tests consciousness, memory, and quantum colony integrations
"""

import asyncio
import logging
from datetime import datetime

import pytest

# Import all integration modules
from consciousness.systems.consciousness_colony_integration import (
    DistributedConsciousnessEngine,
)
from memory.systems.distributed_memory import (
    DistributedMemorySystem,
    MemoryType,
)
from quantum.quantum_colony import QuantumColony

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestColonyIntegrations:
    """Test suite for colony integration implementations."""

    @pytest.mark.asyncio
    async def test_consciousness_colony_integration(self):
        """Test distributed consciousness processing through colonies."""
        engine = DistributedConsciousnessEngine(user_id_context="test_consciousness")

        await engine.start()

        try:
            # Test reflection processing
            experience = {
                "type": "test_experience",
                "content": "Testing distributed consciousness",
                "emotional_context": {"curiosity": 0.8},
                "timestamp": datetime.now().isoformat(),
            }

            reflection_result = await engine.perform_distributed_reflection(experience)

            assert reflection_result is not None
            assert "distributed" in reflection_result
            assert reflection_result["distributed"] is True
            assert "reasoning_analysis" in reflection_result
            assert "memory_context" in reflection_result
            assert "creative_insights" in reflection_result

            # Test awareness processing
            awareness_data = {
                "stimuli": [
                    {"type": "visual", "intensity": 0.7},
                    {"type": "auditory", "intensity": 0.5},
                ],
                "mode": "focused",
            }

            awareness_result = await engine.process_consciousness_task(
                "awareness", awareness_data
            )

            assert awareness_result is not None
            assert "consensus_awareness" in awareness_result
            assert 0 <= awareness_result["consensus_awareness"] <= 1

            # Check colony status
            status = await engine.get_colony_status()

            assert status["engine_running"] is True
            assert "reasoning" in status["colonies"]
            assert "memory" in status["colonies"]
            assert "creativity" in status["colonies"]
            assert status["total_distributed_tasks"] > 0

            logger.info(
                f"Consciousness colony test passed. Tasks: {status['total_distributed_tasks']}"
            )

        finally:
            await engine.stop()

    @pytest.mark.asyncio
    async def test_distributed_memory_system(self):
        """Test distributed memory storage and retrieval."""
        memory_system = DistributedMemorySystem("test-memory")

        await memory_system.initialize()

        try:
            # Store different types of memories
            memories_stored = []

            # Episodic memory
            episodic_id = await memory_system.store_memory(
                content={
                    "event": "test_event",
                    "details": "Testing distributed memory",
                    "timestamp": datetime.now().isoformat(),
                },
                memory_type=MemoryType.EPISODIC,
                importance=0.8,
                tags=["test", "episodic"],
            )
            memories_stored.append(episodic_id)

            # Semantic memory
            semantic_id = await memory_system.store_memory(
                content={
                    "concept": "distributed_systems",
                    "definition": "Systems that operate across multiple nodes",
                    "properties": ["scalable", "fault-tolerant"],
                },
                memory_type=MemoryType.SEMANTIC,
                importance=0.9,
                tags=["test", "semantic", "technical"],
            )
            memories_stored.append(semantic_id)

            # Procedural memory
            procedural_id = await memory_system.store_memory(
                content={
                    "skill": "memory_storage",
                    "steps": ["generate_id", "create_object", "store_in_colony"],
                    "complexity": "medium",
                },
                memory_type=MemoryType.PROCEDURAL,
                importance=0.7,
                tags=["test", "procedural"],
            )
            memories_stored.append(procedural_id)

            # Test retrieval
            for memory_id in memories_stored:
                retrieved = await memory_system.retrieve_memory(memory_id)
                assert retrieved is not None
                assert retrieved.memory_id == memory_id
                assert retrieved.access_count == 1

            # Test search
            search_results = await memory_system.search_memories(
                query={"text": "distributed test"}, limit=5
            )

            assert len(search_results) > 0

            # Test statistics
            stats = await memory_system.get_memory_statistics()

            assert stats["total_memories"] >= 3
            assert stats["by_type"][MemoryType.EPISODIC.value] >= 1
            assert stats["by_type"][MemoryType.SEMANTIC.value] >= 1
            assert stats["by_type"][MemoryType.PROCEDURAL.value] >= 1

            logger.info(
                f"Memory system test passed. Total memories: {stats['total_memories']}"
            )

        finally:
            await memory_system.shutdown()

    @pytest.mark.asyncio
    async def test_quantum_colony_operations(self):
        """Test quantum-inspired colony operations."""
        colony = QuantumColony("test-quantum")

        await colony.start()

        try:
            # Create entangled agents
            entangled_agents = await colony.create_entangled_agents(4)
            assert len(entangled_agents) == 4

            # Test Grover's search
            def oracle(x):
                return x == 15  # Search for 15

            search_result = await colony.execute_quantum_algorithm(
                "grover_search", {"search_space": list(range(20)), "oracle": oracle}
            )

            assert search_result["algorithm"] == "grover_search"
            assert search_result["found_item"] == 15
            assert search_result["probability"] > 0.5

            # Test quantum annealing
            def simple_cost(state):
                x = state.get("x", 0)
                return (x - 5) ** 2  # Minimum at x=5

            annealing_result = await colony.execute_quantum_algorithm(
                "quantum_annealing",
                {
                    "cost_function": simple_cost,
                    "initial_state": {"x": 0},
                    "temperature": [10, 1, 0.1],
                },
            )

            assert annealing_result["algorithm"] == "quantum_annealing"
            assert (
                abs(annealing_result["best_state"]["x"] - 5) < 1.0
            )  # Close to optimal

            # Test entanglement measurement
            entanglement = await colony.measure_entanglement()
            assert len(entanglement) > 0

            for agent_id, strength in entanglement.items():
                assert 0 <= strength <= 1

            # Test coherence maintenance
            await colony.maintain_coherence()

            logger.info(
                f"Quantum colony test passed. Entangled agents: {len(entangled_agents)}"
            )

        finally:
            await colony.stop()

    @pytest.mark.asyncio
    async def test_integrated_consciousness_memory_quantum(self):
        """Test all three systems working together."""
        # Initialize all systems
        consciousness = DistributedConsciousnessEngine("integrated-test")
        memory = DistributedMemorySystem("integrated-memory")
        quantum = QuantumColony("integrated-quantum")

        # Shared event bus for inter-system communication
        event_bus = EventBus()

        await consciousness.start()
        await memory.initialize()
        await quantum.start()

        try:
            # Create a complex experience that uses all systems
            complex_experience = {
                "type": "quantum_consciousness_test",
                "content": "Testing integrated colony systems",
                "quantum_state": {"superposition": True, "entangled": True},
                "requires_memory": True,
                "requires_creativity": True,
                "timestamp": datetime.now().isoformat(),
            }

            # Process through consciousness system
            consciousness_result = await consciousness.perform_distributed_reflection(
                complex_experience
            )

            # Store result in memory system
            memory_id = await memory.store_memory(
                content={
                    "experience": complex_experience,
                    "consciousness_result": consciousness_result,
                },
                memory_type=MemoryType.EPISODIC,
                importance=0.9,
                tags=["integrated", "quantum", "consciousness"],
            )

            # Use quantum colony to analyze the consciousness pattern
            quantum_analysis = await quantum.execute_quantum_algorithm(
                "grover_search",
                {
                    "search_space": [
                        {"pattern": "coherent", "value": 1},
                        {"pattern": "entangled", "value": 2},
                        {"pattern": "superposed", "value": 3},
                        {"pattern": "collapsed", "value": 4},
                    ],
                    "oracle": lambda x: x["value"] == 2,  # Looking for entangled
                },
            )

            # Verify integration results
            assert consciousness_result["distributed"] is True
            assert memory_id is not None
            assert quantum_analysis["found_item"]["pattern"] == "entangled"

            # Store quantum analysis in memory
            quantum_memory_id = await memory.store_memory(
                content={
                    "quantum_analysis": quantum_analysis,
                    "related_consciousness": consciousness_result["task_id"],
                },
                memory_type=MemoryType.SEMANTIC,
                importance=0.85,
                tags=["quantum_analysis", "integrated"],
            )

            # Search for integrated memories
            integrated_memories = await memory.search_memories(
                query={"text": "integrated quantum consciousness"}, limit=10
            )

            assert len(integrated_memories) >= 2  # At least our two stored memories

            # Get final statistics
            consciousness_status = await consciousness.get_colony_status()
            memory_stats = await memory.get_memory_statistics()
            quantum_entanglement = await quantum.measure_entanglement()

            logger.info(
                f"""
            Integrated test completed successfully:
            - Consciousness tasks: {consciousness_status['total_distributed_tasks']}
            - Memories stored: {memory_stats['total_memories']}
            - Quantum agents entangled: {len(quantum_entanglement)}
            """
            )

        finally:
            await consciousness.stop()
            await memory.shutdown()
            await quantum.stop()

    @pytest.mark.asyncio
    async def test_colony_fault_tolerance(self):
        """Test fault tolerance across integrated colonies."""
        consciousness = DistributedConsciousnessEngine("fault-test")

        await consciousness.start()

        try:
            # Simulate multiple tasks with some failures
            tasks = []
            for i in range(10):
                experience = {
                    "type": "fault_test",
                    "id": i,
                    "fail_probability": 0.3 if i % 3 == 0 else 0.0,
                }

                task = consciousness.process_consciousness_task(
                    "reflection" if i % 2 == 0 else "awareness",
                    {"experience": experience},
                )
                tasks.append(task)

            # Execute all tasks
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Count successes and failures
            successes = sum(1 for r in results if not isinstance(r, Exception))
            failures = sum(1 for r in results if isinstance(r, Exception))

            # Check colony health after stress test
            status = await consciousness.get_colony_status()
            avg_success_rate = status["average_success_rate"]

            assert successes > failures  # Most should succeed
            assert avg_success_rate > 0.5  # System should remain healthy

            logger.info(
                f"Fault tolerance test: {successes} successes, {failures} failures"
            )

        finally:
            await consciousness.stop()


# Integration test runner
async def run_all_integration_tests():
    """Run all colony integration tests."""
    test_suite = TestColonyIntegrations()

    tests = [
        (
            "Consciousness Colony Integration",
            test_suite.test_consciousness_colony_integration,
        ),
        ("Distributed Memory System", test_suite.test_distributed_memory_system),
        ("Quantum Colony Operations", test_suite.test_quantum_colony_operations),
        ("Integrated Systems", test_suite.test_integrated_consciousness_memory_quantum),
        ("Fault Tolerance", test_suite.test_colony_fault_tolerance),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            logger.info(f"\n{'='*60}")
            logger.info(f"Running: {test_name}")
            logger.info(f"{'='*60}")

            await test_func()

            results.append((test_name, "PASSED"))
            logger.info(f"✓ {test_name} PASSED")

        except Exception as e:
            results.append((test_name, f"FAILED: {e}"))
            logger.error(f"✗ {test_name} FAILED: {e}")

    # Summary
    logger.info(f"\n{'='*60}")
    logger.info("INTEGRATION TEST SUMMARY")
    logger.info(f"{'='*60}")

    passed = sum(1 for _, result in results if result == "PASSED")
    total = len(results)

    for test_name, result in results:
        status = "✓" if result == "PASSED" else "✗"
        logger.info(f"{status} {test_name}: {result}")

    logger.info(f"\nTotal: {passed}/{total} tests passed")

    return passed == total


if __name__ == "__main__":
    success = asyncio.run(run_all_integration_tests())
    exit(0 if success else 1)
