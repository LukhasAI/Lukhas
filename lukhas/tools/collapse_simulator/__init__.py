"""Tools-facing collapse simulator bridge with safe fallbacks."""
from __future__ import annotations

from importlib import import_module

__all__ = ["CollapseConfig", "run_simulator", "simulate_once"]

_CANDIDATES = (
    "tools.collapse_simulator",
    "tools.collapse_simulator_main",
    "consciousness.collapse.simulator",
    "candidate.tools.collapse_simulator",
    "lukhas_website.lukhas.tools.collapse_simulator",
)


def _get(module: str, name: str):
    try:
        mod = import_module(module)
    except Exception:
        return None
    return getattr(mod, name, None) if hasattr(mod, name) else None


for _name in list(__all__):
    value = next((obj for obj in (_get(mod, _name) for mod in _CANDIDATES) if obj), None)
    if value is not None:
        globals()[_name] = value


if "CollapseConfig" not in globals():
    class CollapseConfig:  # type: ignore[misc]
        def __init__(self, **kwargs) -> None:
            self.__dict__.update(kwargs)


if "run_simulator" not in globals():
    def run_simulator(cfg: "CollapseConfig", *args, **kwargs):  # type: ignore[misc]
        return {"status": "noop", "steps": 0}


if "simulate_once" not in globals():
    def simulate_once(*args, **kwargs):  # type: ignore[misc]
        return {"status": "noop"}
