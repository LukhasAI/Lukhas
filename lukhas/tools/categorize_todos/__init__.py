"""Bridge for categorize_todos used by tests."""

from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module

__all__ = ["CategorizedTodo", "categorize_todos"]

for _module in (
    "tools.categorize_todos",
    "lukhas_website.lukhas.tools.categorize_todos",
    "candidate.tools.categorize_todos",
):
    try:
        backend = import_module(_module)
        if hasattr(backend, "categorize_todos") and hasattr(backend, "CategorizedTodo"):
            categorize_todos = getattr(backend, "categorize_todos")  # type: ignore
            CategorizedTodo = getattr(backend, "CategorizedTodo")  # type: ignore
            break
    except Exception:
        continue
else:

    @dataclass
    class CategorizedTodo:
        text: str
        category: str = "general"

    def categorize_todos(items):  # type: ignore
        return [CategorizedTodo(text=item, category="general") for item in items]
