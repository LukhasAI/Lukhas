"""TODO utilities expected by tests."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List

__all__ = ["TodoItem", "categorize_todos"]


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
