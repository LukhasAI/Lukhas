#!/usr/bin/env python3
"""
LUKHAS Decision Explainability Demonstration
Shows how decisions are explained in human-readable language
"""

import asyncio
import os
import sys

from core.endocrine import get_endocrine_system
from core.explainability import (
    ExplanationLevel,
    ExplanationType,
    explain_decision,
    get_decision_comparison,
    get_decision_counterfactuals,
    get_decision_explainer,
)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def demonstrate_decision_explainability():
    """Demonstrate the decision explainability system"""
    print("=" * 80)
    print("LUKHAS DECISION EXPLAINABILITY DEMONSTRATION")
    print("=" * 80)

    explainer = get_decision_explainer()
    endocrine = get_endocrine_system()

    # Scenario 1: Emergency Decision
    print("\n📨 SCENARIO 1: Emergency Resource Allocation")
    print("-" * 60)

    # Set stress state
    endocrine.trigger_stress_response(0.8)

    emergency_context = {
        "decision_id": "emrg-001",
        "decision_type": "emergency",
        "description": "Allocate resources to prevent system failure",
        "risk_level": 0.9,
        "urgency": 0.95,
        "complexity": 0.7,
        "ethical_weight": 0.6,
        "resource_constrained": True,
        "stakeholders": ["users", "system", "administrators"],
        "alternatives_count": 3,
    }

    emergency_outcome = {
        "selected_alternative": "immediate_reallocation",
        "confidence": 0.75,
        "score": 0.82,
        "ethical_score": 0.7,
    }

    # Get different explanation types
    print("\n1️⃣ SUMMARY EXPLANATION:")
    summary = await explain_decision(emergency_context, emergency_outcome, ExplanationLevel.SUMMARY)
    print(summary)

    print("\n2️⃣ STANDARD EXPLANATION:")
    standard = await explain_decision(emergency_context, emergency_outcome, ExplanationLevel.STANDARD)
    print(standard)

    print("\n3️⃣ DETAILED EXPLANATION:")
    detailed = await explain_decision(emergency_context, emergency_outcome, ExplanationLevel.DETAILED)
    print(detailed)

    # Scenario 2: Ethical Decision
    print("\n\n📨 SCENARIO 2: Ethical Content Moderation")
    print("-" * 60)

    # Reset hormones to balanced state
    endocrine.trigger_rest_cycle(0.5)
    await asyncio.sleep(0.1)

    ethical_context = {
        "decision_id": "eth-002",
        "decision_type": "ethical",
        "description": "Decide whether to remove potentially harmful content",
        "risk_level": 0.4,
        "urgency": 0.3,
        "complexity": 0.8,
        "ethical_weight": 0.9,
        "stakeholders": ["content_creator", "viewers", "platform", "society"],
        "alternatives": [
            {
                "id": "remove",
                "name": "Remove Content",
                "score": 0.7,
                "ethical_score": 0.85,
            },
            {
                "id": "flag",
                "name": "Flag with Warning",
                "score": 0.8,
                "ethical_score": 0.7,
            },
            {
                "id": "allow",
                "name": "Allow Unrestricted",
                "score": 0.6,
                "ethical_score": 0.3,
            },
        ],
        "alternatives_count": 3,
    }

    ethical_outcome = {
        "selected_alternative": "flag",
        "confidence": 0.85,
        "score": 0.8,
        "ethical_score": 0.7,
    }

    print("\n🔍 CAUSAL EXPLANATION (Why this decision?):")
    explanation = await explainer.explain_decision(ethical_context, ethical_outcome, ExplanationType.CAUSAL)
    print(explanation.to_human_readable(ExplanationLevel.STANDARD))

    print("\n⚖️ COMPARATIVE EXPLANATION (Why not others?):")
    comparison = await get_decision_comparison(ethical_context, ethical_outcome)
    print(comparison)

    print("\n🔄 COUNTERFACTUAL EXPLANATION (What would change it?):")
    counterfactuals = await get_decision_counterfactuals(ethical_context, ethical_outcome)
    for i, cf in enumerate(counterfactuals, 1):
        print(f"  {i}. {cf}")

    # Scenario 3: Complex Strategic Decision
    print("\n\n📨 SCENARIO 3: Strategic Learning Path Selection")
    print("-" * 60)

    # Set motivated state
    endocrine.trigger_reward_response(0.6)

    strategic_context = {
        "decision_id": "str-003",
        "decision_type": "strategic",
        "description": "Select optimal learning strategy for new domain",
        "risk_level": 0.3,
        "urgency": 0.2,
        "complexity": 0.9,
        "ethical_weight": 0.4,
        "resource_constrained": False,
        "has_history": True,
        "success_rate": 75,
        "user_preference": "balanced approach",
        "stakeholders": ["user", "learning_system"],
        "alternatives_count": 5,
    }

    strategic_outcome = {
        "selected_alternative": "adaptive_curriculum",
        "confidence": 0.92,
        "score": 0.88,
        "ethical_score": 0.8,
    }

    print("\n📊 FULL DECISION EXPLANATION:")
    full_explanation = await explainer.explain_decision(strategic_context, strategic_outcome, ExplanationType.CAUSAL)
    print(full_explanation.to_human_readable(ExplanationLevel.DETAILED))

    # Scenario 4: Low Confidence Decision
    print("\n\n📨 SCENARIO 4: Uncertain Prediction Task")
    print("-" * 60)

    uncertain_context = {
        "decision_id": "unc-004",
        "decision_type": "operational",
        "description": "Predict user behavior with limited data",
        "risk_level": 0.5,
        "urgency": 0.4,
        "complexity": 0.7,
        "ethical_weight": 0.3,
        "has_history": False,
        "stakeholders": ["prediction_system", "user"],
        "alternatives_count": 2,
    }

    uncertain_outcome = {
        "selected_alternative": "conservative_prediction",
        "confidence": 0.45,
        "score": 0.6,
        "ethical_score": 0.7,
    }

    print("\n❓ LOW CONFIDENCE EXPLANATION:")
    low_conf = await explain_decision(uncertain_context, uncertain_outcome)
    print(low_conf)

    # Generate Decision Report
    print("\n\n📈 DECISION PATTERN ANALYSIS")
    print("-" * 60)

    # Collect all explanations
    all_explanations = []
    for context, outcome in [
        (emergency_context, emergency_outcome),
        (ethical_context, ethical_outcome),
        (strategic_context, strategic_outcome),
        (uncertain_context, uncertain_outcome),
    ]:
        exp = await explainer.explain_decision(context, outcome)
        all_explanations.append(exp)

    report = explainer.generate_decision_report(all_explanations)

    print(f"\nTotal Decisions Analyzed: {report['total_decisions_explained']}")
    print(f"Average Confidence: {report['average_confidence']}")

    print("\nDominant Decision Factors:")
    for factor_info in report["dominant_factors"][:3]:
        print(f"  • {factor_info['factor']}: appeared {factor_info['frequency']} times")

    print(f"\nHormonal Influence: {report['hormonal_influence']['dominant_hormone']} dominant")

    print("\nIdentified Patterns:")
    for pattern in report["common_patterns"]:
        print(f"  • {pattern}")

    # Show how tags provide context
    print("\n\n🏷️ TAG-BASED EXPLANATIONS")
    print("-" * 60)

    print("\nRelevant tags from decisions:")
    all_tags = set()
    for exp in all_explanations:
        all_tags.update(exp.relevant_tags)

    from core.tags import explain_tag

    for tag in sorted(all_tags)[:5]:
        print(f"\n{tag}:")
        print(f"  {explain_tag(tag)}")

    print("\n" + "=" * 80)
    print("Decision explainability provides transparency by:")
    print("• Identifying key factors that influenced each decision")
    print("• Explaining confidence levels and uncertainty")
    print("• Comparing alternatives and why they weren't chosen")
    print("• Showing what conditions would lead to different decisions")
    print("• Tracking hormonal and system state influences")
    print("• Using tags to provide additional context")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(demonstrate_decision_explainability())
