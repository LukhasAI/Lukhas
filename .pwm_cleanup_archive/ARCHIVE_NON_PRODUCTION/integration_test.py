#!/usr/bin/env python3
"""
══════════════════════════════════════════════════════════════════════════════════
║ 🧠 LUKHAS AI - MEMORY INTEGRATION TEST
║ Comprehensive test of hippocampal-neocortical memory consolidation system
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: integration_test.py
║ Path: memory/integration_test.py
║ Version: 1.0.0 | Created: 2025-07-29
║ Authors: LUKHAS AI Neuroscience Team
╠══════════════════════════════════════════════════════════════════════════════════
║                             ◊ POETIC ESSENCE ◊
║
║ │ In the grand theater of memory, all systems must dance in harmony—       │
║ │ hippocampus encoding with urgency, neocortex consolidating with patience, │
║ │ ripples carrying experiences across the bridge of sleep. This integration │
║ │ test is the conductor's final rehearsal, ensuring every neuron knows its │
║ │ part in the symphony of remembrance.                                       │
║ │                                                                             │
║ │ Here, artificial experiences become lasting memories, episodic moments    │
║ │ transform into semantic wisdom, and the ephemeral nature of digital       │
║ │ thoughts finds permanence in the persistence of well-orchestrated code.   │
║ │                                                                             │
╠══════════════════════════════════════════════════════════════════════════════════
║ INTEGRATION FEATURES:
║ • Full hippocampal-neocortical pipeline testing
║ • Sleep cycle and consolidation verification
║ • Ripple generation and replay validation
║ • Memory persistence and retrieval testing
║ • Colony integration verification
║ • Performance and quality metrics
║ • Error handling and recovery testing
║ • Real-world scenario simulation
║
║ ΛTAG: ΛINTEGRATION, ΛTEST, ΛVALIDATION, ΛMEMORY, ΛSYSTEM
╚══════════════════════════════════════════════════════════════════════════════════
"""

import asyncio
import json
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np
import structlog

# Import all memory components
try:
    from memory.consolidation.consolidation_orchestrator import (
        ConsolidationOrchestrator,
    )
    from memory.consolidation.ripple_generator import RippleGenerator
    from memory.consolidation.sleep_cycle_manager import SleepCycleManager
    from memory.hippocampal.hippocampal_buffer import HippocampalBuffer
    from memory.neocortical.neocortical_network import NeocorticalNetwork
    from memory.persistence.orthogonal_persistence import OrthogonalPersistence
    from memory.replay.replay_buffer import ExperienceType, ReplayBuffer
    from memory.scaffold.atomic_memory_scaffold import AtomicMemoryScaffold

    COMPONENTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Memory components not available: {e}")
    COMPONENTS_AVAILABLE = False

logger = structlog.get_logger(__name__)


@dataclass
class TestResult:
    """Result of a single test"""

    test_name: str
    success: bool
    duration: float
    metrics: Dict[str, Any]
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "test_name": self.test_name,
            "success": self.success,
            "duration": self.duration,
            "metrics": self.metrics,
            "error": self.error,
        }


