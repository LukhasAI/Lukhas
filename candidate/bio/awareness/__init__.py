"""
Awareness Module

This package shadows a sibling module file `candidate/bio/awareness.py`.
Load the file dynamically and re-export symbols to avoid import conflicts.
"""

import importlib.machinery
import importlib.util
import logging
import os

logger = logging.getLogger(__name__)

try:
	module_path = os.path.join(os.path.dirname(__file__), "..", "awareness.py")
	module_path = os.path.normpath(module_path)
	loader = importlib.machinery.SourceFileLoader("candidate.bio._awareness_impl", module_path)
	spec = importlib.util.spec_from_loader(loader.name, loader)
	mod = importlib.util.module_from_spec(spec)
	loader.exec_module(mod)

	# Re-export commonly expected symbols
	BioAwareness = getattr(mod, "BioAwareness")
	AwarenessState = getattr(mod, "AwarenessState")
	__all__ = ["BioAwareness", "AwarenessState"]
except Exception as e:
	logger.warning(f"Failed to load awareness implementation: {e}")
	__all__ = []
