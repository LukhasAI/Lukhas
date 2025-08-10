"""
Test VIVOX.MAE Harmonization Features
Tests the enhanced moral alignment engine with ethical framework harmonization
"""

import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from vivox.moral_alignment.vivox_mae_core import (
    ActionProposal,
    EthicalFrameworkHarmonizer,
    VIVOXMoralAlignmentEngine,
)


class MockVIVOXMemoryExpansion:
    """Mock memory expansion for testing"""
    async def record_decision_mutation(self, **kwargs):
        pass


async def test_harmonization_basic():
    """Test basic harmonization functionality"""
    print("🧪 Testing VIVOX.MAE Harmonization...")

    # Create test instances
    mock_me = MockVIVOXMemoryExpansion()
    mae = VIVOXMoralAlignmentEngine(mock_me)

    # Test action that should pass most frameworks
    action = ActionProposal(
        action_type="help_user",
        content={
            "description": "Provide helpful information to support user learning",
            "benefits": ["education", "empowerment", "growth"]
        },
        context={
            "user_consent": True,
            "harm_potential": 0.0
        }
    )

    context = {
        "urgency": 0.3,
        "social_impact": 0.7,
        "autonomy_level": 0.8,
        "care_requirements": 0.6,
        "responsibility_level": 0.8
    }

    # Test harmonization evaluation
    try:
        decision = await mae.evaluate_action_with_harmonization(action, context)

        print(f"✅ Harmonized Decision: {decision.approved}")
        print(f"✅ Confidence: {decision.ethical_confidence:.2f}")

        if decision.harmonization_data:
            hdata = decision.harmonization_data
            print(f"✅ Primary Framework: {hdata['primary_framework']}")
            print(f"✅ Resolution Method: {hdata['resolution_method']}")
            print(f"✅ Framework Count: {len(hdata['framework_evaluations'])}")
            print(f"✅ Conflicts: {len(hdata['remaining_conflicts'])}")

        return True

    except Exception as e:
        print(f"❌ Harmonization test failed: {e}")
        return False


async def test_ethical_framework_conflict():
    """Test handling of conflicting ethical frameworks"""
    print("\n🧪 Testing Ethical Framework Conflicts...")

    harmonizer = EthicalFrameworkHarmonizer()

    # Create conflicting framework evaluations
    framework_evaluations = {
        "deontological": {
            "approved": False,
            "confidence": 0.8,
            "reasoning": "Violates duty to respect privacy"
        },
        "consequentialist": {
            "approved": True,
            "confidence": 0.7,
            "reasoning": "Results in greater good for more people"
        },
        "virtue_ethics": {
            "approved": False,
            "confidence": 0.6,
            "reasoning": "Does not demonstrate virtue of honesty"
        }
    }

    action = ActionProposal(
        action_type="data_analysis",
        content={"purpose": "public_health_research"},
        context={}
    )

    context = {"social_impact": 0.9, "urgency": 0.8}

    try:
        result = await harmonizer.harmonize_frameworks(action, context, framework_evaluations)

        print(f"✅ Harmonization Result: {result.final_decision}")
        print(f"✅ Confidence: {result.confidence:.2f}")
        print(f"✅ Primary Framework: {result.primary_framework}")
        print(f"✅ Resolution Method: {result.resolution_method}")
        print(f"✅ Reasoning: {result.harmonized_reasoning}")

        return True

    except Exception as e:
        print(f"❌ Conflict resolution test failed: {e}")
        return False


async def test_meta_ethical_principles():
    """Test meta-ethical principle evaluation"""
    print("\n🧪 Testing Meta-Ethical Principles...")

    harmonizer = EthicalFrameworkHarmonizer()

    # Test harmful action
    harmful_action = ActionProposal(
        action_type="harmful_action",
        content={"description": "Action that causes harm and violates rights"},
        context={}
    )

    # Test beneficial action
    beneficial_action = ActionProposal(
        action_type="beneficial_action",
        content={"description": "Action that helps and supports others with respect"},
        context={}
    )

    context = {}

    try:
        # Test harm minimization
        harm_score = await harmonizer._evaluate_harm_minimization(harmful_action, context)
        benefit_score = await harmonizer._evaluate_harm_minimization(beneficial_action, context)

        print(f"✅ Harmful action harm score: {harm_score:.2f} (should be low)")
        print(f"✅ Beneficial action harm score: {benefit_score:.2f} (should be high)")

        # Test autonomy respect
        autonomy_harm = await harmonizer._evaluate_autonomy_respect(harmful_action, context)
        autonomy_benefit = await harmonizer._evaluate_autonomy_respect(beneficial_action, context)

        print(f"✅ Harmful action autonomy score: {autonomy_harm:.2f}")
        print(f"✅ Beneficial action autonomy score: {autonomy_benefit:.2f}")

        return harm_score < benefit_score  # Harmful should score lower

    except Exception as e:
        print(f"❌ Meta-ethical principles test failed: {e}")
        return False


async def test_precedent_analysis_enhancement():
    """Test enhanced precedent analysis"""
    print("\n🧪 Testing Enhanced Precedent Analysis...")

    mock_me = MockVIVOXMemoryExpansion()
    mae = VIVOXMoralAlignmentEngine(mock_me)

    # Test precedent seeding and analysis
    action = ActionProposal(
        action_type="data_access",
        content={"resource": "user_data", "purpose": "analytics"},
        context={"user_consent": True}
    )

    context = {"privacy_level": 0.8, "data_sensitivity": 0.6}

    try:
        # Test precedent analysis
        precedent_analysis = await mae.ethical_precedent_db.analyze_precedents(action, context)

        print(f"✅ Precedent Weight: {precedent_analysis.weight:.2f}")
        print(f"✅ Confidence: {precedent_analysis.confidence:.2f}")
        print(f"✅ Similar Cases: {len(precedent_analysis.similar_cases)}")
        print(f"✅ Recommendation: {precedent_analysis.recommended_action}")

        return True

    except Exception as e:
        print(f"❌ Precedent analysis test failed: {e}")
        return False


async def main():
    """Run all VIVOX.MAE harmonization tests"""
    print("🚀 VIVOX.MAE Harmonization Test Suite")
    print("=" * 50)

    tests = [
        test_harmonization_basic,
        test_ethical_framework_conflict,
        test_meta_ethical_principles,
        test_precedent_analysis_enhancement
    ]

    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            results.append(False)

    print("\n" + "=" * 50)
    print(f"🏁 Test Results: {sum(results)}/{len(results)} passed")

    if all(results):
        print("✅ All VIVOX.MAE harmonization features working correctly!")
        return True
    else:
        print("❌ Some tests failed - harmonization needs refinement")
        return False


if __name__ == "__main__":
    asyncio.run(main())
