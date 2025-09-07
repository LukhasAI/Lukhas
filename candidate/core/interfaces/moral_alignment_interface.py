"""
🔌 Moral Alignment Interface
=============================

Interface module to break circular dependencies between:
vivox.moral_alignment.precedent_seeds <-> vivox.moral_alignment.vivox_mae_core
"""
import streamlit as st

from abc import ABC, abstractmethod
from typing import Any, Optional

from lukhas.core.common import GLYPHToken


class Moral_AlignmentInterface(ABC):
    """Abstract interface for moral_alignment modules"""

    @abstractmethod
    async def process(self, data: dict[str, Any]) -> dict[str, Any]:
        """Process data through the module"""

    @abstractmethod
    async def handle_glyph(self, token: GLYPHToken) -> GLYPHToken:
        """Handle GLYPH token"""

    @abstractmethod
    async def get_status(self) -> dict[str, Any]:
        """Get module status"""


# Module registry for dependency injection
_module_registry: dict[str, Moral_AlignmentInterface] = {}


def register_module(name: str, module: Moral_AlignmentInterface) -> None:
    """Register module implementation"""
    _module_registry[name] = module


def get_module(name: str) -> Optional[Moral_AlignmentInterface]:
    """Get registered module"""
    return _module_registry.get(name)
