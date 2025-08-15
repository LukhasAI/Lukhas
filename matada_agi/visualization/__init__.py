"""
MATADA Visualization Module

This module provides comprehensive visualization capabilities for MATADA cognitive graphs,
including interactive plotting, temporal evolution tracking, and statistical analysis.

Classes:
    MATADAGraphViewer: Main visualization system for MATADA cognitive nodes
    NodeTypeConfig: Configuration for node type visualization properties
    LinkTypeConfig: Configuration for link type visualization properties

Example:
    from visualization import MATADAGraphViewer
    
    viewer = MATADAGraphViewer(width=1200, height=800)
    viewer.add_node(matada_node_data)
    fig = viewer.create_interactive_plot()
    fig.show()
"""

from .graph_viewer import MATADAGraphViewer, NodeTypeConfig, LinkTypeConfig

__all__ = ['MATADAGraphViewer', 'NodeTypeConfig', 'LinkTypeConfig']
__version__ = '1.0.0'