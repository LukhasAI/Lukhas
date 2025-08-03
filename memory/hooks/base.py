"""Abstract base class for memory hooks

This module defines the interface for memory management hooks that can
process memory items during storage and retrieval operations.

ΛTAG: memory_hook_base
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List, Set
from dataclasses import dataclass, field
from datetime import datetime
from core.common import get_logger
import uuid

logger = get_logger(__name__)


from core.common import LukhasError, GuardianRejectionError, MemoryDriftError
class HookExecutionError(LukhasError):
    """Raised when hook execution fails"""
    pass


@dataclass
class MemoryItem:
    """Represents a memory item in the LUKHAS system

    This dataclass encapsulates all information about a memory,
    including content, metadata, and symbolic annotations.
    """
    content: Any
    metadata: Dict[str, Any] = field(default_factory=dict)
    fold_level: Optional[int] = None
    glyphs: Optional[List[str]] = None
    causal_lineage: Optional[List[str]] = None
    timestamp: datetime = field(default_factory=datetime.now)
    memory_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # Symbolic state
    entropy: float = 0.5
    coherence: float = 1.0
    resonance: float = 0.5

    # Memory type classification
    memory_type: str = "generic"  # generic, episodic, semantic, procedural

    # Compression and fold data
    is_compressed: bool = False
    compression_ratio: Optional[float] = None
    fold_signature: Optional[str] = None

    # Emotional context
    emotional_valence: Optional[float] = None  # -1.0 to 1.0
    emotional_intensity: Optional[float] = None  # 0.0 to 1.0
    emotional_tags: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Validate memory item structure"""
        if self.content is None:
            raise ValueError("Memory content cannot be None")

        # Validate numeric bounds
        if not 0.0 <= self.entropy <= 1.0:
            raise ValueError("Entropy must be between 0.0 and 1.0")
        if not 0.0 <= self.coherence <= 1.0:
            raise ValueError("Coherence must be between 0.0 and 1.0")
        if not 0.0 <= self.resonance <= 1.0:
            raise ValueError("Resonance must be between 0.0 and 1.0")

        if self.emotional_valence is not None:
            if not -1.0 <= self.emotional_valence <= 1.0:
                raise ValueError("Emotional valence must be between -1.0 and 1.0")

        if self.emotional_intensity is not None:
            if not 0.0 <= self.emotional_intensity <= 1.0:
                raise ValueError("Emotional intensity must be between 0.0 and 1.0")

    def add_to_lineage(self, ancestor_id: str) -> None:
        """Add ancestor to causal lineage"""
        if self.causal_lineage is None:
            self.causal_lineage = []
        if ancestor_id not in self.causal_lineage:
            self.causal_lineage.append(ancestor_id)

    def add_glyph(self, glyph: str) -> None:
        """Add symbolic glyph"""
        if self.glyphs is None:
            self.glyphs = []
        if glyph not in self.glyphs:
            self.glyphs.append(glyph)

    def calculate_symbolic_weight(self) -> float:
        """Calculate overall symbolic weight of memory"""
        # Weighted combination of symbolic metrics
        weight = (
            self.coherence * 0.4 +
            self.resonance * 0.3 +
            (1.0 - self.entropy) * 0.3
        )

        # Adjust for emotional intensity if present
        if self.emotional_intensity is not None:
            weight *= (1.0 + self.emotional_intensity * 0.2)

        return min(weight, 1.0)


