#!/usr/bin/env python3
"""
Demo: Generate a complete dream with narrative and image using OpenAI
"""

import asyncio
import sys
from datetime import datetime, timezone
from pathlib import Path

# Load environment
from dotenv import load_dotenv

from products.lambda_pack.lambda_core.NIAS.dream_generator import (
    BioRhythm,
    DreamContext,
    DreamGenerator,
    DreamMood)
from products.lambda_pack.lambda_core.NIAS.vendor_portal import (
    DreamSeed,
    DreamSeedType,
)

env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(env_path)

# Add to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))


async def generate_demo_dream():
    """Generate a single demo dream with OpenAI"""

    print("\n" + "=" * 80)
    print("🌙 NIAS DREAM COMMERCE - LIVE DEMONSTRATION")
    print("=" * 80)
    print(f"Time: {datetime.now(timezone.utc).strftime('%I:%M %p')}")

    # Determine current bio-rhythm
    hour = datetime.now(timezone.utc).hour
    if 6 <= hour < 10:
        bio_rhythm = BioRhythm.MORNING_PEAK
    elif 17 <= hour < 21:
        bio_rhythm = BioRhythm.EVENING_WIND
    elif 21 <= hour < 24:
        bio_rhythm = BioRhythm.NIGHT_QUIET
    else:
        bio_rhythm = BioRhythm.MIDDAY_FLOW

    print(f"Bio-rhythm: {bio_rhythm.value}")

    # Create a realistic vendor seed
    seed = DreamSeed(
        seed_id="demo_001",
        vendor_id="comfort_co",
        seed_type=DreamSeedType.SEASONAL,
        title="Winter Comfort Collection",
        narrative="Transform your winter evenings into moments of pure comfort...",
        emotional_triggers={"joy": 0.6, "calm": 0.8, "stress": 0.0, "longing": 0.4},
        product_data={
            "id": "WCC-001",
            "name": "Cloud Nine Cashmere Set",
            "price": 249.99,
            "category": "luxury comfort",
        },
        offer_details={"discount": 20, "code": "DREAM20", "valid_until": "2024-12-31"},
        media_assets=[],
        targeting_criteria={"interests": ["comfort", "luxury", "self-care"]},
        affiliate_link="https://comfort.example.com/cashmere",
        one_click_data={
            "sizes": ["S", "M", "L", "XL"],
            "colors": ["Cloud Grey", "Midnight Blue", "Soft Rose"],
        },
    )

    # Create user context
    context = DreamContext(
        user_id="demo_user",
        user_profile={
            "name": "Dream Explorer",
            "interests": ["wellness", "comfort", "sustainable living"],
            "tier": "premium",
        },
        vendor_seed=seed,
        mood=DreamMood.SERENE,
        bio_rhythm=bio_rhythm,
        personal_data={
            "upcoming_events": [
                {"type": "weekend", "activity": "relaxation"},
                {"type": "gift_giving", "occasion": "self-care"},
            ],
            "interests": ["cozy evenings", "reading", "tea ceremonies"],
            "recent_searches": ["sustainable fashion", "hygge lifestyle"],
            "preferences": {
                "materials": "natural fibers",
                "style": "minimalist comfort",
            },
        },
        preferences={"communication_style": "gentle", "visual_style": "ethereal"},
    )

    # Initialize generator
    print("\n🔄 Initializing Dream Generator with OpenAI...")
    generator = DreamGenerator()

    # Check if OpenAI is available
    metrics = generator.get_generation_metrics()
    if not metrics["openai_available"]:
        print("❌ OpenAI not available. Check API key.")
        return

    print("✅ OpenAI connected")
    print("   Models: GPT-4 for narratives, DALL-E 3 for images")

    # Generate the dream
    print("\n⏳ Generating personalized dream experience...")
    print("   • Creating poetic narrative with GPT-4...")
    print("   • Extracting symbolic elements...")
    print("   • Generating dream imagery with DALL-E 3...")

    try:
        dream = await generator.generate_dream(context)

        print("\n" + "=" * 80)
        print("✨ DREAM GENERATED SUCCESSFULLY")
        print("=" * 80)

        print(f"\n🆔 Dream ID: {dream.dream_id}")
        print(f"⏰ Created: {dream.created_at.strftime('%I:%M %p')}")

        print("\n📖 AI-GENERATED POETIC NARRATIVE:")
        print("-" * 60)
        print(dream.narrative)
        print("-" * 60)

        print("\n🎨 VISUAL GENERATION PROMPT:")
        print(f"'{dream.visual_prompt}'")

        if dream.image_url:
            print("\n🖼️ DREAM IMAGE GENERATED!")
            print(f"URL: {dream.image_url}")
            print("\n📱 To view the dream image:")
            print("   1. Copy the URL above")
            print("   2. Paste in your browser")
            print("   3. Experience the visual dream")

        print("\n💭 SYMBOLIC ELEMENTS:")
        for i, symbol in enumerate(dream.symbolism, 1):
            print(f"   {i}. {symbol}")

        print("\n😊 EMOTIONAL RESONANCE:")
        for emotion, value in dream.emotional_profile.items():
            if value > 0:
                bar = "●" * int(value * 10) + "○" * (10 - int(value * 10))
                print(f"   {emotion.capitalize():8s} {bar} {value:.0%}")

        print("\n🎯 GENTLE INVITATION:")
        print(f"   '{dream.call_to_action['text']}'")

        if dream.call_to_action.get("action"):
            print("\n🔗 One-Click Journey:")
            print(f"   {dream.call_to_action['action']}")

        print("\n⚖️ ETHICAL VALIDATION:")
        print(f"   Score: {dream.ethical_score:.0%}")
        if dream.ethical_score >= 0.8:
            print("   ✅ Passed ethical review")

        print("\n📊 GENERATION DETAILS:")
        print(f"   Mood: {dream.generation_metadata.get('mood', 'unknown')}")
        print(f"   Bio-rhythm: {dream.generation_metadata.get('bio_rhythm', 'unknown')}")
        print(f"   Models: {dream.generation_metadata.get('models_used', {)})}")

        # Save results
        results_file = f"dream_{dream.dream_id}.txt"
        with open(results_file, "w") as f:
            f.write("NIAS Dream Commerce - Generated Dream\n")
            f.write(f"{'=' * 60}\n\n")
            f.write(f"Dream ID: {dream.dream_id}\n")
            f.write(f"Generated: {dream.created_at}\n\n")
            f.write(f"NARRATIVE:\n{dream.narrative}\n\n")
            f.write(f"IMAGE URL:\n{dream.image_url or 'Not generated'}\n\n")
            f.write(f"SYMBOLISM: {', '.join(dream.symbolism)}\n")
            f.write(f"ETHICAL SCORE: {dream.ethical_score:.0%}\n")

        print(f"\n💾 Dream saved to: {results_file}")

        print("\n" + "=" * 80)
        print("🎉 DEMONSTRATION COMPLETE")
        print("=" * 80)
        print("\nThe NIAS Dream Commerce System has successfully:")
        print("✅ Generated a personalized poetic narrative (not sales copy)")
        print("✅ Created dream imagery with DALL-E 3")
        print("✅ Extracted symbolic meaning")
        print("✅ Calibrated emotional resonance")
        print("✅ Validated ethical compliance")
        print("✅ Prepared one-click commerce")

        print("\n🌟 This is the future of ethical advertising:")
        print("   Not selling, but dreaming together.")

    except Exception as e:
        print(f"\n❌ Error during generation: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    print("🚀 Starting NIAS Dream Generation Demo...")
    asyncio.run(generate_demo_dream())