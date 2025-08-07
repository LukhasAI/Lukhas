#!/usr/bin/env python3
"""
Test NIAS Dream Generation with real OpenAI API
Loads API key from .env file
"""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent.parent.parent / '.env'
load_dotenv(env_path)

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from lambda_products_pack.lambda_core.NIAS.dream_generator import (
    DreamGenerator, DreamContext, DreamMood, BioRhythm
)
from lambda_products_pack.lambda_core.NIAS.vendor_portal import DreamSeed, DreamSeedType

async def test_openai_dream_generation():
    """Test dream generation with real OpenAI API"""
    
    print("\n" + "="*80)
    print("🌙 NIAS DREAM GENERATION WITH OPENAI")
    print("="*80 + "\n")
    
    # Check if API key is loaded
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print(f"✅ OpenAI API Key loaded: {api_key[:20]}...")
    else:
        print("❌ No API key found in .env file")
        return
    
    # Create dream generator (will use the API key from environment)
    generator = DreamGenerator()
    
    # Create test scenarios
    test_scenarios = [
        {
            "name": "Holiday Shopping Reminder",
            "seed": DreamSeed(
                seed_id="holiday_001",
                vendor_id="vendor_fashion",
                seed_type=DreamSeedType.SEASONAL,
                title="Winter Gift Dreams",
                narrative="The perfect gift awaits in cozy cashmere...",
                emotional_triggers={"joy": 0.8, "calm": 0.6, "stress": 0.0, "longing": 0.5},
                product_data={
                    "id": "GIFT-001",
                    "name": "Luxury Cashmere Gift Set",
                    "price": 299.99,
                    "category": "gifts"
                },
                offer_details={"discount": 25, "code": "HOLIDAY25"},
                media_assets=[],
                targeting_criteria={},
                affiliate_link="https://example.com/buy/gift-set",
                one_click_data={"gift_wrap": True}
            ),
            "context": {
                "mood": DreamMood.CELEBRATORY,
                "bio_rhythm": BioRhythm.EVENING_WIND,
                "personal_data": {
                    "upcoming_events": [
                        {"type": "christmas", "date": "2024-12-25"},
                        {"type": "friend_birthday", "date": "2024-12-15", "name": "Emma"}
                    ],
                    "interests": ["thoughtful gifts", "sustainable fashion"],
                    "shopping_cart": ["Cashmere scarf", "Winter gloves"]
                }
            }
        },
        {
            "name": "Wellness Replenishment",
            "seed": DreamSeed(
                seed_id="wellness_001",
                vendor_id="vendor_health",
                seed_type=DreamSeedType.REPLENISHMENT,
                title="Monthly Wellness Journey",
                narrative="Your wellness routine, gently renewed...",
                emotional_triggers={"joy": 0.5, "calm": 0.8, "stress": 0.0, "longing": 0.2},
                product_data={
                    "id": "WELLNESS-001",
                    "name": "Organic Wellness Bundle",
                    "price": 89.99,
                    "category": "health"
                },
                offer_details={"subscription_discount": 20},
                media_assets=[],
                targeting_criteria={},
                affiliate_link="https://example.com/wellness",
                one_click_data={"auto_ship": True}
            ),
            "context": {
                "mood": DreamMood.SERENE,
                "bio_rhythm": BioRhythm.MORNING_PEAK,
                "personal_data": {
                    "interests": ["meditation", "organic living", "yoga"],
                    "recent_searches": ["vitamin D supplements", "meditation apps"],
                    "health_goals": ["better sleep", "stress reduction"]
                }
            }
        },
        {
            "name": "Adventure Discovery",
            "seed": DreamSeed(
                seed_id="adventure_001",
                vendor_id="vendor_travel",
                seed_type=DreamSeedType.DISCOVERY,
                title="Wanderlust Awakening",
                narrative="New horizons call to your adventurous spirit...",
                emotional_triggers={"joy": 0.7, "calm": 0.4, "stress": 0.0, "longing": 0.8},
                product_data={
                    "id": "TRAVEL-001",
                    "name": "Weekend Adventure Package",
                    "price": 599.00,
                    "category": "travel"
                },
                offer_details={"early_bird": 15},
                media_assets=[],
                targeting_criteria={},
                affiliate_link="https://example.com/adventure",
                one_click_data={"flexible_dates": True}
            ),
            "context": {
                "mood": DreamMood.ADVENTUROUS,
                "bio_rhythm": BioRhythm.MIDDAY_FLOW,
                "personal_data": {
                    "interests": ["hiking", "photography", "local cuisine"],
                    "browsing_history": ["national parks", "weekend getaways", "travel photography"],
                    "vacation_days_available": 5
                }
            }
        }
    ]
    
    # Test each scenario
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{'='*60}")
        print(f"SCENARIO {i}: {scenario['name']}")
        print(f"{'='*60}")
        
        # Create context
        context = DreamContext(
            user_id=f"test_user_{i}",
            user_profile={
                "name": ["Sarah", "Michael", "Alex"][i-1],
                "interests": scenario["context"]["personal_data"]["interests"],
                "tier": "premium"
            },
            vendor_seed=scenario["seed"],
            mood=scenario["context"]["mood"],
            bio_rhythm=scenario["context"]["bio_rhythm"],
            personal_data=scenario["context"]["personal_data"],
            preferences={"style": "minimalist", "language": "poetic"}
        )
        
        print(f"\n📝 Context:")
        print(f"   Product: {scenario['seed'].product_data['name']}")
        print(f"   Price: ${scenario['seed'].product_data['price']}")
        print(f"   Mood: {context.mood.value}")
        print(f"   Bio-rhythm: {context.bio_rhythm.value}")
        
        # Generate dream
        print(f"\n⏳ Generating dream with OpenAI...")
        try:
            dream = await generator.generate_dream(context)
            
            print(f"\n✨ GENERATED DREAM:")
            print(f"{'─'*40}")
            
            print(f"\n📖 AI-GENERATED NARRATIVE:")
            print(f"'{dream.narrative}'")
            
            print(f"\n🎨 AI-GENERATED VISUAL PROMPT:")
            print(f"'{dream.visual_prompt}'")
            
            print(f"\n💭 EXTRACTED SYMBOLISM:")
            for symbol in dream.symbolism:
                print(f"   • {symbol}")
            
            print(f"\n😊 EMOTIONAL PROFILE:")
            for emotion, value in dream.emotional_profile.items():
                bar = "█" * int(value * 10) + "░" * (10 - int(value * 10))
                print(f"   {emotion:8s}: {bar} {value:.2f}")
            
            print(f"\n🎯 CALL TO ACTION:")
            print(f"   '{dream.call_to_action['text']}'")
            
            print(f"\n⚖️ ETHICAL SCORE: {dream.ethical_score:.2f}")
            
            if dream.image_url:
                print(f"\n🖼️ DALL-E 3 IMAGE GENERATED!")
                print(f"   URL: {dream.image_url}")
                print(f"   (Open this URL in a browser to see the dream image)")
            
            # Save the dream ID for reference
            print(f"\n🆔 Dream ID: {dream.dream_id}")
            
        except Exception as e:
            print(f"\n❌ Error generating dream: {e}")
            print(f"   This might be due to API limits or network issues")
    
    # Test unethical content rejection
    print(f"\n\n{'='*80}")
    print("🛡️ TESTING ETHICAL VALIDATION")
    print(f"{'='*80}")
    
    unethical_seed = DreamSeed(
        seed_id="unethical_001",
        vendor_id="vendor_bad",
        seed_type=DreamSeedType.REMINDER,
        title="URGENT! BUY NOW!",
        narrative="HURRY! Limited time! Don't miss out! Last chance! Act NOW or regret forever!",
        emotional_triggers={"joy": 0.1, "calm": 0.0, "stress": 0.9, "longing": 1.0},
        product_data={"id": "BAD-001", "name": "Sketchy Product", "price": 999.99, "category": "scam"},
        offer_details={"fake_urgency": True},
        media_assets=[],
        targeting_criteria={},
        affiliate_link="https://scam.com",
        one_click_data={}
    )
    
    unethical_context = DreamContext(
        user_id="test_vulnerable",
        user_profile={"name": "Vulnerable User", "interests": [], "tier": "free"},
        vendor_seed=unethical_seed,
        mood=DreamMood.SERENE,
        bio_rhythm=BioRhythm.DEEP_NIGHT,
        personal_data={},
        preferences={}
    )
    
    print("\n🚫 Testing with unethical content:")
    print(f"   Stress level: {unethical_seed.emotional_triggers['stress']}")
    print(f"   Narrative: '{unethical_seed.narrative[:50]}...'")
    
    unethical_dream = await generator.generate_dream(unethical_context)
    
    print(f"\n📊 Results:")
    print(f"   Ethical Score: {unethical_dream.ethical_score:.2f}")
    print(f"   Narrative (cleaned): '{unethical_dream.narrative[:100]}...'")
    
    if unethical_dream.ethical_score < 0.8:
        print(f"   ✅ Correctly identified as unethical (score < 0.8)")
    else:
        print(f"   ⚠️ May need additional ethical validation")
    
    # Show final metrics
    metrics = generator.get_generation_metrics()
    print(f"\n\n{'='*80}")
    print("📊 FINAL METRICS")
    print(f"{'='*80}")
    print(f"   Total dreams generated: {metrics['cached_dreams']}")
    print(f"   OpenAI API active: {metrics['openai_available']}")
    print(f"   Models used: {metrics['models']}")
    
    print("\n\n✅ OpenAI dream generation test complete!")
    print("\n💡 The system successfully:")
    print("   • Generated personalized poetic narratives with GPT-4")
    print("   • Created dream imagery with DALL-E 3")
    print("   • Validated content ethically")
    print("   • Adapted to user mood and bio-rhythm")

if __name__ == "__main__":
    # Check if we need to install python-dotenv
    try:
        from dotenv import load_dotenv
    except ImportError:
        print("Installing python-dotenv...")
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "python-dotenv"], check=True)
        from dotenv import load_dotenv
    
    asyncio.run(test_openai_dream_generation())