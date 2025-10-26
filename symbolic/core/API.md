# Quantum Visual Symbol System - API Reference

## Quick Start

```python
from symbolic.core import (
    VisualSymbol,
    QuantumPerceptionField,
    RecursiveSymbolicEngine,
    NeuroSymbolicBridge,
    ConsciousnessIntegration,
    create_visual_symbol,
    create_perception_field,
    create_consciousness_layer
)
```

## Core Classes

### VisualSymbol

Primary class for quantum-aware visual symbols.

```python
class VisualSymbol:
    def __init__(
        self,
        symbol: str,
        meaning: str,
        quantum_field: Optional[QuantumField] = None,
        **kwargs
    )
```

#### Methods

##### `observe(observer_id: str, observation_strength: float) -> Dict[str, Any]`
Observe the symbol, causing quantum effects.

**Parameters:**
- `observer_id`: Unique identifier of the observer
- `observation_strength`: Strength of observation (0.0 to 1.0)

**Returns:**
- Dictionary containing observation results and state changes

**Example:**
```python
symbol = VisualSymbol("🌟", "star")
result = symbol.observe("observer_1", 0.8)
# Result: {'observer_id': 'observer_1', 'quantum_state': 'collapsed', ...}
```

##### `entangle(other: VisualSymbol, strength: float) -> bool`
Create quantum entanglement with another symbol.

**Parameters:**
- `other`: Another VisualSymbol to entangle with
- `strength`: Entanglement strength (0.0 to 1.0)

**Returns:**
- True if entanglement successful

**Example:**
```python
symbol1 = VisualSymbol("🌟", "star")
symbol2 = VisualSymbol("🌙", "moon")
symbol1.entangle(symbol2, 0.8)
```

##### `add_perception_token(token: PerceptionToken)`
Add a perception token for auxiliary reasoning.

**Parameters:**
- `token`: PerceptionToken instance

**Example:**
```python
token = PerceptionToken(salience=0.9, confidence=0.8)
symbol.add_perception_token(token)
```

##### `evolve(drift_rate: float) -> bool`
Allow symbol to evolve through symbolic drift.

**Parameters:**
- `drift_rate`: Rate of evolution (0.0 to 1.0)

**Returns:**
- True if evolution occurred

##### `resonate(frequency: float, magnitude: float)`
Apply resonance at specific frequency.

**Parameters:**
- `frequency`: Resonance frequency
- `magnitude`: Magnitude of resonance

##### `measure_consciousness() -> float`
Measure the consciousness level of this symbol.

**Returns:**
- Consciousness metric between 0.0 and 1.0

##### `to_dict() -> Dict[str, Any]`
Export symbol state as dictionary.

##### `to_matriz_node() -> Dict[str, Any]`
Convert to MATRIZ format node for governance.

---

### QuantumPerceptionField

Quantum perception field containing visual symbols.

```python
class QuantumPerceptionField:
    def __init__(
        self,
        observer_id: str,
        consciousness_level: float = 0.5,
        field_dimensions: Tuple[int, int, int] = (10, 10, 10)
    )
```

#### Methods

##### `add_symbol(symbol: VisualSymbol, position: Optional[Tuple[float, float, float]]) -> str`
Add a visual symbol to the perception field.

**Parameters:**
- `symbol`: The visual symbol to add
- `position`: Optional 3D position in field

**Returns:**
- Symbol ID in the field

**Example:**
```python
field = QuantumPerceptionField("main_observer", 0.7)
symbol_id = field.add_symbol(symbol, position=(5.0, 5.0, 5.0))
```

##### `observe_symbol(symbol_id: str, observer_id: Optional[str], observation_type: ObservationType) -> Optional[Dict[str, Any]]`
Observe a symbol in the field.

**Parameters:**
- `symbol_id`: ID of symbol to observe
- `observer_id`: Observer ID (uses primary if not specified)
- `observation_type`: Type of observation (PASSIVE, ACTIVE, INTENTIONAL, etc.)

