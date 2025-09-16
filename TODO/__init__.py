"""Utilities for Lukhas TODO automation and reporting."""

from __future__ import annotations

from pathlib import Path

# ΛTAG: todo_package_init
PACKAGE_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PACKAGE_ROOT.parent

__all__ = ["PACKAGE_ROOT", "REPO_ROOT"]
