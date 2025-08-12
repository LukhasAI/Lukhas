#!/usr/bin/env python3
"""
Test ABAS Integration with NIAS Engine
Verify that the NIAS Engine properly integrates with ABAS attention boundaries
"""

import asyncio
import logging
import sys
from pathlib import Path

from NIΛS.core.nias_engine import get_nias_engine

# Add lambda-products to path
lambda_products_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(lambda_products_path))

# Import NIAS components

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


async def test_abas_integration():
    """Test ABAS integration with NIAS Engine"""
    print("🧠 NIAS-ΛBAS Integration Test")
    print("=" * 50)

    # Initialize NIAS Engine (which should initialize ABAS adapter)
    nias_engine = get_nias_engine()

    # Check health status to see ABAS integration
    health = await nias_engine.health_check()
    print(f"✅ NIAS Engine Status: {health['status']}")
    print(f"🔗 ABAS Integration Available: {health['abas_integration']['available']}")
    print(f"⚡ ABAS Integration Active: {health['abas_integration']['active']}")
    print(f"🎯 ABAS Integration Mode: {health['abas_integration']['mode']}")

    # Test user context and message
    user_context = {
        "user_id": "test_user_alice",
        "tier": "T2",
        "recent_interactions": [1, 2, 3],  # Low interaction volume
    }

    test_message = {
        "message_id": "test_msg_001",
        "type": "promotional",
        "priority": 3,
        "brand_id": "test_brand",
        "description": "Test promotional message for ABAS integration",
        "dream_seed": {"theme": "productivity", "visualization": "growing plants"},
        "interactive_elements": True,
    }

    print("\n📧 Testing Message Processing:")
    print(f"   Message Type: {test_message['type']}")
    print(f"   Priority: {test_message['priority']}")
    print(f"   Has Dream Seed: {'dream_seed' in test_message}")

    # Test emotional state check
    print("\n🎭 Testing Emotional State Check:")
    emotional_check = await nias_engine.check_emotional_state(user_context)
    print(f"   Approved: {emotional_check.get('approved')}")
    print(f"   Emotional State: {emotional_check.get('emotional_state')}")
    print(f"   Attention State: {emotional_check.get('attention_state', 'N/A')}")
    print(f"   ABAS Integration: {emotional_check.get('abas_integration', False)}")
    if emotional_check.get("lambda_trace"):
        print(f"   Λ Trace: {emotional_check.get('lambda_trace')}")

    # Test full message processing
    print("\n🔄 Testing Full Message Processing:")
    try:
        result = await nias_engine.process_message(test_message, user_context)

        print(f"   Status: {result.get('status', 'unknown')}")
        print(f"   Processed At: {result.get('processed_at', 'N/A')}")

        # Check processing session details
        session = result.get("processing_session", {})
        if session:
            phases = session.get("phases", {})
            if "emotional_gating" in phases:
                gating_phase = phases["emotional_gating"]
                print("   Emotional Gating:")
                print(f"     - Emotional State: {gating_phase.get('emotional_state')}")
                print(
                    f"     - Attention State: {gating_phase.get('attention_state', 'N/A')}"
                )
                print(
                    f"     - ABAS Decision: {gating_phase.get('abas_decision', 'N/A')}"
                )
                if gating_phase.get("lambda_trace"):
                    print(f"     - Λ Trace: {gating_phase.get('lambda_trace')}")
                print(f"     - Duration: {gating_phase.get('duration_ms', 0):.1f}ms")

        # Check for message enhancements
        if result.get("widget_config"):
            widget = result["widget_config"]
            print(f"   Widget Generated: {widget.get('type', 'unknown')}")

        if "message" in result and "attention_enhancement" in result["message"]:
            enhancement = result["message"]["attention_enhancement"]
            print("   Attention Enhancement Applied:")
            print(f"     - Optimal Timing: {enhancement.get('optimal_timing')}")
            print(f"     - Confidence: {enhancement.get('confidence', 0):.2f}")

    except Exception as e:
        print(f"   ❌ Processing Error: {e}")
        import traceback

        traceback.print_exc()

    # Test processing stats
    print("\n📊 Processing Statistics:")
    stats = await nias_engine.get_processing_stats()
    print(f"   Messages Processed: {stats['messages_processed']}")
    print(f"   Messages Delivered: {stats['messages_delivered']}")
    print(f"   Messages Blocked: {stats['messages_blocked']}")
    print(f"   Messages Deferred: {stats['messages_deferred']}")

    print("\n✅ ABAS Integration Test Complete")


if __name__ == "__main__":
    asyncio.run(test_abas_integration())
