"""
LUKHAS AI Methylation Model
DNA-like tag permanence and lifecycle management
Trinity Framework: ⚛️🧠🛡️

Implements a biological-inspired methylation system for controlling
the lifecycle and decay patterns of symbolic tags within LUKHAS AI.
"""
import logging
import math
from datetime import datetime
from typing import Any, Optional

from .tags import SymbolicTag, TagScope

logger = logging.getLogger(__name__)


class MethylationModel:
    """
    Bio-inspired methylation model controlling decay of symbolic tags.

    Similar to DNA methylation in biological systems, this model affects
    how tags persist, decay, and are inherited across system generations.
    """

    def __init__(
        self,
        genetic_decay_factor: float = 0.5,
        temporal_decay_rate: float = 0.1,
        ethical_preservation_bonus: float = 1.5,
    ) -> None:
        """
        Initialize the methylation model.

        Args:
            genetic_decay_factor: Decay factor for genetic tags (0.0-1.0)
            temporal_decay_rate: Base decay rate for temporal tags
            ethical_preservation_bonus: Bonus factor for ethical tags
        """
        self.genetic_decay_factor = max(0.0, min(1.0, genetic_decay_factor))
        self.temporal_decay_rate = max(0.0, temporal_decay_rate)
        self.ethical_preservation_bonus = max(1.0, ethical_preservation_bonus)

        # Methylation patterns for different scopes
        self.scope_patterns = {
            TagScope.GLOBAL: {"stability": 0.9, "inheritance": 0.7},
            TagScope.LOCAL: {"stability": 0.6, "inheritance": 0.3},
            TagScope.ETHICAL: {"stability": 0.95, "inheritance": 0.9},
            TagScope.TEMPORAL: {"stability": 0.3, "inheritance": 0.1},
            TagScope.GENETIC: {"stability": 0.8, "inheritance": 0.95},
        }

        logger.info(f"MethylationModel initialized with genetic_decay_factor={genetic_decay_factor}")

    def adjust_lifespan(
        self,
        scope: TagScope,
        lifespan: Optional[float],
        tag_metadata: Optional[dict[str, Any]] = None,
    ) -> Optional[float]:
        """
        Adjust tag lifespan based on methylation patterns.

        Args:
            scope: Tag scope
            lifespan: Original lifespan in seconds (None = permanent)
            tag_metadata: Additional tag metadata for adjustment

        Returns:
            Adjusted lifespan or None for permanent
        """
        if lifespan is None:
            # Check if scope forces finite lifespan
            if scope == TagScope.TEMPORAL:
                return 3600.0  # Default 1 hour for temporal tags
            return None

        # Get methylation pattern for scope
        pattern = self.scope_patterns.get(scope, {"stability": 0.5, "inheritance": 0.5})
        stability = pattern["stability"]

        # Base adjustment by scope
        adjusted_lifespan = lifespan

        if scope == TagScope.GENETIC:
            # Genetic tags affected by genetic decay factor
            adjusted_lifespan = lifespan * self.genetic_decay_factor
        elif scope == TagScope.ETHICAL:
            # Ethical tags get preservation bonus
            adjusted_lifespan = lifespan * self.ethical_preservation_bonus
        elif scope == TagScope.TEMPORAL:
            # Temporal tags decay faster
            adjusted_lifespan = lifespan * (1.0 - self.temporal_decay_rate)

        # Apply stability factor
        adjusted_lifespan *= stability

        # Consider tag importance from metadata
        if tag_metadata:
            importance = tag_metadata.get("importance", 0.5)  # 0.0-1.0 scale
            access_frequency = tag_metadata.get("access_frequency", 0.0)

            # High importance and frequent access extend lifespan
            importance_factor = 0.5 + (importance * 0.5)  # 0.5-1.0 range
            frequency_factor = 1.0 + (access_frequency * 0.3)  # 1.0-1.3 range

            adjusted_lifespan *= importance_factor * frequency_factor

        # Ensure minimum lifespan
        min_lifespan = self._get_minimum_lifespan(scope)
        adjusted_lifespan = max(adjusted_lifespan, min_lifespan)

        logger.debug(f"Adjusted lifespan for {scope.value}: {lifespan} -> {adjusted_lifespan}")
        return adjusted_lifespan

    def calculate_decay_rate(self, tag: SymbolicTag, current_time: datetime) -> float:
        """
        Calculate current decay rate for a tag.

        Args:
            tag: The symbolic tag
            current_time: Current timestamp

        Returns:
            Decay rate (0.0 = no decay, 1.0 = complete decay)
        """
        if tag.lifespan is None:
            return 0.0  # Permanent tags don't decay

        if tag.created_at is None:
            return 0.0  # Can't calculate without creation time

        # Calculate age
        age_seconds = (current_time - tag.created_at).total_seconds()

        if age_seconds <= 0:
            return 0.0

        # Get scope-specific decay pattern
        pattern = self.scope_patterns.get(tag.scope, {"stability": 0.5})
        stability = pattern["stability"]

        # Calculate base decay
        decay_progress = age_seconds / tag.lifespan

        # Apply non-linear decay based on scope
        if tag.scope == TagScope.TEMPORAL:
            # Exponential decay for temporal tags
            decay_rate = 1.0 - math.exp(-decay_progress * 2.0)
        elif tag.scope == TagScope.GENETIC:
            # Sigmoidal decay for genetic tags
            decay_rate = 1.0 / (1.0 + math.exp(-5.0 * (decay_progress - 0.7)))
        elif tag.scope == TagScope.ETHICAL:
            # Very slow decay for ethical tags
            decay_rate = decay_progress * 0.5
        else:
            # Linear decay for other scopes
            decay_rate = decay_progress

        # Apply stability factor
        decay_rate *= 1.0 - stability * 0.5

        # Consider access patterns
        if tag.access_count > 0:
            # Frequently accessed tags decay slower
            access_factor = 1.0 / (1.0 + math.log(tag.access_count))
            decay_rate *= access_factor

        return min(1.0, max(0.0, decay_rate))

    def should_preserve_tag(self, tag: SymbolicTag, decay_rate: float) -> bool:
        """
        Determine if a tag should be preserved despite decay.

        Args:
            tag: The symbolic tag
            decay_rate: Current decay rate

        Returns:
            True if tag should be preserved
        """
        # Ethical tags have strong preservation bias
        if tag.scope == TagScope.ETHICAL and decay_rate < 0.9:
            return True

        # High-access tags are preserved
        if tag.access_count > 10 and decay_rate < 0.8:
            return True

        # Important tags (from metadata) are preserved
        importance = tag.metadata.get("importance", 0.0)
        if importance > 0.8 and decay_rate < 0.7:
            return True

        # Genetic tags with inheritance patterns
        if tag.scope == TagScope.GENETIC:
            inheritance = self.scope_patterns[TagScope.GENETIC]["inheritance"]
            if decay_rate < (1.0 - inheritance):
                return True

        return False

    def inherit_tag(self, parent_tag: SymbolicTag, generation_id: str) -> Optional[SymbolicTag]:
        """
        Create an inherited tag from a parent tag.

        Args:
            parent_tag: The parent tag to inherit from
            generation_id: ID of the new generation

        Returns:
            Inherited tag or None if inheritance fails
        """
        pattern = self.scope_patterns.get(parent_tag.scope, {"inheritance": 0.0})
        inheritance_probability = pattern["inheritance"]

        # Check if inheritance occurs (simplified - would use random in real implementation)
        if inheritance_probability < 0.5:
            return None

        # Create inherited tag
        inherited_id = f"{parent_tag.tag_id}_gen_{generation_id}"

        # Inherit with some mutations/modifications
        inherited_metadata = parent_tag.metadata.copy()
        inherited_metadata["parent_id"] = parent_tag.tag_id
        inherited_metadata["generation"] = generation_id
        inherited_metadata["inherited"] = True

        # Modify lifespan for inheritance
        inherited_lifespan = parent_tag.lifespan
        if inherited_lifespan is not None:
            inherited_lifespan *= inheritance_probability

        inherited_tag = SymbolicTag(
            tag_id=inherited_id,
            content=parent_tag.content,  # Could be modified in more complex cases
            scope=parent_tag.scope,
            permission=parent_tag.permission,
            metadata=inherited_metadata,
            lifespan=inherited_lifespan,
        )

        logger.debug(f"Inherited tag {inherited_id} from {parent_tag.tag_id}")
        return inherited_tag

    def _get_minimum_lifespan(self, scope: TagScope) -> float:
        """Get minimum lifespan for a scope."""
        minimums = {
            TagScope.GLOBAL: 3600.0,  # 1 hour
            TagScope.LOCAL: 1800.0,  # 30 minutes
            TagScope.ETHICAL: 86400.0,  # 24 hours
            TagScope.TEMPORAL: 300.0,  # 5 minutes
            TagScope.GENETIC: 7200.0,  # 2 hours
        }
        return minimums.get(scope, 1800.0)  # Default 30 minutes

    def get_methylation_stats(self) -> dict[str, Any]:
        """Get statistics about the methylation model."""
        return {
            "genetic_decay_factor": self.genetic_decay_factor,
            "temporal_decay_rate": self.temporal_decay_rate,
            "ethical_preservation_bonus": self.ethical_preservation_bonus,
            "scope_patterns": {scope.value: pattern for scope, pattern in self.scope_patterns.items()},
        }


# Global methylation model instance
_methylation_model = None


def get_methylation_model() -> MethylationModel:
    """Get or create the global methylation model."""
    global _methylation_model
    if _methylation_model is None:
        _methylation_model = MethylationModel()
    return _methylation_model


# Export public interface
__all__ = ["MethylationModel", "get_methylation_model"]
