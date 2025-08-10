#!/usr/bin/env python3
"""
Agent 1 Task 5 Integration Test: Resource Efficiency Analyzer System
Tests the resource efficiency analyzer integration with core hub system.
"""

import json
import logging
import time

# Suppress noisy logs for cleaner test output
logging.getLogger("asyncio").setLevel(logging.WARNING)
logging.getLogger("psutil").setLevel(logging.WARNING)


def test_resource_analyzer_imports():
    """Test that all resource analyzer components can be imported"""
    print("Testing resource efficiency analyzer imports...")

    try:
        from core.resource_efficiency_analyzer import (
            EfficiencyReport,
            ResourceEfficiencyAnalyzer,
            ResourceSnapshot,
            ResourceTrend,
            ResourceType,
        )

        print("✅ All ResourceEfficiencyAnalyzer imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False


def test_resource_types_enum():
    """Test ResourceType enum functionality"""
    print("Testing ResourceType enum...")

    from core.resource_efficiency_analyzer import ResourceType

    expected_types = [
        "CPU",
        "MEMORY",
        "DISK_IO",
        "NETWORK_IO",
        "ENERGY",
        "THREADS",
        "FILE_DESCRIPTORS",
    ]

    actual_types = [rt.name for rt in ResourceType]

    for expected in expected_types:
        if expected not in actual_types:
            print(f"❌ Missing ResourceType: {expected}")
            return False

    print("✅ All ResourceType enum values present")
    return True


def test_resource_snapshot_creation():
    """Test ResourceSnapshot dataclass functionality"""
    print("Testing ResourceSnapshot creation...")

    from core.resource_efficiency_analyzer import ResourceSnapshot

    # Create a test snapshot
    snapshot = ResourceSnapshot(
        timestamp=time.time(),
        cpu_percent=25.5,
        memory_rss=1024 * 1024 * 100,  # 100MB
        memory_vms=1024 * 1024 * 200,  # 200MB
        memory_percent=15.0,
        disk_read_bytes=1024 * 1024,  # 1MB
        disk_write_bytes=1024 * 512,  # 512KB
        network_sent_bytes=1024 * 10,  # 10KB
        network_recv_bytes=1024 * 5,  # 5KB
        thread_count=8,
        open_files=25,
        energy_estimate=0.05,
        gc_stats={"gen0_collections": 10, "gen1_collections": 2},
    )

    # Test conversion to dictionary
    snapshot_dict = snapshot.to_dict()

    if not isinstance(snapshot_dict, dict):
        print("❌ ResourceSnapshot.to_dict() failed")
        return False

    if snapshot_dict["cpu_percent"] != 25.5:
        print("❌ ResourceSnapshot data conversion failed")
        return False

    print("✅ ResourceSnapshot creation and conversion successful")
    return True


def test_resource_analyzer_initialization():
    """Test ResourceEfficiencyAnalyzer initialization"""
    print("Testing ResourceEfficiencyAnalyzer initialization...")

    from core.resource_efficiency_analyzer import ResourceEfficiencyAnalyzer

    try:
        # Test basic initialization
        analyzer = ResourceEfficiencyAnalyzer(
            sample_interval=2.0, history_size=1800, enable_memory_profiling=True
        )

        if analyzer.sample_interval != 2.0:
            print("❌ Sample interval not set correctly")
            return False

        if analyzer.history_size != 1800:
            print("❌ History size not set correctly")
            return False

        if not analyzer.enable_memory_profiling:
            print("❌ Memory profiling not enabled")
            return False

        print("✅ ResourceEfficiencyAnalyzer initialization successful")
        return True

    except Exception as e:
        print(f"❌ ResourceEfficiencyAnalyzer init failed: {e}")
        return False


def test_resource_monitoring():
    """Test resource monitoring functionality"""
    print("Testing resource monitoring...")

    from core.resource_efficiency_analyzer import ResourceEfficiencyAnalyzer

    try:
        analyzer = ResourceEfficiencyAnalyzer(
            sample_interval=0.5,  # Fast sampling for test
            history_size=10,
            enable_memory_profiling=False,  # Disable for test speed
        )

        # Start monitoring
        analyzer.start_monitoring()

        if not analyzer._monitoring:
            print("❌ Monitoring not started")
            return False

        # Wait for some samples
        time.sleep(2.0)

        # Stop monitoring
        analyzer.stop_monitoring()

        if analyzer._monitoring:
            print("❌ Monitoring not stopped")
            return False

        # Check if we collected samples
        if len(analyzer.resource_history) == 0:
            print("❌ No resource samples collected")
            return False

        print(
            f"✅ Resource monitoring collected {len(analyzer.resource_history)} samples"
        )
        return True

    except Exception as e:
        print(f"❌ Resource monitoring failed: {e}")
        return False


def test_efficiency_analysis():
    """Test efficiency analysis functionality"""
    print("Testing efficiency analysis...")

    from core.resource_efficiency_analyzer import ResourceEfficiencyAnalyzer

    try:
        analyzer = ResourceEfficiencyAnalyzer(
            sample_interval=0.2, history_size=20, enable_memory_profiling=False
        )

        # Start monitoring
        analyzer.start_monitoring()

        # Generate some CPU load for more interesting analysis
        import math

        start_time = time.time()
        while time.time() - start_time < 2.0:
            math.sqrt(12345.67)

        # Let analyzer collect samples during the load
        time.sleep(1.0)

        # Stop monitoring
        analyzer.stop_monitoring()

        if len(analyzer.resource_history) < 5:
            print("❌ Insufficient samples for analysis")
            return False

        # Perform efficiency analysis
        report = analyzer.analyze_efficiency(duration_hours=0.1)

        if not hasattr(report, "efficiency_score"):
            print("❌ Missing efficiency_score in report")
            return False

        if not hasattr(report, "trends"):
            print("❌ Missing trends in report")
            return False

        if not hasattr(report, "recommendations"):
            print("❌ Missing recommendations in report")
            return False

        print(f"✅ Efficiency analysis complete: score={report.efficiency_score:.1f}")
        return True

    except Exception as e:
        print(f"❌ Efficiency analysis failed: {e}")
        return False


def test_core_hub_integration():
    """Test integration with CoreHub"""
    print("Testing CoreHub integration...")

    try:
        from core.core_hub import CoreHub

        # Initialize core hub
        hub = CoreHub()

        # Check if resource analyzer was registered
        if "resource_analyzer" not in hub.services:
            print("❌ Resource analyzer not registered in CoreHub")
            return False

        analyzer = hub.services["resource_analyzer"]

        # Verify it's the right type
        if not hasattr(analyzer, "start_monitoring"):
            print("❌ Registered service missing resource analyzer methods")
            return False

        if not hasattr(analyzer, "analyze_efficiency"):
            print("❌ Registered service missing analysis methods")
            return False

        print("✅ CoreHub integration successful")
        return True

    except Exception as e:
        print(f"❌ CoreHub integration failed: {e}")
        return False


def test_json_export():
    """Test JSON export functionality"""
    print("Testing JSON export...")

    from core.resource_efficiency_analyzer import ResourceEfficiencyAnalyzer

    try:
        analyzer = ResourceEfficiencyAnalyzer(
            sample_interval=0.3, history_size=10, enable_memory_profiling=False
        )

        # Start monitoring briefly
        analyzer.start_monitoring()
        time.sleep(1.5)
        analyzer.stop_monitoring()

        if len(analyzer.resource_history) == 0:
            print("❌ No data for JSON export test")
            return False

        # Test report JSON export
        report = analyzer.analyze_efficiency(duration_hours=0.1)
        json_str = report.to_json()

        # Verify it's valid JSON
        parsed = json.loads(json_str)

        if "efficiency_score" not in parsed:
            print("❌ JSON export missing efficiency_score")
            return False

        if "trends" not in parsed:
            print("❌ JSON export missing trends")
            return False

        print("✅ JSON export successful")
        return True

    except Exception as e:
        print(f"❌ JSON export failed: {e}")
        return False


def run_all_tests():
    """Run all resource efficiency analyzer tests"""
    print("=" * 60)
    print("🔬 AGENT 1 TASK 5: RESOURCE EFFICIENCY ANALYZER TESTS")
    print("=" * 60)

    tests = [
        test_resource_analyzer_imports,
        test_resource_types_enum,
        test_resource_snapshot_creation,
        test_resource_analyzer_initialization,
        test_resource_monitoring,
        test_efficiency_analysis,
        test_core_hub_integration,
        test_json_export,
    ]

    passed = 0
    total = len(tests)

    for test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_func.__name__} FAILED")
        except Exception as e:
            print(f"❌ {test_func.__name__} ERROR: {e}")
        print()

    print("=" * 60)
    print(f"📊 RESULTS: {passed}/{total} tests passed ({passed/total*100:.1f}%)")

    if passed == total:
        print(
            "🎉 ALL TESTS PASSED - Resource Efficiency Analyzer integration complete!"
        )
        return True
    else:
        print("⚠️  Some tests failed - review and fix issues")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
