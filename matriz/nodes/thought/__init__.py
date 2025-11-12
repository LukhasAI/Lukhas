#!/usr/bin/env python3
"""
MATRIZ Thought Nodes Module

Specialized thought processing nodes for MATRIZ cognitive architecture:
- AnalogicalReasoningNode: Maps structural relationships across domains
- CausalReasoningNode: Identifies cause-effect relationships
- CounterfactualReasoningNode: Reasons about alternative scenarios
- AbductiveReasoningNode: Infers best explanations
- MetacognitiveReasoningNode: Monitors reasoning quality

All nodes implement the CognitiveNode interface and maintain
full traceability through the MATRIZ node format.
"""

from .analogical_reasoning import AnalogicalReasoningNode
from .causal_reasoning import CausalReasoningNode
from .counterfactual_reasoning import CounterfactualReasoningNode
from .abductive_reasoning import AbductiveReasoningNode
from .metacognitive_reasoning import MetacognitiveReasoningNode

__all__ = [
    "AbductiveReasoningNode",
    "AnalogicalReasoningNode",
    "CausalReasoningNode",
    "CounterfactualReasoningNode",
    "MetacognitiveReasoningNode",
]

__version__ = "1.0.0"
