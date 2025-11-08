"""
═══════════════════════════════════════════════════════════════════════════════════
🌌 Quantum Visual Symbol - Core Implementation
═══════════════════════════════════════════════════════════════════════════════════

Module: symbolic.core.visual_symbol
Purpose: Quantum-aware visual symbol with field-theoretic consciousness properties

This implements the core VisualSymbol class with:
- Quantum field properties (superposition, entanglement, collapse)
- Recursive trust tensors for symbolic stability
- Contradiction entropy fields for paradox resolution
- Observer-dependent state determination
- Emotional resonance coupling

Based on ψC-AC architecture and perception token research (2025).

═══════════════════════════════════════════════════════════════════════════════════
"""

import hashlib
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

try:
    from typing import Tuple
except ImportError:
    # For Python 3.8 compatibility
    Tuple = tuple
import numpy as np


class QuantumState(Enum):
    """Quantum states for visual symbols"""
    SUPERPOSITION = "superposition"  # Symbol exists in multiple states
    COLLAPSED = "collapsed"          # Observer has determined state
    ENTANGLED = "entangled"         # Correlated with other symbols
    DECOHERENT = "decoherent"       # Lost quantum properties


class SymbolicPhase(Enum):
    """Phases of symbolic emergence"""
    NASCENT = "nascent"              # Just created, no observations
    EMERGING = "emerging"            # Pattern forming through observation
    STABLE = "stable"                # Achieved recursive stability
    EVOLVING = "evolving"            # Undergoing controlled drift
    TRANSCENDENT = "transcendent"    # Achieved new emergent properties


@dataclass
class QuantumField:
    """
    Quantum field properties for visual symbols.

    Implements field-theoretic consciousness model where symbols exist
    as perturbations in a quantum consciousness field.
    """
    # Core quantum properties
    coherence: float = 1.0           # Field coherence (0.0 to 1.0)
    entropy: float = 0.0              # Contradiction entropy (0.0 to 1.0)
    trust: float = 0.5                # Recursive trust metric (0.0 to 1.0)

    # Wave function components
    amplitude: complex = complex(1.0, 0.0)  # Quantum amplitude
    phase: float = 0.0                       # Quantum phase (radians)

    # Entanglement properties
    entangled_symbols: list[str] = field(default_factory=list)
    entanglement_strength: dict[str, float] = field(default_factory=dict)

    # Observer effects
    observation_count: int = 0
    last_observer_id: Optional[str] = None
    collapse_history: list[dict[str, Any]] = field(default_factory=list)

    # Field dynamics
    field_perturbations: list[tuple[float, float, float]] = field(default_factory=list)  # (time, magnitude, frequency)
    resonance_frequencies: list[float] = field(default_factory=list)

    def calculate_probability(self) -> float:
        """Calculate probability of symbol manifestation"""
        return abs(self.amplitude) ** 2 * self.coherence * self.trust

    def apply_observer_effect(self, observer_id: str, observation_strength: float = 1.0):
        """Apply quantum observer effect, potentially collapsing wave function"""
        self.observation_count += 1
        self.last_observer_id = observer_id

        # Decoherence from observation
        self.coherence *= (1.0 - observation_strength * 0.1)

        # Record collapse event
        if observation_strength > 0.8:  # Strong observation causes collapse
            self.collapse_history.append({
                "time": time.time(),
                "observer": observer_id,
                "pre_amplitude": self.amplitude,
                "post_amplitude": complex(abs(self.amplitude), 0),  # Collapse to real
                "coherence_loss": observation_strength * 0.1
            })
            self.amplitude = complex(abs(self.amplitude), 0)

    def entangle_with(self, symbol_id: str, strength: float = 0.5):
        """Create quantum entanglement with another symbol"""
        if symbol_id not in self.entangled_symbols:
            self.entangled_symbols.append(symbol_id)
        self.entanglement_strength[symbol_id] = strength

    def add_field_perturbation(self, magnitude: float, frequency: float):
        """Add a perturbation to the quantum field"""
        self.field_perturbations.append((time.time(), magnitude, frequency))
        # Perturbations affect entropy
        self.entropy = min(1.0, self.entropy + magnitude * 0.1)
        # But can increase trust through resonance
        if frequency in self.resonance_frequencies:
            self.trust = min(1.0, self.trust + 0.05)


