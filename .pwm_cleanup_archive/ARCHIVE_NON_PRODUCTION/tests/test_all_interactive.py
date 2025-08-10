#!/usr/bin/env python3
"""
Quick launcher for LUKHAS AGI Interactive Test Suite

Usage:
    python test_all_interactive.py              # Run full interactive suite
    python test_all_interactive.py --quick      # Quick test of core modules only
    python test_all_interactive.py --fix-only   # Only run auto-fixes
    python test_all_interactive.py --report     # Generate report from last run
"""

import os
import subprocess
import sys
from pathlib import Path


def check_dependencies():
    """Check and install required dependencies"""
    try:
        import rich
    except ImportError:
        print("📦 Installing rich for interactive UI...")
        subprocess.run([sys.executable, "-m", "pip", "install", "rich"], check=True)

    try:
        import pytest
    except ImportError:
        print("📦 Installing pytest...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pytest"], check=True)


def main():
    """Main launcher"""
    # Ensure we're in the right directory
    os.chdir(Path(__file__).parent)

    # Check dependencies
    check_dependencies()

    # Parse simple arguments
    if len(sys.argv) > 1:
        if "--quick" in sys.argv:
            print("🚀 Running quick core module tests...")
            # Modify the test runner to only test core modules
            os.environ["LUKHAS_TEST_QUICK"] = "1"
        elif "--fix-only" in sys.argv:
            print("🔧 Running auto-fix mode only...")
            os.environ["LUKHAS_TEST_FIX_ONLY"] = "1"
        elif "--report" in sys.argv:
            print("📊 Generating report from last run...")
            os.environ["LUKHAS_TEST_REPORT_ONLY"] = "1"

    # Run the interactive test suite
    try:
        subprocess.run([sys.executable, "lukhas_interactive_test_suite.py"], check=True)
    except KeyboardInterrupt:
        print("\n\n👋 Test run cancelled by user")
        sys.exit(0)
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Test suite failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
