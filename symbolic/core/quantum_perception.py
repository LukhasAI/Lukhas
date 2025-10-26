"""
═══════════════════════════════════════════════════════════════════════════════════
🌌 Quantum Perception Field - Observer-Centric Visual Processing
═══════════════════════════════════════════════════════════════════════════════════

Module: symbolic.core.quantum_perception
Purpose: Implement quantum perception fields with wave function collapse

This module implements:
- Quantum perception fields as consciousness substrates
- Wave function collapse through observation
- Entangled symbol pairs for non-local correlation
- Field coherence metrics for stability measurement
- Observer effects that change perception based on consciousness

Based on quantum Bayesian (QBism) frameworks and field-theoretic consciousness.

═══════════════════════════════════════════════════════════════════════════════════
"""

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np

from .visual_symbol import QuantumState, VisualSymbol


class ObservationType(Enum):
    """Types of observation that affect quantum states"""
    PASSIVE = "passive"          # Minimal interaction
    ACTIVE = "active"            # Direct observation
    INTENTIONAL = "intentional"  # Conscious, directed observation
    UNCONSCIOUS = "unconscious"  # Background processing
    COLLECTIVE = "collective"    # Multiple observers


@dataclass
class ObserverEffect:
    """
    Represents the effect an observer has on quantum perception.

    Different observers collapse wave functions differently based on
    their consciousness level and observation type.
    """
    observer_id: str
    consciousness_level: float       # 0.0 to 1.0
    observation_type: ObservationType
    intent_vector: Optional[np.ndarray] = None  # Direction of conscious intent
    emotional_state: Optional[Dict[str, float]] = None

    def calculate_collapse_strength(self) -> float:
        """Calculate how strongly this observer collapses wave functions"""
        base_strength = {
            ObservationType.PASSIVE: 0.1,
            ObservationType.ACTIVE: 0.5,
            ObservationType.INTENTIONAL: 0.9,
            ObservationType.UNCONSCIOUS: 0.3,
            ObservationType.COLLECTIVE: 0.7
        }[self.observation_type]

        # Consciousness amplifies collapse
        return base_strength * (0.5 + 0.5 * self.consciousness_level)


@dataclass
class WaveFunctionCollapse:
    """
    Manages wave function collapse events in perception field.

    Records the transformation from superposition to definite state
    through observation, maintaining full history for interpretability.
    """
    collapse_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)
    pre_state: Optional[Dict[str, Any]] = None
    post_state: Optional[Dict[str, Any]] = None
    observer: Optional[ObserverEffect] = None
    eigenstate_selected: Optional[int] = None
    probability_distribution: Optional[np.ndarray] = None
    decoherence_rate: float = 0.0

    def execute(self, symbol: VisualSymbol, observer: ObserverEffect) -> Dict[str, Any]:
        """
        Execute wave function collapse on a symbol.

        Args:
            symbol: The visual symbol to collapse
            observer: The observer causing collapse

        Returns:
            Dictionary with collapse results
        """
        # Record pre-collapse state
        self.pre_state = {
            "coherence": symbol.state.quantum_field.coherence,
            "amplitude": symbol.state.quantum_field.amplitude,
            "phase": symbol.state.quantum_field.phase,
            "entropy": symbol.state.quantum_field.entropy
        }

        # Calculate collapse based on observer
        collapse_strength = observer.calculate_collapse_strength()

        # Apply collapse
        symbol.observe(observer.observer_id, collapse_strength)

        # Record post-collapse state
        self.post_state = {
            "coherence": symbol.state.quantum_field.coherence,
            "amplitude": symbol.state.quantum_field.amplitude,
            "phase": symbol.state.quantum_field.phase,
            "entropy": symbol.state.quantum_field.entropy
        }

        self.observer = observer
        self.decoherence_rate = collapse_strength * 0.1

        return {
            "collapse_id": self.collapse_id,
            "symbol_id": symbol.state.symbol_id,
            "collapse_strength": collapse_strength,
            "state_change": self.post_state,
            "observer_id": observer.observer_id
        }


