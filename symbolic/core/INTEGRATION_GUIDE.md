# Integration Guide - Quantum Visual Symbol System

## Overview

This guide helps developers integrate the Quantum Visual Symbol System into LUKHAS AGI components.

## Installation

### Prerequisites

```bash
# Required Python version
python --version  # 3.9+

# Install dependencies
pip install numpy
pip install dataclasses  # If Python < 3.10
```

### Import Structure

```python
# Basic imports
from symbolic.core import VisualSymbol, create_visual_symbol

# Advanced imports
from symbolic.core import (
    QuantumPerceptionField,
    RecursiveSymbolicEngine,
    NeuroSymbolicBridge,
    ConsciousnessIntegration
)

# Type imports
from symbolic.core.visual_symbol import (
    QuantumState,
    SymbolicPhase,
    QuantumField,
    PerceptionToken
)
```

## Integration Patterns

### 1. Basic Visual Processing

For simple visual symbol creation and observation:

```python
from symbolic.core import create_visual_symbol

class SimpleVisionProcessor:
    def process_image(self, image_data):
        # Extract symbol from image (your logic)
        symbol_char = self.extract_symbol(image_data)
        meaning = self.interpret_symbol(symbol_char)

        # Create quantum visual symbol
        symbol = create_visual_symbol(
            symbol=symbol_char,
            meaning=meaning,
            quantum_state={"coherence": 0.9}
        )

        # Observe to collapse wave function
        result = symbol.observe("vision_processor", 0.7)

        return {
            "symbol": symbol_char,
            "meaning": meaning,
            "consciousness": symbol.measure_consciousness(),
            "quantum_state": result["quantum_state"]
        }
```

### 2. MATRIZ Integration

Emit MATRIZ nodes for governance and tracking:

```python
from symbolic.core import VisualSymbol

class MatrizVisionAdapter:
    def __init__(self, matriz_hub):
        self.matriz_hub = matriz_hub

    def process_symbol(self, symbol: VisualSymbol):
        # Process symbol
        symbol.observe("matriz_adapter", 0.5)

        # Convert to MATRIZ node
        matriz_node = symbol.to_matriz_node()

        # Emit to MATRIZ hub
        self.matriz_hub.emit_node(matriz_node)

        # Send signals
        self.matriz_hub.send_signal({
            "signal": "symbol_observed",
            "data": {
                "symbol_id": symbol.state.symbol_id,
                "quantum_state": symbol.state.quantum_state.value
            }
        })
```

### 3. Consciousness Processing Pipeline

Full consciousness-aware processing:

```python
from symbolic.core import (
    create_perception_field,
    create_consciousness_layer,
    NeuroSymbolicBridge
)

class ConsciousVisionPipeline:
    def __init__(self, observer_id="conscious_vision"):
        # Initialize components
        self.field = create_perception_field(observer_id, 0.8)
        self.consciousness = create_consciousness_layer(
            matriz_compatible=True,
            constellation_stars=["vision", "quantum", "memory"]
        )
        self.bridge = NeuroSymbolicBridge()

    def process_visual_input(self, visual_data):
        # Create symbols from visual data
        symbols = self.create_symbols_from_data(visual_data)

        # Add to quantum field
        for symbol in symbols:
            self.field.add_symbol(symbol)

        # Process through consciousness
        results = []
        for symbol in symbols:
            # Consciousness processing
            conscious_result = self.consciousness.process_with_consciousness(
                symbol,
                self.field.observer_id
            )

            # Neuro-symbolic bridging
            bridge_result = self.bridge.process_visual_symbol(symbol)

            results.append({
                "symbol": symbol.state.symbol,
                "consciousness": conscious_result,
                "scene_graph": bridge_result
            })

        # Generate scene graph
        scene = self.bridge.generate_scene_graph(symbols)

        # Measure collective consciousness
        collective = self.consciousness.measure_collective_consciousness(symbols)

        return {
            "symbols": results,
            "scene": scene,
            "collective_consciousness": collective
        }
```

### 4. Entanglement and Correlation

Create quantum correlations between symbols:

