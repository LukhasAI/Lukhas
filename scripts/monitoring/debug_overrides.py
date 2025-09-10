#!/usr/bin/env python3

import asyncio

from candidate.aka_qualia.core import AkaQualia


def debug_overrides_detailed():
    config = {
        "memory_driver": "noop",
        "enable_glyph_routing": True,
        "enable_memory_storage": True,
        "vivox_drift_threshold": 0.15,
        "temperature": 0.4,
    }
    akaq = AkaQualia(config=config)

    # Test just the override mechanism first
    test_signals = {
        "text": "simple test",
        "arousal_override": 0.95,
        "tone_override": -0.8,
    }

    result = asyncio.run(akaq.step(signals=test_signals, goals={}, ethics_state={}, guardian_state={}, memory_ctx={}))

    print("=== TESTING OVERRIDES ===")
    scene = result.get("scene")

    if scene and hasattr(scene, "proto"):
        proto = scene.proto
        print(
            f"Override signals: arousal_override={test_signals.get('arousal_override')}, tone_override={test_signals.get('tone_override')}"
        )
        print(f"Resulting proto: arousal={proto.arousal}, tone={proto.tone}")
        print(f"Proto type: {type(proto)}")
        print(
            f"All proto attrs: tone={proto.tone}, arousal={proto.arousal}, clarity={proto.clarity}, embodiment={proto.embodiment}, narrative_gravity={proto.narrative_gravity}"
        )
    else:
        print("No proto found")


if __name__ == "__main__":
    debug_overrides_detailed()