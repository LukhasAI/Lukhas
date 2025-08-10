#!/usr/bin/env python3
"""
🔥 LUKHAS Memory System - Final Stress Test
"""

import asyncio
import json
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


async def run_stress_test():
    """Run comprehensive stress test with proper error handling"""

    print("🔥 LUKHAS MEMORY SYSTEM - STRESS TEST")
    print("=" * 60)

    # Initialize
    print("\n🔧 Initializing systems...")
    memory_system = create_hybrid_memory_fold()
    safety = MemorySafetySystem()
    integration = MemorySafetyIntegration(safety, memory_system)

    # Add reality anchors
    safety.add_reality_anchor("test", "This is a stress test")

    # Register modules
    await integration.register_module("learning", {"drift_threshold": 0.3})
    await integration.register_module("creativity", {"drift_threshold": 0.6})

    # Set up swarm with enough colonies
    swarm = SwarmConsensusManager(integration, min_colonies=3)
    for i in range(5):
        role = [
            ColonyRole.VALIDATOR,
            ColonyRole.WITNESS,
            ColonyRole.ARBITER,
            ColonyRole.SPECIALIST,
            ColonyRole.VALIDATOR,
        ][i]
        swarm.register_colony(f"colony_{i}", role)

    print("✅ Systems initialized")

    # Metrics
    results = {
        "storage": {"count": 0, "errors": 0, "time": 0},
        "retrieval": {"count": 0, "errors": 0, "time": 0},
        "drift": {"count": 0, "calibrations": 0, "time": 0},
        "consensus": {"count": 0, "successful": 0, "time": 0},
        "concurrent": {"stores": 0, "retrievals": 0, "time": 0},
        "memory_usage": {},
    }

    # TEST 1: Storage Performance
    print("\n1️⃣ STORAGE PERFORMANCE TEST...")
    start = time.time()

    for i in range(1000):
        try:
            content = f"Test memory {i}: {''.join(random.choices(string.ascii_letters, k=30))}"
            memory_data = {
                "content": content,
                "type": random.choice(["knowledge", "experience", "observation"]),
                "index": i,
                "timestamp": datetime.now(timezone.utc),
            }

            if i % 2 == 0:
                # Direct storage
                await memory_system.fold_in_with_embedding(
                    data=memory_data,
                    tags=["stress_test", f"batch_{i//100}"],
                    text_content=content,
                )
            else:
                # Safe storage
                safe_fold = SafeMemoryFold(memory_system, safety)
                await safe_fold.safe_fold_in(memory_data, ["stress_test"])

            results["storage"]["count"] += 1

        except Exception:
            results["storage"]["errors"] += 1

    results["storage"]["time"] = time.time() - start
    rate = results["storage"]["count"] / results["storage"]["time"]
    print(f"  ✓ Stored {results['storage']['count']} memories")
    print(f"  ✓ Rate: {rate:.1f} memories/second")
    print(f"  ✓ Errors: {results['storage']['errors']}")

    # TEST 2: Retrieval Performance
    print("\n2️⃣ RETRIEVAL PERFORMANCE TEST...")
    start = time.time()

    for i in range(100):
        try:
            # Mix different query types
            if i % 3 == 0:
                # Tag query
                mems = await memory_system.fold_out_by_tag("stress_test", max_items=10)
                results["retrieval"]["count"] += len(mems)
            elif i % 3 == 1:
                # Semantic query
                query = f"Test memory {random.randint(0, 999)}"
                mems = await memory_system.fold_out_semantic(query, top_k=5)
                results["retrieval"]["count"] += len(mems)
            else:
                # Multi-tag query
                mems = await memory_system.fold_out_by_tags(
                    ["stress_test", f"batch_{i % 10}"], max_items=5
                )
                results["retrieval"]["count"] += len(mems)

        except Exception:
            results["retrieval"]["errors"] += 1

    results["retrieval"]["time"] = time.time() - start
    query_rate = 100 / results["retrieval"]["time"]
    print(f"  ✓ Retrieved {results['retrieval']['count']} memories")
    print(f"  ✓ Query rate: {query_rate:.1f} queries/second")
    print(f"  ✓ Errors: {results['retrieval']['errors']}")

    # TEST 3: Drift Detection
    print("\n3️⃣ DRIFT DETECTION TEST...")
    start = time.time()

    base_embedding = np.random.randn(1024).astype(np.float32)

    for i in range(500):
        try:
            # Add progressive drift
            noise = np.random.randn(1024) * (i / 500) * 0.5
            drifted = base_embedding + noise
            drifted = drifted / (np.linalg.norm(drifted) + 1e-8)

            drift_result = await integration.drift.track_module_usage(
                "learning", "drift_test", drifted, {"iteration": i}
            )

            results["drift"]["count"] += 1
            if drift_result["needs_calibration"]:
                results["drift"]["calibrations"] += 1

        except Exception:
            pass

    results["drift"]["time"] = time.time() - start
    drift_rate = results["drift"]["count"] / results["drift"]["time"]
    print(f"  ✓ Tracked {results['drift']['count']} drift measurements")
    print(f"  ✓ Rate: {drift_rate:.1f} measurements/second")
    print(f"  ✓ Calibrations triggered: {results['drift']['calibrations']}")

    # TEST 4: Consensus Validation
    print("\n4️⃣ CONSENSUS VALIDATION TEST...")
    start = time.time()

    for i in range(50):
        try:
            memory_data = {
                "content": f"Consensus test {i}",
                "type": "consensus_test",
                "timestamp": datetime.now(timezone.utc),
            }

            # Add some invalid memories
            if i % 10 == 0:
                memory_data["content"] = "This always never works"

            mem_id = await swarm.distributed_memory_storage(
                memory_data=memory_data,
                tags=["consensus"],
                proposing_colony=f"colony_{i % 5}",
            )

            results["consensus"]["count"] += 1
            if mem_id is not None:
                results["consensus"]["successful"] += 1

        except Exception:
            pass

    results["consensus"]["time"] = time.time() - start

    if results["consensus"]["count"] > 0:
        success_rate = (
            results["consensus"]["successful"] / results["consensus"]["count"] * 100
        )
        consensus_rate = results["consensus"]["count"] / results["consensus"]["time"]
        print(f"  ✓ Consensus validations: {results['consensus']['count']}")
        print(f"  ✓ Success rate: {success_rate:.1f}%")
        print(f"  ✓ Validation rate: {consensus_rate:.1f} validations/second")

    # TEST 5: Concurrent Operations
    print("\n5️⃣ CONCURRENT OPERATIONS TEST (5 seconds)...")
    start = time.time()
    end_time = start + 5

    async def store_worker():
        count = 0
        while time.time() < end_time:
            try:
                await memory_system.fold_in_with_embedding(
                    data={"content": f"Concurrent store {count}"},
                    tags=["concurrent"],
                    text_content=f"Concurrent store {count}",
                )
                results["concurrent"]["stores"] += 1
                count += 1
            except:
                pass
            await asyncio.sleep(0.01)

    async def retrieve_worker():
        while time.time() < end_time:
            try:
                await memory_system.fold_out_semantic("Concurrent", top_k=3)
                results["concurrent"]["retrievals"] += 1
            except:
                pass
            await asyncio.sleep(0.02)

    # Run workers
    await asyncio.gather(store_worker(), retrieve_worker(), return_exceptions=True)

    results["concurrent"]["time"] = time.time() - start
    total_ops = results["concurrent"]["stores"] + results["concurrent"]["retrievals"]
    ops_rate = total_ops / results["concurrent"]["time"]

    print(f"  ✓ Total operations: {total_ops}")
    print(f"  ✓ Rate: {ops_rate:.1f} operations/second")
    print(
        f"  ✓ Stores: {results['concurrent']['stores']}, Retrievals: {results['concurrent']['retrievals']}"
    )

    # Memory Usage
    print("\n6️⃣ MEMORY USAGE...")
    process = psutil.Process(os.getpid())
    memory_mb = process.memory_info().rss / 1024 / 1024

    # Get statistics
    stats = memory_system.get_enhanced_statistics()
    safety_report = safety.get_safety_report()

    results["memory_usage"] = {
        "process_memory_mb": memory_mb,
        "total_memories": stats["total_items"],
        "unique_tags": len(memory_system.tag_registry),
        "vector_cache": stats["vector_stats"]["cache_size"],
        "bytes_per_memory": memory_mb * 1024 * 1024 / max(stats["total_items"], 1),
    }

    print(f"  ✓ Process memory: {memory_mb:.1f} MB")
    print(f"  ✓ Total memories: {stats['total_items']}")
    print(f"  ✓ Bytes per memory: {results['memory_usage']['bytes_per_memory']:.0f}")

    # Final Report
    print("\n📊 STRESS TEST SUMMARY")
    print("=" * 60)

    print("\nPerformance Metrics:")
    print(
        f"  • Storage: {results['storage']['count'] / results['storage']['time']:.1f} memories/sec"
    )
    print(f"  • Retrieval: {100 / results['retrieval']['time']:.1f} queries/sec")
    print(
        f"  • Drift tracking: {results['drift']['count'] / results['drift']['time']:.1f} measurements/sec"
    )

    if results["consensus"]["count"] > 0:
        print(
            f"  • Consensus: {results['consensus']['successful'] / results['consensus']['count'] * 100:.1f}% success"
        )

    print(f"  • Concurrent: {ops_rate:.1f} ops/sec")

    print("\nSystem Health:")
    print(f"  • Average drift: {safety_report['drift_analysis']['average_drift']:.3f}")
    print(f"  • Max drift: {safety_report['drift_analysis']['max_drift']:.3f}")
    print(
        f"  • Integrity score: {safety_report['verifold_status']['average_integrity']:.3f}"
    )
    print(
        f"  • Quarantined: {safety_report['quarantine_status']['memories_in_quarantine']}"
    )

    print("\nCapacity:")
    print(f"  • Memories stored: {stats['total_items']}")
    print(
        f"  • Memory efficiency: {results['memory_usage']['bytes_per_memory']:.0f} bytes/memory"
    )
    print(
        f"  • Estimated capacity: ~{int(1000 * 1024 * 1024 / results['memory_usage']['bytes_per_memory'])} memories per GB"
    )

    # Save results
    with open("stress_test_results_final.json", "w") as f:
        json.dump(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "results": results,
                "system_stats": {
                    "total_memories": stats["total_items"],
                    "unique_tags": len(memory_system.tag_registry),
                    "vector_cache": stats["vector_stats"]["cache_size"],
                    "drift_metrics": safety_report["drift_analysis"],
                    "verifold_status": safety_report["verifold_status"],
                },
            },
            f,
            indent=2,
        )

    print("\n✅ STRESS TEST COMPLETE!")
    print("📁 Results saved to stress_test_results_final.json")

    return results


if __name__ == "__main__":
    asyncio.run(run_stress_test())
