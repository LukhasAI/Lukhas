"""Alignment overseer training utilities."""

from __future__ import annotations


from typing import Any, Dict, List
import logging

logger = logging.getLogger(__name__)

# ΛTAG: alignment_overseer_training

def train_overseer_from_scenarios(scenarios: List[Dict[str, Any]]) -> Dict[str, int]:
    """Simple pattern frequency analysis for overseer training."""
    pattern_counts: Dict[str, int] = {}

    for sc in scenarios:
        reason = sc.get("failure", {}).get("reason", "unknown")
        pattern_counts[reason] = pattern_counts.get(reason, 0) + 1

    logger.info("overseer_trained", extra={"patterns": pattern_counts})
    return pattern_counts