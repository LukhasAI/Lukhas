"""
Symbolic trace logger for consciousness awareness tracking.

⚛️🧠🛡️ Trinity Framework: Identity-Consciousness-Guardian
"""

import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class SymbolicTrace:
    """Represents a symbolic trace entry."""
    timestamp: float
    trace_id: str
    component: str
    level: str
    message: str
    context: dict[str, Any]
    symbolic_markers: list[str]


class SymbolicTraceLogger:
    """
    Enhanced logger for consciousness awareness with symbolic tracing.

    Provides Trinity Framework-compliant logging with consciousness awareness.
    """

    def __init__(self, name: str = "ΛTRACE.symbolic"):
        """Initialize the symbolic trace logger."""
        self.logger = logging.getLogger(name)
        self.traces: list[SymbolicTrace] = []
        self.trace_counter = 0

    def trace(self, component: str, message: str, level: str = "INFO",
              context: Optional[dict[str, Any]] = None,
              symbolic_markers: Optional[list[str]] = None) -> None:
        """Log a symbolic trace entry."""
        if context is None:
            context = {}
        if symbolic_markers is None:
            symbolic_markers = []

        trace_id = f"trace_{self.trace_counter}_{int(time.time() * 1000)}"
        self.trace_counter += 1

        trace = SymbolicTrace(
            timestamp=time.time(),
            trace_id=trace_id,
            component=component,
            level=level,
            message=message,
            context=context,
            symbolic_markers=symbolic_markers
        )

        self.traces.append(trace)
        self.logger.log(getattr(logging, level), f"[{component}] {message}", extra=context)

    def info(self, component: str, message: str, **kwargs) -> None:
        """Log an info-level trace."""
        self.trace(component, message, "INFO", kwargs)

    def warning(self, component: str, message: str, **kwargs) -> None:
        """Log a warning-level trace."""
        self.trace(component, message, "WARNING", kwargs)

    def error(self, component: str, message: str, **kwargs) -> None:
        """Log an error-level trace."""
        self.trace(component, message, "ERROR", kwargs)

    def debug(self, component: str, message: str, **kwargs) -> None:
        """Log a debug-level trace."""
        self.trace(component, message, "DEBUG", kwargs)

    def get_traces(self, component: Optional[str] = None) -> list[SymbolicTrace]:
        """Get traces, optionally filtered by component."""
        if component is None:
            return self.traces.copy()
        return [trace for trace in self.traces if trace.component == component]

    def clear_traces(self) -> None:
        """Clear all stored traces."""
        self.traces.clear()
        self.trace_counter = 0
