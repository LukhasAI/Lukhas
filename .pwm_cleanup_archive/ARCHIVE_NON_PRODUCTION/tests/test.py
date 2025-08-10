#!/usr/bin/env python3
"""
LUKHAS AGI Test Suite
====================

Unified command-line interface for all system testing and diagnostics.
"""

import argparse
import importlib
import json
import os
import subprocess
import sys
import time
import unittest
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))


@dataclass
class TestResult:
    """Enhanced test result with timing and metadata."""

    name: str
    status: str  # 'PASS', 'FAIL', 'WARN', 'SKIP', 'ERROR'
    message: str
    duration: float
    details: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime] = None


class ModernUI:
    """Modern terminal UI with rich formatting and progress indicators."""

    # Color scheme
    COLORS = {
        "header": "\033[96m",  # Cyan
        "success": "\033[92m",  # Green
        "warning": "\033[93m",  # Yellow
        "error": "\033[91m",  # Red
        "info": "\033[94m",  # Blue
        "bold": "\033[1m",  # Bold
        "dim": "\033[2m",  # Dim
        "reset": "\033[0m",  # Reset
        "purple": "\033[95m",  # Purple
        "underline": "\033[4m",  # Underline
    }

    # Icons
    ICONS = {
        "success": "✅",
        "error": "❌",
        "warning": "⚠️",
        "info": "ℹ️",
        "running": "🔄",
        "rocket": "🚀",
        "brain": "🧠",
        "gear": "⚙️",
        "shield": "🛡️",
        "chart": "📊",
        "fire": "🔥",
        "lightning": "⚡",
        "star": "⭐",
    }

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        try:
            self.terminal_width = os.get_terminal_size().columns
        except (OSError, AttributeError):
            self.terminal_width = 80

    def print_header(self, title: str, subtitle: str = ""):
        """Print a styled header."""
        width = self.terminal_width
        title_line = f"{self.ICONS['brain']} {title}"

        print(f"\n{self.COLORS['header']}{self.COLORS['bold']}")
        print("═" * width)
        print(f"{title_line:^{width}}")
        if subtitle:
            print(f"{subtitle:^{width}}")
        print("═" * width)
        print(self.COLORS["reset"])

    def print_section(self, title: str, icon: str = "gear"):
        """Print a section header."""
        icon_char = self.ICONS.get(icon, "•")
        print(
            f"\n{self.COLORS['info']}{self.COLORS['bold']}{icon_char} {title}{self.COLORS['reset']}"
        )
        print(f"{self.COLORS['dim']}{'─' * (len(title) + 4)}{self.COLORS['reset']}")

    def print_result(self, result: TestResult):
        """Print a test result with formatting."""
        status_colors = {
            "PASS": self.COLORS["success"],
            "FAIL": self.COLORS["error"],
            "WARN": self.COLORS["warning"],
            "SKIP": self.COLORS["dim"],
            "ERROR": self.COLORS["error"],
        }

        status_icons = {
            "PASS": self.ICONS["success"],
            "FAIL": self.ICONS["error"],
            "WARN": self.ICONS["warning"],
            "SKIP": "⏭️",
            "ERROR": self.ICONS["error"],
        }

        color = status_colors.get(result.status, "")
        icon = status_icons.get(result.status, "•")
        duration_str = f"({result.duration:.2f}s)" if result.duration else ""

        print(
            f"  {color}{icon} {result.name:<40} {result.status:<6} {duration_str}{self.COLORS['reset']}"
        )

        if result.message and (self.verbose or result.status in ["FAIL", "ERROR"]):
            print(f"    {self.COLORS['dim']}└─ {result.message}{self.COLORS['reset']}")

    def print_progress_bar(self, current: int, total: int, prefix: str = "Progress"):
        """Print an animated progress bar."""
        if total == 0:
            return

        percent = (current / total) * 100
        filled_length = int(self.terminal_width * current // total // 2)
        bar = "█" * filled_length + "░" * (self.terminal_width // 2 - filled_length)

        print(
            f"\r{prefix}: |{bar}| {percent:.1f}% ({current}/{total})",
            end="",
            flush=True,
        )
        if current == total:
            print()  # New line when complete

    def print_summary(self, results: List[TestResult], total_duration: float):
        """Print a comprehensive test summary."""
        passed = len([r for r in results if r.status == "PASS"])
        failed = len([r for r in results if r.status == "FAIL"])
        warnings = len([r for r in results if r.status == "WARN"])
        errors = len([r for r in results if r.status == "ERROR"])
        skipped = len([r for r in results if r.status == "SKIP"])
        total = len(results)

        print(f"\n{self.COLORS['header']}{self.COLORS['bold']}")
        print("═" * self.terminal_width)
        print(f"{'TEST SUMMARY':^{self.terminal_width}}")
        print("═" * self.terminal_width)
        print(self.COLORS["reset"])

        # Results grid
        print(
            f"{self.COLORS['success']}{self.ICONS['success']} Passed:   {passed:>4}{self.COLORS['reset']}"
        )
        print(
            f"{self.COLORS['error']}{self.ICONS['error']} Failed:   {failed:>4}{self.COLORS['reset']}"
        )
        if warnings > 0:
            print(
                f"{self.COLORS['warning']}{self.ICONS['warning']} Warnings: {warnings:>4}{self.COLORS['reset']}"
            )
        if errors > 0:
            print(
                f"{self.COLORS['error']}{self.ICONS['error']} Errors:   {errors:>4}{self.COLORS['reset']}"
            )
        if skipped > 0:
            print(f"{self.COLORS['dim']}⏭️ Skipped:  {skipped:>4}{self.COLORS['reset']}")

        print(f"{self.COLORS['dim']}{'─' * 20}{self.COLORS['reset']}")
        print(f"{self.COLORS['bold']}Total:    {total:>4}{self.COLORS['reset']}")
        print(
            f"{self.COLORS['dim']}Duration: {total_duration:.2f}s{self.COLORS['reset']}"
        )

        # Overall status
        success_rate = (passed / total * 100) if total > 0 else 0
        if failed == 0 and errors == 0:
            status_msg = f"{self.ICONS['success']} ALL TESTS PASSED"
            status_color = self.COLORS["success"]
        elif success_rate >= 80:
            status_msg = f"{self.ICONS['warning']} MOSTLY PASSING ({success_rate:.0f}%)"
            status_color = self.COLORS["warning"]
        else:
            status_msg = f"{self.ICONS['error']} ISSUES DETECTED ({success_rate:.0f}%)"
            status_color = self.COLORS["error"]

        print(
            f"\n{status_color}{self.COLORS['bold']}{status_msg:^{self.terminal_width}}{self.COLORS['reset']}"
        )
        print(
            f"{self.COLORS['dim']}{'═' * self.terminal_width}{self.COLORS['reset']}\n"
        )


class EnhancedTestRunner:
    """Enhanced test runner with comprehensive coverage."""

    def __init__(self, ui: ModernUI):
        self.ui = ui
        self.results: List[TestResult] = []

    def run_test_module(self, module_name: str, test_name: str = None) -> TestResult:
        """Run a test module and return results."""
        start_time = time.time()
        test_display_name = test_name or module_name.split(".")[-1]

        try:
            # Try to set up test mocks before importing
            try:
                import tests.test_mocks

                tests.test_mocks.setup_test_mocks()
            except ImportError:
                pass  # Mocks not available, continue anyway

            module = importlib.import_module(module_name)

            if hasattr(module, "main"):
                result = module.main()
                status = "PASS" if result == 0 else "FAIL"
                message = (
                    "Execution completed" if result == 0 else f"Exit code: {result}"
                )
            elif hasattr(module, "run_tests"):
                result = module.run_tests()
                status = "PASS" if result else "FAIL"
                message = "Tests completed" if result else "Some tests failed"
            else:
                # Try to run as unittest
                loader = unittest.TestLoader()
                suite = loader.loadTestsFromModule(module)
                runner = unittest.TextTestRunner(
                    verbosity=0, stream=open(os.devnull, "w")
                )
                test_result = runner.run(suite)

                if test_result.wasSuccessful():
                    status = "PASS"
                    message = f"All {test_result.testsRun} tests passed"
                else:
                    status = "FAIL"
                    message = f"{len(test_result.failures)} failures, {len(test_result.errors)} errors"

        except ImportError as e:
            status = "SKIP"
            message = f"Module not found: {e}"
        except Exception as e:
            status = "ERROR"
            message = f"Execution error: {e}"

        duration = time.time() - start_time
        return TestResult(
            name=test_display_name,
            status=status,
            message=message,
            duration=duration,
            timestamp=datetime.now(),
        )

    def run_file_test(self, file_path: Path) -> TestResult:
        """Run a test file directly."""
        start_time = time.time()

        try:
            result = subprocess.run(
                [sys.executable, str(file_path)],
                capture_output=True,
                text=True,
                timeout=30,
            )

            status = "PASS" if result.returncode == 0 else "FAIL"
            message = (
                "File executed successfully"
                if result.returncode == 0
                else f"Exit code: {result.returncode}"
            )

            if result.stderr and status == "FAIL":
                message += f" - {result.stderr.strip()[:100]}"

        except subprocess.TimeoutExpired:
            status = "FAIL"
            message = "Test timed out (30s)"
        except Exception as e:
            status = "ERROR"
            message = f"Execution error: {e}"

        duration = time.time() - start_time
        return TestResult(
            name=file_path.stem,
            status=status,
            message=message,
            duration=duration,
            timestamp=datetime.now(),
        )


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(
        description="LUKHAS AGI Testing & Diagnostics Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test.py                    # Quick system check with modern UI
  python test.py --full             # Comprehensive testing suite
  python test.py --core             # Test core modules only
  python test.py --integration      # Test integration modules
  python test.py --security        # Run security tests
  python test.py --performance      # Run performance benchmarks
  python test.py --dashboard        # Visual health dashboard
  python test.py --fix              # Attempt to fix common issues
  python test.py --modules          # Check module imports
  python test.py --coverage         # Generate test coverage report
  python test.py --watch            # Watch mode - rerun on file changes
  python test.py --save report.json # Save results to file
  python test.py --parallel         # Run tests in parallel
        """,
    )

    # Test type options
    parser.add_argument(
        "--full", action="store_true", help="Run comprehensive test suite"
    )
    parser.add_argument("--core", action="store_true", help="Test core modules only")
    parser.add_argument(
        "--integration", action="store_true", help="Test integration modules"
    )
    parser.add_argument("--security", action="store_true", help="Run security tests")
    parser.add_argument(
        "--performance", action="store_true", help="Run performance benchmarks"
    )
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")

    # Tool options
    parser.add_argument(
        "--dashboard", action="store_true", help="Show visual system dashboard"
    )
    parser.add_argument(
        "--fix", action="store_true", help="Attempt to fix common issues"
    )
    parser.add_argument(
        "--modules", action="store_true", help="Run module import diagnostics"
    )
    parser.add_argument(
        "--coverage", action="store_true", help="Generate test coverage report"
    )
    parser.add_argument(
        "--watch", action="store_true", help="Watch mode - rerun on changes"
    )

    # Output options
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--quiet", "-q", action="store_true", help="Minimal output")
    parser.add_argument("--save", type=str, help="Save results to JSON file")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument(
        "--no-color", action="store_true", help="Disable colored output"
    )

    # Performance options
    parser.add_argument("--parallel", action="store_true", help="Run tests in parallel")
    parser.add_argument(
        "--timeout", type=int, default=60, help="Test timeout in seconds"
    )
    parser.add_argument("--filter", type=str, help="Filter tests by name pattern")

    args = parser.parse_args()

    # Initialize UI
    ui = ModernUI(verbose=args.verbose and not args.quiet)
    if args.no_color:
        # Disable colors
        for key in ui.COLORS:
            ui.COLORS[key] = ""

    start_time = time.time()

    # Determine test mode
    test_modes = []
    try:
        test_modes = [
            args.full,
            args.core,
            args.integration,
            args.security,
            args.performance,
            args.unit,
            args.dashboard,
            args.fix,
            args.modules,
            args.coverage,
            args.watch,
        ]
    except AttributeError:
        # Handle missing attributes gracefully
        test_modes = [
            getattr(args, attr, False)
            for attr in [
                "full",
                "core",
                "integration",
                "security",
                "performance",
                "unit",
                "dashboard",
                "fix",
                "modules",
                "coverage",
                "watch",
            ]
        ]

    if not any(test_modes):
        # Default: Quick system check with modern UI
        return run_quick_check(ui, args, start_time)

    # Enhanced test runner
    runner = EnhancedTestRunner(ui)

    # Route to appropriate test mode
    if getattr(args, "dashboard", False):
        return run_dashboard_mode(ui, args)
    elif getattr(args, "fix", False):
        return run_fix_mode(ui, args)
    elif getattr(args, "modules", False):
        return run_module_diagnostics(ui, args)
    elif getattr(args, "coverage", False):
        return run_coverage_analysis(ui, args)
    elif getattr(args, "watch", False):
        return run_watch_mode(ui, args)
    elif getattr(args, "core", False):
        return run_core_tests(ui, runner, args, start_time)
    elif getattr(args, "integration", False):
        return run_integration_tests(ui, runner, args, start_time)
    elif getattr(args, "security", False):
        return run_security_tests(ui, runner, args, start_time)
    elif getattr(args, "performance", False):
        return run_performance_tests(ui, runner, args, start_time)
    elif getattr(args, "unit", False):
        return run_unit_tests(ui, runner, args, start_time)
    elif getattr(args, "full", False):
        return run_comprehensive_tests(ui, runner, args, start_time)

    return 0


def run_quick_check(ui: ModernUI, args, start_time: float) -> int:
    """Run quick system health check."""
    ui.print_header("LUKHAS AGI Quick Health Check", "Fast System Diagnostics")

    runner = EnhancedTestRunner(ui)
    results = []

    # Essential checks
    essential_tests = [
        ("tools.test_runner_professional", "Core Test Runner"),
        ("tools.system_health_checker", "System Health"),
        ("tools.module_diagnostics", "Module Status"),
    ]

    ui.print_section("Essential System Checks", "rocket")

    for i, (module_name, test_name) in enumerate(essential_tests):
        ui.print_progress_bar(i, len(essential_tests), "Checking")
        result = runner.run_test_module(module_name, test_name)
        results.append(result)
        ui.print_result(result)

    ui.print_progress_bar(len(essential_tests), len(essential_tests), "Complete")

    total_duration = time.time() - start_time
    ui.print_summary(results, total_duration)

    # Show missing dependencies
    print_dependency_help(ui)

    # Save results if requested
    if args.save:
        save_results(results, args.save, total_duration)

    # Return based on results
    failed = len([r for r in results if r.status in ["FAIL", "ERROR"]])
    return 0 if failed == 0 else 1


def run_comprehensive_tests(
    ui: ModernUI, runner: EnhancedTestRunner, args, start_time: float
) -> int:
    """Run comprehensive test suite."""
    ui.print_header("LUKHAS AGI Comprehensive Test Suite", "Full System Analysis")

    all_results = []

    # Core tests
    ui.print_section("Core System Tests", "gear")
    core_results = run_test_category(runner, get_core_test_modules(), ui, args)
    all_results.extend(core_results)

    # Integration tests
    ui.print_section("Integration Tests", "lightning")
    integration_results = run_test_category(
        runner, get_integration_test_modules(), ui, args
    )
    all_results.extend(integration_results)

    # Security tests
    ui.print_section("Security Tests", "shield")
    security_results = run_test_category(runner, get_security_test_modules(), ui, args)
    all_results.extend(security_results)

    # Performance tests
    ui.print_section("Performance Tests", "fire")
    performance_results = run_test_category(
        runner, get_performance_test_modules(), ui, args
    )
    all_results.extend(performance_results)

    # File-based tests
    ui.print_section("File-based Tests", "chart")
    file_results = run_file_tests(runner, ui, args)
    all_results.extend(file_results)

    total_duration = time.time() - start_time
    ui.print_summary(all_results, total_duration)

    if args.save:
        save_results(all_results, args.save, total_duration)

    failed = len([r for r in all_results if r.status in ["FAIL", "ERROR"]])
    return 0 if failed == 0 else 1


def run_core_tests(
    ui: ModernUI, runner: EnhancedTestRunner, args, start_time: float
) -> int:
    """Run core module tests only."""
    ui.print_header("Core Module Tests", "Essential System Components")

    ui.print_section("Core System Tests", "gear")
    results = run_test_category(runner, get_core_test_modules(), ui, args)

    total_duration = time.time() - start_time
    ui.print_summary(results, total_duration)

    if args.save:
        save_results(results, args.save, total_duration)

    failed = len([r for r in results if r.status in ["FAIL", "ERROR"]])
    return 0 if failed == 0 else 1


def run_integration_tests(
    ui: ModernUI, runner: EnhancedTestRunner, args, start_time: float
) -> int:
    """Run integration tests only."""
    ui.print_header("Integration Tests", "Module Interconnection Analysis")

    ui.print_section("Integration Tests", "lightning")
    results = run_test_category(runner, get_integration_test_modules(), ui, args)

    total_duration = time.time() - start_time
    ui.print_summary(results, total_duration)

    if args.save:
        save_results(results, args.save, total_duration)

    failed = len([r for r in results if r.status in ["FAIL", "ERROR"]])
    return 0 if failed == 0 else 1


def run_security_tests(
    ui: ModernUI, runner: EnhancedTestRunner, args, start_time: float
) -> int:
    """Run security tests only."""
    ui.print_header("Security Tests", "System Security Analysis")

    ui.print_section("Security Tests", "shield")
    results = run_test_category(runner, get_security_test_modules(), ui, args)

    total_duration = time.time() - start_time
    ui.print_summary(results, total_duration)

    if args.save:
        save_results(results, args.save, total_duration)

    failed = len([r for r in results if r.status in ["FAIL", "ERROR"]])
    return 0 if failed == 0 else 1


def run_performance_tests(
    ui: ModernUI, runner: EnhancedTestRunner, args, start_time: float
) -> int:
    """Run performance tests only."""
    ui.print_header("Performance Tests", "System Performance Analysis")

    ui.print_section("Performance Tests", "fire")
    results = run_test_category(runner, get_performance_test_modules(), ui, args)

    total_duration = time.time() - start_time
    ui.print_summary(results, total_duration)

    if args.save:
        save_results(results, args.save, total_duration)

    failed = len([r for r in results if r.status in ["FAIL", "ERROR"]])
    return 0 if failed == 0 else 1


def run_unit_tests(
    ui: ModernUI, runner: EnhancedTestRunner, args, start_time: float
) -> int:
    """Run unit tests only."""
    ui.print_header("Unit Tests", "Individual Component Testing")

    ui.print_section("Unit Tests", "gear")
    # Find and run unittest-style tests
    test_files = list(PROJECT_ROOT.glob("**/test_*.py")) + list(
        PROJECT_ROOT.glob("**/*_test.py")
    )
    test_files = [f for f in test_files if "venv" not in str(f)][:20]  # Limit for demo

    results = []
    for i, test_file in enumerate(test_files):
        if args.filter and args.filter not in test_file.name:
            continue

        ui.print_progress_bar(i, len(test_files), "Testing")
        result = runner.run_file_test(test_file)
        results.append(result)
        ui.print_result(result)

    ui.print_progress_bar(len(test_files), len(test_files), "Complete")

    total_duration = time.time() - start_time
    ui.print_summary(results, total_duration)

    if args.save:
        save_results(results, args.save, total_duration)

    failed = len([r for r in results if r.status in ["FAIL", "ERROR"]])
    return 0 if failed == 0 else 1


def run_dashboard_mode(ui: ModernUI, args) -> int:
    """Run system dashboard."""
    try:
        from tools.system_dashboard import SystemDashboard

        dashboard = SystemDashboard()
        health = dashboard.run_dashboard()
        return 0 if health == "OPERATIONAL" else 1
    except ImportError as e:
        ui.print_result(TestResult("Dashboard", "ERROR", f"Import error: {e}", 0.0))
        return 1


def run_fix_mode(ui: ModernUI, args) -> int:
    """Run fix mode."""
    try:
        from tools.module_health_fixer import main as fix_main

        fix_main()
        return 0
    except ImportError as e:
        ui.print_result(TestResult("Fix", "ERROR", f"Import error: {e}", 0.0))
        return 1


def run_module_diagnostics(ui: ModernUI, args) -> int:
    """Run module diagnostics."""
    try:
        from tools.module_diagnostics import main as diag_main

        diag_main()
        return 0
    except ImportError as e:
        ui.print_result(
            TestResult("Module Diagnostics", "ERROR", f"Import error: {e}", 0.0)
        )
        return 1


def run_coverage_analysis(ui: ModernUI, args) -> int:
    """Run test coverage analysis."""
    ui.print_header("Test Coverage Analysis", "Code Coverage Report")

    try:
        # Run coverage analysis
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "coverage",
                "run",
                "--source=.",
                "-m",
                "pytest",
                "tests/",
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )

        if result.returncode == 0:
            # Generate coverage report
            coverage_result = subprocess.run(
                [sys.executable, "-m", "coverage", "report"],
                capture_output=True,
                text=True,
            )

            print(coverage_result.stdout)
            return 0
        else:
            print(f"Coverage analysis failed: {result.stderr}")
            return 1

    except subprocess.TimeoutExpired:
        print("Coverage analysis timed out")
        return 1
    except Exception as e:
        print(f"Coverage analysis error: {e}")
        return 1


def run_watch_mode(ui: ModernUI, args) -> int:
    """Run in watch mode."""
    ui.print_header("Watch Mode", "Monitoring File Changes")

    print("Watch mode not yet implemented. Use --full for comprehensive testing.")
    return 0


def run_test_category(
    runner: EnhancedTestRunner, test_modules: List[Tuple[str, str]], ui: ModernUI, args
) -> List[TestResult]:
    """Run a category of tests with progress tracking."""
    results = []

    for i, (module_name, test_name) in enumerate(test_modules):
        if args.filter and args.filter not in test_name.lower():
            continue

        ui.print_progress_bar(i, len(test_modules), "Progress")
        result = runner.run_test_module(module_name, test_name)
        results.append(result)
        ui.print_result(result)

        if not args.verbose and result.status in ["FAIL", "ERROR"]:
            break  # Stop on first failure unless verbose

    ui.print_progress_bar(len(test_modules), len(test_modules), "Complete")
    return results


def run_file_tests(runner: EnhancedTestRunner, ui: ModernUI, args) -> List[TestResult]:
    """Run file-based tests."""
    test_files = list(PROJECT_ROOT.glob("tests/active/*.py"))
    test_files += list(PROJECT_ROOT.glob("quantum/test_*.py"))

    results = []
    for i, test_file in enumerate(test_files[:10]):  # Limit for demo
        if args.filter and args.filter not in test_file.name:
            continue

        ui.print_progress_bar(i, len(test_files), "File Tests")
        result = runner.run_file_test(test_file)
        results.append(result)
        ui.print_result(result)

    ui.print_progress_bar(len(test_files), len(test_files), "Complete")
    return results


def get_core_test_modules() -> List[Tuple[str, str]]:
    """Get core system test modules."""
    return [
        ("tools.test_runner_professional", "Professional Test Runner"),
        ("tools.system_health_checker", "System Health Checker"),
        ("tools.module_diagnostics", "Module Diagnostics"),
        ("tools.advanced_agi_test_suite", "Advanced AGI Tests"),
        ("core.test_autotest_system", "Core Autotest System"),
    ]


def get_integration_test_modules() -> List[Tuple[str, str]]:
    """Get integration test modules."""
    return [
        ("integration.integration_tests", "Integration Test Suite"),
        ("integration.simple_lukhas_integration_test", "Simple Integration Test"),
        ("tools.import_structure_validator", "Import Structure Validator"),
        ("tools.dependency_validator", "Dependency Validator"),
    ]


def get_security_test_modules() -> List[Tuple[str, str]]:
    """Get security test modules."""
    return [
        ("tools.validate_lambda_bot_setup", "Lambda Bot Security"),
        ("scripts.security_cleanup_test", "Security Cleanup"),
        ("tests.hold.simple_security_test", "Simple Security Test"),
    ]


def get_performance_test_modules() -> List[Tuple[str, str]]:
    """Get performance test modules."""
    return [
        ("memory.core_memory.remvix.streamlit_mesh_test", "Memory Mesh Test"),
        ("tools.complexity_audit", "Complexity Audit"),
        ("learning.reinforcement_learning_rpc_test", "RL Performance Test"),
    ]


def check_missing_dependencies() -> List[str]:
    """Check for missing test dependencies."""
    missing = []

    dependencies = [
        ("torch", "PyTorch for ML tests"),
        ("joblib", "Memory caching for memory tests"),
        ("safety", "Security vulnerability scanning"),
        ("bandit", "Code security analysis"),
        ("pytest", "Advanced test framework"),
    ]

    for module, description in dependencies:
        try:
            importlib.import_module(module)
        except ImportError:
            missing.append(f"{module} - {description}")

    return missing


def print_dependency_help(ui: ModernUI):
    """Print helpful information about missing dependencies."""
    missing = check_missing_dependencies()

    if missing:
        ui.print_section("Missing Dependencies", "warning")
        print(
            f"  {ui.COLORS['warning']}⚠️  Some test dependencies are missing:{ui.COLORS['reset']}"
        )

        for dep in missing:
            print(f"    {ui.COLORS['dim']}• {dep}{ui.COLORS['reset']}")

        print(
            f"\n  {ui.COLORS['info']}💡 To install missing dependencies:{ui.COLORS['reset']}"
        )
        print(
            f"    {ui.COLORS['dim']}python3 scripts/install_test_deps.py{ui.COLORS['reset']}"
        )
        print(
            f"    {ui.COLORS['dim']}pip install -r requirements-test.txt{ui.COLORS['reset']}"
        )


def save_results(results: List[TestResult], filename: str, total_duration: float):
    """Save test results to JSON file."""
    output = {
        "timestamp": datetime.now().isoformat(),
        "total_duration": total_duration,
        "summary": {
            "total": len(results),
            "passed": len([r for r in results if r.status == "PASS"]),
            "failed": len([r for r in results if r.status == "FAIL"]),
            "errors": len([r for r in results if r.status == "ERROR"]),
            "skipped": len([r for r in results if r.status == "SKIP"]),
            "warnings": len([r for r in results if r.status == "WARN"]),
        },
        "missing_dependencies": check_missing_dependencies(),
        "results": [
            {
                "name": r.name,
                "status": r.status,
                "message": r.message,
                "duration": r.duration,
                "timestamp": r.timestamp.isoformat() if r.timestamp else None,
            }
            for r in results
        ],
    }

    with open(filename, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\n📄 Results saved to: {filename}")


if __name__ == "__main__":
    sys.exit(main())
