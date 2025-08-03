"""
🔌 Moral Alignment Interface
=============================

Interface module to break circular dependencies between:
vivox.moral_alignment.precedent_seeds <-> vivox.moral_alignment.vivox_mae_core
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from core.common import GLYPHToken


class Moral_AlignmentInterface(ABC):
    """Abstract interface for moral_alignment modules"""
    
    @abstractmethod
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data through the module"""
        pass
        
    @abstractmethod
    async def handle_glyph(self, token: GLYPHToken) -> GLYPHToken:
        """Handle GLYPH token"""
        pass
        
    @abstractmethod
    async def get_status(self) -> Dict[str, Any]:
        """Get module status"""
        pass


# Module registry for dependency injection
_module_registry: Dict[str, Moral_AlignmentInterface] = {}


def register_module(name: str, module: Moral_AlignmentInterface) -> None:
    """Register module implementation"""
    _module_registry[name] = module
    

def get_module(name: str) -> Optional[Moral_AlignmentInterface]:
    """Get registered module"""
    return _module_registry.get(name)
