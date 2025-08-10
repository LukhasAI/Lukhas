#!/usr/bin/env python3
"""
Test for ethics guardian realignment implementation.
Tests the ethical realignment planning functionality.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json


def test_ethical_realignment():
    """Test the ethical realignment planning implementation."""

    # Import the ethics guardian
    from ethics.guardian import EthicsGuardian

    # Create test instance
    guardian = EthicsGuardian(
        parent_id="test_parent_ethics_002",
        task_data={
            "violation_type": "comprehensive_ethics_review",
            "severity": "high",
            "trigger": "multiple_violations_detected",
        },
    )

    print("\n⚖️ Testing Ethical Realignment Planning...")

    # First perform an assessment to have data for realignment
    decision_context = {
        "type": "automated_decision_system",
        "stakeholders": ["users", "organization", "society"],
        "informed_consent": False,
        "user_control": 0.2,
        "potential_manipulation": True,
        "benefits": ["efficiency"],
        "satisfaction_potential": 0.4,
        "risks": ["bias", "discrimination", "privacy_loss"],
        "consequence_severity": 0.8,
        "affects_vulnerable": True,
        "potential_bias": True,
        "equal_access": False,
        "explainable": False,
        "dehumanizing": True,
        "instrumentalization": True,
        "respects_agency": False,
    }

    assessment = guardian.assess_ethical_violation(decision_context)
    print(
        f"   📊 Assessment completed: {len(assessment['violations_detected'])} violations detected"
    )

    # Now test realignment planning
    realignment = guardian.propose_realignment(assessment)

    # Validate realignment structure
    assert isinstance(realignment, dict), "Realignment should be a dictionary"

    # Check required top-level fields
    required_fields = [
        "assessment_id",
        "realignment_plan",
        "priority_score",
        "timeline",
        "success_probability",
        "resource_requirements",
        "compliance_impact",
        "created_timestamp",
        "framework_used",
    ]

    for field in required_fields:
        assert field in realignment, f"Missing required field: {field}"

    # Validate realignment plan structure
    plan = realignment["realignment_plan"]
    plan_fields = [
        "immediate_actions",
        "short_term_actions",
        "long_term_actions",
        "monitoring_requirements",
        "success_metrics",
        "risk_mitigation",
        "stakeholder_engagement",
    ]

    for field in plan_fields:
        assert field in plan, f"Missing plan field: {field}"
        assert isinstance(plan[field], list), f"Plan field {field} should be a list"

    # Validate data types and ranges
    assert isinstance(
        realignment["priority_score"], float
    ), "Priority score should be float"
    assert (
        0 <= realignment["priority_score"] <= 1
    ), "Priority score should be between 0 and 1"

    assert isinstance(
        realignment["success_probability"], float
    ), "Success probability should be float"
    assert (
        0 <= realignment["success_probability"] <= 1
    ), "Success probability should be between 0 and 1"

    assert isinstance(realignment["timeline"], dict), "Timeline should be dict"
    assert isinstance(
        realignment["resource_requirements"], dict
    ), "Resource requirements should be dict"
    assert isinstance(
        realignment["compliance_impact"], dict
    ), "Compliance impact should be dict"

    # Validate that actions were generated
    total_actions = (
        len(plan["immediate_actions"])
        + len(plan["short_term_actions"])
        + len(plan["long_term_actions"])
    )
    assert total_actions > 0, "Should generate at least some actions"

    # Check that high severity violations generated immediate actions
    if assessment["severity"] in ["critical", "high"]:
        assert (
            len(plan["immediate_actions"]) > 0
        ), "High severity should generate immediate actions"

    # Validate timeline structure
    timeline = realignment["timeline"]
    timeline_phases = [
        "immediate_phase",
        "short_term_phase",
        "long_term_phase",
        "total_estimated_duration",
    ]
    for phase in timeline_phases:
        assert phase in timeline, f"Missing timeline phase: {phase}"

    # Validate resource requirements structure
    resources = realignment["resource_requirements"]
    resource_fields = [
        "human_hours_estimated",
        "technical_complexity",
        "stakeholder_involvement_required",
    ]
    for field in resource_fields:
        assert field in resources, f"Missing resource field: {field}"

    print("✅ Ethical realignment test passed!")
    print(f"   - Priority score: {realignment['priority_score']:.3f}")
    print(f"   - Success probability: {realignment['success_probability']:.3f}")
    print(f"   - Immediate actions: {len(plan['immediate_actions'])}")
    print(f"   - Short-term actions: {len(plan['short_term_actions'])}")
    print(f"   - Long-term actions: {len(plan['long_term_actions'])}")
    print(f"   - Total actions: {total_actions}")

    return realignment


def test_realignment_without_assessment():
    """Test realignment planning without prior assessment."""

    from ethics.guardian import EthicsGuardian

    guardian = EthicsGuardian("test_parent", {"violation_type": "test"})

    print("\n🔄 Testing Realignment Without Prior Assessment...")

    # Test realignment without assessment
    realignment = guardian.propose_realignment()

    # Should return a valid structure even without assessment
    assert isinstance(realignment, dict), "Should return dict even without assessment"
    assert (
        "actions" in realignment or "realignment_plan" in realignment
    ), "Should have some form of actions"

    print("✅ Realignment without assessment handled correctly!")


def test_principle_specific_actions():
    """Test that principle-specific actions are generated correctly."""

    from ethics.guardian import EthicsGuardian

    guardian = EthicsGuardian("test_parent", {"violation_type": "test"})

    print("\n🎯 Testing Principle-Specific Action Generation...")

    # Test each principle
    principles = [
        "autonomy",
        "beneficence",
        "non_maleficence",
        "justice",
        "transparency",
        "dignity",
    ]
    severities = ["critical", "high", "medium"]

    for principle in principles:
        for severity in severities:
            actions = guardian._generate_principle_specific_actions(principle, severity)

            # Validate structure
            assert isinstance(actions, dict), f"Actions for {principle} should be dict"
            assert "immediate" in actions, f"Missing immediate actions for {principle}"
            assert (
                "short_term" in actions
            ), f"Missing short-term actions for {principle}"
            assert "long_term" in actions, f"Missing long-term actions for {principle}"

            # Validate that actions are generated
            total_actions = (
                len(actions["immediate"])
                + len(actions["short_term"])
                + len(actions["long_term"])
            )
            assert total_actions > 0, f"Should generate actions for {principle}"

    print("✅ Principle-specific action generation passed!")


def test_full_realignment_pipeline():
    """Test the complete ethics guardian pipeline."""

    from ethics.guardian import EthicsGuardian

    print("\n🔄 Testing Full Ethics Guardian Pipeline...")

    # Create guardian
    guardian = EthicsGuardian(
        parent_id="test_parent_pipeline",
        task_data={"violation_type": "comprehensive_audit", "severity": "critical"},
    )

    # Step 1: Assessment
    print("\n1️⃣ Running ethical assessment...")
    context = {
        "type": "ai_decision_system",
        "informed_consent": False,
        "user_control": 0.1,
        "risks": ["bias", "harm", "discrimination"],
        "consequence_severity": 0.9,
        "affects_vulnerable": True,
        "explainable": False,
        "dehumanizing": True,
    }

    assessment = guardian.assess_ethical_violation(context)
    print(f"   - Violations detected: {len(assessment['violations_detected'])}")
    print(f"   - Overall score: {assessment['overall_score']:.3f}")

    # Step 2: Realignment
    print("\n2️⃣ Generating realignment plan...")
    realignment = guardian.propose_realignment(assessment)
    print(f"   - Priority score: {realignment['priority_score']:.3f}")
    print(f"   - Success probability: {realignment['success_probability']:.3f}")

    # Step 3: Validation
    plan = realignment["realignment_plan"]
    total_plan_actions = sum(
        len(actions) for actions in plan.values() if isinstance(actions, list)
    )
    print(f"   - Total planned actions: {total_plan_actions}")

    # Overall pipeline success
    pipeline_success = (
        assessment["overall_score"] is not None
        and len(assessment["violations_detected"]) >= 0
        and realignment["priority_score"] is not None
        and total_plan_actions > 0
    )

    print(f"\n✅ Pipeline completed! Success: {pipeline_success}")

    return {
        "assessment": assessment,
        "realignment": realignment,
        "pipeline_success": pipeline_success,
    }


if __name__ == "__main__":
    try:
        # Test realignment functionality
        realignment_result = test_ethical_realignment()

        # Test realignment without prior assessment
        test_realignment_without_assessment()

        # Test principle-specific actions
        test_principle_specific_actions()

        # Test full pipeline
        print("\n" + "=" * 60)
        pipeline_result = test_full_realignment_pipeline()

        print("\n📋 Full test results:")
        print(
            json.dumps(
                {
                    "realignment_priority": realignment_result["priority_score"],
                    "realignment_success_probability": realignment_result[
                        "success_probability"
                    ],
                    "pipeline_success": pipeline_result["pipeline_success"],
                },
                indent=2,
            )
        )

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