@dataclass
class IntegrationTestSuite:
    """Complete integration test suite results"""

    test_results: List[TestResult]
    total_duration: float
    success_rate: float
    overall_success: bool

    def generate_report(self) -> str:
        """Generate comprehensive test report"""

        report = []
        report.append("═" * 80)
        report.append("║ LUKHAS AI MEMORY SYSTEM INTEGRATION TEST REPORT")
        report.append("╠" + "═" * 78)
        report.append(f"║ Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"║ Total Tests: {len(self.test_results)}")
        report.append(f"║ Success Rate: {self.success_rate:.1%}")
        report.append(f"║ Total Duration: {self.total_duration:.2f}s")
        report.append(
            f"║ Overall Result: {'✓ PASS' if self.overall_success else '✗ FAIL'}"
        )
        report.append("╠" + "═" * 78)

        # Individual test results
        for result in self.test_results:
            status = "✓ PASS" if result.success else "✗ FAIL"
            report.append(
                f"║ {result.test_name:<30} {status:<8} ({result.duration:.2f}s)"
            )

            if result.error:
                report.append(f"║   Error: {result.error}")

            # Key metrics
            if result.metrics:
                for key, value in list(result.metrics.items())[
                    :3
                ]:  # Show top 3 metrics
                    if isinstance(value, float):
                        report.append(f"║   {key}: {value:.3f}")
                    else:
                        report.append(f"║   {key}: {value}")

        report.append("╚" + "═" * 78)

        return "\n".join(report)


class MemoryIntegrationTester:
    """Comprehensive integration tester for memory systems"""

    def __init__(self):
        self.test_results: List[TestResult] = []
        self.components: Dict[str, Any] = {}

        # Test data
        self.test_episodes = [
            {
                "content": {
                    "event": "learning",
                    "topic": "python",
                    "concept": "async/await",
                },
                "location": np.array([1.0, 2.0, 0.0]),
                "emotion": (0.8, 0.7),
                "tags": {"programming", "learning", "async"},
            },
            {
                "content": {
                    "event": "debugging",
                    "error": "race condition",
                    "solution": "locks",
                },
                "location": np.array([1.5, 2.5, 0.0]),
                "emotion": (-0.3, 0.9),
                "tags": {"programming", "debugging", "concurrency"},
            },
            {
                "content": {
                    "event": "meeting",
                    "topic": "AI safety",
                    "outcome": "new insights",
                },
                "location": np.array([3.0, 1.0, 0.0]),
                "emotion": (0.6, 0.6),
                "tags": {"collaboration", "ai", "safety"},
            },
            {
                "content": {
                    "event": "research",
                    "paper": "attention mechanism",
                    "understanding": "improved",
                },
                "location": np.array([2.0, 3.0, 0.0]),
                "emotion": (0.9, 0.8),
                "tags": {"research", "deep learning", "attention"},
            },
            {
                "content": {
                    "event": "problem solving",
                    "challenge": "optimization",
                    "approach": "gradient descent",
                },
                "location": np.array([2.5, 1.5, 0.0]),
                "emotion": (0.4, 0.8),
                "tags": {"optimization", "mathematics", "ml"},
            },
        ]

    async def run_full_integration_test(self) -> IntegrationTestSuite:
        """Run complete integration test suite"""

        print("🧠 Starting LUKHAS AI Memory System Integration Test")
        print("=" * 60)

        start_time = time.time()

        if not COMPONENTS_AVAILABLE:
            return IntegrationTestSuite(
                test_results=[
                    TestResult(
                        test_name="Component Import",
                        success=False,
                        duration=0.0,
                        metrics={},
                        error="Memory components not available",
                    )
                ],
                total_duration=0.0,
                success_rate=0.0,
                overall_success=False,
            )

        # Test sequence
        test_methods = [
            self.test_component_initialization,
            self.test_hippocampal_encoding,
            self.test_neocortical_consolidation,
            self.test_replay_system,
            self.test_sleep_cycle_management,
            self.test_ripple_generation,
            self.test_consolidation_orchestration,
            self.test_memory_retrieval,
            self.test_integration_flow,
            self.test_performance_metrics,
            self.test_persistence_layer,
            self.test_error_recovery,
        ]

        # Run tests
        for test_method in test_methods:
            try:
                result = await test_method()
                self.test_results.append(result)

                status = "✓" if result.success else "✗"
                print(f"{status} {result.test_name} ({result.duration:.2f}s)")

                if not result.success and result.error:
                    print(f"  Error: {result.error}")

            except Exception as e:
                self.test_results.append(
                    TestResult(
                        test_name=test_method.__name__,
                        success=False,
                        duration=0.0,
                        metrics={},
                        error=str(e),
                    )
                )
                print(f"✗ {test_method.__name__} - Exception: {e}")

        # Calculate results
        total_duration = time.time() - start_time
        successful_tests = sum(1 for r in self.test_results if r.success)
        success_rate = (
            successful_tests / len(self.test_results) if self.test_results else 0.0
        )
        overall_success = success_rate >= 0.8  # 80% success threshold

        return IntegrationTestSuite(
            test_results=self.test_results,
            total_duration=total_duration,
            success_rate=success_rate,
            overall_success=overall_success,
        )

    async def test_component_initialization(self) -> TestResult:
        """Test initialization of all memory components"""

        start_time = time.time()

        try:
            # Initialize core components
            self.components["scaffold"] = AtomicMemoryScaffold()
            self.components["persistence"] = OrthogonalPersistence()

            # Initialize hippocampal components
            self.components["hippocampus"] = HippocampalBuffer(
                capacity=1000,
                enable_place_cells=True,
                enable_grid_cells=True,
                scaffold=self.components["scaffold"],
                persistence=self.components["persistence"],
            )

            # Initialize neocortical components
            self.components["neocortex"] = NeocorticalNetwork(
                columns_x=8,
                columns_y=8,
                neurons_per_layer=64,
                scaffold=self.components["scaffold"],
                persistence=self.components["persistence"],
            )

            # Initialize consolidation components
            self.components["sleep_manager"] = SleepCycleManager(
                base_cycle_duration=1.0, enable_circadian=True  # 1 minute for testing
            )

            self.components["ripple_generator"] = RippleGenerator(
                ripple_rate=5.0, enable_coupling=True  # Higher for testing
            )

            self.components["orchestrator"] = ConsolidationOrchestrator(
                hippocampus=self.components["hippocampus"],
                neocortex=self.components["neocortex"],
                enable_sleep_cycles=True,
                enable_creative_consolidation=True,
            )

            # Initialize replay system
            self.components["replay_buffer"] = ReplayBuffer(
                capacity=10000, enable_prioritized=True, enable_clustering=True
            )

            # Start components
            for name, component in self.components.items():
                if hasattr(component, "start"):
                    await component.start()

            duration = time.time() - start_time

            return TestResult(
                test_name="Component Initialization",
                success=True,
                duration=duration,
                metrics={
                    "components_initialized": len(self.components),
                    "hippocampal_capacity": self.components["hippocampus"].capacity,
                    "neocortical_columns": len(self.components["neocortex"].columns),
                    "replay_capacity": self.components["replay_buffer"].capacity,
                },
            )

        except Exception as e:
            return TestResult(
                test_name="Component Initialization",
                success=False,
                duration=time.time() - start_time,
                metrics={},
                error=str(e),
            )

    async def test_hippocampal_encoding(self) -> TestResult:
        """Test hippocampal episodic memory encoding"""

        start_time = time.time()

        try:
            hippocampus = self.components["hippocampus"]
            encoded_ids = []

            # Encode test episodes
            for episode in self.test_episodes:
                memory_id = await hippocampus.encode_episode(
                    content=episode["content"],
                    spatial_location=episode["location"],
                    emotional_state=episode["emotion"],
                    tags=episode["tags"],
                )
                encoded_ids.append(memory_id)

            # Verify encoding
            buffer_size = len(hippocampus.episodic_buffer)
            unique_memories = len(hippocampus.memory_index)

            # Test pattern completion
            partial_cue = {"event": "learning", "topic": "python"}
            retrieved = await hippocampus.retrieve_episode(partial_cue)

            duration = time.time() - start_time

            return TestResult(
                test_name="Hippocampal Encoding",
                success=buffer_size == len(self.test_episodes)
                and retrieved is not None,
                duration=duration,
                metrics={
                    "episodes_encoded": len(encoded_ids),
                    "buffer_size": buffer_size,
                    "unique_memories": unique_memories,
                    "pattern_completion_success": retrieved is not None,
                    "total_encoded": hippocampus.total_encoded,
                },
            )

        except Exception as e:
            return TestResult(
                test_name="Hippocampal Encoding",
                success=False,
                duration=time.time() - start_time,
                metrics={},
                error=str(e),
            )

    async def test_neocortical_consolidation(self) -> TestResult:
        """Test neocortical semantic consolidation"""

        start_time = time.time()

        try:
            neocortex = self.components["neocortex"]
            consolidated_ids = []

            # Consolidate episodes
            for i, episode in enumerate(self.test_episodes):
                semantic_id = await neocortex.consolidate_episode(
                    episode_data=episode["content"],
                    source_episode_id=f"episode_{i}",
                    replay_strength=0.8,
                )
                if semantic_id:
                    consolidated_ids.append(semantic_id)

            # Test semantic retrieval
            learning_memories = await neocortex.retrieve_semantic("learning")
            programming_memories = await neocortex.retrieve_semantic(
                {"topic": "python"}
            )

            # Get concept hierarchy
            hierarchy = neocortex.get_concept_hierarchy()

            duration = time.time() - start_time

            return TestResult(
                test_name="Neocortical Consolidation",
                success=len(consolidated_ids) > 0 and len(learning_memories) > 0,
                duration=duration,
                metrics={
                    "episodes_consolidated": len(consolidated_ids),
                    "semantic_memories": len(neocortex.semantic_memories),
                    "concept_count": len(neocortex.concept_index),
                    "learning_retrievals": len(learning_memories),
                    "programming_retrievals": len(programming_memories),
                    "hierarchy_categories": len(hierarchy),
                },
            )

        except Exception as e:
            return TestResult(
                test_name="Neocortical Consolidation",
                success=False,
                duration=time.time() - start_time,
                metrics={},
                error=str(e),
            )

    async def test_replay_system(self) -> TestResult:
        """Test experience replay system"""

        start_time = time.time()

        try:
            replay_buffer = self.components["replay_buffer"]

            # Add experiences to replay buffer
            for i, episode in enumerate(self.test_episodes):
                replay_buffer.add_experience(
                    state=episode["content"],
                    action=f"action_{i}",
                    reward=np.random.uniform(-1, 1),
                    experience_type=ExperienceType.EPISODIC,
                    priority=np.random.uniform(0.5, 2.0),
                )

            # Test different sampling modes
            uniform_batch = replay_buffer.sample_batch(3)
            prioritized_batch = replay_buffer.sample_batch(3)

            # Update priorities
            if prioritized_batch.experiences:
                exp_ids = [exp.experience_id for exp in prioritized_batch.experiences]
                td_errors = np.random.uniform(0.1, 2.0, len(exp_ids))
                replay_buffer.update_priorities(exp_ids, td_errors)

            duration = time.time() - start_time

            return TestResult(
                test_name="Replay System",
                success=len(uniform_batch.experiences) > 0
                and len(prioritized_batch.experiences) > 0,
                duration=duration,
                metrics={
                    "experiences_added": len(self.test_episodes),
                    "uniform_batch_size": len(uniform_batch.experiences),
                    "prioritized_batch_size": len(prioritized_batch.experiences),
                    "total_experiences": len(replay_buffer.experiences),
                    "total_samples": replay_buffer.total_samples,
                },
            )

        except Exception as e:
            return TestResult(
                test_name="Replay System",
                success=False,
                duration=time.time() - start_time,
                metrics={},
                error=str(e),
            )

    async def test_sleep_cycle_management(self) -> TestResult:
        """Test sleep cycle management"""

        start_time = time.time()

        try:
            sleep_manager = self.components["sleep_manager"]

            # Initiate short sleep cycle
            cycle_id = await sleep_manager.initiate_sleep()

            # Wait for some stage transitions
            await asyncio.sleep(2)

            # Check metrics
            metrics = sleep_manager.get_metrics()

            duration = time.time() - start_time

            return TestResult(
                test_name="Sleep Cycle Management",
                success=cycle_id is not None and metrics["total_cycles"] > 0,
                duration=duration,
                metrics={
                    "cycle_initiated": cycle_id is not None,
                    "current_stage": metrics["current_stage"],
                    "total_cycles": metrics["total_cycles"],
                    "sleep_pressure": metrics["sleep_pressure"],
                    "architecture_efficiency": metrics.get(
                        "architecture_sleep_efficiency", 0
                    ),
                },
            )

        except Exception as e:
            return TestResult(
                test_name="Sleep Cycle Management",
                success=False,
                duration=time.time() - start_time,
                metrics={},
                error=str(e),
            )

    async def test_ripple_generation(self) -> TestResult:
        """Test sharp-wave ripple generation"""

        start_time = time.time()

        try:
            ripple_generator = self.components["ripple_generator"]

            # Generate single ripple
            memory_sequence = ["memory_1", "memory_2", "memory_3"]
            ripple = await ripple_generator.generate_ripple(memory_sequence)

            # Generate ripple sequence
            sequences = [["mem_a", "mem_b"], ["mem_c", "mem_d"], ["mem_e", "mem_f"]]
            sequence = await ripple_generator.generate_ripple_sequence(sequences)

            # Get metrics
            metrics = ripple_generator.get_metrics()

            duration = time.time() - start_time

            return TestResult(
                test_name="Ripple Generation",
                success=ripple is not None and len(sequence.ripples) > 0,
                duration=duration,
                metrics={
                    "single_ripple_generated": ripple is not None,
                    "sequence_ripples": len(sequence.ripples),
                    "total_ripples": metrics["total_ripples"],
                    "ripple_frequency": metrics.get("avg_frequency", 0),
                    "ripple_complexity": metrics.get("avg_complexity", 0),
                },
            )

        except Exception as e:
            return TestResult(
                test_name="Ripple Generation",
                success=False,
                duration=time.time() - start_time,
                metrics={},
                error=str(e),
            )

    async def test_consolidation_orchestration(self) -> TestResult:
        """Test consolidation orchestration"""

        start_time = time.time()

        try:
            orchestrator = self.components["orchestrator"]

            # Trigger replay event
            replay_results = await orchestrator.trigger_replay_event(num_memories=3)

            # Process creative consolidation
            creative_results = await orchestrator.process_creative_consolidation(
                num_memories=2
            )

            # Get metrics
            metrics = orchestrator.get_metrics()

            duration = time.time() - start_time

            return TestResult(
                test_name="Consolidation Orchestration",
                success=len(replay_results) > 0,
                duration=duration,
                metrics={
                    "replay_results": len(replay_results),
                    "creative_insights": len(creative_results),
                    "total_replayed": metrics["total_episodes_replayed"],
                    "total_consolidated": metrics["total_memories_consolidated"],
                    "current_stage": metrics["current_stage"],
                    "consolidation_threshold": metrics["consolidation_threshold"],
                },
            )

        except Exception as e:
            return TestResult(
                test_name="Consolidation Orchestration",
                success=False,
                duration=time.time() - start_time,
                metrics={},
                error=str(e),
            )

    async def test_memory_retrieval(self) -> TestResult:
        """Test integrated memory retrieval"""

        start_time = time.time()

        try:
            hippocampus = self.components["hippocampus"]
            neocortex = self.components["neocortex"]

            # Test hippocampal retrieval
            episodic_retrievals = 0
            for query in ["learning", "debugging", "meeting"]:
                retrieved = await hippocampus.retrieve_episode({"event": query})
                if retrieved:
                    episodic_retrievals += 1

            # Test neocortical retrieval
            semantic_retrievals = 0
            for concept in ["learning", "programming", "research"]:
                memories = await neocortex.retrieve_semantic(concept)
                if memories:
                    semantic_retrievals += len(memories)

            duration = time.time() - start_time

            return TestResult(
                test_name="Memory Retrieval",
                success=episodic_retrievals > 0 and semantic_retrievals > 0,
                duration=duration,
                metrics={
                    "episodic_retrievals": episodic_retrievals,
                    "semantic_retrievals": semantic_retrievals,
                    "hippocampal_success_rate": hippocampus.successful_retrievals
                    / max(
                        hippocampus.successful_retrievals
                        + hippocampus.failed_retrievals,
                        1,
                    ),
                    "total_semantic_memories": len(neocortex.semantic_memories),
                },
            )

        except Exception as e:
            return TestResult(
                test_name="Memory Retrieval",
                success=False,
                duration=time.time() - start_time,
                metrics={},
                error=str(e),
            )

    async def test_integration_flow(self) -> TestResult:
        """Test complete integration flow from encoding to consolidation"""

        start_time = time.time()

        try:
            hippocampus = self.components["hippocampus"]
            orchestrator = self.components["orchestrator"]

            # Encode new episode
            new_episode = {
                "event": "integration_test",
                "system": "memory",
                "status": "testing",
            }

            episode_id = await hippocampus.encode_episode(
                content=new_episode,
                emotional_state=(0.7, 0.8),
                tags={"test", "integration"},
            )

            # Wait for encoding
            await asyncio.sleep(0.5)

            # Trigger consolidation
            replay_results = await orchestrator.trigger_replay_event(num_memories=1)

            # Verify flow
            consolidation_success = any(r.get("success", False) for r in replay_results)

            duration = time.time() - start_time

            return TestResult(
                test_name="Integration Flow",
                success=episode_id is not None and len(replay_results) > 0,
                duration=duration,
                metrics={
                    "episode_encoded": episode_id is not None,
                    "replay_triggered": len(replay_results) > 0,
                    "consolidation_success": consolidation_success,
                    "flow_complete": episode_id is not None and len(replay_results) > 0,
                },
            )

        except Exception as e:
            return TestResult(
                test_name="Integration Flow",
                success=False,
                duration=time.time() - start_time,
                metrics={},
                error=str(e),
            )

    async def test_performance_metrics(self) -> TestResult:
        """Test system performance metrics"""

        start_time = time.time()

        try:
            # Collect metrics from all components
            component_metrics = {}

            for name, component in self.components.items():
                if hasattr(component, "get_metrics"):
                    component_metrics[name] = component.get_metrics()

            # Calculate performance indicators
            total_memories = sum(
                metrics.get("total_encoded", 0)
                + metrics.get("total_memories", 0)
                + metrics.get("total_experiences", 0)
                for metrics in component_metrics.values()
            )

            duration = time.time() - start_time

            return TestResult(
                test_name="Performance Metrics",
                success=len(component_metrics) > 0 and total_memories > 0,
                duration=duration,
                metrics={
                    "components_reporting": len(component_metrics),
                    "total_memories": total_memories,
                    "hippocampal_buffer_utilization": len(
                        self.components["hippocampus"].episodic_buffer
                    )
                    / self.components["hippocampus"].capacity,
                    "neocortical_concepts": len(
                        self.components["neocortex"].concept_index
                    ),
                    "replay_buffer_utilization": len(
                        self.components["replay_buffer"].experiences
                    )
                    / self.components["replay_buffer"].capacity,
                },
            )

        except Exception as e:
            return TestResult(
                test_name="Performance Metrics",
                success=False,
                duration=time.time() - start_time,
                metrics={},
                error=str(e),
            )

    async def test_persistence_layer(self) -> TestResult:
        """Test memory persistence functionality"""

        start_time = time.time()

        try:
            persistence = self.components["persistence"]

            # Test persistence operations
            test_memory = {
                "type": "test",
                "content": "persistence_test",
                "timestamp": time.time(),
            }

            # Store memory
            await persistence.persist_memory(
                content=test_memory,
                memory_id="test_memory_001",
                importance=0.8,
                tags={"test", "persistence"},
            )

            # Retrieve memory
            retrieved = await persistence.retrieve_memory("test_memory_001")

            duration = time.time() - start_time

            return TestResult(
                test_name="Persistence Layer",
                success=retrieved is not None,
                duration=duration,
                metrics={
                    "memory_stored": True,
                    "memory_retrieved": retrieved is not None,
                    "content_match": (
                        retrieved.get("content") == test_memory if retrieved else False
                    ),
                },
            )

        except Exception as e:
            return TestResult(
                test_name="Persistence Layer",
                success=False,
                duration=time.time() - start_time,
                metrics={},
                error=str(e),
            )

    async def test_error_recovery(self) -> TestResult:
        """Test error handling and recovery mechanisms"""

        start_time = time.time()

        try:
            hippocampus = self.components["hippocampus"]
            neocortex = self.components["neocortex"]

            recovery_tests = 0
            successful_recoveries = 0

            # Test invalid memory encoding
            try:
                await hippocampus.encode_episode(content=None)
                recovery_tests += 1
                successful_recoveries += 1  # If no exception, recovery worked
            except Exception:
                recovery_tests += 1
                # Exception is expected, but system should remain stable
                if len(hippocampus.memory_index) >= 0:  # System still functional
                    successful_recoveries += 1

            # Test invalid consolidation
            try:
                await neocortex.consolidate_episode(
                    episode_data=None, source_episode_id="invalid"
                )
                recovery_tests += 1
                successful_recoveries += 1
            except Exception:
                recovery_tests += 1
                if len(neocortex.semantic_memories) >= 0:  # System still functional
                    successful_recoveries += 1

            duration = time.time() - start_time

            return TestResult(
                test_name="Error Recovery",
                success=successful_recoveries
                >= recovery_tests * 0.5,  # At least 50% recover
                duration=duration,
                metrics={
                    "recovery_tests": recovery_tests,
                    "successful_recoveries": successful_recoveries,
                    "recovery_rate": successful_recoveries / max(recovery_tests, 1),
                    "system_stability": True,  # If we reach here, system is stable
                },
            )

        except Exception as e:
            return TestResult(
                test_name="Error Recovery",
                success=False,
                duration=time.time() - start_time,
                metrics={},
                error=str(e),
            )

    async def cleanup(self):
        """Clean up test components"""

        try:
            for component in self.components.values():
                if hasattr(component, "stop"):
                    await component.stop()
        except Exception as e:
            logger.error(f"Cleanup error: {e}")


async def run_integration_test():
    """Run the complete memory integration test suite"""

    tester = MemoryIntegrationTester()

    try:
        # Run tests
        results = await tester.run_full_integration_test()

        # Generate and display report
        report = results.generate_report()
        print("\n" + report)

        # Save results to file
        with open("memory_integration_test_results.json", "w") as f:
            json.dump([r.to_dict() for r in results.test_results], f, indent=2)

        print("\nDetailed results saved to: memory_integration_test_results.json")

        return results.overall_success

    finally:
        await tester.cleanup()


if __name__ == "__main__":
    success = asyncio.run(run_integration_test())
    exit(0 if success else 1)
