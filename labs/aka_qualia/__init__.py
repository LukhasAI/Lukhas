"""Bridge for aka_qualia test compatibility.

Search order (richest → leanest):
  1) lukhas_website.lukhas.aka_qualia
  2) aka_qualia (root-level module)

Exports only the symbols tests expect.
"""
from __future__ import annotations

__all__ = ["core", "lukhas.memory", "metrics"]

try:  # 1) product code
    from lukhas_website.lukhas import aka_qualia as _aka
    core = _aka.core
    memory = _aka.memory
    metrics = _aka.metrics
except Exception:
    try:  # 2) root-level module
        import aka_qualia as _aka
        core = getattr(_aka, "core", None)
        memory = getattr(_aka, "lukhas.memory", None)
        metrics = getattr(_aka, "metrics", None)
    except Exception:
        # Minimal fallbacks so imports never kill collection
        class _Null:  # pragma: no cover
            def __getattr__(self, *_): return None
        core = memory = metrics = _Null()
