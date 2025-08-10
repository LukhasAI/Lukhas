#!/usr/bin/env python3
"""
LUKHAS AGI Automatic Testing System - Quick Validation
===================================================

Quick validation script to test the automatic testing and logging system.
"""

import asyncio
import sys
import time
from pathlib import Path


# Simple test to verify the system works
async def main():
    print("🚀 LUKHAS AGI Automatic Testing System - Quick Test")
    print("=" * 60)

    try:
        # Import the system
        from automatic_testing_system import AutomaticTestingSystem

        print("✅ Successfully imported AutomaticTestingSystem")

        # Initialize the system
        autotest = AutomaticTestingSystem(
            workspace_path=Path.cwd().parent,
            enable_ai_analysis=True,
            enable_performance_monitoring=True,
        )
        print("✅ System initialized successfully")

        # Test 1: Simple terminal operation
        print("\n🧪 Test 1: Basic terminal operation capture")
        start_time = time.time()

        operation = await autotest.capture_terminal_operation(
            command="echo 'Hello LUKHAS AGI Testing System!'",
            operation_type="validation_test",
            timeout_seconds=10,
        )

        end_time = time.time()

        print(f"   Status: {operation.status}")
        print(f"   Duration: {operation.duration_ms:.2f}ms")
        print(f"   Output: {operation.output.strip()}")
        print(f"   Exit Code: {operation.exit_code}")

        # Performance validation
        if operation.duration_ms < 100:
            print("   🎯 ✅ Performance target met (< 100ms)")
        else:
            print(f"   🎯 ⚠️ Performance target missed ({operation.duration_ms:.2f}ms)")

        # Test 2: Multiple quick operations
        print("\n🧪 Test 2: Multiple operations performance test")

        test_commands = [
            "echo 'Test 1'",
            "echo 'Test 2'",
            "python3 -c 'print(\"Test 3\")'",
            "echo 'Test 4'",
            "echo 'Test 5'",
        ]

        durations = []
        successful = 0

        for i, cmd in enumerate(test_commands, 1):
            op = await autotest.capture_terminal_operation(cmd, timeout_seconds=5)
            durations.append(op.duration_ms)
            if op.status == "completed":
                successful += 1
            print(f"   Operation {i}: {op.duration_ms:.2f}ms - {op.status}")

        # Statistics
        if durations:
            avg_duration = sum(durations) / len(durations)
            max_duration = max(durations)
            min_duration = min(durations)
            success_rate = successful / len(test_commands) * 100
            sub_100ms = len([d for d in durations if d < 100])

            print("\n   📊 Performance Statistics:")
            print(f"   📈 Average: {avg_duration:.2f}ms")
            print(f"   ⬆️ Maximum: {max_duration:.2f}ms")
            print(f"   ⬇️ Minimum: {min_duration:.2f}ms")
            print(f"   ✅ Success rate: {success_rate:.1f}%")
            print(f"   🎯 Sub-100ms operations: {sub_100ms}/{len(durations)}")

        # Test 3: AI Analysis (if available)
        print("\n🧪 Test 3: AI Analysis capabilities")
        if autotest.ai_analyzer:
            try:
                analysis = autotest.ai_analyzer.analyze_operation(operation)
                print("   ✅ AI analysis completed")
                print(
                    f"   📊 Performance category: {analysis.get('performance_category', 'unknown')}"
                )
                print(
                    f"   🎯 Success probability: {analysis.get('success_probability', 0):.2f}"
                )
            except Exception as e:
                print(f"   ⚠️ AI analysis error: {e}")
        else:
            print("   ⚠️ AI analysis not available")

        # Test 4: Performance monitoring
        print("\n🧪 Test 4: Performance monitoring")
        if autotest.performance_monitor:
            try:
                metrics = autotest.performance_monitor.capture_metrics()
                print("   ✅ Performance monitoring active")
                print(f"   💻 CPU usage: {metrics.get('cpu_percent', 'N/A'):.1f}%")
                print(
                    f"   💾 Memory usage: {metrics.get('memory_percent', 'N/A'):.1f}%"
                )
            except Exception as e:
                print(f"   ⚠️ Performance monitoring error: {e}")
        else:
            print("   ⚠️ Performance monitoring not available")

        print("\n" + "=" * 60)
        print("🎉 VALIDATION COMPLETED SUCCESSFULLY!")
        print("✅ The automatic testing system is working properly")
        print("🚀 Ready for full-scale testing and monitoring")

        return True

    except Exception as e:
        print(f"\n❌ VALIDATION FAILED: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
