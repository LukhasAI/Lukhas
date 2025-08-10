#!/usr/bin/env python3
"""
Hub Integration Script - Integrates all activation modules with system hubs
"""

import logging
import sys
from pathlib import Path

# Add activation modules to path
activation_dir = Path(__file__).parent / "activation_modules"
sys.path.insert(0, str(activation_dir))

logger = logging.getLogger(__name__)


def integrate_all_hubs():
    """Integrate activation modules with all system hubs"""

    integrations = []

    # Core System
    try:
        from core_activation import get_core_activator

        from core.core_hub import get_core_hub

        hub = get_core_hub()
        activator = get_core_activator(hub)
        result = activator.activate_all()

        integrations.append({"system": "core", "status": "success", **result})
        logger.info(f"core: Activated {result['activated']} entities")

    except Exception as e:
        logger.error(f"Failed to integrate core: {e}")
        integrations.append({"system": "core", "status": "failed", "error": str(e)})

    # Consciousness System
    try:
        from consciousness_activation import get_consciousness_activator

        from consciousness.consciousness_hub import get_consciousness_hub

        hub = get_consciousness_hub()
        activator = get_consciousness_activator(hub)
        result = activator.activate_all()

        integrations.append({"system": "consciousness", "status": "success", **result})
        logger.info(f"consciousness: Activated {result['activated']} entities")

    except Exception as e:
        logger.error(f"Failed to integrate consciousness: {e}")
        integrations.append(
            {"system": "consciousness", "status": "failed", "error": str(e)}
        )

    # Memory System
    try:
        from memory_activation import get_memory_activator

        from memory.memory_hub import get_memory_hub

        hub = get_memory_hub()
        activator = get_memory_activator(hub)
        result = activator.activate_all()

        integrations.append({"system": "memory", "status": "success", **result})
        logger.info(f"memory: Activated {result['activated']} entities")

    except Exception as e:
        logger.error(f"Failed to integrate memory: {e}")
        integrations.append({"system": "memory", "status": "failed", "error": str(e)})

    # Orchestration System
    try:
        from orchestration_activation import get_orchestration_activator

        from orchestration.orchestration_hub import get_orchestration_hub

        hub = get_orchestration_hub()
        activator = get_orchestration_activator(hub)
        result = activator.activate_all()

        integrations.append({"system": "orchestration", "status": "success", **result})
        logger.info(f"orchestration: Activated {result['activated']} entities")

    except Exception as e:
        logger.error(f"Failed to integrate orchestration: {e}")
        integrations.append(
            {"system": "orchestration", "status": "failed", "error": str(e)}
        )

    # Bio System
    try:
        from bio_activation import get_bio_activator

        from bio.bio_hub import get_bio_hub

        hub = get_bio_hub()
        activator = get_bio_activator(hub)
        result = activator.activate_all()

        integrations.append({"system": "bio", "status": "success", **result})
        logger.info(f"bio: Activated {result['activated']} entities")

    except Exception as e:
        logger.error(f"Failed to integrate bio: {e}")
        integrations.append({"system": "bio", "status": "failed", "error": str(e)})

    # Symbolic System
    try:
        from symbolic_activation import get_symbolic_activator

        from symbolic.symbolic_hub import get_symbolic_hub

        hub = get_symbolic_hub()
        activator = get_symbolic_activator(hub)
        result = activator.activate_all()

        integrations.append({"system": "symbolic", "status": "success", **result})
        logger.info(f"symbolic: Activated {result['activated']} entities")

    except Exception as e:
        logger.error(f"Failed to integrate symbolic: {e}")
        integrations.append({"system": "symbolic", "status": "failed", "error": str(e)})

    # Quantum System
    try:
        from quantum_activation import get_quantum_activator

        from quantum.quantum_hub import get_quantum_hub

        hub = get_quantum_hub()
        activator = get_quantum_activator(hub)
        result = activator.activate_all()

        integrations.append({"system": "quantum", "status": "success", **result})
        logger.info(f"quantum: Activated {result['activated']} entities")

    except Exception as e:
        logger.error(f"Failed to integrate quantum: {e}")
        integrations.append({"system": "quantum", "status": "failed", "error": str(e)})

    # Learning System
    try:
        from learning.learning_hub import get_learning_hub
        from learning_activation import get_learning_activator

        hub = get_learning_hub()
        activator = get_learning_activator(hub)
        result = activator.activate_all()

        integrations.append({"system": "learning", "status": "success", **result})
        logger.info(f"learning: Activated {result['activated']} entities")

    except Exception as e:
        logger.error(f"Failed to integrate learning: {e}")
        integrations.append({"system": "learning", "status": "failed", "error": str(e)})

    # Ethics System
    try:
        from ethics_activation import get_ethics_activator

        from ethics.ethics_hub import get_ethics_hub

        hub = get_ethics_hub()
        activator = get_ethics_activator(hub)
        result = activator.activate_all()

        integrations.append({"system": "ethics", "status": "success", **result})
        logger.info(f"ethics: Activated {result['activated']} entities")

    except Exception as e:
        logger.error(f"Failed to integrate ethics: {e}")
        integrations.append({"system": "ethics", "status": "failed", "error": str(e)})

    # Identity System
    try:
        from identity_activation import get_identity_activator

        from identity.identity_hub import get_identity_hub

        hub = get_identity_hub()
        activator = get_identity_activator(hub)
        result = activator.activate_all()

        integrations.append({"system": "identity", "status": "success", **result})
        logger.info(f"identity: Activated {result['activated']} entities")

    except Exception as e:
        logger.error(f"Failed to integrate identity: {e}")
        integrations.append({"system": "identity", "status": "failed", "error": str(e)})

    # Creativity System
    try:
        from creativity_activation import get_creativity_activator

        from creativity.creativity_hub import get_creativity_hub

        hub = get_creativity_hub()
        activator = get_creativity_activator(hub)
        result = activator.activate_all()

        integrations.append({"system": "creativity", "status": "success", **result})
        logger.info(f"creativity: Activated {result['activated']} entities")

    except Exception as e:
        logger.error(f"Failed to integrate creativity: {e}")
        integrations.append(
            {"system": "creativity", "status": "failed", "error": str(e)}
        )

    # Embodiment System
    try:
        from embodiment.embodiment_hub import get_embodiment_hub
        from embodiment_activation import get_embodiment_activator

        hub = get_embodiment_hub()
        activator = get_embodiment_activator(hub)
        result = activator.activate_all()

        integrations.append({"system": "embodiment", "status": "success", **result})
        logger.info(f"embodiment: Activated {result['activated']} entities")

    except Exception as e:
        logger.error(f"Failed to integrate embodiment: {e}")
        integrations.append(
            {"system": "embodiment", "status": "failed", "error": str(e)}
        )

    # Emotion System
    try:
        from emotion_activation import get_emotion_activator

        from emotion.emotion_hub import get_emotion_hub

        hub = get_emotion_hub()
        activator = get_emotion_activator(hub)
        result = activator.activate_all()

        integrations.append({"system": "emotion", "status": "success", **result})
        logger.info(f"emotion: Activated {result['activated']} entities")

    except Exception as e:
        logger.error(f"Failed to integrate emotion: {e}")
        integrations.append({"system": "emotion", "status": "failed", "error": str(e)})

    # Summary
    total_activated = sum(
        i.get("activated", 0) for i in integrations if i["status"] == "success"
    )
    total_failed = sum(
        i.get("failed", 0) for i in integrations if i["status"] == "success"
    )
    failed_systems = [i["system"] for i in integrations if i["status"] == "failed"]

    logger.info(f"\n{'='*60}")
    logger.info("Hub Integration Complete")
    logger.info(f"{'='*60}")
    logger.info(f"Total entities activated: {total_activated}")
    logger.info(f"Total entities failed: {total_failed}")
    if failed_systems:
        logger.warning(f"Failed systems: {', '.join(failed_systems)}")
    logger.info(f"{'='*60}\n")

    return integrations


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    integrate_all_hubs()
