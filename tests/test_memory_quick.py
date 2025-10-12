#!/usr/bin/env python3
"""
Quick Memory Event Test
======================

Test our T4/0.01% Memory Event optimization implementation
"""

import gc
import time
from collections import deque

import psutil

from lukhas.memory.memory_event import MemoryEvent, MemoryEventFactory


def test_memory_event_bounded_optimization():
    """Test Memory Event bounded optimization"""
    print("🔍 Testing Memory Event Bounded Optimization...")

    factory = MemoryEventFactory()

    # Test 1: Drift history is bounded deque
    print("\n✅ Test 1: Drift History Structure")
    if isinstance(factory._drift_history, deque):
        print(f"  ✅ Drift history is deque: {type(factory._drift_history)}")
    else:
        print(f"  ❌ Drift history is not deque: {type(factory._drift_history)}")
        return False

    if factory._drift_history.maxlen == 100:
        print(f"  ✅ Drift history maxlen correct: {factory._drift_history.maxlen}")
    else:
        print(f"  ❌ Wrong maxlen: {factory._drift_history.maxlen}")
        return False

    # Test 2: Bounds are respected
    print("\n✅ Test 2: Bounds Enforcement")
    # Add more than maxlen items
    for i in range(150):
        factory._drift_history.append(float(i))

    if len(factory._drift_history) == 100:
        print(f"  ✅ Bounds respected: {len(factory._drift_history)}/100")
    else:
        print(f"  ❌ Bounds violated: {len(factory._drift_history)}/100")
        return False

    # Should contain the last 100 items (50-149)
    expected_values = list(range(50, 150))
    actual_values = list(factory._drift_history)
    if actual_values == expected_values:
        print("  ✅ Contains correct recent values")
    else:
        print(f"  ❌ Wrong values: expected {expected_values[:5]}..., got {actual_values[:5]}...")
        return False

    # Test 3: Empty deque handling
    print("\n✅ Test 3: Empty Deque Handling")
    empty_factory = MemoryEventFactory()
    assert len(empty_factory._drift_history) == 0

    event = empty_factory.create(
        data={"test": "data"},
        metadata={"affect_delta": 0.5}
    )

    if "driftTrend" in event.metadata["metrics"]:
        print("  ✅ Empty deque handled gracefully")
    else:
        print("  ❌ Empty deque not handled")
        return False

    # Test 4: Event creation
    print("\n✅ Test 4: Event Creation")
    event = factory.create(
        data={"test": "data"},
        metadata={"affect_delta": 0.6}
    )

    if isinstance(event, MemoryEvent):
        print(f"  ✅ Correct event type: {type(event)}")
    else:
        print(f"  ❌ Wrong event type: {type(event)}")
        return False

    if hasattr(event, 'data') and hasattr(event, 'metadata'):
        print("  ✅ Event has required attributes")
    else:
        print("  ❌ Event missing attributes")
        return False

    return True


def test_memory_event_performance():
    """Test Memory Event performance meets T4/0.01% SLA (<100μs)"""
    print("\n⚡ Testing Memory Event Performance SLA...")

    factory = MemoryEventFactory()

    # Warm up
    for _ in range(100):
        factory.create(
            data={"warmup": "test"},
            metadata={"affect_delta": 0.5}
        )

    # Performance test
    times = []
    event_count = 1000

    for i in range(event_count):
        start_time = time.time()
        event = factory.create(
            data={"event": i},
            metadata={"affect_delta": float(i % 100) / 100.0}
        )
        end_time = time.time()

        duration = (end_time - start_time) * 1000000  # Convert to μs
        times.append(duration)

    avg_time = sum(times) / len(times)
    p95_time = sorted(times)[int(event_count * 0.95)]
    max_time = max(times)
    events_per_second = event_count / (sum(times) / 1000000)

    print(f"  Average creation time: {avg_time:.2f}μs")
    print(f"  P95 creation time: {p95_time:.2f}μs")
    print(f"  Max creation time: {max_time:.2f}μs")
    print(f"  Events per second: {events_per_second:.0f}")

    # T4/0.01% SLA: <100μs p95
    if p95_time < 100.0:
        print(f"  ✅ P95 performance SLA met: {p95_time:.2f}μs < 100μs")
        performance_pass = True
    else:
        print(f"  ❌ P95 performance SLA violated: {p95_time:.2f}μs >= 100μs")
        performance_pass = False

    # Events per second should be > 10,000
    if events_per_second > 10000:
        print(f"  ✅ Throughput SLA met: {events_per_second:.0f} > 10,000 events/sec")
        throughput_pass = True
    else:
        print(f"  ❌ Throughput SLA violated: {events_per_second:.0f} <= 10,000 events/sec")
        throughput_pass = False

    return performance_pass and throughput_pass


