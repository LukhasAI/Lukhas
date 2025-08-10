#!/usr/bin/env python3
"""
🔥 LUKHAS Memory System - Comprehensive Stress Tests
Tests system limits, performance, and reliability under extreme conditions
"""

import asyncio
import gc
import os
import random
import string
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

import numpy as np
import psutil

from memory.core import create_hybrid_memory_fold
from memory.systems.colony_swarm_integration import (
    ColonyRole,
    SwarmConsensusManager,
)
from memory.systems.integration_adapters import MemorySafetyIntegration
from memory.systems.memory_safety_features import (
    MemorySafetySystem,
    SafeMemoryFold,
)
from memory.systems.module_integrations import (
    CreativityModuleIntegration,
    LearningModuleIntegration,
    MetaModuleIntegration,
    VoiceModuleIntegration,
)


class MemoryStressTester:
    """Comprehensive stress testing for LUKHAS memory system"""

    def __init__(self):
        self.memory = None
        self.safety = None
        self.integration = None
        self.swarm = None
        self.modules = {}

        # Performance metrics
        self.metrics = {
            "memories_stored": 0,
            "memories_retrieved": 0,
            "consensus_validations": 0,
            "drift_calibrations": 0,
            "errors": [],
            "performance_samples": [],
        }

    async def setup(self):
        """Initialize all systems for stress testing"""
        print("🔧 Setting up stress test environment...")

        # Create systems with stress-test configuration
        self.memory = create_hybrid_memory_fold(
            embedding_dim=1024, enable_attention=True, enable_continuous_learning=True
        )

        self.safety = MemorySafetySystem(
            max_drift_threshold=0.5, quarantine_threshold=0.8, consensus_threshold=3
        )

        self.integration = MemorySafetyIntegration(self.safety, self.memory)

        # Register modules with aggressive thresholds
        await self.integration.register_module("learning", {"drift_threshold": 0.2})
        await self.integration.register_module("creativity", {"drift_threshold": 0.7})
        await self.integration.register_module("voice", {"drift_threshold": 0.4})
        await self.integration.register_module("meta", {"drift_threshold": 0.3})

        # Initialize module integrations
        self.modules = {
            "learning": LearningModuleIntegration(self.integration),
            "creativity": CreativityModuleIntegration(self.integration),
            "voice": VoiceModuleIntegration(self.integration),
            "meta": MetaModuleIntegration(self.integration),
        }

        # Set up swarm with many colonies
        self.swarm = SwarmConsensusManager(self.integration, min_colonies=5)

        # Register 10 colonies for stress testing
        for i in range(10):
            role = random.choice(list(ColonyRole))
            self.swarm.register_colony(f"colony_{i}", role)

        # Add reality anchors for stress testing
        for i in range(20):
            self.safety.add_reality_anchor(f"anchor_{i}", f"Truth statement {i}")

        print("✅ Stress test environment ready")

    def generate_random_memory(self, index: int) -> Dict[str, Any]:
        """Generate random memory for testing"""
        memory_types = [
            "knowledge",
            "experience",
            "observation",
            "creative",
            "technical",
        ]
        emotions = ["joy", "neutral", "curiosity", "excitement", "concern"]

        content_length = random.randint(10, 500)
        content = "".join(
            random.choices(string.ascii_letters + string.digits + " ", k=content_length)
        )

        return {
            "content": f"Memory {index}: {content}",
            "type": random.choice(memory_types),
            "emotion": random.choice(emotions),
            "importance": random.random(),
            "timestamp": datetime.now(timezone.utc)
            - timedelta(seconds=random.randint(0, 86400)),
            "metadata": {
                "source": f"stress_test_{index}",
                "random_field": random.random(),
                "nested": {
                    "level": random.randint(1, 10),
                    "data": [random.random() for _ in range(5)],
                },
            },
        }

    async def stress_test_storage(self, num_memories: int = 10000):
        """Test massive memory storage"""
        print(f"\n🔥 STRESS TEST 1: Storing {num_memories} memories...")

        start_time = time.time()
        errors = 0
        batch_size = 100

        for batch_start in range(0, num_memories, batch_size):
            batch_end = min(batch_start + batch_size, num_memories)
            batch_tasks = []

            for i in range(batch_start, batch_end):
                memory_data = self.generate_random_memory(i)
                tags = [
                    "stress_test",
                    f"batch_{batch_start // batch_size}",
                    memory_data["type"],
                    f"emotion:{memory_data['emotion']}",
                ]

                # Randomly use different storage methods
                if i % 3 == 0:
                    # Direct storage
                    task = self.memory.fold_in_with_embedding(
                        data=memory_data, tags=tags, text_content=memory_data["content"]
                    )
                elif i % 3 == 1:
                    # Safe storage with verification
                    safe_memory = SafeMemoryFold(self.memory, self.safety)
                    task = safe_memory.safe_fold_in(memory_data, tags)
                else:
                    # Consensus storage (if enough colonies)
                    if len(self.swarm.colonies) >= self.swarm.min_colonies:
                        task = self.swarm.distributed_memory_storage(
                            memory_data=memory_data,
                            tags=tags,
                            proposing_colony=f"colony_{i % 10}",
                        )
                    else:
                        task = self.memory.fold_in_with_embedding(
                            data=memory_data,
                            tags=tags,
                            text_content=memory_data["content"],
                        )

                batch_tasks.append(task)

            # Execute batch concurrently
            results = await asyncio.gather(*batch_tasks, return_exceptions=True)

            for result in results:
                if isinstance(result, Exception):
                    errors += 1
                    self.metrics["errors"].append(str(result))
                elif result is not None:
                    self.metrics["memories_stored"] += 1

            # Progress update
            if (batch_end % 1000) == 0:
                elapsed = time.time() - start_time
                rate = self.metrics["memories_stored"] / elapsed
                print(
                    f"  Progress: {batch_end}/{num_memories} - Rate: {rate:.1f} memories/sec"
                )

        end_time = time.time()
        duration = end_time - start_time

        print("\n📊 Storage Results:")
        print(f"  • Total attempted: {num_memories}")
        print(f"  • Successfully stored: {self.metrics['memories_stored']}")
        print(f"  • Errors: {errors}")
        print(f"  • Duration: {duration:.2f} seconds")
        print(
            f"  • Rate: {self.metrics['memories_stored'] / duration:.1f} memories/second"
        )

        # Memory usage
        process = psutil.Process(os.getpid())
        memory_mb = process.memory_info().rss / 1024 / 1024
        print(f"  • Memory usage: {memory_mb:.1f} MB")

    async def stress_test_retrieval(self, num_queries: int = 1000):
        """Test massive parallel retrieval"""
        print(f"\n🔥 STRESS TEST 2: Performing {num_queries} retrievals...")

        if self.metrics["memories_stored"] == 0:
            print("  ⚠️ No memories to retrieve, skipping test")
            return

        start_time = time.time()
        retrieval_times = []

        # Get all available tags
        all_tags = list(self.memory.tag_registry.values())
        if not all_tags:
            print("  ⚠️ No tags available, skipping test")
            return

        batch_size = 50
        for batch_start in range(0, num_queries, batch_size):
            batch_end = min(batch_start + batch_size, num_queries)
            batch_tasks = []

            for i in range(batch_start, batch_end):
                # Mix different query types
                query_type = i % 4

                if query_type == 0:
                    # Tag-based retrieval
                    tag = random.choice(all_tags).tag_name
                    task = self.memory.fold_out_by_tag(tag, max_items=10)

                elif query_type == 1:
                    # Semantic search
                    query = f"Random query {random.randint(1, 100)}"
                    task = self.memory.fold_out_semantic(query, top_k=10)

                elif query_type == 2:
                    # Multi-tag retrieval
                    tags = [random.choice(all_tags).tag_name for _ in range(2)]
                    task = self.memory.fold_out_by_tags(tags, max_items=10)

                else:
                    # Consensus query
                    query = f"Test query {i}"
                    task = self.swarm.query_with_consensus(
                        query=query,
                        requesting_colony=f"colony_{i % 10}",
                        min_confirmations=2,
                    )

                # Time individual queries
                query_start = time.time()
                batch_tasks.append((task, query_start))

            # Execute batch
            for task, query_start in batch_tasks:
                try:
                    result = await task
                    query_time = time.time() - query_start
                    retrieval_times.append(query_time)
                    self.metrics["memories_retrieved"] += len(result) if result else 0
                except Exception as e:
                    self.metrics["errors"].append(f"Retrieval error: {str(e)}")

        end_time = time.time()
        duration = end_time - start_time

        print("\n📊 Retrieval Results:")
        print(f"  • Total queries: {num_queries}")
        print(f"  • Memories retrieved: {self.metrics['memories_retrieved']}")
        print(f"  • Duration: {duration:.2f} seconds")
        print(f"  • Query rate: {num_queries / duration:.1f} queries/second")

        if retrieval_times:
            print(f"  • Avg query time: {np.mean(retrieval_times)*1000:.2f} ms")
            print(
                f"  • P95 query time: {np.percentile(retrieval_times, 95)*1000:.2f} ms"
            )
            print(
                f"  • P99 query time: {np.percentile(retrieval_times, 99)*1000:.2f} ms"
            )

    async def stress_test_drift(self, num_iterations: int = 1000):
        """Test drift detection under rapid changes"""
        print(
            f"\n🔥 STRESS TEST 3: Drift detection with {num_iterations} rapid changes..."
        )

        start_time = time.time()
        drift_scores = []
        calibrations = 0

        # Create rapidly drifting embeddings
        base_embedding = np.random.randn(1024).astype(np.float32)

        for i in range(num_iterations):
            # Add increasing drift
            drift_factor = i / num_iterations
            noise = np.random.randn(1024) * drift_factor * 0.5
            drifted_embedding = base_embedding + noise

            # Normalize
            drifted_embedding = drifted_embedding / (
                np.linalg.norm(drifted_embedding) + 1e-8
            )

            # Track drift for different modules
            module = random.choice(["learning", "creativity", "voice", "meta"])
            tag = f"drift_test_{module}"

            drift_result = await self.integration.drift.track_module_usage(
                module,
                tag,
                drifted_embedding,
                {"iteration": i, "drift_factor": drift_factor},
            )

            drift_scores.append(drift_result["drift_score"])

            if drift_result["needs_calibration"]:
                calibrations += 1
                self.metrics["drift_calibrations"] += 1

            # Progress update
            if i % 100 == 0 and i > 0:
                current_avg_drift = np.mean(drift_scores[-100:])
                print(f"  Iteration {i}: Avg drift = {current_avg_drift:.3f}")

        end_time = time.time()
        duration = end_time - start_time

        print("\n📊 Drift Test Results:")
        print(f"  • Iterations: {num_iterations}")
        print(f"  • Duration: {duration:.2f} seconds")
        print(f"  • Rate: {num_iterations / duration:.1f} iterations/second")
        print(f"  • Calibrations triggered: {calibrations}")
        print(f"  • Final avg drift: {np.mean(drift_scores):.3f}")
        print(f"  • Max drift: {max(drift_scores):.3f}")

    async def stress_test_consensus(self, num_validations: int = 500):
        """Test consensus validation under load"""
        print(
            f"\n🔥 STRESS TEST 4: Consensus validation with {num_validations} memories..."
        )

        start_time = time.time()
        consensus_reached = 0
        consensus_times = []

        for i in range(num_validations):
            memory_data = self.generate_random_memory(i)

            # Randomly corrupt some memories to test rejection
            if i % 10 == 0:
                memory_data["content"] = "This always contains never contradictions"

            consensus_start = time.time()

            mem_id = await self.swarm.distributed_memory_storage(
                memory_data=memory_data,
                tags=["consensus_test", f"batch_{i // 50}"],
                proposing_colony=f"colony_{i % 10}",
            )

            consensus_time = time.time() - consensus_start
            consensus_times.append(consensus_time)

            if mem_id is not None:
                consensus_reached += 1
                self.metrics["consensus_validations"] += 1

        end_time = time.time()
        duration = end_time - start_time

        print("\n📊 Consensus Results:")
        print(f"  • Total validations: {num_validations}")
        print(f"  • Consensus reached: {consensus_reached}")
        print(f"  • Success rate: {consensus_reached / num_validations * 100:.1f}%")
        print(f"  • Duration: {duration:.2f} seconds")
        print(f"  • Rate: {num_validations / duration:.1f} validations/second")

        if consensus_times:
            print(f"  • Avg consensus time: {np.mean(consensus_times)*1000:.2f} ms")
            print(
                f"  • P95 consensus time: {np.percentile(consensus_times, 95)*1000:.2f} ms"
            )

    async def stress_test_concurrent_operations(self, duration_seconds: int = 60):
        """Test system under mixed concurrent load"""
        print(
            f"\n🔥 STRESS TEST 5: Concurrent operations for {duration_seconds} seconds..."
        )

        start_time = time.time()
        end_time = start_time + duration_seconds

        operations = {
            "stores": 0,
            "retrievals": 0,
            "consensus": 0,
            "drift_tracks": 0,
            "pattern_extracts": 0,
        }

        async def store_worker():
            while time.time() < end_time:
                try:
                    memory = self.generate_random_memory(operations["stores"])
                    await self.memory.fold_in_with_embedding(
                        data=memory,
                        tags=["concurrent", memory["type"]],
                        text_content=memory["content"],
                    )
                    operations["stores"] += 1
                except Exception as e:
                    self.metrics["errors"].append(f"Store error: {str(e)}")
                await asyncio.sleep(0.001)

        async def retrieve_worker():
            while time.time() < end_time:
                try:
                    if operations["stores"] > 10:
                        results = await self.memory.fold_out_semantic(
                            f"Memory {random.randint(0, operations['stores'])}", top_k=5
                        )
                        operations["retrievals"] += 1
                except Exception as e:
                    self.metrics["errors"].append(f"Retrieve error: {str(e)}")
                await asyncio.sleep(0.01)

        async def consensus_worker():
            while time.time() < end_time:
                try:
                    memory = self.generate_random_memory(operations["consensus"])
                    result = await self.swarm.distributed_memory_storage(
                        memory_data=memory,
                        tags=["consensus"],
                        proposing_colony=f"colony_{operations['consensus'] % 10}",
                    )
                    if result:
                        operations["consensus"] += 1
                except Exception as e:
                    self.metrics["errors"].append(f"Consensus error: {str(e)}")
                await asyncio.sleep(0.05)

        async def drift_worker():
            while time.time() < end_time:
                try:
                    embedding = np.random.randn(1024).astype(np.float32)
                    await self.integration.drift.track_module_usage(
                        "learning", "concurrent_test", embedding, {"worker": "drift"}
                    )
                    operations["drift_tracks"] += 1
                except Exception as e:
                    self.metrics["errors"].append(f"Drift error: {str(e)}")
                await asyncio.sleep(0.02)

        async def pattern_worker():
            while time.time() < end_time:
                try:
                    if operations["stores"] > 100:
                        patterns = await self.modules["meta"].extract_verified_patterns(
                            min_occurrences=2
                        )
                        operations["pattern_extracts"] += 1
                except Exception as e:
                    self.metrics["errors"].append(f"Pattern error: {str(e)}")
                await asyncio.sleep(1.0)

        # Start all workers
        workers = [
            store_worker(),
            store_worker(),  # Multiple store workers
            store_worker(),
            retrieve_worker(),
            retrieve_worker(),
            consensus_worker(),
            drift_worker(),
            pattern_worker(),
        ]

        # Monitor progress
        async def monitor():
            while time.time() < end_time:
                await asyncio.sleep(5)
                elapsed = time.time() - start_time
                print(
                    f"  Progress ({elapsed:.0f}s): "
                    f"Stores={operations['stores']}, "
                    f"Retrievals={operations['retrievals']}, "
                    f"Consensus={operations['consensus']}"
                )

        # Run all workers concurrently
        await asyncio.gather(*workers, monitor(), return_exceptions=True)

        actual_duration = time.time() - start_time

        print("\n📊 Concurrent Operations Results:")
        print(f"  • Duration: {actual_duration:.1f} seconds")
        print(f"  • Total operations: {sum(operations.values())}")
        print(
            f"  • Operations/second: {sum(operations.values()) / actual_duration:.1f}"
        )
        print("  • Breakdown:")
        for op, count in operations.items():
            rate = count / actual_duration
            print(f"    - {op}: {count} ({rate:.1f}/sec)")
        print(
            f"  • Errors: {len([e for e in self.metrics['errors'] if 'Concurrent' in str(e)])}"
        )

    async def stress_test_memory_limits(self):
        """Test system behavior at memory limits"""
        print("\n🔥 STRESS TEST 6: Memory limits and cleanup...")

        initial_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024
        print(f"  Initial memory: {initial_memory:.1f} MB")

        # Store memories until we hit limits
        batch_size = 1000
        total_stored = 0
        memory_samples = []

        try:
            while True:
                # Check memory usage
                current_memory = (
                    psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024
                )
                memory_samples.append(current_memory)

                if current_memory > initial_memory + 500:  # 500MB increase limit
                    print(f"  Memory limit reached: {current_memory:.1f} MB")
                    break

                # Store batch
                print(f"  Storing batch (memory: {current_memory:.1f} MB)...")
                for i in range(batch_size):
                    memory = self.generate_random_memory(total_stored + i)
                    # Create large embedding to consume memory
                    large_embedding = np.random.randn(1024).astype(np.float32)

                    await self.memory.fold_in_with_embedding(
                        data=memory,
                        tags=["memory_test", f"batch_{total_stored // batch_size}"],
                        embedding=large_embedding,
                        text_content=memory["content"],
                    )

                total_stored += batch_size

                # Force garbage collection periodically
                if total_stored % 5000 == 0:
                    gc.collect()

        except Exception as e:
            print(f"  Hit limit with error: {str(e)}")

        final_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024

        print("\n📊 Memory Limit Results:")
        print(f"  • Memories stored: {total_stored}")
        print(f"  • Memory increase: {final_memory - initial_memory:.1f} MB")
        print(
            f"  • Bytes per memory: {(final_memory - initial_memory) * 1024 * 1024 / max(total_stored, 1):.0f}"
        )
        print(f"  • Peak memory: {max(memory_samples):.1f} MB")

        # Test cleanup
        print("\n  Testing memory cleanup...")

        # Clear caches
        self.memory.embedding_cache.clear()
        self.memory.items.clear()
        self.memory.tag_index.clear()
        gc.collect()

        cleaned_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024
        print(f"  • Memory after cleanup: {cleaned_memory:.1f} MB")
        print(f"  • Memory recovered: {final_memory - cleaned_memory:.1f} MB")

    async def run_all_stress_tests(self):
        """Run all stress tests in sequence"""
        print("🚀 STARTING COMPREHENSIVE STRESS TESTS")
        print("=" * 70)

        await self.setup()

        # Run tests with increasing intensity
        await self.stress_test_storage(num_memories=10000)
        await self.stress_test_retrieval(num_queries=1000)
        await self.stress_test_drift(num_iterations=1000)
        await self.stress_test_consensus(num_validations=500)
        await self.stress_test_concurrent_operations(duration_seconds=30)
        await self.stress_test_memory_limits()

        # Final report
        print("\n📊 FINAL STRESS TEST REPORT")
        print("=" * 70)

        print("Total operations:")
        print(f"  • Memories stored: {self.metrics['memories_stored']}")
        print(f"  • Memories retrieved: {self.metrics['memories_retrieved']}")
        print(f"  • Consensus validations: {self.metrics['consensus_validations']}")
        print(f"  • Drift calibrations: {self.metrics['drift_calibrations']}")
        print(f"  • Total errors: {len(self.metrics['errors'])}")

        if self.metrics["errors"]:
            print("\nError summary:")
            error_types = {}
            for error in self.metrics["errors"]:
                error_type = error.split(":")[0]
                error_types[error_type] = error_types.get(error_type, 0) + 1

            for error_type, count in sorted(
                error_types.items(), key=lambda x: x[1], reverse=True
            ):
                print(f"  • {error_type}: {count}")

        # System health check
        print("\nSystem health:")
        final_stats = self.memory.get_enhanced_statistics()
        safety_report = self.safety.get_safety_report()

        print(f"  • Total memories: {final_stats['total_items']}")
        print(f"  • Unique tags: {len(self.memory.tag_registry)}")
        print(f"  • Vector cache size: {final_stats['vector_stats']['cache_size']}")
        print(
            f"  • Average drift: {safety_report['drift_analysis']['average_drift']:.3f}"
        )
        print(
            f"  • Integrity score: {safety_report['verifold_status']['average_integrity']:.3f}"
        )

        print("\n✅ STRESS TESTS COMPLETE!")

        return self.metrics


async def main():
    """Run stress tests"""
    tester = MemoryStressTester()

    try:
        metrics = await tester.run_all_stress_tests()

        # Save metrics for analysis
        import json

        with open("stress_test_results.json", "w") as f:
            json.dump(
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "metrics": metrics,
                    "errors": metrics["errors"][:100],  # First 100 errors
                },
                f,
                indent=2,
            )

        print("\n📁 Results saved to stress_test_results.json")

    except Exception as e:
        print(f"\n❌ Stress test failed: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
