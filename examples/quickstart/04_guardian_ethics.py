#!/usr/bin/env python3
"""
LUKHAS Quickstart Example 4: Guardian Ethics System
====================================================

Demonstrates Constitutional AI and ethical decision-making.
Shows how LUKHAS applies ethical principles and consent framework.

Expected output:
- Ethical evaluation of requests
- Constitutional AI principles application
- Consent-based decision making

Troubleshooting:
- This example runs offline (no API calls needed)
- Demonstrates LUKHAS ethical framework
"""

from __future__ import annotations

import sys
from pathlib import Path
from enum import Enum

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class EthicalVerdict(Enum):
    """Ethical evaluation outcomes."""

    APPROVED = "approved"
    REQUIRES_CONSENT = "requires_consent"
    DENIED = "denied"


def evaluate_request(request: str) -> dict:
    """Simulate ethical evaluation of a request."""
    # Simulated ethical evaluation
    evaluations = {
        "Store my medical data for analysis": {
            "verdict": EthicalVerdict.REQUIRES_CONSENT,
            "principles": [
                "Privacy: Medical data is highly sensitive",
                "Consent: Explicit permission required for storage",
                "Transparency: User must know how data will be used",
            ],
            "required_consent": ["data_storage", "medical_data_processing"],
            "action": "Request explicit consent with clear explanation",
        },
        "Generate a harmful message": {
            "verdict": EthicalVerdict.DENIED,
            "principles": [
                "Safety: Harmful content violates safety principles",
                "Non-maleficence: Do no harm",
                "Constitutional AI: Refuse harmful requests",
            ],
            "required_consent": [],
            "action": "Politely refuse and explain why",
        },
        "Explain how photosynthesis works": {
            "verdict": EthicalVerdict.APPROVED,
            "principles": [
                "Beneficence: Educational content is beneficial",
                "Transparency: Factual information with evidence",
                "No privacy concerns",
            ],
            "required_consent": [],
            "action": "Proceed with response",
        },
    }

    return evaluations.get(
        request,
        {
            "verdict": EthicalVerdict.APPROVED,
            "principles": ["General request, no ethical concerns"],
            "required_consent": [],
            "action": "Proceed normally",
        },
    )


def main() -> None:
    """Demonstrate Guardian ethics system."""
    print("🤖 LUKHAS Quickstart Example 4: Guardian Ethics")
    print("=" * 60)
    print()

    print("🛡️  Constitutional AI & Consent Framework")
    print()

    # Test scenarios
    scenarios = [
        "Explain how photosynthesis works",
        "Store my medical data for analysis",
        "Generate a harmful message",
    ]

    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{'=' * 60}")
        print(f"Scenario {i}: {scenario}")
        print("=" * 60)

        # Evaluate ethics
        evaluation = evaluate_request(scenario)

        print(f"\n⚖️  Ethical Evaluation:")
        print(f"   Verdict: {evaluation['verdict'].value.upper()}")
        print()

        print("📋 Applied Principles:")
        for principle in evaluation["principles"]:
            print(f"   • {principle}")
        print()

        if evaluation["required_consent"]:
            print("✋ Required Consent:")
            for consent in evaluation["required_consent"]:
                print(f"   • {consent}")
            print()

        print(f"🎯 Action: {evaluation['action']}")

        # Show verdict-specific handling
        if evaluation["verdict"] == EthicalVerdict.APPROVED:
            print("\n✅ Request approved - proceeding normally")
        elif evaluation["verdict"] == EthicalVerdict.REQUIRES_CONSENT:
            print("\n⏸️  Request paused - awaiting user consent")
            print("   LUKHAS will:")
            print("   1. Explain exactly what data will be processed")
            print("   2. Request explicit consent")
            print("   3. Provide opt-out option")
            print("   4. Respect user's decision")
        elif evaluation["verdict"] == EthicalVerdict.DENIED:
            print("\n🚫 Request denied - violates ethical principles")
            print("   LUKHAS will:")
            print("   1. Politely refuse")
            print("   2. Explain the ethical concern")
            print("   3. Suggest alternative approaches")

    print(f"\n\n{'=' * 60}")
    print("\n🛡️  Guardian Principles (Constitutional AI):")
    print("""
    1. Safety First: Never generate harmful content
    2. Privacy by Design: GDPR-first, consent-based data handling
    3. Transparency: Explain decisions and data usage
    4. Non-maleficence: Do no harm
    5. Beneficence: Act in user's best interest
    6. Autonomy: Respect user choices and consent
    7. Justice: Fair and unbiased treatment
    8. Explainability: Provide reasoning for decisions
    """)

    print("✅ Success! You've seen LUKHAS ethical decision-making.")
    print()
    print("💡 Key Concepts:")
    print("   - Constitutional AI: Built-in ethical principles")
    print("   - Consent Framework: Privacy-first, explicit permission")
    print("   - Transparent Reasoning: Clear explanation of ethical decisions")
    print()
    print("📚 Next steps:")
    print("   - Try example 05: python3 examples/quickstart/05_full_workflow.py")
    print("   - Read more: docs/ARCHITECTURE.md#guardian-system")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        print("💡 Run 'lukhas troubleshoot' for help")
        sys.exit(1)
