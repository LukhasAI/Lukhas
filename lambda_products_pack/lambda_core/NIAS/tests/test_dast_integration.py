#!/usr/bin/env python3
"""
Test DAST Integration with NIAS Engine
Verify that the NIAS Engine properly integrates with DAST symbolic context
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add lambda-products to path
lambda_products_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(lambda_products_path))

# Import NIAS components
from NIΛS.core.nias_engine import get_nias_engine

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


async def test_dast_integration():
    """Test DAST integration with NIAS Engine"""
    print("🔮 NIAS-DΛST Integration Test")
    print("=" * 50)

    # Initialize NIAS Engine (which should initialize DAST adapter)
    nias_engine = get_nias_engine()

    # Check health status to see DAST integration
    health = await nias_engine.health_check()
    print(f"✅ NIAS Engine Status: {health['status']}")
    print(f"🔗 DΛST Integration Available: {health['dast_integration']['available']}")
    print(f"⚡ DΛST Integration Active: {health['dast_integration']['active']}")
    print(f"🎯 DΛST Integration Mode: {health['dast_integration']['mode']}")
    print(f"🧠 ΛBAS Integration Active: {health['abas_integration']['active']}")

    # Test user context with creative focus
    user_context = {
        "user_id": "test_user_bob",
        "tier": "T3",  # Premium tier
        "recent_interactions": [1, 2],  # Low interaction volume for testing
    }

    # Test multiple message types to see different symbolic contexts
    test_messages = [
        {
            "message_id": "test_creative_001",
            "type": "dream_seed",
            "priority": 2,
            "brand_id": "creative_studio",
            "description": "Inspire your next creative breakthrough with symbolic visualization",
            "dream_seed": {
                "theme": "creative-flow",
                "visualization": "flowing colors and patterns",
                "inspiration_level": 0.8,
            },
            "interactive_elements": True,
        },
        {
            "message_id": "test_educational_002",
            "type": "educational",
            "priority": 3,
            "brand_id": "learning_platform",
            "description": "Master advanced Python patterns with our new course",
            "educational_content": {
                "topic": "advanced-python",
                "difficulty": "intermediate",
                "estimated_time": 45,
            },
        },
        {
            "message_id": "test_promotional_003",
            "type": "promotional",
            "priority": 4,
            "brand_id": "productivity_app",
            "description": "Boost your productivity with our AI-powered workspace",
            "promotional_content": {
                "discount": 0.25,
                "expiry": "2025-08-20",
                "urgency": "limited-time",
            },
        },
    ]

    for i, test_message in enumerate(test_messages, 1):
        print(f"\n🧪 Test {i}: {test_message['type'].upper()} Message")
        print(f"   Message: {test_message['description'][:50]}...")

        try:
            # Test full message processing with DAST integration
            result = await nias_engine.process_message(test_message, user_context)

            print(f"   Status: {result.get('status', 'unknown')}")

            # Check processing session for DAST integration
            session = result.get("processing_session", {})
            if session:
                phases = session.get("phases", {})

                # Check symbolic processing phase
                if "symbolic_processing" in phases:
                    symbolic_phase = phases["symbolic_processing"]
                    print(
                        f"   DΛST Integration: {symbolic_phase.get('dast_integration', False)}"
                    )
                    print(
                        f"   Symbolic Tags: {symbolic_phase.get('symbolic_tags_count', 0)}"
                    )
                    print(
                        f"   Primary Activity: {symbolic_phase.get('primary_activity', 'N/A')}"
                    )
                    print(
                        f"   Coherence Score: {symbolic_phase.get('coherence_score', 0):.2f}"
                    )
                    print(
                        f"   Message Coherence: {symbolic_phase.get('message_coherence', 0):.2f}"
                    )
                    if symbolic_phase.get("lambda_fingerprint"):
                        print(
                            f"   Λ Fingerprint: {symbolic_phase.get('lambda_fingerprint')}"
                        )

                # Check delivery phase for DAST context updates
                if "delivery" in phases:
                    delivery_phase = phases["delivery"]
                    print(
                        f"   DΛST Context Updated: {delivery_phase.get('dast_context_updated', False)}"
                    )

            # Check if message was enhanced with DAST symbolic data
            if "message" in result:
                symbolic_processing = result["message"].get("symbolic_processing", {})
                if symbolic_processing.get("dast_integration"):
                    print("   Symbolic Enhancement:")
                    print(
                        f"     - Colors: {len(symbolic_processing.get('recommended_colors', []))} colors"
                    )
                    print(
                        f"     - Elements: {len(symbolic_processing.get('recommended_symbols', []))} elements"
                    )
                    print(
                        f"     - Tone: {symbolic_processing.get('recommended_tone', 'neutral')}"
                    )
                    print(
                        f"     - Symbolic Tags: {symbolic_processing.get('symbolic_tags', [])}"
                    )

        except Exception as e:
            print(f"   ❌ Processing Error: {e}")
            import traceback

            traceback.print_exc()

    # Test direct DAST adapter functionality if available
    if hasattr(nias_engine, "dast_adapter") and nias_engine.dast_adapter:
        print("\n🔬 Direct DΛST Adapter Testing:")

        try:
            # Test symbolic context retrieval
            symbolic_context = await nias_engine.dast_adapter.get_symbolic_context(
                user_context["user_id"], "creative"
            )

            print("   Symbolic Context Retrieved:")
            print(f"   - Primary Activity: {symbolic_context.get('primary_activity')}")
            print(
                f"   - Active Symbols: {len(symbolic_context.get('symbolic_tags', []))}"
            )
            print(
                f"   - Focus Score: {symbolic_context.get('context_scores', {}).get('focus_score', 0):.2f}"
            )
            print(
                f"   - Coherence Score: {symbolic_context.get('coherence_score', 0):.2f}"
            )
            print(f"   - Recommended Tone: {symbolic_context.get('recommended_tone')}")
            print(
                f"   - DΛST Integration: {symbolic_context.get('dast_integration', False)}"
            )

            # Test activity suggestions
            suggestions = await nias_engine.dast_adapter.get_activity_suggestions(
                user_context["user_id"], symbolic_context
            )

            if suggestions:
                print(f"   Activity Suggestions: {len(suggestions)} found")
                for suggestion in suggestions[:2]:  # Show first 2
                    print(
                        f"   - {suggestion.get('activity')}: {suggestion.get('reason')}"
                    )

        except Exception as e:
            print(f"   ⚠️  Direct DΛST test error: {e}")

    # Test integration status
    print("\n📊 Integration Status Summary:")

    if hasattr(nias_engine, "abas_adapter") and nias_engine.abas_adapter:
        abas_status = nias_engine.abas_adapter.get_integration_status()
        print(
            f"   ΛBAS: {abas_status.get('integration_mode', 'unknown')} mode, {abas_status.get('registered_users', 0)} users"
        )

    if hasattr(nias_engine, "dast_adapter") and nias_engine.dast_adapter:
        dast_status = nias_engine.dast_adapter.get_integration_status()
        print(
            f"   DΛST: {dast_status.get('integration_mode', 'unknown')} mode, {dast_status.get('registered_users', 0)} users"
        )

    # Final processing stats
    stats = await nias_engine.get_processing_stats()
    print("\n📈 Final Processing Statistics:")
    print(f"   Messages Processed: {stats['messages_processed']}")
    print(f"   Messages Delivered: {stats['messages_delivered']}")
    print(f"   Messages Blocked: {stats['messages_blocked']}")
    print(f"   Messages Deferred: {stats['messages_deferred']}")

    print("\n✅ DΛST Integration Test Complete")


async def test_dast_symbolic_coherence():
    """Test DAST symbolic coherence calculations"""
    print("\n🎨 Testing Symbolic Coherence")
    print("-" * 30)

    nias_engine = get_nias_engine()

    if not (hasattr(nias_engine, "dast_adapter") and nias_engine.dast_adapter):
        print("   DΛST adapter not available")
        return

    user_id = "test_coherence_user"

    # Test different message types and their coherence
    coherence_tests = [
        ("creative", "dream_seed"),  # High coherence expected
        ("working", "promotional"),  # Medium coherence
        ("relaxed", "urgent"),  # Low coherence expected
    ]

    for context_type, message_type in coherence_tests:
        try:
            # Simulate different contexts by requesting symbolic context
            symbolic_context = await nias_engine.dast_adapter.get_symbolic_context(
                user_id, message_type
            )

            coherence = symbolic_context.get("message_coherence", 0)
            print(
                f"   {context_type.capitalize()} + {message_type}: coherence {coherence:.2f}"
            )

        except Exception as e:
            print(f"   Error testing {context_type}/{message_type}: {e}")


if __name__ == "__main__":

    async def main():
        await test_dast_integration()
        await test_dast_symbolic_coherence()

    asyncio.run(main())
