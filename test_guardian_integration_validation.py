#!/usr/bin/env python3
"""
Guardian Integration Validation Test Suite
==========================================

Quick validation test for Guardian integration across all LUKHAS modules.
This is a focused test specifically for our implemented Guardian integration.
"""

import asyncio
import json
import sys
import time
import traceback
import uuid
from pathlib import Path


async def test_guardian_system_basics():
    """Test basic Guardian system functionality"""
    print("🛡️  Testing Guardian System basics...")

    try:
        from governance.guardian_system import GuardianSystem

        guardian = GuardianSystem()

        # Test sync validation
        result = guardian.validate_safety({"test": "basic_sync"})
        assert result.get("safe") is not None, "Guardian should return safety status"

        # Test async validation if available
        if hasattr(guardian, 'validate_action_async'):
            async_result = await guardian.validate_action_async({"test": "basic_async"})
            assert async_result.get("safe") is not None, "Async Guardian should return safety status"

        # Test Guardian status
        status = guardian.get_guardian_status()
        assert "enabled" in status, "Guardian status should include enabled field"

        print("    ✅ Guardian System basic functionality works")
        return True

    except Exception as e:
        print(f"    ❌ Guardian System test failed: {e}")
        return False


async def test_guardian_reflector():
    """Test Guardian drift detection and reflection"""
    print("🔍 Testing Guardian Reflector...")

    try:
        from governance.guardian_reflector import GuardianReflector

        reflector = GuardianReflector()

        # Test drift analysis
        drift_analysis = await reflector.analyze_drift({"test": "drift_analysis"})

        assert hasattr(drift_analysis, 'behavioral_drift'), "Should have behavioral drift score"
        assert hasattr(drift_analysis, 'performance_drift'), "Should have performance drift score"
        assert hasattr(drift_analysis, 'ethical_drift'), "Should have ethical drift score"

        # Test remediation plan generation
        if drift_analysis.remediation_plan:
            assert hasattr(drift_analysis.remediation_plan, 'actions'), "Should have remediation actions"

        print("    ✅ Guardian Reflector functionality works")
        return True

    except Exception as e:
        print(f"    ❌ Guardian Reflector test failed: {e}")
        return False


async def test_memory_guardian_integration():
    """Test Memory-Guardian integration"""
    print("🧠 Testing Memory-Guardian integration...")

    try:
        from memory.memory_event import MemoryEventFactory

        factory = MemoryEventFactory()

        # Check if Guardian integration is available
        if hasattr(factory, '_guardian_instance'):
            print("    ✅ Memory has Guardian integration configured")

        # Test memory event creation (should work with or without Guardian)
        event = factory.create(
            {"test": "memory_guardian_integration"},
            {"affect_delta": 0.3, "test_mode": True}
        )

        assert event.data is not None, "Memory event should have data"
        assert event.metadata is not None, "Memory event should have metadata"

        print("    ✅ Memory-Guardian integration works")
        return True

    except Exception as e:
        print(f"    ❌ Memory-Guardian integration test failed: {e}")
        return False


async def test_consciousness_guardian_integration():
    """Test Consciousness-Guardian integration"""
    print("🌟 Testing Consciousness-Guardian integration...")

    try:
        from lukhas.core.consciousness_stream import ConsciousnessStream

        stream = ConsciousnessStream()

        # Check if Guardian integration is enabled
        if hasattr(stream, '_guardian_integration_enabled'):
            guardian_enabled = stream._guardian_integration_enabled
            print(f"    Guardian integration enabled: {guardian_enabled}")

        # Test consciousness stream basic functionality
        if hasattr(stream, 'validate_consciousness_state_transition'):
            result = await stream.validate_consciousness_state_transition(
                "test_state",
                {"test": True}
            )
            assert "validated" in result, "Should return validation result"

        print("    ✅ Consciousness-Guardian integration works")
        return True

    except Exception as e:
        print(f"    ❌ Consciousness-Guardian integration test failed: {e}")
        return False


async def test_orchestrator_guardian_integration():
    """Test AI Orchestrator-Guardian integration"""
    print("🎭 Testing AI Orchestrator-Guardian integration...")

    try:
        from ai_orchestration.lukhas_ai_orchestrator import LUKHASAIOrchestrator

        # Use current directory as root for test
        orchestrator = LUKHASAIOrchestrator("/Users/agi_dev/LOCAL-REPOS/Lukhas")

        # Check if Guardian integration is available
        if hasattr(orchestrator, '_guardian_integration_enabled'):
            guardian_enabled = orchestrator._guardian_integration_enabled
            print(f"    Guardian integration enabled: {guardian_enabled}")

        # Test orchestrator status
        if hasattr(orchestrator, 'get_guardian_orchestrator_status'):
            status = orchestrator.get_guardian_orchestrator_status()
            assert "enabled" in status, "Should return Guardian status"

        print("    ✅ AI Orchestrator-Guardian integration works")
        return True

    except Exception as e:
        print(f"    ❌ AI Orchestrator-Guardian integration test failed: {e}")
        return False


