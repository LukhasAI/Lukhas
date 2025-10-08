"""Project-level site customizations for legacy import compatibility."""

from __future__ import annotations

import importlib.util
import os
import sys
import types
from importlib.abc import MetaPathFinder
from importlib.machinery import ModuleSpec

_repo_root = os.path.dirname(__file__)
_todo_pkg = os.path.join(_repo_root, "TODO")

try:
    import todo as _todo_module  # type: ignore
except ImportError:
    _todo_module = None

if _todo_module is not None:
    sys.modules.setdefault("TODO", _todo_module)
elif os.path.isdir(_todo_pkg):
    try:
        spec = importlib.util.spec_from_file_location("TODO", os.path.join(_todo_pkg, "__init__.py"))
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)  # type: ignore[arg-type]
            module.__path__ = [_todo_pkg]  # type: ignore[attr-defined]
            sys.modules.setdefault("TODO", module)
            sys.modules.setdefault("todo", module)
    except Exception:
        shim = types.ModuleType("TODO")
        shim.__path__ = [_todo_pkg]  # type: ignore[attr-defined]
        sys.modules.setdefault("TODO", shim)
        sys.modules.setdefault("todo", shim)


class _TodoFinder(MetaPathFinder):
    """Meta path finder to alias `TODO` → `todo` package."""

    def find_spec(self, fullname: str, path, target=None) -> ModuleSpec | None:
        if not fullname.startswith("TODO"):
            return None
        alias = fullname.replace("TODO", "todo", 1)
        try:
            return importlib.util.find_spec(alias)
        except Exception:
            return None


_finder = _TodoFinder()
if _finder not in sys.meta_path:
    sys.meta_path.insert(0, _finder)
