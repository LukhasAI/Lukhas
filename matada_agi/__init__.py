#!/usr/bin/env python3
"""
MATADA AGI System

A comprehensive cognitive architecture implementing the MATADA framework:
Memory, Attention, Thought, Action, Decision, Awareness

This system ensures complete interpretability and governance through
the MATADA node format, providing full traceability of all cognitive processes.

Key Features:
- Complete cognitive traceability
- Deterministic processing
- Ethical governance integration
- Causal chain reconstruction
- Multi-modal processing support
"""

from .core import (
    CognitiveNode,
    CognitiveOrchestrator,
    NodeState,
    NodeLink,
    NodeTrigger,
    NodeReflection,
    NodeProvenance,
    ExecutionTrace
)

__version__ = '1.0.0'
__author__ = 'LUKHAS AI Team'

__all__ = [
    'CognitiveNode',
    'CognitiveOrchestrator', 
    'NodeState',
    'NodeLink',
    'NodeTrigger',
    'NodeReflection',
    'NodeProvenance',
    'ExecutionTrace'
]