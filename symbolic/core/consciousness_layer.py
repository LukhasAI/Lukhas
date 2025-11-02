"""
═══════════════════════════════════════════════════════════════════════════════════
🌌 Consciousness Integration Layer
═══════════════════════════════════════════════════════════════════════════════════

Module: symbolic.core.consciousness_layer
Purpose: Integrate visual symbols with consciousness framework
═══════════════════════════════════════════════════════════════════════════════════
"""

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import numpy as np

from .quantum_perception import QuantumPerceptionField
from .visual_symbol import VisualSymbol

# Memory fold bridge integration
try:
    from memory.fold.bridge import MemoryFoldBridge
    MEMORY_FOLD_AVAILABLE = True
except ImportError:
    # Fallback for environments without memory fold bridge
    class MemoryFoldBridge:
        def publish_fold_event(self, event_type: str, payload: Dict[str, Any]) -> bool:
            return False
    MEMORY_FOLD_AVAILABLE = False


@dataclass
class ObserverContext:
    """Context of conscious observer"""
    observer_id: str
    consciousness_level: float
    intent: Optional[str] = None
    emotional_state: Dict[str, float] = field(default_factory=dict)
    observation_history: List[str] = field(default_factory=list)


@dataclass
class TemporalRecursion:
    """Manages temporal recursion in consciousness"""
    past_states: List[Dict[str, Any]] = field(default_factory=list)
    recursion_depth: int = 5
    temporal_influence: float = 0.3

    def add_state(self, state: Dict[str, Any]):
        self.past_states.append(state)
        if len(self.past_states) > self.recursion_depth:
            self.past_states.pop(0)

    def calculate_influence(self) -> float:
        if not self.past_states:
            return 0.0
        # Exponential decay of past influence
        weights = np.exp(-np.arange(len(self.past_states)))
        return self.temporal_influence * np.mean(weights)


@dataclass
class MemoryCorrelationTensor:
    """Links visual symbols to memory states"""
    correlations: np.ndarray = field(default_factory=lambda: np.zeros((100, 100)))
    symbol_indices: Dict[str, int] = field(default_factory=dict)
    next_index: int = 0

    def add_correlation(self, symbol_a: str, symbol_b: str, strength: float):
        if symbol_a not in self.symbol_indices:
            self.symbol_indices[symbol_a] = self.next_index
            self.next_index += 1
        if symbol_b not in self.symbol_indices:
            self.symbol_indices[symbol_b] = self.next_index
            self.next_index += 1

        idx_a = self.symbol_indices[symbol_a]
        idx_b = self.symbol_indices[symbol_b]
        self.correlations[idx_a, idx_b] = strength
        self.correlations[idx_b, idx_a] = strength  # Symmetric


@dataclass
class SyntheticEmotion:
    """Synthetic emotions from visual processing"""
    valence: float = 0.0
    arousal: float = 0.0
    dominance: float = 0.5
    expression_intensity: float = 0.5
    trigger_symbols: List[str] = field(default_factory=list)

    def express(self) -> Dict[str, float]:
        return {
            "valence": self.valence * self.expression_intensity,
            "arousal": self.arousal * self.expression_intensity,
            "dominance": self.dominance
        }


