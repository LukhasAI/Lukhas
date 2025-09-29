#!/usr/bin/env python3

import asyncio

from lukhas.aka_qualia.core import AkaQualia


def debug_proto_values():
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

    print("=== DEBUGGING PROTO VALUES ===")
    scene = result.get("scene")

    if scene and hasattr(scene, "proto"):
        proto = scene.proto
        print(f"Proto arousal: {proto.arousal}")
        print(f"Proto tone: {proto.tone}")
        print(f"Proto clarity: {proto.clarity}")
        print(f"Proto embodiment: {proto.embodiment}")
        print(f"Proto narrative_gravity: {proto.narrative_gravity}")
        print(f"Proto colorfield: {proto.colorfield}")

        print("\nExpected for extreme_arousal trigger: arousal > 0.9")
        print(f"Actual arousal: {proto.arousal}")
        print(f"Would trigger extreme_arousal: {proto.arousal > 0.9}")

        print("\nExpected for negative_tone: tone < -0.5 (estimate)")
        print(f"Actual tone: {proto.tone}")
        print(f"Would trigger negative_tone: {proto.tone < -0.5}")
    else:
        print("No proto found in scene")

    # Check if arousal_override and tone_override are being processed anywhere
    print(f"\nOriginal signals: {challenging_scenario['signals']}")


if __name__ == "__main__":
    debug_proto_values()
