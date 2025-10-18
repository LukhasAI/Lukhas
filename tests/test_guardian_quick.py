#!/usr/bin/env python3
"""
Quick Guardian System Test
==========================

Test our T4/0.01% Guardian response schema standardization
"""

import os
import time
from pathlib import Path

from governance.guardian_system import GuardianSystem


def test_guardian_schema_standardization():
    """Test Guardian response schema standardization"""
    print("🔍 Testing Guardian Response Schema Standardization...")

    guardian = GuardianSystem()

    # Test 1: Basic response structure
    print("\n✅ Test 1: Basic Response Structure")
    response = guardian.validate_safety({"test": "data"})

    required_fields = {
        "safe", "drift_score", "guardian_status", "emergency_active",
        "enforcement_enabled", "schema_version", "timestamp", "correlation_id"
    }

    print(f"  Response keys: {set(response.keys())}")
    missing_fields = required_fields - set(response.keys())

    if missing_fields:
        print(f"  ❌ Missing fields: {missing_fields}")
        return False
    else:
        print("  ✅ All required fields present")

    # Test 2: Schema version
    print("\n✅ Test 2: Schema Version")
    if response["schema_version"] == "1.0.0":
        print(f"  ✅ Schema version correct: {response['schema_version']}")
    else:
        print(f"  ❌ Wrong schema version: {response['schema_version']}")
        return False

    # Test 3: Timestamp validity
    print("\n✅ Test 3: Timestamp Validity")
    timestamp = response["timestamp"]
    current_time = time.time()

    if abs(timestamp - current_time) < 1.0:  # Within 1 second
        print(f"  ✅ Timestamp valid: {timestamp}")
    else:
        print(f"  ❌ Timestamp invalid: {timestamp} vs {current_time}")
        return False

    # Test 4: Correlation ID format
    print("\n✅ Test 4: Correlation ID Format")
    correlation_id = response["correlation_id"]

    if len(correlation_id) == 36 and correlation_id.count('-') == 4:
        print(f"  ✅ Correlation ID valid UUID format: {correlation_id}")
    else:
        print(f"  ❌ Invalid correlation ID format: {correlation_id}")
        return False

    # Test 5: Emergency Active Field
    print("\n✅ Test 5: Emergency Active Field")
    emergency_active = response["emergency_active"]
    emergency_file = Path("/tmp/guardian_emergency_disable")

    expected_emergency = emergency_file.exists()
    if emergency_active == expected_emergency:
        print(f"  ✅ Emergency active field correct: {emergency_active}")
    else:
        print(f"  ❌ Emergency active mismatch: {emergency_active} vs {expected_emergency}")
        return False

    # Test 6: Enforcement Enabled Field
    print("\n✅ Test 6: Enforcement Enabled Field")
    enforcement_enabled = response["enforcement_enabled"]
    dsl_setting = os.getenv("ENFORCE_ETHICS_DSL", "1")
    expected_enforcement = dsl_setting != "0"

    if enforcement_enabled == expected_enforcement:
        print(f"  ✅ Enforcement enabled field correct: {enforcement_enabled}")
    else:
        print(f"  ❌ Enforcement enabled mismatch: {enforcement_enabled} vs {expected_enforcement}")
        return False

    print("\n🎉 All Guardian schema tests passed!")
    print(f"📊 Full response: {response}")

    return True


def test_guardian_performance():
    """Test Guardian performance meets T4/0.01% SLA (<100ms)"""
    print("\n⚡ Testing Guardian Performance SLA...")

    guardian = GuardianSystem()

    # Warm up
    for _ in range(10):
        guardian.validate_safety({"warmup": "test"})

    # Performance test
    times = []
    for i in range(100):
        start_time = time.time()
        guardian.validate_safety({"test": f"data_{i}"})
        end_time = time.time()

        duration = (end_time - start_time) * 1000  # Convert to ms
        times.append(duration)

    avg_time = sum(times) / len(times)
    p95_time = sorted(times)[94]  # 95th percentile
    max_time = max(times)

    print(f"  Average response time: {avg_time:.2f}ms")
    print(f"  P95 response time: {p95_time:.2f}ms")
    print(f"  Max response time: {max_time:.2f}ms")

    # T4/0.01% SLA: <100ms p95
    if p95_time < 100.0:
        print(f"  ✅ P95 performance SLA met: {p95_time:.2f}ms < 100ms")
        return True
    else:
        print(f"  ❌ P95 performance SLA violated: {p95_time:.2f}ms >= 100ms")
        return False


def main():
    """Run Guardian tests"""
    print("🚀 T4/0.01% Guardian System Testing")
    print("=" * 50)

    try:
        # Test schema standardization
        schema_test = test_guardian_schema_standardization()

        # Test performance
        performance_test = test_guardian_performance()

        print("\n📊 Test Summary")
        print("=" * 30)
        print(f"Schema Standardization: {'✅ PASS' if schema_test else '❌ FAIL'}")
        print(f"Performance SLA: {'✅ PASS' if performance_test else '❌ FAIL'}")

        if schema_test and performance_test:
            print("\n🎉 All Guardian tests passed! T4/0.01% excellence achieved.")
            return 0
        else:
            print("\n⚠️  Some Guardian tests failed.")
            return 1

    except Exception as e:
        print(f"\n❌ Guardian test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
