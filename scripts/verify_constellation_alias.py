"""Simple script to verify constellation/constellation alias behavior without running pytest.

Run with the project's venv python:

    /path/to/.venv/bin/python scripts/verify_constellation_alias.py
"""

import os
import sys
import warnings

# Ensure the repository root is on sys.path so the local `lukhas` package can be imported
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from lukhas import branding_bridge as bb

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    tr = bb.get_trinity_description()
    cs = bb.get_constellation_context()

    print("constellation framework:", tr.get("framework"))
    print("constellation framework:", cs.get("framework"))

    # Check that deprecation warning was emitted
    dep_warnings = [x for x in w if issubclass(x.category, DeprecationWarning)]
    print("deprecation warnings emitted:", len(dep_warnings))

    assert tr.get("framework") == cs.get("framework"), "Framework strings must match"

print("Alias verification OK")
