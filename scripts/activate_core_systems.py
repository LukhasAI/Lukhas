#!/usr/bin/env python3
"""
LUKHAS Core Systems Activation Script
======================================
Activates the Signal Bus and Endocrine System for full AGI operation.
Part of the 21-day AGI implementation roadmap.
"""

import asyncio
import logging
import sys
from pathlib import Path

from core.endocrine.hormone_system import get_endocrine_system
from feedback.card_system import FeedbackCardSystem
from lukhas.orchestration.signals.signal_bus import Signal, SignalType, get_signal_bus

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


async def activate_signal_bus():
    """Activate and test the Signal Bus system."""
    logger.info("🚀 Activating Signal Bus...")

    try:
        # Get signal bus instance
        bus = get_signal_bus()

        # Start the bus
        await bus.start()
        logger.info("✅ Signal Bus started successfully")

        # Test signal emission
        test_signal = Signal(name=SignalType.NOVELTY, level=0.5, source="activation_script", ttl_ms=5000)

        success = bus.publish(test_signal)
        if success:
            logger.info("✅ Test signal published successfully")
        else:
            logger.warning("⚠️ Test signal blocked by cooldown")

        # Get metrics
        metrics = bus.get_metrics()
        logger.info(f"📊 Signal Bus Metrics: {metrics}")

        return bus

    except Exception as e:
        logger.error(f"❌ Failed to activate Signal Bus: {e}")
        raise


async def activate_endocrine_system():
    """Activate and test the Endocrine System."""
    logger.info("🧬 Activating Endocrine System...")

    try:
        # Get endocrine system instance
        endocrine = get_endocrine_system()

        # Start the system
        await endocrine.start()
        logger.info("✅ Endocrine System started successfully")

        # Test hormone triggers
        endocrine.trigger_reward_response(intensity=0.3)
        logger.info("✅ Test reward response triggered")

        # Wait a moment for hormones to update
        await asyncio.sleep(2)

        # Get hormone profile
        profile = endocrine.get_hormone_profile()
        logger.info(f"🧪 Hormone Profile: {profile['summary']}")
        logger.info(f"📊 Dominant State: {profile['dominant_state']}")

        # Get neuroplasticity
        from core.endocrine.hormone_system import get_neuroplasticity

        plasticity = get_neuroplasticity()
        logger.info(f"🧠 Current Neuroplasticity: {plasticity:.2f}")

        return endocrine

    except Exception as e:
        logger.error(f"❌ Failed to activate Endocrine System: {e}")
        raise


async def connect_systems(bus, endocrine):
    """Connect Signal Bus to Endocrine System."""
    logger.info("🔗 Connecting Signal Bus to Endocrine System...")

    try:
        # Create hormone receptor for signal bus
        async def hormone_receptor(effects):
            """Receive hormone effects and emit corresponding signals."""
            # High stress triggers stress signal
            if effects.get("stress_level", 0) > 0.7:
                stress_signal = Signal(
                    name=SignalType.STRESS,
                    level=effects["stress_level"],
                    source="endocrine_system",
                    metadata={"hormones": effects},
                )
                bus.publish(stress_signal)
                logger.info(f"📡 Emitted stress signal: {effects['stress_level']:.2f}")

            # High motivation triggers novelty signal
            if effects.get("motivation", 0) > 0.7:
                novelty_signal = Signal(
                    name=SignalType.NOVELTY,
                    level=effects["motivation"],
                    source="endocrine_system",
                    metadata={"dopamine": effects.get("motivation")},
                )
                bus.publish(novelty_signal)
                logger.info(f"📡 Emitted novelty signal: {effects['motivation']:.2f}")

        # Register the receptor
        endocrine.register_receptor("signal_bus", hormone_receptor)
        logger.info("✅ Systems connected successfully")

        # Test the connection with a stress trigger
        logger.info("🧪 Testing system connection with stress trigger...")
        endocrine.trigger_stress_response(intensity=0.8)
        await asyncio.sleep(3)  # Wait for propagation

        # Check signal bus for stress signals
        active_signals = bus.get_active_signals()
        stress_signals = [s for s in active_signals if s.name == SignalType.STRESS]
        if stress_signals:
            logger.info(f"✅ Connection verified: {len(stress_signals} stress signals active")
        else:
            logger.warning("⚠️ No stress signals detected - connection may need debugging")

    except Exception as e:
        logger.error(f"❌ Failed to connect systems: {e}")
        raise


async def activate_feedback_system():
    """Activate the Feedback Card System."""
    logger.info("📝 Activating Feedback Card System...")

    try:
        # Initialize feedback system
        feedback = FeedbackCardSystem(storage_path="feedback_data")

        # Create a test feedback card
        test_card = feedback.capture_feedback(
            action_id="test_action_001",
            rating=4,
            note="System activation test",
            symbols=["🚀", "✅"],
            context={
                "prompt": "Activate core systems",
                "response": "Systems activated successfully",
                "signal_state": {"stress": 0.3, "novelty": 0.7},
            },
            user_id="system_test",
        )

        logger.info(f"✅ Test feedback card created: {test_card.card_id}")

        # Get metrics
        metrics = feedback.get_metrics()
        logger.info(f"📊 Feedback System Metrics: {metrics}")

        return feedback

    except Exception as e:
        logger.error(f"❌ Failed to activate Feedback System: {e}")
        raise


async def main():
    """Main activation sequence."""
    logger.info("=" * 60)
    logger.info("🚀 LUKHAS AGI CORE SYSTEMS ACTIVATION")
    logger.info("=" * 60)

    try:
        # Phase 1: Activate individual systems
        bus = await activate_signal_bus()
        endocrine = await activate_endocrine_system()
        feedback = await activate_feedback_system()

        # Phase 2: Connect systems
        await connect_systems(bus, endocrine)

        logger.info("=" * 60)
        logger.info("✅ ALL CORE SYSTEMS ACTIVATED SUCCESSFULLY")
        logger.info("=" * 60)

        # Keep systems running for observation
        logger.info("Systems running. Press Ctrl+C to stop...")

        try:
            while True:
                # Periodic status check
                await asyncio.sleep(10)

                # Log current status
                bus_metrics = bus.get_metrics()
                hormone_levels = endocrine.get_hormone_levels()
                feedback_metrics = feedback.get_metrics()

                logger.info("📊 Status Update:")
                logger.info(f"  Signal Bus: {bus_metrics['active_signals']} active signals")
                logger.info(f"  Endocrine: {endocrine._determine_dominant_state(} state")
                logger.info(f"  Feedback: {feedback_metrics['total_cards']} cards captured")

        except KeyboardInterrupt:
            logger.info("\n🛑 Shutting down systems...")

    except Exception as e:
        logger.error(f"❌ Activation failed: {e}")
        return 1

    finally:
        # Cleanup
        if "bus" in locals():
            await bus.stop()
        if "endocrine" in locals():
            await endocrine.stop()
        logger.info("👋 Systems shut down gracefully")

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
