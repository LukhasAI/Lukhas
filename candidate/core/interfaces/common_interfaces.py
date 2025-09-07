"""
Common interfaces to break circular dependencies
"""
import streamlit as st

from abc import ABC, abstractmethod
from typing import Any


class EthicsCheckable(ABC):
    """Interface for ethics-checkable components"""

    @abstractmethod
    def get_ethical_context(self) -> dict[str, Any]:
        """Get context for ethical evaluation"""


class DreamAnalyzable(ABC):
    """Interface for dream-analyzable components"""

    @abstractmethod
    def get_dream_state(self) -> dict[str, Any]:
        """Get current dream state"""
