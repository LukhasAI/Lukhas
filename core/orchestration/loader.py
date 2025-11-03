import logging
# candidate/core/orchestration/loader.py
"""
Dynamic node discovery (dark by default).

Discovers classes subclassing CognitiveNodeBase with AUTOINIT=True.
Env:
- NODES_DISABLED="a,b,c" optional deny-list
"""

from __future__ import annotations

import importlib
import inspect
import os
import pkgutil

from core.interfaces import CognitiveNodeBase
from core.registry import register


def discover_nodes(root_package: str = "labs") -> int:
    """
    Discover and register cognitive nodes from lukhas.*.nodes modules.

    Scans all packages under root_package for modules containing 'nodes'
    and registers any CognitiveNodeBase subclasses with AUTOINIT=True.

    Args:
        root_package: Root package to scan (default: "candidate")

    Returns:
        Number of nodes discovered and registered
    """
    disabled = {x.strip() for x in os.getenv("NODES_DISABLED", "").split(",") if x.strip()}
    found = 0

    # Try to import the root package first
    try:
        root_module = importlib.import_module(root_package)
    except ImportError:
        return 0

    # Use pkgutil.walk_packages to find all submodules
    for importer, modname, ispkg in pkgutil.walk_packages(
        path=getattr(root_module, "__path__", []),
        prefix=f"{root_package}.",
        onerror=lambda x: None
    ):
        # Only process modules that contain 'nodes' in their path
        if ".nodes" not in modname:
            continue

        try:
            module = importlib.import_module(modname)
        except Exception:
            # Skip modules that can't be imported
            continue

        # Scan the module for CognitiveNodeBase subclasses
        for name, cls in inspect.getmembers(module, inspect.isclass):
            # Skip if not a CognitiveNodeBase subclass
            if not issubclass(cls, CognitiveNodeBase):
                continue

            # Skip if class is defined in a different module (imported class)
            if cls.__module__ != modname:
                continue

            # Skip if AUTOINIT is not True
            if not getattr(cls, "AUTOINIT", False):
                continue

            # Get the node name (prefer 'name' attribute, fall back to class name)
            node_name = getattr(cls, "name", cls.__name__.lower())

            # Skip if disabled
            if node_name in disabled:
                continue

            try:
                # Instantiate the node
                inst = cls.from_env()

                # Register in the global registry
                register(f"node:{node_name}", inst)
                found += 1

            except Exception as e:
                # Log but don't fail on individual node registration errors
                import logging
                logging.debug(f"Failed to register node {node_name}: {e}")
                continue

    return found