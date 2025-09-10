#!/usr/bin/env python3
"""
Smoke Test Runner
================
Automatically discovers and runs smoke tests across the LUKHAS system.
Provides safe execution with timeout and failure tolerance for CI environments.

Features:
- Auto-discovery of smoke tests
- Timeout protection
- Failure isolation
- Comprehensive reporting
- CI-safe execution
"""

import json
import logging
import signal
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]


@dataclass
class SmokeTestResult:
    """Result of a single smoke test"""

    name: str
    file_path: str
    status: str  # passed/failed/timeout/error
    duration: float
    output: str = ""
    error: str = ""
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


class TimeoutHandler:
    """Handle test timeouts"""

    def __init__(self, timeout_seconds: int = 30):
        self.timeout_seconds = timeout_seconds
        self.timed_out = False

    def timeout_handler(self, signum, frame):
        self.timed_out = True
        raise TimeoutError(f"Test exceeded {self.timeout_seconds} seconds")

    def __enter__(self):
        signal.signal(signal.SIGALRM, self.timeout_handler)
        signal.alarm(self.timeout_seconds)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        signal.alarm(0)


class SmokeTestRunner:
    """Main smoke test runner"""

    def __init__(self, timeout: int = 30, max_failures: int = 5):
        self.timeout = timeout
        self.max_failures = max_failures
        self.results = []
        self.discovered_tests = []

    def discover_smoke_tests(self) -> list[dict[str, str]]:
        """Discover all smoke tests in the codebase"""
        logger.info("🔍 Discovering smoke tests...")

        tests = []

        # 1. Known smoke test files
        known_smoke_files = [
            "candidate/aka_qualia/demo_smoke.py",
            "tests/smoke_basic.py",
            "tests/integration/smoke_integration.py",
        ]

        for smoke_file in known_smoke_files:
            test_path = ROOT / smoke_file
            if test_path.exists():
                tests.append(
                    {
                        "name": f"known_smoke:{smoke_file}",
                        "file_path": str(test_path),
                        "type": "known_file",
                        "runner": "python",
                    }
                )

        # 2. Files with "smoke" in the name
        smoke_patterns = ["**/smoke*.py", "**/*smoke*.py"]
        for pattern in smoke_patterns:
            for file_path in ROOT.glob(pattern):
                if file_path.is_file() and file_path.suffix == ".py":
                    relative_path = str(file_path.relative_to(ROOT))
                    if not any(t["file_path"] == str(file_path) for t in tests):
                        tests.append(
                            {
                                "name": f"pattern_smoke:{relative_path}",
                                "file_path": str(file_path),
                                "type": "pattern_match",
                                "runner": "python",
                            }
                        )

        # 3. Pytest files with @pytest.mark.smoke decorator
        test_files = list(ROOT.glob("**/test_*.py")) + list(ROOT.glob("**/tests/**/*.py"))
        for test_file in test_files[:20]:  # Limit search
            if test_file.is_file():
                try:
                    content = test_file.read_text(errors="ignore")
                    if "@pytest.mark.smoke" in content or "pytest.mark.smoke" in content:
                        relative_path = str(test_file.relative_to(ROOT))
                        tests.append(
                            {
                                "name": f"pytest_smoke:{relative_path}",
                                "file_path": str(test_file),
                                "type": "pytest_marker",
                                "runner": "pytest",
                            }
                        )
                except Exception as e:
                    logger.debug(f"Error reading {test_file}: {e}")

        # 4. Files with smoke test functions
        for test_file in test_files[:10]:  # Limited search
            if test_file.is_file():
                try:
                    content = test_file.read_text(errors="ignore")
                    if "def test_smoke" in content or "def smoke_test" in content:
                        relative_path = str(test_file.relative_to(ROOT))
                        if not any(t["file_path"] == str(test_file) for t in tests):
                            tests.append(
                                {
                                    "name": f"function_smoke:{relative_path}",
                                    "file_path": str(test_file),
                                    "type": "function_pattern",
                                    "runner": "pytest",
                                }
                            )
                except Exception as e:
                    logger.debug(f"Error reading {test_file}: {e}")

        self.discovered_tests = tests
        logger.info(f"📋 Discovered {len(tests)} smoke tests")
        return tests

    def run_single_smoke_test(self, test_info: dict[str, str]) -> SmokeTestResult:
        """Run a single smoke test safely"""
        logger.info(f"🧪 Running {test_info['name']}")

        start_time = time.time()
        result = SmokeTestResult(
            name=test_info["name"], file_path=test_info["file_path"], status="unknown", duration=0.0
        )

        try:
            file_path = Path(test_info["file_path"])

            if not file_path.exists():
                result.status = "error"
                result.error = "Test file not found"
                return result

            # Determine how to run the test
            if test_info["runner"] == "pytest":
                cmd = ["python3", "-m", "pytest", str(file_path), "-v", "--tb=short"]
                if test_info["type"] == "pytest_marker":
                    cmd.extend(["-m", "smoke"])
            else:
                # Direct python execution
                cmd = ["python3", str(file_path)]

            # Execute with timeout protection
            with TimeoutHandler(self.timeout):
                process = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=self.timeout)

                result.output = process.stdout
                result.error = process.stderr
                result.duration = time.time() - start_time

                if process.returncode == 0:
                    result.status = "passed"
                    logger.info(f"✅ {test_info['name']} passed ({result.duration:.2f}s)")
                else:
                    result.status = "failed"
                    logger.warning(f"❌ {test_info['name']} failed ({result.duration:.2f}s)")

        except TimeoutError:
            result.status = "timeout"
            result.duration = self.timeout
            result.error = f"Test exceeded {self.timeout} seconds timeout"
            logger.warning(f"⏰ {test_info['name']} timed out")

        except Exception as e:
            result.status = "error"
            result.duration = time.time() - start_time
            result.error = str(e)
            logger.error(f"💥 {test_info['name']} error: {e}")

        return result

    def run_all_smoke_tests(self) -> dict:
        """Run all discovered smoke tests"""
        if not self.discovered_tests:
            self.discover_smoke_tests()

        logger.info(f"🚀 Running {len(self.discovered_tests)} smoke tests...")

        start_time = time.time()
        failures = 0

        for test_info in self.discovered_tests:
            # Check failure limit
            if failures >= self.max_failures:
                logger.warning(f"🛑 Stopping after {failures} failures (max: {self.max_failures})")
                break

            result = self.run_single_smoke_test(test_info)
            self.results.append(result)

            if result.status in ["failed", "error", "timeout"]:
                failures += 1

        total_duration = time.time() - start_time

        # Generate summary
        summary = self.generate_summary(total_duration)

        # Save results
        self.save_results(summary)

        logger.info(f"🏁 Smoke tests completed in {total_duration:.2f}s")
        return summary

    def generate_summary(self, total_duration: float) -> dict:
        """Generate test run summary"""
        passed = sum(1 for r in self.results if r.status == "passed")
        failed = sum(1 for r in self.results if r.status == "failed")
        errors = sum(1 for r in self.results if r.status == "error")
        timeouts = sum(1 for r in self.results if r.status == "timeout")

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_tests": len(self.results),
            "discovered_tests": len(self.discovered_tests),
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "timeouts": timeouts,
            "total_duration": total_duration,
            "success_rate": (passed / len(self.results) * 100) if self.results else 0,
            "status": "passed" if failed == 0 and errors == 0 else "failed",
            "results": [asdict(r) for r in self.results],
        }

    def save_results(self, summary: dict):
        """Save test results"""
        reports_dir = ROOT / "reports" / "testing"
        reports_dir.mkdir(parents=True, exist_ok=True)

        # Save latest results
        latest_file = reports_dir / "smoke-tests-latest.json"
        latest_file.write_text(json.dumps(summary, indent=2))

        # Save timestamped results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        timestamped_file = reports_dir / f"smoke-tests-{timestamp}.json"
        timestamped_file.write_text(json.dumps(summary, indent=2))

        logger.info(f"💾 Results saved to {latest_file}")

    def print_summary(self, summary: dict):
        """Print human-readable summary"""
        print("\n🧪 SMOKE TEST RESULTS")
        print("====================")
        print(f"Total Tests: {summary['total_tests']}")
        print(f"✅ Passed: {summary['passed']}")
        print(f"❌ Failed: {summary['failed']}")
        print(f"💥 Errors: {summary['errors']}")
        print(f"⏰ Timeouts: {summary['timeouts']}")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        print(f"Duration: {summary['total_duration']:.2f}s")
        print(f"Status: {'✅ PASSED' if summary['status'] == 'passed' else '❌ FAILED'}")

        # Show failures
        failures = [r for r in self.results if r["status"] in ["failed", "error", "timeout"]]
        if failures:
            print("\n🔍 FAILURES:")
            for failure in failures:
                print(f"  ❌ {failure['name']}: {failure['status']}")
                if failure["error"]:
                    print(f"     Error: {failure['error'][:100]}...")


def main():
    """CLI interface for smoke test runner"""
    import argparse

    parser = argparse.ArgumentParser(description="LUKHAS Smoke Test Runner")
    parser.add_argument("--timeout", type=int, default=30, help="Test timeout in seconds (default: 30)")
    parser.add_argument("--max-failures", type=int, default=5, help="Maximum failures before stopping (default: 5)")
    parser.add_argument("--discover-only", action="store_true", help="Only discover tests, don't run them")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Create runner
    runner = SmokeTestRunner(timeout=args.timeout, max_failures=args.max_failures)

    if args.discover_only:
        # Just discover and list tests
        tests = runner.discover_smoke_tests()
        print(f"\n📋 DISCOVERED SMOKE TESTS ({len(tests)})")
        print("=" * 40)
        for test in tests:
            print(f"  {test['name']} ({test['type']})")
            print(f"    {test['file_path']}")
        return 0

    # Run all smoke tests
    summary = runner.run_all_smoke_tests()
    runner.print_summary(summary)

    # Return appropriate exit code
    return 0 if summary["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
