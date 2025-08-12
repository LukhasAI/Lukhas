#!/usr/bin/env python3
"""
Standalone test to demonstrate dream generation with and without OpenAI
"""

import asyncio
import sys
from pathlib import Path

from lambda_products_pack.lambda_core.NIAS.dream_generator import (
    BioRhythm,
    DreamContext,
    DreamGenerator,
    DreamMood,
)
from lambda_products_pack.lambda_core.NIAS.vendor_portal import (
    DreamSeed,
    DreamSeedType,
)

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))


async def test_dream_generation():
    """Test dream generation with fallback"""

    print("\n" + "=" * 80)
    print("🌙 TESTING DREAM GENERATION - FALLBACK MODE")
    print("=" * 80 + "\n")

    # Create dream generator
    generator = DreamGenerator()

    # Create a test vendor seed
    test_seed = DreamSeed(
        seed_id="test_seed_001",
        vendor_id="vendor_test",
        seed_type=DreamSeedType.SEASONAL,
        title="Winter Dreams Collection",
        narrative="As snowflakes dance outside your window, imagine wrapping yourself in clouds of cashmere...",
        emotional_triggers={"joy": 0.7, "calm": 0.8, "stress": 0.0, "longing": 0.4},
        product_data={
            "id": "PROD-001",
            "name": "Cloud Cashmere Sweater",
            "price": 189.99,
            "category": "apparel",
        },
        offer_details={"discount": 20, "code": "WINTER20"},
        media_assets=[],
        targeting_criteria={},
        affiliate_link="https://example.com/buy/sweater",
        one_click_data={"express_checkout": True},
    )

    # Create test context
    test_context = DreamContext(
        user_id="test_user",
        user_profile={
            "interests": ["fashion", "comfort", "wellness"],
            "tier": "premium",
            "name": "Sarah",
        },
        vendor_seed=test_seed,
        mood=DreamMood.SERENE,
        bio_rhythm=BioRhythm.EVENING_WIND,
        personal_data={
            "upcoming_events": [{"type": "holiday_party", "date": "2024-12-20"}],
            "interests": ["sustainable fashion", "cozy evenings"],
            "recent_activity": [
                "browsing winter fashion",
                "reading about cashmere care",
            ],
        },
        preferences={"color": "soft neutrals", "style": "minimalist comfort"},
    )

    print("📝 Generating dream with context:")
    print(f"   - User: {test_context.user_id}")
    print(f"   - Mood: {test_context.mood.value}")
    print(f"   - Bio-rhythm: {test_context.bio_rhythm.value}")
    print(f"   - Product: {test_seed.product_data['name']}")
    print(f"   - Price: ${test_seed.product_data['price']}")

    # Generate dream
    print("\n⏳ Generating dream narrative...")
    dream = await generator.generate_dream(test_context)

    print("\n✨ GENERATED DREAM:")
    print("-" * 40)

    print(f"\n🆔 Dream ID: {dream.dream_id}")

    print("\n📖 NARRATIVE:")
    print(f"'{dream.narrative}'")

    print("\n🎨 VISUAL PROMPT:")
    print(f"'{dream.visual_prompt}'")

    print("\n💭 SYMBOLISM:")
    for symbol in dream.symbolism:
        print(f"   • {symbol}")

    print("\n😊 EMOTIONAL PROFILE:")
    for emotion, value in dream.emotional_profile.items():
        bar = "█" * int(value * 10) + "░" * (10 - int(value * 10))
        print(f"   {emotion:8s}: {bar} {value:.2f}")

    print("\n🎯 CALL TO ACTION:")
    print(f"   Type: {dream.call_to_action['type']}")
    print(f"   Text: '{dream.call_to_action['text']}'")
    if dream.call_to_action.get("action"):
        print(f"   Link: {dream.call_to_action['action']}")

    print(f"\n⚖️ ETHICAL SCORE: {dream.ethical_score:.2f}")

    if dream.image_url:
        print(f"\n🖼️ IMAGE URL: {dream.image_url}")
    else:
        print("\n🖼️ IMAGE: Not generated (no OpenAI API key)")

    if dream.video_url:
        print(f"\n🎥 VIDEO URL: {dream.video_url}")
    else:
        print("\n🎥 VIDEO: Not available (Sora not yet released)")

    print("\n🔧 GENERATION METADATA:")
    for key, value in dream.generation_metadata.items():
        print(f"   {key}: {value}")

    # Test different moods
    print("\n" + "=" * 80)
    print("🎭 TESTING DIFFERENT MOODS")
    print("=" * 80)

    moods_to_test = [DreamMood.NOSTALGIC, DreamMood.ASPIRATIONAL, DreamMood.WHIMSICAL]

    for mood in moods_to_test:
        test_context.mood = mood
        dream = await generator.generate_dream(test_context)

        print(f"\n🎨 Mood: {mood.value}")
        print(f"   Narrative snippet: '{dream.narrative[:100]}...'")
        print(
            f"   Emotional profile: Joy={dream.emotional_profile['joy']:.1f}, "
            f"Calm={dream.emotional_profile['calm']:.1f}, "
            f"Longing={dream.emotional_profile['longing']:.1f}"
        )

    # Show metrics
    metrics = generator.get_generation_metrics()
    print("\n" + "=" * 80)
    print("📊 GENERATION METRICS")
    print("=" * 80)
    print(f"   Cached dreams: {metrics['cached_dreams']}")
    print(f"   OpenAI available: {metrics['openai_available']}")
    print(f"   Models configured: {metrics['models']}")

    print("\n✅ Dream generation test complete!")

    # Check if we could use OpenAI
    if not metrics["openai_available"]:
        print("\n" + "=" * 80)
        print("💡 TO ENABLE OPENAI GENERATION:")
        print("=" * 80)
        print("1. Get your OpenAI API key from: https://platform.openai.com/api-keys")
        print("2. Set the environment variable:")
        print("   export OPENAI_API_KEY='sk-your-api-key-here'")
        print("3. Run this test again to see:")
        print("   - GPT-4 generated poetic narratives")
        print("   - DALL-E 3 generated dream images")
        print("   - More sophisticated emotional profiling")


if __name__ == "__main__":
    asyncio.run(test_dream_generation())
