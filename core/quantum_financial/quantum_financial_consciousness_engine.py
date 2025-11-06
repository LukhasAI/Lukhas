"""Compatibility shim for quantum financial consciousness engine."""

from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
import sys
from types import ModuleType
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SPEC = spec_from_file_location(
    "labs.core.qi_financial.quantum_financial_consciousness_engine",
    _REPO_ROOT / "labs/core/qi_financial/quantum_financial_consciousness_engine.py",
)
if _SPEC is None or _SPEC.loader is None:  # pragma: no cover - defensive
    raise ImportError("Unable to load labs.core.qi_financial.quantum_financial_consciousness_engine")
_MODULE = module_from_spec(_SPEC)
_MODULE_NAME = _SPEC.name

_existing = sys.modules.get(_MODULE_NAME)
if isinstance(_existing, ModuleType):
    _MODULE = _existing
else:
    sys.modules[_MODULE_NAME] = _MODULE
    try:
        _SPEC.loader.exec_module(_MODULE)
    except Exception:  # pragma: no cover - bubble up while cleaning sys.modules
        sys.modules.pop(_MODULE_NAME, None)
        raise

__all__ = getattr(_MODULE, "__all__", [name for name in dir(_MODULE) if not name.startswith("_")])
for _name in __all__:
    globals()[_name] = getattr(_MODULE, _name)
