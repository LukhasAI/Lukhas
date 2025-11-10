import logging
import time
from typing import Any, Dict

from core.matriz_consciousness_signals import BioSymbolicData, ConsciousnessSignal

from .bio_symbolic_objects import AdaptationRule, BioPatternType

logger = logging.getLogger(__name__)


class Adapter:
    def __init__(self):
        self.adaptation_rules: list[AdaptationRule] = []
        self._initialize_default_adaptation_rules()

    def _initialize_default_adaptation_rules(self):
        """Initialize default bio-symbolic adaptation rules"""

        # Neural oscillation to synaptic plasticity adaptation
        self.adaptation_rules.append(
            AdaptationRule(
                rule_id="neural_osc_to_plasticity",
                source_pattern=BioPatternType.NEURAL_OSCILLATION,
                target_pattern=BioPatternType.SYNAPTIC_PLASTICITY,
                adaptation_strength=0.8,
                adaptation_direction=[0.1, 0.3, 0.6],
                trigger_conditions={"frequency_range": (8, 40), "coherence_min": 0.6},
                success_criteria={"plasticity_increase": 0.2},
                decay_rate=0.95,
                learning_rate=0.02,
            )
        )

        # Cellular adaptation to membrane dynamics
        self.adaptation_rules.append(
            AdaptationRule(
                rule_id="cellular_to_membrane",
                source_pattern=BioPatternType.CELLULAR_ADAPTATION,
                target_pattern=BioPatternType.MEMBRANE_DYNAMICS,
                adaptation_strength=0.7,
                adaptation_direction=[0.2, 0.4, 0.4],
                trigger_conditions={"adaptation_rate": 0.1},
                success_criteria={"membrane_fluidity": 0.8},
                decay_rate=0.9,
                learning_rate=0.015,
            )
        )

        # Metabolic flow to enzymatic cascade
        self.adaptation_rules.append(
            AdaptationRule(
                rule_id="metabolic_to_enzymatic",
                source_pattern=BioPatternType.METABOLIC_FLOW,
                target_pattern=BioPatternType.ENZYMATIC_CASCADE,
                adaptation_strength=0.9,
                adaptation_direction=[0.3, 0.3, 0.4],
                trigger_conditions={"flow_rate": 0.5},
                success_criteria={"cascade_efficiency": 0.75},
                decay_rate=0.85,
                learning_rate=0.025,
            )
        )

    def apply_adaptations(
        self,
        bio_data: BioSymbolicData,
        symbolic_data: Dict[str, Any],
        signal: ConsciousnessSignal,
        processing_stats,
    ) -> BioSymbolicData:
        """Apply bio-symbolic adaptations based on adaptation rules"""

        adapted_data = bio_data
        adaptations_applied = 0

        for rule in self.adaptation_rules:
            if self._check_adaptation_triggers(rule, bio_data, signal):
                adapted_data = self._apply_single_adaptation(
                    rule, adapted_data, symbolic_data
                )
                adaptations_applied += 1
                processing_stats["adaptations_applied"] += 1

                logger.debug(
                    f"Applied adaptation rule {rule.rule_id} to signal {signal.signal_id}"
                )

        # Update adaptation vector with new coefficients
        if adaptations_applied > 0:
            adapted_data.adaptation_vector["adaptations_applied"] = adaptations_applied
            adapted_data.adaptation_vector["adaptation_timestamp"] = time.time()

        return adapted_data

    def _check_adaptation_triggers(
        self, rule: AdaptationRule, bio_data: BioSymbolicData, signal: ConsciousnessSignal
    ) -> bool:
        """Check if adaptation rule triggers should fire"""

        try:
            for condition_key, condition_value in rule.trigger_conditions.items():
                if condition_key == "frequency_range":
                    freq = bio_data.oscillation_frequency
                    if not (condition_value[0] <= freq <= condition_value[1]):
                        return False

                elif condition_key == "coherence_min":
                    if bio_data.coherence_score < condition_value:
                        return False

                elif condition_key == "adaptation_rate":
                    if abs(bio_data.entropy_delta) < condition_value:
                        return False

                elif condition_key == "flow_rate":
                    temporal_flow = 1.0 - bio_data.temporal_decay
                    if temporal_flow < condition_value:
                        return False

                elif condition_key == "awareness_threshold":
                    if signal.awareness_level < condition_value:
                        return False

            return True

        except Exception as e:
            logger.warning(
                f"Error checking adaptation triggers for rule {rule.rule_id}: {e}"
            )
            return False

    def _apply_single_adaptation(
        self,
        rule: AdaptationRule,
        bio_data: BioSymbolicData,
        symbolic_data: Dict[str, Any],
    ) -> BioSymbolicData:
        """Apply a single adaptation rule to bio-symbolic data"""

        # Create modified copy
        adapted_data = BioSymbolicData(
            pattern_type=bio_data.pattern_type,
            oscillation_frequency=bio_data.oscillation_frequency,
            coherence_score=bio_data.coherence_score,
            adaptation_vector=bio_data.adaptation_vector.copy(),
            entropy_delta=bio_data.entropy_delta,
            resonance_patterns=bio_data.resonance_patterns.copy(),
            membrane_permeability=bio_data.membrane_permeability,
            temporal_decay=bio_data.temporal_decay,
        )

        # Apply adaptation based on rule type
        if (
            rule.source_pattern == BioPatternType.NEURAL_OSCILLATION
            and rule.target_pattern == BioPatternType.SYNAPTIC_PLASTICITY
        ):
            # Increase frequency and coherence for synaptic plasticity
            adapted_data.oscillation_frequency *= 1 + rule.adaptation_strength * 0.1
            adapted_data.coherence_score = min(
                1.0, adapted_data.coherence_score + rule.adaptation_strength * 0.05
            )
            adapted_data.adaptation_vector[
                "synaptic_plasticity"
            ] = rule.adaptation_strength

        elif (
            rule.source_pattern == BioPatternType.CELLULAR_ADAPTATION
            and rule.target_pattern == BioPatternType.MEMBRANE_DYNAMICS
        ):
            # Adjust membrane permeability
            adapted_data.membrane_permeability = min(
                1.0,
                adapted_data.membrane_permeability + rule.adaptation_strength * 0.1,
            )
            adapted_data.adaptation_vector[
                "membrane_adaptation"
            ] = rule.adaptation_strength

        elif (
            rule.source_pattern == BioPatternType.METABOLIC_FLOW
            and rule.target_pattern == BioPatternType.ENZYMATIC_CASCADE
        ):
            # Improve temporal decay (less decay = better cascade)
            adapted_data.temporal_decay = min(
                1.0, adapted_data.temporal_decay + rule.adaptation_strength * 0.05
            )
            adapted_data.adaptation_vector[
                "enzymatic_cascade"
            ] = rule.adaptation_strength

        # Apply directional adaptation
        for i, direction_weight in enumerate(rule.adaptation_direction):
            if i == 0:  # Frequency component
                adapted_data.oscillation_frequency += (
                    direction_weight * rule.learning_rate * 10
                )
            elif i == 1:  # Coherence component
                adapted_data.coherence_score = min(
                    1.0,
                    max(
                        0.0,
                        adapted_data.coherence_score + direction_weight * rule.learning_rate,
                    ),
                )
            elif i == 2:  # Entropy component
                adapted_data.entropy_delta += direction_weight * rule.learning_rate * 0.1

        return adapted_data
