"""
Meta-learning capabilities for LUKHAS Cognitive AI.

This module provides meta-learning functionality that enables the system
to learn how to learn more effectively across different domains and tasks.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger(__name__)


class MetaLearningStrategy(Enum):
    """Meta-learning strategy types."""

    MODEL_AGNOSTIC = "model_agnostic"
    GRADIENT_BASED = "gradient_based"
    OPTIMIZATION_BASED = "optimization_based"
    MEMORY_AUGMENTED = "memory_augmented"
    FEW_SHOT = "few_shot"


# Alias for backward compatibility
LearningStrategy = MetaLearningStrategy


@dataclass
class MetaLearningContext:
    """Context for meta-learning operations."""

    domain: str
    task_type: str
    strategy: MetaLearningStrategy
    support_examples: list[dict[str, Any]] = field(default_factory=list)
    query_examples: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class MetaLearningResult:
    """Result of meta-learning operation."""

    context_id: str
    performance_metrics: dict[str, float]
    learned_parameters: dict[str, Any]
    adaptation_time: float
    success: bool
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class MetaLearner:
    """Core meta-learning engine for LUKHAS."""

    def __init__(self, strategy: MetaLearningStrategy = MetaLearningStrategy.MODEL_AGNOSTIC):
        self.strategy = strategy
        logger.info(f"MetaLearner initialized with strategy: {strategy.value}")


# Backward compatibility aliases
MetaLearningInsight = MetaLearningResult

# Export main classes and functions
__all__ = [
    "LearningStrategy",
    "MetaLearner",
    "MetaLearningContext",
    "MetaLearningInsight",
    "MetaLearningResult",
    "MetaLearningStrategy",
]
