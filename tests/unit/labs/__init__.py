"""Test package for labs modules.

This package shadows the top-level ``labs`` project package when unit tests
are collected. We ensure the repository root is inserted into ``sys.path`` so
imports resolve to the production modules.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
_repo_root_str = str(_REPO_ROOT)
if _repo_root_str not in sys.path:
    sys.path.insert(0, _repo_root_str)