**Returns:**
- Observation results or None if symbol not found

##### `entangle_symbols(symbol_id_a: str, symbol_id_b: str, strength: float) -> bool`
Create quantum entanglement between two symbols.

**Parameters:**
- `symbol_id_a`: First symbol ID
- `symbol_id_b`: Second symbol ID
- `strength`: Entanglement strength

**Returns:**
- True if entanglement successful

##### `measure_field_state() -> Dict[str, Any]`
Measure the overall state of the quantum perception field.

**Returns:**
- Dictionary containing field metrics

##### `stabilize(energy: float)`
Stabilize the field to maintain quantum coherence.

**Parameters:**
- `energy`: Stabilization energy to apply

##### `evolve_field(time_step: float)`
Evolve the field forward in time.

**Parameters:**
- `time_step`: Time step for evolution

---

### RecursiveSymbolicEngine

Engine for recursive symbolic emergence.

```python
class RecursiveSymbolicEngine:
    def __init__(self, recursion_depth: int = 10)
```

#### Methods

##### `observe_recursive(symbol: VisualSymbol, depth: int) -> Dict[str, Any]`
Recursively observe symbol, triggering emergence.

**Parameters:**
- `symbol`: Symbol to observe
- `depth`: Current recursion depth

**Returns:**
- Dictionary with observation results

##### `compress_symbols(symbols: List[VisualSymbol]) -> QSymbol`
Compress symbols into Q-symbol.

**Parameters:**
- `symbols`: List of symbols to compress

**Returns:**
- Compressed QSymbol

**Example:**
```python
engine = RecursiveSymbolicEngine()
q_symbol = engine.compress_symbols([symbol1, symbol2, symbol3])
```

##### `detect_contradiction(symbol_a: VisualSymbol, symbol_b: VisualSymbol) -> bool`
Detect if two symbols are contradictory.

**Parameters:**
- `symbol_a`: First symbol
- `symbol_b`: Second symbol

**Returns:**
- True if contradictory

##### `resolve_contradictions() -> Optional[EmergentSymbol]`
Attempt to resolve accumulated contradictions.

**Returns:**
- EmergentSymbol if resolution successful

##### `measure_emergence_potential(symbols: List[VisualSymbol]) -> float`
Calculate potential for new symbol emergence.

**Parameters:**
- `symbols`: List of symbols

**Returns:**
- Emergence potential (0.0 to 1.0)

##### `evolve_symbolic_landscape(time_step: float)`
Evolve entire symbolic landscape.

**Parameters:**
- `time_step`: Time step for evolution

---

### NeuroSymbolicBridge

Bridge between visual symbols and MATRIZ.

```python
class NeuroSymbolicBridge:
    def __init__(self, matriz_compatible: bool = True)
```

#### Methods

##### `process_visual_symbol(symbol: VisualSymbol) -> Dict[str, Any]`
Process symbol through neuro-symbolic pipeline.

**Parameters:**
- `symbol`: Visual symbol to process

**Returns:**
- Processing results dictionary

##### `generate_scene_graph(symbols: List[VisualSymbol]) -> SceneGraph`
Generate complete scene graph from symbols.

**Parameters:**
- `symbols`: List of visual symbols

**Returns:**
- SceneGraph object

**Example:**
```python
bridge = NeuroSymbolicBridge()
scene = bridge.generate_scene_graph([symbol1, symbol2, symbol3])
```

---

### ConsciousnessIntegration

Consciousness integration layer.

```python
class ConsciousnessIntegration:
    def __init__(
        self,
        matriz_compatible: bool = True,
        constellation_stars: Optional[List[str]] = None
    )
```

#### Methods

##### `register_observer(observer_id: str, consciousness_level: float) -> ObserverContext`
Register conscious observer.

