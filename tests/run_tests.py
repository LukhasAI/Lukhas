#!/usr/bin/env python3
"""
LUKHAS Professional Test Runner
Generates timestamped artifacts: JUnit XML, HTML, JSON, coverage, and logs.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


class LUKHASTestRunner:
    """Comprehensive test runner for LUKHAS systems with professional reporting."""

    def __init__(self, project_root: Optional[str] = None):
        root = project_root or os.getcwd()
        self.project_root = Path(root)
        self.test_dir = self.project_root / "tests"
        # Base reports dir
        self.reports_root = self.project_root / "reports" / "test-runs"
        self.reports_root.mkdir(parents=True, exist_ok=True)
        # Timestamped run dir
        self.run_ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.run_dir = self.reports_root / self.run_ts
        # Create subdirs
        for sub in ("junit", "html", "json", "coverage", "logs"):
            (self.run_dir / sub).mkdir(parents=True, exist_ok=True)

        # Test categories (best-effort; files may be absent)
        self.test_suites: dict[str, dict[str, Any]] = {
            "unit": {
                "path": "unit/",
                "description": "Unit tests for individual components",
                "files": [
                    "test_consciousness.py",
                    "test_memory.py",
                    "test_guardian.py",
                    "test_symbolic.py",
                ],
            },
            "integration": {
                "path": "integration/",
                "description": "Integration tests for system interactions",
                "files": ["test_core_integration.py"],
            },
            "e2e": {
                "path": "e2e/",
                "description": "End-to-end workflow tests",
                "files": ["test_e2e_workflows.py"],
            },
            "security": {
                "path": "security/",
                "description": "Security and authentication tests",
                "files": ["test_enhanced_security.py"],
            },
            "api": {
                "path": "api/",
                "description": "API functionality tests",
                "files": ["test_enhanced_api.py"],
            },
            "governance": {
                "path": "governance/",
                "description": "Governance and compliance tests",
                "files": [
                    "test_governance.py",
                    "test_enhanced_governance.py",
                    "test_comprehensive_governance.py",
                ],
            },
        }

    def run_suite(
        self,
        suite_name: str,
        verbose: bool = False,
        coverage: bool = False,
        fast: bool = False,
        artifacts: bool = False,
        workers: Optional[str] = None,
    ) -> dict[str, Any]:
        """Run a specific test suite."""
        if suite_name not in self.test_suites:
            raise ValueError(f"Unknown test suite: {suite_name}")

        suite = self.test_suites[suite_name]
        suite_path = self.test_dir / suite["path"]

        # Build pytest arguments
        pytest_args: list[str] = []

        # Add test files (only those that exist)
        for test_file in suite["files"]:
            test_path = suite_path / test_file
            if test_path.exists():
                pytest_args.append(str(test_path))

        # If no explicit files found, fall back to the suite directory
        if not pytest_args and suite_path.exists():
            pytest_args.append(str(suite_path))

        if not pytest_args:
            print(f"No test files found for suite: {suite_name} → marking as skipped")
            return {
                "suite": suite_name,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "exit_code": 5,
                "status": "skipped",
                "reason": "no_tests_found",
                "artifacts": {},
            }

        # Add options
        if verbose:
            pytest_args.extend(["-v", "-s"])
        else:
            pytest_args.append("-q")

        # Coverage (disabled in fast mode for speed)
        if coverage and not fast:
            pytest_args.extend(
                [
                    "--cov=core",
                    "--cov=consciousness",
                    "--cov=memory",
                    "--cov=governance",
                    "--cov=emotion",
                    "--cov=bridge",
                    "--cov-report=term-missing",
                    f"--cov-report=html:{self.run_dir / 'coverage'}",
                ]
            )

        # Add result output only when artifacts=True and not in fast mode
        json_report = self.run_dir / "json" / f"{suite_name}.json"
        junit_xml = self.run_dir / "junit" / f"junit-{suite_name}.xml"
        html_report = self.run_dir / "html" / f"{suite_name}.html"
        log_file = self.run_dir / "logs" / f"{suite_name}.log"

        if artifacts and not fast:
            # JSON
            pytest_args.extend(["--json-report", f"--json-report-file={json_report}"])
            # JUnit XML
            pytest_args.extend(["--junitxml", str(junit_xml)])
            # HTML report (requires pytest-html)
            pytest_args.extend(["--html", str(html_report), "--self-contained-html"])
            # Log to file
            pytest_args.extend(["--log-file", str(log_file), "--log-file-level=INFO"])
        else:
            # Quieter logs in fast mode
            pytest_args.extend(["--log-cli-level=ERROR"])  # reduce console spam

        # Parallelization via pytest-xdist if requested and available
        if workers:
            try:
                import importlib.util as _ilus

                if _ilus.find_spec("xdist") is not None:
                    pytest_args.extend(["-n", str(workers)])
                else:
                    print(
                        "[runner] pytest-xdist not installed; ignoring --workers option"
                    )
            except Exception:
                print(
                    "[runner] Could not verify xdist availability; proceeding without -n"
                )

        # Run tests
        print(f"\n{'=' * 60}")
        print(
            f"Running {suite_name} tests: {suite['description']}"
            + (" [FAST]" if fast else "")
        )
        print(f"{'=' * 60}\n")

        # Import pytest lazily to allow --help without pytest installed
        import pytest

        exit_code = pytest.main(pytest_args)

        # Interpret exit code: 0=OK, 1=tests failed, 5=no tests collected
        status = (
            "passed" if exit_code == 0 else ("skipped" if exit_code == 5 else "failed")
        )

        results: dict[str, Any] = {
            "suite": suite_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "exit_code": exit_code,
            "status": status,
            "artifacts": (
                {
                    "json": str(json_report),
                    "junit": str(junit_xml),
                    "html": str(html_report),
                    "log": str(log_file),
                }
                if (artifacts and not fast)
                else {}
            ),
        }

        if (artifacts and not fast) and json_report.exists():
            with open(json_report) as f:
                json_results = json.load(f)
                results.update(json_results)

        return results

    def run_all(self, exclude: Optional[list[str]] = None, **kwargs) -> dict[str, Any]:
        """Run all test suites."""
        exclude = exclude or []
        all_results: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "suites": {},
        }

        for suite_name in self.test_suites:
            if suite_name in exclude:
                print(f"Skipping {suite_name} tests (excluded)")
                continue

            suite_results = self.run_suite(suite_name, **kwargs)
            all_results["suites"][suite_name] = suite_results

        # Summary
        total_suites = len(all_results["suites"])
        passed_suites = sum(
            1 for r in all_results["suites"].values() if r.get("status") == "passed"
        )
        failed_suites = sum(
            1 for r in all_results["suites"].values() if r.get("status") == "failed"
        )
        skipped_suites = sum(
            1 for r in all_results["suites"].values() if r.get("status") == "skipped"
        )
        error_suites = sum(
            1 for r in all_results["suites"].values() if r.get("status") == "error"
        )

        # Success rate among executed suites (exclude skipped). If none executed,
        # consider success.
        executed = passed_suites + failed_suites + error_suites
        success_rate = (passed_suites / executed) if executed > 0 else 1.0

        all_results["summary"] = {
            "total_suites": total_suites,
            "passed_suites": passed_suites,
            "failed_suites": failed_suites,
            "skipped_suites": skipped_suites,
            "error_suites": error_suites,
            "success_rate": success_rate,
        }

        # Write manifest
        manifest = {
            "run_dir": str(self.run_dir),
            "timestamp": all_results["timestamp"],
            "artifacts": {
                "junit": str(self.run_dir / "junit"),
                "html": str(self.run_dir / "html"),
                "json": str(self.run_dir / "json"),
                "coverage": str(self.run_dir / "coverage"),
                "logs": str(self.run_dir / "logs"),
            },
            "summary": all_results.get("summary", {}),
        }
        (self.run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))

        # Update symlink for latest
        latest = self.project_root / "reports" / "latest"
        try:
            if latest.is_symlink() or latest.exists():
                latest.unlink()
            latest.symlink_to(self.run_dir, target_is_directory=True)
        except Exception:
            # On platforms/filesystems where symlink isn't allowed, copy manifest
            (self.project_root / "reports").mkdir(exist_ok=True)
            (self.project_root / "reports" / "latest_manifest.json").write_text(
                json.dumps(manifest, indent=2)
            )

        return all_results

    def run_performance_tests(self, iterations: int = 3) -> dict[str, Any]:
        """Run performance benchmarks."""
        print(f"\n{'=' * 60}")
        print("Running Performance Benchmarks")
        print(f"{'=' * 60}\n")

        pytest_args = [
            "tests/integration/test_core_integration.py::TestSystemPerformance",
            "tests/e2e/test_e2e_workflows.py::TestPerformanceScenarios",
            "-v",
            "--benchmark-only",
            f"--benchmark-rounds={iterations}",
        ]

        import pytest

        exit_code = pytest.main(pytest_args)

        return {
            "status": "completed" if exit_code == 0 else "failed",
            "iterations": iterations,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def run_smoke_tests(
        self, fast: bool = False, workers: Optional[str] = None
    ) -> dict[str, Any]:
        """Run quick smoke tests."""
        print(f"\n{'=' * 60}")
        print("Running Smoke Tests (Quick Validation)" + (" [FAST]" if fast else ""))
        print(f"{'=' * 60}\n")

        smoke_tests = [
            "tests/unit/test_consciousness.py::TestConsciousnessCore::test_initialization",
            "tests/unit/test_memory.py::TestMemoryCore::test_initialization",
            "tests/unit/test_guardian.py::TestGuardianCore::test_initialization",
            "tests/api/test_enhanced_api.py::TestEnhancedAPI::test_health_endpoint",
            "tests/security/test_enhanced_security.py::TestEnhancedCrypto::test_aes_encryption",
        ]

        pytest_args = smoke_tests + ["-v"]
        import pytest

        if fast:
            # Quieter logging in fast mode
            pytest_args.extend(["--log-cli-level=ERROR"])  # reduce console chatter

        if workers:
            try:
                import importlib.util as _ilus

                if _ilus.find_spec("xdist") is not None:
                    pytest_args.extend(["-n", str(workers)])
                else:
                    print(
                        "[runner] pytest-xdist not installed; ignoring --workers option"
                    )
            except Exception:
                print(
                    "[runner] Could not verify xdist availability; proceeding without -n"
                )

        exit_code = pytest.main(pytest_args)

        return {
            "status": "passed" if exit_code == 0 else "failed",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def generate_report(self, results: dict[str, Any]) -> Path:
        """Generate a simple markdown summary for the run."""
        report_path = self.run_dir / "summary.md"

        with open(report_path, "w") as f:
            f.write("# LUKHAS Test Report\n\n")
            f.write(f"**Generated:** {results['timestamp']}\n\n")

            # Determine if this is an aggregated multi-suite result or a single-suite
            # result
            aggregated = isinstance(results.get("suites"), dict)

            if (
                aggregated
                and isinstance(results.get("summary"), dict)
                and "total_suites" in results["summary"]
            ):
                summary = results["summary"]
                f.write("## Summary\n\n")
                f.write(f"- Total Test Suites: {summary['total_suites']}\n")
                f.write(f"- Passed: {summary['passed_suites']}\n")
                f.write(f"- Failed: {summary['failed_suites']}\n")
                if "skipped_suites" in summary:
                    f.write(f"- Skipped: {summary['skipped_suites']}\n")
                if "error_suites" in summary:
                    f.write(f"- Errors: {summary['error_suites']}\n")
                f.write(f"- Success Rate: {summary['success_rate']:.1%}\n\n")

            f.write("## Test Suites\n\n")
            if aggregated:
                for suite_name, suite_results in results.get("suites", {}).items():
                    f.write(f"### {suite_name.upper()}\n\n")
                    f.write(f"**Status:** {suite_results.get('status', 'unknown')}\n")
                    if "summary" in suite_results:
                        test_summary = suite_results["summary"]
                        f.write(f"- Total Tests: {test_summary.get('total', 0)}\n")
                        f.write(f"- Passed: {test_summary.get('passed', 0)}\n")
                        f.write(f"- Failed: {test_summary.get('failed', 0)}\n")
                        f.write(f"- Skipped: {test_summary.get('skipped', 0)}\n")
                    f.write("\n")
            else:
                # Single suite result passed as results
                f.write("### SUITE\n\n")
                f.write(f"**Status:** {results.get('status', 'unknown')}\n")
                if isinstance(results.get("summary"), dict):
                    ts = results["summary"]
                    f.write(f"- Total Tests: {ts.get('total', 0)}\n")
                    f.write(f"- Passed: {ts.get('passed', 0)}\n")
                    f.write(f"- Failed: {ts.get('failed', 0)}\n")
                    f.write(f"- Skipped: {ts.get('skipped', 0)}\n")
                f.write("\n")

        print(f"\nSummary report: {report_path}")
        return report_path


def main() -> None:
    """Main test runner entry point."""
    parser = argparse.ArgumentParser(description="LUKHAS Comprehensive Test Runner")

    parser.add_argument(
        "command",
        choices=["all", "suite", "smoke", "performance"],
        help="Test command to run",
    )
    parser.add_argument(
        "--suite",
        choices=[
            "unit",
            "integration",
            "e2e",
            "security",
            "api",
            "governance",
        ],
        help="Specific test suite to run (with suite command)",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument(
        "--coverage",
        "-c",
        action="store_true",
        help="Generate coverage report",
    )
    parser.add_argument(
        "--exclude", nargs="+", help="Suites to exclude (with all command)"
    )
    parser.add_argument(
        "--report",
        "-r",
        action="store_true",
        help="Generate test report and artifacts",
    )
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Fast mode: disable heavy plugins, reports, and lower log verbosity",
    )
    parser.add_argument(
        "--workers",
        "-n",
        help="Run tests in parallel using pytest-xdist (e.g., -n auto or -n 4)",
    )

    args = parser.parse_args()

    # Initialize runner
    runner = LUKHASTestRunner()

    # Run appropriate command
    # Determine when to produce artifacts (CI or explicit --report, and not fast)
    produce_artifacts = bool(
        (not args.fast)
        and (args.report or os.getenv("CI") or os.getenv("GITHUB_ACTIONS"))
    )

    if args.command == "all":
        # In fast mode, ignore coverage/report flags for speed
        results = runner.run_all(
            exclude=args.exclude,
            verbose=args.verbose,
            coverage=(False if args.fast else args.coverage),
            fast=args.fast,
            artifacts=produce_artifacts,
            workers=args.workers,
        )
    elif args.command == "suite":
        if not args.suite:
            print("Error: --suite required with suite command")
            sys.exit(1)
        results = runner.run_suite(
            args.suite,
            verbose=args.verbose,
            coverage=(False if args.fast else args.coverage),
            fast=args.fast,
            artifacts=produce_artifacts,
            workers=args.workers,
        )
    elif args.command == "smoke":
        results = runner.run_smoke_tests(fast=args.fast, workers=args.workers)
    elif args.command == "performance":
        results = runner.run_performance_tests()
    else:
        print("Unknown command")
        sys.exit(2)

    # Generate report if requested
    if args.report and not args.fast and isinstance(results, dict):
        runner.generate_report(results)

    # Exit with appropriate code
    if isinstance(results, dict) and "summary" in results:
        failed = results["summary"].get("failed_suites", 0)
        errors = results["summary"].get("error_suites", 0)
        sys.exit(0 if (failed == 0 and errors == 0) else 1)
    else:
        status = results.get("status") if isinstance(results, dict) else None
        if status in ("passed", "skipped"):
            sys.exit(0)
        sys.exit(1)


if __name__ == "__main__":
    main()