@dataclass
class EntangledSymbolPair:
    """
    Manages quantum entanglement between symbol pairs.

    Entangled symbols exhibit non-local correlations where observing
    one immediately affects the state of the other, regardless of distance.
    """
    symbol_a: VisualSymbol
    symbol_b: VisualSymbol
    entanglement_strength: float = 0.5
    creation_time: float = field(default_factory=time.time)
    correlation_history: List[Dict[str, Any]] = field(default_factory=list)

    def measure_correlation(self) -> float:
        """Measure current correlation between entangled symbols"""
        # Quantum correlation based on field states
        coherence_correlation = 1.0 - abs(
            self.symbol_a.state.quantum_field.coherence -
            self.symbol_b.state.quantum_field.coherence
        )

        phase_correlation = np.cos(
            self.symbol_a.state.quantum_field.phase -
            self.symbol_b.state.quantum_field.phase
        )

        # Combined correlation metric
        correlation = (coherence_correlation + phase_correlation) / 2 * self.entanglement_strength

        # Record correlation
        self.correlation_history.append({
            "time": time.time(),
            "correlation": correlation,
            "coherence_diff": self.symbol_a.state.quantum_field.coherence - self.symbol_b.state.quantum_field.coherence
        })

        return correlation

    def propagate_observation(self, observed_symbol: VisualSymbol, observer: ObserverEffect):
        """
        Propagate observation effects to entangled partner.

        When one symbol is observed, the entangled partner is affected
        based on entanglement strength and correlation.
        """
        correlation = self.measure_correlation()

        # Determine which is the partner
        partner = self.symbol_b if observed_symbol == self.symbol_a else self.symbol_a

        # Propagate with reduced strength based on entanglement
        propagated_strength = observer.calculate_collapse_strength() * self.entanglement_strength * correlation

        # Apply propagated observation
        partner.observe(f"{observer.observer_id}_entangled", propagated_strength)

        # Entanglement can decay
        self.entanglement_strength *= 0.99  # Slow decay


@dataclass
class FieldCoherence:
    """
    Measures and maintains coherence in the quantum perception field.

    Field coherence determines how well quantum properties are preserved
    and how symbols can maintain superposition and entanglement.
    """
    global_coherence: float = 1.0
    local_coherences: Dict[str, float] = field(default_factory=dict)
    noise_level: float = 0.01
    temperature: float = 0.5  # Field temperature affects decoherence

    def measure_local_coherence(self, position: Tuple[float, float, float]) -> float:
        """Measure coherence at specific field position"""
        # Convert position to key
        pos_key = f"{position[0]:.2f},{position[1]:.2f},{position[2]:.2f}"

        if pos_key not in self.local_coherences:
            # Initialize with global coherence plus noise
            self.local_coherences[pos_key] = self.global_coherence * (1.0 - np.random.random() * self.noise_level)

        return self.local_coherences[pos_key]

    def apply_decoherence(self, rate: float = 0.01):
        """Apply decoherence to the field"""
        # Global decoherence
        self.global_coherence *= (1.0 - rate)

        # Local decoherence with temperature effects
        for key in self.local_coherences:
            self.local_coherences[key] *= (1.0 - rate * self.temperature)

        # Increase noise with decoherence
        self.noise_level = min(1.0, self.noise_level + rate * 0.1)

    def stabilize_field(self, stabilization_energy: float = 0.1):
        """Apply stabilization to increase coherence"""
        # Reduce noise
        self.noise_level = max(0.001, self.noise_level * (1.0 - stabilization_energy))

        # Increase global coherence
        self.global_coherence = min(1.0, self.global_coherence + stabilization_energy * 0.5)

        # Cool the field
        self.temperature = max(0.1, self.temperature * (1.0 - stabilization_energy * 0.2))