def test_memory_usage_bounded():
    """Test that memory usage remains bounded under load"""
    print("\n💾 Testing Memory Usage Bounds...")

    process = psutil.Process()
    initial_memory = process.memory_info().rss

    factory = MemoryEventFactory()

    # Create many events to test memory bounds
    for i in range(10000):
        factory.create(
            data={"event": i},
            metadata={"affect_delta": float(i % 100) / 100.0}
        )

    # Force garbage collection
    gc.collect()

    final_memory = process.memory_info().rss
    memory_growth = final_memory - initial_memory

    print(f"  Initial memory: {initial_memory / 1024 / 1024:.1f}MB")
    print(f"  Final memory: {final_memory / 1024 / 1024:.1f}MB")
    print(f"  Memory growth: {memory_growth / 1024 / 1024:.1f}MB")

    # Drift history should still be bounded
    if len(factory._drift_history) <= 100:
        print(f"  ✅ Drift history bounded: {len(factory._drift_history)}/100")
        bounds_pass = True
    else:
        print(f"  ❌ Drift history exceeded bounds: {len(factory._drift_history)}/100")
        bounds_pass = False

    # Memory growth should be reasonable (less than 50MB for 10K events)
    if memory_growth < 50 * 1024 * 1024:
        print(f"  ✅ Memory growth acceptable: {memory_growth / 1024 / 1024:.1f}MB < 50MB")
        memory_pass = True
    else:
        print(f"  ❌ Excessive memory growth: {memory_growth / 1024 / 1024:.1f}MB >= 50MB")
        memory_pass = False

    return bounds_pass and memory_pass


def test_drift_trend_accuracy():
    """Test drift trend calculation accuracy"""
    print("\n📊 Testing Drift Trend Calculation...")

    factory = MemoryEventFactory()

    # Add known drift values
    test_values = [0.1, 0.2, 0.3, 0.4, 0.5]
    for value in test_values:
        factory._drift_history.append(value)

    # Create event which will add one more value
    event = factory.create(
        data={"test": "data"},
        metadata={"affect_delta": 0.6, "driftScore": 0.6}
    )

    # Should calculate trend from last 3 values: [0.4, 0.5, 0.6]
    expected_trend = (0.4 + 0.5 + 0.6) / 3
    actual_trend = event.metadata["metrics"]["driftTrend"]

    print(f"  Expected trend: {expected_trend:.6f}")
    print(f"  Actual trend: {actual_trend:.6f}")
    print(f"  Difference: {abs(actual_trend - expected_trend):.6f}")

    if abs(actual_trend - expected_trend) < 0.001:
        print("  ✅ Drift trend calculation accurate")
        return True
    else:
        print("  ❌ Drift trend calculation inaccurate")
        return False


def main():
    """Run Memory Event tests"""
    print("🚀 T4/0.01% Memory Event System Testing")
    print("=" * 50)

    try:
        # Test bounded optimization
        bounded_test = test_memory_event_bounded_optimization()

        # Test performance
        performance_test = test_memory_event_performance()

        # Test memory usage
        memory_test = test_memory_usage_bounded()

        # Test drift trend accuracy
        accuracy_test = test_drift_trend_accuracy()

        print("\n📊 Test Summary")
        print("=" * 30)
        print(f"Bounded Optimization: {'✅ PASS' if bounded_test else '❌ FAIL'}")
        print(f"Performance SLA: {'✅ PASS' if performance_test else '❌ FAIL'}")
        print(f"Memory Bounds: {'✅ PASS' if memory_test else '❌ FAIL'}")
        print(f"Drift Accuracy: {'✅ PASS' if accuracy_test else '❌ FAIL'}")

        all_pass = bounded_test and performance_test and memory_test and accuracy_test

        if all_pass:
            print("\n🎉 All Memory Event tests passed! T4/0.01% excellence achieved.")
            return 0
        else:
            print("\n⚠️  Some Memory Event tests failed.")
            return 1

    except Exception as e:
        print(f"\n❌ Memory Event test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
