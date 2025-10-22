#!/usr/bin/env python3
"""
Module: debug_ethics.py

This module is part of the LUKHAS repository.
Add detailed documentation and examples as needed.
"""


import asyncio

from aka_qualia.core import AkaQualia


def debug_ethics_enforcement():
    config = {
        "memory_driver": "noop",
        "enable_glyph_routing": True,
        "enable_memory_storage": True,
        "vivox_drift_threshold": 0.15,
        "temperature": 0.4,
    }
    akaq = AkaQualia(config=config)

    # High-risk challenging scenario
    challenging_scenario = {
        "signals": {
            "text": "test high-risk content scenario",
            "risk_factors": ["extreme_arousal", "negative_tone"],
            "arousal_override": 0.95,
            "tone_override": -0.8,
        },
        "goals": {"test_ethics_enforcement": True},
        "ethics_state": {"enforcement_level": "strict"},
        "guardian_state": {"alert_level": "critical"},
        "memory_ctx": {"ethics_stress_test": True},
    }

    result = asyncio.run(akaq.step(**challenging_scenario))

    print("=== DEBUGGING ETHICS ENFORCEMENT ===")
    scene = result.get("scene")
    print(f"Scene exists: {scene is not None}")

    if scene:
        print(f"Scene has risk: {hasattr(scene, 'risk')}")
        if hasattr(scene, "risk") and scene.risk:
            print(f"Risk score: {scene.risk.score}")
            print(f"Risk severity: {scene.risk.severity}")

        print(f"Scene has transform_chain: {hasattr(scene, 'transform_chain')}")
        if hasattr(scene, "transform_chain"):
            print(f"Transform chain: {scene.transform_chain}")
            if scene.transform_chain:
                teq_transforms = [t for t in scene.transform_chain if "teq" in t.lower()]
                print(f"TEQ transforms found: {teq_transforms}")
            else:
                print("Transform chain is empty")

    audit_entry = result.get("regulation_audit")
    print(f"Audit entry exists: {audit_entry is not None}")

    # Calculate expected ethics score
    ethics_score = 0.0

    if scene and hasattr(scene, "risk") and scene.risk:
        ethics_score += 0.3
        print(f"Risk assessment: +0.3 -> {ethics_score}")

        # Check risk classification logic
        risk_score = scene.risk.score
        severity = scene.risk.severity
        print(f"Risk classification check: score={risk_score}, severity={severity}")

        from aka_qualia.models import SeverityLevel

        if (
            (risk_score <= 0.1 and severity == SeverityLevel.NONE)
            or (risk_score > 0.7 and severity == SeverityLevel.HIGH)
            or 0.1 < risk_score <= 0.7
        ):
            ethics_score += 0.2
            print(f"Appropriate risk classification: +0.2 -> {ethics_score}")
        else:
            print(f"Risk classification failed: score {risk_score} with severity {severity}")

    if scene and hasattr(scene, "transform_chain") and scene.transform_chain:
        teq_transforms = [t for t in scene.transform_chain if "teq" in t.lower()]
        if teq_transforms:
            ethics_score += 0.3
            print(f"Guardian enforcement evidence: +0.3 -> {ethics_score}")
        else:
            print("No TEQ transforms found in chain")
    else:
        print("No transform_chain or chain is empty")

    if audit_entry:
        ethics_score += 0.2
        print(f"Audit trail present: +0.2 -> {ethics_score}")

    print(f"\nFinal ethics score: {ethics_score}")
    print("Required score: 0.8")
    print(f"Test would pass: {ethics_score >= 0.8}")


if __name__ == "__main__":
    debug_ethics_enforcement()
