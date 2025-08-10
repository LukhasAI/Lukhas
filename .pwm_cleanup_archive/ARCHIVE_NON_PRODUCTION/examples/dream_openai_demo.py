#!/usr/bin/env python3
"""
LUKHAS Dream System - OpenAI Integration Demo
Demonstrates the full capabilities of the OpenAI-enhanced dream system
"""

import asyncio
import json

# Add parent directory to path for imports
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from dream.dream_generator import generate_dream_sync
from dream.dream_pipeline import UnifiedDreamPipeline


async def main():
    """Run comprehensive dream generation demo."""

    print("=" * 70)
    print("🌙 LUKHAS DREAM SYSTEM - OpenAI Integration Demo")
    print("=" * 70)
    print()

    # Initialize pipeline
    print("🔧 Initializing dream pipeline...")
    pipeline = UnifiedDreamPipeline(
        user_id="demo_user", output_dir="dream_demo_outputs", use_openai=True
    )

    try:
        # Demo 1: Basic narrative dream
        print("\n📖 Demo 1: Narrative Dream Generation")
        print("-" * 50)

        narrative_dream = await pipeline.generate_dream_from_text(
            "a garden where time flows backwards and flowers sing memories",
            dream_type="narrative",
            context={"mood": "whimsical", "time_of_day": "twilight"},
        )

        print(f"✅ Dream ID: {narrative_dream['dream_id']}")
        if "enhanced_narrative" in narrative_dream:
            narrative_text = narrative_dream["enhanced_narrative"]["full_text"]
            print(f"📝 Narrative Preview: {narrative_text[:200]}...")

        if "generated_image" in narrative_dream:
            print(f"🎨 Image saved: {narrative_dream['generated_image']['path']}")

        if "narration" in narrative_dream:
            print(f"🎙️ Audio narration: {narrative_dream['narration']['path']}")

        if "sora_prompt" in narrative_dream:
            print(f"🎬 SORA video prompt: {narrative_dream['sora_prompt'][:100]}...")

        # Demo 2: Oracle dream
        print("\n\n🔮 Demo 2: Oracle Dream Generation")
        print("-" * 50)

        oracle_dream = await pipeline.generate_dream_from_text(
            "seeking wisdom about creative inspiration",
            dream_type="oracle",
            context={
                "user_state": "contemplative",
                "recent_activity": "artistic_creation",
                "time": "evening",
            },
        )

        print(f"✅ Oracle Dream ID: {oracle_dream['dream_id']}")
        if "message" in oracle_dream:
            print(f"💭 Oracle Message: {oracle_dream['message']}")

        if "ai_enhanced" in oracle_dream and oracle_dream["ai_enhanced"]:
            print("🤖 Dream enhanced with AI")

        # Demo 3: Symbolic dream
        print("\n\n🧬 Demo 3: Symbolic Dream Generation")
        print("-" * 50)

        symbolic_dream = await pipeline.generate_dream_from_text(
            "quantum entanglement of consciousness across parallel realities",
            dream_type="symbolic",
            context={"cognitive_mode": "abstract", "complexity": "high"},
        )

        print(f"✅ Symbolic Dream ID: {symbolic_dream['dream_id']}")
        if "symbolic_elements" in symbolic_dream:
            elements = symbolic_dream["symbolic_elements"]
            print(f"🔮 Primary GLYPH: {elements.get('primary_glyph')}")
            print(f"⚛️ Quantum State: {elements.get('quantum_state')}")
            print(f"📊 Coherence Factor: {elements.get('coherence_factor')}")

        # Demo 4: Voice-simulated dream (using text as mock voice input)
        print("\n\n🎤 Demo 4: Voice-Inspired Dream")
        print("-" * 50)

        # Simulate voice input with descriptive text
        voice_inspired = await pipeline.generate_dream_from_text(
            "I had a dream where I was flying over cities made of music notes",
            dream_type="narrative",
            context={"source": "voice_description", "emotion": "euphoric"},
        )

        print(f"✅ Voice-inspired Dream ID: {voice_inspired['dream_id']}")
        print("🎵 (Simulated voice input processed)")

        # Demo 5: Multi-theme dream sequence
        print("\n\n🌈 Demo 5: Multi-Theme Dream Sequence")
        print("-" * 50)

        themes = [
            "underwater libraries of forgotten languages",
            "conversations with future versions of myself",
            "painting with colors that don't exist yet",
        ]

        for i, theme in enumerate(themes, 1):
            print(f"\n  Dream {i}/3: {theme}")
            mini_dream = await pipeline.generate_dream_from_text(
                theme, dream_type="narrative"
            )
            print(f"  ✅ Generated: {mini_dream['dream_id']}")

        # Show analytics
        print("\n\n📊 Dream Generation Analytics")
        print("-" * 50)

        analytics = await pipeline.get_dream_analytics()
        print(json.dumps(analytics, indent=2))

        # Demo complete
        print("\n\n✨ Demo Complete!")
        print("=" * 70)
        print("\n📁 Dream outputs saved to: dream_demo_outputs/")
        print("📋 Dream log available at: dream_demo_outputs/dream_log.jsonl")

    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback

        traceback.print_exc()

    finally:
        await pipeline.close()
        print("\n🔚 Pipeline closed")


def demo_basic_generation():
    """Demonstrate basic dream generation without async."""
    print("\n🌟 Basic Dream Generation Demo")
    print("-" * 50)

    def mock_evaluate(action):
        return {"status": "allowed", "score": 0.95}

    # Generate basic dream
    basic_dream = generate_dream_sync(
        mock_evaluate, generate_visuals=True, generate_audio=True
    )

    print("✅ Basic Dream Generated")
    print(f"📝 Theme: {basic_dream.get('narrative', {}).get('theme')}")
    print(f"🎨 Visual Ready: {basic_dream.get('narrative', {}).get('sora_ready')}")

    return basic_dream


if __name__ == "__main__":
    print("🚀 Starting LUKHAS Dream OpenAI Integration Demo...\n")

    # Check for API key
    import os

    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not set!")
        print("   The demo will run with limited functionality.")
        print("   Set your API key: export OPENAI_API_KEY='your-key-here'\n")

    # Run basic demo first
    demo_basic_generation()

    # Run full async demo
    print("\n" + "=" * 70)
    asyncio.run(main())
