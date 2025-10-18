"""Bridge for TODO.scripts."""

from __future__ import annotations

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
    "tools.todo.scripts",
    "candidate.tools.todo.scripts",
    "todo.scripts",
):
    if candidate == __name__:
        continue
    if _bind(candidate):
        break
else:

    def list_tasks(*_args, **_kwargs):
        """Fallback no-op TODO task listing."""

        return []

    __all__.append("list_tasks")