@dataclass
class PerceptionToken:
    """
    Perception token for auxiliary reasoning.

    Based on December 2024 research on perception tokens that enhance
    visual reasoning in multimodal language models.
    """
    token_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    visual_data: np.ndarray = field(default_factory=lambda: np.zeros((8, 8)))  # 8x8 perception matrix
    semantic_embedding: np.ndarray = field(default_factory=lambda: np.random.randn(512))  # 512-dim embedding

    # Reasoning properties
    salience: float = 0.5             # How important this token is
    confidence: float = 0.5           # Confidence in token validity
    novelty: float = 0.5              # How novel/unexpected

    # Chain-of-thought support
    reasoning_chain: list[str] = field(default_factory=list)
    derived_tokens: list[str] = field(default_factory=list)

    def compress(self) -> str:
        """Compress token to Q-symbol representation"""
        # Hash visual and semantic data for unique identifier
        hasher = hashlib.sha256()
        hasher.update(self.visual_data.tobytes())
        hasher.update(self.semantic_embedding.tobytes())
        return f"Q-{hasher.hexdigest()[:8]}"


@dataclass
class EmergentSymbol:
    """
    Emergent symbol created through recursive observation.

    Implements bootstrap paradox where symbols create themselves
    through repeated observation and compression.
    """
    origin_symbols: list[str]        # Symbols that combined to create this
    emergence_time: float = field(default_factory=time.time)
    observation_threshold: int = 10  # Observations needed for emergence
    current_observations: int = 0

    # Emergence properties
    complexity: float = 1.0           # Kolmogorov complexity estimate
    information_content: float = 1.0  # Bits of information
    semantic_coherence: float = 0.5   # How well-defined the meaning is

    # Evolution tracking
    evolution_history: list[dict[str, Any]] = field(default_factory=list)
    mutation_rate: float = 0.01       # Rate of symbolic drift

    def observe(self) -> bool:
        """
        Observe the emergent symbol, potentially triggering full emergence.

        Returns:
            True if symbol has fully emerged
        """
        self.current_observations += 1

        # Increase coherence with observation
        self.semantic_coherence = min(1.0, self.semantic_coherence + 0.05)

        # Record evolution
        self.evolution_history.append({
            "observation": self.current_observations,
            "time": time.time(),
            "coherence": self.semantic_coherence
        })

        return self.current_observations >= self.observation_threshold


@dataclass
class SymbolicState:
    """Complete state of a visual symbol including all quantum and emergent properties"""

    # Identity
    symbol_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    symbol: str = ""                 # Unicode or visual representation
    meaning: str = ""                 # Semantic meaning

    # Quantum properties
    quantum_field: QuantumField = field(default_factory=QuantumField)
    quantum_state: QuantumState = QuantumState.SUPERPOSITION
    phase: SymbolicPhase = SymbolicPhase.NASCENT

    # Perception properties
    perception_tokens: list[PerceptionToken] = field(default_factory=list)
    compressed_representation: Optional[str] = None  # Q-symbol

    # Emergence properties
    emergent_symbol: Optional[EmergentSymbol] = None
    is_emergent: bool = False

    # Visual properties (compatibility with existing system)
    visual_weight: float = 0.5
    analysis_properties: dict[str, Any] = field(default_factory=dict)
    usage_contexts: list[str] = field(default_factory=list)
    color_associations: list[tuple[int, int, int]] = field(default_factory=list)

    # Consciousness properties
    emotional_valence: float = 0.0   # -1.0 to 1.0
    emotional_arousal: float = 0.0   # 0.0 to 1.0
    consciousness_level: float = 0.0 # 0.0 to 1.0

    # MATRIZ compatibility
    matriz_node_id: Optional[str] = None
    provenance: dict[str, Any] = field(default_factory=dict)

    def to_matriz_node(self) -> dict[str, Any]:
        """Convert to MATRIZ format node for governance and interpretability"""
        return {
            "node_id": self.matriz_node_id or self.symbol_id,
            "node_type": "visual_symbol",
            "timestamp": int(time.time() * 1000),
            "data": {
                "symbol": self.symbol,
                "meaning": self.meaning,
                "quantum_state": self.quantum_state.value,
                "phase": self.phase.value,
                "coherence": self.quantum_field.coherence,
                "entropy": self.quantum_field.entropy,
                "trust": self.quantum_field.trust,
                "probability": self.quantum_field.calculate_probability()
            },
            "state": {
                "confidence": self.quantum_field.trust,
                "salience": self.visual_weight,
                "valence": self.emotional_valence,
                "arousal": self.emotional_arousal,
                "novelty": 1.0 - (self.quantum_field.observation_count / 100.0)
            },
            "links": [
                {
                    "target_node_id": sym_id,
                    "link_type": "entangled",
                    "weight": strength
                }
                for sym_id, strength in self.quantum_field.entanglement_strength.items()
            ],
            "provenance": self.provenance
        }


