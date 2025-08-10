#!/usr/bin/env python3
"""
Test runner for Lukhas integration tests.
"""

import os
import sys

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Now import and run the integration tests
if __name__ == "__main__":
    try:
        # Just run the integration_tests.py file directly
        import runpy

        runpy.run_module("lukhas.core.integration_tests", run_name="__main__")

    except Exception as e:
        print(f"❌ Test runner failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
