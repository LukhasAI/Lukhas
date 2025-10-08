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

# Ensure six's legacy meta-importer cooperates with Python 3.11 importlib.
try:
    import six

    importer_cls = getattr(six, "_SixMetaPathImporter", None)
    if importer_cls is not None and not hasattr(importer_cls, "find_spec"):

        def _find_spec(self, fullname, path=None, target=None):
            loader = self.find_module(fullname, path)  # type: ignore[attr-defined]
            if loader is None:
                return None
            from importlib.util import spec_from_loader

            return spec_from_loader(fullname, loader)

        importer_cls.find_spec = _find_spec  # type: ignore[assignment]

        importer = next(
            (finder for finder in sys.meta_path if isinstance(finder, importer_cls)),
            None,
        )
        if importer is not None and not hasattr(importer, "find_spec"):
            importer.find_spec = _find_spec.__get__(importer, importer_cls)  # type: ignore[attr-defined]
except Exception:  # pragma: no cover - best effort shim
    pass
