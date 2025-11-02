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

if "streamlit" not in sys.modules:

    def _noop(*args, **kwargs):
        return None

    def _cache_data(*args, **kwargs):
        return lambda func: func

    streamlit_stub = types.SimpleNamespace(
        write=_noop,
        markdown=_noop,
        title=_noop,
        caption=_noop,
        info=_noop,
        success=_noop,
        warning=_noop,
        error=_noop,
        set_page_config=_noop,
        cache_data=_cache_data,
    )
    streamlit_stub.sidebar = types.SimpleNamespace(
        write=_noop,
        markdown=_noop,
        button=_noop,
        caption=_noop,
        info=_noop,
        success=_noop,
        warning=_noop,
        error=_noop,
    )
    sys.modules["streamlit"] = streamlit_stub

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

# Provide minimal urllib3 warning stubs when the dependency is unavailable.
try:  # pragma: no cover - prefer real urllib3 when available
    import urllib3 as _urllib3  # type: ignore
except Exception:  # pragma: no cover - executed when urllib3 missing
    urllib3_stub = types.ModuleType("urllib3")
    exceptions_stub = types.ModuleType("urllib3.exceptions")

    class NotOpenSSLWarning(Warning):
        """Fallback for urllib3's SSL warning."""

    class InsecureRequestWarning(Warning):
        """Fallback for urllib3's insecure request warning."""

    exceptions_stub.NotOpenSSLWarning = NotOpenSSLWarning
    exceptions_stub.InsecureRequestWarning = InsecureRequestWarning

    def _missing_attr(name: str):  # ΛTAG: governance_stub_guardian
        raise AttributeError("urllib3 stub does not implement attribute %r; install urllib3 for full support" % name)

    def __getattr__(name: str):  # pragma: no cover - diagnostic helper
        return _missing_attr(name)

    urllib3_stub.__getattr__ = __getattr__  # type: ignore[attr-defined]
    urllib3_stub.exceptions = exceptions_stub  # type: ignore[attr-defined]

    sys.modules.setdefault("urllib3", urllib3_stub)
    sys.modules.setdefault("urllib3.exceptions", exceptions_stub)
else:  # pragma: no cover - real urllib3 available
    sys.modules.setdefault("urllib3", _urllib3)