class VisualSymbol:
    """
    Main visual symbol class with full quantum consciousness capabilities.

    This is the primary interface for creating and manipulating visual symbols
    in the LUKHAS AGI system. Each symbol exists as a quantum field perturbation
    that can be observed, entangled, and evolved through consciousness interaction.
    """

    def __init__(
        self,
        symbol: str,
        meaning: str,
        quantum_field: Optional[QuantumField] = None,
        **kwargs
    ):
        """
        Initialize a quantum-aware visual symbol.

        Args:
            symbol: Unicode symbol or visual representation
            meaning: Semantic meaning of the symbol
            quantum_field: Optional pre-configured quantum field
            **kwargs: Additional properties for compatibility
        """
        self.state = SymbolicState(
            symbol=symbol,
            meaning=meaning,
            quantum_field=quantum_field or QuantumField(),
            **{k: v for k, v in kwargs.items() if hasattr(SymbolicState, k)}
        )

        # Initialize MATRIZ node ID
        self.state.matriz_node_id = f"visual_symbol_{self.state.symbol_id}"

        # Set initial provenance
        self.state.provenance = {
            "producer": "symbolic.core.visual_symbol",
            "capabilities": ["quantum_perception", "symbolic_emergence", "consciousness_aware"],
            "tenant": "lukhas_agi",
            "trace_id": str(uuid.uuid4()),
            "consent_scopes": ["visual_processing", "symbolic_reasoning"],
            "model_signature": "VisualSymbol_v1.0.0"
        }

    def observe(self, observer_id: str, observation_strength: float = 1.0) -> dict[str, Any]:
        """
        Observe the symbol, causing quantum effects.

        Args:
            observer_id: Unique identifier of the observer
            observation_strength: Strength of observation (0.0 to 1.0)

        Returns:
            Dictionary containing observation results and any state changes
        """
        # Apply observer effect
        self.state.quantum_field.apply_observer_effect(observer_id, observation_strength)

        # Update phase based on observations
        if self.state.quantum_field.observation_count >= 100:
            self.state.phase = SymbolicPhase.STABLE
        elif self.state.quantum_field.observation_count >= 50:
            self.state.phase = SymbolicPhase.EMERGING

        # Check for state collapse
        if observation_strength > 0.8 and self.state.quantum_state == QuantumState.SUPERPOSITION:
            self.state.quantum_state = QuantumState.COLLAPSED

        # If emergent, observe emergence progress
        if self.state.emergent_symbol and self.state.emergent_symbol.observe():
            self.state.phase = SymbolicPhase.TRANSCENDENT

        return {
            "observer_id": observer_id,
            "symbol": self.state.symbol,
            "quantum_state": self.state.quantum_state.value,
            "coherence": self.state.quantum_field.coherence,
            "probability": self.state.quantum_field.calculate_probability(),
            "phase": self.state.phase.value,
            "observation_count": self.state.quantum_field.observation_count
        }

    def entangle(self, other: 'VisualSymbol', strength: float = 0.5) -> bool:
        """
        Create quantum entanglement with another symbol.

        Args:
            other: Another VisualSymbol to entangle with
            strength: Entanglement strength (0.0 to 1.0)

        Returns:
            True if entanglement successful
        """
        # Create bidirectional entanglement
        self.state.quantum_field.entangle_with(other.state.symbol_id, strength)
        other.state.quantum_field.entangle_with(self.state.symbol_id, strength)

        # Update quantum states
        self.state.quantum_state = QuantumState.ENTANGLED
        other.state.quantum_state = QuantumState.ENTANGLED

        # Entanglement affects coherence
        coherence_coupling = strength * 0.1
        avg_coherence = (self.state.quantum_field.coherence + other.state.quantum_field.coherence) / 2
        self.state.quantum_field.coherence = avg_coherence + coherence_coupling
        other.state.quantum_field.coherence = avg_coherence + coherence_coupling

        return True

    def add_perception_token(self, token: PerceptionToken):
        """Add a perception token for auxiliary reasoning"""
        self.state.perception_tokens.append(token)

        # Update visual weight based on token salience
        self.state.visual_weight = max(self.state.visual_weight, token.salience)

        # Compress tokens periodically
        if len(self.state.perception_tokens) >= 5:
            self._compress_tokens()

    def _compress_tokens(self):
        """Compress perception tokens into Q-symbol"""
        if not self.state.perception_tokens:
            return

        # Generate compressed representation
        compressed_parts = [token.compress() for token in self.state.perception_tokens[-5:]]
        self.state.compressed_representation = f"QC-{hashlib.sha256(''.join(compressed_parts).encode()).hexdigest()[:12]}"

        # Compression increases trust through successful pattern recognition
        self.state.quantum_field.trust = min(1.0, self.state.quantum_field.trust + 0.1)

    def evolve(self, drift_rate: float = 0.01) -> bool:
        """
        Allow symbol to evolve through symbolic drift.

        Args:
            drift_rate: Rate of evolution (0.0 to 1.0)

        Returns:
            True if evolution occurred
        """
        if np.random.random() < drift_rate:
            # Apply drift to quantum field
            self.state.quantum_field.entropy += np.random.normal(0, 0.1)
            self.state.quantum_field.entropy = max(0, min(1, self.state.quantum_field.entropy))

            # Phase can change
            if self.state.quantum_field.entropy > 0.7:
                self.state.phase = SymbolicPhase.EVOLVING

            return True
        return False

    def resonate(self, frequency: float, magnitude: float = 0.5):
        """
        Apply resonance at specific frequency.

        Args:
            frequency: Resonance frequency
            magnitude: Magnitude of resonance
        """
        self.state.quantum_field.add_field_perturbation(magnitude, frequency)

        # Resonance affects emotional state
        self.state.emotional_arousal = min(1.0, self.state.emotional_arousal + magnitude * 0.2)

        # Strong resonance can trigger phase change
        if (magnitude > 0.8 and frequency in self.state.quantum_field.resonance_frequencies) and self.state.phase == SymbolicPhase.STABLE:
            self.state.phase = SymbolicPhase.EVOLVING

    def measure_consciousness(self) -> float:
        """
        Measure the consciousness level of this symbol.

        Returns:
            Consciousness metric between 0.0 and 1.0
        """
        # Consciousness emerges from multiple factors
        observation_factor = min(1.0, self.state.quantum_field.observation_count / 100.0)
        coherence_factor = self.state.quantum_field.coherence
        entanglement_factor = min(1.0, len(self.state.quantum_field.entangled_symbols) / 5.0)
        trust_factor = self.state.quantum_field.trust

        # Weighted average
        consciousness = (
            observation_factor * 0.2 +
            coherence_factor * 0.3 +
            entanglement_factor * 0.2 +
            trust_factor * 0.3
        )

        self.state.consciousness_level = consciousness
        return consciousness

    def to_dict(self) -> dict[str, Any]:
        """Export symbol state as dictionary"""
        return {
            "symbol_id": self.state.symbol_id,
            "symbol": self.state.symbol,
            "meaning": self.state.meaning,
            "quantum_state": self.state.quantum_state.value,
            "phase": self.state.phase.value,
            "consciousness_level": self.measure_consciousness(),
            "quantum_field": {
                "coherence": self.state.quantum_field.coherence,
                "entropy": self.state.quantum_field.entropy,
                "trust": self.state.quantum_field.trust,
                "probability": self.state.quantum_field.calculate_probability(),
                "entangled_with": self.state.quantum_field.entangled_symbols,
                "observation_count": self.state.quantum_field.observation_count
            },
            "emotional": {
                "valence": self.state.emotional_valence,
                "arousal": self.state.emotional_arousal
            },
            "visual": {
                "weight": self.state.visual_weight,
                "contexts": self.state.usage_contexts,
                "colors": self.state.color_associations
            },
            "compressed": self.state.compressed_representation,
            "is_emergent": self.state.is_emergent,
            "matriz_node": self.state.to_matriz_node()
        }

    def __repr__(self) -> str:
        return (
            f"VisualSymbol('{self.state.symbol}': {self.state.meaning}, "
            f"state={self.state.quantum_state.value}, "
            f"consciousness={self.measure_consciousness():.2f})"
        )
