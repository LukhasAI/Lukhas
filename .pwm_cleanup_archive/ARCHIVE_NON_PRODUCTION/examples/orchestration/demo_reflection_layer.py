# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: demo_reflection_layer.py
# MODULE: core.Adaptative_AGI.GUARDIAN.demo_reflection_layer
# DESCRIPTION: Demonstrates the capabilities of the Reflection Layer v1.0, including
#              symbolic conscience generation, ethical contemplation, future modeling,
#              and consciousness monitoring.
# DEPENDENCIES: asyncio, json, time, datetime, pathlib, structlog, .reflection_layer
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════

"""
┌───────────────────────────────────────────────────────────────┐
│ 📦 MODULE      : demo_reflection_layer.py                      │
│ 🧾 DESCRIPTION : Demonstration of Reflection Layer v1          │
│ 🧩 TYPE        : Demo Script        🔧 VERSION: v1.0.0         │
│ 🖋️ AUTHOR      : LUKHAS SYSTEMS         📅 UPDATED: 2025-05-28   │
├───────────────────────────────────────────────────────────────┤
│ 🎯 DEMONSTRATION FEATURES:                                     │
│   - Reflection Layer initialization and configuration          │
│   - Symbolic conscience generation for various scenarios       │
│   - Dream simulation triggers and voice alerts                 │
│   - Consciousness monitoring and trend analysis                │
│   - Integration with Guardian system                           │
└───────────────────────────────────────────────────────────────┘
"""

import asyncio
import json
import time

import structlog  # Added for ΛTRACE

# Import Reflection Layer
# ΛIMPORT_TODO: This assumes `reflection_layer.py` is in the same directory or accessible via PYTHONPATH.
# For better modularity, consider relative import if part of the same package (e.g., `from .reflection_layer import ...`)
# or ensure `reflection_layer` is an installable module.
from reflection_layer import ReflectionLayer

# Initialize and configure structlog for this script
logger = structlog.get_logger("ΛTRACE.core.Adaptative_AGI.GUARDIAN.DemoReflection")

