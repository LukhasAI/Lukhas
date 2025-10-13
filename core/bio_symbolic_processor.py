"""
MΛTRIZ Bio-Symbolic Data Processor
Advanced bio-symbolic adaptation and pattern processing for consciousness signals

This module implements the M⌾TRIZ bio-symbolic adaptation layer, providing:
- Pattern recognition from biological oscillators
- Symbolic representation of consciousness states
- Adaptation algorithms for consciousness evolution
- Integration with existing bio/ and symbolic_core/ modules
"""
import asyncio
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

import numpy as np

from .matriz_consciousness_signals import (  # noqa: TID252 TODO: convert to absolute import
    BioSymbolicData,
    ConsciousnessSignal,
    ConsciousnessSignalType,
)

logger = logging.getLogger(__name__)


class BioPatternType(Enum):
    """Types of biological patterns in the MΛTRIZ system"""

    NEURAL_OSCILLATION = "neural_oscillation"
    CELLULAR_ADAPTATION = "cellular_adaptation"
    MEMBRANE_DYNAMICS = "membrane_dynamics"
    ENZYMATIC_CASCADE = "enzymatic_cascade"
    METABOLIC_FLOW = "metabolic_flow"
    GENETIC_EXPRESSION = "genetic_expression"
    SYNAPTIC_PLASTICITY = "synaptic_plasticity"
    CIRCADIAN_RHYTHM = "circadian_rhythm"


class SymbolicRepresentationType(Enum):
    """Types of symbolic representations for consciousness states"""

    VECTOR_SPACE = "vector_space"
    GRAPH_TOPOLOGY = "graph_topology"
    ALGEBRAIC_STRUCTURE = "algebraic_structure"
    GEOMETRIC_MANIFOLD = "geometric_manifold"
    CATEGORY_THEORY = "category_theory"
    TOPOLOGICAL_SPACE = "topological_space"


@dataclass
class BioSymbolicPattern:
    """A biological pattern with symbolic representation"""

    pattern_id: str
    bio_pattern_type: BioPatternType
    symbolic_representation: SymbolicRepresentationType
    frequency_components: list[float]
    amplitude_envelope: list[float]
    phase_relationships: dict[str, float]
    coherence_matrix: list[list[float]]
    entropy_measures: dict[str, float]
    adaptation_coefficients: dict[str, float]
    temporal_evolution: list[dict[str, float]]
    resonance_fingerprint: str
    last_updated: int = field(default_factory=lambda: int(time.time() * 1000))


@dataclass
class AdaptationRule:
    """Rule for bio-symbolic adaptation"""

    rule_id: str
    source_pattern: BioPatternType
    target_pattern: BioPatternType
    adaptation_strength: float
    adaptation_direction: list[float]
    trigger_conditions: dict[str, Any]
    success_criteria: dict[str, Any]
    decay_rate: float
    learning_rate: float