class MemoryHook(ABC):
    """Abstract base class for memory management hooks

    Hooks can process memory items at two key points:
    1. Before storage - allowing transformation, validation, or enrichment
    2. After recall - allowing post-processing or context injection
    """

    def __init__(self):
        self._enabled = True
        self._metrics = {
            'before_store_count': 0,
            'after_recall_count': 0,
            'errors_count': 0,
            'total_processing_time': 0.0
        }

    @abstractmethod
    def before_store(self, item: MemoryItem) -> MemoryItem:
        """Process memory item before storage

        This method is called before a memory item is stored. Hooks can:
        - Validate the memory content
        - Add metadata or annotations
        - Transform the content
        - Reject storage by raising HookExecutionError

        Args:
            item: The memory item to process

        Returns:
            Processed memory item

        Raises:
            HookExecutionError: If the memory should not be stored
        """
        pass

    @abstractmethod
    def after_recall(self, item: MemoryItem) -> MemoryItem:
        """Process memory item after retrieval

        This method is called after a memory item is retrieved. Hooks can:
        - Enrich with current context
        - Transform based on retrieval context
        - Filter or modify content

        Args:
            item: The retrieved memory item

        Returns:
            Processed memory item

        Raises:
            HookExecutionError: If the memory cannot be processed
        """
        pass

    @abstractmethod
    def get_hook_name(self) -> str:
        """Return hook identifier

        Returns:
            Unique hook name
        """
        pass

    @abstractmethod
    def get_hook_version(self) -> str:
        """Return hook version

        Returns:
            Hook version string
        """
        pass

    def validate_fold_integrity(self, item: MemoryItem) -> bool:
        """Ensure memory fold integrity

        This method checks that memory fold operations maintain
        reversibility and causal lineage.

        Args:
            item: Memory item to validate

        Returns:
            True if fold integrity is maintained
        """
        # Default implementation - can be overridden
        if not item.is_compressed:
            return True

        # Check compression ratio is reasonable
        if item.compression_ratio is not None:
            if item.compression_ratio <= 0 or item.compression_ratio > 100:
                logger.warning(f"Suspicious compression ratio: {item.compression_ratio}")
                return False

        # Check fold signature exists for compressed items
        if item.fold_signature is None:
            logger.warning("Compressed item missing fold signature")
            return False

        # Verify causal lineage preserved
        if item.causal_lineage is None or len(item.causal_lineage) == 0:
            logger.warning("Compressed item missing causal lineage")
            return False

        return True

    def validate_symbolic_consistency(self, item: MemoryItem) -> bool:
        """Validate symbolic state consistency

        Args:
            item: Memory item to validate

        Returns:
            True if symbolic state is consistent
        """
        # Check glyph consistency
        if item.glyphs:
            # Ensure no contradictory glyphs
            contradiction_pairs = [
                ('🌱', '💀'),  # Growth vs Death
                ('🛡️', '🔥'),  # Protection vs Destruction
                ('✓', '❌'),   # Success vs Failure
            ]

            for glyph1, glyph2 in contradiction_pairs:
                if glyph1 in item.glyphs and glyph2 in item.glyphs:
                    logger.warning(f"Contradictory glyphs found: {glyph1} and {glyph2}")
                    return False

        # Check symbolic metric consistency
        # High entropy should correlate with low coherence
        if item.entropy > 0.8 and item.coherence > 0.8:
            logger.warning("Inconsistent symbolic metrics: high entropy with high coherence")
            return False

        return True

    def enable(self) -> None:
        """Enable the hook"""
        self._enabled = True
        logger.info(f"Enabled hook: {self.get_hook_name()}")

    def disable(self) -> None:
        """Disable the hook"""
        self._enabled = False
        logger.info(f"Disabled hook: {self.get_hook_name()}")

    def is_enabled(self) -> bool:
        """Check if hook is enabled"""
        return self._enabled

    def get_metrics(self) -> Dict[str, Any]:
        """Get hook performance metrics"""
        total_calls = (
            self._metrics['before_store_count'] +
            self._metrics['after_recall_count']
        )

        if total_calls > 0:
            avg_time = self._metrics['total_processing_time'] / total_calls
            error_rate = self._metrics['errors_count'] / total_calls
        else:
            avg_time = 0.0
            error_rate = 0.0

        return {
            'hook_name': self.get_hook_name(),
            'hook_version': self.get_hook_version(),
            'enabled': self._enabled,
            'before_store_count': self._metrics['before_store_count'],
            'after_recall_count': self._metrics['after_recall_count'],
            'errors_count': self._metrics['errors_count'],
            'average_processing_time_ms': avg_time * 1000,
            'error_rate': error_rate
        }

    def _update_metrics(self, operation: str, processing_time: float, error: bool = False) -> None:
        """Update internal metrics

        Args:
            operation: 'before_store' or 'after_recall'
            processing_time: Time taken in seconds
            error: Whether an error occurred
        """
        if operation == 'before_store':
            self._metrics['before_store_count'] += 1
        elif operation == 'after_recall':
            self._metrics['after_recall_count'] += 1

        self._metrics['total_processing_time'] += processing_time

        if error:
            self._metrics['errors_count'] += 1