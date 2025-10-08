"""Bridge for legacy TODO module imports."""

from __future__ import annotations

try:
    from lukhas.tools.todo import *  # type: ignore # noqa: F401,F403
except Exception:
    from dataclasses import dataclass

    __all__ = ["TodoItem", "TodoList"]

    @dataclass
    class TodoItem:
        text: str
        done: bool = False

    class TodoList:
        def __init__(self):
            self.items = []

        def add(self, text: str):
            self.items.append(TodoItem(text))
