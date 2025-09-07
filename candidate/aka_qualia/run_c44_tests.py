#!/usr/bin/env python3

"""
Wave C C4.4 Test Suite Runner
============================

Comprehensive test runner for the Wave C memory system with detailed reporting.
Validates production readiness across all test categories.
"""
import streamlit as st

import subprocess
import sys
import time
from pathlib import Path


def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"\n🧪 {description}")
    print(f"   Command: {' '.join(cmd)}")

    start_time = time.time()
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent,  # Project root
            env={"PYTHONPATH": ".", **dict(subprocess.os.environ)},
        )
        elapsed = time.time() - start_time

        if result.returncode == 0:
            print(f"   ✅ PASSED ({elapsed:.1f}s)")
            if result.stdout.strip():
                # Show key output lines
                lines = result.stdout.strip().split("\n")
                summary_lines = [l for l in lines if any(x in l for x in ["passed", "failed", "error", "==="])]
                for line in summary_lines[-3:]:  # Last 3 summary lines
                    print(f"      {line}")
            return True
        else:
            print(f"   ❌ FAILED ({elapsed:.1f}s)")
            if result.stderr.strip():
                # Show error details
                error_lines = result.stderr.strip().split("\n")
                for line in error_lines[:5]:  # First 5 error lines
                    print(f"      {line}")
            return False

    except Exception as e:
        elapsed = time.time() - start_time
        print(f"   💥 ERROR ({elapsed:.1f}s): {e!s}")
        return False


def main():
    """Run the complete C4.4 test suite"""
    print("🚀 Wave C C4.4 Memory System Test Suite")
    print("=" * 50)

    # Test categories with their commands
    test_categories = [
        {
            "name": "Simple Validation Tests",
            "cmd": ["python", "candidate/aka_qualia/test_simple.py"],
            "critical": True,
        },
        {
            "name": "Unit Tests - Fast Feedback",
            "cmd": [
                "python",
                "-m",
                "pytest",
                "candidate/aka_qualia/tests/test_memory_unit.py",
                "-v",
                "--tb=short",
                "-x",
            ],
            "critical": True,
        },
        {
            "name": "Contract Tests - Business Rules",
            "cmd": [
                "python",
                "-m",
                "pytest",
                "candidate/aka_qualia/tests/",
                "-m",
                "contract",
                "-v",
                "--tb=short",
            ],
            "critical": True,
        },
        {
            "name": "Integration Tests - Database Operations",
            "cmd": [
                "python",
                "-m",
                "pytest",
                "candidate/aka_qualia/tests/test_memory_integration.py",
                "-v",
                "--tb=short",
                "-x",
            ],
            "critical": False,
        },
        {
            "name": "Security Tests - Fault Injection",
            "cmd": [
                "python",
                "-m",
                "pytest",
                "candidate/aka_qualia/tests/test_memory_security.py",
                "-m",
                "fault",
                "-v",
                "--tb=short",
            ],
            "critical": False,
        },
        {
            "name": "GDPR Compliance Tests",
            "cmd": [
                "python",
                "-m",
                "pytest",
                "candidate/aka_qualia/tests/test_memory_gdpr.py",
                "-v",
                "--tb=short",
                "-x",
            ],
            "critical": False,
        },
        {
            "name": "Performance Tests - Benchmarks",
            "cmd": [
                "python",
                "-m",
                "pytest",
                "candidate/aka_qualia/tests/test_memory_performance.py",
                "-m",
                "perf and not slow",
                "-v",
                "--tb=short",
            ],
            "critical": False,
        },
    ]

    # Results tracking
    results = []
    critical_failures = 0

    # Run each test category
    for category in test_categories:
        success = run_command(category["cmd"], category["name"])
        results.append(
            {
                "name": category["name"],
                "success": success,
                "critical": category["critical"],
            }
        )

        if not success and category["critical"]:
            critical_failures += 1

    # Summary report
    print("\n" + "=" * 50)
    print("📊 C4.4 Test Suite Summary")
    print("=" * 50)

    total_tests = len(results)
    passed_tests = sum(1 for r in results if r["success"])
    failed_tests = total_tests - passed_tests

    print(f"📈 Overall: {passed_tests}/{total_tests} categories passed")
    print(
        f"🔍 Critical: {len([r for r in results if r['critical']]) - critical_failures}/{len([r for r in results if r['critical']])} critical tests passed"
    )

    # Detailed results
    for result in results:
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        critical = " (CRITICAL)" if result["critical"] else ""
        print(f"   {status} {result['name']}{critical}")

    # Final assessment
    print("\n🎯 Production Readiness Assessment:")

    if critical_failures == 0:
        if failed_tests == 0:
            print("   🌟 EXCELLENT: All tests passed - ready for production!")
            exit_code = 0
        else:
            print("   ✅ GOOD: Core functionality validated - minor issues in optional tests")
            exit_code = 0
    else:
        print("   ❌ NOT READY: Critical test failures must be resolved")
        exit_code = 1

    # Test infrastructure validation
    print("\n🏗️  Test Infrastructure Status:")
    test_files = [
        "candidate/aka_qualia/tests/conftest.py",
        "candidate/aka_qualia/tests/test_memory_unit.py",
        "candidate/aka_qualia/tests/test_memory_integration.py",
        "candidate/aka_qualia/tests/test_memory_security.py",
        "candidate/aka_qualia/tests/test_memory_gdpr.py",
        "candidate/aka_qualia/tests/test_memory_performance.py",
    ]

    for test_file in test_files:
        path = Path(test_file)
        if path.exists():
            print(f"   ✅ {path.name} - {path.stat().st_size} bytes")
        else:
            print(f"   ❌ {path.name} - MISSING")

    # Usage recommendations
    print("\n📚 Quick Test Commands:")
    print("   # Fast feedback loop")
    print("   python candidate/aka_qualia/test_simple.py")
    print("   ")
    print("   # Unit tests only")
    print("   python -m pytest candidate/aka_qualia/tests/test_memory_unit.py -v")
    print("   ")
    print("   # Contract validation")
    print("   python -m pytest candidate/aka_qualia/tests/ -m contract -v")
    print("   ")
    print("   # Full test suite")
    print("   python candidate/aka_qualia/run_c44_tests.py")

    print(f"\n🏁 C4.4 Testing Complete! Exit code: {exit_code}")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
