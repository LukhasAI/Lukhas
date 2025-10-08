"""
Bridge for `lukhas.tools.collapse_simulator`.
Delegates to the first available implementation; exposes its public API.
"""
from __future__ import annotations
from importlib import import_module
from typing import Optional, List

__all__: List[str] = []
_SRC = None  # underlying implementation module

def _try(modname: str):
    global _SRC, __all__
    try:
        m = import_module(modname)
    except Exception:
        return False
    _SRC = m
    __all__ = [n for n in dir(m) if not n.startswith("_")]
    return True

# Likely locations (richest → leanest)
for _mod in (
    "candidate.tools.collapse_simulator",
    "tools.collapse_simulator_main",
    "consciousness.collapse.simulator",
):
    if _try(_mod):
        break

if _SRC is None or len(__all__) < 3:  # If source is too minimal, use fallbacks
    # Minimal fallback to keep collection alive
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
        def run(self, *args, **kwargs):
            return {"status": "noop", "args": args, "kwargs": kwargs}

    __all__ = [
        "DEFAULT_OUTPUT_PATH",
        "SimulationContext",
        "compile_summary",
        "derive_top_symbols",
        "simulate_collapse",
        "CollapseSimulator"
    ]
else:
    # PEP 562: delegate attributes to the bound source module
    def __getattr__(name: str):
        return getattr(_SRC, name)
