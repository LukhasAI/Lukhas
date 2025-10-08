"""Bridge for legacy TODO module imports."""

from __future__ import annotations

import os
import sys

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

__path__ = [os.path.dirname(__file__)]
sys.modules.setdefault("todo", sys.modules[__name__])
sys.modules.setdefault("TODO", sys.modules[__name__])
