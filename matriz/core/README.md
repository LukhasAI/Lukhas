---
status: wip
type: documentation
---
# MATRIZ Cognitive Node Interface

This document describes the base `CognitiveNode` interface that all MATRIZ nodes must implement for complete interpretability and governance.

## Overview

The MATRIZ (Multimodal Adaptive Temporal Architecture for Dynamic Awareness) cognitive architecture ensures complete traceability of all cognitive processes through standardized node formats. Every cognitive operation must emit MATRIZ format nodes that can be audited, traced, and governed.

## Core Interface

### CognitiveNode (Abstract Base Class)

All cognitive nodes must inherit from `CognitiveNode` and implement two key methods:

```python
from matriz_agi.core import CognitiveNode, NodeState

class MyNode(CognitiveNode):
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input and return result with MATADA node"""
        # Your processing logic here

    def validate_output(self, output: Dict[str, Any]) -> bool:
        """Validate the output format and quality"""
        # Your validation logic here
```

### Required Methods

#### `process(input_data: Dict) -> Dict`

**Purpose**: Main processing method that must return both results and MATADA node.

**Must Return**:
- `answer`: The processing result
- `confidence`: Confidence level (0.0-1.0)
- `matada_node`: Complete MATADA format node
- `processing_time`: Time taken in seconds

**Example**:
```python
def process(self, input_data):
    start_time = time.time()

    # Your processing logic
    result = self.do_processing(input_data['query'])

    # Create MATADA node
    state = NodeState(confidence=0.9, salience=0.8)
    matada_node = self.create_matada_node(
        node_type="DECISION",
        state=state,
        additional_data={'result': result}
    )

    return {
        'answer': f"The result is {result}",
        'confidence': 0.9,
        'matada_node': matada_node,
        'processing_time': time.time() - start_time
    }
```

#### `validate_output(output: Dict) -> bool`

**Purpose**: Validate output format, MATADA node structure, and result quality.

**Should Check**:
- Required fields present
- MATADA node schema compliance
- Confidence matches result quality
- Logical consistency
- Ethical compliance (if applicable)

### Helper Methods

#### `create_matada_node()`

Creates properly formatted MATADA nodes:

```python
matada_node = self.create_matada_node(
    node_type="DECISION",           # Required: MATADA node type
    state=NodeState(0.9, 0.8),     # Required: confidence, salience
    links=[...],                   # Optional: connections
    triggers=[...],                # Optional: what triggered this
    reflections=[...],             # Optional: introspective logs
    additional_data={...}          # Optional: extra state data
)
```

#### `create_reflection()`

Creates introspective reflection logs:

```python
reflection = self.create_reflection(
    reflection_type="affirmation",  # regret, affirmation, etc.
    cause="Successfully processed input",
    old_state={...},               # Optional
    new_state={...}                # Optional
)
```

#### `create_link()`

Creates connections between nodes:

```python
link = self.create_link(
    target_node_id="other-node-id",
    link_type="causal",            # causal, temporal, semantic, etc.
    direction="unidirectional",    # bidirectional, unidirectional
    weight=0.8,                    # Optional: 0.0-1.0
    explanation="Because X caused Y"  # Optional
)
```

## MATADA Node Format

Every node must produce nodes conforming to this schema:

```json
{
  "version": 1,
  "id": "unique-node-id",
  "type": "DECISION",                    // See allowed types below
  "state": {
    "confidence": 0.9,                   // Required: 0.0-1.0
    "salience": 0.8,                     // Required: 0.0-1.0
    "valence": 0.5,                      // Optional: -1.0 to 1.0
    "arousal": 0.7,                      // Optional: 0.0-1.0
    // ... other optional state fields
    // ... custom additional data
  },
  "timestamps": {
    "created_ts": 1640995200000          // Epoch milliseconds
  },
  "provenance": {
    "producer": "module.path.NodeClass",
    "capabilities": ["reasoning", "math"],
    "tenant": "default",
    "trace_id": "trace-uuid",
    "consent_scopes": ["cognitive_processing"]
  },
  "links": [...],                        // Connections to other nodes
  "evolves_to": [...],                   // Future evolution paths
  "triggers": [...],                     // What triggered this node
  "reflections": [...],                  // Introspective logs
  "schema_ref": "lukhas://schemas/matada_node_v1.json"
}
```