```python
from symbolic.core import create_visual_symbol
from symbolic.core.quantum_perception import ObservationType

class EntanglementProcessor:
    def __init__(self):
        self.field = create_perception_field("entangle_proc", 0.9)

    def create_entangled_pair(self, symbol1_data, symbol2_data):
        # Create symbols
        symbol1 = create_visual_symbol(
            symbol1_data["symbol"],
            symbol1_data["meaning"]
        )
        symbol2 = create_visual_symbol(
            symbol2_data["symbol"],
            symbol2_data["meaning"]
        )

        # Add to field
        id1 = self.field.add_symbol(symbol1)
        id2 = self.field.add_symbol(symbol2)

        # Create entanglement
        success = self.field.entangle_symbols(id1, id2, strength=0.8)

        if success:
            # Observe one symbol
            self.field.observe_symbol(
                id1,
                observation_type=ObservationType.INTENTIONAL
            )

            # Check correlation (other symbol affected)
            state = self.field.measure_field_state()
            return {
                "entangled": True,
                "correlation": state["symbol_metrics"]["avg_correlation"]
            }

        return {"entangled": False}
```

### 5. Recursive Emergence

Enable symbolic self-creation:

```python
from symbolic.core import RecursiveSymbolicEngine

class EmergenceManager:
    def __init__(self):
        self.engine = RecursiveSymbolicEngine(recursion_depth=10)
        self.symbols = []

    def add_symbol(self, symbol):
        self.symbols.append(symbol)

        # Check for emergence potential
        if len(self.symbols) >= 3:
            potential = self.engine.measure_emergence_potential(
                self.symbols[-3:]
            )

            if potential > 0.7:
                # Compress to Q-symbol
                q_symbol = self.engine.compress_symbols(self.symbols[-3:])

                # Check for contradictions
                for i, s1 in enumerate(self.symbols[-3:]):
                    for s2 in self.symbols[-3:][i+1:]:
                        if self.engine.detect_contradiction(s1, s2):
                            # Attempt resolution
                            emergent = self.engine.resolve_contradictions()
                            if emergent:
                                return {
                                    "emerged": True,
                                    "emergent_symbol": emergent,
                                    "q_symbol": q_symbol
                                }

        return {"emerged": False}

    def evolve(self):
        # Evolve symbolic landscape
        self.engine.evolve_symbolic_landscape(time_step=0.01)
```

## Constellation Framework Integration

### Mapping Symbols to Stars

```python
from symbolic.core import ConsciousnessIntegration

class ConstellationMapper:
    def __init__(self):
        self.consciousness = ConsciousnessIntegration()
        self.star_mappings = {
            "identity": [],
            "memory": [],
            "vision": [],
            "bio": [],
            "dream": [],
            "ethics": [],
            "guardian": [],
            "quantum": []
        }

    def map_symbol_to_stars(self, symbol):
        # Get constellation integration
        integration = self.consciousness.integrate_with_constellation(symbol)

        # Map to appropriate stars based on strength
        for star, strength in integration.items():
            if strength > 0.5:
                self.star_mappings[star].append({
                    "symbol": symbol.state.symbol,
                    "strength": strength
                })

        return integration

    def get_dominant_star(self, symbol):
        integration = self.consciousness.integrate_with_constellation(symbol)
        return max(integration, key=integration.get)
```

## Event Handling

### Signal Reception

```python
from symbolic.core import VisualSymbol

class SymbolEventHandler:
    def __init__(self):
        self.handlers = {
            "observe_symbol": self.handle_observe,
            "entangle_symbols": self.handle_entangle,
            "evolve_symbol": self.handle_evolve
        }

    def handle_signal(self, signal):
        handler = self.handlers.get(signal["type"])
        if handler:
            return handler(signal["data"])

    def handle_observe(self, data):
        symbol = self.get_symbol(data["symbol_id"])
        return symbol.observe(
            data["observer_id"],
            data["observation_strength"]
        )

    def handle_entangle(self, data):
        symbol1 = self.get_symbol(data["symbol1_id"])
        symbol2 = self.get_symbol(data["symbol2_id"])
        return symbol1.entangle(symbol2, data["strength"])

    def handle_evolve(self, data):
        symbol = self.get_symbol(data["symbol_id"])
        return symbol.evolve(data["drift_rate"])
```