**Parameters:**
- `observer_id`: Unique observer identifier
- `consciousness_level`: Level of consciousness (0.0 to 1.0)

**Returns:**
- ObserverContext object

##### `process_with_consciousness(symbol: VisualSymbol, observer_id: str) -> Dict[str, Any]`
Process symbol through consciousness.

**Parameters:**
- `symbol`: Visual symbol to process
- `observer_id`: Observer identifier

**Returns:**
- Processing results with consciousness metrics

##### `correlate_with_memory(symbol_a: VisualSymbol, symbol_b: VisualSymbol)`
Create memory correlation between symbols.

**Parameters:**
- `symbol_a`: First symbol
- `symbol_b`: Second symbol

##### `integrate_with_constellation(symbol: VisualSymbol) -> Dict[str, float]`
Integrate symbol with Constellation Framework stars.

**Parameters:**
- `symbol`: Visual symbol

**Returns:**
- Dictionary mapping stars to integration strengths

##### `measure_collective_consciousness(symbols: List[VisualSymbol]) -> float`
Measure collective consciousness of symbol group.

**Parameters:**
- `symbols`: List of visual symbols

**Returns:**
- Collective consciousness level (0.0 to 1.0)

---

## Factory Functions

### `create_visual_symbol(symbol: str, meaning: str, quantum_state: Optional[Dict]) -> VisualSymbol`
Factory function to create a quantum-aware visual symbol.

**Example:**
```python
symbol = create_visual_symbol(
    "🌟",
    "consciousness star",
    quantum_state={"coherence": 0.9, "trust": 0.8}
)
```

### `create_perception_field(observer_id: str, consciousness_level: float) -> QuantumPerceptionField`
Initialize a quantum perception field for an observer.

**Example:**
```python
field = create_perception_field("main_observer", consciousness_level=0.7)
```

### `create_consciousness_layer(matriz_compatible: bool, constellation_stars: Optional[List[str]]) -> ConsciousnessIntegration`
Create a consciousness integration layer.

**Example:**
```python
consciousness = create_consciousness_layer(
    matriz_compatible=True,
    constellation_stars=["vision", "quantum", "dream"]
)
```

---

## Data Classes

### QuantumField
```python
@dataclass
class QuantumField:
    coherence: float = 1.0
    entropy: float = 0.0
    trust: float = 0.5
    amplitude: complex = complex(1.0, 0.0)
    phase: float = 0.0
    entangled_symbols: List[str]
    entanglement_strength: Dict[str, float]
    observation_count: int = 0
```

### PerceptionToken
```python
@dataclass
class PerceptionToken:
    token_id: str
    visual_data: np.ndarray
    semantic_embedding: np.ndarray
    salience: float = 0.5
    confidence: float = 0.5
    novelty: float = 0.5
    reasoning_chain: List[str]
    derived_tokens: List[str]
```

### EmergentSymbol
```python
@dataclass
class EmergentSymbol:
    origin_symbols: List[str]
    emergence_time: float
    observation_threshold: int = 10
    current_observations: int = 0
    complexity: float = 1.0
    information_content: float = 1.0
    semantic_coherence: float = 0.5
```

### ObserverEffect
```python
@dataclass
class ObserverEffect:
    observer_id: str
    consciousness_level: float
    observation_type: ObservationType
    intent_vector: Optional[np.ndarray]
    emotional_state: Optional[Dict[str, float]]
```

---

## Enums

### QuantumState
```python
class QuantumState(Enum):
    SUPERPOSITION = "superposition"
    COLLAPSED = "collapsed"
    ENTANGLED = "entangled"
    DECOHERENT = "decoherent"
```

### SymbolicPhase
```python
class SymbolicPhase(Enum):
    NASCENT = "nascent"
    EMERGING = "emerging"
    STABLE = "stable"
    EVOLVING = "evolving"
    TRANSCENDENT = "transcendent"
```

