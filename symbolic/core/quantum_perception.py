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

import hashlib
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional

import numpy as np

from .visual_symbol import QuantumState, VisualSymbol

# ΛTRACE imports for symbolic trace routing
try:
    from core.traces.trace_router import TraceRouter
    TRACE_ROUTER_AVAILABLE = True
except ImportError:
    # Fallback for environments without trace router
    class TraceRouter:
        def route_symbolic_trace(self, event_type: str, payload: dict[str, Any]) -> None:
            pass
    TRACE_ROUTER_AVAILABLE = False


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
    emotional_state: Optional[dict[str, float]] = None

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
    pre_state: Optional[dict[str, Any]] = None
    post_state: Optional[dict[str, Any]] = None
    observer: Optional[ObserverEffect] = None
    eigenstate_selected: Optional[int] = None
    probability_distribution: Optional[np.ndarray] = None
    decoherence_rate: float = 0.0

    def execute(self, symbol: VisualSymbol, observer: ObserverEffect) -> dict[str, Any]:
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
    Enhanced with health tracking and ΛTAG drift warnings.
    """
    symbol_a: VisualSymbol
    symbol_b: VisualSymbol
    entanglement_strength: float = 0.5
    entanglement_health: float = 1.0
    drift_threshold: float = 0.35
    last_drift_warning: float = 0.0
    health_window_size: int = 10
    creation_time: float = field(default_factory=time.time)
    correlation_history: list[dict[str, Any]] = field(default_factory=list)
    health_history: list[dict[str, Any]] = field(default_factory=list)

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

        # Record correlation with enhanced health tracking
        correlation_entry = {
            "time": time.time(),
            "correlation": correlation,
            "coherence_diff": self.symbol_a.state.quantum_field.coherence - self.symbol_b.state.quantum_field.coherence,
            "phase_diff": self.symbol_a.state.quantum_field.phase - self.symbol_b.state.quantum_field.phase,
            "entanglement_health": self.entanglement_health
        }
        self.correlation_history.append(correlation_entry)

        # Update entanglement health based on correlation
        self._update_entanglement_health(correlation)

        return correlation

    def _update_entanglement_health(self, current_correlation: float) -> None:
        """Update rolling entanglement health metric"""
        # Calculate health based on correlation stability
        if len(self.correlation_history) >= 2:
            # Recent correlation variance as health indicator
            recent_correlations = [entry["correlation"] for entry in self.correlation_history[-self.health_window_size:]]
            correlation_variance = np.var(recent_correlations) if len(recent_correlations) > 1 else 0.0
            correlation_mean = np.mean(recent_correlations)

            # Health decreases with variance and low correlation
            stability_factor = 1.0 - min(correlation_variance * 2.0, 0.8)
            strength_factor = max(0.2, correlation_mean)

            new_health = stability_factor * strength_factor * self.entanglement_strength

            # Smooth health updates with exponential moving average
            self.entanglement_health = 0.7 * self.entanglement_health + 0.3 * new_health
        else:
            # Initial health based on current correlation
            self.entanglement_health = current_correlation * self.entanglement_strength

        # Record health history
        health_entry = {
            "time": time.time(),
            "health": self.entanglement_health,
            "correlation": current_correlation,
            "stability": 1.0 - (np.var([entry["correlation"] for entry in self.correlation_history[-5:]]) if len(self.correlation_history) >= 2 else 0.0)
        }
        self.health_history.append(health_entry)

        # Emit ΛTAG drift warning if health drops below threshold
        if self.entanglement_health < self.drift_threshold:
            self._emit_drift_warning()

    def _emit_drift_warning(self) -> None:
        """Emit ΛTAG drift warning when entanglement health degrades"""
        current_time = time.time()

        # Throttle warnings to avoid spam (minimum 10 seconds between warnings)
        if current_time - self.last_drift_warning < 10.0:
            return

        self.last_drift_warning = current_time

        # Generate drift warning payload
        warning_payload = {
            'lambda_tag': 'drift',
            'event_type': 'entanglement_health_degradation',
            'symbol_a_id': self.symbol_a.state.symbol_id,
            'symbol_b_id': self.symbol_b.state.symbol_id,
            'entanglement_health': self.entanglement_health,
            'drift_threshold': self.drift_threshold,
            'entanglement_strength': self.entanglement_strength,
            'correlation_variance': np.var([entry["correlation"] for entry in self.correlation_history[-5:]]) if len(self.correlation_history) >= 2 else 0.0,
            'timestamp': current_time,
            'severity': 'HIGH' if self.entanglement_health < 0.2 else 'MEDIUM'
        }

        # Route warning through trace system if available
        try:
            from core.traces.trace_router import TraceRouter
            trace_router = TraceRouter()
            trace_router.route_symbolic_trace('entanglement_drift_warning', warning_payload)
        except ImportError:
            # Fallback logging if trace router unavailable
            print(f"ΛTAG:drift - Entanglement health degraded: {warning_payload}")

    def summarize_health(self) -> dict[str, Any]:
        """
        Deterministic helper for downstream analytics.

        Returns:
            Comprehensive health summary for analytics
        """
        if not self.health_history:
            return {
                'current_health': self.entanglement_health,
                'health_trend': 'stable',
                'risk_level': 'low',
                'correlation_stability': 1.0,
                'recommendations': []
            }

        # Calculate health trend
        recent_health = [entry["health"] for entry in self.health_history[-5:]]
        health_trend = 'improving' if len(recent_health) >= 2 and recent_health[-1] > recent_health[0] else \
                      'degrading' if len(recent_health) >= 2 and recent_health[-1] < recent_health[0] else \
                      'stable'

        # Calculate correlation stability
        recent_correlations = [entry["correlation"] for entry in self.correlation_history[-10:]]
        correlation_stability = 1.0 - (np.var(recent_correlations) if len(recent_correlations) > 1 else 0.0)

        # Determine risk level
        risk_level = 'high' if self.entanglement_health < 0.2 else \
                    'medium' if self.entanglement_health < self.drift_threshold else \
                    'low'

        # Generate recommendations
        recommendations = []
        if self.entanglement_health < self.drift_threshold:
            recommendations.append('Consider field stabilization to restore entanglement health')
        if correlation_stability < 0.6:
            recommendations.append('High correlation variance detected - investigate environmental factors')
        if self.entanglement_strength < 0.3:
            recommendations.append('Entanglement strength declining - may need re-entanglement')

        return {
            'current_health': self.entanglement_health,
            'health_trend': health_trend,
            'risk_level': risk_level,
            'correlation_stability': correlation_stability,
            'entanglement_strength': self.entanglement_strength,
            'age_seconds': time.time() - self.creation_time,
            'total_observations': len(self.correlation_history),
            'drift_warnings_issued': len([entry for entry in self.health_history if entry.get('health', 1.0) < self.drift_threshold]),
            'recommendations': recommendations,
            'analytics_metadata': {
                'last_updated': time.time(),
                'health_window_size': self.health_window_size,
                'drift_threshold': self.drift_threshold,
                'mean_health': np.mean([entry["health"] for entry in self.health_history]) if self.health_history else self.entanglement_health,
                'min_health': min([entry["health"] for entry in self.health_history]) if self.health_history else self.entanglement_health,
                'max_health': max([entry["health"] for entry in self.health_history]) if self.health_history else self.entanglement_health
            }
        }

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

        # Entanglement can decay with each observation
        self.entanglement_strength *= 0.99  # Slow decay


@dataclass
class FieldCoherence:
    """
    Measures and maintains coherence in the quantum perception field.

    Field coherence determines how well quantum properties are preserved
    and how symbols can maintain superposition and entanglement.
    """
    global_coherence: float = 1.0
    local_coherences: dict[str, float] = field(default_factory=dict)
    noise_level: float = 0.01
    temperature: float = 0.5  # Field temperature affects decoherence

    def measure_local_coherence(self, position: tuple[float, float, float]) -> float:
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
        field_dimensions: tuple[int, int, int] = (10, 10, 10)
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
        self.symbols: dict[str, VisualSymbol] = {}
        self.entangled_pairs: list[EntangledSymbolPair] = []
        self.field_coherence = FieldCoherence()
        self.collapse_history: list[WaveFunctionCollapse] = []

        # Observer management
        self.registered_observers: dict[str, ObserverEffect] = {
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

        # ΛTRACE configuration
        self._trace_enabled: bool = False
        self.interaction_history: list[dict[str, Any]] = []

        # Callbacks for consciousness integration
        self.observation_callbacks: list[Callable] = []

    def add_symbol(self, symbol: VisualSymbol, position: Optional[tuple[float, float, float]] = None) -> str:
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
    ) -> Optional[dict[str, Any]]:
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

        # Capture pre-observation state for ΛTRACE metrics
        pre_observation_entropy = symbol.state.quantum_field.entropy
        pre_observation_coherence = symbol.state.quantum_field.coherence

        # Create and execute collapse
        collapse = WaveFunctionCollapse()
        result = collapse.execute(symbol, observer)
        self.collapse_history.append(collapse)

        # Calculate ΛTRACE metrics
        drift_score = self._calculate_drift_score(
            pre_observation_entropy,
            symbol.state.quantum_field.entropy,
            pre_observation_coherence,
            symbol.state.quantum_field.coherence
        )

        collapse_hash = self._generate_collapse_hash(symbol, observer, result)
        affect_delta = self._calculate_affect_delta(observer, observation_type, drift_score)

        # Enhanced result with ΛTRACE metadata
        enhanced_result = {
            **result,
            'lambda_trace': {
                'drift_score': drift_score,
                'collapse_hash': collapse_hash,
                'affect_delta': affect_delta,
                'observer_id': observer_id,
                'symbol_id': symbol_id,
                'observation_timestamp': time.time(),
                'field_coherence': self.field_coherence.current_coherence,
                'observation_count': self.observation_count + 1
            }
        }

        # Route ΛTRACE event with deterministic flag support
        if hasattr(self, '_trace_enabled') and self._trace_enabled:
            trace_router = TraceRouter()
            provenance_payload = {
                'event_type': 'quantum_observation',
                'symbol_id': symbol_id,
                'observer_id': observer_id,
                'observation_type': observation_type.value,
                'drift_score': drift_score,
                'collapse_hash': collapse_hash,
                'affect_delta': affect_delta,
                'field_entropy': self.field_entropy,
                'provenance_chain': self._build_provenance_chain(symbol, observer)
            }
            trace_router.route_symbolic_trace('quantum_observation', provenance_payload)

        # Propagate to entangled symbols
        for pair in self.entangled_pairs:
            if symbol in [pair.symbol_a, pair.symbol_b]:
                pair.propagate_observation(symbol, observer)

        # Update field state
        self.observation_count += 1
        self.field_coherence.apply_decoherence(0.001)

        # Trigger callbacks
        for callback in self.observation_callbacks:
            callback(symbol_id, observer_id, enhanced_result)

        return enhanced_result

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

    def measure_field_state(self) -> dict[str, Any]:
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
        state_counts = dict.fromkeys(QuantumState, 0)
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

    def _calculate_drift_score(
        self,
        pre_entropy: float,
        post_entropy: float,
        pre_coherence: float,
        post_coherence: float
    ) -> float:
        """
        Calculate drift score from observation-induced state changes.

        Args:
            pre_entropy: Entropy before observation
            post_entropy: Entropy after observation
            pre_coherence: Coherence before observation
            post_coherence: Coherence after observation

        Returns:
            Drift score (0.0 = stable, 1.0 = maximum drift)
        """
        entropy_delta = abs(post_entropy - pre_entropy)
        coherence_delta = abs(post_coherence - pre_coherence)

        # Normalize and combine deltas
        normalized_entropy_drift = min(entropy_delta / (pre_entropy + 0.001), 1.0)
        normalized_coherence_drift = min(coherence_delta / (pre_coherence + 0.001), 1.0)

        drift_score = (normalized_entropy_drift + normalized_coherence_drift) / 2.0
        return max(0.0, min(1.0, drift_score))

    def _generate_collapse_hash(
        self,
        symbol: 'VisualSymbol',
        observer: 'ObserverEffect',
        result: dict[str, Any]
    ) -> str:
        """
        Generate deterministic hash for collapse event.

        Args:
            symbol: The observed symbol
            observer: The observer effect
            result: The observation result

        Returns:
            Hexadecimal hash string for collapse identification
        """
        collapse_data = f"{symbol.state.symbol_id}:{observer.observer_id}:{observer.consciousness_level}:{result.get('collapsed_state', 'unknown')}:{time.time():.6f}"
        return hashlib.sha256(collapse_data.encode()).hexdigest()[:16]

    def _calculate_affect_delta(
        self,
        observer: 'ObserverEffect',
        observation_type: ObservationType,
        drift_score: float
    ) -> dict[str, float]:
        """
        Calculate affective impact of observation.

        Args:
            observer: The observer effect
            observation_type: Type of observation performed
            drift_score: Calculated drift score

        Returns:
            Dictionary containing affective delta measurements
        """
        # Base affect based on observation type
        type_affect = {
            ObservationType.PASSIVE: 0.1,
            ObservationType.ACTIVE: 0.3,
            ObservationType.INTENTIONAL: 0.6,
            ObservationType.UNCONSCIOUS: 0.05,
            ObservationType.COLLECTIVE: 0.4
        }.get(observation_type, 0.2)

        # Modulate by consciousness level and drift
        consciousness_modifier = observer.consciousness_level
        drift_modifier = drift_score * 0.5

        valence = type_affect * consciousness_modifier * (1.0 - drift_modifier)
        arousal = type_affect * (consciousness_modifier + drift_modifier) / 2.0
        dominance = consciousness_modifier * (1.0 - drift_score * 0.3)

        return {
            'valence': max(-1.0, min(1.0, valence)),
            'arousal': max(0.0, min(1.0, arousal)),
            'dominance': max(0.0, min(1.0, dominance)),
            'intensity': (abs(valence) + arousal + dominance) / 3.0
        }

    def _build_provenance_chain(
        self,
        symbol: 'VisualSymbol',
        observer: 'ObserverEffect'
    ) -> list[dict[str, Any]]:
        """
        Build provenance chain for guardian auditing.

        Args:
            symbol: The observed symbol
            observer: The observer effect

        Returns:
            List of provenance events leading to this observation
        """
        provenance = []

        # Symbol creation provenance
        provenance.append({
            'event': 'symbol_creation',
            'symbol_id': symbol.state.symbol_id,
            'timestamp': getattr(symbol, '_creation_time', time.time()),
            'initial_state': symbol.state.current_state.value
        })

        # Observer registration provenance
        provenance.append({
            'event': 'observer_registration',
            'observer_id': observer.observer_id,
            'consciousness_level': observer.consciousness_level,
            'registration_time': getattr(observer, '_registration_time', time.time())
        })

        # Recent field interactions
        if hasattr(self, 'interaction_history'):
            recent_interactions = getattr(self, 'interaction_history', [])[-5:]
            for interaction in recent_interactions:
                provenance.append({
                    'event': 'field_interaction',
                    **interaction
                })

        return provenance

    def enable_trace(self, enabled: bool = True) -> None:
        """
        Enable or disable ΛTRACE event routing.

        Args:
            enabled: Whether to enable trace routing
        """
        self._trace_enabled = enabled

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

    def to_matriz_field_node(self) -> dict[str, Any]:
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
