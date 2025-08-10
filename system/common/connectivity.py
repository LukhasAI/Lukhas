"""
Module Connectivity Enhancer
===========================
Enhances connectivity between LUKHAS modules post-modularization.
"""

import importlib
import logging
from typing import Any, Optional


class ModuleConnector:
    """Facilitates cross-module communication"""

    def __init__(self):
        self.module_registry = {}
        self.logger = logging.getLogger(__name__)
        self._register_core_modules()

    def _register_core_modules(self):
        """Register core LUKHAS modules"""
        core_modules = {
            "core": ["core.common", "core.glyph", "core.symbolic"],
            "consciousness": ["consciousness.unified", "consciousness.dream"],
            "memory": ["memory.core", "memory.folds"],
            "orchestration": ["orchestration.brain", "orchestration.agents"],
            "governance": ["governance.guardian", "governance.ethics"],
            "vivox": ["vivox.consciousness", "vivox.integration"],
        }

        for category, modules in core_modules.items():
            for module_name in modules:
                try:
                    module = importlib.import_module(module_name)
                    self.module_registry[module_name] = module
                    self.logger.info(f"Registered module: {module_name}")
                except ImportError as e:
                    self.logger.warning(f"Could not import {module_name}: {e}")

    def get_module(self, module_name: str) -> Optional[Any]:
        """Get a registered module"""
        return self.module_registry.get(module_name)

    def connect_modules(self, source: str, target: str) -> bool:
        """Establish connection between modules"""
        source_module = self.get_module(source)
        target_module = self.get_module(target)

        if source_module and target_module:
            # Establish bidirectional awareness
            if hasattr(source_module, "_connected_modules"):
                source_module._connected_modules.add(target)
            else:
                source_module._connected_modules = {target}

            if hasattr(target_module, "_connected_modules"):
                target_module._connected_modules.add(source)
            else:
                target_module._connected_modules = {source}

            self.logger.info(f"Connected {source} <-> {target}")
            return True

        return False


# Global connector instance
connector = ModuleConnector()


def enhance_import(module_name: str) -> Optional[Any]:
    """Enhanced import that uses the module registry"""
    # Try normal import first
    try:
        return importlib.import_module(module_name)
    except ImportError:
        # Fall back to connector
        module = connector.get_module(module_name)
        if module:
            return module

        # Try alternative paths
        alternatives = {
            "core.base": "core.common.base",
            "consciousness.base": "consciousness.unified.base",
            "memory.base": "memory.core.base",
        }

        if module_name in alternatives:
            try:
                return importlib.import_module(alternatives[module_name])
            except ImportError:
                pass

        raise ImportError(f"Cannot import {module_name}")
