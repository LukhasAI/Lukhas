"""Utilities for working with repository TODO inventories."""

from importlib import import_module as _import_module

categorize_todos = _import_module(".categorize_todos", __name__)

PRIORITY_KEYWORDS = categorize_todos.PRIORITY_KEYWORDS
TODORecord = categorize_todos.TODORecord
extract_todo_context = categorize_todos.extract_todo_context
generate_priority_files = categorize_todos.generate_priority_files
load_exclusions = categorize_todos.load_exclusions

__all__ = [
    "categorize_todos",
    "PRIORITY_KEYWORDS",
    "TODORecord",
    "extract_todo_context",
    "generate_priority_files",
    "load_exclusions",
]
