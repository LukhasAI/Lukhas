"""Project-level site customizations for legacy import compatibility."""

from __future__ import annotations

import importlib
import os
import sys
import types

try:
    todo_module = importlib.import_module("todo")  # type: ignore
except ImportError:
    todo_module = None

if todo_module is not None:
    sys.modules.setdefault("TODO", todo_module)
else:
    repo_root = os.path.dirname(__file__)
    todo_pkg = os.path.join(repo_root, "TODO")
    if os.path.isdir(todo_pkg):
        shim = types.ModuleType("TODO")
        shim.__path__ = [todo_pkg]  # type: ignore[attr-defined]
        sys.modules.setdefault("TODO", shim)
