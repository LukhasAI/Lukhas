"""
Common base classes and utilities for governance module
"""
from abc import ABC, abstractmethod
from typing import Any

import streamlit as st


class BaseLukhasModule(ABC):
    """Base class for all LUKHAS modules"""

    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def process(self, input_data: Any) -> Any:
        pass


class BaseLukhasConfig:
    """Base configuration class"""

    def __init__(self):
        self.config = {}

    def get(self, key: str, default: Any = None) -> Any:
        return self.config.get(key, default)

    def set(self, key: str, value: Any):
        self.config[key] = value


class BaseLukhasHealth:
    """Base health monitoring class"""

    def __init__(self):
        self.status = "healthy"
        self.metrics = {}

    def update_metric(self, name: str, value: Any):
        self.metrics[name] = value

    def get_status(self) -> dict[str, Any]:
        return {"status": self.status, "metrics": self.metrics}


def symbolic_vocabulary(func=None):
    """
    Decorator or function that returns symbolic vocabulary for GLYPH tokens.
    Can be used as @symbolic_vocabulary or symbolic_vocabulary()
    """
    if func is None:
        # Called as a function
        return {
            "SAFE": "✅",
            "WARNING": "⚠️",
            "ERROR": "❌",
            "INFO": "ℹ️",
            "SUCCESS": "✨",
            "PROCESSING": "⚙️",
        }
    else:
        # Used as a decorator
        return func


def symbolic_message(cls):
    """Decorator for symbolic message classes"""
    return cls


def ethical_validation(func):
    """Decorator for functions requiring ethical validation"""

    def wrapper(*args, **kwargs):
        # In production, this would validate through the ethics engine
        return func(*args, **kwargs)

    return wrapper
