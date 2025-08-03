"""

#TAG:qim
#TAG:quantum_states
#TAG:neuroplastic
#TAG:colony


Quantum Dream Adapter for Dream Systems
Provides quantum-based dream processing and adaptation capabilities.
"""

from typing import Dict, Any, List, Optional, Tuple
import math
import random
import numpy as np
from dataclasses import dataclass


@dataclass
class DreamQuantumConfig:
    """Configuration for quantum dream processing."""

    coherence_threshold: float = 0.7
    entanglement_strength: float = 0.5
    superposition_depth: int = 3
    decoherence_rate: float = 0.1
    quantum_frequency: float = 6.5
    measurement_precision: float = 0.8

    def __post_init__(self):
        """Validate configuration parameters."""
        self.coherence_threshold = max(0.0, min(1.0, self.coherence_threshold))
        self.entanglement_strength = max(0.0, min(1.0, self.entanglement_strength))
        self.superposition_depth = max(1, min(10, self.superposition_depth))
        self.decoherence_rate = max(0.0, min(1.0, self.decoherence_rate))
        self.quantum_frequency = max(0.1, min(20.0, self.quantum_frequency))
        self.measurement_precision = max(0.0, min(1.0, self.measurement_precision))


class QuantumDreamAdapter:
    """
    Quantum-based dream processing adapter.

    This class provides quantum-inspired processing for dream systems,
    including superposition states, entanglement, and coherence management.
    """

    def __init__(self, config: Optional[DreamQuantumConfig] = None):
        """
        Initialize the quantum dream adapter.

        Args:
            config: Configuration for quantum-inspired processing
        """
        self.config = config or DreamQuantumConfig()
        self.quantum_like_state = self._initialize_quantum_like_state()
        self.entangled_dreams = {}
        self.coherence_history = []
        self.superposition_states = []

    def _initialize_quantum_like_state(self) -> Dict[str, Any]:
        """Initialize the quantum-like state for dream processing."""
        return {
            "coherence": self.config.coherence_threshold,
            "phase": 0.0,
            "amplitude": 1.0,
            "entanglement_pairs": [],
            "superposition_active": False,
            "measurement_count": 0,
        }

    def create_dream_superposition(
        self, dream_states: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Create a superposition of multiple dream states.

        Args:
            dream_states: List of dream state dictionaries

        Returns:
            Superposition dream state
        """
        if not dream_states:
            return {"error": "No dream states provided"}

        # Limit to configuration depth
        effective_states = dream_states[: self.config.superposition_depth]

        # Create superposition by averaging weighted states
        superposition = {
            "type": "superposition",
            "component_states": effective_states,
            "coherence": self.quantum_like_state["coherence"],
            "superposition_weights": [],
        }

        # Calculate weights for each component state
        total_weight = 0
        for i, state in enumerate(effective_states):
            weight = math.exp(-i * 0.5)  # Exponential decay for later states
            superposition["superposition_weights"].append(weight)
            total_weight += weight

        # Normalize weights
        superposition["superposition_weights"] = [
            w / total_weight for w in superposition["superposition_weights"]
        ]

        # Combine dream content
        combined_content = self._combine_dream_content(
            effective_states, superposition["superposition_weights"]
        )
        superposition.update(combined_content)

        # Update quantum-like state
        self.quantum_like_state["superposition_active"] = True
        self.superposition_states.append(superposition)

        return superposition

    def _combine_dream_content(
        self, states: List[Dict[str, Any]], weights: List[float]
    ) -> Dict[str, Any]:
        """Combine dream content from multiple states using superposition-like state."""
        combined = {
            "dream_content": "",
            "emotional_intensity": 0.0,
            "symbolic_elements": [],
            "narrative_coherence": 0.0,
            "lucidity_level": 0.0,
        }

        for state, weight in zip(states, weights):
            # Combine textual content
            if "dream_content" in state:
                combined["dream_content"] += f"[{weight:.2f}] {state['dream_content']} "

            # Weighted average for numerical values
            for key in ["emotional_intensity", "narrative_coherence", "lucidity_level"]:
                if key in state:
                    combined[key] += weight * state.get(key, 0)

            # Combine symbolic elements
            if "symbolic_elements" in state:
                combined["symbolic_elements"].extend(state["symbolic_elements"])

        # Remove duplicates from symbolic elements
        combined["symbolic_elements"] = list(set(combined["symbolic_elements"]))

        return combined

    def entangle_dreams(
        self,
        dream_id_1: str,
        dream_id_2: str,
        dream_data_1: Dict[str, Any],
        dream_data_2: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Create entanglement-like correlation between two dreams.

        Args:
            dream_id_1: ID of first dream
            dream_id_2: ID of second dream
            dream_data_1: Data for first dream
            dream_data_2: Data for second dream

        Returns:
            Entanglement result
        """
        entanglement_strength = self.config.entanglement_strength

        # Create entanglement pair
        entanglement_pair = {
            "dream_1": {"id": dream_id_1, "data": dream_data_1},
            "dream_2": {"id": dream_id_2, "data": dream_data_2},
            "strength": entanglement_strength,
            "created_at": self._get_timestamp(),
            "correlation_factors": self._calculate_correlation_factors(
                dream_data_1, dream_data_2
            ),
        }

        # Store entanglement
        pair_id = f"{dream_id_1}_{dream_id_2}"
        self.entangled_dreams[pair_id] = entanglement_pair

        # Update quantum-like state
        self.quantum_like_state["entanglement_pairs"].append(pair_id)

        # Create entangled properties
        entangled_result = self._create_entangled_properties(
            dream_data_1, dream_data_2, entanglement_strength
        )

        return {
            "pair_id": pair_id,
            "entanglement_strength": entanglement_strength,
            "entangled_properties": entangled_result,
            "correlation_factors": entanglement_pair["correlation_factors"],
        }

    def _calculate_correlation_factors(
        self, data1: Dict[str, Any], data2: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calculate correlation factors between two dream data sets."""
        factors = {}

        # Emotional correlation
        if "emotional_intensity" in data1 and "emotional_intensity" in data2:
            factors["emotional"] = 1.0 - abs(
                data1["emotional_intensity"] - data2["emotional_intensity"]
            )

        # Narrative correlation
        if "narrative_coherence" in data1 and "narrative_coherence" in data2:
            factors["narrative"] = 1.0 - abs(
                data1["narrative_coherence"] - data2["narrative_coherence"]
            )

        # Symbolic correlation
        if "symbolic_elements" in data1 and "symbolic_elements" in data2:
            set1 = set(data1["symbolic_elements"])
            set2 = set(data2["symbolic_elements"])
            if set1 and set2:
                factors["symbolic"] = len(set1 & set2) / len(set1 | set2)
            else:
                factors["symbolic"] = 0.0

        return factors

    def _create_entangled_properties(
        self, data1: Dict[str, Any], data2: Dict[str, Any], strength: float
    ) -> Dict[str, Any]:
        """Create entangled properties from two dream data sets."""
        entangled = {}

        # Entangled emotional intensity
        if "emotional_intensity" in data1 and "emotional_intensity" in data2:
            avg_intensity = (
                data1["emotional_intensity"] + data2["emotional_intensity"]
            ) / 2
            entangled["emotional_intensity"] = avg_intensity

        # Entangled narrative elements
        if "dream_content" in data1 and "dream_content" in data2:
            entangled["dream_content"] = (
                f"[Entangled] {data1['dream_content']} <-> {data2['dream_content']}"
            )

        # Entangled symbolic elements
        if "symbolic_elements" in data1 and "symbolic_elements" in data2:
            entangled["symbolic_elements"] = list(
                set(data1["symbolic_elements"] + data2["symbolic_elements"])
            )

        # Entanglement-specific properties
        entangled["entanglement_strength"] = strength
        entangled["quantum_correlation"] = self._calculate_quantum_correlation(
            data1, data2
        )

        return entangled

    def _calculate_quantum_correlation(
        self, data1: Dict[str, Any], data2: Dict[str, Any]
    ) -> float:
        """Calculate quantum correlation between two dream states."""
        # Simplified quantum correlation based on dream properties
        correlation = 0.0
        comparisons = 0

        for key in ["emotional_intensity", "narrative_coherence", "lucidity_level"]:
            if key in data1 and key in data2:
                correlation += 1.0 - abs(data1[key] - data2[key])
                comparisons += 1

        return correlation / comparisons if comparisons > 0 else 0.0

    def measure_quantum_like_state(self, observable: str = "coherence") -> Dict[str, Any]:
        """
        Perform probabilistic observation on the dream state.

        Args:
            observable: The quantum observable to measure

        Returns:
            Measurement result
        """
        measurement_result = {
            "observable": observable,
            "timestamp": self._get_timestamp(),
            "measurement_count": self.quantum_like_state["measurement_count"] + 1,
        }

        if observable == "coherence":
            # Measure coherence with some uncertainty
            uncertainty = (1.0 - self.config.measurement_precision) * 0.1
            measured_value = self.quantum_like_state["coherence"] + random.uniform(
                -uncertainty, uncertainty
            )
            measurement_result["value"] = max(0.0, min(1.0, measured_value))

        elif observable == "phase":
            # Measure phase
            measurement_result["value"] = self.quantum_like_state["phase"] % (2 * math.pi)

        elif observable == "entanglement":
            # Measure entanglement strength
            if self.quantum_like_state["entanglement_pairs"]:
                avg_strength = sum(
                    self.entangled_dreams[pair_id]["strength"]
                    for pair_id in self.quantum_like_state["entanglement_pairs"]
                ) / len(self.quantum_like_state["entanglement_pairs"])
                measurement_result["value"] = avg_strength
            else:
                measurement_result["value"] = 0.0

        else:
            measurement_result["error"] = f"Unknown observable: {observable}"
            measurement_result["value"] = 0.0

        # Update quantum-like state (measurement affects the system)
        self.quantum_like_state["measurement_count"] += 1
        self._apply_measurement_decoherence()

        return measurement_result

    def _apply_measurement_decoherence(self):
        """Apply decoherence due to measurement."""
        decoherence_factor = 1.0 - self.config.decoherence_rate
        self.quantum_like_state["coherence"] *= decoherence_factor

        # Collapse superposition if coherence drops too low
        if self.quantum_like_state["coherence"] < self.config.coherence_threshold * 0.5:
            self.quantum_like_state["superposition_active"] = False

    def evolve_quantum_like_state(self, time_step: float = 0.1) -> Dict[str, Any]:
        """
        Evolve the quantum-like state over time.

        Args:
            time_step: Time evolution step

        Returns:
            Evolution result
        """
        # Update phase
        self.quantum_like_state["phase"] += (
            2 * math.pi * self.config.quantum_frequency * time_step
        )

        # Apply decoherence
        decoherence_factor = math.exp(-self.config.decoherence_rate * time_step)
        self.quantum_like_state["coherence"] *= decoherence_factor

        # Update amplitude with small fluctuations
        fluctuation = 0.01 * random.uniform(-1, 1)
        self.quantum_like_state["amplitude"] *= 1 + fluctuation
        self.quantum_like_state["amplitude"] = max(
            0.1, min(2.0, self.quantum_like_state["amplitude"])
        )

        # Record coherence history
        self.coherence_history.append(
            {
                "time": self._get_timestamp(),
                "coherence": self.quantum_like_state["coherence"],
                "phase": self.quantum_like_state["phase"],
                "amplitude": self.quantum_like_state["amplitude"],
            }
        )

        # Limit history size
        if len(self.coherence_history) > 1000:
            self.coherence_history = self.coherence_history[-1000:]

        return {
            "evolved_state": self.quantum_like_state.copy(),
            "decoherence_factor": decoherence_factor,
            "time_step": time_step,
        }

    def get_quantum_metrics(self) -> Dict[str, Any]:
        """
        Get current quantum metrics and statistics.

        Returns:
            Dictionary with quantum metrics
        """
        metrics = {
            "current_coherence": self.quantum_like_state["coherence"],
            "current_phase": self.quantum_like_state["phase"],
            "current_amplitude": self.quantum_like_state["amplitude"],
            "superposition_active": self.quantum_like_state["superposition_active"],
            "entanglement_pairs": len(self.quantum_like_state["entanglement_pairs"]),
            "measurement_count": self.quantum_like_state["measurement_count"],
            "superposition_states": len(self.superposition_states),
            "config": {
                "coherence_threshold": self.config.coherence_threshold,
                "entanglement_strength": self.config.entanglement_strength,
                "quantum_frequency": self.config.quantum_frequency,
            },
        }

        # Add coherence statistics if history exists
        if self.coherence_history:
            coherence_values = [entry["coherence"] for entry in self.coherence_history]
            metrics["coherence_stats"] = {
                "mean": sum(coherence_values) / len(coherence_values),
                "min": min(coherence_values),
                "max": max(coherence_values),
                "trend": self._calculate_coherence_trend(),
            }

        return metrics

    def _calculate_coherence_trend(self) -> str:
        """Calculate coherence trend from history."""
        if len(self.coherence_history) < 2:
            return "insufficient_data"

        recent_coherence = [
            entry["coherence"] for entry in self.coherence_history[-10:]
        ]

        if len(recent_coherence) < 2:
            return "stable"

        # Simple trend calculation
        start_avg = sum(recent_coherence[: len(recent_coherence) // 2]) / (
            len(recent_coherence) // 2
        )
        end_avg = sum(recent_coherence[len(recent_coherence) // 2 :]) / (
            len(recent_coherence) - len(recent_coherence) // 2
        )

        if end_avg > start_avg + 0.05:
            return "increasing"
        elif end_avg < start_avg - 0.05:
            return "decreasing"
        else:
            return "stable"

    def reset_quantum_like_state(self) -> None:
        """Reset the quantum-like state to initial conditions."""
        self.quantum_like_state = self._initialize_quantum_like_state()
        self.entangled_dreams.clear()
        self.coherence_history.clear()
        self.superposition_states.clear()

    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        import datetime

        return datetime.datetime.now().isoformat()

    def _apply_measurement_decoherence(self):
        """Apply decoherence due to measurement."""
        decoherence_factor = 1.0 - self.config.decoherence_rate
        self.quantum_like_state["coherence"] *= decoherence_factor

        # Collapse superposition if coherence drops too low
        if self.quantum_like_state["coherence"] < self.config.coherence_threshold * 0.5:
            self.quantum_like_state["superposition_active"] = False
