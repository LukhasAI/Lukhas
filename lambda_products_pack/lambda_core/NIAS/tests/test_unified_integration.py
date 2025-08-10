#!/usr/bin/env python3
"""
Test Unified Three-Way Integration (NIAS-ABAS-DAST)
Comprehensive test of the unified processor orchestrating all three systems
"""

from NIΛS.integration.unified_processor import get_unified_processor
import asyncio
import logging
import sys
from pathlib import Path

# Add lambda-products to path
lambda_products_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(lambda_products_path))

# Import unified processor

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


async def test_unified_integration():
    """Test complete unified three-way integration"""
    print("🚀 Unified NIΛS-ΛBAS-DΛST Integration Test")
    print("=" * 60)

    # Initialize unified processor
    unified_processor = get_unified_processor()

    # Check system health
    health = await unified_processor.health_check()
    print(f"✅ Unified Processor Status: {health['status']}")
    print(f"🔗 Integrations Active: {health['integrations']}")
    print(
        f"📊 Processing Stats: {health['processing_stats']['total_requests']} total requests"
    )

    # Test comprehensive user context
    user_context = {
        "user_id": "test_unified_user",
        "tier": "T3",  # Premium tier for full features
        "preferences": {
            "symbolic_enhancement": True,
            "attention_protection": True,
            "dream_seeds_enabled": True,
        },
        "recent_interactions": [1, 2, 3],  # Moderate interaction history
        "timezone": "America/New_York",
        "device_context": "desktop",
    }

    # Test different message scenarios for complete integration
    test_scenarios = [
        {
            "name": "Creative Dream Seed",
            "message": {
                "message_id": "unified_creative_001",
                "type": "dream_seed",
                "priority": 3,
                "brand_id": "inspiration_studio",
                "title": "Unlock Your Creative Potential",
                "description": "Experience a guided visualization journey to spark your next creative breakthrough",
                "dream_seed": {
                    "theme": "creative-flow",
                    "visualization": "flowing energy patterns",
                    "emotional_target": "inspired",
                    "duration_minutes": 5,
                },
                "interactive_elements": True,
                "personalization": {
                    "user_interests": ["creativity", "art", "design"],
                    "optimal_timing": "evening",
                },
            },
            "expected_outcome": "Should leverage symbolic context for enhanced personalization",
        },
        {
            "name": "Educational Content",
            "message": {
                "message_id": "unified_education_002",
                "type": "educational",
                "priority": 4,
                "brand_id": "learning_platform",
                "title": "Advanced AI Development Course",
                "description": "Master the latest techniques in artificial intelligence and machine learning",
                "educational_content": {
                    "topic": "ai-development",
                    "difficulty": "advanced",
                    "estimated_time": 120,
                    "prerequisites": ["python", "mathematics"],
                },
                "personalization": {
                    "skill_level": "intermediate",
                    "learning_style": "hands-on",
                },
            },
            "expected_outcome": "Should respect attention boundaries during focused work",
        },
        {
            "name": "High Priority Alert",
            "message": {
                "message_id": "unified_urgent_003",
                "type": "urgent",
                "priority": 5,
                "brand_id": "security_service",
                "title": "Security Alert",
                "description": "Important security update requires your immediate attention",
                "urgency_indicators": {
                    "time_sensitive": True,
                    "security_related": True,
                    "user_action_required": True,
                },
                "personalization": {
                    "override_boundaries": True,
                    "minimal_cognitive_load": True,
                },
            },
            "expected_outcome": "Should override attention boundaries due to high priority",
        },
        {
            "name": "Promotional with Low Coherence",
            "message": {
                "message_id": "unified_promo_004",
                "type": "promotional",
                "priority": 2,
                "brand_id": "shopping_platform",
                "title": "Weekend Sale Event",
                "description": "Save 50% on electronics and gadgets this weekend only",
                "promotional_content": {
                    "discount_percentage": 50,
                    "category": "electronics",
                    "expiry": "2025-08-10",
                    "limited_quantity": True,
                },
                "personalization": {
                    "user_interests": ["technology", "shopping"],
                    "price_sensitivity": "medium",
                },
            },
            "expected_outcome": "Should be filtered based on symbolic coherence and attention state",
        },
    ]

    # Process each scenario through the unified pipeline
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n🧪 Scenario {i}: {scenario['name']}")
        print(f"   Expected: {scenario['expected_outcome']}")
        print(f"   Message: {scenario['message']['description'][:60]}...")

        try:
            # Process through unified pipeline
            result = await unified_processor.process_message(
                user_context["user_id"], scenario["message"], user_context
            )

            # Analyze results
            print(f"   📋 Result: {result.get('status', 'unknown')}")
            print(f"   ⏱️ Processing Time: {result.get('processing_time_ms', 0):.1f}ms")
            print(
                f"   🔄 Unified Processing: {result.get('unified_processing', False)}"
            )

            # Integration status
            integration_status = result.get("integration_status", {})
            active_integrations = sum(
                1 for status in integration_status.values() if status
            )
            print(f"   🔗 Active Integrations: {active_integrations}/3")

            # Symbolic context analysis
            symbolic_context = result.get("symbolic_context", {})
            if symbolic_context:
                print("   🎨 Symbolic Context:")
                print(
                    f"     - Primary Activity: {symbolic_context.get('primary_activity', 'N/A')}"
                )
                print(
                    f"     - Coherence Score: {symbolic_context.get('coherence_score', 0):.2f}"
                )
                print(
                    f"     - DΛST Integration: {symbolic_context.get('dast_integration', False)}"
                )

                # Message coherence specific to this message type
                message_coherence = symbolic_context.get("message_coherence", 0)
                print(f"     - Message Coherence: {message_coherence:.2f}")

            # Attention decision analysis
            attention_decision = result.get("attention_decision", {})
            if attention_decision:
                print("   🧠 Attention Decision:")
                print(f"     - Approved: {attention_decision.get('approved', False)}")
                print(
                    f"     - Emotional State: {attention_decision.get('emotional_state', 'N/A')}"
                )
                print(
                    f"     - Attention State: {attention_decision.get('attention_state', 'N/A')}"
                )
                print(
                    f"     - Confidence: {attention_decision.get('confidence', 0):.2f}"
                )
                print(
                    f"     - ΛBAS Integration: {attention_decision.get('abas_integration', False)}"
                )

                if not attention_decision.get("approved"):
                    print(f"     - Reason: {attention_decision.get('reason', 'N/A')}")
                    if attention_decision.get("defer_until"):
                        print(
                            f"     - Defer Until: {attention_decision.get('defer_until')}"
                        )

            # Lambda traces
            lambda_trace = result.get("lambda_trace")
            if lambda_trace:
                print(f"   Λ Trace: {lambda_trace}")

            # Widget and delivery analysis
            if result.get("status") == "delivered":
                widget_config = result.get("widget_config")
                if widget_config:
                    print(
                        f"   🎛️ Widget Generated: {widget_config.get('type', 'unknown')}"
                    )

                delivery_method = result.get("delivery_method", "basic")
                print(f"   📤 Delivery Method: {delivery_method}")

        except Exception as e:
            print(f"   ❌ Processing Error: {e}")
            import traceback

            traceback.print_exc()

    # Test system metrics and performance
    print("\n📊 System Performance Analysis:")
    metrics = unified_processor.get_system_metrics()

    print(f"   System: {metrics['system']}")
    print(f"   Version: {metrics['version']}")
    print(
        f"   Active Integrations: {metrics['integrations_active']}/{metrics['total_integrations']}"
    )

    processing_stats = metrics["processing_stats"]
    print(f"   Total Requests: {processing_stats['total_requests']}")
    print(f"   Successful Deliveries: {processing_stats['successful_deliveries']}")
    print(f"   Blocked Messages: {processing_stats['blocked_messages']}")
    print(f"   Deferred Messages: {processing_stats['deferred_messages']}")
    print(
        f"   Average Processing Time: {processing_stats['average_processing_time_ms']:.1f}ms"
    )

    if processing_stats["integration_errors"] > 0:
        print(f"   ⚠️ Integration Errors: {processing_stats['integration_errors']}")

    # Final health check
    final_health = await unified_processor.health_check()
    print("\n🏥 Final Health Check:")
    print(f"   Status: {final_health['status']}")

    if "abas_details" in final_health:
        abas_details = final_health["abas_details"]
        print(f"   ΛBAS: {abas_details.get('integration_mode', 'unknown')} mode")

    if "dast_details" in final_health:
        dast_details = final_health["dast_details"]
        print(f"   DΛST: {dast_details.get('integration_mode', 'unknown')} mode")

    if "nias_details" in final_health:
        nias_details = final_health["nias_details"]
        print(f"   NIΛS: {nias_details.get('status', 'unknown')} status")

    print("\n✅ Unified Three-Way Integration Test Complete")


