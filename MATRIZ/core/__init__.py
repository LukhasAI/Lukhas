#!/usr/bin/env python3
"""
MATRIZ AGI Core Module

This module contains the core interfaces and orchestration components
for the MATRIZ (Memory, Attention, Thought, Action, Decision, Awareness)
cognitive architecture.

Key Components:
- CognitiveNode: Base interface all nodes must implement
- CognitiveOrchestrator: Routes queries through MATRIZ nodes
- NodeState, NodeLink, NodeReflection: Data structures for MATRIZ format

All components ensure complete traceability and governance through
the MATRIZ node format.
"""

try:
    import streamlit as st
except ImportError:  # pragma: no cover
    st = None
    # Optional UI dependency; core runtime must not require it.

from .node_interface import (  # noqa: TID252 (relative imports in __init__.py are idiomatic)
    CognitiveNode,
    NodeLink,
    NodeProvenance,
    NodeReflection,
    NodeState,
    NodeTrigger,
)
from .orchestrator import (  # noqa: TID252 (relative imports in __init__.py are idiomatic)
    CognitiveOrchestrator,
    ExecutionTrace,
)

__all__ = [
    "CognitiveNode",
    "CognitiveOrchestrator",
    "ExecutionTrace",
    "NodeLink",
    "NodeProvenance",
    "NodeReflection",
    "NodeState",
    "NodeTrigger",
]

__version__ = "1.0.0"
