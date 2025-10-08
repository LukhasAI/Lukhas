"""Symbolic core bridge for plan_symbolic_core_preservation."""

from __future__ import annotations

from importlib import import_module
from typing import Callable

__all__ = ["plan_symbolic_core_preservation"]

for _module in (
    "lukhas_website.lukhas.core.symbolic_core",
    "candidate.core.symbolic_core",
    "core.symbolic_core",
):
    try:
        backend = import_module(_module)
        if hasattr(backend, "plan_symbolic_core_preservation"):
            plan_symbolic_core_preservation = getattr(backend, "plan_symbolic_core_preservation")  # type: ignore
            break
    except Exception:
        continue
else:
    def plan_symbolic_core_preservation(*args, **kwargs):  # type: ignore
        return {"status": "not_implemented"}
