"""
Symbolic Module

Load the sibling module file `candidate/bio/symbolic.py` and re-export symbols.
"""

import importlib.machinery
import importlib.util
import logging
import os

logger = logging.getLogger(__name__)

try:
	module_path = os.path.join(os.path.dirname(__file__), "..", "symbolic.py")
	module_path = os.path.normpath(module_path)
	loader = importlib.machinery.SourceFileLoader("candidate.bio._symbolic_impl", module_path)
	spec = importlib.util.spec_from_loader(loader.name, loader)
	mod = importlib.util.module_from_spec(spec)
	loader.exec_module(mod)

	get_symbolic_processor = mod.get_symbolic_processor
	__all__ = ["get_symbolic_processor"]
except Exception as e:
	logger.warning(f"Failed to load symbolic implementation: {e}")
	__all__ = []