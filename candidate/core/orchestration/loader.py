# candidate/core/orchestration/loader.py
"""
Dynamic node discovery (dark by default).

Discovers classes subclassing CognitiveNodeBase with AUTOINIT=True.
Env:
- NODES_DISABLED="a,b,c" optional deny-list
"""

from __future__ import annotations
import os
import pkgutil
import importlib
import inspect
from typing import Iterable
from lukhas.core.interfaces import CognitiveNodeBase
from lukhas.core.registry import register


def discover_nodes(root_package: str = "candidate") -> int:
    disabled = {x.strip() for x in os.getenv("NODES_DISABLED", "").split(",") if x.strip()}
    found = 0
    for mod in pkgutil.iter_modules():
        name = mod.name
        if not name.startswith(f"{root_package}."):
            continue
        if ".nodes." not in name:
            continue
        try:
            m = importlib.import_module(name)
        except Exception:
            continue
        for _, cls in inspect.getmembers(m, inspect.isclass):
            if not issubclass(cls, CognitiveNodeBase):
                continue
            if not getattr(cls, "AUTOINIT", False):
                continue
            node_name = getattr(cls, "name", cls.__name__)
            if node_name in disabled:
                continue
            try:
                inst = cls.from_env()
                register(f"node:{node_name}", inst)
                found += 1
            except Exception:
                continue
    return found