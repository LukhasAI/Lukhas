"""
LUKHAS AGI - Pattern Learning Engine
Advanced pattern recognition and learning system for consciousness development.
⚛️🧠🛡️ Trinity Framework: Identity-Consciousness-Guardian
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple


class PatternType(Enum):
    """Types of patterns that can be learned."""
    SEQUENTIAL = "sequential"
    SPATIAL = "spatial"
    TEMPORAL = "temporal"
    BEHAVIORAL = "behavioral"
    SYMBOLIC = "symbolic"
    CAUSAL = "causal"


@dataclass
class Pattern:
    """Represents a learned pattern."""

    pattern_id: str
    pattern_type: PatternType
    structure: dict[str, Any]
    confidence: float  # 0.0 to 1.0
    frequency: int = 0
    last_seen: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)


# Alias for backward compatibility
LearningPattern = Pattern

# Additional alias for PatternLearner (engine) - defined after class


@dataclass
class PatternLearningContext:
    """Context for pattern learning operations."""

    learning_mode: str = "adaptive"
    confidence_threshold: float = 0.7
    max_patterns: int = 1000
    learning_rate: float = 0.1
    decay_rate: float = 0.01
    metadata: Dict[str, Any] = field(default_factory=dict)


class PatternLearningEngine:
    """Advanced pattern learning engine for consciousness development."""

    def __init__(self, context: Optional[PatternLearningContext] = None):
        """Initialize the pattern learning engine."""
        self.context = context or PatternLearningContext()
        self.learned_patterns: Dict[str, Pattern] = {}
        self.pattern_relationships: Dict[str, Set[str]] = {}
        self.learning_history: List[Dict[str, Any]] = []

    async def learn_pattern(
        self,
        data: Any,
        pattern_type: PatternType,
        pattern_id: Optional[str] = None
    ) -> Pattern:
        """Learn a new pattern from data."""
        if pattern_id is None:
            pattern_id = f"{pattern_type.value}_{len(self.learned_patterns)}"

        # Extract pattern structure (simplified)
        structure = await self._extract_pattern_structure(data, pattern_type)

        pattern = Pattern(
            pattern_id=pattern_id,
            pattern_type=pattern_type,
            structure=structure,
            confidence=self._calculate_confidence(data, pattern_type)
        )

        self.learned_patterns[pattern_id] = pattern

        # Log learning event
        self.learning_history.append({
            "event": "pattern_learned",
            "pattern_id": pattern_id,
            "pattern_type": pattern_type.value,
            "confidence": pattern.confidence,
            "timestamp": datetime.now(timezone.utc)
        })

        return pattern

    async def recognize_pattern(
        self,
        data: Any,
        pattern_types: Optional[List[PatternType]] = None
    ) -> List[Tuple[Pattern, float]]:
        """Recognize patterns in new data."""
        if pattern_types is None:
            pattern_types = list(PatternType)

        recognized = []

        for pattern in self.learned_patterns.values():
            if pattern.pattern_type in pattern_types:
                similarity = await self._calculate_similarity(data, pattern)
                if similarity >= self.context.confidence_threshold:
                    recognized.append((pattern, similarity))

        # Sort by similarity (highest first)
        recognized.sort(key=lambda x: x[1], reverse=True)
        return recognized

    async def update_pattern(
        self,
        pattern_id: str,
        new_data: Any,
        learning_rate: Optional[float] = None
    ) -> Optional[Pattern]:
        """Update an existing pattern with new data."""
        if pattern_id not in self.learned_patterns:
            return None

        pattern = self.learned_patterns[pattern_id]
        rate = learning_rate or self.context.learning_rate

        # Update pattern structure (simplified)
        await self._update_pattern_structure(pattern, new_data, rate)

        pattern.frequency += 1
        pattern.last_seen = datetime.now(timezone.utc)

        return pattern

    async def _extract_pattern_structure(
        self,
        data: Any,
        pattern_type: PatternType
    ) -> Dict[str, Any]:
        """Extract pattern structure from data."""
        # Simplified pattern extraction
        if pattern_type == PatternType.SEQUENTIAL:
            return {"sequence": str(data), "length": len(str(data))}
        elif pattern_type == PatternType.TEMPORAL:
            return {"timestamp": datetime.now(timezone.utc).isoformat()}
        elif pattern_type == PatternType.BEHAVIORAL:
            return {"behavior": str(data)}
        else:
            return {"raw_data": str(data)}

    def _calculate_confidence(self, data: Any, pattern_type: PatternType) -> float:
        """Calculate confidence level for a pattern."""
        # Simplified confidence calculation
        base_confidence = 0.5

        if hasattr(data, "__len__"):
            # Longer sequences tend to be more reliable
            length_factor = min(len(data) / 100.0, 0.3)
            base_confidence += length_factor

        return min(base_confidence, 1.0)

    async def _calculate_similarity(self, data: Any, pattern: Pattern) -> float:
        """Calculate similarity between data and a learned pattern."""
        # Simplified similarity calculation
        data_str = str(data)
        pattern_str = str(pattern.structure)

        # Basic string similarity (simplified)
        if data_str == pattern_str:
            return 1.0
        elif data_str in pattern_str or pattern_str in data_str:
            return 0.8
        else:
            return 0.3

    async def _update_pattern_structure(
        self,
        pattern: Pattern,
        new_data: Any,
        learning_rate: float
    ) -> None:
        """Update pattern structure with new data."""
        # Simplified pattern update
        pattern.structure["last_update"] = datetime.now(timezone.utc).isoformat()
        pattern.structure["update_count"] = pattern.structure.get("update_count", 0) + 1


# Backward compatibility aliases
PatternLearner = PatternLearningEngine


# Convenience functions for quick pattern learning
async def quick_pattern_learning(
    data: Any,
    pattern_type: PatternType = PatternType.SEQUENTIAL
) -> Pattern:
    """Quick pattern learning for simple use cases."""
    engine = PatternLearningEngine()
    return await engine.learn_pattern(data, pattern_type)


def create_pattern_learning_context(
    learning_mode: str = "adaptive",
    confidence_threshold: float = 0.7,
    **kwargs
) -> PatternLearningContext:
    """Create a pattern learning context with common settings."""
    return PatternLearningContext(
        learning_mode=learning_mode,
        confidence_threshold=confidence_threshold,
        **kwargs
    )


# Export main classes and functions
__all__ = [
    "PatternLearningEngine",
    "PatternLearner",  # Alias for PatternLearningEngine
    "PatternType",
    "Pattern",
    "LearningPattern",  # Alias for Pattern
    "PatternLearningContext",
    "quick_pattern_learning",
    "create_pattern_learning_context"
]