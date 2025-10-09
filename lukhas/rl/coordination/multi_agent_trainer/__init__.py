"""Bridge for `lukhas.rl.coordination.multi_agent_trainer`.

Auto-generated bridge following canonical pattern:
  1) lukhas_website.lukhas.lukhas.rl.coordination.multi_agent_trainer
  2) candidate.lukhas.rl.coordination.multi_agent_trainer
  3) rl.coordination.multi_agent_trainer

Graceful fallback to stubs if no backend available.
"""
from __future__ import annotations
from importlib import import_module
from typing import List

__all__: List[str] = [
    "MultiAgentConsciousnessTrainer",
    "TrainingConfiguration",
]


def _try(n: str):
    try:
        mod = import_module(n)
    except Exception:
        return None
    if mod.__name__ == __name__:
        return None
    return mod


_CANDIDATES = (
    "lukhas_website.lukhas.rl.coordination.multi_agent_trainer",
    "candidate.rl.coordination.multi_agent_trainer",
    "rl.coordination.multi_agent_trainer",
)

_SRC = None
for _cand in _CANDIDATES:
    _m = _try(_cand)
    if not _m:
        continue
    _SRC = _m
    for _k in dir(_m):
        if _k.startswith("_"):
            continue
        globals()[_k] = getattr(_m, _k)
        if _k not in __all__:
            __all__.append(_k)
    break


class _TrainerStub:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    async def train(self, *args, **kwargs):
        return {"episodes": 0}


class _ConfigStub:
    def __init__(self, **kwargs):
        self.options = kwargs


if "MultiAgentConsciousnessTrainer" not in globals():
    MultiAgentConsciousnessTrainer = _TrainerStub  # type: ignore

if "TrainingConfiguration" not in globals():
    TrainingConfiguration = _ConfigStub  # type: ignore
