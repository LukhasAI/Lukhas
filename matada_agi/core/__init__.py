#!/usr/bin/env python3
"""
MATADA AGI Core Module

This module contains the core interfaces and orchestration components
for the MATADA (Memory, Attention, Thought, Action, Decision, Awareness) 
cognitive architecture.

Key Components:
- CognitiveNode: Base interface all nodes must implement
- CognitiveOrchestrator: Routes queries through MATADA nodes
- NodeState, NodeLink, NodeReflection: Data structures for MATADA format

All components ensure complete traceability and governance through
the MATADA node format.
"""

from .node_interface import (
    CognitiveNode,
    NodeState,
    NodeLink,
    NodeTrigger,
    NodeReflection,
    NodeProvenance
)
from .orchestrator import CognitiveOrchestrator, ExecutionTrace

__all__ = [
    'CognitiveNode',
    'NodeState', 
    'NodeLink',
    'NodeTrigger',
    'NodeReflection',
    'NodeProvenance',
    'CognitiveOrchestrator',
    'ExecutionTrace'
]

__version__ = '1.0.0'