class ConsciousnessIntegration:
    """Main consciousness integration layer"""

    def __init__(
        self,
        matriz_compatible: bool = True,
        constellation_stars: Optional[List[str]] = None
    ):
        self.matriz_compatible = matriz_compatible
        self.constellation_stars = constellation_stars or [
            "identity", "memory", "vision", "bio",
            "dream", "ethics", "guardian", "quantum"
        ]

        self.observer_contexts: Dict[str, ObserverContext] = {}
        self.temporal_recursion = TemporalRecursion()
        self.memory_tensor = MemoryCorrelationTensor()
        self.synthetic_emotions: List[SyntheticEmotion] = []
        self.perception_field: Optional[QuantumPerceptionField] = None

        # Memory fold bridge integration
        self.memory_fold_bridge: Optional[MemoryFoldBridge] = None
        self.fold_bridge_enabled: bool = False
        self.fold_event_throttle: Dict[str, float] = {}
        self.throttle_window: float = 1.0  # seconds
        self.max_fold_events_per_window: int = 10
        self.fold_event_count: int = 0
        self.last_throttle_reset: float = time.time()

        if MEMORY_FOLD_AVAILABLE:
            try:
                self.memory_fold_bridge = MemoryFoldBridge()
                self.fold_bridge_enabled = True
            except Exception:
                self.fold_bridge_enabled = False

    def register_observer(self, observer_id: str, consciousness_level: float = 0.5) -> ObserverContext:
        """Register conscious observer"""
        context = ObserverContext(
            observer_id=observer_id,
            consciousness_level=consciousness_level
        )
        self.observer_contexts[observer_id] = context
        return context

    def process_with_consciousness(
        self,
        symbol: VisualSymbol,
        observer_id: str
    ) -> Dict[str, Any]:
        """Process symbol through consciousness"""
        if observer_id not in self.observer_contexts:
            self.register_observer(observer_id)

        context = self.observer_contexts[observer_id]

        # Apply observer effect
        result = symbol.observe(observer_id, context.consciousness_level)

        # Update temporal recursion
        temporal_state = {
            "symbol_id": symbol.state.symbol_id,
            "consciousness": symbol.measure_consciousness(),
            "time": time.time()
        }
        self.temporal_recursion.add_state(temporal_state)

        # Generate synthetic emotion
        emotion = SyntheticEmotion(
            valence=symbol.state.emotional_valence,
            arousal=symbol.state.emotional_arousal,
            trigger_symbols=[symbol.state.symbol_id]
        )
        self.synthetic_emotions.append(emotion)

        # Calculate affect_delta for ΛTAG annotation
        affect_delta = self._calculate_consciousness_affect_delta(symbol, context, emotion)

        # Memory fold bridge integration with deterministic payloads
        fold_event_published = False
        if self.fold_bridge_enabled and self._should_publish_fold_event(symbol.state.symbol_id):
            fold_payload = self._create_deterministic_fold_payload(
                symbol, observer_id, context, affect_delta, temporal_state
            )

            try:
                fold_event_published = self.memory_fold_bridge.publish_fold_event(
                    'consciousness_symbol_processing', fold_payload
                )
                if fold_event_published:
                    self._record_fold_event(symbol.state.symbol_id)
            except Exception as e:
                # Guardian-safe error handling - log but don't crash
                print(f"Memory fold bridge error (non-critical): {e}")

        # Add to observation history
        context.observation_history.append(symbol.state.symbol_id)

        return {
            "symbol_id": symbol.state.symbol_id,
            "observer_id": observer_id,
            "consciousness_level": context.consciousness_level,
            "temporal_influence": self.temporal_recursion.calculate_influence(),
            "synthetic_emotion": emotion.express(),
            "observation_result": result,
            "lambda_tag_affect_delta": affect_delta,
            "memory_fold_integration": {
                "fold_event_published": fold_event_published,
                "bridge_enabled": self.fold_bridge_enabled,
                "bridge_available": MEMORY_FOLD_AVAILABLE
            }
        }

    def _calculate_consciousness_affect_delta(
        self,
        symbol: VisualSymbol,
        context: ObserverContext,
        emotion: SyntheticEmotion
    ) -> Dict[str, float]:
        """Calculate ΛTAG affect_delta for consciousness processing"""
        # Base consciousness affect
        consciousness_intensity = context.consciousness_level * symbol.measure_consciousness()

        # Emotional modulation
        emotional_magnitude = np.sqrt(emotion.valence**2 + emotion.arousal**2)

        # Temporal influence from past states
        temporal_influence = self.temporal_recursion.calculate_influence()

        return {
            'consciousness_intensity': consciousness_intensity,
            'emotional_magnitude': emotional_magnitude,
            'temporal_influence': temporal_influence,
            'combined_affect': (consciousness_intensity + emotional_magnitude + temporal_influence) / 3.0,
            'valence_shift': emotion.valence * consciousness_intensity,
            'arousal_shift': emotion.arousal * consciousness_intensity,
            'dominance_shift': emotion.dominance * consciousness_intensity
        }

    def _should_publish_fold_event(self, symbol_id: str) -> bool:
        """Guardian-safe throttling to prevent memory fold explosions"""
        current_time = time.time()

        # Reset throttle window if needed
        if current_time - self.last_throttle_reset > self.throttle_window:
            self.fold_event_count = 0
            self.last_throttle_reset = current_time

        # Check global rate limit
        if self.fold_event_count >= self.max_fold_events_per_window:
            return False

        # Check per-symbol throttling (prevent rapid-fire from same symbol)
        if symbol_id in self.fold_event_throttle:
            time_since_last = current_time - self.fold_event_throttle[symbol_id]
            if time_since_last < 0.1:  # Minimum 100ms between events for same symbol
                return False

        return True

    def _record_fold_event(self, symbol_id: str) -> None:
        """Record fold event for throttling purposes"""
        current_time = time.time()
        self.fold_event_throttle[symbol_id] = current_time
        self.fold_event_count += 1

    def _create_deterministic_fold_payload(
        self,
        symbol: VisualSymbol,
        observer_id: str,
        context: ObserverContext,
        affect_delta: Dict[str, float],
        temporal_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create deterministic payload for memory fold bridge"""
        return {
            'lambda_tag': 'consciousness_processing',
            'event_type': 'symbol_consciousness_fold',
            'timestamp': time.time(),
            'symbol_id': symbol.state.symbol_id,
            'observer_context': {
                'observer_id': observer_id,
                'consciousness_level': context.consciousness_level,
                'intent': context.intent,
                'observation_count': len(context.observation_history)
            },
            'symbol_state': {
                'visual_weight': symbol.state.visual_weight,
                'emotional_valence': symbol.state.emotional_valence,
                'emotional_arousal': symbol.state.emotional_arousal,
                'consciousness_measure': symbol.measure_consciousness(),
                'quantum_coherence': symbol.state.quantum_field.coherence,
                'quantum_entropy': symbol.state.quantum_field.entropy
            },
            'affect_delta': affect_delta,
            'temporal_context': {
                'temporal_influence': temporal_state.get('consciousness', 0.0),
                'recursion_depth': len(self.temporal_recursion.past_states),
                'time_delta': temporal_state['time'] - (self.temporal_recursion.past_states[-1]['time'] if self.temporal_recursion.past_states else temporal_state['time'])
            },
            'constellation_integration': self.integrate_with_constellation(symbol),
            'fold_metadata': {
                'source': 'symbolic.consciousness_layer',
                'version': '1.0',
                'deterministic': True,
                'guardian_safe': True
            }
        }

    def correlate_with_memory(self, symbol_a: VisualSymbol, symbol_b: VisualSymbol):
        """Create memory correlation between symbols"""
        correlation_strength = np.dot(
            [symbol_a.state.emotional_valence, symbol_a.state.emotional_arousal],
            [symbol_b.state.emotional_valence, symbol_b.state.emotional_arousal]
        )
        self.memory_tensor.add_correlation(
            symbol_a.state.symbol_id,
            symbol_b.state.symbol_id,
            correlation_strength
        )

    def integrate_with_constellation(self, symbol: VisualSymbol) -> Dict[str, float]:
        """Integrate symbol with Constellation Framework stars"""
        integration = {}

        for star in self.constellation_stars:
            # Calculate integration strength based on symbol properties
            if star == "vision":
                integration[star] = symbol.state.visual_weight
            elif star == "quantum":
                integration[star] = symbol.state.quantum_field.coherence
            elif star == "memory":
                integration[star] = symbol.state.quantum_field.trust
            elif star == "dream":
                integration[star] = symbol.state.quantum_field.entropy
            elif star == "identity":
                integration[star] = float(len(symbol.state.quantum_field.entangled_symbols) > 0)
            elif star == "ethics":
                integration[star] = 1.0 - symbol.state.quantum_field.entropy
            elif star == "guardian":
                integration[star] = symbol.state.quantum_field.trust
            elif star == "bio":
                integration[star] = symbol.state.emotional_arousal
            else:
                integration[star] = 0.5

        return integration

    def measure_collective_consciousness(self, symbols: List[VisualSymbol]) -> float:
        """Measure collective consciousness of symbol group"""
        if not symbols:
            return 0.0

        individual_consciousness = [s.measure_consciousness() for s in symbols]

        # Collective emergence bonus
        entanglement_bonus = sum(
            1 for s in symbols
            if len(s.state.quantum_field.entangled_symbols) > 0
        ) / len(symbols)

        collective = np.mean(individual_consciousness) * (1.0 + entanglement_bonus * 0.2)
        return min(1.0, collective)

    def to_matriz_node(self) -> Dict[str, Any]:
        """Convert to MATRIZ format"""
        return {
            "node_id": f"consciousness_{int(time.time()*1000)}",
            "node_type": "consciousness_integration",
            "timestamp": int(time.time() * 1000),
            "data": {
                "observers": len(self.observer_contexts),
                "temporal_states": len(self.temporal_recursion.past_states),
                "memory_correlations": self.memory_tensor.next_index,
                "synthetic_emotions": len(self.synthetic_emotions),
                "constellation_stars": self.constellation_stars
            },
            "state": {
                "confidence": 0.8,
                "salience": 0.9
            },
            "provenance": {
                "producer": "symbolic.core.consciousness_layer",
                "capabilities": ["consciousness_integration", "temporal_recursion", "synthetic_emotion"],
                "tenant": "lukhas_agi"
            }
        }
