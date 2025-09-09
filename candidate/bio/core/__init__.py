"""
Bio Core Module
Exposes the BioEngine class for bio-inspired processing
"""

import logging

logger = logging.getLogger(__name__)

import importlib.machinery
import importlib.util
import os

try:
    # The repository contains both a package `candidate.bio.core` (this directory)
    # and a sibling module file `candidate/bio/core.py`. Python treats the
    # directory as the package, so directly importing the file by name causes
    # a circular import. Load the file as a separate module and export BioEngine.
    module_path = os.path.join(os.path.dirname(__file__), "..", "core.py")
    module_path = os.path.normpath(module_path)

    loader = importlib.machinery.SourceFileLoader("candidate.bio._core_impl", module_path)
    spec = importlib.util.spec_from_loader(loader.name, loader)
    core_mod = importlib.util.module_from_spec(spec)
    loader.exec_module(core_mod)

    BioEngine = core_mod.BioEngine
    __all__ = ["BioEngine"]
except Exception as e:
    logger.warning(f"Could not import BioEngine: {e}")
    __all__ = []

logger.info(f"bio core module initialized. Available components: {__all__}")