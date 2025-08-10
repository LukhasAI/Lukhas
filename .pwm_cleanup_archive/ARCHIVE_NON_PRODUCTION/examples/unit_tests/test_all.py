"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: test_all.py
Advanced: test_all.py
Integration Date: 2025-05-31T07:55:27.757398
"""

"""
┌────────────────────────────────────────────────────────────────────────────┐
│ 📦 MODULE      : test_all.py                                               │
│ 🧾 DESCRIPTION : Runs all test_*.py files in trace/                        │
│ 🧩 TYPE        : Testing Utility          🔧 VERSION: v1.0.0                │
│ 🖋️ AUTHOR      : LUKHAS SYSTEMS           📅 UPDATED: 2025-05-05             │
├────────────────────────────────────────────────────────────────────────────┤
│ 📚 DEPENDENCIES:                                                           │
│   - Python 3.x                                                             │
│   - unittest                                                               │
│   - os, importlib                                                          │
└────────────────────────────────────────────────────────────────────────────┘
"""

import importlib.util
import os
import sys
import unittest


def discover_and_run_tests(directory="."):
    print(f"🧪 Scanning {directory} for test_*.py files...\n")
    suite = unittest.TestSuite()

    for filename in os.listdir(directory):
        if filename.startswith("test_") and filename.endswith(".py"):
            filepath = os.path.join(directory, filename)
            module_name = filename[:-3]  # Strip .py

            print(f"🔹 Found test: {filename}")
            spec = importlib.util.spec_from_file_location(module_name, filepath)
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(module))

    print("\n🚀 Running all collected tests...\n")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return result


if __name__ == "__main__":
    trace_dir = os.path.dirname(__file__)
    discover_and_run_tests(trace_dir)