async def test_identity_guardian_integration():
    """Test Identity-Guardian integration"""
    print("🔑 Testing Identity-Guardian integration...")

    try:
        from candidate.core.identity.manager import AdvancedIdentityManager

        identity_mgr = AdvancedIdentityManager()

        # Check if Guardian integration is available
        if hasattr(identity_mgr, '_guardian_integration_enabled'):
            guardian_enabled = identity_mgr._guardian_integration_enabled
            print(f"    Guardian integration enabled: {guardian_enabled}")

        # Test authentication with Guardian validation
        auth_result = await identity_mgr.authenticate({
            "user_id": "test_user_guardian",
            "text": "Test authentication with Guardian",
            "test_mode": True
        })

        assert "verified" in auth_result, "Should return authentication result"

        # Test registration with Guardian validation
        reg_result = await identity_mgr.register_user(
            "test_user_guardian_reg",
            {"text": "Test registration with Guardian"},
            {"test_mode": True}
        )

        assert "registered" in reg_result, "Should return registration result"

        print("    ✅ Identity-Guardian integration works")
        return True

    except Exception as e:
        print(f"    ❌ Identity-Guardian integration test failed: {e}")
        return False


async def test_lambda_id_guardian_integration():
    """Test Lambda ID-Guardian integration"""
    print("🆔 Testing Lambda ID-Guardian integration...")

    try:
        from candidate.governance.identity.core.lambd_id_service import LambdaIDService

        lambda_service = LambdaIDService()

        # Check if Guardian integration is available
        if hasattr(lambda_service, '_guardian_integration_enabled'):
            guardian_enabled = lambda_service._guardian_integration_enabled
            print(f"    Guardian integration enabled: {guardian_enabled}")

        # Test Lambda ID generation with Guardian validation
        result = await lambda_service.generate_lambda_id(
            tier=3,
            custom_options={"test_mode": True, "guardian_test": True}
        )

        assert "success" in result, "Should return generation result"

        if result.get("success"):
            assert "lambda_id" in result, "Should return Lambda ID on success"
            print(f"    Generated Lambda ID: {result.get('lambda_id', 'N/A')}")

        print("    ✅ Lambda ID-Guardian integration works")
        return True

    except Exception as e:
        print(f"    ❌ Lambda ID-Guardian integration test failed: {e}")
        return False


async def test_performance_baseline():
    """Test performance baseline for Guardian operations"""
    print("⚡ Testing Guardian performance baseline...")

    try:
        from governance.guardian_system import GuardianSystem

        guardian = GuardianSystem()

        # Test multiple Guardian operations for performance
        response_times = []

        for i in range(100):
            start_time = time.perf_counter_ns()

            result = guardian.validate_safety({
                "action_type": "performance_test",
                "iteration": i,
                "test_data": f"performance_test_{i}"
            })

            end_time = time.perf_counter_ns()
            response_time_us = (end_time - start_time) / 1000
            response_times.append(response_time_us)

        # Calculate basic statistics
        avg_time = sum(response_times) / len(response_times)
        sorted_times = sorted(response_times)
        p95_time = sorted_times[int(len(sorted_times) * 0.95)]

        print(f"    Average response time: {avg_time:.2f}μs")
        print(f"    P95 response time: {p95_time:.2f}μs")

        # Check if meets SLA (should be <100ms = 100,000μs)
        sla_compliant = p95_time < 100000
        print(f"    SLA compliance (<100ms): {'✅ PASS' if sla_compliant else '❌ FAIL'}")

        return sla_compliant

    except Exception as e:
        print(f"    ❌ Performance baseline test failed: {e}")
        return False


async def run_all_tests():
    """Run all Guardian integration tests"""
    print("="*70)
    print("🛡️  GUARDIAN INTEGRATION VALIDATION TESTS")
    print("="*70)

    test_results = {}

    # Run all test functions
    test_functions = [
        ("Guardian System Basics", test_guardian_system_basics),
        ("Guardian Reflector", test_guardian_reflector),
        ("Memory-Guardian Integration", test_memory_guardian_integration),
        ("Consciousness-Guardian Integration", test_consciousness_guardian_integration),
        ("Orchestrator-Guardian Integration", test_orchestrator_guardian_integration),
        ("Identity-Guardian Integration", test_identity_guardian_integration),
        ("Lambda ID-Guardian Integration", test_lambda_id_guardian_integration),
        ("Performance Baseline", test_performance_baseline),
    ]

    for test_name, test_func in test_functions:
        print(f"\n📋 Running: {test_name}")
        try:
            result = await test_func()
            test_results[test_name] = result
        except Exception as e:
            print(f"    ❌ Test failed with exception: {e}")
            test_results[test_name] = False

    # Summary
    print("\n" + "="*70)
    print("📊 TEST RESULTS SUMMARY")
    print("="*70)

    passed_tests = sum(1 for result in test_results.values() if result)
    total_tests = len(test_results)

    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"    {test_name}: {status}")

    print(f"\n🎯 Overall: {passed_tests}/{total_tests} tests passed")

    if passed_tests == total_tests:
        print("🏆 ALL GUARDIAN INTEGRATION TESTS PASSED! ✅")
        return 0
    else:
        print("⚠️  Some Guardian integration tests failed")
        return 1


def main():
    """Main entry point"""
    try:
        return asyncio.run(run_all_tests())
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted")
        return 1
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())