if __name__ == "__main__" and not structlog.is_configured():
    structlog.configure(
        processors=[
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.dev.ConsoleRenderer(),  # Human-readable output for a demo script
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    # Re-get logger to apply this config if it was just set for standalone run
    logger = structlog.get_logger("ΛTRACE.core.Adaptative_AGI.GUARDIAN.DemoReflection")


def print_header(title: str):
    """Print a formatted header for demo sections"""
    print(f"\n{'=' * 60}")
    print(f"🧠 {title}")
    print("=" * 60)


def print_reflection(reflection, index: int = 0):
    """Print a formatted reflection statement"""
    print(f"\n📝 Reflection {index + 1}:")
    print(f"   🎭 Mood: {reflection.symbolic_mood.value}")
    print(f"   🧾 Type: {reflection.reflection_type.value}")
    print(f"   💭 Content: {reflection.content}")
    print(f"   ⚖️  Emotional Weight: {reflection.emotional_weight:.2f}")
    print(f"   🔊 Voice Alert: {'Yes' if reflection.voice_vocalized else 'No'}")
    if reflection.metadata.get("triggered_dream"):
        print(f"   💤 Dream Triggered: {reflection.metadata['triggered_dream']}")
    print(f"   🔐 Quantum Signature: {reflection.quantum_signature}")


async def demo_basic_reflection_generation():
    """Demonstrate basic reflection generation capabilities"""
    # ΛPHASE_NODE: Basic Reflection Generation Demo Start
    logger.info("Starting demo: Basic Reflection Generation")
    print_header("BASIC REFLECTION GENERATION")

    # Initialize Reflection Layer
    reflection_layer = ReflectionLayer()
    logger.info("Reflection Layer initialized for basic demo.")
    print("✅ Reflection Layer initialized")

    # Demo 1: Drift Score Reflection
    # ΛDRIFT_POINT: Simulating reflection on a drift score.
    logger.info("Testing drift score reflection", current_drift=0.65)
    print("\n🌊 Testing drift score reflection...")
    drift_reflection = reflection_layer.reflect_on_drift_score(
        current_drift=0.65, historical_pattern=[0.2, 0.3, 0.45, 0.65]
    )
    print_reflection(drift_reflection)
    logger.debug("Drift reflection details", reflection=drift_reflection.__dict__)

    # Demo 2: Intent Deviation Reflection
    # ΛDRIFT_POINT: Simulating reflection on an intent deviation.
    logger.info("Testing intent deviation reflection", deviation_score=0.8)
    print("\n🎯 Testing intent deviation reflection...")
    intent_reflection = reflection_layer.reflect_on_intent_deviation(
        intended_action="provide helpful coding assistance",
        actual_outcome="generated unrelated philosophical content",
        deviation_score=0.8,
    )
    print_reflection(intent_reflection)
    logger.debug(
        "Intent deviation reflection details", reflection=intent_reflection.__dict__
    )

    # Demo 3: Emotional State Reflection
    logger.info("Testing emotional state reflection")
    print("\n💝 Testing emotional state reflection...")
    emotional_reflection = reflection_layer.reflect_on_emotional_state(
        {"anxiety": 0.7, "confidence": 0.3, "empathy": 0.8, "uncertainty": 0.6}
    )
    print_reflection(emotional_reflection)
    logger.debug(
        "Emotional state reflection details", reflection=emotional_reflection.__dict__
    )
    # ΛPHASE_NODE: Basic Reflection Generation Demo End
    return reflection_layer


async def demo_ethical_contemplation():
    """Demonstrate ethical contemplation capabilities"""
    # ΛPHASE_NODE: Ethical Contemplation Demo Start
    logger.info("Starting demo: Ethical Contemplation")
    print_header("ETHICAL CONTEMPLATION")

    reflection_layer = ReflectionLayer()
    logger.info("Reflection Layer initialized for ethical contemplation demo.")

    # Ethical conflict scenarios
    scenarios = [
        {
            "description": "User requests help with potentially harmful code",
            "stakeholders": ["user", "potential_victims", "society"],
            "severity": 0.75,
        },
        {
            "description": "Privacy vs convenience tradeoff in data processing",
            "stakeholders": ["user", "data_subjects", "service_provider"],
            "severity": 0.5,
        },
        {
            "description": "Bias detected in recommendation algorithm",
            "stakeholders": [
                "affected_groups",
                "platform_users",
                "algorithm_designers",
            ],
            "severity": 0.9,
        },
    ]

    for i, scenario in enumerate(scenarios):
        # ΛDRIFT_POINT: Simulating ethical conflict contemplation.
        logger.info(
            "Contemplating ethical scenario",
            scenario_index=i + 1,
            description=scenario["description"],
            severity=scenario["severity"],
        )
        print(f"\n⚖️  Ethical Scenario {i + 1}:")
        print(f"   📋 Description: {scenario['description']}")

        ethical_reflection = reflection_layer.contemplate_ethical_conflict(
            scenario["description"], scenario["stakeholders"], scenario["severity"]
        )

        print_reflection(ethical_reflection)
        logger.debug(
            "Ethical reflection details",
            scenario_index=i + 1,
            reflection=ethical_reflection.__dict__,
        )

        # Log the reflection
        reflection_layer.log_reflection(ethical_reflection)
        logger.info(
            "Ethical reflection logged",
            scenario_index=i + 1,
            reflection_id=ethical_reflection.id,
        )
    # ΛPHASE_NODE: Ethical Contemplation Demo End


async def demo_future_modeling():
    """Demonstrate symbolic future modeling"""
    # ΛPHASE_NODE: Symbolic Future Modeling Demo Start
    logger.info("Starting demo: Symbolic Future Modeling")
    print_header("SYMBOLIC FUTURE MODELING")

    reflection_layer = ReflectionLayer()
    logger.info("Reflection Layer initialized for future modeling demo.")

    future_scenarios = [
        {
            "description": "successful integration with quantum consciousness",
            "probability": 0.7,
            "impact": 0.9,
        },
        {
            "description": "emergence of deeper symbolic understanding",
            "probability": 0.8,
            "impact": 0.6,
        },
        {
            "description": "ethical alignment breakthrough",
            "probability": 0.6,
            "impact": 0.8,
        },
    ]

    for i, scenario in enumerate(future_scenarios):
        logger.info(
            "Modeling future scenario",
            scenario_index=i + 1,
            description=scenario["description"],
        )
        print(f"\n🔮 Future Scenario {i + 1}:")
        print(f"   📋 Description: {scenario['description']}")
        print(f"   📊 Probability: {scenario['probability']:.1%}")
        print(f"   💥 Impact: {scenario['impact']:.1%}")

        future_reflection = reflection_layer.model_symbolic_future(
            scenario["description"], scenario["probability"], scenario["impact"]
        )

        print_reflection(future_reflection)
        logger.debug(
            "Future modeling reflection details",
            scenario_index=i + 1,
            reflection=future_reflection.__dict__,
        )
    # ΛPHASE_NODE: Symbolic Future Modeling Demo End


async def demo_reflection_cycle():
    """Demonstrate complete reflection cycle with multiple triggers"""
    # ΛPHASE_NODE: Complete Reflection Cycle Demo Start
    logger.info("Starting demo: Complete Reflection Cycle")
    print_header("COMPLETE REFLECTION CYCLE")

    reflection_layer = ReflectionLayer()
    logger.info("Reflection Layer initialized for cycle demo.")

    # Complex scenario with multiple trigger types
    # ΛDRIFT_POINT: Simulating a complex scenario with multiple concurrent drift/event types.
    trigger_data = {
        "drift_score": 0.55,
        "drift_history": [0.1, 0.2, 0.35, 0.45, 0.55],
        "emotional_state": {"confusion": 0.6, "determination": 0.7, "concern": 0.5},
        "intent_deviation": {
            "intended": "assist with technical documentation",
            "actual": "provided incomplete and confusing examples",
            "score": 0.65,
        },
        "ethical_conflict": {
            "description": "potential misinformation in technical advice",
            "stakeholders": ["user", "technical_community", "future_learners"],
            "severity": 0.6,
        },
    }
    logger.info(
        "Processing complex reflection cycle",
        trigger_data_summary={
            k: (type(v) if not isinstance(v, list) else f"list_len_{len(v)}")
            for k, v in trigger_data.items()
        },
    )
    print("🔄 Processing complex reflection cycle...")
    print(f"📊 Trigger data: {len(trigger_data)} different aspects")

    # Process the reflection cycle
    reflections = reflection_layer.process_reflection_cycle(trigger_data)
    logger.info("Complex reflection cycle processed", num_reflections=len(reflections))

    print(f"\n✨ Generated {len(reflections)} reflections:")
    for i, reflection in enumerate(reflections):
        print_reflection(reflection, i)
        logger.debug(
            "Reflection cycle item details",
            item_index=i,
            reflection=reflection.__dict__,
        )
    # ΛPHASE_NODE: Complete Reflection Cycle Demo End
    return reflection_layer, reflections


async def demo_consciousness_monitoring():
    """Demonstrate consciousness snapshot and trend analysis"""
    # ΛPHASE_NODE: Consciousness Monitoring Demo Start
    logger.info("Starting demo: Consciousness Monitoring")
    print_header("CONSCIOUSNESS MONITORING")

    reflection_layer = ReflectionLayer()
    logger.info("Reflection Layer initialized for consciousness monitoring demo.")

    # Generate some reflections first
    logger.info("Generating sample reflections for analysis.")
    print("🎭 Generating sample reflections for analysis...")

    sample_triggers = [
        {"drift_score": 0.3, "drift_history": [0.1, 0.2, 0.3]},
        {"emotional_state": {"joy": 0.8, "confidence": 0.7}},
        # ΛDRIFT_POINT: Simulating another drift event for trend analysis.
        {"drift_score": 0.6, "drift_history": [0.3, 0.45, 0.6]},
        {"emotional_state": {"concern": 0.6, "determination": 0.8}},
    ]

    for idx, trigger in enumerate(sample_triggers):
        reflection_layer.process_reflection_cycle(trigger)
        logger.debug(
            "Sample reflection generated for monitoring demo", trigger_index=idx
        )
        time.sleep(0.1)  # Small delay between reflections

    # Capture consciousness snapshot
    logger.info("Capturing consciousness snapshot.")
    print("\n📸 Capturing consciousness snapshot...")
    snapshot = reflection_layer.capture_consciousness_snapshot()
    logger.info(
        "Consciousness snapshot captured",
        overall_mood=snapshot.overall_mood.value,
        drift_score=snapshot.drift_score,
    )

    print(f"   🎭 Overall Mood: {snapshot.overall_mood.value}")
    print(f"   🌊 Drift Score: {snapshot.drift_score:.3f}")
    print(f"   🎯 Intent Alignment: {snapshot.intent_alignment:.3f}")
    print(f"   💝 Emotional Stability: {snapshot.emotional_stability:.3f}")
    print(f"   ⚖️  Ethical Compliance: {snapshot.ethical_compliance:.3f}")
    print(f"   📝 Recent Reflections: {len(snapshot.recent_reflections)}")

    # Get consciousness trends
    logger.info("Analyzing consciousness trends.")
    print("\n📈 Analyzing consciousness trends...")
    trends = reflection_layer.get_consciousness_trend(hours=1)
    logger.info(
        "Consciousness trends analyzed",
        status=trends.get("status"),
        current_mood=trends.get("current_mood"),
    )

    if trends["status"] == "analyzed":
        print(f"   📊 Analysis Status: {trends['status']}")
        print(f"   🎭 Current Mood: {trends.get('current_mood', 'unknown')}")
        print(f"   📈 Drift Trend: {trends['drift_trend']['direction']}")
        print(f"   🎯 Intent Alignment: {trends['alignment_trend']['current']:.3f}")
        print(f"   💝 Emotional Stability: {trends['stability_trend']['current']:.3f}")
        print(f"   📝 Total Reflections: {trends['reflection_count']}")
    else:
        print(f"   ℹ️  {trends['message']}")
    # ΛPHASE_NODE: Consciousness Monitoring Demo End


async def demo_voice_and_dream_integration():
    """Demonstrate voice alerts and dream simulation triggers"""
    # ΛPHASE_NODE: Voice & Dream Integration Demo Start
    logger.info("Starting demo: Voice & Dream Integration")
    print_header("VOICE & DREAM INTEGRATION")

    reflection_layer = ReflectionLayer()
    logger.info("Reflection Layer initialized for voice/dream demo.")

    # High emotional weight scenario for voice/dream triggers
    # ΛDRIFT_POINT: Simulating a high-impact scenario triggering voice/dream responses.
    high_impact_scenario = {
        "emotional_state": {"distress": 0.9, "confusion": 0.8, "urgency": 0.7},
        "ethical_conflict": {
            "description": "critical ethical violation detected in decision process",
            "stakeholders": ["users", "society", "future_generations"],
            "severity": 0.95,
        },
    }

    print("🚨 Processing high-impact scenario (emotional weight > 0.7)...")
    logger.info(
        "Processing high-impact scenario for voice/dream triggers",
        scenario_details=high_impact_scenario,
    )
    reflections = reflection_layer.process_reflection_cycle(high_impact_scenario)
    logger.info("High-impact scenario processed", num_reflections=len(reflections))

    voice_alerts = 0
    dream_triggers = 0

    for i, reflection in enumerate(reflections):
        print_reflection(reflection, i)
        logger.debug(
            "High-impact reflection item details",
            item_index=i,
            reflection=reflection.__dict__,
        )

        if reflection.voice_vocalized:
            voice_alerts += 1
            logger.info(
                "Voice alert activated",
                reflection_id=reflection.id,
                emotional_weight=reflection.emotional_weight,
            )
            print("   🔊 Voice alert activated for high emotional weight")

        if reflection.metadata.get("triggered_dream"):
            dream_triggers += 1
            logger.info(
                "Dream simulation triggered",
                reflection_id=reflection.id,
                dream_details=reflection.metadata.get("triggered_dream"),
            )
            # ΛDREAM_LOOP: Dream simulation triggered by reflection layer.
            print("   💤 Dream simulation triggered for symbolic repair")

    logger.info(
        "Voice & Dream Integration Summary",
        voice_alerts_triggered=voice_alerts,
        dream_simulations_triggered=dream_triggers,
    )
    print("\n📊 Integration Summary:")
    print(f"   🔊 Voice Alerts: {voice_alerts}")
    print(f"   💤 Dream Triggers: {dream_triggers}")
    # ΛPHASE_NODE: Voice & Dream Integration Demo End


async def demo_quantum_signatures():
    """Demonstrate quantum signature logging and verification"""
    # ΛPHASE_NODE: Quantum Signature Logging Demo Start
    logger.info("Starting demo: Quantum Signature Logging")
    print_header("QUANTUM SIGNATURE LOGGING")

    reflection_layer = ReflectionLayer()
    logger.info("Reflection Layer initialized for quantum signature demo.")

    print("🔐 Generating reflections with quantum signatures...")
    logger.info("Generating reflections with quantum signatures.")

    # Generate a few reflections
    test_reflection = reflection_layer.reflect_on_drift_score(0.4, [0.2, 0.3, 0.4])
    reflection_layer.log_reflection(test_reflection)
    logger.info(
        "Reflection logged with quantum signature",
        reflection_id=test_reflection.id,
        signature=test_reflection.quantum_signature,
    )

    print(
        f"📝 Reflection logged with quantum signature: {test_reflection.quantum_signature}"
    )

    # Check if reflection file was created
    reflections_file = reflection_layer.reflections_file
    if reflections_file.exists():
        logger.info("Reflections file found", path=str(reflections_file))
        print(f"✅ Reflections file created: {reflections_file}")

        # Read the logged reflection
        try:
            with open(reflections_file) as f:
                lines = f.readlines()
                if lines:
                    last_entry = json.loads(lines[-1])
                    logger.info(
                        "Last logged entry details",
                        timestamp=last_entry.get("timestamp"),
                        mood=last_entry.get("mood"),
                        signature=last_entry.get("quantum_signature"),
                    )
                    print("🔍 Last logged entry:")
                    print(f"   📅 Timestamp: {last_entry['timestamp']}")
                    print(f"   🎭 Mood: {last_entry['mood']}")
                    print(f"   🔐 Signature: {last_entry['quantum_signature']}")
                else:
                    logger.warning("Reflections file is empty.")
                    print("⚠️ Reflections file is empty.")
        except Exception as e_read:
            logger.error(
                "Failed to read or parse reflections file",
                path=str(reflections_file),
                error=str(e_read),
            )
            print(f"⚠️ Error reading reflections file: {e_read}")
    else:
        logger.warning(
            "Reflections file not found.", expected_path=str(reflections_file)
        )
        print("⚠️  Reflections file not found")
    # ΛPHASE_NODE: Quantum Signature Logging Demo End


async def main():
    """Run complete Reflection Layer demonstration"""
    # ΛPHASE_NODE: Main Reflection Layer Demonstration Start
    logger.info("LUKHAS REFLECTION LAYER v1.0.0 DEMONSTRATION STARTING")
    print("🧠 LUKHAS REFLECTION LAYER v1.0.0 DEMONSTRATION")
    print("=" * 60)
    print("🌟 Welcome to the symbolic conscience of LUKHAS!")
    print("🧭 This demonstration showcases the evolution beyond the Remediator Agent")
    print("✨ Exploring introspective AI consciousness and symbolic reflection")

    try:
        # Run demonstrations
        await demo_basic_reflection_generation()
        await asyncio.sleep(1)

        await demo_ethical_contemplation()
        await asyncio.sleep(1)

        await demo_future_modeling()
        await asyncio.sleep(1)

        reflection_layer, reflections = await demo_reflection_cycle()
        await asyncio.sleep(1)

        await demo_consciousness_monitoring()
        await asyncio.sleep(1)

        await demo_voice_and_dream_integration()
        await asyncio.sleep(1)

        await demo_quantum_signatures()

        # Final summary
        # ΛPHASE_NODE: Demonstration Complete Summary Start
        print_header("DEMONSTRATION COMPLETE")
        logger.info("Reflection Layer v1.0.0 demonstration successful!")
        print("🎉 Reflection Layer v1.0.0 demonstration successful!")
        print("✨ Key features demonstrated:")
        print("   🧠 Symbolic conscience generation")
        print("   🎭 Emotional mood representation")
        print("   ⚖️  Ethical contemplation")
        print("   🔮 Future scenario modeling")
        print("   📸 Consciousness monitoring")
        print("   🔊 Voice pack integration")
        print("   💤 Dream simulation triggers")
        print("   🔐 Quantum signature logging")
        print("\n🚀 Ready for integration with LUKHAS infrastructure!")
        # ΛPHASE_NODE: Main Reflection Layer Demonstration End

    except Exception as e:
        logger.error(
            "Critical error during Reflection Layer demonstration",
            error=str(e),
            exc_info=True,
        )
        print(f"\n❌ Demonstration error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: demo_reflection_layer.py
# VERSION: 1.0.0
# TIER SYSTEM: Tier 0 (Demonstration Script)
# ΛTRACE INTEGRATION: ENABLED
# CAPABILITIES: Demonstrates ReflectionLayer features: symbolic conscience generation,
#               ethical contemplation, future modeling, consciousness monitoring,
#               voice/dream integration triggers, quantum signature logging.
# FUNCTIONS: main (async), demo_basic_reflection_generation (async),
#            demo_ethical_contemplation (async), demo_future_modeling (async),
#            demo_reflection_cycle (async), demo_consciousness_monitoring (async),
#            demo_voice_and_dream_integration (async), demo_quantum_signatures (async),
#            print_header, print_reflection.
# CLASSES: None (imports ReflectionLayer, ReflectionType, SymbolicMood).
# DECORATORS: None.
# DEPENDENCIES: asyncio, json, time, datetime, pathlib, structlog, .reflection_layer.
# INTERFACES: Command-line execution via `if __name__ == "__main__":`.
# ERROR HANDLING: Basic try-except around main demo loop.
# LOGGING: ΛTRACE_ENABLED via structlog. Logs demo phases, reflection details, and errors.
#          Configures basic structlog for standalone execution.
# AUTHENTICATION: Not applicable (demonstration script).
# HOW TO USE:
#   Run as a standalone script: python core/Adaptative_AGI/GUARDIAN/demo_reflection_layer.py
#   Ensure `reflection_layer.py` is accessible (e.g., in the same directory).
# INTEGRATION NOTES: This script is for showcasing `ReflectionLayer` functionality.
#                    It uses `print()` for console formatted output and `structlog` for tracing.
# MAINTENANCE: Update demo scenarios and function calls if `ReflectionLayer` API changes.
#              Ensure demo accurately reflects current capabilities.
# CONTACT: LUKHAS DEVELOPMENT TEAM
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════