### ObservationType
```python
class ObservationType(Enum):
    PASSIVE = "passive"
    ACTIVE = "active"
    INTENTIONAL = "intentional"
    UNCONSCIOUS = "unconscious"
    COLLECTIVE = "collective"
```

---

## Constants

### Performance Targets
- `MAX_LATENCY_MS`: 50ms for symbol operations
- `COHERENCE_THRESHOLD`: 0.7 minimum for stability
- `DECOHERENCE_RATE`: 0.01 per observation
- `EMERGENCE_THRESHOLD`: 5-10 observations
- `RECURSION_DEPTH`: 10 maximum

### Quantum Mechanics
- `COLLAPSE_STRENGTH_PASSIVE`: 0.1
- `COLLAPSE_STRENGTH_ACTIVE`: 0.5
- `COLLAPSE_STRENGTH_INTENTIONAL`: 0.9
- `ENTANGLEMENT_DECAY_RATE`: 0.01
- `FIELD_TEMPERATURE_RANGE`: [0.1, 1.0]

### Constellation Integration
- `CONSTELLATION_STARS`: ["identity", "memory", "vision", "bio", "dream", "ethics", "guardian", "quantum"]
- `EMERGENCE_BONUS`: 0.2 for collective consciousness

---

## Error Handling

### Common Exceptions

```python
class QuantumCoherenceError(Exception):
    """Raised when field coherence drops below threshold"""

class EntanglementError(Exception):
    """Raised when entanglement cannot be established"""

class EmergenceError(Exception):
    """Raised when emergence conditions not met"""

class ObserverNotFoundError(Exception):
    """Raised when observer not registered"""
```

### Error Handling Example

```python
try:
    field = create_perception_field("observer", 0.8)
    symbol = create_visual_symbol("🌟", "star")
    field.add_symbol(symbol)

    # Attempt observation
    result = field.observe_symbol(
        symbol.state.symbol_id,
        observation_type=ObservationType.INTENTIONAL
    )

except QuantumCoherenceError as e:
    # Stabilize field
    field.stabilize(energy=0.2)

except EntanglementError as e:
    # Retry with lower strength
    field.entangle_symbols(id1, id2, strength=0.5)
```

---

## Thread Safety

All core classes are NOT thread-safe by default. For concurrent access:

```python
import threading

class ThreadSafeField:
    def __init__(self):
        self.field = create_perception_field("main", 0.7)
        self.lock = threading.Lock()

    def observe_symbol(self, symbol_id):
        with self.lock:
            return self.field.observe_symbol(symbol_id)
```

---

## Memory Management

### Resource Limits
- Max symbols per field: 10,000
- Max entangled pairs: 5,000
- Max perception tokens per symbol: 50
- Memory per symbol: ~10KB
- Memory per field: ~100MB

### Cleanup

```python
# Clean up unused symbols
field.symbols = {
    id: sym for id, sym in field.symbols.items()
    if sym.state.quantum_field.observation_count > 0
}

# Remove weak entanglements
field.entangled_pairs = [
    p for p in field.entangled_pairs
    if p.entanglement_strength > 0.01
]
```

---

## Best Practices

1. **Coherence Management**
   - Monitor field coherence regularly
   - Stabilize when below 0.7
   - Limit observation strength for preservation

2. **Entanglement**
   - Start with moderate strength (0.5-0.7)
   - Monitor correlation regularly
   - Refresh weakening entanglements

3. **Emergence**
   - Allow sufficient observations (5-10)
   - Maintain moderate entropy (0.4-0.6)
   - Don't force emergence

4. **Consciousness**
   - Register observers before processing
   - Match consciousness levels appropriately
   - Use temporal recursion for continuity

5. **MATRIZ Integration**
   - Always emit nodes for governance
   - Include complete provenance
   - Maintain signal contracts

---

## Version History

- **v1.0.0** (2024-10-23): Initial release with quantum perception, recursive emergence, neuro-symbolic bridge, and consciousness integration