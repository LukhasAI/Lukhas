"""Test configuration for labs package tests.

Ensures the real project package is importable even though this test
package shadows the top-level ``labs`` module name.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Add the repository root to the front of sys.path so imports like
# ``labs.bridge`` resolve to the actual project package instead of the
# tests' shadow package.
_REPO_ROOT = Path(__file__).resolve().parents[3]
_repo_root_str = str(_REPO_ROOT)
if _repo_root_str not in sys.path:
    sys.path.insert(0, _repo_root_str)
