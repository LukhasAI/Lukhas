"""Shim exposing `labs.core.bridges.core_safety_bridge` without package deps."""

from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
_LABS_BRIDGES = _REPO_ROOT / "labs/core/bridges"
_SPEC = spec_from_file_location(
    "labs.core.bridges.core_safety_bridge",
    _LABS_BRIDGES / "core_safety_bridge.py",
)
if _SPEC is None or _SPEC.loader is None:  # pragma: no cover - defensive
    raise ImportError("Unable to load labs.core.bridges.core_safety_bridge")
_MODULE = module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)

__all__ = getattr(_MODULE, "__all__", [name for name in dir(_MODULE) if not name.startswith("_")])
for _name in __all__:
    globals()[_name] = getattr(_MODULE, _name)
