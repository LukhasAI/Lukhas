#!/usr/bin/env python3
"""
Comprehensive verification of all 14 MATRIZ cognitive nodes.
Tests import, instantiation, processing, and output validation.
"""

import sys


def test_node(node_class, node_name: str, test_input: dict) -> Tuple[bool, str]:
    """Test a single node."""
    try:
        # Instantiate
        node = node_class()

        # Process
        result = node.process(test_input)

        # Validate required keys
        required_keys = ["answer", "confidence", "matriz_node", "processing_time"]
        for key in required_keys:
            if key not in result:
                return False, f"Missing key: {key}"

        # Validate confidence range
        if not 0.0 <= result["confidence"] <= 1.0:
            return False, f"Invalid confidence: {result['confidence']}"

        # Validate output
        if not node.validate_output(result):
            return False, "validate_output() returned False"

        # Validate MATRIZ node
        matriz_node = result["matriz_node"]
        if "id" not in matriz_node or "type" not in matriz_node:
            return False, "Invalid MATRIZ node structure"

        return True, "OK"

    except Exception as e:
        return False, str(e)


def main():
    print("=" * 70)
    print("MATRIZ COGNITIVE NODES COMPREHENSIVE VERIFICATION")
    print("=" * 70)
    print()

    results: List[Tuple[str, str, bool, str]] = []

    # ========== THOUGHT NODES ==========
    print("Testing Thought Nodes...")
    print("-" * 70)

    from matriz.nodes.thought.causal_reasoning import CausalReasoningNode
    success, msg = test_node(
        CausalReasoningNode,
        "CausalReasoningNode",
        {
            "events": [
                {"name": "rain", "timestamp": 100},
                {"name": "wet_ground", "timestamp": 200}
            ],
            "temporal_order": {},
            "domain_knowledge": {}
        }
    )
    results.append(("Thought", "CausalReasoningNode", success, msg))
    print(f"  {'✅' if success else '❌'} CausalReasoningNode: {msg}")

    from matriz.nodes.thought.counterfactual_reasoning import CounterfactualReasoningNode
    success, msg = test_node(
        CounterfactualReasoningNode,
        "CounterfactualReasoningNode",
        {
            "actual_scenario": {"outcome": "failed"},
            "intervention": {"variable": "X", "value": "changed"},
            "causal_model": {"variables": {}}
        }
    )
    results.append(("Thought", "CounterfactualReasoningNode", success, msg))
    print(f"  {'✅' if success else '❌'} CounterfactualReasoningNode: {msg}")

    from matriz.nodes.thought.abductive_reasoning import AbductiveReasoningNode
    success, msg = test_node(
        AbductiveReasoningNode,
        "AbductiveReasoningNode",
        {
            "observations": ["grass is wet", "sky is cloudy"],
            "background_knowledge": {"patterns": []},
            "explanation_constraints": {}
        }
    )
    results.append(("Thought", "AbductiveReasoningNode", success, msg))
    print(f"  {'✅' if success else '❌'} AbductiveReasoningNode: {msg}")

    from matriz.nodes.thought.metacognitive_reasoning import MetacognitiveReasoningNode
    success, msg = test_node(
        MetacognitiveReasoningNode,
        "MetacognitiveReasoningNode",
        {
            "reasoning_trace": [{"step": 1, "type": "inference"}],
            "conclusions": ["conclusion 1"],
            "evidence": ["evidence 1", "evidence 2"]
        }
    )
    results.append(("Thought", "MetacognitiveReasoningNode", success, msg))
    print(f"  {'✅' if success else '❌'} MetacognitiveReasoningNode: {msg}")

    # ========== ACTION NODES ==========
    print()
    print("Testing Action Nodes...")
    print("-" * 70)

    from matriz.nodes.action.plan_generation import PlanGenerationNode
    success, msg = test_node(
        PlanGenerationNode,
        "PlanGenerationNode",
        {
            "goal": "make coffee",
            "current_state": {"facts": []},
            "available_actions": [
                {"description": "fill water", "effects": ["water_filled"]}
            ],
            "constraints": {}
        }
    )
    results.append(("Action", "PlanGenerationNode", success, msg))
    print(f"  {'✅' if success else '❌'} PlanGenerationNode: {msg}")

    from matriz.nodes.action.action_selection import ActionSelectionNode
    success, msg = test_node(
        ActionSelectionNode,
        "ActionSelectionNode",
        {
            "candidate_actions": [
                {"id": "a1", "description": "Walk", "effects": ["arrive"], "risk": 0.1},
                {"id": "a2", "description": "Drive", "effects": ["arrive"], "risk": 0.3}
            ],
            "current_state": {"facts": []},
            "goals": ["arrive"],
            "constraints": {}
        }
    )
    results.append(("Action", "ActionSelectionNode", success, msg))
    print(f"  {'✅' if success else '❌'} ActionSelectionNode: {msg}")

    from matriz.nodes.action.goal_prioritization import GoalPrioritizationNode
    success, msg = test_node(
        GoalPrioritizationNode,
        "GoalPrioritizationNode",
        {
            "goals": [
                {"id": "g1", "description": "Learn Python", "importance": 0.8},
                {"id": "g2", "description": "Finish project", "importance": 0.9}
            ],
            "current_state": {},
            "constraints": {},
            "values": {}
        }
    )
    results.append(("Action", "GoalPrioritizationNode", success, msg))
    print(f"  {'✅' if success else '❌'} GoalPrioritizationNode: {msg}")

    from matriz.nodes.action.resource_allocation import ResourceAllocationNode
    success, msg = test_node(
        ResourceAllocationNode,
        "ResourceAllocationNode",
        {
            "tasks": [
                {"id": "t1", "name": "Task 1", "requested_resources": {"time": 10}}
            ],
            "available_resources": {"time": 100},
            "constraints": {},
            "objectives": ["maximize_value"]
        }
    )
    results.append(("Action", "ResourceAllocationNode", success, msg))
    print(f"  {'✅' if success else '❌'} ResourceAllocationNode: {msg}")

    from matriz.nodes.action.execution_monitoring import ExecutionMonitoringNode
    success, msg = test_node(
        ExecutionMonitoringNode,
        "ExecutionMonitoringNode",
        {
            "executing_actions": [
                {"id": "a1", "name": "Download file"}
            ],
            "expected_states": {},
            "actual_states": {"a1": {"progress": 0.75}},
            "plan": {}
        }
    )
    results.append(("Action", "ExecutionMonitoringNode", success, msg))
    print(f"  {'✅' if success else '❌'} ExecutionMonitoringNode: {msg}")

    # ========== DECISION NODES ==========
    print()
    print("Testing Decision Nodes...")
    print("-" * 70)

    from matriz.nodes.decision.utility_maximization import UtilityMaximizationNode
    success, msg = test_node(
        UtilityMaximizationNode,
        "UtilityMaximizationNode",
        {
            "options": [
                {"id": "opt1", "value": 100, "probability": 0.7},
                {"id": "opt2", "value": 50, "probability": 1.0}
            ],
            "utility_function": {"type": "linear"},
            "risk_preference": 0.0,
            "constraints": {}
        }
    )
    results.append(("Decision", "UtilityMaximizationNode", success, msg))
    print(f"  {'✅' if success else '❌'} UtilityMaximizationNode: {msg}")

    from matriz.nodes.decision.risk_assessment import RiskAssessmentNode
    success, msg = test_node(
        RiskAssessmentNode,
        "RiskAssessmentNode",
        {
            "decision": {
                "id": "d1",
                "risks": [
                    {"id": "r1", "description": "Market risk", "probability": 0.3, "impact": 0.5}
                ]
            },
            "context": {},
            "historical_data": [],
            "risk_tolerance": 0.5
        }
    )
    results.append(("Decision", "RiskAssessmentNode", success, msg))
    print(f"  {'✅' if success else '❌'} RiskAssessmentNode: {msg}")

    from matriz.nodes.decision.ethical_constraint import EthicalConstraintNode
    success, msg = test_node(
        EthicalConstraintNode,
        "EthicalConstraintNode",
        {
            "decision": {
                "id": "d1",
                "consent_obtained": True,
                "harmful_effects": []
            },
            "ethical_principles": [],
            "context": {},
            "stakeholders": []
        }
    )
    results.append(("Decision", "EthicalConstraintNode", success, msg))
    print(f"  {'✅' if success else '❌'} EthicalConstraintNode: {msg}")

    # ========== AWARENESS NODES ==========
    print()
    print("Testing Awareness Nodes...")
    print("-" * 70)

    from matriz.nodes.awareness.metacognitive_monitoring import MetacognitiveMonitoringNode
    success, msg = test_node(
        MetacognitiveMonitoringNode,
        "MetacognitiveMonitoringNode",
        {
            "active_processes": [
                {"name": "reasoning", "processing_time": 1000, "outputs_produced": 5}
            ],
            "performance_history": [
                {"process": "reasoning", "accuracy": 0.8, "success": True}
            ],
            "target_metrics": {},
            "monitoring_window": 3600000
        }
    )
    results.append(("Awareness", "MetacognitiveMonitoringNode", success, msg))
    print(f"  {'✅' if success else '❌'} MetacognitiveMonitoringNode: {msg}")

    from matriz.nodes.awareness.confidence_calibration import ConfidenceCalibrationNode
    success, msg = test_node(
        ConfidenceCalibrationNode,
        "ConfidenceCalibrationNode",
        {
            "predictions": [
                {"id": "p1", "confidence": 0.9, "value": "A"}
            ],
            "actual_outcomes": [
                {"id": "p1", "value": "A"}
            ],
            "calibration_history": [],
            "target_calibration": 0.1
        }
    )
    results.append(("Awareness", "ConfidenceCalibrationNode", success, msg))
    print(f"  {'✅' if success else '❌'} ConfidenceCalibrationNode: {msg}")

    # ========== SUMMARY ==========
    print()
    print("=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)

    # Count by category
    categories = {}
    for category, node_name, success, msg in results:
        if category not in categories:
            categories[category] = {"total": 0, "passed": 0}
        categories[category]["total"] += 1
        if success:
            categories[category]["passed"] += 1

    for category, stats in categories.items():
        print(f"{category:12s}: {stats['passed']}/{stats['total']} passed")

    # Overall
    total = len(results)
    passed = sum(1 for _, _, success, _ in results if success)

    print()
    print(f"OVERALL: {passed}/{total} nodes passed ({int(passed/total*100)}%)")

    if passed == total:
        print()
        print("🎉 ALL NODES VERIFIED SUCCESSFULLY!")
        print()
        return 0
    else:
        print()
        print("❌ Some nodes failed verification")
        print()
        print("Failed nodes:")
        for category, node_name, success, msg in results:
            if not success:
                print(f"  - {category}/{node_name}: {msg}")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