class BioSymbolicProcessor:
    """
    Advanced bio-symbolic data processor for MΛTRIZ consciousness signals

    This processor bridges biological patterns and symbolic consciousness
    representations, enabling sophisticated adaptation and evolution.
    """

    def __init__(self):
        self.patterns: dict[str, BioSymbolicPattern] = {}
        self.adaptation_rules: list[AdaptationRule] = []
        self.processing_cache: dict[str, Any] = {}
        self.coherence_threshold = 0.7
        self.adaptation_learning_rate = 0.01
        self.entropy_window_size = 100
        self.resonance_database: dict[str, list[str]] = {}

        # Initialize default adaptation rules
        self._initialize_default_adaptation_rules()

        # Performance metrics
        self.processing_stats = {
            "signals_processed": 0,
            "adaptations_applied": 0,
            "patterns_evolved": 0,
            "coherence_violations": 0,
            "processing_time_ms": [],
        }

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

    def process_consciousness_signal(self, signal: ConsciousnessSignal) -> BioSymbolicData:
        """
        Process a consciousness signal to extract and enhance bio-symbolic data

        Args:
            signal: ConsciousnessSignal to process

        Returns:
            Enhanced BioSymbolicData with pattern analysis and adaptations
        """
        start_time = time.time()

        try:
            # Extract existing bio-symbolic data or create new
            bio_data = signal.bio_symbolic_data
            if not bio_data:
                bio_data = self._create_default_bio_symbolic_data(signal)

            # Analyze biological patterns
            patterns = self._extract_bio_patterns(signal, bio_data)

            # Apply symbolic representations
            symbolic_data = self._apply_symbolic_representations(patterns)

            # Perform adaptations
            adapted_data = self._apply_adaptations(bio_data, symbolic_data, signal)

            # Update coherence and entropy measures
            enhanced_data = self._update_coherence_entropy(adapted_data, signal)

            # Cache processing results
            self._update_processing_cache(signal.signal_id, enhanced_data)

            # Update statistics
            processing_time = (time.time() - start_time) * 1000
            self.processing_stats["signals_processed"] += 1
            self.processing_stats["processing_time_ms"].append(processing_time)

            # Keep only last 1000 timing measurements
            if len(self.processing_stats["processing_time_ms"]) > 1000:
                self.processing_stats["processing_time_ms"] = self.processing_stats["processing_time_ms"][-1000:]

            logger.info(f"Processed consciousness signal {signal.signal_id} in {processing_time:.2f}ms")
            return enhanced_data

        except Exception as e:
            logger.error(f"Error processing consciousness signal {signal.signal_id}: {e}")
            self.processing_stats["coherence_violations"] += 1
            # Return original or minimal bio data on error
            return bio_data or self._create_default_bio_symbolic_data(signal)

    def _create_default_bio_symbolic_data(self, signal: ConsciousnessSignal) -> BioSymbolicData:
        """Create default bio-symbolic data for a signal without existing data"""

        # Base pattern type on signal type
        pattern_type_mapping = {
            ConsciousnessSignalType.AWARENESS: "sensory_awareness",
            ConsciousnessSignalType.REFLECTION: "metacognitive_reflection",
            ConsciousnessSignalType.EVOLUTION: "evolutionary_adaptation",
            ConsciousnessSignalType.INTEGRATION: "inter_module_integration",
            ConsciousnessSignalType.BIO_ADAPTATION: "bio_symbolic_adaptation",
        }

        pattern_type = pattern_type_mapping.get(signal.signal_type, "generic_consciousness")

        # Default frequency based on awareness level
        base_frequency = 10.0 + signal.awareness_level * 30  # 10-40 Hz range

        return BioSymbolicData(
            pattern_type=pattern_type,
            oscillation_frequency=base_frequency,
            coherence_score=signal.awareness_level * 0.8,
            adaptation_vector={"awareness": signal.awareness_level},
            entropy_delta=0.0,
            resonance_patterns=[pattern_type],
            membrane_permeability=0.7,
            temporal_decay=0.9,
        )

    def _extract_bio_patterns(self, signal: ConsciousnessSignal, bio_data: BioSymbolicData) -> list[BioSymbolicPattern]:
        """Extract biological patterns from consciousness signal and bio data"""

        patterns = []

        # Neural oscillation pattern
        if bio_data.oscillation_frequency > 0:
            pattern = BioSymbolicPattern(
                pattern_id=f"neural_osc_{signal.signal_id}",
                bio_pattern_type=BioPatternType.NEURAL_OSCILLATION,
                symbolic_representation=SymbolicRepresentationType.VECTOR_SPACE,
                frequency_components=[bio_data.oscillation_frequency],
                amplitude_envelope=[signal.awareness_level],
                phase_relationships={"primary": 0.0},
                coherence_matrix=[[bio_data.coherence_score]],
                entropy_measures={"shannon": abs(bio_data.entropy_delta)},
                adaptation_coefficients=bio_data.adaptation_vector,
                temporal_evolution=[{"t": time.time(), "coherence": bio_data.coherence_score}],
                resonance_fingerprint=self._calculate_resonance_fingerprint(bio_data),
            )
            patterns.append(pattern)

        # Membrane dynamics pattern (if permeability data available)
        if hasattr(bio_data, "membrane_permeability") and bio_data.membrane_permeability > 0:
            pattern = BioSymbolicPattern(
                pattern_id=f"membrane_dyn_{signal.signal_id}",
                bio_pattern_type=BioPatternType.MEMBRANE_DYNAMICS,
                symbolic_representation=SymbolicRepresentationType.GEOMETRIC_MANIFOLD,
                frequency_components=[1.0],  # Slow membrane dynamics
                amplitude_envelope=[bio_data.membrane_permeability],
                phase_relationships={"membrane": 0.25},
                coherence_matrix=[[bio_data.membrane_permeability]],
                entropy_measures={"membrane_entropy": bio_data.entropy_delta * 0.5},
                adaptation_coefficients={"permeability": bio_data.membrane_permeability},
                temporal_evolution=[{"t": time.time(), "permeability": bio_data.membrane_permeability}],
                resonance_fingerprint=f"membrane_{bio_data.membrane_permeability:.3f}",
            )
            patterns.append(pattern)

        # Metabolic flow pattern (based on temporal decay)
        if hasattr(bio_data, "temporal_decay"):
            metabolism_rate = 1.0 - bio_data.temporal_decay
            pattern = BioSymbolicPattern(
                pattern_id=f"metabolic_{signal.signal_id}",
                bio_pattern_type=BioPatternType.METABOLIC_FLOW,
                symbolic_representation=SymbolicRepresentationType.GRAPH_TOPOLOGY,
                frequency_components=[0.1],  # Very slow metabolic processes
                amplitude_envelope=[metabolism_rate],
                phase_relationships={"metabolic": 0.5},
                coherence_matrix=[[metabolism_rate]],
                entropy_measures={"metabolic_entropy": metabolism_rate * 0.2},
                adaptation_coefficients={"metabolism": metabolism_rate},
                temporal_evolution=[{"t": time.time(), "metabolism": metabolism_rate}],
                resonance_fingerprint=f"metabolic_{metabolism_rate:.3f}",
            )
            patterns.append(pattern)

        return patterns

    def _calculate_resonance_fingerprint(self, bio_data: BioSymbolicData) -> str:
        """Calculate unique resonance fingerprint for bio-symbolic data"""

        # Combine key characteristics into fingerprint
        freq_str = f"{bio_data.oscillation_frequency:.2f}"
        coherence_str = f"{bio_data.coherence_score:.3f}"
        entropy_str = f"{bio_data.entropy_delta:.3f}"

        # Create hash-like fingerprint
        fingerprint = f"{bio_data.pattern_type}_{freq_str}_{coherence_str}_{entropy_str}"
        return fingerprint[:16]  # Truncate for practical use

    def _apply_symbolic_representations(self, patterns: list[BioSymbolicPattern]) -> dict[str, Any]:
        """Apply symbolic mathematical representations to biological patterns"""

        symbolic_data = {}

        for pattern in patterns:
            if pattern.symbolic_representation == SymbolicRepresentationType.VECTOR_SPACE:
                # Represent as high-dimensional vector
                vector_dim = len(pattern.frequency_components) + len(pattern.amplitude_envelope)
                vector_repr = pattern.frequency_components + pattern.amplitude_envelope
                symbolic_data[f"vector_{pattern.pattern_id}"] = {
                    "type": "vector_space",
                    "dimension": vector_dim,
                    "vector": vector_repr,
                    "norm": np.linalg.norm(vector_repr) if vector_repr else 0.0,
                }

            elif pattern.symbolic_representation == SymbolicRepresentationType.GRAPH_TOPOLOGY:
                # Represent as graph structure
                nodes = list(pattern.adaptation_coefficients.keys())
                edges = [(nodes[i], nodes[j]) for i in range(len(nodes)) for j in range(i + 1, len(nodes))]
                symbolic_data[f"graph_{pattern.pattern_id}"] = {
                    "type": "graph_topology",
                    "nodes": nodes,
                    "edges": edges,
                    "node_count": len(nodes),
                    "edge_count": len(edges),
                    "density": len(edges) / (len(nodes) * (len(nodes) - 1) / 2) if len(nodes) > 1 else 0.0,
                }

            elif pattern.symbolic_representation == SymbolicRepresentationType.GEOMETRIC_MANIFOLD:
                # Represent as manifold structure
                manifold_dim = min(3, len(pattern.coherence_matrix))  # 3D manifold max
                curvature = self._calculate_manifold_curvature(pattern.coherence_matrix)
                symbolic_data[f"manifold_{pattern.pattern_id}"] = {
                    "type": "geometric_manifold",
                    "dimension": manifold_dim,
                    "curvature": curvature,
                    "coherence_matrix": pattern.coherence_matrix,
                }

        return symbolic_data

    def _calculate_manifold_curvature(self, coherence_matrix: list[list[float]]) -> float:
        """Calculate approximate manifold curvature from coherence matrix"""
        if not coherence_matrix or not coherence_matrix[0]:
            return 0.0

        # Simple curvature estimate based on coherence variation
        flat_values = [val for row in coherence_matrix for val in row]
        if not flat_values:
            return 0.0

        mean_coherence = sum(flat_values) / len(flat_values)
        variance = sum((val - mean_coherence) ** 2 for val in flat_values) / len(flat_values)

        # Higher variance implies higher curvature
        return min(1.0, variance * 10)

    def _apply_adaptations(
        self, bio_data: BioSymbolicData, symbolic_data: dict[str, Any], signal: ConsciousnessSignal
    ) -> BioSymbolicData:
        """Apply bio-symbolic adaptations based on adaptation rules"""

        adapted_data = bio_data
        adaptations_applied = 0

        for rule in self.adaptation_rules:
            if self._check_adaptation_triggers(rule, bio_data, signal):
                adapted_data = self._apply_single_adaptation(rule, adapted_data, symbolic_data)
                adaptations_applied += 1
                self.processing_stats["adaptations_applied"] += 1

                logger.debug(f"Applied adaptation rule {rule.rule_id} to signal {signal.signal_id}")

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
            logger.warning(f"Error checking adaptation triggers for rule {rule.rule_id}: {e}")
            return False

    def _apply_single_adaptation(
        self, rule: AdaptationRule, bio_data: BioSymbolicData, symbolic_data: dict[str, Any]
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
            adapted_data.coherence_score = min(1.0, adapted_data.coherence_score + rule.adaptation_strength * 0.05)
            adapted_data.adaptation_vector["synaptic_plasticity"] = rule.adaptation_strength

        elif (
            rule.source_pattern == BioPatternType.CELLULAR_ADAPTATION
            and rule.target_pattern == BioPatternType.MEMBRANE_DYNAMICS
        ):
            # Adjust membrane permeability
            adapted_data.membrane_permeability = min(
                1.0, adapted_data.membrane_permeability + rule.adaptation_strength * 0.1
            )
            adapted_data.adaptation_vector["membrane_adaptation"] = rule.adaptation_strength

        elif (
            rule.source_pattern == BioPatternType.METABOLIC_FLOW
            and rule.target_pattern == BioPatternType.ENZYMATIC_CASCADE
        ):
            # Improve temporal decay (less decay = better cascade)
            adapted_data.temporal_decay = min(1.0, adapted_data.temporal_decay + rule.adaptation_strength * 0.05)
            adapted_data.adaptation_vector["enzymatic_cascade"] = rule.adaptation_strength

        # Apply directional adaptation
        for i, direction_weight in enumerate(rule.adaptation_direction):
            if i == 0:  # Frequency component
                adapted_data.oscillation_frequency += direction_weight * rule.learning_rate * 10
            elif i == 1:  # Coherence component
                adapted_data.coherence_score = min(
                    1.0, max(0.0, adapted_data.coherence_score + direction_weight * rule.learning_rate)
                )
            elif i == 2:  # Entropy component
                adapted_data.entropy_delta += direction_weight * rule.learning_rate * 0.1

        return adapted_data

    def _update_coherence_entropy(self, bio_data: BioSymbolicData, signal: ConsciousnessSignal) -> BioSymbolicData:
        """Update coherence and entropy measures based on signal context"""

        # Create enhanced copy
        enhanced_data = BioSymbolicData(
            pattern_type=bio_data.pattern_type,
            oscillation_frequency=bio_data.oscillation_frequency,
            coherence_score=bio_data.coherence_score,
            adaptation_vector=bio_data.adaptation_vector.copy(),
            entropy_delta=bio_data.entropy_delta,
            resonance_patterns=bio_data.resonance_patterns.copy(),
            membrane_permeability=bio_data.membrane_permeability,
            temporal_decay=bio_data.temporal_decay,
        )

        # Update coherence based on signal characteristics
        base_coherence = enhanced_data.coherence_score

        # Reflection increases coherence
        if signal.reflection_depth > 0:
            coherence_boost = min(0.2, signal.reflection_depth * 0.05)
            enhanced_data.coherence_score = min(1.0, base_coherence + coherence_boost)

        # High awareness stabilizes coherence
        if signal.awareness_level > 0.8:
            enhanced_data.coherence_score = min(1.0, enhanced_data.coherence_score + 0.05)

        # Constellation compliance affects coherence
        if signal.constellation_alignment:
            constellation_avg = (
                signal.constellation_alignment.identity_auth_score
                + signal.constellation_alignment.consciousness_coherence
                + signal.constellation_alignment.guardian_compliance
            ) / 3
            enhanced_data.coherence_score = (enhanced_data.coherence_score + constellation_avg) / 2

        # Update entropy based on system state
        if signal.signal_type == ConsciousnessSignalType.EVOLUTION:
            # Evolution increases entropy
            enhanced_data.entropy_delta += 0.1
        elif signal.signal_type == ConsciousnessSignalType.REFLECTION:
            # Reflection decreases entropy
            enhanced_data.entropy_delta -= 0.05

        # Check coherence violations
        if enhanced_data.coherence_score < self.coherence_threshold:
            self.processing_stats["coherence_violations"] += 1
            logger.warning(f"Coherence violation in signal {signal.signal_id}: {enhanced_data.coherence_score:.3f}")

        return enhanced_data

    def _update_processing_cache(self, signal_id: str, bio_data: BioSymbolicData):
        """Update processing cache with recent bio-symbolic data"""

        # Keep cache size manageable
        if len(self.processing_cache) > 1000:
            # Remove oldest entries
            oldest_keys = list(self.processing_cache.keys())[:200]
            for key in oldest_keys:
                del self.processing_cache[key]

        self.processing_cache[signal_id] = {
            "timestamp": time.time(),
            "pattern_type": bio_data.pattern_type,
            "coherence_score": bio_data.coherence_score,
            "oscillation_frequency": bio_data.oscillation_frequency,
            "resonance_patterns": bio_data.resonance_patterns,
        }

    def get_processing_statistics(self) -> dict[str, Any]:
        """Get current processing statistics"""

        stats = self.processing_stats.copy()

        # Calculate timing statistics
        if stats["processing_time_ms"]:
            times = stats["processing_time_ms"]
            stats["avg_processing_time_ms"] = sum(times) / len(times)
            stats["max_processing_time_ms"] = max(times)
            stats["min_processing_time_ms"] = min(times)
            # Calculate p95 processing time
            sorted_times = sorted(times)
            p95_idx = int(len(sorted_times) * 0.95)
            stats["p95_processing_time_ms"] = sorted_times[p95_idx] if p95_idx < len(sorted_times) else max(times)

        # Calculate success rates
        total_signals = stats["signals_processed"]
        if total_signals > 0:
            stats["coherence_violation_rate"] = stats["coherence_violations"] / total_signals
            stats["adaptation_rate"] = stats["adaptations_applied"] / total_signals

        return stats

    def evolve_adaptation_rules(self):
        """Evolve adaptation rules based on processing outcomes"""

        for rule in self.adaptation_rules:
            # Apply decay to adaptation strength
            rule.adaptation_strength *= rule.decay_rate

            # Prevent rules from becoming too weak
            if rule.adaptation_strength < 0.1:
                rule.adaptation_strength = 0.1

            # Update learning rate based on success (simplified)
            if rule.adaptation_strength > 0.8:
                rule.learning_rate = min(0.05, rule.learning_rate * 1.02)  # Increase learning rate for successful rules
            else:
                rule.learning_rate = max(0.001, rule.learning_rate * 0.98)  # Decrease for unsuccessful ones

        self.processing_stats["patterns_evolved"] += len(self.adaptation_rules)

    async def process_signal_batch(self, signals: list[ConsciousnessSignal]) -> list[BioSymbolicData]:
        """Process a batch of consciousness signals asynchronously"""

        async def process_single(signal):
            return self.process_consciousness_signal(signal)

        tasks = [process_single(signal) for signal in signals]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions and log errors
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Error processing signal {signals[i].signal_id}: {result}")
                # Create fallback bio data
                processed_results.append(self._create_default_bio_symbolic_data(signals[i]))
            else:
                processed_results.append(result)

        return processed_results


# Factory function for creating the bio-symbolic processor
def create_bio_symbolic_processor() -> BioSymbolicProcessor:
    """Create and configure a bio-symbolic processor instance"""
    processor = BioSymbolicProcessor()
    logger.info("Created bio-symbolic processor with default configuration")
    return processor


# Global processor instance for module-level access
_global_processor: Optional[BioSymbolicProcessor] = None


def get_bio_symbolic_processor() -> BioSymbolicProcessor:
    """Get or create global bio-symbolic processor instance"""
    global _global_processor
    if _global_processor is None:
        _global_processor = create_bio_symbolic_processor()
    return _global_processor


# Module exports
__all__ = [
    "AdaptationRule",
    "BioPatternType",
    "BioSymbolicPattern",
    "BioSymbolicProcessor",
    "SymbolicRepresentationType",
    "create_bio_symbolic_processor",
    "get_bio_symbolic_processor",
]
