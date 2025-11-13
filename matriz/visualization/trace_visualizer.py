#!/usr/bin/env python3
"""
MATRIZ Trace Visualization Module

This module provides functions to convert execution traces
from the BioSymbolicOrchestrator into a graph format
suitable for visualization with the MATRIZGraphViewer.
"""

import networkx as nx
from matriz.visualization.graph_viewer import MATRIZGraphViewer


def trace_to_graph(trace_data: list[dict]) -> nx.DiGraph:
    """
    Converts a trace from the BioSymbolicOrchestrator into a NetworkX graph.

    Args:
        trace_data: The trace data, a list of dictionaries.

    Returns:
        A NetworkX DiGraph representing the trace.
    """
    graph = nx.DiGraph()
    last_node = None

    for i, step in enumerate(trace_data):
        node_id = f"step_{i+1}"
        graph.add_node(
            node_id,
            type="PROCESSING_STEP",
            label=f"Step {i+1}: {step['processor']}",
            input=str(step["input"]),
            output=str(step["output"]),
        )

        if last_node:
            graph.add_edge(last_node, node_id)

        last_node = node_id

    return graph


def calculate_trace_metrics(trace_data: list[dict]) -> dict:
    """
    Calculates metrics for a given trace.

    Args:
        trace_data: The trace data, a list of dictionaries.

    Returns:
        A dictionary of metrics.
    """
    depth = len(trace_data)
    processors = [step["processor"] for step in trace_data]
    breadth = len(set(processors))
    complexity = depth * breadth

    return {"depth": depth, "breadth": breadth, "complexity": complexity, "processors": processors}


def visualize_trace(trace_data: list[dict]):
    """
    Visualizes a trace from the BioSymbolicOrchestrator.

    Args:
        trace_data: The trace data, a list of dictionaries.
    """
    graph = trace_to_graph(trace_data)
    metrics = calculate_trace_metrics(trace_data)

    # We need to convert the NetworkX graph to a format that MATRIZGraphViewer can ingest.
    # The MATRIZGraphViewer expects a list of MATRIZ node dictionaries.
    # For this proof of concept, we'll create a simple conversion.

    matriz_nodes = []
    for i, (node_id, node_data) in enumerate(graph.nodes(data=True)):
        matriz_node = {
            "id": node_id,
            "type": node_data.get("type", "UNKNOWN"),
            "state": {
                "confidence": 1.0,
                "salience": 1.0,
            },
            "timestamps": {"created_ts": i},
            "provenance": {
                "producer": "TraceVisualizer",
            },
            "links": [{"target_node_id": f"step_{i+2}"}] if i < len(graph.nodes()) - 1 else [],
        }
        matriz_nodes.append(matriz_node)

    viewer = MATRIZGraphViewer()
    viewer.add_nodes_batch(matriz_nodes)
    title = f"Bio-Symbolic Reasoning Trace (Depth: {metrics['depth']}, Breadth: {metrics['breadth']}, Complexity: {metrics['complexity']})"
    fig = viewer.create_interactive_plot(title=title)
    fig.show()