### Allowed Node Types

- `SENSORY_IMG`, `SENSORY_AUD`, `SENSORY_VID`, `SENSORY_TOUCH`: Sensory inputs
- `EMOTION`: Emotional states and reactions
- `INTENT`: Detected user intents and goals
- `DECISION`: Decision-making processes
- `CONTEXT`: Contextual understanding
- `MEMORY`: Memory retrieval and storage
- `REFLECTION`: Introspective analysis
- `CAUSAL`: Causal reasoning
- `TEMPORAL`: Temporal reasoning
- `AWARENESS`: Self-awareness processes
- `HYPOTHESIS`: Hypothesis formation
- `REPLAY`: Experience replay
- `DRM`: Dream/simulation states

## State Fields

### Required Fields
- `confidence`: How confident the node is in its output (0.0-1.0)
- `salience`: How important/relevant this node is (0.0-1.0)

### Optional Emotional Fields
- `valence`: Emotional positivity/negativity (-1.0 to 1.0)
- `arousal`: Emotional intensity/activation (0.0-1.0)

### Optional Cognitive Fields
- `novelty`: How novel/surprising this is (0.0-1.0)
- `urgency`: Time pressure factor (0.0-1.0)
- `shock_factor`: Unexpectedness (0.0-1.0)
- `risk`: Risk assessment (0.0-1.0)
- `utility`: Value/usefulness (0.0-1.0)

## Example Implementation

See `example_node.py` for a complete working example of a mathematical reasoning node.

```python
# Basic usage
from matriz_agi.core import CognitiveNode, NodeState

class MyReasoningNode(CognitiveNode):
    def __init__(self):
        super().__init__(
            node_name="my_reasoner",
            capabilities=["reasoning", "analysis"],
            tenant="default"
        )

    def process(self, input_data):
        # Process the input
        result = self.analyze(input_data['query'])

        # Create state
        state = NodeState(
            confidence=0.85,
            salience=0.9,
            valence=0.6  # Positive outcome
        )

        # Create MATADA node
        matada_node = self.create_matada_node(
            node_type="DECISION",
            state=state,
            additional_data={'analysis_result': result}
        )

        return {
            'answer': f"Analysis complete: {result}",
            'confidence': 0.85,
            'matada_node': matada_node,
            'processing_time': 0.1
        }

    def validate_output(self, output):
        # Validate required fields and MATADA node
        return (all(k in output for k in ['answer', 'confidence', 'matada_node'])
                and self.validate_matada_node(output['matada_node']))
```

## Integration with Orchestrator

Nodes integrate with the `CognitiveOrchestrator` for full cognitive workflows:

```python
from matriz_agi.core import CognitiveOrchestrator

# Create orchestrator and register nodes
orchestrator = CognitiveOrchestrator()
orchestrator.register_node('my_reasoner', MyReasoningNode())

# Process queries with full traceability
result = orchestrator.process_query("Analyze this situation")
print(result['answer'])
print(f"Confidence: {result['confidence']}")
print(f"MATADA nodes created: {len(result['matada_nodes'])}")
```

## Key Benefits

1. **Complete Traceability**: Every cognitive step is recorded in MATADA format
2. **Deterministic Processing**: Same inputs always produce same results
3. **Governance Ready**: Full provenance tracking for ethical oversight
4. **Interpretability**: Causal chains can be reconstructed and explained
5. **Standardization**: All nodes follow the same interface and format
6. **Composability**: Nodes can be easily combined and orchestrated

## Testing

Run the comprehensive test suite:

```bash
python3 matada_agi/test_interface.py
```

This validates all interface functionality and demonstrates a complete workflow.

## Next Steps

1. Implement your cognitive nodes by inheriting from `CognitiveNode`
2. Ensure all nodes emit complete MATADA format
3. Test with the provided validation methods
4. Integrate with the orchestrator for full workflows
5. Use the tracing capabilities for interpretability and governance

For more examples and advanced usage, see the `examples/` directory.
