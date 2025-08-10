#!/usr/bin/env python3
"""
LUKHAS AI - Comprehensive Integration Test Runner
Executes all integration, performance, and security tests
"""

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Test suite modules to run
TEST_SUITES = [
    {
        "name": "Golden Trio Integration",
        "module": "tests.test_golden_trio_integration",
        "file": "test_golden_trio_integration.py",
        "category": "integration",
        "priority": "high",
    },
    {
        "name": "System Integration E2E",
        "module": "tests.test_system_integration_e2e",
        "file": "test_system_integration_e2e.py",
        "category": "integration",
        "priority": "high",
    },
    {
        "name": "Performance Benchmarks",
        "module": "tests.test_performance_benchmarks",
        "file": "test_performance_benchmarks.py",
        "category": "performance",
        "priority": "medium",
    },
    {
        "name": "Security Validation",
        "module": "tests.test_security_validation",
        "file": "test_security_validation.py",
        "category": "security",
        "priority": "high",
    },
]


class IntegrationTestRunner:
    """Main test runner for all integration tests"""

    def __init__(self, verbose: bool = True, categories: List[str] = None):
        self.verbose = verbose
        self.categories = categories or ["integration", "performance", "security"]
        self.results = []
        self.start_time = None
        self.end_time = None

    def run_test_suite(self, suite: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single test suite"""
        print(f"\n{'='*60}")
        print(f"🧪 Running: {suite['name']}")
        print(f"Category: {suite['category']} | Priority: {suite['priority']}")
        print(f"{'='*60}")

        start_time = time.time()

        # Run pytest for the test file
        cmd = [
            sys.executable,
            "-m",
            "pytest",
            f"tests/{suite['file']}",
            "-v" if self.verbose else "-q",
            "--tb=short",
            "-x",  # Stop on first failure
            "--color=yes",
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout per suite
            )

            duration = time.time() - start_time

            # Parse results
            passed = "passed" in result.stdout
            failed_count = result.stdout.count("FAILED")
            passed_count = result.stdout.count("passed")

            suite_result = {
                "name": suite["name"],
                "category": suite["category"],
                "priority": suite["priority"],
                "duration": round(duration, 2),
                "passed": result.returncode == 0,
                "tests_run": passed_count + failed_count,
                "tests_passed": passed_count,
                "tests_failed": failed_count,
                "stdout": result.stdout if self.verbose else "",
                "stderr": result.stderr if result.stderr else "",
            }

            # Print summary
            if suite_result["passed"]:
                print(
                    f"✅ {suite['name']} - PASSED ({suite_result['tests_passed']} tests in {duration:.2f}s)"
                )
            else:
                print(
                    f"❌ {suite['name']} - FAILED ({suite_result['tests_failed']} failures in {duration:.2f}s)"
                )
                if result.stderr:
                    print(f"Errors:\n{result.stderr}")

        except subprocess.TimeoutExpired:
            suite_result = {
                "name": suite["name"],
                "category": suite["category"],
                "priority": suite["priority"],
                "duration": 300,
                "passed": False,
                "error": "Timeout expired (>5 minutes)",
                "tests_run": 0,
                "tests_passed": 0,
                "tests_failed": 0,
            }
            print(f"⏱️ {suite['name']} - TIMEOUT")

        except Exception as e:
            suite_result = {
                "name": suite["name"],
                "category": suite["category"],
                "priority": suite["priority"],
                "duration": time.time() - start_time,
                "passed": False,
                "error": str(e),
                "tests_run": 0,
                "tests_passed": 0,
                "tests_failed": 0,
            }
            print(f"💥 {suite['name']} - ERROR: {e}")

        return suite_result

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all test suites"""
        self.start_time = datetime.now()

        print("\n" + "=" * 80)
        print("🚀 LUKHAS AI - Comprehensive Integration Test Suite")
        print(f"Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Categories: {', '.join(self.categories)}")
        print("=" * 80)

        # Filter suites by category
        suites_to_run = [
            suite for suite in TEST_SUITES if suite["category"] in self.categories
        ]

        print(f"\nTest Suites to Run: {len(suites_to_run)}")
        for suite in suites_to_run:
            print(f"  - {suite['name']} ({suite['category']})")

        # Run each suite
        for suite in suites_to_run:
            result = self.run_test_suite(suite)
            self.results.append(result)

            # Stop if high priority test fails
            if suite["priority"] == "high" and not result["passed"]:
                print(
                    f"\n⚠️  Stopping execution - High priority test failed: {suite['name']}"
                )
                break

        self.end_time = datetime.now()

        # Generate comprehensive report
        report = self.generate_report()

        # Save report
        self.save_report(report)

        # Print summary
        self.print_summary(report)

        return report

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        total_duration = (self.end_time - self.start_time).total_seconds()

        # Calculate statistics
        total_suites = len(self.results)
        passed_suites = sum(1 for r in self.results if r["passed"])
        failed_suites = total_suites - passed_suites

        total_tests = sum(r.get("tests_run", 0) for r in self.results)
        passed_tests = sum(r.get("tests_passed", 0) for r in self.results)
        failed_tests = sum(r.get("tests_failed", 0) for r in self.results)

        # Group by category
        by_category = {}
        for category in self.categories:
            category_results = [r for r in self.results if r["category"] == category]
            by_category[category] = {
                "total": len(category_results),
                "passed": sum(1 for r in category_results if r["passed"]),
                "failed": sum(1 for r in category_results if not r["passed"]),
                "duration": sum(r["duration"] for r in category_results),
            }

        report = {
            "metadata": {
                "start_time": self.start_time.isoformat(),
                "end_time": self.end_time.isoformat(),
                "total_duration_seconds": round(total_duration, 2),
                "categories_tested": self.categories,
            },
            "summary": {
                "total_suites": total_suites,
                "passed_suites": passed_suites,
                "failed_suites": failed_suites,
                "suite_success_rate": (
                    round(passed_suites / total_suites * 100, 2)
                    if total_suites > 0
                    else 0
                ),
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "test_success_rate": (
                    round(passed_tests / total_tests * 100, 2) if total_tests > 0 else 0
                ),
            },
            "by_category": by_category,
            "suite_results": self.results,
            "recommendations": self.generate_recommendations(),
        }

        return report

    def generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []

        # Check for failures
        failures = [r for r in self.results if not r["passed"]]
        if failures:
            high_priority_failures = [f for f in failures if f["priority"] == "high"]
            if high_priority_failures:
                recommendations.append(
                    f"CRITICAL: Fix {len(high_priority_failures)} high-priority test failures immediately"
                )
            recommendations.append(
                f"Address {len(failures)} failing test suites before deployment"
            )

        # Check performance
        perf_results = [
            r for r in self.results if r["category"] == "performance" and r["passed"]
        ]
        if not perf_results:
            recommendations.append(
                "Run performance benchmarks to establish baseline metrics"
            )

        # Check security
        sec_results = [r for r in self.results if r["category"] == "security"]
        if not sec_results:
            recommendations.append(
                "Security tests must pass before production deployment"
            )
        elif any(not r["passed"] for r in sec_results):
            recommendations.append(
                "CRITICAL: Security vulnerabilities detected - fix immediately"
            )

        # Check coverage
        if len(self.results) < len(TEST_SUITES):
            recommendations.append(
                "Run complete test suite for comprehensive validation"
            )

        if not recommendations:
            recommendations.append("All tests passing - system ready for next phase")

        return recommendations

    def save_report(self, report: Dict[str, Any]):
        """Save test report to file"""
        timestamp = self.start_time.strftime("%Y%m%d_%H%M%S")
        report_file = Path(f"test_reports/integration_test_report_{timestamp}.json")

        # Create directory if needed
        report_file.parent.mkdir(exist_ok=True)

        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        print(f"\n📄 Report saved to: {report_file}")

        # Also save latest report
        latest_file = Path("test_reports/latest_integration_report.json")
        with open(latest_file, "w") as f:
            json.dump(report, f, indent=2)

    def print_summary(self, report: Dict[str, Any]):
        """Print test execution summary"""
        print("\n" + "=" * 80)
        print("📊 TEST EXECUTION SUMMARY")
        print("=" * 80)

        summary = report["summary"]
        print(
            f"\nTest Suites: {summary['passed_suites']}/{summary['total_suites']} passed "
            f"({summary['suite_success_rate']}%)"
        )
        print(
            f"Individual Tests: {summary['passed_tests']}/{summary['total_tests']} passed "
            f"({summary['test_success_rate']}%)"
        )
        print(
            f"Total Duration: {report['metadata']['total_duration_seconds']:.2f} seconds"
        )

        print("\nBy Category:")
        for category, stats in report["by_category"].items():
            print(
                f"  {category}: {stats['passed']}/{stats['total']} passed "
                f"(duration: {stats['duration']:.2f}s)"
            )

        print("\nRecommendations:")
        for i, rec in enumerate(report["recommendations"], 1):
            print(f"  {i}. {rec}")

        # Exit code based on results
        exit_code = 0 if summary["failed_suites"] == 0 else 1

        if exit_code == 0:
            print("\n✅ All test suites passed!")
        else:
            print(f"\n❌ {summary['failed_suites']} test suites failed")

        print("=" * 80)

        return exit_code


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Run LUKHAS AI integration tests")
    parser.add_argument(
        "-c",
        "--categories",
        nargs="+",
        choices=["integration", "performance", "security"],
        default=["integration", "performance", "security"],
        help="Test categories to run",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument(
        "--quick", action="store_true", help="Run only high priority tests"
    )

    args = parser.parse_args()

    # Adjust categories for quick mode
    if args.quick:
        # Filter TEST_SUITES to only high priority
        global TEST_SUITES
        TEST_SUITES = [s for s in TEST_SUITES if s["priority"] == "high"]
        print("🏃 Quick mode: Running only high-priority tests")

    # Create and run test runner
    runner = IntegrationTestRunner(verbose=args.verbose, categories=args.categories)

    report = runner.run_all_tests()

    # Exit with appropriate code
    sys.exit(0 if report["summary"]["failed_suites"] == 0 else 1)


if __name__ == "__main__":
    main()
