#!/usr/bin/env python3
"""
Test suite runner for LUKHAS AGI.

This script provides convenient test execution with various options.
"""

import subprocess
import sys


def run_tests(args=None):
    """Run the test suite with given arguments."""
    if args is None:
        args = []

    base_cmd = [sys.executable, "-m", "pytest"]

    # Add default arguments
    default_args = ["-v", "--tb=short", "--strict-markers"]

    cmd = base_cmd + default_args + args

    print(f"Running: {' '.join(cmd)}")
    return subprocess.run(cmd).returncode


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="LUKHAS AGI Test Suite Runner")
    parser.add_argument("--quick", action="store_true", help="Run quick tests only")
    parser.add_argument("--memory", action="store_true", help="Run memory tests only")
    parser.add_argument("--fold", action="store_true", help="Run fold tests only")
    parser.add_argument(
        "--integration", action="store_true", help="Run integration tests only"
    )
    parser.add_argument(
        "--coverage", action="store_true", help="Run with coverage report"
    )
    parser.add_argument("--parallel", action="store_true", help="Run tests in parallel")
    parser.add_argument("args", nargs="*", help="Additional pytest arguments")

    args = parser.parse_args()

    pytest_args = []

    if args.quick:
        pytest_args.extend(["-m", "not slow and not long_running"])

    if args.memory:
        pytest_args.extend(["-m", "memory"])

    if args.fold:
        pytest_args.extend(["-m", "fold"])

    if args.integration:
        pytest_args.extend(["-m", "integration"])

    if args.coverage:
        pytest_args.extend(["--cov=lukhas", "--cov-report=term-missing"])

    if args.parallel:
        pytest_args.extend(["-n", "auto"])

    # Add any additional arguments
    pytest_args.extend(args.args)

    return run_tests(pytest_args)


if __name__ == "__main__":
    sys.exit(main())
