"""
Diagnostic Signal Type - Stub Implementation
"""

from enum import Enum


class DiagnosticSignalType(Enum):
    """Stub enum for diagnostic signal types."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    DEBUG = "debug"
    TRACE = "trace"


__all__ = ['DiagnosticSignalType']