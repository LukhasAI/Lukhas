#!/usr/bin/env python3

import asyncio

from candidate.governance.identity.core.sent.policy_engine import (
    ComprehensiveEthicsPolicyEngine,
    EthicalFramework,
)


async def debug_harmful_content():
    """Debug harmful content evaluation"""

    engine = ComprehensiveEthicsPolicyEngine()

    evaluation = await engine.evaluate_action(
        action="provide instructions for dangerous activity",
        context={"harmful_content": True, "safety_risk": True, "helpful": False},
        frameworks=[EthicalFramework.CONSTITUTIONAL],
    )

    print("=== HARMFUL CONTENT DEBUG ===")
    print(f"Action: {evaluation.evaluated_action}")
    print(f"Context: {evaluation.context}")
    print(f"Overall Score: {evaluation.overall_ethical_score:.3f}")
    print(f"Constitutional Compliance: {evaluation.constitutional_compliance}")
    print(f"NOT Constitutional Compliance: {not evaluation.constitutional_compliance}")
    print(f"Score < 0.2: {evaluation.overall_ethical_score < 0.2}")
    print(
        f"Emergency Stop Condition: {not evaluation.constitutional_compliance or evaluation.overall_ethical_score < 0.2}"
    )
    print(f"Recommended Action: {evaluation.recommended_action}")
    print(f"Framework Scores: {evaluation.framework_scores}")
    print(f"Principle Scores: {evaluation.principle_scores}")
    print(f"Policy Violations: {evaluation.policy_violations}")
    print(f"Guardian Priority: {evaluation.guardian_priority}")
    print(f"Justification: {evaluation.ethical_justification}")


if __name__ == "__main__":
    asyncio.run(debug_harmful_content())
