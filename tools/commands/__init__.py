"""Convenience exports for the :mod:`tools.commands` package."""

from __future__ import annotations

# Use absolute imports to prevent relative import issues
try:
    from tools.commands.base import BaseCommand, CommandExecutionError, CommandHandler

    __all__ = ["BaseCommand", "CommandExecutionError", "CommandHandler"]
except ImportError:
    # Fallback if running from different context
    import warnings

    warnings.warn("Could not import command classes - may be running from different context", ImportWarning)
    __all__ = []
