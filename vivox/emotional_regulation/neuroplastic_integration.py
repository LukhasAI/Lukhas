import logging
import streamlit as st
import time
logger = logging.getLogger(__name__)
"""
VIVOX.ERN Neuroplastic & Tag System Integration
Connects emotional regulation to neuroplastic learning and tag propagation
"""

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from lukhas.core.common import get_logger

# Import tag system
try:
    from lukhas.core.tags import get_tag_registry
    from lukhas.core.tags.registry import TagCategory, TagDefinition, TagRegistry

    TAG_SYSTEM_AVAILABLE = True
except ImportError:
    TAG_SYSTEM_AVAILABLE = False

    # Fallback classes
    class TagRegistry:
        pass

    class TagDefinition:
        pass

    class TagCategory:
        pass


# Import neuroplastic connector
try:
    from emotion.neuroplastic_connector import EmotionConnector, connector

    NEUROPLASTIC_AVAILABLE = True
except ImportError:
    NEUROPLASTIC_AVAILABLE = False

    # Mock connector
    class EmotionConnector:
        def connect_component(self, name, component):
            pass

        def emit_hormone(self, hormone, intensity):
            pass

        def get_stress_response(self):
            return {}

    connector = EmotionConnector()

from .vivox_ern_core import RegulationResponse, RegulationStrategy, VADVector

logger = get_logger(__name__)


@dataclass
class EmotionalPattern:
    """Represents a learned emotional pattern"""

    pattern_id: str
    triggers: list[str]
    emotional_signature: dict[str, float]  # VAD + intensity
    effective_strategies: list[str]
    success_rate: float
    usage_count: int = 0
    last_used: Optional[datetime] = None
    context_factors: dict[str, Any] = field(default_factory=dict)
    neuroplastic_tags: list[str] = field(default_factory=list)
    colony_propagatable: bool = False

    def matches_context(self, context: dict[str, Any], similarity_threshold: float = 0.7) -> float:
        """Calculate how well this pattern matches current context"""
        if not self.context_factors:
            return 0.5  # Default similarity for patterns without context

        matches = 0
        total_factors = 0

        for factor, expected_value in self.context_factors.items():
            if factor in context:
                total_factors += 1
                actual_value = context[factor]

                # Calculate similarity based on value type
                if isinstance(expected_value, (int, float)) and isinstance(actual_value, (int, float)):
                    # Numeric similarity
                    max_val = max(abs(expected_value), abs(actual_value), 1.0)
                    similarity = 1.0 - abs(expected_value - actual_value) / max_val
                    matches += similarity
                elif str(expected_value).lower() == str(actual_value).lower():
                    # Exact string match
                    matches += 1.0
                else:
                    # Partial string similarity
                    expected_str = str(expected_value).lower()
                    actual_str = str(actual_value).lower()
                    if expected_str in actual_str or actual_str in expected_str:
                        matches += 0.5

        return matches / max(total_factors, 1)

    def update_effectiveness(self, new_effectiveness: float):
        """Update pattern effectiveness with new data"""
        # Exponential moving average
        alpha = 0.3
        self.success_rate = alpha * new_effectiveness + (1 - alpha) * self.success_rate
        self.usage_count += 1
        self.last_used = datetime.now(timezone.utc)


@dataclass
class ColonyLearningPattern:
    """Pattern suitable for colony propagation across sessions"""

    pattern_hash: str
    emotional_context: dict[str, float]
    regulation_strategy: str
    effectiveness_scores: list[float]
    usage_contexts: list[str]
    propagation_strength: float
    created_by: str  # Source of pattern
    verified_by: list[str] = field(default_factory=list)  # Users who verified effectiveness

    def should_propagate(self) -> bool:
        """Determine if pattern should propagate to other users"""
        # Criteria for propagation:
        # 1. High average effectiveness
        # 2. Multiple successful uses
        # 3. Verified by multiple users

        if len(self.effectiveness_scores) < 3:
            return False

        avg_effectiveness = sum(self.effectiveness_scores) / len(self.effectiveness_scores)
        if avg_effectiveness < 0.7:
            return False

        return not len(self.verified_by) < 2


