"""TODO utilities expected by tests."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List

__all__ = ["TodoItem", "TodoList", "categorize_todos"]


@dataclass
class TodoItem:
    text: str
    priority: str = "normal"
    tags: List[str] | None = None


def categorize_todos(items: Iterable[TodoItem]) -> Dict[str, List[TodoItem]]:
    buckets: Dict[str, List[TodoItem]] = {"low": [], "normal": [], "high": []}
    for item in items:
        priority = (item.priority or "normal").lower()
        if priority not in buckets:
            priority = "normal"
        buckets[priority].append(item)
    return buckets


class TodoList:
    """Simple in-memory todo list used in legacy tests."""

    def __init__(self):
        self.items: List[TodoItem] = []

    def add(self, text: str, priority: str = "normal", tags: List[str] | None = None) -> TodoItem:
        item = TodoItem(text=text, priority=priority, tags=tags)
        self.items.append(item)
        return item

    def pending(self) -> List[TodoItem]:
        return list(self.items)
