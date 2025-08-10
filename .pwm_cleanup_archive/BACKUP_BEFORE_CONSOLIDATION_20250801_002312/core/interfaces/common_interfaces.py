"""
Common interfaces to break circular dependencies
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class EthicsCheckable(ABC):
    """Interface for ethics-checkable components"""

    @abstractmethod
    def get_ethical_context(self) -> Dict[str, Any]:
        """Get context for ethical evaluation"""
        pass


class DreamAnalyzable(ABC):
    """Interface for dream-analyzable components"""

    @abstractmethod
    def get_dream_state(self) -> Dict[str, Any]:
        """Get current dream state"""
        pass
