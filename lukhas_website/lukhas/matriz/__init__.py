"""Compatibility shim: expose the top-level `matriz` package under ``matriz``.

This module prefers an installed ``matriz`` package, otherwise falls back to
the local repository copy. It also re-exports a small set of runtime symbols
when available.
"""
import importlib
import logging
import time
from typing import Any
import streamlit as st
logger = logging.getLogger(__name__)
try:
    import MATRIZ as _matriz
except Exception:
    _matriz = importlib.import_module('matriz')
__all__ = getattr(_matriz, '__all__', [])
for _name in __all__:
    globals()[_name] = getattr(_matriz, _name)
try:
    from .runtime.policy import PolicyEngine
    from .runtime.supervisor import RuntimeSupervisor
    MatrizNode = RuntimeSupervisor
except Exception as e:
    logger.info(f'MΛTRIZ runtime components not available: {e}')
    RuntimeSupervisor = None
    PolicyEngine = None
    MatrizNode = None
__all__ += ['MatrizNode', 'PolicyEngine', 'RuntimeSupervisor']
__version__ = '1.0.0'