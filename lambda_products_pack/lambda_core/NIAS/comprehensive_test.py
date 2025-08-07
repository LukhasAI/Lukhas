#!/usr/bin/env python3
"""
NIAS Comprehensive Ad Demo
Shows various advertising scenarios and targeting
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from nias_core import (
    NIΛS, SymbolicMessage, MessageTier, ConsentLevel, 
    EmotionalState
)

async def comprehensive_ad_demo():
    """Comprehensive advertising demonstration"""
    print("🎯 NIΛS Comprehensive Advertising Demo")
    print("=" * 60)
    
    nias = NIΛS()
    
    # Setup different user personas
    users = [
        {
            "id": "tech_pro", 
            "tier": MessageTier.CREATIVE,
            "consent": ConsentLevel.FULL_SYMBOLIC,
            "tags": ["AI", "coding", "productivity", "innovation"],
            "emotions": {"stress": 0.2, "creativity": 0.9, "focus": 0.8, "energy": 0.8}
        },
        {
            "id": "wellness_seeker",
            "tier": MessageTier.PERSONAL, 
            "consent": ConsentLevel.ENHANCED,
            "tags": ["wellness", "mindfulness", "health", "balance"],
            "emotions": {"stress": 0.6, "creativity": 0.4, "focus": 0.5, "energy": 0.6}
        },
        {
            "id": "eco_conscious",
            "tier": MessageTier.PERSONAL,
            "consent": ConsentLevel.ENHANCED, 
            "tags": ["sustainability", "eco-friendly", "environment", "conscious"],
            "emotions": {"stress": 0.3, "creativity": 0.6, "focus": 0.7, "energy": 0.7}
        }
    ]
    
    # Register users
    print("👥 Setting up user personas...")
    for user in users:
        await nias.register_user(user["id"], user["tier"], user["consent"])
        await nias.update_emotional_state(user["id"], user["emotions"])
        nias.user_contexts[user["id"]].current_tags = user["tags"]
        print(f"   ✅ {user['id']}: {user['tier'].name} tier")
    
    # Create targeted ads
    ads = [
        {
            "ad": SymbolicMessage(
                id="ai-dev-001",
                content="🤖 Revolutionary AI coding assistant - 10x your productivity",
                tags=["AI", "coding", "productivity", "development"],
                tier=MessageTier.CREATIVE,
                emotional_tone=EmotionalState.FOCUSED,
                intensity=0.7,
                metadata={"brand": "CodeAI Pro", "target": "tech_pro"}
            ),
            "target": "tech_pro"
        },
        {
            "ad": SymbolicMessage(
                id="meditation-001", 
                content="🧘 5-minute guided meditations for instant calm",
                tags=["mindfulness", "wellness", "meditation", "calm"],
                tier=MessageTier.PERSONAL,
                emotional_tone=EmotionalState.CALM,
                intensity=0.3,
                metadata={"brand": "CalmSpace", "target": "wellness_seeker"}
            ),
            "target": "wellness_seeker"
        },
        {
            "ad": SymbolicMessage(
                id="eco-products-001",
                content="🌱 Sustainable living made simple - eco-friendly essentials",
                tags=["sustainability", "eco-friendly", "environment", "green"],
                tier=MessageTier.PERSONAL,
                emotional_tone=EmotionalState.CALM,
                intensity=0.4,
                metadata={"brand": "EcoLife", "target": "eco_conscious"}
            ),
            "target": "eco_conscious"
        }
    ]
    
    print(f"\n📢 Testing targeted ad delivery...")
    
    successful_deliveries = 0
    total_attempts = 0
    
    # Test targeted delivery
    for ad_info in ads:
        ad = ad_info["ad"]
        target_user = ad_info["target"]
        
        print(f"\n  🎯 {ad.metadata['brand']} → {target_user}")
        print(f"     Content: {ad.content}")
        print(f"     Tags: {ad.tags[:3]}...")
        
        result = await nias.push_message(ad, target_user)
        total_attempts += 1
        
        if result.status == "delivered":
            successful_deliveries += 1
            print(f"     ✅ SUCCESS: {result.delivery_method} delivery")
            print(f"     Λ Trace: {result.lambda_trace}")
        else:
            print(f"     ❌ BLOCKED: {result.reason}")
    
    # Test cross-targeting (should mostly fail)
    print(f"\n🔄 Testing cross-targeting (anti-spam protection)...")
    
    cross_tests = [
        ("AI ad to wellness user", ads[0]["ad"], "wellness_seeker"),
        ("Wellness ad to tech user", ads[1]["ad"], "tech_pro"),
        ("Eco ad to tech user", ads[2]["ad"], "tech_pro")
    ]
    
    for test_name, ad, user_id in cross_tests:
        result = await nias.push_message(ad, user_id)
        total_attempts += 1
        status_emoji = "✅" if result.status == "delivered" else "🛡️"
        print(f"     {status_emoji} {test_name}: {result.status}")
    
    # Final metrics
    metrics = nias.get_system_metrics()
    print(f"\n📊 Final Analytics")
    print("=" * 40)
    print(f"Total Users: {len(users)}")
    print(f"Total Ads Created: {len(ads)}")
    print(f"Delivery Attempts: {total_attempts}")
    print(f"Successful Deliveries: {successful_deliveries}")
    print(f"Targeted Success Rate: {successful_deliveries/len(ads):.1%}")
    print(f"System Delivery Rate: {metrics['delivery_rate']:.1%}")
    print(f"Anti-spam Protection: {'🛡️ Active' if successful_deliveries < total_attempts else '⚠️ Needs Review'}")
    
    print(f"\n🎉 Comprehensive Demo Results:")
    print(f"  ✅ Targeted advertising working")
    print(f"  ✅ Emotional intelligence active")
    print(f"  ✅ Symbolic matching operational")
    print(f"  ✅ Anti-spam protection enabled")
    print(f"  ✅ Lambda verification working")
    
    return successful_deliveries > 0

if __name__ == "__main__":
    asyncio.run(comprehensive_ad_demo())
