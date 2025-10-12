from datetime import timezone

"""

#TAG:consciousness
#TAG:reflection
#TAG:neuroplastic
#TAG:colony


Quantum Layer for Bio Systems
Provides quantum-enhanced bio-oscillator functionality.
"""
import math
import random
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class QIBioConfig:
    """Configuration for quantum bio-oscillator."""

    base_frequency: float = 5.0
    qi_coherence: float = 0.8
    entanglement_strength: float = 0.6
    decoherence_rate: float = 0.05
    measurement_precision: float = 0.9
    oscillation_amplitude: float = 1.0

    def __post_init__(self):
        """Validate configuration parameters."""
        self.base_frequency = max(0.1, min(100.0, self.base_frequency))
        self.qi_coherence = max(0.0, min(1.0, self.qi_coherence))
        self.entanglement_strength = max(0.0, min(1.0, self.entanglement_strength))
        self.decoherence_rate = max(0.0, min(1.0, self.decoherence_rate))
        self.measurement_precision = max(0.0, min(1.0, self.measurement_precision))
        self.oscillation_amplitude = max(0.1, min(10.0, self.oscillation_amplitude))


class QIBioOscillator:
    """
    Quantum-enhanced bio-oscillator for consciousness and dream systems.

    This class combines biological rhythms with coherence-inspired processing effects
    to create complex oscillatory patterns suitable for consciousness modeling.
    """

    def __init__(self, config: Optional[QIBioConfig] = None):
        """
        Initialize the quantum bio-oscillator.

        Args:
            config: Configuration for the oscillator
        """
        self.config = config or QIBioConfig()
        self.qi_like_state = self._initialize_quantum_like_state()
        self.oscillation_history = []
        self.entangled_oscillators = {}
        self.coherence_matrix = []
        self.measurement_count = 0

    def _initialize_quantum_like_state(self) -> dict[str, Any]:
        """Initialize quantum-like state for the oscillator."""
        return {
            "coherence": self.config.qi_coherence,
            "phase": 0.0,
            "amplitude": self.config.oscillation_amplitude,
            "frequency": self.config.base_frequency,
            "entanglement_pairs": [],
            "superposition_active": False,
            "measurement_disturbance": 0.0,
        }

    def oscillate(self, time_point: float, external_influence: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """
        Generate oscillation value at given time point.

        Args:
            time_point: Time point for oscillation calculation
            external_influence: Optional external influence on oscillation

        Returns:
            Dictionary with oscillation data
        """
        # Base oscillation
        base_oscillation = self.qi_like_state["amplitude"] * math.sin(
            2 * math.pi * self.qi_like_state["frequency"] * time_point + self.qi_like_state["phase"]
        )

        # Apply coherence-inspired processing effects
        coherence_factor = self.qi_like_state["coherence"]
        qi_noise = (1 - coherence_factor) * random.uniform(-0.1, 0.1)

        # Apply external influence if provided
        if external_influence:
            influence_factor = external_influence.get("strength", 0.1)
            influence_phase = external_influence.get("phase", 0.0)
            influence_freq = external_influence.get("frequency", self.qi_like_state["frequency"])

            external_component = influence_factor * math.sin(
                2 * math.pi * influence_freq * time_point + influence_phase
            )
        else:
            external_component = 0.0

        # Combine components
        total_oscillation = base_oscillation + qi_noise + external_component

        # Apply measurement disturbance
        if self.qi_like_state["measurement_disturbance"] > 0:
            disturbance = self.qi_like_state["measurement_disturbance"] * random.uniform(-0.05, 0.05)
            total_oscillation += disturbance

            # Decay measurement disturbance
            self.qi_like_state["measurement_disturbance"] *= 0.9

        # Create result
        result = {
            "time": time_point,
            "oscillation_value": total_oscillation,
            "base_component": base_oscillation,
            "qi_noise": qi_noise,
            "external_component": external_component,
            "coherence": self.qi_like_state["coherence"],
            "frequency": self.qi_like_state["frequency"],
            "phase": self.qi_like_state["phase"],
            "amplitude": self.qi_like_state["amplitude"],
        }

        # Store in history
        self.oscillation_history.append(result)

        # Limit history size
        if len(self.oscillation_history) > 1000:
            self.oscillation_history = self.oscillation_history[-1000:]

        return result

    def create_entanglement(
        self, other_oscillator: "QIBioOscillator", strength: Optional[float] = None
    ) -> dict[str, Any]:
        """
        Create entanglement-like correlation with another oscillator.

        Args:
            other_oscillator: Another quantum bio-oscillator
            strength: Entanglement strength (0-1)

        Returns:
            Entanglement result
        """
        if strength is None:
            strength = self.config.entanglement_strength

        # Create entanglement ID
        entanglement_id = f"entanglement_{id(self)}_{id(other_oscillator)}"

        # Store entanglement in both oscillators
        self.entangled_oscillators[entanglement_id] = entanglement_data
        other_oscillator.entangled_oscillators[entanglement_id] = entanglement_data

        # Update quantum-like states
        self.qi_like_state["entanglement_pairs"].append(entanglement_id)
        other_oscillator.qi_like_state["entanglement_pairs"].append(entanglement_id)

        return entanglement_data

    def apply_entanglement_effects(self, time_point: float) -> dict[str, Any]:
        """
        Apply entanglement effects on oscillation.

        Args:
            time_point: Current time point

        Returns:
            Entanglement effects data
        """
        if not self.entangled_oscillators:
            return {"entanglement_effect": 0.0, "entangled_pairs": 0}

        total_effect = 0.0
        active_entanglements = 0

        for entanglement_data in self.entangled_oscillators.values():
            other_oscillator = (
                entanglement_data["oscillator_2"]
                if entanglement_data["oscillator_1"] is self
                else entanglement_data["oscillator_1"]
            )

            # Calculate entanglement effect based on other oscillator's state
            phase_difference = abs(self.qi_like_state["phase"] - other_oscillator.qi_like_state["phase"])
            correlation_factor = entanglement_data["phase_correlation"]

            # Entanglement effect depends on phase correlation
            entanglement_effect = correlation_factor * math.cos(phase_difference) * entanglement_data["strength"]
            total_effect += entanglement_effect
            active_entanglements += 1

        # Apply entanglement effects to quantum-like state
        if active_entanglements > 0:
            avg_effect = total_effect / active_entanglements
            self.qi_like_state["phase"] += avg_effect * 0.1  # Small phase adjustment
            self.qi_like_state["coherence"] += avg_effect * 0.05  # Coherence enhancement
            self.qi_like_state["coherence"] = max(0.0, min(1.0, self.qi_like_state["coherence"]))

        return {
            "entanglement_effect": total_effect,
            "entangled_pairs": active_entanglements,
            "avg_effect": (total_effect / active_entanglements if active_entanglements > 0 else 0.0),
        }

    def measure_quantum_property(self, property_name: str) -> dict[str, Any]:
        """
        Measure a quantum property of the oscillator.

        Args:
            property_name: Name of the property to measure

        Returns:
            Measurement result
        """
        self.measurement_count += 1

        # Add measurement disturbance
        disturbance_strength = 1.0 - self.config.measurement_precision
        self.qi_like_state["measurement_disturbance"] = disturbance_strength

        measurement_result = {
            "property": property_name,
            "measurement_count": self.measurement_count,
            "timestamp": self._get_timestamp(),
            "precision": self.config.measurement_precision,
        }

        if property_name == "coherence":
            # Measure coherence with uncertainty
            uncertainty = disturbance_strength * 0.1
            measured_value = self.qi_like_state["coherence"] + random.uniform(-uncertainty, uncertainty)
            measurement_result["value"] = max(0.0, min(1.0, measured_value))

        elif property_name == "phase":
            # Measure phase
            uncertainty = disturbance_strength * 0.2
            measured_value = self.qi_like_state["phase"] + random.uniform(-uncertainty, uncertainty)
            measurement_result["value"] = measured_value % (2 * math.pi)

        elif property_name == "frequency":
            # Measure frequency
            uncertainty = disturbance_strength * 0.5
            measured_value = self.qi_like_state["frequency"] + random.uniform(-uncertainty, uncertainty)
            measurement_result["value"] = max(0.1, measured_value)

        elif property_name == "amplitude":
            # Measure amplitude
            uncertainty = disturbance_strength * 0.1
            measured_value = self.qi_like_state["amplitude"] + random.uniform(-uncertainty, uncertainty)
            measurement_result["value"] = max(0.0, measured_value)

        else:
            measurement_result["error"] = f"Unknown property: {property_name}"

    def get_oscillator_metrics(self) -> dict[str, Any]:
        """
        Get comprehensive metrics for the oscillator.

        Returns:
            Dictionary with oscillator metrics
        """
        metrics = {
            "qi_like_state": self.qi_like_state.copy(),
            "entangled_pairs": len(self.entangled_oscillators),
            "measurement_count": self.measurement_count,
            "history_length": len(self.oscillation_history),
            "config": {
                "base_frequency": self.config.base_frequency,
                "qi_coherence": self.config.qi_coherence,
                "entanglement_strength": self.config.entanglement_strength,
                "decoherence_rate": self.config.decoherence_rate,
            },
        }

        # Add statistics from history
        if self.oscillation_history:
            values = [entry["oscillation_value"] for entry in self.oscillation_history]
            metrics["oscillation_stats"] = {
                "mean": sum(values) / len(values),
                "min": min(values),
                "max": max(values),
                "variance": self._calculate_variance(values),
            }

        return metrics

    def _calculate_variance(self, values: list[float]) -> float:
        """Calculate variance of a list of values."""
        if len(values) < 2:
            return 0.0

        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance

    def reset_oscillator(self):
        """Reset the oscillator to initial state."""
        self.qi_like_state = self._initialize_quantum_like_state()
        self.oscillation_history.clear()
        self.entangled_oscillators.clear()
        self.coherence_matrix.clear()
        self.measurement_count = 0

    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        import datetime

        return datetime.datetime.now(timezone.utc).isoformat()

    def synchronize_with_rhythm(self, rhythm_frequency: float, sync_strength: float = 0.5) -> dict[str, Any]:
        """
        Synchronize oscillator with external rhythm.

        Args:
            rhythm_frequency: Frequency to synchronize with
            sync_strength: Strength of synchronization (0-1)

        Returns:
            Synchronization result
        """
        # Calculate frequency difference
        freq_diff = abs(self.qi_like_state["frequency"] - rhythm_frequency)

        # Apply synchronization
        if freq_diff > 0.1:  # Only sync if difference is significant
            freq_adjustment = sync_strength * (rhythm_frequency - self.qi_like_state["frequency"])
            self.qi_like_state["frequency"] += freq_adjustment * 0.1  # Gradual adjustment

            # Adjust phase to align with rhythm
            phase_adjustment = sync_strength * 0.1
            self.qi_like_state["phase"] += phase_adjustment

        return {
            "target_frequency": rhythm_frequency,
            "current_frequency": self.qi_like_state["frequency"],
            "sync_strength": sync_strength,
            "frequency_difference": freq_diff,
            "synchronized": freq_diff < 0.1,
        }

    def create_coherence_field(self, other_oscillators: list["QIBioOscillator"]) -> dict[str, Any]:
        """
        Create coherence field with multiple oscillators.

        Args:
            other_oscillators: List of other oscillators

        Returns:
            Coherence field data
        """
        if not other_oscillators:
            return {"coherence_field_strength": 0.0, "participants": 0}

        # Calculate coherence matrix
        coherence_matrix = []
        total_coherence = 0.0

        for other in other_oscillators:
            # Calculate pairwise coherence
            freq_similarity = 1.0 - abs(self.qi_like_state["frequency"] - other.qi_like_state["frequency"]) / 10.0
            phase_similarity = 1.0 - abs(self.qi_like_state["phase"] - other.qi_like_state["phase"]) / (2 * math.pi)

            pairwise_coherence = (freq_similarity + phase_similarity) / 2
            coherence_matrix.append(pairwise_coherence)
            total_coherence += pairwise_coherence

        # Calculate field strength
        field_strength = total_coherence / len(other_oscillators) if other_oscillators else 0.0

        # Apply field effects
        if field_strength > 0.5:
            # Enhance coherence when field is strong
            self.qi_like_state["coherence"] += field_strength * 0.1
            self.qi_like_state["coherence"] = min(1.0, self.qi_like_state["coherence"])

        return {
            "coherence_field_strength": field_strength,
            "participants": len(other_oscillators),
            "coherence_matrix": coherence_matrix,
            "field_enhanced": field_strength > 0.5,
        }
