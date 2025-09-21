"""Compatibility bridge exposing :mod:`lukhas.core` under the historical ``core`` namespace."""
from __future__ import annotations

import importlib
import logging
import sys
from pathlib import Path
from typing import Any

# ΛTAG: bridge
_logger = logging.getLogger(__name__)

_pkg_dir = Path(__file__).resolve().parent
_lukhas_core_dir = (_pkg_dir.parent / "lukhas" / "core").resolve()

if str(_lukhas_core_dir.parent) not in sys.path:
    sys.path.insert(0, str(_lukhas_core_dir.parent))

__path__ = [str(_pkg_dir)]
if _lukhas_core_dir.exists():
    __path__.append(str(_lukhas_core_dir))
else:
    _logger.warning("ΛTRACE: lukhas.core directory missing; core namespace shims only.")

try:
    _lukhas_core = importlib.import_module("lukhas.core")
except ModuleNotFoundError as exc:  # pragma: no cover - defensive fallback
    _logger.error("ΛTRACE: Failed to import lukhas.core: %s", exc)
    __all__ = []
else:
    globals().update({name: getattr(_lukhas_core, name) for name in getattr(_lukhas_core, "__all__", [])})
    __all__ = getattr(_lukhas_core, "__all__", [])


def __getattr__(item: str) -> Any:
    """Lazy proxy that resolves ``core.<item>`` into ``lukhas.core.<item>`` on demand."""
    module_name = f"lukhas.core.{item}"
    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError as exc:
        raise AttributeError(f"core namespace cannot resolve '{item}'") from exc
    sys.modules.setdefault(f"core.{item}", module)
    return module


def __dir__() -> list[str]:
    baseline = set(globals())
    if '_lukhas_core' in globals():
        baseline.update(getattr(_lukhas_core, '__all__', []))
    return sorted(baseline)


# ✅ TODO: replace shim once native core package lives inside repository.
