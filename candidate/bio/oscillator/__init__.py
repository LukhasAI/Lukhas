"""
Oscillator Module

This package co-exists with a sibling module file `candidate/bio/oscillator.py`.
Load that file dynamically and re-export key symbols to avoid import conflicts.
"""

import importlib.machinery
import importlib.util
import logging
import os

logger = logging.getLogger(__name__)

try:
	module_path = os.path.join(os.path.dirname(__file__), "..", "oscillator.py")
	module_path = os.path.normpath(module_path)
	loader = importlib.machinery.SourceFileLoader("candidate.bio._oscillator_impl", module_path)
	spec = importlib.util.spec_from_loader(loader.name, loader)
	mod = importlib.util.module_from_spec(spec)
	loader.exec_module(mod)

	get_orchestrator = mod.get_orchestrator
	BioOrchestrator = mod.BioOrchestrator
	__all__ = ["get_orchestrator", "BioOrchestrator"]
except Exception as e:
	logger.warning(f"Failed to load oscillator implementation: {e}")
	__all__ = []
