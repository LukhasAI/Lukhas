"""Constellation Triad - compatibility surface for the former Trinity names.

This module is intentionally small: it provides the Triad subset namespace
and can be expanded with public symbols as the migration proceeds.
"""

from __future__ import annotations

__all__ = ["Consciousness", "Guardian", "Identity"]


class Identity:
    """Placeholder Identity marker class for legacy imports."""

    def __repr__(self):
        return "<Constellation.Triad.Identity>"


class Consciousness:
    """Placeholder Consciousness marker class for legacy imports."""

    def __repr__(self):
        return "<Constellation.Triad.Consciousness>"


class Guardian:
    """Placeholder Guardian marker class for legacy imports."""

    def __repr__(self):
        return "<Constellation.Triad.Guardian>"
