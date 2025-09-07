"""
🔌 Common Interface
====================

Interface module to break circular dependencies between:
consciousness.reflection.memory_hub <-> core.bridges.memory_consciousness_bridge
"""
from abc import ABC, abstractmethod
from typing import Any, Optional

import streamlit as st

from lukhas.core.common import GLYPHToken


class CommonInterface(ABC):
    """Abstract interface for common modules"""

    @abstractmethod
    async def process(self, data: dict[str, Any]) -> dict[str, Any]:
        """Process data through the module"""
        pass

    @abstractmethod
    async def handle_glyph(self, token: GLYPHToken) -> GLYPHToken:
        """Handle GLYPH token"""
        pass

    @abstractmethod
    async def get_status(self) -> dict[str, Any]:
        """Get module status"""
        pass


# Module registry for dependency injection
_module_registry: dict[str, CommonInterface] = {}


def register_module(name: str, module: CommonInterface) -> None:
    """Register module implementation"""
    _module_registry[name] = module


def get_module(name: str) -> Optional[CommonInterface]:
    """Get registered module"""
    return _module_registry.get(name)
