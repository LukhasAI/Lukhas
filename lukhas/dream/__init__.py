"""
LUKHAS Dream Engine Wrapper Module
===================================

Production-safe wrapper for core dream functionality.
All features are gated behind LUKHAS_DREAMS_ENABLED flag (default: OFF).

Usage:
    from lukhas.dream import is_enabled, simulate_dream, get_dream_engine

    if is_enabled():
        result = simulate_dream(seed="morning_thoughts")
"""

# T4: code=UP035 | ticket=ruff-cleanup | owner=lukhas-cleanup-team | status=resolved
# reason: Modernizing deprecated typing imports to native Python 3.9+ types for dream engine
# estimate: 10min | priority: high | dependencies: none

import asyncio
import logging
import os
import time
import uuid
from typing import Any, Optional
from collections.abc import Coroutine

logger = logging.getLogger(__name__)

# Feature flags - default OFF for safety
_DREAMS_ENABLED = (os.getenv("LUKHAS_DREAMS_ENABLED", "0") or "0").strip() == "1"
_PARALLEL_DREAMS_ENABLED = (os.getenv("LUKHAS_PARALLEL_DREAMS", "0") or "0").strip() == "1"

# Import core modules safely
_DREAMS_AVAILABLE = False
_dream_engine = None

# Configuration for retry and timeout
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 0.1
SIMULATION_TIMEOUT_SECONDS = 5.0


if _DREAMS_ENABLED:
    try:
        from labs.consciousness.dream.core.dream_engine import EnhancedDreamEngine
        from labs.core.unified.orchestration import BioOrchestrator
        from labs.core.unified.integration import UnifiedIntegration

        logger.info("Dream subsystem enabled, initializing...")

        # Instantiate real components
        orchestrator = BioOrchestrator()
        integration = UnifiedIntegration()

        _dream_engine = EnhancedDreamEngine(orchestrator=orchestrator, integration=integration)
        _DREAMS_AVAILABLE = True
        logger.info("Dream subsystem initialized successfully")
    except ImportError as e:
        logger.warning(f"Dream subsystem unavailable: {e}")
    except Exception as e:
        logger.error(f"Error initializing dream subsystem: {e}")


