#!/usr/bin/env python3
"""
MATRIZ Node Registry

A central registry for all available cognitive nodes.
"""

from matriz.nodes.thought.deductive_reasoning import DeductiveReasoningNode
from matriz.nodes.action.tool_usage import ToolUsageNode
from matriz.nodes.decision.option_selection import OptionSelectionNode
from matriz.nodes.awareness.state_assessment import StateAssessmentNode
from matriz.nodes.math_node import MathNode

_NODE_REGISTRY = {}


def register_node(node_name: str, node_class: type):
    """
    Register a cognitive node.
    """
    if node_name in _NODE_REGISTRY:
        raise ValueError(f"Node '{node_name}' is already registered.")
    _NODE_REGISTRY[node_name] = node_class


def get_node(node_name: str) -> type:
    """
    Get a cognitive node from the registry.
    """
    if node_name not in _NODE_REGISTRY:
        raise ValueError(f"Node '{node_name}' is not registered.")
    return _NODE_REGISTRY[node_name]


def get_all_nodes() -> dict[str, type]:
    """
    Get all registered cognitive nodes.
    """
    return _NODE_REGISTRY


# Register the nodes
register_node("deductive_reasoning", DeductiveReasoningNode)
register_node("tool_usage", ToolUsageNode)
register_node("option_selection", OptionSelectionNode)
register_node("state_assessment", StateAssessmentNode)
register_node("math", Math.MathNode)
