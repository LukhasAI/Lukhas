"""Executable tooling helpers for the Lukhas TODO system."""

from __future__ import annotations

from pathlib import Path

# ΛTAG: todo_scripts_package
SCRIPTS_ROOT = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS_ROOT.parent.parent

__all__ = ["SCRIPTS_ROOT", "REPO_ROOT"]