def _run_async(coro: Coroutine) -> Any:
    """Helper to run async code from a sync context."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


def is_enabled() -> bool:
    """Check if dream subsystem is enabled and available."""
    return _DREAMS_ENABLED and _DREAMS_AVAILABLE


def is_parallel_enabled() -> bool:
    """Check if parallel dreams feature is enabled."""
    return _PARALLEL_DREAMS_ENABLED and is_enabled()


def get_dream_engine() -> Optional[Any]:
    """
    Get the dream engine instance.
    """
    if not is_enabled():
        logger.debug("Dream subsystem not enabled")
        return None
    return _dream_engine


async def _simulate_dream_async(
    seed: str,
    user_id: str,
    context: Optional[dict] = None,
    parallel: bool = False,
) -> dict[str, Any]:
    """Async implementation of dream simulation with retry and timeout."""
    engine = get_dream_engine()
    if not engine:
        return {"success": False, "error": "Dream engine not available"}

    dream_id = f"dream_{uuid.uuid4().hex[:12]}"
    dream_object = {
        "id": dream_id,
        "user_id": user_id,
        "seed": seed,
        "context": context or {},
        "state": "pending",
        "metadata": {
            "created_at": time.time(),
            "engine_version": "2.0.0-beta",
            "mode": "parallel" if parallel else "sequential",
        },
    }

    last_exception = None
    for attempt in range(MAX_RETRIES):
        try:
            await asyncio.wait_for(
                engine.process_dream(dream_object),
                timeout=SIMULATION_TIMEOUT_SECONDS
            )
            return {
                "success": True,
                "dream_id": dream_id,
                "seed": seed,
                "result": dream_object,
                "metadata": dream_object["metadata"],
            }
        except asyncio.TimeoutError:
            last_exception = asyncio.TimeoutError(f"Simulation timed out after {SIMULATION_TIMEOUT_SECONDS}s")
            logger.warning(f"Attempt {attempt + 1} failed: {last_exception}")
        except Exception as e:
            last_exception = e
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            await asyncio.sleep(RETRY_DELAY_SECONDS)

    return {"success": False, "error": str(last_exception)}


def simulate_dream(
    seed: str,
    user_id: str,
    context: Optional[dict] = None,
    parallel: bool = False
) -> dict[str, Any]:
    """
    Simulate a dream based on a seed and context.
    """
    if not is_enabled():
        return {"success": False, "error": "Dream subsystem not enabled", "enabled": False}

    if parallel and not is_parallel_enabled():
        return {"success": False, "error": "Parallel dreams not enabled", "parallel_enabled": False}

    try:
        result = _run_async(_simulate_dream_async(seed, user_id, context, parallel))
        if result.get("success"):
            logger.info(f"Dream simulation completed: {result.get('dream_id')}")
        else:
            logger.error(f"Dream simulation failed for seed '{seed}': {result.get('error')}")
        return result
    except Exception as e:
        logger.error(f"Error simulating dream: {e}", exc_info=True)
        return {"success": False, "error": str(e), "seed": seed}


async def _get_dream_by_id_async(dream_id: str, user_id: str) -> Optional[dict]:
    """Async implementation of dream retrieval."""
    engine = get_dream_engine()
    if not engine:
        return None

    all_dreams = await engine.integration.get_data("enhanced_memories")
    for dream in all_dreams:
        if dream.get("id") == dream_id and dream.get("user_id") == user_id:
            return dream
    return None


def get_dream_by_id(dream_id: str, user_id: str) -> Optional[dict]:
    """
    Retrieve a dream by its ID, ensuring user isolation.
    """
    if not is_enabled():
        logger.debug("Dream subsystem not enabled")
        return None
    try:
        return _run_async(_get_dream_by_id_async(dream_id, user_id))
    except Exception as e:
        logger.error(f"Error retrieving dream: {e}", exc_info=True)
        return None


async def _parallel_dream_mesh_async(
    seeds: list[str],
    user_id: str,
    consensus_threshold: float = 0.7
) -> dict[str, Any]:
    """Async implementation of parallel dream mesh."""
    tasks = [_simulate_dream_async(seed, user_id, parallel=True) for seed in seeds]
    dream_results = await asyncio.gather(*tasks)

    successful_dreams = [d for d in dream_results if d.get("success")]

    return {
        "success": True,
        "mesh_id": f"mesh_{uuid.uuid4().hex[:8]}",
        "seeds": seeds,
        "consensus_threshold": consensus_threshold,
        "dreams": successful_dreams,
        "consensus": None,
        "metadata": {
            "timestamp": time.time(),
            "mode": "parallel_mesh",
            "successful_count": len(successful_dreams),
            "failed_count": len(dream_results) - len(successful_dreams),
        }
    }


def parallel_dream_mesh(
    seeds: list[str],
    user_id: str,
    consensus_threshold: float = 0.7
) -> dict[str, Any]:
    """
    Run parallel dream mesh with multiple seeds and consensus.
    """
    if not is_parallel_enabled():
        return {"success": False, "error": "Parallel dreams not enabled", "parallel_enabled": False}

    try:
        results = _run_async(_parallel_dream_mesh_async(seeds, user_id, consensus_threshold))
        logger.info(f"Parallel dream mesh completed: {results.get('mesh_id')}")
        return results
    except Exception as e:
        logger.error(f"Error in parallel dream mesh: {e}", exc_info=True)
        return {"success": False, "error": str(e), "seeds": seeds}


# Public API
__all__ = [
    "get_dream_by_id",
    "get_dream_engine",
    "is_enabled",
    "is_parallel_enabled",
    "parallel_dream_mesh",
    "simulate_dream",
]

# Expose feature flag status for testing
DREAMS_ENABLED = _DREAMS_ENABLED
PARALLEL_DREAMS_ENABLED = _PARALLEL_DREAMS_ENABLED
