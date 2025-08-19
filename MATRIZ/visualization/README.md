# MATADA Graph Visualization System

A production-ready interactive visualization system for MATADA cognitive nodes and their relationships. This system provides comprehensive graph analysis, temporal evolution tracking, and interactive exploration capabilities for understanding cognitive processing chains.

## Features

### 🎨 Interactive Visualizations
- **Real-time interactive plots** with hover details and zoom/pan
- **Color-coded node types** with configurable visual properties
- **Multiple layout algorithms** (force-directed, hierarchical, circular, spiral)
- **Link type visualization** with different colors and styles
- **Node size scaling** based on importance metrics

### ⏱️ Temporal Analysis
- **Temporal evolution animations** showing how graphs develop over time
- **Time-based filtering** to view specific time periods
- **Activity tracking** with timestamps and duration analysis
- **Snapshot management** for comparing different time states

### 📊 Statistical Analysis
- **Comprehensive metrics dashboard** with multiple subplots
- **Graph topology analysis** (density, centrality, clustering)
- **Node confidence and salience distributions**
- **Link type analysis** and relationship patterns
- **Performance monitoring** with caching for large graphs

### 🔍 Search and Filtering
- **Advanced node search** by type, confidence, salience, time range
- **Interactive filtering** with real-time updates
- **Path analysis** for understanding information flow
- **Critical path highlighting** for important connections

### 📤 Export Capabilities
- **Multiple file formats** (JSON, GraphML, GEXF, HTML, PNG, PDF)
- **Complete data preservation** including MATADA metadata
- **Layout position saving** for consistent visualizations
- **Batch export** for multiple visualization types

## Installation

### Prerequisites
- Python 3.7+
- Required packages: `networkx`, `plotly`, `pandas`, `numpy`

### Install Dependencies
```bash
pip install networkx plotly pandas numpy
```

### Optional Dependencies
For enhanced features:
```bash
pip install pygraphviz  # For hierarchical layouts
pip install kaleido     # For static image export
```

## Quick Start

### Basic Usage
```python
from visualization import MATADAGraphViewer

# Create viewer
viewer = MATADAGraphViewer(width=1200, height=800)

# Add MATADA nodes
viewer.add_node(matada_node_data)

# Create interactive visualization
fig = viewer.create_interactive_plot()
fig.show()

# Export as HTML
fig.write_html("my_graph.html")
```

### Batch Operations
```python
# Add multiple nodes efficiently
nodes = [node1, node2, node3, ...]
success, failed = viewer.add_nodes_batch(nodes)

# Search for specific nodes
high_confidence = viewer.search_nodes(min_confidence=0.8)
emotion_nodes = viewer.search_nodes(node_type="EMOTION")
```

### Advanced Visualizations
```python
# Statistics dashboard
stats_fig = viewer.create_statistics_dashboard()

# Temporal animation
animation_fig = viewer.create_temporal_animation()

# Different layouts
layouts = ['force_directed', 'hierarchical', 'circular', 'spiral']
for layout in layouts:
    fig = viewer.create_interactive_plot(layout=layout)
    fig.write_html(f"graph_{layout}.html")
```

## MATADA Node Format

The visualization system expects nodes in the standard MATADA format:

```json
{
  "version": 1,
  "id": "unique_node_id",
  "type": "NODE_TYPE",
  "state": {
    "confidence": 0.85,
    "salience": 0.7,
    "valence": 0.5,
    "arousal": 0.4,
    // additional state data
  },
  "timestamps": {
    "created_ts": 1640995200000
  },
  "provenance": {
    "producer": "NodeClass",
    "capabilities": ["capability1", "capability2"],
    "tenant": "tenant_id",
    "trace_id": "trace_id",
    "consent_scopes": ["scope1"]
  },
  "links": [
    {
      "target_node_id": "target_id",
      "link_type": "causal",
      "direction": "unidirectional",
      "weight": 0.8
    }
  ],
  "evolves_to": [],
  "triggers": [],
  "reflections": []
}
```

## Supported Node Types

The system supports all standard MATADA node types with appropriate visual styling:

### Sensory Nodes
- `SENSORY_IMG` - Visual input (red square)
- `SENSORY_AUD` - Audio input (teal circle) 
- `SENSORY_VID` - Video input (blue diamond)
- `SENSORY_TOUCH` - Touch input (green triangle)

### Cognitive Nodes
- `EMOTION` - Emotional processing (yellow star)
- `INTENT` - Intentions (plum hexagon)
- `DECISION` - Decision points (coral octagon)
- `CONTEXT` - Contextual information (purple circle)
- `MEMORY` - Memory nodes (pink circle)
- `REFLECTION` - Introspection (orange triangle)

### Processing Nodes
- `COMPUTATION` - Mathematical/logical (light blue circle)
- `VALIDATION` - Validation results (ocean blue hexagon)
- `CAUSAL` - Causal relationships (brown circle)
- `TEMPORAL` - Temporal links (sea green circle)
- `AWARENESS` - Awareness states (cyan star)
- `HYPOTHESIS` - Hypotheses (violet diamond)

### Special Nodes
- `REPLAY` - Replay/simulation (gray square)
- `DRM` - Memory reconstruction (dark gray triangle)

## Link Types

Connections between nodes are visualized with different colors and styles:

- `temporal` - Time-based connections (blue solid)
- `causal` - Cause-effect relationships (orange-red dashed)
- `semantic` - Meaning-based connections (green dotted)
- `emotional` - Emotion-based links (yellow dash-dot)
- `spatial` - Space-based connections (purple solid)
- `evidence` - Evidence relationships (pink dashed)

## API Reference

### MATADAGraphViewer Class

#### Constructor
```python
MATADAGraphViewer(width=1200, height=800, show_labels=True, enable_physics=True)
```

#### Core Methods
- `add_node(matada_node)` - Add a single MATADA node
- `add_nodes_batch(nodes)` - Add multiple nodes efficiently
- `remove_node(node_id)` - Remove a node from the graph
- `get_node_details(node_id)` - Get complete node information
- `clear_graph()` - Clear all graph data

#### Search Methods
- `search_nodes(**criteria)` - Search nodes by various criteria
- `calculate_graph_metrics()` - Compute comprehensive graph statistics
- `get_summary()` - Get overall graph summary

#### Visualization Methods
- `create_interactive_plot(**options)` - Create main interactive visualization
- `create_temporal_animation(**options)` - Create temporal evolution animation
- `create_statistics_dashboard()` - Create comprehensive statistics dashboard

#### Export Methods
- `export_graph(filepath, format)` - Export graph data
- `export_visualization(filepath, format)` - Export visualization
- `import_graph(filepath, format)` - Import graph data

### Configuration Classes

#### NodeTypeConfig
- `get_color(node_type)` - Get color for node type
- `get_shape(node_type)` - Get shape for node type
- `get_size_multiplier(node_type)` - Get size scaling factor

#### LinkTypeConfig
- `get_color(link_type)` - Get color for link type
- `get_style(link_type)` - Get line style for link type
- `get_width_multiplier(link_type)` - Get width scaling factor

## Examples

### Example 1: Basic Cognitive Chain
See `example_usage.py` for a complete example showing:
- Sensory input processing
- Memory retrieval
- Emotional response
- Decision making
- Visualization and analysis

### Example 2: Mathematical Processing
```python
# Create a math processing chain
math_viewer = MATADAGraphViewer()

# Add computation node
computation_node = {
    "id": "math_001",
    "type": "COMPUTATION", 
    "state": {"confidence": 0.95, "salience": 0.8, "expression": "2+3*4", "result": 14},
    # ... other required fields
}
math_viewer.add_node(computation_node)

# Add validation node
validation_node = {
    "id": "validate_001",
    "type": "VALIDATION",
    "state": {"confidence": 0.9, "salience": 0.6, "validation_result": True},
    "links": [{"target_node_id": "math_001", "link_type": "evidence"}],
    # ... other required fields  
}
math_viewer.add_node(validation_node)

# Visualize
fig = math_viewer.create_interactive_plot(title="Mathematical Processing Chain")
fig.show()
```

### Example 3: Performance Analysis
```python
# Analyze graph performance
metrics = viewer.calculate_graph_metrics()
print(f"Graph density: {metrics['Density']:.3f}")
print(f"Average confidence: {metrics['Avg Confidence']:.3f}")
print(f"Node type diversity: {metrics['Node Type Diversity']}")

# Find bottlenecks
high_centrality = viewer.search_nodes(min_confidence=0.9)
print(f"High-importance nodes: {len(high_centrality)}")
```

## Performance Considerations

### Large Graphs
- **Sampling**: Centrality calculations use sampling for graphs >100 nodes
- **Caching**: Layout positions and metrics are cached for performance
- **Batch operations**: Use `add_nodes_batch()` for multiple nodes
- **Selective visualization**: Use filtering to show subsets of large graphs

### Memory Usage
- **Node data storage**: Full MATADA nodes are stored separately from graph structure
- **Layout caching**: Computed layouts are cached but can be cleared
- **Temporal snapshots**: Automatically managed for efficiency

### Optimization Tips
```python
# For large graphs, disable expensive features
viewer = MATADAGraphViewer(enable_physics=False, show_labels=False)

# Use simpler layouts for speed
fig = viewer.create_interactive_plot(layout='circular')

# Cache frequently accessed data
metrics = viewer.calculate_graph_metrics()  # Cached for 5 minutes
```

## Error Handling

The system includes comprehensive error handling:

- **Input validation**: MATADA node format verification
- **Graceful degradation**: Fallback layouts when algorithms fail
- **Logging**: Detailed logging for debugging and monitoring
- **Exception safety**: Robust error handling prevents crashes

## Troubleshooting

### Common Issues

**Dependencies Missing**
```bash
# Install required packages
pip install networkx plotly pandas numpy
```

**Hierarchical Layout Fails**
```bash
# Install optional dependency
pip install pygraphviz
```

**Export Fails**
```bash
# Install for image export
pip install kaleido
```

**Performance Issues with Large Graphs**
```python
# Use sampling and simpler layouts
viewer = MATADAGraphViewer(enable_physics=False)
fig = viewer.create_interactive_plot(layout='circular')
```

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Now all operations will show detailed logging
viewer = MATADAGraphViewer()
```

## Contributing

To extend the visualization system:

1. **Add new node types**: Update `NodeTypeConfig` with colors/shapes
2. **Add new link types**: Update `LinkTypeConfig` with styles
3. **Add new layouts**: Extend the `_compute_layout()` method
4. **Add new metrics**: Extend `calculate_graph_metrics()`
5. **Add new visualizations**: Create new methods following existing patterns

## License

This visualization system is part of the MATADA-AGI project and follows the same licensing terms.