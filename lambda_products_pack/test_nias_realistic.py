#!/usr/bin/env python3
"""
NIΛS Realistic Advertising Demo - Show successful ad delivery
This demonstrates how NIAS delivers targeted ads to interested users
"""

import asyncio
import sys
from pathlib import Path

# Add the lambda_core to path
sys.path.insert(0, str(Path(__file__).parent))

from lambda_core.NIAS.nias_core import (
    NIΛS, SymbolicMessage, MessageTier, ConsentLevel, 
    EmotionalState
)

async def realistic_advertising_demo():
    """Demo with realistic user targeting and successful deliveries"""
    print("🎯 NIΛS Realistic Advertising Demo")
    print("=" * 60)
    print("Showing successful targeted ad delivery with symbolic matching")
    print()
    
    # Initialize NIAS
    nias = NIΛS()
    
    # Setup users with specific interests
    print("👥 Setting up users with specific interests...")
    
    # Eco-conscious user
    await nias.register_user(
        user_id="eco_sarah",
        tier=MessageTier.PERSONAL,
        consent_level=ConsentLevel.ENHANCED
    )
    
    # Tech professional
    await nias.register_user(
        user_id="tech_mike",
        tier=MessageTier.CREATIVE,
        consent_level=ConsentLevel.FULL_SYMBOLIC
    )
    
    # Wellness enthusiast
    await nias.register_user(
        user_id="wellness_jane",
        tier=MessageTier.PERSONAL,
        consent_level=ConsentLevel.ENHANCED
    )
    
    print("✅ Users registered")
    
    # Set user contexts with matching interests
    print("\n🎨 Setting user contexts and interests...")
    
    # Eco-conscious user context
    await nias.update_emotional_state("eco_sarah", {
        "stress": 0.3, "creativity": 0.6, "focus": 0.7, "energy": 0.7
    })
    nias.user_contexts["eco_sarah"].current_tags = ["sustainability", "eco-friendly", "values", "conscious-living"]
    
    # Tech professional context  
    await nias.update_emotional_state("tech_mike", {
        "stress": 0.4, "creativity": 0.8, "focus": 0.8, "energy": 0.8
    })
    nias.user_contexts["tech_mike"].current_tags = ["productivity", "AI", "technology", "workflow", "efficiency"]
    
    # Wellness enthusiast context
    await nias.update_emotional_state("wellness_jane", {
        "stress": 0.6, "creativity": 0.5, "focus": 0.5, "energy": 0.6
    })
    nias.user_contexts["wellness_jane"].current_tags = ["mindfulness", "wellness", "meditation", "stress-relief", "balance"]
    
    print("✅ User contexts configured")
    
    # Create targeted ads
    print("\n📢 Creating targeted advertisements...")
    
    # Eco brand ad - targeted to eco_sarah
    eco_ad = SymbolicMessage(
        id="eco-ad-001",
        content="🌱 Join the movement: Sustainable products that make a difference",
        tags=["sustainability", "eco-friendly", "conscious-living", "values"],
        tier=MessageTier.PERSONAL,
        emotional_tone=EmotionalState.CALM,
        intensity=0.4,
        voice_tag="authentic_caring",
        metadata={
            "brand": "EcoLife Solutions",
            "campaign": "sustainable_future",
            "cta": "Shop sustainable alternatives →"
        }
    )
    
    # Tech productivity ad - targeted to tech_mike
    tech_ad = SymbolicMessage(
        id="tech-ad-002", 
        content="⚡ AI-powered automation: Code faster, think deeper",
        tags=["productivity", "AI", "workflow", "efficiency", "technology"],
        tier=MessageTier.CREATIVE,
        emotional_tone=EmotionalState.FOCUSED,
        intensity=0.6,
        voice_tag="confident_innovative",
        metadata={
            "brand": "DevFlow AI",
            "campaign": "productivity_revolution",
            "cta": "Start free trial →"
        }
    )
    
    # Wellness app ad - targeted to wellness_jane
    wellness_ad = SymbolicMessage(
        id="wellness-ad-003",
        content="🧘 7-minute meditations for busy professionals",
        tags=["mindfulness", "meditation", "wellness", "stress-relief"],
        tier=MessageTier.PERSONAL,
        emotional_tone=EmotionalState.CALM,
        intensity=0.3,
        voice_tag="soothing_mindful",
        metadata={
            "brand": "MindfulSpace",
            "campaign": "quick_mindfulness",
            "cta": "Try free meditation →"
        }
    )
    
    print("✅ Advertisements created")
    
    # Test targeted delivery
    print("\n🎯 Testing targeted ad delivery...")
    
    scenarios = [
        ("eco_sarah", eco_ad, "🌱 Eco-conscious user"),
        ("tech_mike", tech_ad, "⚡ Tech professional"),
        ("wellness_jane", wellness_ad, "🧘 Wellness enthusiast"),
        # Cross-targeting (should be blocked or have lower success)
        ("eco_sarah", tech_ad, "🌱 Eco user seeing tech ad"),
        ("tech_mike", wellness_ad, "⚡ Tech user seeing wellness ad"),
    ]
    
    for user_id, ad, description in scenarios:
        print(f"\n  {description}:")
        print(f"    User tags: {nias.user_contexts[user_id].current_tags[:3]}...")
        print(f"    Ad tags: {ad.tags[:3]}...")
        
        result = await nias.push_message(ad, user_id)
        
        if result.status == "delivered":
            print(f"    ✅ SUCCESS: {result.delivery_method} delivery")
            print(f"       Message: {ad.content}")
            print(f"       CTA: {ad.metadata.get('cta', 'No CTA')}")
            print(f"       Λ Trace: {result.lambda_trace}")
        else:
            print(f"    ❌ BLOCKED: {result.reason}")
    
    # Show emotional state protection
    print(f"\n🛡️ Testing emotional protection...")
    
    # Put wellness_jane in high stress state
    await nias.update_emotional_state("wellness_jane", {
        "stress": 0.9, "creativity": 0.2, "focus": 0.2, "energy": 0.3
    })
    
    print(f"    Wellness user now in HIGH STRESS state (0.9)")
    result = await nias.push_message(tech_ad, "wellness_jane")
    print(f"    Tech ad attempt: {result.status} - {result.reason}")
    
    # Try low-intensity wellness ad
    gentle_wellness = SymbolicMessage(
        id="gentle-ad-004",
        content="💆 Take a moment to breathe",
        tags=["wellness", "breathing", "calm"],
        tier=MessageTier.PERSONAL,
        emotional_tone=EmotionalState.CALM,
        intensity=0.1,  # Very gentle
        voice_tag="ultra_gentle"
    )
    
    result = await nias.push_message(gentle_wellness, "wellness_jane")
    print(f"    Gentle wellness ad: {result.status} - {result.reason}")
    
    # Generate final metrics
    print(f"\n📊 Final Analytics")
    print("=" * 40)
    
    metrics = nias.get_system_metrics()
    print(f"Total Users: {metrics['total_users']}")
    print(f"Total Messages Attempted: {len(scenarios) + 2}")
    print(f"Successful Deliveries: {metrics['total_deliveries']}")
    print(f"Success Rate: {metrics['delivery_rate']:.1%}")
    
    print(f"\n🎉 Demo Highlights:")
    print(f"  ✅ Symbolic tag matching ensures relevant ads")
    print(f"  ✅ Subscription tiers control ad complexity")
    print(f"  ✅ Emotional state protection prevents overwhelming users")
    print(f"  ✅ Consent levels respected throughout delivery")
    print(f"  ✅ Lambda signatures provide cryptographic authenticity")

if __name__ == "__main__":
    asyncio.run(realistic_advertising_demo())
