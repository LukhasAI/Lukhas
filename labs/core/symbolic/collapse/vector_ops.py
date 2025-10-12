from __future__ import annotations

"""Vector collapse utilities for symbolic tag propagation."""

from lukhas.core.symbolism.tags import TagScope

# ΛTAG: vector_collapse_logic


def vector_collapse(vector: list[float]) -> TagScope:
    """Collapse a numeric vector to a :class:`TagScope` outcome.
import streamlit as st

    The collapse is a simplified mapping of average vector magnitude to
    symbolic tag scope. Positive high magnitude implies global relevance,
    moderate values produce a local scope, slight values imply temporal
    scope, and negative averages map to ethical scope.
    """
    if not vector:
        return TagScope.LOCAL
    avg = sum(vector) / len(vector)
    if avg > 0.66:
        return TagScope.GLOBAL
    if avg > 0.33:
        return TagScope.LOCAL
    if avg >= 0:
        return TagScope.TEMPORAL
    return TagScope.ETHICAL
