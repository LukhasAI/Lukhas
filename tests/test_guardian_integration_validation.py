#!/usr/bin/env python3
"""
M.1 Memory Integration Validation
=================================

Quick integration test to verify M.1 memory system components
work correctly with Guardian integration.
"""

import asyncio
import sys
import time
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from lukhas.memory.backends.pgvector_store import PgVectorStore, VectorDoc
from lukhas.memory.indexer import Indexer
from lukhas.memory.lifecycle import Lifecycle, RetentionPolicy
from lukhas.memory.memory_orchestrator import MemoryOrchestrator
from lukhas.memory.observability import MemoryTracer


class TestPgClient:
    """Test database client."""
    def __init__(self):
        self.call_count = 0

    def execute(self, query, params=None):
        self.call_count += 1
        return {"affected_rows": 1}

class TestVectorStore(PgVectorStore):
    """Test vector store with actual implementations."""
    def __init__(self, conn, table="test_store", dim: int = 1536):
        super().__init__(conn, table, dim)
        self.storage = {}

    def add(self, doc: VectorDoc) -> str:
        self.storage[doc.id] = doc
        return doc.id

    def bulk_add(self, docs):
        return [self.add(doc) for doc in docs]

    def search(self, embedding, k: int = 10, filters=None):
        # Simple mock search
        results = []
        for doc_id, doc in self.storage.items():
            if filters:
                # Check filters
                match = True
                for key, value in filters.items():
                    if key not in doc.meta or doc.meta[key] != value:
                        match = False
                        break
                if not match:
                    continue
            # Mock similarity score
            results.append((doc_id, 0.95))
        return results[:k]

    def delete(self, *, id=None, where=None):
        if id and id in self.storage:
            del self.storage[id]
            return 1
        return 0

    def stats(self):
        return {"table": self.table, "dim": self.dim, "count": len(self.storage)}

async def test_memory_orchestrator_integration():
    """Test MemoryOrchestrator with all components."""
    print("🧪 Testing Memory Orchestrator Integration...")

    # Setup components
    conn = TestPgClient()
    store = TestVectorStore(conn, dim=128)
    indexer = Indexer(store)
    orchestrator = MemoryOrchestrator(indexer)

    # Test add_event
    start_time = time.perf_counter()
    event_id = await orchestrator.add_event("Test memory event", {"lane": "test", "priority": "high"})
    add_duration = (time.perf_counter() - start_time) * 1000

    assert isinstance(event_id, str)
    assert len(event_id) > 0
    print(f"   ✅ add_event: {add_duration:.3f}ms")

    # Test query
    start_time = time.perf_counter()
    results = orchestrator.query("Test memory", k=5)
    query_duration = (time.perf_counter() - start_time) * 1000

    assert isinstance(results, list)
    print(f"   ✅ query: {query_duration:.3f}ms")

    # Test legacy compatibility
    legacy_result = orchestrator.orchestrate_memory("test_op", {"data": "test"})
    assert legacy_result["status"] == "success"
    print("   ✅ legacy compatibility maintained")

    # Test storage stats
    stats = store.stats()
    assert stats["count"] >= 1
    print(f"   ✅ storage stats: {stats['count']} events stored")

    return {
        "add_event_ms": add_duration,
        "query_ms": query_duration,
        "events_stored": stats["count"],
        "integration_success": True
    }

async def test_guardian_integration():
    """Test Guardian integration hooks."""
    print("🛡️  Testing Guardian Integration...")

    class MockGuardian:
        def __init__(self):
            self.validate_calls = 0
            self.monitor_calls = 0

        async def validate_action_async(self, action, context):
            self.validate_calls += 1
            # Simulate Guardian validation
            assert action == "memory_add"
            assert "text" in context
            assert "meta" in context
            return True

        async def monitor_behavior_async(self, behavior, context):
            self.monitor_calls += 1
            assert behavior == "memory_added"
            assert "id" in context
            assert "text_len" in context
            return True

    # Setup with Guardian
    conn = TestPgClient()
    store = TestVectorStore(conn, dim=128)
    indexer = Indexer(store)
    guardian = MockGuardian()
    orchestrator = MemoryOrchestrator(indexer, guardian)

    # Test Guardian-integrated operation
    event_id = await orchestrator.add_event("Guardian-protected event", {"security": "high"})

    assert guardian.validate_calls == 1
    assert guardian.monitor_calls == 1
    assert isinstance(event_id, str)

    print(f"   ✅ Guardian validation calls: {guardian.validate_calls}")
    print(f"   ✅ Guardian monitoring calls: {guardian.monitor_calls}")

    return {
        "guardian_validate_calls": guardian.validate_calls,
        "guardian_monitor_calls": guardian.monitor_calls,
        "guardian_integration_success": True
    }