async def test_integration_failure_scenarios():
    """Test how the unified processor handles integration failures"""
    print("\n🔧 Testing Integration Failure Scenarios")
    print("-" * 45)

    unified_processor = get_unified_processor()

    user_context = {"user_id": "test_failure_scenarios", "tier": "T2"}

    test_message = {
        "message_id": "failure_test_001",
        "type": "notification",
        "priority": 3,
        "description": "Test message for failure scenario testing",
    }

    # This will test the fallback mechanisms
    try:
        result = await unified_processor.process_message(
            user_context["user_id"], test_message, user_context
        )

        print(f"   Graceful Degradation: {result.get('status', 'unknown')}")
        print(
            f"   Fallback Mechanisms: {'activated' if result.get('unified_processing') else 'inactive'}"
        )

        # Check which integrations had fallbacks
        integration_status = result.get("integration_status", {})
        for system, available in integration_status.items():
            status = "active" if available else "fallback"
            print(f"   {system.upper()}: {status}")

    except Exception as e:
        print(f"   Error handling test: {e}")


async def test_performance_benchmarking():
    """Test performance of unified processing pipeline"""
    print("\n⚡ Performance Benchmarking")
    print("-" * 30)

    unified_processor = get_unified_processor()

    # Simple benchmark with multiple messages
    import time

    user_context = {"user_id": "benchmark_user", "tier": "T1"}
    test_message = {
        "message_id": "benchmark_msg",
        "type": "notification",
        "priority": 2,
        "description": "Benchmark test message",
    }

    num_messages = 10
    start_time = time.time()

    results = []
    for i in range(num_messages):
        test_message["message_id"] = f"benchmark_msg_{i}"
        result = await unified_processor.process_message(
            user_context["user_id"], test_message, user_context
        )
        results.append(result.get("processing_time_ms", 0))

    end_time = time.time()
    total_time = (end_time - start_time) * 1000

    print(f"   Messages Processed: {num_messages}")
    print(f"   Total Time: {total_time:.1f}ms")
    print(f"   Average Per Message: {total_time/num_messages:.1f}ms")
    print(f"   Min Processing Time: {min(results):.1f}ms")
    print(f"   Max Processing Time: {max(results):.1f}ms")

    # Check if we meet performance targets (< 100ms per message)
    avg_time = total_time / num_messages
    if avg_time < 100:
        print(f"   ✅ Performance Target Met: {avg_time:.1f}ms < 100ms")
    else:
        print(f"   ⚠️  Performance Target Missed: {avg_time:.1f}ms > 100ms")


if __name__ == "__main__":

    async def main():
        await test_unified_integration()
        await test_integration_failure_scenarios()
        await test_performance_benchmarking()

    asyncio.run(main())
