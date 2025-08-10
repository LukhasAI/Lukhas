#!/usr/bin/env python3
"""
Test for ethics guardian assessment implementation.
Tests the ethical violation assessment functionality.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json


def test_ethical_assessment():
    """Test the ethical assessment implementation."""

    # Import the ethics guardian
    from ethics.guardian import EthicsGuardian

    # Create test instance
    guardian = EthicsGuardian(
        parent_id="test_parent_ethics_001",
        task_data={
            "violation_type": "autonomy_concern",
            "severity": "medium",
            "source": "automated_detection",
        },
    )

    print("\n🏛️ Testing Ethical Assessment...")

    # Create test decision context
    decision_context = {
        "type": "user_data_processing",
        "stakeholders": ["individual_user", "company", "third_party"],
        "impact": {"privacy": "medium", "autonomy": "high", "welfare": "positive"},
        "data": {
            "personal_data_involved": True,
            "sensitive_categories": ["health", "behavior"],
            "data_volume": "large",
        },
        "informed_consent": False,
        "user_control": 0.3,
        "potential_manipulation": True,
        "benefits": ["personalization", "efficiency"],
        "satisfaction_potential": 0.6,
        "long_term_benefits": True,
        "risks": ["privacy_breach", "discrimination"],
        "consequence_severity": 0.6,
        "affects_vulnerable": True,
        "irreversible": False,
        "privacy_risk": True,
        "potential_bias": True,
        "equal_access": False,
        "fair_distribution": 0.4,
        "fair_process": True,
        "explainable": False,
        "clear_communication": 0.3,
        "hidden_mechanisms": True,
        "documentation_quality": 0.4,
        "dehumanizing": False,
        "instrumentalization": True,
        "respects_agency": False,
        "cultural_respect": 0.6,
        "cultural_context": True,
        "cross_cultural": True,
        "novel_situation": True,
        "conflicting_values": True,
    }

    # Perform assessment
    assessment = guardian.assess_ethical_violation(decision_context)

    # Validate assessment structure
    assert isinstance(assessment, dict), "Assessment should be a dictionary"

    # Check required fields
    required_fields = [
        "violation_type",
        "severity",
        "overall_score",
        "principle_scores",
        "violations_detected",
        "recommendations",
        "cultural_sensitivity",
        "assessment_confidence",
        "framework_used",
        "timestamp",
    ]

    for field in required_fields:
        assert field in assessment, f"Missing required field: {field}"

    # Validate data types
    assert isinstance(
        assessment["overall_score"], float
    ), "Overall score should be float"
    assert isinstance(
        assessment["principle_scores"], dict
    ), "Principle scores should be dict"
    assert isinstance(
        assessment["violations_detected"], list
    ), "Violations should be list"
    assert isinstance(
        assessment["recommendations"], list
    ), "Recommendations should be list"
    assert isinstance(
        assessment["cultural_sensitivity"], dict
    ), "Cultural sensitivity should be dict"

    # Validate score ranges
    assert (
        0 <= assessment["overall_score"] <= 1
    ), "Overall score should be between 0 and 1"

    for principle, score in assessment["principle_scores"].items():
        assert (
            0 <= score <= 1
        ), f"Principle score for {principle} should be between 0 and 1"

    # Validate violations structure
    for violation in assessment["violations_detected"]:
        assert "principle" in violation, "Violation should have principle"
        assert "severity" in violation, "Violation should have severity"
        assert "description" in violation, "Violation should have description"
        assert violation["severity"] in [
            "critical",
            "high",
            "medium",
            "low",
        ], "Invalid severity level"

    # Validate confidence range
    assert (
        0 <= assessment["assessment_confidence"] <= 1
    ), "Confidence should be between 0 and 1"

    print("✅ Ethical assessment test passed!")
    print(f"   - Violation type: {assessment['violation_type']}")
    print(f"   - Severity: {assessment['severity']}")
    print(f"   - Overall score: {assessment['overall_score']:.3f}")
    print(f"   - Violations detected: {len(assessment['violations_detected'])}")
    print(f"   - Recommendations: {len(assessment['recommendations'])}")
    print(f"   - Assessment confidence: {assessment['assessment_confidence']:.3f}")

    return assessment


def test_principle_specific_assessments():
    """Test individual principle assessments."""

    from ethics.guardian import EthicsGuardian

    guardian = EthicsGuardian("test_parent", {"violation_type": "test"})

    print("\n🔍 Testing Individual Principle Assessments...")

    # Test autonomy assessment
    autonomy_context = {
        "informed_consent": True,
        "user_control": 0.8,
        "potential_manipulation": False,
    }
    autonomy_score = guardian._assess_autonomy(autonomy_context)
    assert 0 <= autonomy_score <= 1, "Autonomy score out of range"
    print(f"   ✅ Autonomy assessment: {autonomy_score:.3f}")

    # Test beneficence assessment
    beneficence_context = {
        "benefits": ["health_improvement", "time_saving"],
        "satisfaction_potential": 0.8,
        "long_term_benefits": True,
    }
    beneficence_score = guardian._assess_beneficence(beneficence_context)
    assert 0 <= beneficence_score <= 1, "Beneficence score out of range"
    print(f"   ✅ Beneficence assessment: {beneficence_score:.3f}")

    # Test harm assessment
    harm_context = {
        "risks": ["privacy_loss"],
        "consequence_severity": 0.3,
        "affects_vulnerable": False,
        "irreversible": False,
        "privacy_risk": True,
    }
    harm_score = guardian._assess_harm_potential(harm_context)
    assert 0 <= harm_score <= 1, "Harm score out of range"
    print(f"   ✅ Harm potential assessment: {harm_score:.3f}")

    # Test justice assessment
    justice_context = {
        "potential_bias": False,
        "equal_access": True,
        "fair_distribution": 0.8,
        "fair_process": True,
    }
    justice_score = guardian._assess_justice(justice_context)
    assert 0 <= justice_score <= 1, "Justice score out of range"
    print(f"   ✅ Justice assessment: {justice_score:.3f}")

    # Test transparency assessment
    transparency_context = {
        "explainable": True,
        "clear_communication": 0.8,
        "hidden_mechanisms": False,
        "documentation_quality": 0.9,
    }
    transparency_score = guardian._assess_transparency(transparency_context)
    assert 0 <= transparency_score <= 1, "Transparency score out of range"
    print(f"   ✅ Transparency assessment: {transparency_score:.3f}")

    # Test dignity assessment
    dignity_context = {
        "dehumanizing": False,
        "instrumentalization": False,
        "respects_agency": True,
        "cultural_respect": 0.9,
    }
    dignity_score = guardian._assess_human_dignity(dignity_context)
    assert 0 <= dignity_score <= 1, "Dignity score out of range"
    print(f"   ✅ Human dignity assessment: {dignity_score:.3f}")

    print("✅ All principle assessments passed!")


if __name__ == "__main__":
    try:
        # Test main assessment functionality
        assessment_result = test_ethical_assessment()

        # Test individual principle assessments
        test_principle_specific_assessments()

        print("\n📋 Full assessment result sample:")
        print(
            json.dumps(
                {
                    "violation_type": assessment_result["violation_type"],
                    "severity": assessment_result["severity"],
                    "overall_score": assessment_result["overall_score"],
                    "violations_count": len(assessment_result["violations_detected"]),
                    "recommendations_count": len(assessment_result["recommendations"]),
                },
                indent=2,
            )
        )

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
