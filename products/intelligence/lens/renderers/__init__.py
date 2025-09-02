"""
Renderers Module for ΛLens
Output format renderers for dashboards
"""

from .web2d_renderer import Web2DRenderer
from .xr_renderer import XRRenderer

__all__ = ["Web2DRenderer", "XRRenderer"]
