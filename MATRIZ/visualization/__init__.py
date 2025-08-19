"""
MATRIZ Visualization Module

This module provides comprehensive visualization capabilities for MATRIZ cognitive graphs,
including interactive plotting, temporal evolution tracking, and statistical analysis.

Classes:
    MATRIZGraphViewer: Main visualization system for MATRIZ cognitive nodes
    NodeTypeConfig: Configuration for node type visualization properties
    LinkTypeConfig: Configuration for link type visualization properties

Example:
    from visualization import MATRIZGraphViewer
    
    viewer = MATRIZGraphViewer(width=1200, height=800)
    viewer.add_node(matriz_node_data)
    fig = viewer.create_interactive_plot()
    fig.show()
"""

from .graph_viewer import MATRIZGraphViewer, NodeTypeConfig, LinkTypeConfig

__all__ = ['MATRIZGraphViewer', 'NodeTypeConfig', 'LinkTypeConfig']
__version__ = '1.0.0'