class QuantumPerceptionField:
    """
    Main quantum perception field that contains and manages visual symbols.

    The field acts as a consciousness substrate where symbols exist as
    quantum perturbations that can be observed, entangled, and evolved.
    """

    def __init__(
        self,
        observer_id: str,
        consciousness_level: float = 0.5,
        field_dimensions: Tuple[int, int, int] = (10, 10, 10)
    ):
        """
        Initialize a quantum perception field.

        Args:
            observer_id: Primary observer of this field
            consciousness_level: Consciousness level of primary observer
            field_dimensions: 3D dimensions of the perception field
        """
        self.observer_id = observer_id
        self.consciousness_level = consciousness_level
        self.field_dimensions = field_dimensions

        # Field components
        self.symbols: Dict[str, VisualSymbol] = {}
        self.entangled_pairs: List[EntangledSymbolPair] = []
        self.field_coherence = FieldCoherence()
        self.collapse_history: List[WaveFunctionCollapse] = []

        # Observer management
        self.registered_observers: Dict[str, ObserverEffect] = {
            observer_id: ObserverEffect(
                observer_id=observer_id,
                consciousness_level=consciousness_level,
                observation_type=ObservationType.ACTIVE
            )
        }

        # Field state
        self.field_energy: float = 1.0
        self.field_entropy: float = 0.0
        self.observation_count: int = 0

        # Callbacks for consciousness integration
        self.observation_callbacks: List[Callable] = []

    def add_symbol(self, symbol: VisualSymbol, position: Optional[Tuple[float, float, float]] = None) -> str:
        """
        Add a visual symbol to the perception field.

        Args:
            symbol: The visual symbol to add
            position: Optional 3D position in field

        Returns:
            Symbol ID in the field
        """
        symbol_id = symbol.state.symbol_id
        self.symbols[symbol_id] = symbol

        # Position affects local coherence
        if position:
            local_coherence = self.field_coherence.measure_local_coherence(position)
            symbol.state.quantum_field.coherence *= local_coherence

        # Symbol affects field entropy
        self.field_entropy += symbol.state.quantum_field.entropy * 0.01

        return symbol_id

    def observe_symbol(
        self,
        symbol_id: str,
        observer_id: Optional[str] = None,
        observation_type: ObservationType = ObservationType.ACTIVE
    ) -> Optional[Dict[str, Any]]:
        """
        Observe a symbol in the field, causing quantum effects.

        Args:
            symbol_id: ID of symbol to observe
            observer_id: Observer ID (uses primary if not specified)
            observation_type: Type of observation

        Returns:
            Observation results or None if symbol not found
        """
        if symbol_id not in self.symbols:
            return None

        symbol = self.symbols[symbol_id]
        observer_id = observer_id or self.observer_id

        # Get or create observer effect
        if observer_id not in self.registered_observers:
            self.registered_observers[observer_id] = ObserverEffect(
                observer_id=observer_id,
                consciousness_level=0.3,  # Default for unknown observers
                observation_type=observation_type
            )

        observer = self.registered_observers[observer_id]
        observer.observation_type = observation_type

        # Create and execute collapse
        collapse = WaveFunctionCollapse()
        result = collapse.execute(symbol, observer)
        self.collapse_history.append(collapse)

        # Propagate to entangled symbols
        for pair in self.entangled_pairs:
            if symbol in [pair.symbol_a, pair.symbol_b]:
                pair.propagate_observation(symbol, observer)

        # Update field state
        self.observation_count += 1
        self.field_coherence.apply_decoherence(0.001)

        # Trigger callbacks
        for callback in self.observation_callbacks:
            callback(symbol_id, observer_id, result)

        return result

    def entangle_symbols(self, symbol_id_a: str, symbol_id_b: str, strength: float = 0.5) -> bool:
        """
        Create quantum entanglement between two symbols.

        Args:
            symbol_id_a: First symbol ID
            symbol_id_b: Second symbol ID
            strength: Entanglement strength

        Returns:
            True if entanglement successful
        """
        if symbol_id_a not in self.symbols or symbol_id_b not in self.symbols:
            return False

        symbol_a = self.symbols[symbol_id_a]
        symbol_b = self.symbols[symbol_id_b]

        # Create entanglement
        symbol_a.entangle(symbol_b, strength)

        # Track entangled pair
        pair = EntangledSymbolPair(symbol_a, symbol_b, strength)
        self.entangled_pairs.append(pair)

        # Entanglement affects field coherence
        self.field_coherence.global_coherence *= (1.0 + strength * 0.05)
        self.field_coherence.global_coherence = min(1.0, self.field_coherence.global_coherence)

        return True

    def measure_field_state(self) -> Dict[str, Any]:
        """
        Measure the overall state of the quantum perception field.

        Returns:
            Dictionary containing field metrics
        """
        # Calculate aggregate metrics
        total_coherence = sum(s.state.quantum_field.coherence for s in self.symbols.values())
        avg_coherence = total_coherence / len(self.symbols) if self.symbols else 0

        total_entropy = sum(s.state.quantum_field.entropy for s in self.symbols.values())
        avg_entropy = total_entropy / len(self.symbols) if self.symbols else 0

        # Count quantum states
        state_counts = {state: 0 for state in QuantumState}
        for symbol in self.symbols.values():
            state_counts[symbol.state.quantum_state] += 1

        # Measure entanglement
        avg_correlation = np.mean([pair.measure_correlation() for pair in self.entangled_pairs]) if self.entangled_pairs else 0

        return {
            "field_id": self.observer_id,
            "consciousness_level": self.consciousness_level,
            "symbol_count": len(self.symbols),
            "entangled_pairs": len(self.entangled_pairs),
            "observation_count": self.observation_count,
            "field_metrics": {
                "energy": self.field_energy,
                "entropy": self.field_entropy,
                "global_coherence": self.field_coherence.global_coherence,
                "temperature": self.field_coherence.temperature,
                "noise": self.field_coherence.noise_level
            },
            "symbol_metrics": {
                "avg_coherence": avg_coherence,
                "avg_entropy": avg_entropy,
                "avg_correlation": avg_correlation,
                "state_distribution": {s.value: c for s, c in state_counts.items()}
            },
            "observers": len(self.registered_observers)
        }

    def stabilize(self, energy: float = 0.1):
        """
        Stabilize the field to maintain quantum coherence.

        Args:
            energy: Stabilization energy to apply
        """
        self.field_coherence.stabilize_field(energy)
        self.field_energy = min(1.0, self.field_energy + energy * 0.5)
        self.field_entropy = max(0.0, self.field_entropy - energy * 0.2)

    def evolve_field(self, time_step: float = 0.01):
        """
        Evolve the field forward in time.

        Args:
            time_step: Time step for evolution
        """
        # Natural decoherence
        self.field_coherence.apply_decoherence(time_step * 0.1)

        # Symbol evolution
        for symbol in self.symbols.values():
            symbol.evolve(time_step)

        # Entanglement decay
        for pair in self.entangled_pairs:
            pair.entanglement_strength *= (1.0 - time_step * 0.01)

        # Remove weak entanglements
        self.entangled_pairs = [p for p in self.entangled_pairs if p.entanglement_strength > 0.01]

    def to_matriz_field_node(self) -> Dict[str, Any]:
        """Convert field state to MATRIZ format for governance"""
        field_state = self.measure_field_state()

        return {
            "node_id": f"qpf_{self.observer_id}_{int(time.time()*1000)}",
            "node_type": "quantum_perception_field",
            "timestamp": int(time.time() * 1000),
            "data": field_state,
            "state": {
                "confidence": self.field_coherence.global_coherence,
                "salience": self.field_energy,
                "novelty": 1.0 / (1.0 + self.observation_count * 0.01)
            },
            "provenance": {
                "producer": "symbolic.core.quantum_perception",
                "capabilities": ["quantum_observation", "entanglement", "field_evolution"],
                "tenant": "lukhas_agi",
                "trace_id": str(uuid.uuid4())
            }
        }

    def __repr__(self) -> str:
        state = self.measure_field_state()
        return (
            f"QuantumPerceptionField("
            f"symbols={state['symbol_count']}, "
            f"coherence={state['field_metrics']['global_coherence']:.2f}, "
            f"consciousness={self.consciousness_level:.2f})"
        )