class VIVOXNeuroplasticLearner:
    """
    Neuroplastic learning system for VIVOX emotional regulation
    """

    def __init__(self):
        self.learned_patterns: dict[str, EmotionalPattern] = {}
        self.colony_patterns: dict[str, ColonyLearningPattern] = {}
        self.tag_registry: Optional[TagRegistry] = None
        self.neuroplastic_connector: EmotionConnector = connector

        # Learning parameters
        self.min_pattern_confidence = 0.6
        self.max_patterns = 500
        self.colony_propagation_threshold = 0.8

        # Pattern matching weights
        self.context_weight = 0.4
        self.emotional_weight = 0.3
        self.temporal_weight = 0.2
        self.usage_weight = 0.1

        # Initialize tag registry if available
        if TAG_SYSTEM_AVAILABLE:
            self._initialize_tag_registry()

        # Connect to neuroplastic system
        if NEUROPLASTIC_AVAILABLE:
            self._connect_to_neuroplastic_system()

    def _initialize_tag_registry(self):
        """Initialize connection to tag registry"""
        try:
            self.tag_registry = get_tag_registry()
            self._create_vivox_emotional_tags()
            logger.info("Connected to tag registry system")
        except Exception as e:
            logger.error(f"Failed to initialize tag registry: {e}")

    def _connect_to_neuroplastic_system(self):
        """Connect to neuroplastic connector"""
        try:
            self.neuroplastic_connector.connect_component("vivox_ern", self)
            logger.info("Connected to neuroplastic system")
        except Exception as e:
            logger.error(f"Failed to connect to neuroplastic system: {e}")

    def _create_vivox_emotional_tags(self):
        """Create VIVOX-specific emotional tags in registry"""
        if not self.tag_registry:
            return

        vivox_tags = [
            {
                "name": "vivox_regulation_success",
                "category": TagCategory.EMOTION,
                "description": "Successful VIVOX emotional regulation",
                "human_meaning": "The AI successfully helped regulate your emotions",
                "triggers": ["high_effectiveness", "positive_outcome"],
                "effects": ["increased_confidence", "pattern_reinforcement"],
                "priority": 2,
            },
            {
                "name": "vivox_stress_pattern",
                "category": TagCategory.NEUROPLASTIC,
                "description": "Detected stress response pattern",
                "human_meaning": "Recurring stress pattern identified for optimization",
                "triggers": ["high_arousal", "negative_valence", "stress_context"],
                "effects": ["stress_regulation", "breathing_suggestion"],
                "priority": 1,
            },
            {
                "name": "vivox_colony_learning",
                "category": TagCategory.COLONY,
                "description": "Pattern learned from colony propagation",
                "human_meaning": "Emotional regulation technique learned from similar users",
                "triggers": ["pattern_effectiveness", "multi_user_verification"],
                "effects": ["pattern_adoption", "effectiveness_boost"],
                "priority": 3,
            },
            {
                "name": "vivox_neuroplastic_adaptation",
                "category": TagCategory.NEUROPLASTIC,
                "description": "Neuroplastic adaptation in emotional processing",
                "human_meaning": "The AI adapted its approach based on your preferences",
                "triggers": ["pattern_change", "effectiveness_improvement"],
                "effects": ["personalization", "improved_outcomes"],
                "priority": 2,
            },
            {
                "name": "vivox_emotional_memory",
                "category": TagCategory.MEMORY,
                "description": "Emotional experience stored for learning",
                "human_meaning": "Your emotional experience was remembered for better future support",
                "triggers": ["significant_emotion", "successful_regulation"],
                "effects": ["memory_formation", "pattern_learning"],
                "priority": 4,
            },
        ]

        for tag_def in vivox_tags:
            try:
                tag = TagDefinition(**tag_def)
                self.tag_registry.register_tag(tag)
            except Exception as e:
                logger.error(f"Failed to register tag {tag_def['name']}: {e}")

    async def learn_from_regulation(
        self,
        regulation_response: RegulationResponse,
        context: dict[str, Any],
        user_feedback: Optional[float] = None,
    ) -> list[str]:
        """
        Learn from regulation experience and update patterns

        Returns list of neuroplastic tags generated
        """
        try:
            # Extract pattern features
            pattern_features = self._extract_pattern_features(regulation_response, context)

            # Find or create matching pattern
            pattern = await self._find_or_create_pattern(pattern_features, regulation_response, context)

            # Update pattern with new experience
            effectiveness = user_feedback if user_feedback is not None else regulation_response.effectiveness
            pattern.update_effectiveness(effectiveness)

            # Generate neuroplastic tags
            tags = await self._generate_neuroplastic_tags(pattern, regulation_response, effectiveness)

            # Update tag registry
            if self.tag_registry and tags:
                await self._update_tag_registry_with_learning(tags, pattern, context)

            # Check for colony propagation
            if effectiveness > self.colony_propagation_threshold:
                await self._consider_colony_propagation(pattern, regulation_response, context)

            # Emit hormonal signals for neuroplastic changes
            await self._emit_neuroplastic_hormones(pattern, effectiveness)

            # Prune old patterns if needed
            await self._prune_patterns()

            logger.debug(f"Learned from regulation: {len(tags)} tags generated")
            return tags

        except Exception as e:
            logger.error(f"Error in neuroplastic learning: {e}")
            return []

    def _extract_pattern_features(
        self, regulation_response: RegulationResponse, context: dict[str, Any]
    ) -> dict[str, Any]:
        """Extract key features for pattern matching"""
        return {
            "emotional_state": {
                "valence": regulation_response.original_state.valence,
                "arousal": regulation_response.original_state.arousal,
                "dominance": regulation_response.original_state.dominance,
                "intensity": regulation_response.original_state.intensity,
            },
            "strategy_used": regulation_response.strategy_used.value,
            "context_hash": hashlib.md5(json.dumps(context, sort_keys=True).encode()).hexdigest()[:8],
            "time_of_day": context.get("time_of_day", "unknown"),
            "environment": context.get("environment", "unknown"),
            "stress_level": context.get("stress_level", 0.5),
        }

    async def _find_or_create_pattern(
        self,
        features: dict[str, Any],
        regulation_response: RegulationResponse,
        context: dict[str, Any],
    ) -> EmotionalPattern:
        """Find existing pattern or create new one"""

        # Look for similar existing patterns
        best_match = None
        best_similarity = 0.0

        for pattern in self.learned_patterns.values():
            similarity = await self._calculate_pattern_similarity(pattern, features, context)
            if similarity > best_similarity and similarity > self.min_pattern_confidence:
                best_similarity = similarity
                best_match = pattern

        if best_match:
            return best_match

        # Create new pattern
        pattern_id = f"pattern_{len(self.learned_patterns)}_{int(datetime.now(timezone.utc).timestamp())}"

        triggers = self._extract_triggers(regulation_response, context)

        new_pattern = EmotionalPattern(
            pattern_id=pattern_id,
            triggers=triggers,
            emotional_signature=features["emotional_state"],
            effective_strategies=[features["strategy_used"]],
            success_rate=regulation_response.effectiveness,
            context_factors={
                "environment": context.get("environment"),
                "time_of_day": context.get("time_of_day"),
                "stress_level": context.get("stress_level", 0.5),
            },
            neuroplastic_tags=regulation_response.neuroplastic_tags.copy(),
        )

        self.learned_patterns[pattern_id] = new_pattern
        return new_pattern

    async def _calculate_pattern_similarity(
        self,
        pattern: EmotionalPattern,
        features: dict[str, Any],
        context: dict[str, Any],
    ) -> float:
        """Calculate similarity between pattern and current features"""

        # Emotional state similarity
        emotional_similarity = self._calculate_emotional_similarity(
            pattern.emotional_signature, features["emotional_state"]
        )

        # Context similarity
        context_similarity = pattern.matches_context(context)

        # Strategy compatibility (only if strategy_used is provided)
        strategy_compatibility = 1.0  # Default to neutral compatibility
        if "strategy_used" in features:
            strategy_compatibility = 1.0 if features["strategy_used"] in pattern.effective_strategies else 0.3

        # Temporal decay (recent patterns are more relevant)
        temporal_decay = 1.0
        if pattern.last_used:
            days_since_use = (datetime.now(timezone.utc) - pattern.last_used).days
            temporal_decay = max(0.1, 1.0 - (days_since_use * 0.1))

        # Usage frequency bonus
        usage_bonus = min(1.0, pattern.usage_count / 10.0)

        # Weighted combination
        similarity = (
            emotional_similarity * self.emotional_weight
            + context_similarity * self.context_weight
            + strategy_compatibility * 0.2
            + temporal_decay * self.temporal_weight
            + usage_bonus * self.usage_weight
        )

        return similarity

    def _calculate_emotional_similarity(self, signature1: dict[str, float], signature2: dict[str, float]) -> float:
        """Calculate similarity between emotional signatures"""
        total_difference = 0.0
        dimensions = ["valence", "arousal", "dominance", "intensity"]

        for dim in dimensions:
            val1 = signature1.get(dim, 0.0)
            val2 = signature2.get(dim, 0.0)
            total_difference += abs(val1 - val2)

        # Convert difference to similarity (lower difference = higher similarity)
        max_possible_difference = len(dimensions) * 2.0  # Each dimension can differ by at most 2
        similarity = 1.0 - (total_difference / max_possible_difference)

        return max(0.0, similarity)

    def _extract_triggers(self, regulation_response: RegulationResponse, context: dict[str, Any]) -> list[str]:
        """Extract triggers from regulation context"""
        triggers = []

        original_state = regulation_response.original_state

        # Emotional triggers
        if original_state.arousal > 0.7:
            triggers.append("high_arousal")
        elif original_state.arousal < -0.5:
            triggers.append("low_arousal")

        if original_state.valence < -0.5:
            triggers.append("negative_valence")
        elif original_state.valence > 0.7:
            triggers.append("positive_valence")

        if original_state.intensity > 0.8:
            triggers.append("high_intensity")

        # Context triggers
        if context.get("stress_level", 0) > 0.7:
            triggers.append("high_stress")

        environment = context.get("environment")
        if environment:
            triggers.append(f"env_{environment}")

        time_of_day = context.get("time_of_day")
        if time_of_day:
            triggers.append(f"time_{time_of_day}")

        return triggers

    async def _generate_neuroplastic_tags(
        self,
        pattern: EmotionalPattern,
        regulation_response: RegulationResponse,
        effectiveness: float,
    ) -> list[str]:
        """Generate neuroplastic tags for this learning event"""
        tags = []

        # Success/failure tags
        if effectiveness > 0.8:
            tags.append("vivox_regulation_success")
            tags.append("high_effectiveness_learning")
        elif effectiveness < 0.3:
            tags.append("regulation_ineffective")
            tags.append("strategy_review_needed")

        # Pattern-specific tags
        if pattern.usage_count == 1:
            tags.append("new_pattern_learned")
        elif pattern.usage_count > 10:
            tags.append("well_established_pattern")

        # Strategy-specific tags
        strategy = regulation_response.strategy_used
        tags.append(f"strategy_{strategy.value}_learned")

        if strategy == RegulationStrategy.BREATHING:
            tags.append("breathing_technique_effective")
        elif strategy == RegulationStrategy.COGNITIVE:
            tags.append("cognitive_reframing_effective")

        # Emotional context tags
        if regulation_response.original_state.arousal > 0.7:
            tags.append("vivox_stress_pattern")
            tags.append("high_arousal_regulation")

        # Neuroplastic adaptation tags
        if pattern.success_rate > 0.7:
            tags.append("vivox_neuroplastic_adaptation")
            tags.append("pattern_reinforcement")

        return tags

    async def _update_tag_registry_with_learning(
        self, tags: list[str], pattern: EmotionalPattern, context: dict[str, Any]
    ):
        """Update tag registry with learning results"""
        if not self.tag_registry:
            return

        try:
            # Trigger relevant tags
            for tag_name in tags:
                if hasattr(self.tag_registry, "trigger_tag"):
                    await self.tag_registry.trigger_tag(
                        tag_name,
                        context={
                            "pattern_id": pattern.pattern_id,
                            "effectiveness": pattern.success_rate,
                            "usage_count": pattern.usage_count,
                            **context,
                        },
                    )
        except Exception as e:
            logger.error(f"Error updating tag registry: {e}")

    async def _consider_colony_propagation(
        self,
        pattern: EmotionalPattern,
        regulation_response: RegulationResponse,
        context: dict[str, Any],
    ):
        """Consider if pattern should be propagated to colony"""
        if not pattern.colony_propagatable and pattern.success_rate > self.colony_propagation_threshold:
            # Create colony learning pattern
            pattern_hash = hashlib.md5(
                json.dumps(
                    {
                        "triggers": pattern.triggers,
                        "strategy": regulation_response.strategy_used.value,
                        "emotional_context": pattern.emotional_signature,
                    },
                    sort_keys=True,
                ).encode()
            ).hexdigest()[:16]

            if pattern_hash not in self.colony_patterns:
                colony_pattern = ColonyLearningPattern(
                    pattern_hash=pattern_hash,
                    emotional_context=pattern.emotional_signature,
                    regulation_strategy=regulation_response.strategy_used.value,
                    effectiveness_scores=[pattern.success_rate],
                    usage_contexts=[context.get("environment", "unknown")],
                    propagation_strength=pattern.success_rate,
                    created_by=context.get("user_id", "unknown"),
                )

                self.colony_patterns[pattern_hash] = colony_pattern
                pattern.colony_propagatable = True

                logger.info(f"Created colony pattern: {pattern_hash}")

    async def _emit_neuroplastic_hormones(self, pattern: EmotionalPattern, effectiveness: float):
        """Emit hormonal signals for neuroplastic changes"""
        if not NEUROPLASTIC_AVAILABLE:
            return

        try:
            # Success hormones
            if effectiveness > 0.7:
                self.neuroplastic_connector.emit_hormone("dopamine", effectiveness * 0.5)
                self.neuroplastic_connector.emit_hormone("serotonin", effectiveness * 0.3)

            # Learning hormones
            if pattern.usage_count <= 3:  # New learning
                self.neuroplastic_connector.emit_hormone("acetylcholine", 0.4)  # Learning neurotransmitter

            # Stress reduction if pattern is stress-related
            if "stress" in str(pattern.triggers).lower():
                self.neuroplastic_connector.emit_hormone("gaba", 0.3)

        except Exception as e:
            logger.error(f"Error emitting neuroplastic hormones: {e}")

    async def _prune_patterns(self):
        """Remove old or ineffective patterns"""
        if len(self.learned_patterns) <= self.max_patterns:
            return

        # Sort patterns by relevance (combination of success rate, usage, and recency)
        patterns_with_scores = []

        for pattern in self.learned_patterns.values():
            # Calculate relevance score
            success_score = pattern.success_rate
            usage_score = min(1.0, pattern.usage_count / 10.0)

            recency_score = 1.0
            if pattern.last_used:
                days_old = (datetime.now(timezone.utc) - pattern.last_used).days
                recency_score = max(0.1, 1.0 - (days_old * 0.05))

            relevance_score = success_score * 0.5 + usage_score * 0.3 + recency_score * 0.2
            patterns_with_scores.append((pattern, relevance_score))

        # Sort by relevance (lowest first for removal)
        patterns_with_scores.sort(key=lambda x: x[1])

        # Remove least relevant patterns
        patterns_to_remove = len(self.learned_patterns) - self.max_patterns + 50  # Remove extra for buffer

        for i in range(patterns_to_remove):
            if i < len(patterns_with_scores):
                pattern_to_remove = patterns_with_scores[i][0]
                del self.learned_patterns[pattern_to_remove.pattern_id]

        logger.info(f"Pruned {patterns_to_remove} old patterns")

    async def get_recommended_strategy(
        self, current_state: VADVector, context: dict[str, Any]
    ) -> Optional[tuple[RegulationStrategy, float]]:
        """Get recommended strategy based on learned patterns"""

        features = {
            "emotional_state": {
                "valence": current_state.valence,
                "arousal": current_state.arousal,
                "dominance": current_state.dominance,
                "intensity": current_state.intensity,
            }
        }

        # Find best matching pattern
        best_pattern = None
        best_similarity = 0.0

        for pattern in self.learned_patterns.values():
            similarity = await self._calculate_pattern_similarity(pattern, features, context)
            if similarity > best_similarity and similarity > self.min_pattern_confidence:
                best_similarity = similarity
                best_pattern = pattern

        if best_pattern and best_pattern.effective_strategies:
            # Return most effective strategy from pattern
            strategy_name = best_pattern.effective_strategies[0]  # First is usually most effective
            try:
                strategy = RegulationStrategy(strategy_name)
                confidence = best_similarity * best_pattern.success_rate
                return strategy, confidence
            except ValueError:
                pass

        return None

    def get_learning_statistics(self) -> dict[str, Any]:
        """Get neuroplastic learning statistics"""
        if not self.learned_patterns:
            return {
                "total_patterns": 0,
                "average_effectiveness": 0.0,
                "colony_patterns": 0,
                "most_effective_strategies": [],
                "propagatable_patterns": 0,
                "patterns_by_usage": {
                    "high_usage": 0,
                    "medium_usage": 0,
                    "low_usage": 0,
                },
            }

        # Calculate statistics
        total_patterns = len(self.learned_patterns)
        avg_effectiveness = sum(p.success_rate for p in self.learned_patterns.values()) / total_patterns

        # Strategy effectiveness
        strategy_stats = {}
        for pattern in self.learned_patterns.values():
            for strategy in pattern.effective_strategies:
                if strategy not in strategy_stats:
                    strategy_stats[strategy] = {"count": 0, "total_effectiveness": 0.0}
                strategy_stats[strategy]["count"] += 1
                strategy_stats[strategy]["total_effectiveness"] += pattern.success_rate

        # Calculate average effectiveness per strategy
        for strategy in strategy_stats:
            count = strategy_stats[strategy]["count"]
            strategy_stats[strategy]["average_effectiveness"] = strategy_stats[strategy]["total_effectiveness"] / count

        # Sort strategies by effectiveness
        sorted_strategies = sorted(
            strategy_stats.items(),
            key=lambda x: x[1]["average_effectiveness"],
            reverse=True,
        )

        return {
            "total_patterns": total_patterns,
            "average_effectiveness": avg_effectiveness,
            "colony_patterns": len(self.colony_patterns),
            "propagatable_patterns": sum(1 for p in self.learned_patterns.values() if p.colony_propagatable),
            "most_effective_strategies": sorted_strategies[:5],
            "patterns_by_usage": {
                "high_usage": sum(1 for p in self.learned_patterns.values() if p.usage_count >= 10),
                "medium_usage": sum(1 for p in self.learned_patterns.values() if 3 <= p.usage_count < 10),
                "low_usage": sum(1 for p in self.learned_patterns.values() if p.usage_count < 3),
            },
        }


