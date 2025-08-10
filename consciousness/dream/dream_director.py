from typing import Any, Dict, List

from core.common import get_logger

from .immersive_ingestion import dream_breath

logger = get_logger(__name__)


# ΛTAG: dream_director
async def direct_dream_flow(memory_snaps: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Run a minimal dream cycle and produce tag metrics."""
    result = await dream_breath(memory_snaps)
    reflection = result.get("reflection", {})
    tags = [snap.get("tag", "memory") for snap in memory_snaps]
    tags.append("dream_generated")
    drift = result.get("affect_delta", 0.0)
    convergence = max(0.0, 1.0 - drift)
    metrics = {"driftScore": drift, "convergence": convergence}
    logger.debug("Dream flow tags=%s metrics=%s", tags, metrics)
    return {"tags": tags, "metrics": metrics, "dream": reflection}
