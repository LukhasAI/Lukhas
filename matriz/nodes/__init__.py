#!/usr/bin/env python3
"""
MATRIZ Nodes Module

Complete suite of specialized cognitive nodes for the MATRIZ architecture.

Base Nodes:
- MathNode: Mathematical computation and validation
- ValidatorNode: Data validation and constraint checking
- FactNode: Fact storage and retrieval operations
- SymbolicNode: Symbolic reasoning and formal proof generation

Thought Nodes (5):
- AnalogicalReasoningNode: Maps structural relationships across domains
- CausalReasoningNode: Identifies cause-effect relationships
- CounterfactualReasoningNode: Reasons about alternative scenarios
- AbductiveReasoningNode: Infers best explanations
- MetacognitiveReasoningNode: Monitors reasoning quality

Action Nodes (5):
- PlanGenerationNode: Generate action plans
- ActionSelectionNode: Select optimal actions
- GoalPrioritizationNode: Prioritize goals
- ResourceAllocationNode: Allocate cognitive resources
- ExecutionMonitoringNode: Monitor action execution

Decision Nodes (3):
- UtilityMaximizationNode: Maximize utility functions
- RiskAssessmentNode: Assess decision risks
- EthicalConstraintNode: Apply ethical constraints

Awareness Nodes (4):
- MetacognitiveMonitoringNode: Monitor cognitive processes
- ConfidenceCalibrationNode: Calibrate confidence estimates
- PerformanceEvaluationNode: Evaluate cognitive performance
- SelfMonitoringNode: Monitor internal cognitive states

All nodes implement the CognitiveNode interface and maintain
full traceability through the MATRIZ node format.
"""

# Base cognitive nodes
from .fact_node import FactNode  # (relative imports in __init__.py are idiomatic)
from .math_node import MathNode  # (relative imports in __init__.py are idiomatic)
from .symbolic_node import SymbolicNode  # (relative imports in __init__.py are idiomatic)
from .validator_node import ValidatorNode  # (relative imports in __init__.py are idiomatic)

# Specialized node categories
from .action import (
    ActionSelectionNode,
    ExecutionMonitoringNode,
    GoalPrioritizationNode,
    PlanGenerationNode,
    ResourceAllocationNode,
)
from .awareness import (
    ConfidenceCalibrationNode,
    MetacognitiveMonitoringNode,
    PerformanceEvaluationNode,
    SelfMonitoringNode,
)
from .decision import (
    EthicalConstraintNode,
    RiskAssessmentNode,
    UtilityMaximizationNode,
)
from .thought import (
    AbductiveReasoningNode,
    AnalogicalReasoningNode,
    CausalReasoningNode,
    CounterfactualReasoningNode,
    MetacognitiveReasoningNode,
)

__all__ = [
    # Thought nodes
    "AbductiveReasoningNode",
    # Action nodes
    "ActionSelectionNode",
    "AnalogicalReasoningNode",
    "CausalReasoningNode",
    # Awareness nodes
    "ConfidenceCalibrationNode",
    "CounterfactualReasoningNode",
    # Decision nodes
    "EthicalConstraintNode",
    "ExecutionMonitoringNode",
    # Base nodes
    "FactNode",
    "GoalPrioritizationNode",
    "MathNode",
    "MetacognitiveMonitoringNode",
    "MetacognitiveReasoningNode",
    "PerformanceEvaluationNode",
    "PlanGenerationNode",
    "ResourceAllocationNode",
    "RiskAssessmentNode",
    "SelfMonitoringNode",
    "SymbolicNode",
    "UtilityMaximizationNode",
    "ValidatorNode",
]

__version__ = "2.0.0"
