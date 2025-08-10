#!/usr/bin/env python3
"""
Test Quantized Thought Cycles Implementation
Verifies discrete, auditable cognitive processing steps
"""

import asyncio
from datetime import datetime

from core.quantized_thought_cycles import (
    QuantizedThoughtProcessor,
)


async def test_basic_cycle_operation():
    """Test basic cycle operation"""
    print("\n🧪 Testing Basic Cycle Operation...")

    processor = QuantizedThoughtProcessor(cycle_frequency_hz=50.0)
    await processor.start()

    # Submit a thought
    thought_id = await processor.submit_thought("Hello, quantum world!")
    print(f"   - Submitted thought: {thought_id}")

    # Get result
    result = await processor.get_result(timeout=1.0)

    if result:
        print("   - Result received: ✅")
        print(f"   - Output: {result.output_data}")
        print(f"   - Duration: {result.duration_ms:.2f}ms")
        success = True
    else:
        print("   - Result timeout: ❌")
        success = False

    await processor.stop()
    return success


async def test_discrete_cycles():
    """Test that cycles are discrete and countable"""
    print("\n🧪 Testing Discrete Cycle Counting...")

    processor = QuantizedThoughtProcessor(cycle_frequency_hz=100.0)
    await processor.start()

    # Submit multiple thoughts
    num_thoughts = 10
    for i in range(num_thoughts):
        await processor.submit_thought(f"Thought {i}")

    # Wait for processing
    await asyncio.sleep(0.5)

    # Check metrics
    metrics = processor.get_metrics()
    print(f"   - Total cycles: {metrics['total_cycles']}")
    print(f"   - Successful cycles: {metrics['successful_cycles']}")
    print(f"   - Average cycle time: {metrics['average_cycle_time_ms']:.2f}ms")
    print(f"   - Current frequency: {metrics['current_frequency_hz']:.1f}Hz")

    # Verify discrete cycles
    success = metrics["total_cycles"] >= num_thoughts
    print(f"   - Discrete cycles verified: {'✅' if success else '❌'}")

    await processor.stop()
    return success


async def test_cycle_phases():
    """Test that all phases are executed in order"""
    print("\n🧪 Testing Cycle Phase Execution...")

    processor = QuantizedThoughtProcessor(cycle_frequency_hz=20.0)
    await processor.start()

    # Submit thought
    await processor.submit_thought({"test": "data", "phase": "check"})

    # Wait and get result
    result = await processor.get_result(timeout=1.0)

    # Get cycle trace
    trace = processor.get_cycle_trace(last_n=1)

    if trace and len(trace) > 0:
        last_cycle = trace[0]
        phases = [p["phase"] for p in last_cycle["phases"]]

        expected_phases = ["bind", "conform", "catalyze", "release"]
        phases_match = phases == expected_phases

        print(f"   - Executed phases: {phases}")
        print(f"   - Phase order correct: {'✅' if phases_match else '❌'}")

        # Show phase timings
        for phase_info in last_cycle["phases"]:
            print(f"   - {phase_info['phase']}: {phase_info['duration_ms']:.2f}ms")

        success = phases_match
    else:
        print("   - No cycle trace available: ❌")
        success = False

    await processor.stop()
    return success


async def test_energy_management():
    """Test energy consumption and limits"""
    print("\n🧪 Testing Energy Management...")

    processor = QuantizedThoughtProcessor(
        cycle_frequency_hz=50.0, max_energy_per_cycle=3
    )
    await processor.start()

    initial_energy = processor.energy_pool
    print(f"   - Initial energy pool: {initial_energy}")

    # Submit high-energy thought
    high_energy_id = await processor.submit_thought(
        "High energy computation", energy_required=5
    )

    # Submit normal thought
    normal_id = await processor.submit_thought("Normal computation", energy_required=2)

    # Wait for processing
    await asyncio.sleep(0.2)

    # Check results
    metrics = processor.get_metrics()
    final_energy = processor.energy_pool

    print(f"   - Final energy pool: {final_energy}")
    print(f"   - Energy consumed: {initial_energy - final_energy}")
    print(f"   - Successful cycles: {metrics['successful_cycles']}")

    # Energy should have been consumed for normal thought
    success = final_energy < initial_energy
    print(f"   - Energy management working: {'✅' if success else '❌'}")

    await processor.stop()
    return success


