#!/usr/bin/env python3
"""
MATRIZ AI Core Module

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

from .async_orchestrator import AsyncCognitiveOrchestrator  # Export async orchestrator
from .memory_system import MemorySystem  # Export memory system
from .node_interface import (  # (relative imports in __init__.py are idiomatic)
    CognitiveNode,
    NodeLink,
    NodeProvenance,
    NodeReflection,
    NodeState,
    NodeTrigger,
)
from .orchestrator import (  # (relative imports in __init__.py are idiomatic)
    CognitiveOrchestrator,
    ExecutionTrace,
)

__all__ = [
    "AsyncCognitiveOrchestrator",
    "CognitiveNode",
    "CognitiveOrchestrator",
    "ExecutionTrace",
    "MemorySystem",
    "NodeLink",
    "NodeProvenance",
    "NodeReflection",
    "NodeState",
    "NodeTrigger",
]

__version__ = "1.0.0"
