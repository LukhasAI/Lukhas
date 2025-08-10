#!/usr/bin/env python3
"""
🔥 LUKHAS Memory System - Light Stress Tests (Optimized for completion)
"""

import asyncio
import os
import random
import string
import time
from datetime import datetime, timezone

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


async def run_light_stress_tests():
    """Run lighter stress tests that complete quickly"""

    print("🔥 LUKHAS MEMORY SYSTEM - LIGHT STRESS TESTS")
    print("=" * 60)

    # Initialize systems
    print("\n🔧 Setting up test environment...")
    memory = create_hybrid_memory_fold()
    safety = MemorySafetySystem()
    integration = MemorySafetyIntegration(safety, memory)

    # Register modules
    await integration.register_module("learning", {"drift_threshold": 0.3})
    await integration.register_module("creativity", {"drift_threshold": 0.6})

    # Set up minimal swarm
    swarm = SwarmConsensusManager(integration, min_colonies=3)
    swarm.register_colony("validator", ColonyRole.VALIDATOR)
    swarm.register_colony("witness", ColonyRole.WITNESS)
    swarm.register_colony("arbiter", ColonyRole.ARBITER)

    print("✅ Environment ready")

    # Track metrics
    metrics = {"test_results": {}, "performance": {}, "errors": []}

    # TEST 1: Rapid Storage
    print("\n1️⃣ RAPID STORAGE TEST (1000 memories)...")
    start_time = time.time()

    for i in range(1000):
        memory = {
            "content": f"Memory {i}: {''.join(random.choices(string.ascii_letters, k=50))}",
            "type": random.choice(["knowledge", "experience", "observation"]),
            "timestamp": datetime.now(timezone.utc),
        }

        try:
            if i % 3 == 0:
                # Direct storage
                await memory.fold_in_with_embedding(
                    data=memory,
                    tags=["stress", f"batch_{i//100}"],
                    text_content=memory["content"],
                )
            else:
                # Safe storage
                safe_memory = SafeMemoryFold(memory, safety)
                await safe_memory.safe_fold_in(memory, ["stress", memory["type"]])

        except Exception as e:
            metrics["errors"].append(f"Storage error: {str(e)}")

    storage_time = time.time() - start_time
    storage_rate = 1000 / storage_time

    print(f"  ✓ Storage rate: {storage_rate:.1f} memories/second")
    print(f"  ✓ Time taken: {storage_time:.2f} seconds")

    metrics["test_results"]["storage"] = {
        "total": 1000,
        "rate": storage_rate,
        "duration": storage_time,
    }

    # TEST 2: Parallel Retrieval
    print("\n2️⃣ PARALLEL RETRIEVAL TEST (100 queries)...")
    start_time = time.time()

    async def query_worker(query_id: int):
        query = f"Memory {random.randint(0, 999)}"
        results = await memory.fold_out_semantic(query, top_k=5)
        return len(results)

    # Run 100 queries in parallel
    query_tasks = [query_worker(i) for i in range(100)]
    results = await asyncio.gather(*query_tasks, return_exceptions=True)

    retrieval_time = time.time() - start_time
    successful_queries = sum(1 for r in results if isinstance(r, int))
    total_retrieved = sum(r for r in results if isinstance(r, int))

    print(f"  ✓ Query rate: {100 / retrieval_time:.1f} queries/second")
    print(f"  ✓ Successful queries: {successful_queries}/100")
    print(f"  ✓ Total memories retrieved: {total_retrieved}")

    metrics["test_results"]["retrieval"] = {
        "queries": 100,
        "successful": successful_queries,
        "rate": 100 / retrieval_time,
        "total_retrieved": total_retrieved,
    }

    # TEST 3: Drift Detection
    print("\n3️⃣ DRIFT DETECTION TEST (500 iterations)...")
    start_time = time.time()

    base_embedding = np.random.randn(1024).astype(np.float32)
    calibrations = 0

    for i in range(500):
        # Add progressive drift
        drift = base_embedding + np.random.randn(1024) * (i / 500) * 0.5
        drift = drift / (np.linalg.norm(drift) + 1e-8)

        result = await integration.drift.track_module_usage(
            "learning", "drift_test", drift, {"iteration": i}
        )

        if result["needs_calibration"]:
            calibrations += 1

    drift_time = time.time() - start_time

    print(f"  ✓ Drift tracking rate: {500 / drift_time:.1f} iterations/second")
    print(f"  ✓ Calibrations triggered: {calibrations}")

    metrics["test_results"]["drift"] = {
        "iterations": 500,
        "calibrations": calibrations,
        "rate": 500 / drift_time,
    }

    # TEST 4: Consensus Validation
    print("\n4️⃣ CONSENSUS VALIDATION TEST (50 memories)...")
    start_time = time.time()

    consensus_reached = 0
    for i in range(50):
        memory = {
            "content": f"Consensus test {i}",
            "type": "test",
            "timestamp": datetime.now(timezone.utc),
        }

        # Add some invalid memories
        if i % 10 == 0:
            memory["content"] = "This always never works"  # Contradiction

        result = await swarm.distributed_memory_storage(
            memory_data=memory, tags=["consensus_test"], proposing_colony="validator"
        )

        if result is not None:
            consensus_reached += 1

    consensus_time = time.time() - start_time
    consensus_rate = consensus_reached / 50 * 100

    print(f"  ✓ Consensus success rate: {consensus_rate:.1f}%")
    print(f"  ✓ Validation rate: {50 / consensus_time:.1f} validations/second")

    metrics["test_results"]["consensus"] = {
        "total": 50,
        "successful": consensus_reached,
        "success_rate": consensus_rate,
        "rate": 50 / consensus_time,
    }

    # TEST 5: Concurrent Operations
    print("\n5️⃣ CONCURRENT OPERATIONS TEST (10 seconds)...")
    start_time = time.time()
    end_time = start_time + 10

    operations = {"stores": 0, "retrievals": 0, "verifications": 0}

    async def store_worker():
        while time.time() < end_time:
            try:
                await memory.fold_in_with_embedding(
                    data={"content": f"Concurrent {operations['stores']}"},
                    tags=["concurrent"],
                    text_content=f"Concurrent {operations['stores']}",
                )
                operations["stores"] += 1
            except:
                pass
            await asyncio.sleep(0.01)

    async def retrieve_worker():
        while time.time() < end_time:
            try:
                await memory.fold_out_semantic("Concurrent", top_k=3)
                operations["retrievals"] += 1
            except:
                pass
            await asyncio.sleep(0.02)

    async def verify_worker():
        while time.time() < end_time:
            try:
                if memory.items:
                    item = random.choice(list(memory.items.values()))
                    await integration.verifold.verify_for_module(
                        "learning", item.item_id, item.data
                    )
                    operations["verifications"] += 1
            except:
                pass
            await asyncio.sleep(0.05)

    # Run workers concurrently
    await asyncio.gather(
        store_worker(),
        store_worker(),
        retrieve_worker(),
        retrieve_worker(),
        verify_worker(),
        return_exceptions=True,
    )

    concurrent_time = time.time() - start_time
    total_ops = sum(operations.values())

    print(f"  ✓ Total operations: {total_ops}")
    print(f"  ✓ Operations/second: {total_ops / concurrent_time:.1f}")
    print(
        f"  ✓ Breakdown: Stores={operations['stores']}, "
        f"Retrievals={operations['retrievals']}, "
        f"Verifications={operations['verifications']}"
    )

    metrics["test_results"]["concurrent"] = {
        "duration": concurrent_time,
        "total_operations": total_ops,
        "rate": total_ops / concurrent_time,
        "breakdown": operations,
    }

    # TEST 6: Memory Usage
    print("\n6️⃣ MEMORY USAGE TEST...")

    process = psutil.Process(os.getpid())
    current_memory = process.memory_info().rss / 1024 / 1024

    # Get system statistics
    stats = memory.get_enhanced_statistics()
    safety_report = safety.get_safety_report()

    print(f"  ✓ Process memory: {current_memory:.1f} MB")
    print(f"  ✓ Total memories: {stats['total_items']}")
    print(f"  ✓ Unique tags: {stats.get('unique_tags', len(memory.tag_registry))}")
    print(f"  ✓ Vector cache: {stats['vector_stats']['cache_size']}")
    print(
        f"  ✓ Bytes per memory: {current_memory * 1024 * 1024 / max(stats['total_items'], 1):.0f}"
    )

    metrics["performance"]["memory_usage"] = {
        "process_memory_mb": current_memory,
        "total_memories": stats["total_items"],
        "bytes_per_memory": current_memory * 1024 * 1024 / max(stats["total_items"], 1),
    }

    # FINAL REPORT
    print("\n📊 STRESS TEST SUMMARY")
    print("=" * 60)

    print("\nPerformance Metrics:")
    print(f"  • Storage: {metrics['test_results']['storage']['rate']:.1f} memories/sec")
    print(
        f"  • Retrieval: {metrics['test_results']['retrieval']['rate']:.1f} queries/sec"
    )
    print(
        f"  • Drift tracking: {metrics['test_results']['drift']['rate']:.1f} iterations/sec"
    )
    print(
        f"  • Consensus: {metrics['test_results']['consensus']['success_rate']:.1f}% success rate"
    )
    print(
        f"  • Concurrent ops: {metrics['test_results']['concurrent']['rate']:.1f} ops/sec"
    )

    print("\nSystem Health:")
    print(f"  • Average drift: {safety_report['drift_analysis']['average_drift']:.3f}")
    print(
        f"  • Integrity score: {safety_report['verifold_status']['average_integrity']:.3f}"
    )
    print(
        f"  • Quarantined memories: {safety_report['quarantine_status']['memories_in_quarantine']}"
    )
    print(f"  • Total errors: {len(metrics['errors'])}")

    print("\n✅ STRESS TESTS COMPLETE!")

    # Save results
    import json

    with open("stress_test_light_results.json", "w") as f:
        json.dump(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "metrics": metrics,
                "system_stats": {
                    "total_memories": stats["total_items"],
                    "unique_tags": stats.get("unique_tags", len(memory.tag_registry)),
                    "vector_cache_size": stats["vector_stats"]["cache_size"],
                    "causal_links": stats["causal_stats"]["total_causal_links"],
                },
            },
            f,
            indent=2,
        )

    print("\n📁 Results saved to stress_test_light_results.json")

    return metrics


if __name__ == "__main__":
    asyncio.run(run_light_stress_tests())
