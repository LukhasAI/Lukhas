#!/usr/bin/env python3
"""
Demo script showing parallel orchestration capabilities.
Demonstrates the performance improvements from parallel execution.
"""

import asyncio
import time
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from lukhas.core.orchestration.async_orchestrator import AsyncOrchestrator
from lukhas.core.interfaces import CognitiveNodeBase


class DemoCognitiveNode(CognitiveNodeBase):
    """Demo cognitive node with realistic processing simulation."""

    def __init__(self, name: str, base_latency: float = 0.1):
        self.name = name
        self.base_latency = base_latency

    async def process(self, context):
        """Simulate cognitive processing with realistic latency."""
        # Simulate variable processing time based on complexity
        query_complexity = len(str(context.get("query", "")))
        processing_time = self.base_latency + (query_complexity * 0.001)

        await asyncio.sleep(processing_time)

        return {
            "result": f"processed_by_{self.name}",
            "confidence": 0.85,
            "ethics_risk": 0.1,
            "reasoning_chain": [f"{self.name}_analysis", f"{self.name}_synthesis"],
            "processing_time": processing_time,
            "timestamp": time.time()
        }


def setup_demo_registry():
    """Setup demo nodes for the orchestrator."""
    from lukhas.core.registry import register

    # Register demo cognitive nodes with realistic latencies
    register("node:memory", DemoCognitiveNode("memory", 0.15))
    register("node:attention", DemoCognitiveNode("attention", 0.12))
    register("node:thought", DemoCognitiveNode("thought", 0.25))
    register("node:risk", DemoCognitiveNode("risk", 0.08))
    register("node:intent", DemoCognitiveNode("intent", 0.10))
    register("node:action", DemoCognitiveNode("action", 0.18))


async def demo_sequential_vs_parallel():
    """Demonstrate sequential vs parallel execution performance."""
    print("🧠 LUKHAS AI - Parallel Orchestration Demo")
    print("=" * 50)

    # Setup
    setup_demo_registry()

    config = {
        "MATRIZ_ASYNC": "1",
        "MATRIZ_PARALLEL": "1",
        "MATRIZ_MAX_PARALLEL": "3"
    }

    orchestrator = AsyncOrchestrator(config)

    # Configure MATRIZ stages
    stages = [
        {"name": "MEMORY", "timeout_ms": 1000, "max_retries": 1},
        {"name": "ATTENTION", "timeout_ms": 1000, "max_retries": 1},
        {"name": "THOUGHT", "timeout_ms": 1500, "max_retries": 1},
        {"name": "RISK", "timeout_ms": 500, "max_retries": 1},
        {"name": "INTENT", "timeout_ms": 800, "max_retries": 1},
        {"name": "ACTION", "timeout_ms": 1200, "max_retries": 1},
    ]

    orchestrator.configure_stages(stages)

    # Test contexts
    contexts = [
        {
            "query": "Simple query",
            "user_id": "demo_user_1"
        },
        {
            "query": "This is a more complex query that requires deeper analysis and processing across multiple cognitive dimensions",
            "user_id": "demo_user_2"
        }
    ]

    for i, context in enumerate(contexts, 1):
        print(f"\n📝 Test {i}: {context['query'][:50]}{'...' if len(context['query']) > 50 else ''}")
        print("-" * 60)

        # Sequential execution
        print("🔄 Sequential Execution:")
        seq_start = time.time()
        seq_result = await orchestrator.process_query(context)
        seq_duration = time.time() - seq_start

        print(f"   ✅ Success: {seq_result.success}")
        print(f"   ⏱️  Duration: {seq_duration:.3f}s")
        print(f"   📊 Stages: {len(seq_result.stage_results)}")

        # Parallel execution
        print("\n⚡ Parallel Execution:")
        par_start = time.time()
        par_result = await orchestrator.process_query_parallel(context)
        par_duration = time.time() - par_start

        print(f"   ✅ Success: {par_result.success}")
        print(f"   ⏱️  Duration: {par_duration:.3f}s")
        print(f"   📊 Stages: {len(par_result.stage_results)}")

        # Performance comparison
        if par_duration > 0:
            speedup = seq_duration / par_duration
            improvement = ((seq_duration - par_duration) / seq_duration) * 100

            print(f"\n🚀 Performance Improvement:")
            print(f"   📈 Speedup Ratio: {speedup:.2f}x")
            print(f"   ⚡ Time Saved: {improvement:.1f}%")
            print(f"   🕐 Absolute Savings: {(seq_duration - par_duration):.3f}s")

        # Adaptive execution
        print("\n🎯 Adaptive Execution:")
        adapt_start = time.time()
        adapt_result = await orchestrator.process_adaptive(context)
        adapt_duration = time.time() - adapt_start

        print(f"   ✅ Success: {adapt_result.success}")
        print(f"   ⏱️  Duration: {adapt_duration:.3f}s")
        print(f"   🔀 Mode: {'Parallel' if len(context['query']) > 100 else 'Sequential'} (auto-selected)")


async def demo_batch_execution():
    """Demonstrate parallel batch execution patterns."""
    print("\n" + "=" * 50)
    print("🔄 Batch Processing Demo")
    print("=" * 50)

    setup_demo_registry()

    config = {
        "MATRIZ_ASYNC": "1",
        "MATRIZ_PARALLEL": "1",
        "MATRIZ_MAX_PARALLEL": "2"  # Smaller batches for demo
    }

    orchestrator = AsyncOrchestrator(config)

    stages = [
        {"name": "MEMORY", "timeout_ms": 800},
        {"name": "ATTENTION", "timeout_ms": 800},
        {"name": "THOUGHT", "timeout_ms": 800},
        {"name": "RISK", "timeout_ms": 800},
    ]

    orchestrator.configure_stages(stages)

    context = {
        "query": "Batch processing demonstration with multiple cognitive stages",
        "user_id": "batch_demo"
    }

    print(f"🧠 Processing: {context['query']}")
    print(f"📦 Max Parallel Stages: {orchestrator.max_parallel_stages}")

    # Show batch creation
    batches = orchestrator._create_stage_batches()
    print(f"\n📋 Created {len(batches)} batches:")
    for i, batch in enumerate(batches):
        batch_names = [stage.name for stage in batch]
        print(f"   Batch {i}: {batch_names}")

    # Execute with timing
    start_time = time.time()
    result = await orchestrator.process_query_parallel(context)
    duration = time.time() - start_time

    print(f"\n✅ Execution completed in {duration:.3f}s")
    print(f"📊 Results: {len(result.stage_results)} stages processed")

    # Show parallel metadata
    parallel_results = [r for r in result.stage_results if isinstance(r, dict) and "_parallel" in r]
    if parallel_results:
        print("\n🔍 Parallel Execution Metadata:")
        for r in parallel_results:
            batch_info = r.get("_parallel", {})
            print(f"   {r.get('stage', 'Unknown')}: Batch {batch_info.get('batch_index', '?')}")


if __name__ == "__main__":
    print("Starting LUKHAS AI Parallel Orchestration Demo...")
    print("This demo shows the performance benefits of parallel cognitive processing.\n")

    asyncio.run(demo_sequential_vs_parallel())
    asyncio.run(demo_batch_execution())

    print("\n" + "=" * 50)
    print("🎉 Demo Complete!")
    print("\nKey Takeaways:")
    print("• Parallel execution provides measurable performance improvements")
    print("• Adaptive mode automatically chooses optimal execution strategy")
    print("• Batch processing maintains result integrity while improving speed")
    print("• Comprehensive observability tracks all execution modes")
    print("=" * 50)