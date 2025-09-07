#!/usr/bin/env python3
"""
Example Usage of MATRIZ Graph Visualization System

This script demonstrates how to use the MATRIZGraphViewer to visualize
cognitive nodes and their relationships in various ways.
"""
import streamlit as st

import time
from typing import Any, Optional

from graph_viewer import MATRIZGraphViewer


def create_sample_matriz_node(
    node_id: str,
    node_type: str,
    confidence: float = 0.8,
    salience: float = 0.7,
    additional_state: Optional[dict] = None,
    links: Optional[list] = None,
) -> dict[str, Any]:
    """Create a sample MATRIZ node for demonstration."""
    state = {
        "confidence": confidence,
        "salience": salience,
        "valence": 0.5,
        "arousal": 0.4,
    }

    if additional_state:
        state.update(additional_state)

    return {
        "version": 1,
        "id": node_id,
        "type": node_type,
        "state": state,
        "timestamps": {"created_ts": int(time.time() * 1000)},
        "provenance": {
            "producer": f"{node_type}Node",
            "capabilities": [f"{node_type.lower(}_processing"],
            "tenant": "demo",
            "trace_id": f"trace_{node_id}",
            "consent_scopes": ["cognitive_processing"],
        },
        "links": links or [],
        "evolves_to": [],
        "triggers": [],
        "reflections": [],
    }


def main():
    """Demonstrate various visualization capabilities."""
    print("MATRIZ Graph Visualization Example")
    print("=" * 40)

    # Create the viewer
    viewer = MATRIZGraphViewer(width=1200, height=800)

    # Example 1: Create a simple cognitive processing chain
    print("\n1. Creating a cognitive processing chain...")

    # Sensory input
    sensory_node = create_sample_matriz_node(
        "sensory_001",
        "SENSORY_IMG",
        confidence=0.9,
        salience=0.8,
        additional_state={"image_classification": "cat", "certainty": 0.92},
    )

    # Memory retrieval
    memory_node = create_sample_matriz_node(
        "memory_001",
        "MEMORY",
        confidence=0.85,
        salience=0.7,
        additional_state={"retrieved_facts": ["cats are mammals", "cats have whiskers"]},
        links=[
            {
                "target_node_id": "sensory_001",
                "link_type": "semantic",
                "direction": "unidirectional",
                "weight": 0.8,
            }
        ],
    )

    # Emotional response
    emotion_node = create_sample_matriz_node(
        "emotion_001",
        "EMOTION",
        confidence=0.75,
        salience=0.9,
        additional_state={"emotion_type": "joy", "intensity": 0.6},
        links=[
            {
                "target_node_id": "sensory_001",
                "link_type": "emotional",
                "direction": "unidirectional",
                "weight": 0.7,
            }
        ],
    )

    # Decision making
    decision_node = create_sample_matriz_node(
        "decision_001",
        "DECISION",
        confidence=0.88,
        salience=0.95,
        additional_state={
            "decision": "approach the cat",
            "rationale": "positive emotional response",
        },
        links=[
            {
                "target_node_id": "memory_001",
                "link_type": "causal",
                "direction": "unidirectional",
                "weight": 0.6,
            },
            {
                "target_node_id": "emotion_001",
                "link_type": "causal",
                "direction": "unidirectional",
                "weight": 0.9,
            },
        ],
    )

    # Add all nodes
    nodes = [sensory_node, memory_node, emotion_node, decision_node]
    success, failed = viewer.add_nodes_batch(nodes)
    print(f"Added {success} nodes successfully, {failed} failed")

    # Example 2: Display graph summary
    print("\n2. Graph Summary:")
    summary = viewer.get_summary()
    for section, data in summary.items():
        print(f"   {section}: {data}")

    # Example 3: Create interactive visualization
    print("\n3. Creating interactive visualization...")
    fig_interactive = viewer.create_interactive_plot(
        layout="force_directed", title="Cognitive Processing Chain - Interactive View"
    )

    # Save to file
    try:
        fig_interactive.write_html("cognitive_chain_interactive.html")
        print("   ✓ Saved to cognitive_chain_interactive.html")
    except Exception as e:
        print(f"   ✗ Could not save HTML: {e}")

    # Example 4: Create statistics dashboard
    print("\n4. Creating statistics dashboard...")
    fig_stats = viewer.create_statistics_dashboard()

    try:
        fig_stats.write_html("cognitive_chain_stats.html")
        print("   ✓ Saved to cognitive_chain_stats.html")
    except Exception as e:
        print(f"   ✗ Could not save stats HTML: {e}")

    # Example 5: Search functionality
    print("\n5. Testing search functionality...")

    # Find high-confidence nodes
    high_conf_nodes = viewer.search_nodes(min_confidence=0.85)
    print(f"   High confidence nodes (≥0.85): {len(high_conf_nodes}")

    # Find emotional nodes
    emotion_nodes = viewer.search_nodes(node_type="EMOTION")
    print(f"   Emotion nodes: {len(emotion_nodes}")

    # Find high-salience nodes
    high_sal_nodes = viewer.search_nodes(min_salience=0.9)
    print(f"   High salience nodes (≥0.9): {len(high_sal_nodes}")

    # Example 6: Node details inspection
    print("\n6. Node details inspection...")
    for node_id in ["sensory_001", "decision_001"]:
        details = viewer.get_node_details(node_id)
        if details:
            print(
                f"   {node_id}: {details['type']} - "
                f"Conf: {details['state']['confidence']:.2f}, "
                f"Sal: {details['state']['salience']:.2f}"
            )

    # Example 7: Export graph data
    print("\n7. Exporting graph data...")

    # Export as JSON
    if viewer.export_graph("cognitive_chain.json", format="json"):
        print("   ✓ Exported as JSON")

    # Export as GraphML (for use with other tools)
    if viewer.export_graph("cognitive_chain.graphml", format="graphml"):
        print("   ✓ Exported as GraphML")

    # Example 8: Graph metrics
    print("\n8. Graph Analysis Metrics:")
    metrics = viewer.calculate_graph_metrics()
    for metric, value in metrics.items():
        if isinstance(value, float):
            print(f"   {metric}: {value:.3f}")
        else:
            print(f"   {metric}: {value}")

    # Example 9: Different layout algorithms
    print("\n9. Creating visualizations with different layouts...")

    layouts = ["force_directed", "hierarchical", "circular", "spiral"]
    for layout in layouts:
        try:
            fig = viewer.create_interactive_plot(layout=layout, title=f"Cognitive Chain - {layout.title(} Layout")
            filename = f"cognitive_chain_{layout}.html"
            fig.write_html(filename)
            print(f"   ✓ Created {layout} layout: {filename}")
        except Exception as e:
            print(f"   ✗ Failed {layout} layout: {e}")

    print("\nExample completed! Check the generated HTML files to view the visualizations.")
    print("Open the HTML files in a web browser to explore the interactive features.")


if __name__ == "__main__":
    main()