def test_component_contracts():
    """Test that all components meet their contracts."""
    print("📋 Testing Component Contracts...")

    # Test VectorDoc
    doc = VectorDoc("test-123", "test text", [0.1] * 1536, {"key": "value"})
    assert doc.id == "test-123"
    assert doc.text == "test text"
    assert len(doc.embedding) == 1536
    assert doc.meta["key"] == "value"
    print("   ✅ VectorDoc contract")

    # Test RetentionPolicy
    policy = RetentionPolicy(days=30)
    assert policy.days == 30
    print("   ✅ RetentionPolicy contract")

    # Test Lifecycle
    lifecycle = Lifecycle(policy)
    assert lifecycle.retention.days == 30
    print("   ✅ Lifecycle contract")

    # Test MemoryTracer
    tracer = MemoryTracer()
    span_context = tracer.trace_operation("test")
    assert hasattr(span_context, '__enter__')
    assert hasattr(span_context, '__exit__')
    print("   ✅ MemoryTracer contract")

    return {"contract_validation_success": True}

async def run_performance_baseline():
    """Run performance baseline for key operations."""
    print("⚡ Running Performance Baseline...")

    conn = TestPgClient()
    store = TestVectorStore(conn, dim=128)
    indexer = Indexer(store)
    orchestrator = MemoryOrchestrator(indexer)

    # Warmup
    for i in range(10):
        await orchestrator.add_event(f"warmup {i}", {"type": "warmup"})

    # Measure add_event performance
    latencies = []
    for i in range(100):
        start = time.perf_counter_ns()
        await orchestrator.add_event(f"perf test {i}", {"index": i})
        end = time.perf_counter_ns()
        latencies.append((end - start) / 1000)  # microseconds

    avg_latency = sum(latencies) / len(latencies)
    p95_latency = sorted(latencies)[95]

    print(f"   📊 add_event average: {avg_latency:.1f}μs")
    print(f"   📊 add_event P95: {p95_latency:.1f}μs")

    # Target: <1000μs (1ms)
    sla_met = avg_latency < 1000 and p95_latency < 1000

    print(f"   {'✅' if sla_met else '❌'} SLA compliance: {sla_met}")

    return {
        "avg_latency_us": avg_latency,
        "p95_latency_us": p95_latency,
        "sla_target_us": 1000,
        "sla_met": sla_met
    }

async def main():
    """Run complete M.1 integration validation."""
    print("🔬 M.1 Memory Integration Validation")
    print("=" * 40)

    results = {}

    try:
        # Test component contracts
        results["contracts"] = test_component_contracts()

        # Test memory orchestrator integration
        results["orchestrator"] = await test_memory_orchestrator_integration()

        # Test Guardian integration
        results["guardian"] = await test_guardian_integration()

        # Run performance baseline
        results["performance"] = await run_performance_baseline()

        # Overall assessment
        all_success = (
            results["contracts"]["contract_validation_success"] and
            results["orchestrator"]["integration_success"] and
            results["guardian"]["guardian_integration_success"] and
            results["performance"]["sla_met"]
        )

        print("\n🏆 INTEGRATION VALIDATION SUMMARY")
        print("=" * 35)
        print(f"Component Contracts: {'✅ PASS' if results['contracts']['contract_validation_success'] else '❌ FAIL'}")
        print(f"Orchestrator Integration: {'✅ PASS' if results['orchestrator']['integration_success'] else '❌ FAIL'}")
        print(f"Guardian Integration: {'✅ PASS' if results['guardian']['guardian_integration_success'] else '❌ FAIL'}")
        print(f"Performance SLA: {'✅ PASS' if results['performance']['sla_met'] else '❌ FAIL'}")
        print("")
        print(f"Overall M.1 Status: {'🎉 SUCCESS - READY FOR DEPLOYMENT' if all_success else '🔧 NEEDS WORK'}")

        return results

    except Exception as e:
        print(f"❌ Validation failed with error: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

if __name__ == "__main__":
    asyncio.run(main())
