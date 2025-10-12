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
    # Use __dict__ to avoid triggering lukhas.core's __getattr__
    _lukhas_all = _lukhas_core.__dict__.get("__all__", [])
    # Only update globals if __all__ is valid and non-empty
    if _lukhas_all and isinstance(_lukhas_all, (list, tuple)):
        globals().update({name: getattr(_lukhas_core, name) for name in _lukhas_all if not name.startswith("_")})
    __all__ = list(_lukhas_all) if isinstance(_lukhas_all, (list, tuple)) else []


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

# Added for test compatibility (core.core_wrapper)
try:
    from candidate.core import core_wrapper  # noqa: F401
except ImportError:
    def core_wrapper(*args, **kwargs):
        """Stub for core_wrapper."""
        return None

# Add GLYPH exports for test compatibility
try:
    from candidate.core.common.glyph import GLYPHSymbol, GLYPHToken, create_glyph  # noqa: F401
except ImportError:
    GLYPHSymbol = None  # type: ignore[assignment]
    GLYPHToken = None  # type: ignore[assignment]
    def create_glyph(*args, **kwargs):  # type: ignore[misc]
        """Stub for create_glyph."""
        return None

# Add CoreWrapper export for test compatibility
try:
    from lukhas_website.lukhas.core.core_wrapper import CoreWrapper  # noqa: F401
except ImportError:
    try:
        from candidate.core.core_wrapper import CoreWrapper  # noqa: F401
    except ImportError:
        CoreWrapper = None  # type: ignore[assignment, misc]

# Define TRINITY_SYMBOLS for constellation framework
TRINITY_SYMBOLS = {
    "identity": "⚛️",
    "consciousness": "🧠",
    "guardian": "🛡️",
    "memory": "✦",
    "vision": "🔬",
    "bio": "🌱",
    "dream": "🌙",
    "ethics": "⚖️",
}

# Update __all__
try:
    __all__  # type: ignore[name-defined]
except NameError:
    __all__ = []

for _name in ("core_wrapper", "GLYPHSymbol", "GLYPHToken", "create_glyph", "CoreWrapper", "TRINITY_SYMBOLS"):
    if _name not in __all__:
        __all__.append(_name)
