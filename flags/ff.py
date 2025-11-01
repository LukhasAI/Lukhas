"""Compatibility shim for ``flags.ff`` legacy import path."""

from __future__ import annotations

from lukhas_website.lukhas.flags.ff import Flags

__all__ = ["Flags"]
