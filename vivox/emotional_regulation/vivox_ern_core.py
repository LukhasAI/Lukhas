"""
VIVOX.ERN - Emotional Regulation Network
The emotional homeostasis guardian

Maintains emotional equilibrium through adaptive regulation strategies
Integrates with neuroplastic systems, event bus, and endocrine signals
"""
import math
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

import numpy as np


class EmotionalState(Enum):
    """Core emotional states for regulation"""

    NEUTRAL = "neutral"
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    ANTICIPATION = "anticipation"
    TRUST = "trust"
    CONTEMPT = "contempt"


class RegulationStrategy(Enum):
    """Emotional regulation strategies"""

    DAMPENING = "dampening"  # Reduce intensity
    AMPLIFICATION = "amplification"  # Increase intensity
    STABILIZATION = "stabilization"  # Maintain balance
    REDIRECTION = "redirection"  # Shift emotional focus
    BREATHING = "breathing"  # Breathing-based regulation
    COGNITIVE = "cognitive"  # Cognitive reframing
    DISTRACTION = "distraction"  # Attention shifting
    ACCEPTANCE = "acceptance"  # Mindful acceptance


@dataclass
class VADVector:
    """Valence-Arousal-Dominance emotional representation"""

    valence: float = 0.0  # Pleasant(+1) to Unpleasant(-1)
    arousal: float = 0.0  # High(+1) to Low(-1) activation
    dominance: float = 0.0  # Controlled(+1) to Submissive(-1)
    intensity: float = 0.5  # Overall emotional intensity
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def magnitude(self) -> float:
        """Calculate vector magnitude"""
        return math.sqrt(self.valence**2 + self.arousal**2 + self.dominance**2)

    def distance_to(self, other: "VADVector") -> float:
        """Calculate distance to another VAD vector"""
        return math.sqrt(
            (self.valence - other.valence) ** 2
            + (self.arousal - other.arousal) ** 2
            + (self.dominance - other.dominance) ** 2
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "valence": self.valence,
            "arousal": self.arousal,
            "dominance": self.dominance,
            "intensity": self.intensity,
            "timestamp": self.timestamp.isoformat(),
            "magnitude": self.magnitude(),
        }

    @classmethod
    def from_emotions(cls, emotion_scores: dict[str, float]) -> "VADVector":
        """Create VAD from emotion scores"""
        # Mapping emotions to VAD space
        emotion_mappings = {
            EmotionalState.JOY: (0.8, 0.6, 0.4),
            EmotionalState.SADNESS: (-0.6, -0.4, -0.3),
            EmotionalState.ANGER: (-0.4, 0.8, 0.6),
            EmotionalState.FEAR: (-0.7, 0.4, -0.6),
            EmotionalState.SURPRISE: (0.2, 0.8, 0.0),
            EmotionalState.DISGUST: (-0.8, 0.3, 0.2),
            EmotionalState.ANTICIPATION: (0.4, 0.5, 0.3),
            EmotionalState.TRUST: (0.6, -0.2, 0.4),
            EmotionalState.CONTEMPT: (-0.5, 0.2, 0.7),
            EmotionalState.NEUTRAL: (0.0, 0.0, 0.0),
        }

        # Weighted average based on emotion scores
        valence = arousal = dominance = 0.0
        total_weight = 0.0

        for emotion_name, score in emotion_scores.items():
            try:
                emotion = EmotionalState(emotion_name.lower())
                if emotion in emotion_mappings:
                    v, a, d = emotion_mappings[emotion]
                    valence += v * score
                    arousal += a * score
                    dominance += d * score
                    total_weight += score
            except ValueError:
                continue

        if total_weight > 0:
            valence /= total_weight
            arousal /= total_weight
            dominance /= total_weight

        intensity = min(1.0, total_weight)

        return cls(valence=valence, arousal=arousal, dominance=dominance, intensity=intensity)


