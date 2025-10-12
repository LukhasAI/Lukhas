"""
Bridge for `lukhas.tools.collapse_simulator`.
Search order: tools → website → candidate → legacy consciousness/collapse paths.
"""
from __future__ import annotations

from importlib import import_module
from typing import Optional

__all__ = ["CollapseSimulator", "main", "DEFAULT_OUTPUT_PATH", "SimulationContext",
           "compile_summary", "derive_top_symbols", "simulate_collapse"]
_SRC: Optional[object] = None

def _try(modname: str):
    try:
        return import_module(modname)
    except Exception:
        return None

for _mod in (
    # First prefer an explicit tools backend if present
    "tools.collapse_simulator",
    "lukhas_website.lukhas.tools.collapse_simulator",
    "candidate.tools.collapse_simulator",
    # Common legacy locations
    "consciousness.collapse.simulator",
    "collapse.simulator",
    "tools.collapse.simulator",
):
    _m = _try(_mod)
    if _m:
        _SRC = _m
        break

# Define fallbacks first, then override with source if available
DEFAULT_OUTPUT_PATH = "./collapse_output"

class SimulationContext:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

def compile_summary(*args, **kwargs):
    return {"status": "noop"}

def derive_top_symbols(*args, **kwargs):
    return []

def simulate_collapse(*args, **kwargs):
    return {"status": "noop"}

class CollapseSimulator:
    def run(self, *_a, **_k):
        return {"status": "noop"}

def main(*_a, **_k):
    return 0

# Override with source if available
if _SRC is not None:
    for _name in ("CollapseSimulator", "main", "DEFAULT_OUTPUT_PATH", "SimulationContext",
                  "compile_summary", "derive_top_symbols", "simulate_collapse"):
        if hasattr(_SRC, _name):
            globals()[_name] = getattr(_SRC, _name)

def __getattr__(name: str):
    if _SRC is not None:
        return getattr(_SRC, name)
    raise AttributeError(name)