## Performance Optimization

### Batch Processing

```python
class BatchSymbolProcessor:
    def __init__(self):
        self.field = create_perception_field("batch_proc", 0.7)

    def process_batch(self, symbol_batch):
        # Add all symbols first
        symbol_ids = []
        for sym_data in symbol_batch:
            symbol = create_visual_symbol(
                sym_data["symbol"],
                sym_data["meaning"]
            )
            symbol_id = self.field.add_symbol(symbol)
            symbol_ids.append(symbol_id)

        # Batch observations
        results = []
        for symbol_id in symbol_ids:
            # Use passive observation for batch
            result = self.field.observe_symbol(
                symbol_id,
                observation_type=ObservationType.PASSIVE
            )
            results.append(result)

        # Periodic field stabilization
        if len(symbol_ids) > 100:
            self.field.stabilize(energy=0.1)

        return results
```

### Memory Management

```python
class MemoryOptimizedProcessor:
    def __init__(self, max_symbols=1000):
        self.max_symbols = max_symbols
        self.field = create_perception_field("mem_opt", 0.6)

    def add_symbol_with_cleanup(self, symbol):
        # Check capacity
        if len(self.field.symbols) >= self.max_symbols:
            self.cleanup_old_symbols()

        # Add new symbol
        return self.field.add_symbol(symbol)

    def cleanup_old_symbols(self):
        # Remove symbols with low observation count
        to_remove = []
        for sym_id, symbol in self.field.symbols.items():
            if symbol.state.quantum_field.observation_count < 2:
                to_remove.append(sym_id)

        for sym_id in to_remove[:100]:  # Remove max 100 at a time
            del self.field.symbols[sym_id]

        # Clean up weak entanglements
        self.field.entangled_pairs = [
            p for p in self.field.entangled_pairs
            if p.entanglement_strength > 0.1
        ]
```

## Testing Integration

### Unit Test Example

```python
import unittest
from symbolic.core import create_visual_symbol, QuantumState

class TestSymbolIntegration(unittest.TestCase):
    def setUp(self):
        self.symbol = create_visual_symbol("🌟", "test_star")

    def test_observation_collapses_wave_function(self):
        # Initial state should be superposition
        self.assertEqual(
            self.symbol.state.quantum_state,
            QuantumState.SUPERPOSITION
        )

        # Strong observation should collapse
        self.symbol.observe("test_observer", 0.9)

        # Should be collapsed
        self.assertEqual(
            self.symbol.state.quantum_state,
            QuantumState.COLLAPSED
        )

    def test_entanglement_creates_correlation(self):
        symbol2 = create_visual_symbol("🌙", "test_moon")

        # Create entanglement
        success = self.symbol.entangle(symbol2, 0.8)
        self.assertTrue(success)

        # Check both are entangled
        self.assertEqual(
            self.symbol.state.quantum_state,
            QuantumState.ENTANGLED
        )
        self.assertEqual(
            symbol2.state.quantum_state,
            QuantumState.ENTANGLED
        )

    def test_consciousness_measurement(self):
        # Measure initial consciousness
        initial = self.symbol.measure_consciousness()
        self.assertGreaterEqual(initial, 0.0)
        self.assertLessEqual(initial, 1.0)

        # Observations should increase consciousness
        for _ in range(10):
            self.symbol.observe("test", 0.3)

        final = self.symbol.measure_consciousness()
        self.assertGreater(final, initial)
```

### Integration Test Example

