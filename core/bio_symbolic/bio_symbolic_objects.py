from dataclasses import dataclass, field
from enum import Enum
import time
from typing import Any


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
