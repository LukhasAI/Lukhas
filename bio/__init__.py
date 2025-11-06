"""Compatibility package for legacy `bio.*` imports."""
from __future__ import annotations

from bio.core import BioCore, BioSymbolicProcessor

__version__ = "0.1.0"
__all__ = ["BioCore", "BioSymbolicProcessor", "energy"]
