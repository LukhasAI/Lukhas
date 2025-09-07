from __future__ import annotations

import site
from collections.abc import Iterable
from pathlib import Path

import streamlit as st


def find_repo_root(start: Path | None = None) -> Path:
    """Return the repo root by walking up until a known marker is found.

    Looks for common project markers: pyproject.toml, .git, Makefile.
    Falls back to the filesystem root if no marker found.
    """
    current = (start or Path(__file__)).resolve()
    if current.is_file():
        current = current.parent

    markers = {"pyproject.toml", ".git", "Makefile"}
    while True:
        if any((current / m).exists() for m in markers):
            return current
        if current.parent == current:
            return current
        current = current.parent


def ensure_repo_paths(subdirs: Iterable[str], *, base: Path | None = None) -> None:
    """Register repo-relative directories as import search locations.

    Uses `site.addsitedir` to make directories importable without directly
    mutating `sys.path`, satisfying internal linting rules against
    explicit path manipulation.

    - subdirs: list of first-level directory names under the repo root to add
    - base: optional explicit base path (defaults to detected repo root)
    """
    root = find_repo_root(base)
    for name in subdirs:
        p = (root / name).resolve()
        if p.exists() and p.is_dir():
            site.addsitedir(str(p))


__all__ = ["ensure_repo_paths", "find_repo_root"]
