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
import streamlit as st

from .core import (
    CognitiveNode,
    CognitiveOrchestrator,
    ExecutionTrace,
    NodeLink,
    NodeProvenance,
    NodeReflection,
    NodeState,
    NodeTrigger,
)

__version__ = "1.0.0"
__author__ = "LUKHAS AI Team"

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