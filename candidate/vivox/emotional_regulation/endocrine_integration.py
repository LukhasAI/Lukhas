"""
VIVOX.ERN Endocrine System Integration
Connects emotional regulation to biological hormone simulation
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional

from candidate.core.common import get_logger

# Import endocrine system
try:
    from candidate.core.endocrine.hormone_system import (
        HormoneSystem,
        HormoneType,
    )

    ENDOCRINE_AVAILABLE = True
except ImportError:
    ENDOCRINE_AVAILABLE = False

    # Fallback classes
    class HormoneSystem:
        def __init__(self):
            pass

        async def release_hormone(self, hormone_type, amount, duration=None):
            pass

        def get_hormone_levels(self):
            return {}

    class HormoneType:
        CORTISOL = "cortisol"
        DOPAMINE = "dopamine"
        SEROTONIN = "serotonin"
        OXYTOCIN = "oxytocin"
        ADRENALINE = "adrenaline"
        MELATONIN = "melatonin"
        GABA = "gaba"
        ENDORPHIN = "endorphin"


from .vivox_ern_core import RegulationResponse, RegulationStrategy, VADVector

logger = get_logger(__name__)


@dataclass
class EmotionalHormoneMapping:
    """Maps emotional states to hormone responses"""

    emotion_pattern: str
    primary_hormones: dict[str, float]  # hormone -> base release amount
    modulating_hormones: dict[str, float]  # secondary hormones
    duration_minutes: float = 30.0
    decay_rate: float = 0.1

    def calculate_release_amount(
        self, emotional_intensity: float, regulation_effectiveness: float
    ) -> dict[str, float]:
        """Calculate actual hormone release amounts"""
        release_amounts = {}

        # Scale primary hormones by emotional intensity
        for hormone, base_amount in self.primary_hormones.items():
            scaled_amount = base_amount * emotional_intensity

            # Adjust based on regulation effectiveness
            if regulation_effectiveness > 0.7:
                # Successful regulation can reduce stress hormones, boost positive ones
                if hormone in ["cortisol", "adrenaline"]:
                    scaled_amount *= 0.7  # Reduce stress hormones
                elif hormone in ["dopamine", "serotonin", "endorphin"]:
                    scaled_amount *= 1.3  # Boost positive hormones

            release_amounts[hormone] = min(1.0, max(0.0, scaled_amount))

        # Add modulating hormones
        for hormone, amount in self.modulating_hormones.items():
            modulated_amount = amount * emotional_intensity * 0.5
            release_amounts[hormone] = min(1.0, max(0.0, modulated_amount))

        return release_amounts


class VIVOXEndocrineIntegration:
    """
    Integration between VIVOX emotional regulation and endocrine system
    """

    def __init__(self, hormone_system: Optional[HormoneSystem] = None):
        self.hormone_system = hormone_system or HormoneSystem()
        self.emotional_hormone_mappings = self._initialize_hormone_mappings()
        self.regulation_hormone_mappings = self._initialize_regulation_mappings()

        # Hormone release history for learning
        self.hormone_release_history: list[dict[str, Any]] = []

        # Baseline hormone levels for comparison
        self.baseline_levels = {
            HormoneType.CORTISOL: 0.3,
            HormoneType.DOPAMINE: 0.4,
            HormoneType.SEROTONIN: 0.5,
            HormoneType.OXYTOCIN: 0.3,
            HormoneType.ADRENALINE: 0.2,
            HormoneType.MELATONIN: 0.3,
            HormoneType.GABA: 0.4,
            HormoneType.ENDORPHIN: 0.2,
        }

        # Feedback mechanisms
        self.hormone_feedback_enabled = True
        self.feedback_sensitivity = 0.5

    def _initialize_hormone_mappings(self) -> dict[str, EmotionalHormoneMapping]:
        """Initialize emotional state to hormone mappings"""
        return {
            "high_stress": EmotionalHormoneMapping(
                emotion_pattern="high_stress",
                primary_hormones={
                    HormoneType.CORTISOL: 0.8,
                    HormoneType.ADRENALINE: 0.6,
                },
                modulating_hormones={
                    HormoneType.GABA: -0.3  # Reduced inhibitory response
                },
                duration_minutes=45.0,
            ),
            "joy_happiness": EmotionalHormoneMapping(
                emotion_pattern="joy_happiness",
                primary_hormones={
                    HormoneType.DOPAMINE: 0.7,
                    HormoneType.SEROTONIN: 0.5,
                    HormoneType.ENDORPHIN: 0.4,
                },
                modulating_hormones={HormoneType.OXYTOCIN: 0.3},
                duration_minutes=60.0,
            ),
            "anxiety_fear": EmotionalHormoneMapping(
                emotion_pattern="anxiety_fear",
                primary_hormones={
                    HormoneType.CORTISOL: 0.7,
                    HormoneType.ADRENALINE: 0.8,
                },
                modulating_hormones={
                    HormoneType.SEROTONIN: -0.2,
                    HormoneType.GABA: -0.4,
                },
                duration_minutes=40.0,
            ),
            "sadness_depression": EmotionalHormoneMapping(
                emotion_pattern="sadness_depression",
                primary_hormones={
                    HormoneType.SEROTONIN: -0.4,  # Reduced serotonin
                    HormoneType.DOPAMINE: -0.3,  # Reduced dopamine
                },
                modulating_hormones={HormoneType.CORTISOL: 0.4},
                duration_minutes=120.0,  # Longer duration for mood states
            ),
            "anger_frustration": EmotionalHormoneMapping(
                emotion_pattern="anger_frustration",
                primary_hormones={
                    HormoneType.ADRENALINE: 0.9,
                    HormoneType.CORTISOL: 0.6,
                },
                modulating_hormones={
                    HormoneType.GABA: -0.5,
                    HormoneType.SEROTONIN: -0.2,
                },
                duration_minutes=30.0,
            ),
            "calm_relaxed": EmotionalHormoneMapping(
                emotion_pattern="calm_relaxed",
                primary_hormones={HormoneType.GABA: 0.6, HormoneType.SEROTONIN: 0.4},
                modulating_hormones={
                    HormoneType.MELATONIN: 0.2,
                    HormoneType.CORTISOL: -0.3,
                },
                duration_minutes=90.0,
            ),
            "excitement_anticipation": EmotionalHormoneMapping(
                emotion_pattern="excitement_anticipation",
                primary_hormones={
                    HormoneType.DOPAMINE: 0.8,
                    HormoneType.ADRENALINE: 0.5,
                },
                modulating_hormones={HormoneType.ENDORPHIN: 0.3},
                duration_minutes=45.0,
            ),
        }

    def _initialize_regulation_mappings(
        self,
    ) -> dict[RegulationStrategy, dict[str, float]]:
        """Initialize regulation strategy to hormone mappings"""
        return {
            RegulationStrategy.BREATHING: {
                HormoneType.GABA: 0.4,  # Calming effect
                HormoneType.SEROTONIN: 0.3,  # Mood stabilization
                HormoneType.CORTISOL: -0.2,  # Stress reduction
            },
            RegulationStrategy.COGNITIVE: {
                HormoneType.DOPAMINE: 0.2,  # Reward for mental effort
                HormoneType.SEROTONIN: 0.3,  # Mood improvement
                HormoneType.ENDORPHIN: 0.1,  # Satisfaction
            },
            RegulationStrategy.DAMPENING: {
                HormoneType.GABA: 0.5,  # Strong inhibitory effect
                HormoneType.CORTISOL: -0.4,  # Reduce stress
                HormoneType.ADRENALINE: -0.3,  # Reduce activation
            },
            RegulationStrategy.AMPLIFICATION: {
                HormoneType.DOPAMINE: 0.3,  # Boost motivation
                HormoneType.ENDORPHIN: 0.2,  # Enhance positive feelings
                HormoneType.SEROTONIN: 0.2,  # Stabilize mood
            },
            RegulationStrategy.STABILIZATION: {
                HormoneType.SEROTONIN: 0.4,  # Mood stabilization
                HormoneType.GABA: 0.2,  # Mild calming
                HormoneType.OXYTOCIN: 0.1,  # Social comfort
            },
            RegulationStrategy.ACCEPTANCE: {
                HormoneType.OXYTOCIN: 0.3,  # Self-compassion
                HormoneType.ENDORPHIN: 0.2,  # Natural pain relief
                HormoneType.SEROTONIN: 0.2,  # Mood support
            },
            RegulationStrategy.DISTRACTION: {
                HormoneType.DOPAMINE: 0.2,  # Mild reward
                HormoneType.GABA: 0.1,  # Slight calming
            },
            RegulationStrategy.REDIRECTION: {
                HormoneType.DOPAMINE: 0.3,  # Motivation for new direction
                HormoneType.SEROTONIN: 0.2,  # Mood support
                HormoneType.ADRENALINE: -0.2,  # Reduce misdirected energy
            },
        }

    async def process_emotional_hormones(
        self, regulation_response: RegulationResponse, context: dict[str, Any]
    ) -> dict[str, float]:
        """
        Process emotional state and trigger appropriate hormone releases
        """
        if not ENDOCRINE_AVAILABLE:
            logger.warning("Endocrine system not available - using simulation")
            return self._simulate_hormone_release(regulation_response, context)

        try:
            # Analyze emotional state
            emotional_pattern = self._analyze_emotional_pattern(
                regulation_response.original_state
            )

            # Calculate hormone triggers from emotional state
            emotional_triggers = await self._calculate_emotional_hormone_triggers(
                emotional_pattern, regulation_response, context
            )

            # Calculate hormone triggers from regulation strategy
            regulation_triggers = await self._calculate_regulation_hormone_triggers(
                regulation_response.strategy_used, regulation_response.effectiveness
            )

            # Combine and balance hormone releases
            combined_triggers = self._combine_hormone_triggers(
                emotional_triggers, regulation_triggers
            )

            # Apply hormone feedback mechanisms
            if self.hormone_feedback_enabled:
                combined_triggers = await self._apply_hormone_feedback(
                    combined_triggers
                )

            # Execute hormone releases
            await self._execute_hormone_releases(combined_triggers, context)

            # Record for learning and analysis
            await self._record_hormone_release(
                combined_triggers, regulation_response, context
            )

            return combined_triggers

        except Exception as e:
            logger.error(f"Error processing emotional hormones: {e}")
            return {}

    def _analyze_emotional_pattern(self, emotional_state: VADVector) -> str:
        """Analyze emotional state and classify into hormone-relevant patterns"""

        # High arousal + negative valence = stress/anxiety
        if emotional_state.arousal > 0.5 and emotional_state.valence < -0.3:
            if emotional_state.arousal > 0.7:
                return (
                    "high_stress"
                    if emotional_state.dominance < 0
                    else "anger_frustration"
                )
            else:
                return "anxiety_fear"

        # High arousal + positive valence = excitement/joy
        elif emotional_state.arousal > 0.3 and emotional_state.valence > 0.3:
            if emotional_state.valence > 0.6:
                return "joy_happiness"
            else:
                return "excitement_anticipation"

        # Low arousal + negative valence = sadness/depression
        elif emotional_state.arousal < -0.2 and emotional_state.valence < -0.2:
            return "sadness_depression"

        # Low arousal + neutral/positive valence = calm/relaxed
        elif emotional_state.arousal < 0.1 and emotional_state.valence > -0.2:
            return "calm_relaxed"

        # Default to stress pattern for high intensity situations
        elif emotional_state.intensity > 0.8:
            return "high_stress"

        # Default neutral pattern
        return "calm_relaxed"

    async def _calculate_emotional_hormone_triggers(
        self,
        emotional_pattern: str,
        regulation_response: RegulationResponse,
        context: dict[str, Any],
    ) -> dict[str, float]:
        """Calculate hormone triggers based on emotional pattern"""

        if emotional_pattern not in self.emotional_hormone_mappings:
            return {}

        mapping = self.emotional_hormone_mappings[emotional_pattern]

        # Calculate release amounts based on emotional intensity and regulation
        # effectiveness
        triggers = mapping.calculate_release_amount(
            regulation_response.original_state.intensity,
            regulation_response.effectiveness,
        )

        # Apply contextual modulations
        triggers = self._apply_contextual_modulations(triggers, context)

        return triggers

    async def _calculate_regulation_hormone_triggers(
        self, strategy: RegulationStrategy, effectiveness: float
    ) -> dict[str, float]:
        """Calculate hormone triggers based on regulation strategy"""

        if strategy not in self.regulation_hormone_mappings:
            return {}

        base_triggers = self.regulation_hormone_mappings[strategy]

        # Scale by effectiveness
        scaled_triggers = {
            hormone: amount * effectiveness for hormone, amount in base_triggers.items()
        }

        return scaled_triggers

    def _combine_hormone_triggers(
        self,
        emotional_triggers: dict[str, float],
        regulation_triggers: dict[str, float],
    ) -> dict[str, float]:
        """Combine emotional and regulation hormone triggers"""

        combined = emotional_triggers.copy()

        for hormone, amount in regulation_triggers.items():
            if hormone in combined:
                # For conflicting signals, take weighted average favoring regulation
                combined[hormone] = combined[hormone] * 0.4 + amount * 0.6
            else:
                combined[hormone] = amount

        # Ensure values stay within reasonable bounds
        for hormone in combined:
            combined[hormone] = max(-1.0, min(1.0, combined[hormone]))

        return combined

    def _apply_contextual_modulations(
        self, triggers: dict[str, float], context: dict[str, Any]
    ) -> dict[str, float]:
        """Apply contextual modulations to hormone triggers"""

        modulated = triggers.copy()

        # Time of day effects
        time_of_day = context.get("time_of_day", "").lower()
        if time_of_day == "morning":
            # Morning - boost activation hormones
            if HormoneType.DOPAMINE in modulated:
                modulated[HormoneType.DOPAMINE] *= 1.2
            if HormoneType.CORTISOL in modulated:
                modulated[HormoneType.CORTISOL] *= 1.1
        elif time_of_day in ["evening", "night"]:
            # Evening/Night - boost calming hormones
            if HormoneType.MELATONIN in modulated:
                modulated[HormoneType.MELATONIN] *= 1.3
            if HormoneType.GABA in modulated:
                modulated[HormoneType.GABA] *= 1.2

        # Environment effects
        environment = context.get("environment", "").lower()
        if environment == "work":
            # Work environment - modulate stress response
            if HormoneType.CORTISOL in modulated:
                modulated[HormoneType.CORTISOL] *= 1.15
        elif environment in ["home", "personal"]:
            # Home environment - boost comfort hormones
            if HormoneType.OXYTOCIN in modulated:
                modulated[HormoneType.OXYTOCIN] *= 1.2

        # Stress level context
        stress_level = context.get("stress_level", 0.5)
        if stress_level > 0.7:
            # High stress - amplify calming hormones from regulation
            calming_hormones = [HormoneType.GABA, HormoneType.SEROTONIN]
            for hormone in calming_hormones:
                if hormone in modulated and modulated[hormone] > 0:
                    modulated[hormone] *= 1.3

        return modulated

    async def _apply_hormone_feedback(
        self, triggers: dict[str, float]
    ) -> dict[str, float]:
        """Apply feedback mechanisms based on current hormone levels"""

        if not ENDOCRINE_AVAILABLE:
            return triggers

        try:
            # Get current hormone levels
            current_levels = self.hormone_system.get_hormone_levels()

            adjusted_triggers = triggers.copy()

            for hormone, trigger_amount in triggers.items():
                current_level = current_levels.get(
                    hormone, self.baseline_levels.get(hormone, 0.5)
                )
                baseline = self.baseline_levels.get(hormone, 0.5)

                # Calculate feedback adjustment
                if current_level > baseline * 1.5:
                    # High levels - reduce further increases
                    if trigger_amount > 0:
                        adjusted_triggers[hormone] = trigger_amount * 0.7
                elif current_level < baseline * 0.5:
                    # Low levels - boost increases
                    if trigger_amount > 0:
                        adjusted_triggers[hormone] = trigger_amount * 1.3

                # Apply sensitivity scaling
                adjusted_triggers[hormone] *= self.feedback_sensitivity

            return adjusted_triggers

        except Exception as e:
            logger.error(f"Error applying hormone feedback: {e}")
            return triggers

    async def _execute_hormone_releases(
        self, triggers: dict[str, float], context: dict[str, Any]
    ):
        """Execute actual hormone releases through endocrine system"""

        if not ENDOCRINE_AVAILABLE:
            return

        try:
            for hormone, amount in triggers.items():
                if abs(amount) > 0.01:  # Only release significant amounts

                    # Determine duration based on hormone type and amount
                    duration = self._calculate_release_duration(hormone, amount)

                    # Execute release
                    if amount > 0:
                        await self.hormone_system.release_hormone(
                            hormone_type=hormone, amount=amount, duration=duration
                        )
                    else:
                        # Negative amount = suppression
                        await self.hormone_system.suppress_hormone(
                            hormone_type=hormone,
                            suppression_factor=abs(amount),
                            duration=duration,
                        )

                    logger.debug(f"Released {hormone}: {amount:.3f} for {duration}min")

        except Exception as e:
            logger.error(f"Error executing hormone releases: {e}")

    def _calculate_release_duration(self, hormone: str, amount: float) -> float:
        """Calculate appropriate release duration for hormone"""

        # Base durations for different hormones (in minutes)
        base_durations = {
            HormoneType.ADRENALINE: 15.0,  # Quick acting
            HormoneType.CORTISOL: 60.0,  # Medium duration
            HormoneType.DOPAMINE: 30.0,  # Medium-short
            HormoneType.SEROTONIN: 45.0,  # Medium
            HormoneType.GABA: 20.0,  # Short-medium
            HormoneType.OXYTOCIN: 25.0,  # Short-medium
            HormoneType.MELATONIN: 120.0,  # Long duration
            HormoneType.ENDORPHIN: 40.0,  # Medium
        }

        base_duration = base_durations.get(hormone, 30.0)

        # Scale duration by release amount
        intensity_factor = min(2.0, max(0.5, abs(amount) * 2))

        return base_duration * intensity_factor

    async def _record_hormone_release(
        self,
        triggers: dict[str, float],
        regulation_response: RegulationResponse,
        context: dict[str, Any],
    ):
        """Record hormone release for learning and analysis"""

        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_id": context.get("user_id", "unknown"),
            "regulation_strategy": regulation_response.strategy_used.value,
            "regulation_effectiveness": regulation_response.effectiveness,
            "emotional_state": regulation_response.original_state.to_dict(),
            "hormone_triggers": triggers,
            "context": context,
        }

        self.hormone_release_history.append(record)

        # Limit history size
        if len(self.hormone_release_history) > 1000:
            self.hormone_release_history = self.hormone_release_history[-800:]

    def _simulate_hormone_release(
        self, regulation_response: RegulationResponse, context: dict[str, Any]
    ) -> dict[str, float]:
        """Simulate hormone release when endocrine system is not available"""

        # Basic simulation based on regulation response
        simulated_triggers = {}

        effectiveness = regulation_response.effectiveness
        original_state = regulation_response.original_state
        strategy = regulation_response.strategy_used

        # Stress-related hormones
        if original_state.arousal > 0.5 or original_state.valence < -0.3:
            simulated_triggers[HormoneType.CORTISOL] = (1 - effectiveness) * 0.6
            simulated_triggers[HormoneType.ADRENALINE] = (1 - effectiveness) * 0.4

        # Positive regulation hormones
        if effectiveness > 0.6:
            if strategy == RegulationStrategy.BREATHING:
                simulated_triggers[HormoneType.GABA] = effectiveness * 0.4
                simulated_triggers[HormoneType.SEROTONIN] = effectiveness * 0.3
            elif strategy == RegulationStrategy.COGNITIVE:
                simulated_triggers[HormoneType.DOPAMINE] = effectiveness * 0.3
                simulated_triggers[HormoneType.SEROTONIN] = effectiveness * 0.2

        return simulated_triggers

    def get_hormone_analytics(self, user_id: str, hours: int = 24) -> dict[str, Any]:
        """Get hormone release analytics for user"""

        cutoff_time = datetime.now(timezone.utc).timestamp() - (hours * 3600)

        relevant_records = [
            record
            for record in self.hormone_release_history
            if record["user_id"] == user_id
            and datetime.fromisoformat(record["timestamp"]).timestamp() > cutoff_time
        ]

        if not relevant_records:
            return {"message": "No hormone data available"}

        # Analyze hormone patterns
        hormone_totals = {}
        strategy_effectiveness = {}

        for record in relevant_records:
            # Sum hormone releases
            for hormone, amount in record["hormone_triggers"].items():
                if hormone not in hormone_totals:
                    hormone_totals[hormone] = {
                        "positive": 0.0,
                        "negative": 0.0,
                        "count": 0,
                    }

                if amount > 0:
                    hormone_totals[hormone]["positive"] += amount
                else:
                    hormone_totals[hormone]["negative"] += abs(amount)
                hormone_totals[hormone]["count"] += 1

            # Track strategy effectiveness
            strategy = record["regulation_strategy"]
            effectiveness = record["regulation_effectiveness"]

            if strategy not in strategy_effectiveness:
                strategy_effectiveness[strategy] = []
            strategy_effectiveness[strategy].append(effectiveness)

        # Calculate averages
        for strategy in strategy_effectiveness:
            scores = strategy_effectiveness[strategy]
            strategy_effectiveness[strategy] = {
                "average": sum(scores) / len(scores),
                "count": len(scores),
            }

        return {
            "total_hormone_events": len(relevant_records),
            "hormone_release_patterns": hormone_totals,
            "strategy_effectiveness": strategy_effectiveness,
            "most_active_hormones": sorted(
                [
                    (h, data["positive"] + data["negative"])
                    for h, data in hormone_totals.items()
                ],
                key=lambda x: x[1],
                reverse=True,
            )[:5],
            "stress_indicators": {
                "cortisol_releases": hormone_totals.get(HormoneType.CORTISOL, {}).get(
                    "positive", 0
                ),
                "adrenaline_releases": hormone_totals.get(
                    HormoneType.ADRENALINE, {}
                ).get("positive", 0),
                "stress_regulation_success": sum(
                    1
                    for r in relevant_records
                    if r["regulation_effectiveness"] > 0.7
                    and (
                        HormoneType.CORTISOL in r["hormone_triggers"]
                        or HormoneType.ADRENALINE in r["hormone_triggers"]
                    )
                ),
            },
            "wellbeing_indicators": {
                "serotonin_releases": hormone_totals.get(HormoneType.SEROTONIN, {}).get(
                    "positive", 0
                ),
                "dopamine_releases": hormone_totals.get(HormoneType.DOPAMINE, {}).get(
                    "positive", 0
                ),
                "endorphin_releases": hormone_totals.get(HormoneType.ENDORPHIN, {}).get(
                    "positive", 0
                ),
            },
        }

    def get_integration_status(self) -> dict[str, Any]:
        """Get endocrine integration status"""
        return {
            "endocrine_system_available": ENDOCRINE_AVAILABLE,
            "hormone_mappings_loaded": len(self.emotional_hormone_mappings),
            "regulation_mappings_loaded": len(self.regulation_hormone_mappings),
            "hormone_release_history_size": len(self.hormone_release_history),
            "feedback_enabled": self.hormone_feedback_enabled,
            "feedback_sensitivity": self.feedback_sensitivity,
            "baseline_hormones": self.baseline_levels,
        }