class VIVOXTagSystemIntegration:
    """
    Integration with LUKHAS tag system for VIVOX emotional processing
    """

    def __init__(self, neuroplastic_learner: VIVOXNeuroplasticLearner):
        self.neuroplastic_learner = neuroplastic_learner
        self.tag_registry = neuroplastic_learner.tag_registry
        self.active_tags: set[str] = set()
        self.tag_history: list[dict[str, Any]] = []

    async def process_emotional_tags(
        self,
        regulation_response: RegulationResponse,
        context: dict[str, Any],
        user_id: str,
    ) -> list[str]:
        """Process and activate emotional tags"""
        generated_tags = []

        try:
            # Learn from regulation and get neuroplastic tags
            neuroplastic_tags = await self.neuroplastic_learner.learn_from_regulation(regulation_response, context)
            generated_tags.extend(neuroplastic_tags)

            # Activate tags in registry
            for tag in generated_tags:
                await self._activate_tag(tag, context, user_id)

            # Check for tag combinations and emergent patterns
            emergent_tags = await self._check_emergent_patterns(generated_tags, context)
            generated_tags.extend(emergent_tags)

            # Update tag history
            self._update_tag_history(generated_tags, regulation_response, context, user_id)

        except Exception as e:
            logger.error(f"Error processing emotional tags: {e}")

        return generated_tags

    async def _activate_tag(self, tag_name: str, context: dict[str, Any], user_id: str):
        """Activate a tag in the registry"""
        if not self.tag_registry or not TAG_SYSTEM_AVAILABLE:
            return

        try:
            self.active_tags.add(tag_name)

            # Create tag activation context
            activation_context = {
                "user_id": user_id,
                "source": "vivox_ern",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "context": context,
            }

            # Activate tag if registry supports it
            if hasattr(self.tag_registry, "activate_tag"):
                await self.tag_registry.activate_tag(tag_name, activation_context)

        except Exception as e:
            logger.error(f"Error activating tag {tag_name}: {e}")

    async def _check_emergent_patterns(self, current_tags: list[str], context: dict[str, Any]) -> list[str]:
        """Check for emergent patterns from tag combinations"""
        emergent_tags = []

        # Pattern: Stress + Success -> Resilience Building
        if "vivox_stress_pattern" in current_tags and "vivox_regulation_success" in current_tags:
            emergent_tags.append("resilience_building")
            emergent_tags.append("stress_mastery_developing")

        # Pattern: Multiple learning tags -> Advanced User
        learning_tags = [tag for tag in current_tags if "learning" in tag or "adaptation" in tag]
        if len(learning_tags) >= 2:
            emergent_tags.append("advanced_emotional_learner")

        # Pattern: Colony learning + Success -> Pattern Leader
        if "vivox_colony_learning" in current_tags and "vivox_regulation_success" in current_tags:
            emergent_tags.append("emotional_pattern_leader")

        return emergent_tags

    def _update_tag_history(
        self,
        tags: list[str],
        regulation_response: RegulationResponse,
        context: dict[str, Any],
        user_id: str,
    ):
        """Update tag activation history"""
        history_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_id": user_id,
            "tags_activated": tags,
            "regulation_strategy": regulation_response.strategy_used.value,
            "effectiveness": regulation_response.effectiveness,
            "emotional_state": regulation_response.regulated_state.to_dict(),
            "context": context,
        }

        self.tag_history.append(history_entry)

        # Limit history size
        if len(self.tag_history) > 1000:
            self.tag_history = self.tag_history[-800:]

    def get_tag_analytics(self, user_id: str, hours: int = 24) -> dict[str, Any]:
        """Get tag analytics for user"""
        cutoff_time = datetime.now(timezone.utc).timestamp() - (hours * 3600)

        relevant_history = [
            entry
            for entry in self.tag_history
            if entry["user_id"] == user_id and datetime.fromisoformat(entry["timestamp"]).timestamp() > cutoff_time
        ]

        if not relevant_history:
            return {"message": "No tag data available"}

        # Analyze tag patterns
        tag_counts = {}
        tag_effectiveness = {}

        for entry in relevant_history:
            effectiveness = entry["effectiveness"]

            for tag in entry["tags_activated"]:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

                if tag not in tag_effectiveness:
                    tag_effectiveness[tag] = []
                tag_effectiveness[tag].append(effectiveness)

        # Calculate average effectiveness per tag
        tag_avg_effectiveness = {tag: sum(scores) / len(scores) for tag, scores in tag_effectiveness.items()}

        # Find most effective tags
        most_effective_tags = sorted(tag_avg_effectiveness.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "total_tag_activations": sum(tag_counts.values()),
            "unique_tags_activated": len(tag_counts),
            "most_frequent_tags": sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:5],
            "most_effective_tags": most_effective_tags,
            "tag_activation_trend": len(relevant_history),
            "learning_indicators": {
                "neuroplastic_adaptations": tag_counts.get("vivox_neuroplastic_adaptation", 0),
                "successful_regulations": tag_counts.get("vivox_regulation_success", 0),
                "stress_patterns_identified": tag_counts.get("vivox_stress_pattern", 0),
                "colony_learning_events": tag_counts.get("vivox_colony_learning", 0),
            },
        }