async def test_pause_resume():
    """Test pause and resume functionality"""
    print("\n🧪 Testing Pause/Resume Functionality...")

    processor = QuantizedThoughtProcessor(cycle_frequency_hz=50.0)
    await processor.start()

    # Submit thoughts
    await processor.submit_thought("Before pause")

    # Get initial metrics
    await asyncio.sleep(0.1)
    metrics_before = processor.get_metrics()
    cycles_before = metrics_before["total_cycles"]

    # Pause
    await processor.pause()
    print(f"   - Processor paused at cycle {cycles_before}")

    # Wait while paused
    await asyncio.sleep(0.2)

    # Check no new cycles during pause
    metrics_paused = processor.get_metrics()
    cycles_paused = metrics_paused["total_cycles"]

    # Resume
    await processor.resume()
    print("   - Processor resumed")

    # Submit more thoughts
    await processor.submit_thought("After resume")
    await asyncio.sleep(0.1)

    # Final metrics
    metrics_after = processor.get_metrics()
    cycles_after = metrics_after["total_cycles"]

    print(f"   - Cycles before pause: {cycles_before}")
    print(f"   - Cycles during pause: {cycles_paused - cycles_before}")
    print(f"   - Cycles after resume: {cycles_after - cycles_paused}")

    # Should have no cycles during pause
    success = cycles_paused == cycles_before and cycles_after > cycles_paused
    print(f"   - Pause/Resume working: {'✅' if success else '❌'}")

    await processor.stop()
    return success


async def test_cycle_auditing():
    """Test cycle trace auditing capability"""
    print("\n🧪 Testing Cycle Auditing...")

    processor = QuantizedThoughtProcessor(cycle_frequency_hz=30.0)
    await processor.start()

    # Submit various thoughts
    test_data = [
        "Simple string",
        {"key": "value", "number": 42},
        ["list", "of", "items"],
        12345,
    ]

    for data in test_data:
        await processor.submit_thought(data)

    # Wait for processing
    await asyncio.sleep(0.3)

    # Get full trace
    trace = processor.get_cycle_trace(last_n=10)

    print(f"   - Captured {len(trace)} cycle traces")

    # Verify each cycle has auditable information
    audit_success = True
    for i, cycle in enumerate(trace):
        has_id = "quantum_id" in cycle
        has_phases = "phases" in cycle and len(cycle["phases"]) > 0
        has_timing = all("duration_ms" in p for p in cycle.get("phases", []))

        if not (has_id and has_phases and has_timing):
            audit_success = False
            print(f"   - Cycle {i} missing audit info: ❌")
        else:
            total_time = sum(p["duration_ms"] for p in cycle["phases"])
            print(f"   - Cycle {i}: {cycle['quantum_id'][:15]}... ({total_time:.1f}ms)")

    print(f"   - All cycles auditable: {'✅' if audit_success else '❌'}")

    await processor.stop()
    return audit_success


async def main():
    """Run all tests"""
    print("🚀 Testing Quantized Thought Cycles Implementation")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    results = []

    # Run tests
    results.append(await test_basic_cycle_operation())
    results.append(await test_discrete_cycles())
    results.append(await test_cycle_phases())
    results.append(await test_energy_management())
    results.append(await test_pause_resume())
    results.append(await test_cycle_auditing())

    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    passed = sum(results)
    total = len(results)
    print(f"   - Tests passed: {passed}/{total}")
    print(f"   - Success rate: {(passed/total)*100:.0f}%")

    if passed == total:
        print("\n✅ Quantized Thought Cycles fully operational!")
        print("   - Discrete cycles: Working")
        print("   - Phase execution: Verified")
        print("   - Energy management: Active")
        print("   - Pause/Resume: Functional")
        print("   - Audit trail: Complete")
    else:
        print("\n⚠️ Some tests need attention")

    return passed == total


if __name__ == "__main__":
    import sys

    success = asyncio.run(main())
    sys.exit(0 if success else 1)