@dataclass
class EmotionalMemory:
    """Memory of emotional experiences for learning"""

    vad_state: VADVector
    context: dict[str, Any]
    regulation_applied: Optional[RegulationStrategy]
    effectiveness: float  # How well regulation worked (0-1)
    user_feedback: Optional[str] = None
    tags: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class RegulationResponse:
    """Response from emotional regulation attempt"""

    original_state: VADVector
    regulated_state: VADVector
    strategy_used: RegulationStrategy
    effectiveness: float
    reasoning: str
    hormone_triggers: dict[str, float] = field(default_factory=dict)
    neuroplastic_tags: list[str] = field(default_factory=list)
    duration_seconds: float = 0.0


class EmotionalRegulator:
    """Core emotional regulation engine"""

    def __init__(self):
        self.regulation_thresholds = {
            "high_arousal": 0.8,
            "low_arousal": -0.6,
            "negative_valence": -0.7,
            "high_intensity": 0.9,
        }

        # Regulation strategy effectiveness weights
        self.strategy_weights = {
            RegulationStrategy.DAMPENING: {
                "high_arousal": 0.8,
                "high_intensity": 0.9,
                "negative_valence": 0.6,
            },
            RegulationStrategy.BREATHING: {
                "high_arousal": 0.9,
                "fear": 0.8,
                "anger": 0.7,
            },
            RegulationStrategy.COGNITIVE: {
                "negative_valence": 0.8,
                "sadness": 0.7,
                "fear": 0.6,
            },
            RegulationStrategy.STABILIZATION: {"volatility": 0.9, "transitions": 0.8},
        }

        # Learning memory
        self.emotional_memories: list[EmotionalMemory] = []

    async def regulate_emotion(
        self,
        current_state: VADVector,
        context: dict[str, Any],
        user_preferences: Optional[dict[str, Any]] = None,
    ) -> RegulationResponse:
        """
        Main emotional regulation function

        Args:
            current_state: Current VAD emotional state
            context: Situational context
            user_preferences: User's regulation preferences

        Returns:
            RegulationResponse with regulated state and metadata
        """
        start_time = time.time()

        # Analyze if regulation is needed
        regulation_needed, triggers = await self._assess_regulation_needs(current_state, context)

        if not regulation_needed:
            return RegulationResponse(
                original_state=current_state,
                regulated_state=current_state,
                strategy_used=RegulationStrategy.STABILIZATION,
                effectiveness=1.0,
                reasoning="No regulation needed - emotional state within optimal range",
                duration_seconds=time.time() - start_time,
            )

        # Select optimal regulation strategy
        strategy = await self._select_regulation_strategy(current_state, triggers, context, user_preferences)

        # Apply regulation
        regulated_state = await self._apply_regulation(current_state, strategy, context)

        # Calculate effectiveness
        effectiveness = await self._calculate_effectiveness(current_state, regulated_state, strategy)

        # Generate reasoning
        reasoning = await self._generate_regulation_reasoning(current_state, regulated_state, strategy, triggers)

        # Generate hormone triggers
        hormone_triggers = await self._generate_hormone_triggers(regulated_state, strategy)

        # Generate neuroplastic tags
        neuroplastic_tags = await self._generate_neuroplastic_tags(current_state, regulated_state, strategy, context)

        # Store in emotional memory for learning
        memory = EmotionalMemory(
            vad_state=current_state,
            context=context,
            regulation_applied=strategy,
            effectiveness=effectiveness,
            tags=neuroplastic_tags,
        )
        self.emotional_memories.append(memory)

        # Limit memory size
        if len(self.emotional_memories) > 1000:
            self.emotional_memories = self.emotional_memories[-800:]  # Keep recent 800

        return RegulationResponse(
            original_state=current_state,
            regulated_state=regulated_state,
            strategy_used=strategy,
            effectiveness=effectiveness,
            reasoning=reasoning,
            hormone_triggers=hormone_triggers,
            neuroplastic_tags=neuroplastic_tags,
            duration_seconds=time.time() - start_time,
        )

    async def _assess_regulation_needs(self, state: VADVector, context: dict[str, Any]) -> tuple[bool, list[str]]:
        """Assess if emotional regulation is needed"""
        triggers = []

        # High arousal check
        if abs(state.arousal) > self.regulation_thresholds["high_arousal"]:
            triggers.append("high_arousal")

        # Low arousal check (depression/apathy)
        if state.arousal < self.regulation_thresholds["low_arousal"]:
            triggers.append("low_arousal")

        # Negative valence check
        if state.valence < self.regulation_thresholds["negative_valence"]:
            triggers.append("negative_valence")

        # High intensity check
        if state.intensity > self.regulation_thresholds["high_intensity"]:
            triggers.append("high_intensity")

        # Context-based triggers
        stress_level = context.get("stress_level", 0.0)
        if stress_level > 0.7:
            triggers.append("high_stress")

        # Check for emotional volatility
        if len(self.emotional_memories) > 2:
            recent_states = [mem.vad_state for mem in self.emotional_memories[-3:]]
            volatility = self._calculate_volatility(recent_states)
            if volatility > 0.6:
                triggers.append("high_volatility")

        return len(triggers) > 0, triggers

    async def _select_regulation_strategy(
        self,
        state: VADVector,
        triggers: list[str],
        context: dict[str, Any],
        user_preferences: Optional[dict[str, Any]],
    ) -> RegulationStrategy:
        """Select optimal regulation strategy"""
        strategy_scores = {}

        # Score each strategy based on triggers and context
        for strategy in RegulationStrategy:
            score = 0.0

            # Base effectiveness for triggers
            if strategy in self.strategy_weights:
                for trigger in triggers:
                    if trigger in self.strategy_weights[strategy]:
                        score += self.strategy_weights[strategy][trigger]

            # User preference bonus
            if user_preferences and strategy.value in user_preferences.get("preferred_strategies", []):
                score += 0.3

            # Context-based adjustments
            if context.get("environment") == "work" and strategy == RegulationStrategy.BREATHING:
                score += 0.2  # Breathing good for work stress

            # Historical effectiveness (learning)
            historical_effectiveness = self._get_historical_effectiveness(strategy, triggers)
            score += historical_effectiveness * 0.4

            strategy_scores[strategy] = score

        # Select best strategy
        best_strategy = max(strategy_scores.items(), key=lambda x: x[1])[0]

        # Fallback to breathing if no clear winner
        if strategy_scores[best_strategy] < 0.3:
            best_strategy = RegulationStrategy.BREATHING

        return best_strategy

    async def _apply_regulation(
        self,
        current_state: VADVector,
        strategy: RegulationStrategy,
        context: dict[str, Any],
    ) -> VADVector:
        """Apply the selected regulation strategy"""

        if strategy == RegulationStrategy.DAMPENING:
            return await self._apply_dampening(current_state)
        elif strategy == RegulationStrategy.AMPLIFICATION:
            return await self._apply_amplification(current_state)
        elif strategy == RegulationStrategy.BREATHING:
            return await self._apply_breathing_regulation(current_state)
        elif strategy == RegulationStrategy.COGNITIVE:
            return await self._apply_cognitive_reframing(current_state, context)
        elif strategy == RegulationStrategy.STABILIZATION:
            return await self._apply_stabilization(current_state)
        elif strategy == RegulationStrategy.REDIRECTION:
            return await self._apply_redirection(current_state, context)
        elif strategy == RegulationStrategy.DISTRACTION:
            return await self._apply_distraction(current_state)
        elif strategy == RegulationStrategy.ACCEPTANCE:
            return await self._apply_acceptance(current_state)
        else:
            return current_state

    async def _apply_dampening(self, state: VADVector) -> VADVector:
        """Apply dampening regulation to reduce emotional intensity"""
        dampening_factor = 0.7

        return VADVector(
            valence=state.valence * dampening_factor,
            arousal=state.arousal * dampening_factor,
            dominance=state.dominance * dampening_factor,
            intensity=state.intensity * 0.6,
        )

    async def _apply_amplification(self, state: VADVector) -> VADVector:
        """Apply amplification for low-energy states"""
        if state.valence > 0:  # Only amplify positive emotions
            return VADVector(
                valence=min(1.0, state.valence * 1.3),
                arousal=min(1.0, state.arousal * 1.2),
                dominance=min(1.0, state.dominance * 1.1),
                intensity=min(1.0, state.intensity * 1.4),
            )
        return state

    async def _apply_breathing_regulation(self, state: VADVector) -> VADVector:
        """Apply breathing-based regulation"""
        # Breathing tends to reduce arousal and increase dominance
        return VADVector(
            valence=state.valence + 0.1,  # Slight positive shift
            arousal=state.arousal * 0.6,  # Significant arousal reduction
            dominance=min(1.0, state.dominance + 0.3),  # Increase sense of control
            intensity=state.intensity * 0.8,
        )

    async def _apply_cognitive_reframing(self, state: VADVector, context: dict[str, Any]) -> VADVector:
        """Apply cognitive reframing regulation"""
        # Cognitive reframing primarily affects valence and dominance
        valence_improvement = 0.3 if state.valence < 0 else 0.1

        return VADVector(
            valence=min(1.0, state.valence + valence_improvement),
            arousal=state.arousal * 0.9,  # Slight arousal reduction
            dominance=min(1.0, state.dominance + 0.4),  # Increase sense of control
            intensity=state.intensity,
        )

    async def _apply_stabilization(self, state: VADVector) -> VADVector:
        """Apply stabilization to bring state toward neutral"""
        stabilization_factor = 0.3
        target = VADVector(valence=0.1, arousal=0.0, dominance=0.2, intensity=0.5)

        return VADVector(
            valence=state.valence + (target.valence - state.valence) * stabilization_factor,
            arousal=state.arousal + (target.arousal - state.arousal) * stabilization_factor,
            dominance=state.dominance + (target.dominance - state.dominance) * stabilization_factor,
            intensity=state.intensity + (target.intensity - state.intensity) * stabilization_factor,
        )

    async def _apply_redirection(self, state: VADVector, context: dict[str, Any]) -> VADVector:
        """Apply emotional redirection"""
        # Redirect negative emotions toward more constructive channels
        if state.valence < 0:
            return VADVector(
                valence=state.valence + 0.4,
                arousal=min(1.0, abs(state.arousal)),  # Channel arousal constructively
                dominance=min(1.0, state.dominance + 0.3),
                intensity=state.intensity * 0.9,
            )
        return state

    async def _apply_distraction(self, state: VADVector) -> VADVector:
        """Apply distraction-based regulation"""
        # Distraction reduces intensity across all dimensions
        return VADVector(
            valence=state.valence * 0.5,
            arousal=state.arousal * 0.4,
            dominance=state.dominance,
            intensity=state.intensity * 0.3,
        )

    async def _apply_acceptance(self, state: VADVector) -> VADVector:
        """Apply mindful acceptance regulation"""
        # Acceptance doesn't change emotions but increases dominance (sense of control)
        return VADVector(
            valence=state.valence,
            arousal=state.arousal * 0.8,  # Slight reduction in arousal
            dominance=min(1.0, state.dominance + 0.5),  # Significant increase in control
            intensity=state.intensity,
        )

    async def _calculate_effectiveness(
        self, original: VADVector, regulated: VADVector, strategy: RegulationStrategy
    ) -> float:
        """Calculate regulation effectiveness"""
        # Distance moved toward optimal emotional range
        optimal = VADVector(valence=0.3, arousal=0.1, dominance=0.4, intensity=0.6)

        original_distance = original.distance_to(optimal)
        regulated_distance = regulated.distance_to(optimal)

        if original_distance == 0:
            return 1.0

        improvement = (original_distance - regulated_distance) / original_distance
        return max(0.0, min(1.0, improvement))

    async def _generate_regulation_reasoning(
        self,
        original: VADVector,
        regulated: VADVector,
        strategy: RegulationStrategy,
        triggers: list[str],
    ) -> str:
        """Generate human-readable reasoning for regulation"""
        reasoning_parts = []

        # Describe the triggers
        if triggers:
            trigger_descriptions = {
                "high_arousal": "elevated emotional intensity",
                "negative_valence": "negative emotional tone",
                "high_intensity": "overwhelming emotional strength",
                "high_stress": "elevated stress levels",
                "high_volatility": "emotional instability",
            }

            trigger_text = ", ".join([trigger_descriptions.get(t, t) for t in triggers])
            reasoning_parts.append(f"Detected {trigger_text}")

        # Describe the strategy
        strategy_descriptions = {
            RegulationStrategy.DAMPENING: "reduced emotional intensity",
            RegulationStrategy.BREATHING: "applied breathing-based calming techniques",
            RegulationStrategy.COGNITIVE: "used cognitive reframing to shift perspective",
            RegulationStrategy.STABILIZATION: "worked to stabilize emotional state",
            RegulationStrategy.ACCEPTANCE: "applied mindful acceptance techniques",
        }

        strategy_text = strategy_descriptions.get(strategy, f"applied {strategy.value} regulation")
        reasoning_parts.append(f"Applied regulation: {strategy_text}")

        # Describe the outcome
        valence_change = regulated.valence - original.valence
        arousal_change = regulated.arousal - original.arousal
        intensity_change = regulated.intensity - original.intensity

        outcome_parts = []
        if abs(valence_change) > 0.1:
            if valence_change > 0:
                outcome_parts.append("improved emotional tone")
            else:
                outcome_parts.append("moderated emotional tone")

        if abs(arousal_change) > 0.1:
            if arousal_change > 0:
                outcome_parts.append("increased activation")
            else:
                outcome_parts.append("reduced activation")

        if abs(intensity_change) > 0.1:
            if intensity_change > 0:
                outcome_parts.append("heightened emotional intensity")
            else:
                outcome_parts.append("moderated emotional intensity")

        if outcome_parts:
            reasoning_parts.append(f"Result: {', '.join(outcome_parts)}")

        return ". ".join(reasoning_parts) + "."

    async def _generate_hormone_triggers(
        self, regulated_state: VADVector, strategy: RegulationStrategy
    ) -> dict[str, float]:
        """Generate hormone release triggers for endocrine system"""
        hormones = {}

        # Strategy-based hormone releases
        if strategy == RegulationStrategy.BREATHING:
            hormones["serotonin"] = 0.3  # Calming effect
            hormones["gaba"] = 0.4  # Inhibitory neurotransmitter

        elif strategy == RegulationStrategy.COGNITIVE:
            hormones["dopamine"] = 0.2  # Reward for cognitive effort
            hormones["serotonin"] = 0.2  # Mood stabilization

        elif strategy == RegulationStrategy.DAMPENING:
            hormones["gaba"] = 0.5  # Strong inhibitory effect
            hormones["cortisol"] = -0.3  # Reduce stress hormone

        # State-based hormone adjustments
        if regulated_state.valence > 0.5:
            hormones["dopamine"] = hormones.get("dopamine", 0) + 0.3
            hormones["serotonin"] = hormones.get("serotonin", 0) + 0.2

        if regulated_state.arousal < -0.3:  # Low arousal
            hormones["melatonin"] = 0.2  # Promote rest

        return hormones

    async def _generate_neuroplastic_tags(
        self,
        original: VADVector,
        regulated: VADVector,
        strategy: RegulationStrategy,
        context: dict[str, Any],
    ) -> list[str]:
        """Generate neuroplastic tags for learning and adaptation"""
        tags = []

        # Strategy effectiveness tags
        effectiveness = await self._calculate_effectiveness(original, regulated, strategy)
        if effectiveness > 0.7:
            tags.append(f"regulation_success_{strategy.value}")
        elif effectiveness < 0.3:
            tags.append(f"regulation_ineffective_{strategy.value}")

        # Context-based tags
        if context.get("environment"):
            tags.append(f"context_{context['environment']}")

        if context.get("time_of_day"):
            tags.append(f"time_{context['time_of_day']}")

        # Emotional pattern tags
        if original.arousal > 0.7:
            tags.append("high_arousal_regulation")

        if original.valence < -0.5:
            tags.append("negative_emotion_regulation")

        # Colony propagation tags (for sharing successful patterns)
        if effectiveness > 0.8:
            tags.append("colony_propagate_success")
            tags.append(f"colony_strategy_{strategy.value}")

        return tags

    def _calculate_volatility(self, states: list[VADVector]) -> float:
        """Calculate emotional volatility from recent states"""
        if len(states) < 2:
            return 0.0

        distances = []
        for i in range(1, len(states)):
            distance = states[i].distance_to(states[i - 1])
            distances.append(distance)

        return np.mean(distances) if distances else 0.0

    def _get_historical_effectiveness(self, strategy: RegulationStrategy, triggers: list[str]) -> float:
        """Get historical effectiveness of strategy for given triggers"""
        relevant_memories = [mem for mem in self.emotional_memories if mem.regulation_applied == strategy]

        if not relevant_memories:
            return 0.5  # Neutral score for unknown strategies

        # Filter by trigger similarity
        trigger_relevant = []
        for mem in relevant_memories:
            if any(trigger in str(mem.tags) for trigger in triggers):
                trigger_relevant.append(mem)

        memories_to_use = trigger_relevant if trigger_relevant else relevant_memories

        if memories_to_use:
            return np.mean([mem.effectiveness for mem in memories_to_use])

        return 0.5

    async def get_emotional_insights(self, user_id: str) -> dict[str, Any]:
        """Get insights about emotional patterns for user transparency"""
        if not self.emotional_memories:
            return {
                "message": "No emotional data available yet",
                "patterns": [],
                "recommendations": [],
            }

        recent_memories = self.emotional_memories[-50:]  # Last 50 emotional events

        insights = {
            "total_regulations": len(recent_memories),
            "average_effectiveness": np.mean([mem.effectiveness for mem in recent_memories]),
            "most_effective_strategies": self._get_top_strategies(recent_memories),
            "emotional_patterns": self._analyze_emotional_patterns(recent_memories),
            "recommendations": self._generate_recommendations(recent_memories),
        }

        return insights

    def _get_top_strategies(self, memories: list[EmotionalMemory]) -> list[dict[str, Any]]:
        """Get most effective regulation strategies"""
        strategy_effectiveness = {}
        strategy_counts = {}

        for mem in memories:
            if mem.regulation_applied:
                strategy = mem.regulation_applied
                if strategy not in strategy_effectiveness:
                    strategy_effectiveness[strategy] = []
                    strategy_counts[strategy] = 0

                strategy_effectiveness[strategy].append(mem.effectiveness)
                strategy_counts[strategy] += 1

        top_strategies = []
        for strategy, effectiveness_scores in strategy_effectiveness.items():
            if len(effectiveness_scores) >= 3:  # Minimum sample size
                avg_effectiveness = np.mean(effectiveness_scores)
                top_strategies.append(
                    {
                        "strategy": strategy.value,
                        "effectiveness": avg_effectiveness,
                        "usage_count": strategy_counts[strategy],
                    }
                )

        return sorted(top_strategies, key=lambda x: x["effectiveness"], reverse=True)[:3]

    def _analyze_emotional_patterns(self, memories: list[EmotionalMemory]) -> list[dict[str, Any]]:
        """Analyze emotional patterns for insights"""
        patterns = []

        # Analyze valence trends
        valences = [mem.vad_state.valence for mem in memories]
        if valences:
            avg_valence = np.mean(valences)
            valence_trend = "positive" if avg_valence > 0.1 else "negative" if avg_valence < -0.1 else "neutral"
            patterns.append(
                {
                    "type": "valence_trend",
                    "description": f"Overall emotional tone tends to be {valence_trend}",
                    "value": avg_valence,
                }
            )

        # Analyze arousal patterns
        arousals = [mem.vad_state.arousal for mem in memories]
        if arousals:
            avg_arousal = np.mean(arousals)
            arousal_level = "high" if avg_arousal > 0.3 else "low" if avg_arousal < -0.3 else "moderate"
            patterns.append(
                {
                    "type": "arousal_pattern",
                    "description": f"Emotional activation level is typically {arousal_level}",
                    "value": avg_arousal,
                }
            )

        return patterns

    def _generate_recommendations(self, memories: list[EmotionalMemory]) -> list[str]:
        """Generate personalized recommendations"""
        recommendations = []

        # Analyze recent effectiveness
        recent_effectiveness = [mem.effectiveness for mem in memories[-10:]]
        if recent_effectiveness and np.mean(recent_effectiveness) < 0.5:
            recommendations.append(
                "Consider trying different regulation strategies - recent approaches haven't been very effective"
            )

        # Check for stress patterns
        high_arousal_count = sum(1 for mem in memories if mem.vad_state.arousal > 0.6)
        if high_arousal_count > len(memories) * 0.7:
            recommendations.append("High arousal detected frequently - breathing exercises and mindfulness may help")

        # Check for negative emotion patterns
        negative_count = sum(1 for mem in memories if mem.vad_state.valence < -0.4)
        if negative_count > len(memories) * 0.6:
            recommendations.append(
                "Frequent negative emotions detected - cognitive reframing techniques might be beneficial"
            )

        return recommendations


