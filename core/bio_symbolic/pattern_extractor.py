import time
from typing import List

from core.matriz_consciousness_signals import BioSymbolicData, ConsciousnessSignal

from .bio_symbolic_objects import BioPatternType, BioSymbolicPattern


class PatternExtractor:
    def extract_bio_patterns(
        self, signal: ConsciousnessSignal, bio_data: BioSymbolicData
    ) -> List[BioSymbolicPattern]:
        """Extract biological patterns from consciousness signal and bio data"""

        patterns = []

        # Neural oscillation pattern
        if bio_data.oscillation_frequency > 0:
            pattern = BioSymbolicPattern(
                pattern_id=f"neural_osc_{signal.signal_id}",
                bio_pattern_type=BioPatternType.NEURAL_OSCILLATION,
                symbolic_representation="vector_space",
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
                symbolic_representation="geometric_manifold",
                frequency_components=[1.0],  # Slow membrane dynamics
                amplitude_envelope=[bio_data.membrane_permeability],
                phase_relationships={"membrane": 0.25},
                coherence_matrix=[[bio_data.membrane_permeability]],
                entropy_measures={"membrane_entropy": bio_data.entropy_delta * 0.5},
                adaptation_coefficients={"permeability": bio_data.membrane_permeability},
                temporal_evolution=[
                    {"t": time.time(), "permeability": bio_data.membrane_permeability}
                ],
                resonance_fingerprint=f"membrane_{bio_data.membrane_permeability:.3f}",
            )
            patterns.append(pattern)

        # Metabolic flow pattern (based on temporal decay)
        if hasattr(bio_data, "temporal_decay"):
            metabolism_rate = 1.0 - bio_data.temporal_decay
            pattern = BioSymbolicPattern(
                pattern_id=f"metabolic_{signal.signal_id}",
                bio_pattern_type=BioPatternType.METABOLIC_FLOW,
                symbolic_representation="graph_topology",
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
