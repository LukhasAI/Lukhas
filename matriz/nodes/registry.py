#!/usr/bin/env python3
"""
MATRIZ Node Registry

A central registry for all available cognitive nodes across all categories:
- Thought (6 nodes): Reasoning and cognitive processes
- Action (6 nodes): Planning and execution
- Decision (4 nodes): Choice and evaluation
- Awareness (5 nodes): Self-monitoring and metacognition
"""

# Thought nodes
# Action nodes
from matriz.nodes.action.action_selection import ActionSelectionNode
from matriz.nodes.action.execution_monitoring import ExecutionMonitoringNode
from matriz.nodes.action.goal_prioritization import GoalPrioritizationNode
from matriz.nodes.action.plan_generation import PlanGenerationNode
from matriz.nodes.action.resource_allocation import ResourceAllocationNode
from matriz.nodes.action.tool_usage import ToolUsageNode

# Awareness nodes
from matriz.nodes.awareness.confidence_calibration import ConfidenceCalibrationNode
from matriz.nodes.awareness.metacognitive_monitoring import MetacognitiveMonitoringNode
from matriz.nodes.awareness.performance_evaluation import PerformanceEvaluationNode
from matriz.nodes.awareness.self_monitoring import SelfMonitoringNode
from matriz.nodes.awareness.state_assessment import StateAssessmentNode

# Decision nodes
from matriz.nodes.decision.ethical_constraint import EthicalConstraintNode
from matriz.nodes.decision.option_selection import OptionSelectionNode
from matriz.nodes.decision.risk_assessment import RiskAssessmentNode
from matriz.nodes.decision.utility_maximization import UtilityMaximizationNode

# Legacy nodes
from matriz.nodes.math_node import MathNode
from matriz.nodes.thought.abductive_reasoning import AbductiveReasoningNode
from matriz.nodes.thought.analogical_reasoning import AnalogicalReasoningNode
from matriz.nodes.thought.causal_reasoning import CausalReasoningNode
from matriz.nodes.thought.counterfactual_reasoning import CounterfactualReasoningNode
from matriz.nodes.thought.deductive_reasoning import DeductiveReasoningNode
from matriz.nodes.thought.metacognitive_reasoning import MetacognitiveReasoningNode

_NODE_REGISTRY = {}


def register_node(node_name: str, node_class: type):
    """
    Register a cognitive node.

    Args:
        node_name: Unique identifier for the node
        node_class: Node class (must extend CognitiveNode)

    Raises:
        ValueError: If node_name is already registered
    """
    if node_name in _NODE_REGISTRY:
        raise ValueError(f"Node '{node_name}' is already registered.")
    _NODE_REGISTRY[node_name] = node_class


def get_node(node_name: str) -> type:
    """
    Get a cognitive node class from the registry.

    Args:
        node_name: Node identifier

    Returns:
        Node class

    Raises:
        ValueError: If node_name is not registered
    """
    if node_name not in _NODE_REGISTRY:
        raise ValueError(f"Node '{node_name}' is not registered.")
    return _NODE_REGISTRY[node_name]


def get_all_nodes() -> dict[str, type]:
    """
    Get all registered cognitive nodes.

    Returns:
        Dict mapping node names to node classes
    """
    return _NODE_REGISTRY.copy()


def get_nodes_by_category(category: str) -> dict[str, type]:
    """
    Get all nodes in a specific category.

    Args:
        category: Category name (thought, action, decision, awareness)

    Returns:
        Dict mapping node names to node classes in that category
    """
    return {
        name: cls for name, cls in _NODE_REGISTRY.items()
        if name.startswith(category)
    }


def list_all_node_names() -> list[str]:
    """
    Get list of all registered node names.

    Returns:
        Sorted list of node names
    """
    return sorted(_NODE_REGISTRY.keys())


# ============================================================================
# Register all cognitive nodes
# ============================================================================

# Thought nodes (6)
register_node("thought.abductive_reasoning", AbductiveReasoningNode)
register_node("thought.analogical_reasoning", AnalogicalReasoningNode)
register_node("thought.causal_reasoning", CausalReasoningNode)
register_node("thought.counterfactual_reasoning", CounterfactualReasoningNode)
register_node("thought.deductive_reasoning", DeductiveReasoningNode)
register_node("thought.metacognitive_reasoning", MetacognitiveReasoningNode)

# Action nodes (6)
register_node("action.action_selection", ActionSelectionNode)
register_node("action.execution_monitoring", ExecutionMonitoringNode)
register_node("action.goal_prioritization", GoalPrioritizationNode)
register_node("action.plan_generation", PlanGenerationNode)
register_node("action.resource_allocation", ResourceAllocationNode)
register_node("action.tool_usage", ToolUsageNode)

# Decision nodes (4)
register_node("decision.ethical_constraint", EthicalConstraintNode)
register_node("decision.option_selection", OptionSelectionNode)
register_node("decision.risk_assessment", RiskAssessmentNode)
register_node("decision.utility_maximization", UtilityMaximizationNode)

# Awareness nodes (5)
register_node("awareness.confidence_calibration", ConfidenceCalibrationNode)
register_node("awareness.metacognitive_monitoring", MetacognitiveMonitoringNode)
register_node("awareness.performance_evaluation", PerformanceEvaluationNode)
register_node("awareness.self_monitoring", SelfMonitoringNode)
register_node("awareness.state_assessment", StateAssessmentNode)

# Legacy nodes
register_node("math", MathNode)

# ============================================================================
# Module initialization complete: 22 nodes registered
# ============================================================================
