"""Bridge for legacy TODO module imports."""

from __future__ import annotations

import os
import sys
from importlib import import_module
from typing import List

__all__: List[str] = []


def _bind(module_name: str) -> bool:
    try:
        module = import_module(module_name)
    except Exception:
        return False

    for attr in dir(module):
        if attr.startswith("_"):
            continue
        globals()[attr] = getattr(module, attr)
        __all__.append(attr)
    return True


for candidate in (
    "tools.todo",
    "candidate.tools.todo",
):
    if candidate == __name__:
        continue
    if _bind(candidate):
        break
else:
    from dataclasses import dataclass

    __all__ = ["TodoItem", "TodoList"]

    @dataclass
    class TodoItem:
        text: str
        done: bool = False

    class TodoList:
        """Fallback todo list implementation."""

        def __init__(self):
            self.items = []

        def add(self, text: str):
            self.items.append(TodoItem(text))


__path__ = [os.path.dirname(__file__)]
sys.modules["todo"] = sys.modules[__name__]
sys.modules["TODO"] = sys.modules[__name__]