```python
import pytest
from symbolic.core import (
    create_perception_field,
    create_visual_symbol,
    NeuroSymbolicBridge,
    ConsciousnessIntegration
)

@pytest.fixture
def setup_pipeline():
    field = create_perception_field("test_field", 0.7)
    bridge = NeuroSymbolicBridge()
    consciousness = ConsciousnessIntegration()
    return field, bridge, consciousness

def test_full_pipeline(setup_pipeline):
    field, bridge, consciousness = setup_pipeline

    # Create test symbols
    symbols = [
        create_visual_symbol("🌟", "star"),
        create_visual_symbol("🌙", "moon"),
        create_visual_symbol("☀️", "sun")
    ]

    # Add to field
    for symbol in symbols:
        field.add_symbol(symbol)

    # Process through bridge
    for symbol in symbols:
        result = bridge.process_visual_symbol(symbol)
        assert "symbol_id" in result
        assert "perception_value" in result

    # Generate scene graph
    scene = bridge.generate_scene_graph(symbols)
    assert len(scene.objects) == 3

    # Process through consciousness
    for symbol in symbols:
        result = consciousness.process_with_consciousness(
            symbol,
            "test_observer"
        )
        assert "consciousness_level" in result
        assert "synthetic_emotion" in result

    # Measure collective
    collective = consciousness.measure_collective_consciousness(symbols)
    assert 0.0 <= collective <= 1.0
```

## Debugging

### Enable Debug Logging

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Get logger for symbolic core
logger = logging.getLogger('symbolic.core')
logger.setLevel(logging.DEBUG)

# Debug symbol operations
def debug_symbol(symbol):
    logger.debug(f"Symbol: {symbol.state.symbol}")
    logger.debug(f"Quantum State: {symbol.state.quantum_state}")
    logger.debug(f"Coherence: {symbol.state.quantum_field.coherence}")
    logger.debug(f"Entropy: {symbol.state.quantum_field.entropy}")
    logger.debug(f"Consciousness: {symbol.measure_consciousness()}")
```

### State Inspection

```python
def inspect_field_state(field):
    state = field.measure_field_state()

    print(f"Field State Inspection")
    print(f"=" * 50)
    print(f"Symbols: {state['symbol_count']}")
    print(f"Entangled Pairs: {state['entangled_pairs']}")
    print(f"Global Coherence: {state['field_metrics']['global_coherence']:.3f}")
    print(f"Field Entropy: {state['field_metrics']['entropy']:.3f}")
    print(f"Temperature: {state['field_metrics']['temperature']:.3f}")
    print(f"Observations: {state['observation_count']}")

    print(f"\nSymbol Metrics:")
    print(f"  Avg Coherence: {state['symbol_metrics']['avg_coherence']:.3f}")
    print(f"  Avg Entropy: {state['symbol_metrics']['avg_entropy']:.3f}")
    print(f"  Avg Correlation: {state['symbol_metrics']['avg_correlation']:.3f}")

    print(f"\nQuantum State Distribution:")
    for state_type, count in state['symbol_metrics']['state_distribution'].items():
        print(f"  {state_type}: {count}")
```

## Common Pitfalls

### 1. Low Coherence
**Problem**: Field coherence drops below threshold.

**Solution**:
```python
# Monitor and stabilize
if field.field_coherence.global_coherence < 0.7:
    field.stabilize(energy=0.2)
```

### 2. Entanglement Decay
**Problem**: Entanglements weaken over time.

**Solution**:
```python
# Refresh entanglements periodically
for pair in field.entangled_pairs:
    if pair.entanglement_strength < 0.3:
        field.entangle_symbols(
            pair.symbol_a.state.symbol_id,
            pair.symbol_b.state.symbol_id,
            strength=0.7
        )
```

### 3. Memory Leaks
**Problem**: Symbols accumulate without cleanup.

**Solution**:
```python
# Implement periodic cleanup
def cleanup_unused_symbols(field, threshold=100):
    if len(field.symbols) > threshold:
        # Remove least observed symbols
        sorted_symbols = sorted(
            field.symbols.items(),
            key=lambda x: x[1].state.quantum_field.observation_count
        )
        for sym_id, _ in sorted_symbols[:20]:
            del field.symbols[sym_id]
```

## Support

For issues or questions:
- GitHub: github.com/lukhas/quantum-visual-symbols
- Documentation: docs.lukhas.ai/visual-symbols
- Support: support@lukhas.ai