class VIVOXEmotionalRegulationNetwork:
    """
    Main VIVOX.ERN class integrating all emotional regulation components
    """

    def __init__(self, vivox_me: Optional["VIVOXMemoryExpansion"] = None):  # noqa: F821  # TODO: VIVOXMemoryExpansion
        self.vivox_me = vivox_me
        self.regulator = EmotionalRegulator()
        self.current_state = VADVector()  # Neutral starting state
        self.regulation_active = False
        self.integration_interfaces = {
            "event_bus": None,
            "tag_registry": None,
            "endocrine_system": None,
            "neuroplastic_connector": None,
        }

        # Performance metrics
        self.total_regulations = 0
        self.successful_regulations = 0
        self.user_satisfaction_scores = []

    async def process_emotional_input(
        self,
        emotion_data: dict[str, Any],
        context: Optional[dict[str, Any]] = None,
        user_preferences: Optional[dict[str, Any]] = None,
    ) -> RegulationResponse:
        """
        Main entry point for emotional processing

        Args:
            emotion_data: Raw emotional data (text, speech, biometrics, etc.)
            context: Current context information
            user_preferences: User's emotional regulation preferences

        Returns:
            RegulationResponse with regulated emotional state
        """
        if context is None:
            context = {}

        # Convert emotion data to VAD vector
        current_state = await self._convert_to_vad(emotion_data)
        self.current_state = current_state

        # Apply regulation if needed
        self.regulation_active = True
        try:
            regulation_response = await self.regulator.regulate_emotion(current_state, context, user_preferences)

            # Update performance metrics
            self.total_regulations += 1
            if regulation_response.effectiveness > 0.6:
                self.successful_regulations += 1

            # Update current state
            self.current_state = regulation_response.regulated_state

            # Trigger integrations
            await self._trigger_integrations(regulation_response, context)

            return regulation_response

        finally:
            self.regulation_active = False

    async def _convert_to_vad(self, emotion_data: dict[str, Any]) -> VADVector:
        """Convert various emotion input formats to VAD vector"""
        if "vad" in emotion_data:
            # Direct VAD input
            vad_data = emotion_data["vad"]
            return VADVector(
                valence=vad_data.get("valence", 0.0),
                arousal=vad_data.get("arousal", 0.0),
                dominance=vad_data.get("dominance", 0.0),
                intensity=vad_data.get("intensity", 0.5),
            )

        elif "emotions" in emotion_data:
            # Emotion scores input
            return VADVector.from_emotions(emotion_data["emotions"])

        elif "text" in emotion_data:
            # Text-based emotion analysis (simplified)
            return await self._analyze_text_emotion(emotion_data["text"])

        else:
            # Default neutral state
            return VADVector()

    async def _analyze_text_emotion(self, text: str) -> VADVector:
        """Analyze emotion from text (simplified implementation)"""
        # This would normally use NLP models, but for now simple keyword analysis
        text_lower = text.lower()

        # Simple keyword-based emotion detection
        emotion_keywords = {
            "joy": ["happy", "joy", "excited", "wonderful", "great", "amazing"],
            "sadness": ["sad", "depressed", "down", "unhappy", "terrible", "awful"],
            "anger": ["angry", "mad", "furious", "annoyed", "frustrated"],
            "fear": ["scared", "afraid", "worried", "anxious", "nervous"],
            "surprise": ["surprised", "shocked", "amazed", "unexpected"],
            "disgust": ["disgusted", "sick", "revolted", "gross"],
        }

        emotion_scores = {}
        for emotion, keywords in emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                emotion_scores[emotion] = min(1.0, score * 0.3)

        if not emotion_scores:
            emotion_scores = {"neutral": 1.0}

        return VADVector.from_emotions(emotion_scores)

    async def _trigger_integrations(self, response: RegulationResponse, context: dict[str, Any]):
        """Trigger integration events and updates"""

        # Event bus integration
        if self.integration_interfaces["event_bus"]:
            await self._publish_emotional_event(response, context)

        # Tag registry integration
        if self.integration_interfaces["tag_registry"] and response.neuroplastic_tags:
            await self._update_tag_registry(response.neuroplastic_tags, context)

        # Endocrine system integration
        if self.integration_interfaces["endocrine_system"] and response.hormone_triggers:
            await self._trigger_hormone_release(response.hormone_triggers)

        # Neuroplastic connector integration
        if self.integration_interfaces["neuroplastic_connector"]:
            await self._update_neuroplastic_patterns(response, context)

    async def _publish_emotional_event(self, response: RegulationResponse, context: dict[str, Any]):
        """Publish emotional state change to event bus"""
        event_bus = self.integration_interfaces["event_bus"]
        if event_bus:
            user_id = context.get("user_id", "unknown")

            # Publish regulation applied event
            await event_bus.publish_regulation_applied(user_id, response)

            # Publish emotional shift if significant
            shift_magnitude = response.original_state.distance_to(response.regulated_state)
            if shift_magnitude > 0.1:
                await event_bus.publish_emotional_shift(
                    user_id=user_id,
                    previous_state=response.original_state,
                    new_state=response.regulated_state,
                    triggers=context.get("triggers", []),
                    context=context,
                )

    async def _update_tag_registry(self, tags: list[str], context: dict[str, Any]):
        """Update tag registry with neuroplastic tags"""
        tag_integration = self.integration_interfaces.get("tag_integration")
        if tag_integration and tags:
            user_id = context.get("user_id", "unknown")
            # Process tags through neuroplastic learning system
            await tag_integration.process_emotional_tags(tags, context, user_id)

    async def _trigger_hormone_release(self, hormone_triggers: dict[str, float]):
        """Trigger hormone releases in endocrine system"""
        endocrine_integration = self.integration_interfaces.get("endocrine_system")
        if endocrine_integration:
            # Process hormone triggers through endocrine integration
            # Need to create a mock regulation response for the hormone processing
            mock_response = RegulationResponse(
                original_state=VADVector(),
                regulated_state=VADVector(),
                strategy_used=RegulationStrategy.BREATHING,
                effectiveness=0.7,
                reasoning="Mock response for hormone processing",
                hormone_triggers=hormone_triggers,
                neuroplastic_tags=[],
            )
            await endocrine_integration.process_emotional_hormones(mock_response, {"hormone_only": True})

    async def _update_neuroplastic_patterns(self, response: RegulationResponse, context: dict[str, Any]):
        """Update neuroplastic learning patterns"""
        neuroplastic_connector = self.integration_interfaces.get("neuroplastic_connector")
        if neuroplastic_connector:
            # Update neuroplastic patterns with regulation results
            await neuroplastic_connector.learn_from_regulation(response, context)

    def set_integration_interface(self, interface_name: str, interface_object: Any):
        """Set integration interface for external systems"""
        if interface_name in self.integration_interfaces:
            self.integration_interfaces[interface_name] = interface_object

    async def get_current_emotional_state(self) -> dict[str, Any]:
        """Get current emotional state for monitoring"""
        return {
            "current_state": self.current_state.to_dict(),
            "regulation_active": self.regulation_active,
            "performance": {
                "total_regulations": self.total_regulations,
                "success_rate": self.successful_regulations / max(1, self.total_regulations),
                "average_satisfaction": (
                    np.mean(self.user_satisfaction_scores) if self.user_satisfaction_scores else 0.0
                ),
            },
        }

    async def get_user_insights(self, user_id: str) -> dict[str, Any]:
        """Get emotional insights for user transparency"""
        return await self.regulator.get_emotional_insights(user_id)

    async def record_user_feedback(self, regulation_id: str, satisfaction_score: float, feedback: str = ""):
        """Record user feedback for learning"""
        self.user_satisfaction_scores.append(satisfaction_score)

        # Update most recent regulation effectiveness based on user feedback
        if self.regulator.emotional_memories:
            self.regulator.emotional_memories[-1].effectiveness = satisfaction_score
            self.regulator.emotional_memories[-1].user_feedback = feedback
