"""Bridge for consciousness collapse simulator with noop fallbacks."""
from __future__ import annotations

from importlib import import_module

__all__ = ["CollapseConfig", "run_simulator", "simulate_once"]

_CANDIDATES = (
    "lukhas_website.lukhas.consciousness.collapse.simulator",
    "candidate.consciousness.collapse.simulator",
    "consciousness.collapse.simulator_impl",
    "tools.collapse_simulator",
)


def _bind(name: str) -> bool:
    for module in _CANDIDATES:
        try:
            mod = import_module(module)
        except Exception:
            continue
        if hasattr(mod, name):
            globals()[name] = getattr(mod, name)
            return True
    return False


ok_config = _bind("CollapseConfig")
ok_run = _bind("run_simulator")
ok_once = _bind("simulate_once")


if not ok_config:
    class CollapseConfig:  # type: ignore[misc]
        def __init__(self, **kwargs) -> None:
            self.__dict__.update(kwargs)


if not ok_run:
    def run_simulator(cfg: "CollapseConfig", *args, **kwargs):  # type: ignore[misc]
        return {"status": "noop", "steps": 0}


if not ok_once:
    def simulate_once(*args, **kwargs):  # type: ignore[misc]
        return {"status": "noop"}
