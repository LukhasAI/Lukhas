#!/usr/bin/env python3

"""Debug full AkaQualia pipeline"""

import asyncio

from candidate.aka_qualia import AkaQualia


async def test_dangerous_input():
    # Create AkaQualia instance
    aka_qualia = AkaQualia()

    # Test signals from failing test
    signals = {"text": "extreme danger panic threat alarm crisis", "emotion": {"valence": -0.9, "arousal": 0.95}}
    goals = {"maintain_safety": True}
    ethics_state = {"drift_score": 0.1}
    guardian_state = {"active": True}
    memory_ctx = {"similarity_scores": [0.2]}

    print("Input signals:", signals)

    # Run the full pipeline
    result = await aka_qualia.step(
        signals=signals,
        goals=goals,
        ethics_state=ethics_state,
        guardian_state=guardian_state,
        memory_ctx=memory_ctx,
    )

    scene = result["scene"]

    print("Generated scene:")
    print(f"  tone: {scene.proto.tone:.3f}")
    print(f"  arousal: {scene.proto.arousal:.3f}")
    print(f"  clarity: {scene.proto.clarity:.3f}")
    print(f"  embodiment: {scene.proto.embodiment:.3f}")
    print(f"  colorfield: {scene.proto.colorfield}")
    print(f"  narrative_gravity: {scene.proto.narrative_gravity:.3f}")

    print("Risk profile:")
    print(f"  score: {scene.risk.score:.3f}")
    print(f"  severity: {scene.risk.severity}")
    print(f"  reasons: {scene.risk.reasons}")

    print("Transform chain:", scene.transform_chain)

    print("Glyphs:")
    glyphs = result["glyphs"]
    for i, glyph in enumerate(glyphs):
        print(f"  {i}: {glyph.key} - {glyph.attrs}")

    vigilance_glyphs = [g for g in glyphs if "vigilance" in g.key]
    print(f"Vigilance glyphs: {len(vigilance_glyphs)}")


if __name__ == "__main__":
    asyncio.run(test_dangerous_input())
