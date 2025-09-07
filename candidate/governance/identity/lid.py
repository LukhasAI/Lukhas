"""Canonical Lambda ID helper (short name: lid)

This module provides small, well-tested helpers to normalize and validate
Lambda-style identifiers (Λambda ID). The implementation is intentionally
minimal and compatibility-focused: callers get a stable `lid` namespace with
`normalize` and `is_valid` helpers. Heavy transformations will be performed by
the AST/CST codemod later; this runtime helper keeps existing code working.
"""
import time
import streamlit as st

from __future__ import annotations

from typing import Any


def normalize_lid(value: str) -> str:
    """Return a canonical, short representation for a Lambda ID.

    This is intentionally conservative: trim whitespace, remove common
    Λambda prefixes, and lowercase the result. Do NOT attempt aggressive
    semantic rewrites here; the codemod will handle repo-wide renames.
    """
    s = value.strip()

    # Remove common visual prefixes used in older code
    for prefix in ("Λ", "LAMBDA:", "lambda:", "lid:"):
        if s.startswith(prefix):
            s = s[len(prefix) :].strip()

    # Conservative normalization
    return s.lower()


def is_valid_lid(value: Any) -> bool:
    """Return True when the provided value looks like a valid lid.

    Validity is intentionally permissive during migration: non-empty strings
    that yield a non-empty normalization are considered valid.
    """
    try:
        if not isinstance(value, str):
            return False
        norm = normalize_lid(value)
        return bool(norm)
    except Exception:
        return False


__all__ = ["is_valid_lid", "normalize_lid"]
