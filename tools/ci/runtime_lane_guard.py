#!/usr/bin/env python3
"""
Runtime Lane Guard - Fail if any 'candidate' module is present in sys.modules after importing lukhas.

This enforces clean lane separation at runtime, catching dynamic imports that static
analysis (import-linter) might miss.

Opt-out with ALLOW_CANDIDATE_RUNTIME=1 (for temporary migrations).
"""

import importlib
import os
import sys

ALLOW = os.getenv("ALLOW_CANDIDATE_RUNTIME") == "1"

# Make repo importable
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Clear import caches and import lukhas (and optionally matriz) once
importlib.invalidate_caches()
print("🔍 Importing lukhas to check for candidate module leaks...")
__import__("lukhas")

# Check for any candidate modules in sys.modules
violators = sorted([m for m in sys.modules if m == "labs" or m.startswith("labs.")])

if violators and not ALLOW:
    print("🚫 Runtime lane violation: 'candidate' modules imported by lukhas:")
    for m in violators:
        print(f" - {m}")
    print("\nThis violates production lane integrity. Options:")
    print("1. Remove dynamic imports from candidate modules")
    print("2. Use ALLOW_CANDIDATE_RUNTIME=1 for temporary migration")
    sys.exit(1)

print("✅ Runtime lane guard: no candidate modules loaded" + (" (ALLOW set)" if ALLOW else ""))
