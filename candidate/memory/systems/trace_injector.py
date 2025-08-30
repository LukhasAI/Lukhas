"""
Memory Trace Injector
ΛAGENT: Jules-05/Jules-02 Integration
ΛPURPOSE: Inject symbolic traces into memory operations for traceability
ΛMODULE: memory.core_memory.trace_injector
"""

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Optional


@dataclass
class MemoryTrace:
    """Represents a trace point in memory operations."""

    trace_id: str
    timestamp: str
    operation_type: str
    memory_address: str
    symbolic_tag: str
    metadata: dict[str, Any]
    agent_id: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert trace to dictionary for serialization."""
        return asdict(self)


class TraceInjector:
    """Injects symbolic traces into memory operations."""

    def __init__(self, agent_id: str = "unknown"):
        self.agent_id = agent_id
        self.trace_stack: list[MemoryTrace] = []
        self.active_traces: dict[str, MemoryTrace] = {}

    def generate_trace_id(self, operation_type: str, memory_address: str) -> str:
        """Generate unique trace ID for operation."""
        timestamp = datetime.now().isoformat()
        trace_input = f"{operation_type}:{memory_address}:{timestamp}:{self.agent_id}"
        # SECURITY: Use SHA-256 instead of MD5 for better security
        return hashlib.sha256(trace_input.encode()).hexdigest()[:16]

    def inject_trace(
        self,
        operation_type: str,
        memory_address: str,
        symbolic_tag: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> MemoryTrace:
        """Inject a trace point into memory operation."""
        trace_id = self.generate_trace_id(operation_type, memory_address)

        trace = MemoryTrace(
            trace_id=trace_id,
            timestamp=datetime.now().isoformat(),
            operation_type=operation_type,
            memory_address=memory_address,
            symbolic_tag=symbolic_tag,
            metadata=metadata or {},
            agent_id=self.agent_id,
        )

        self.trace_stack.append(trace)
        self.active_traces[trace_id] = trace

        return trace

    def start_memory_operation(self, operation_type: str, memory_address: str) -> str:
        """Start tracing a memory operation."""
        trace = self.inject_trace(
            operation_type=f"START_{operation_type}",
            memory_address=memory_address,
            symbolic_tag=f"ΛMEM_{operation_type}",
            metadata={"status": "started"},
        )
        return trace.trace_id

    def end_memory_operation(self, trace_id: str, result: Any = None) -> None:
        """End tracing a memory operation."""
        if trace_id in self.active_traces:
            original_trace = self.active_traces[trace_id]
            self.inject_trace(
                operation_type=f"END_{original_trace.operation_type.replace('START_', '')}",
                memory_address=original_trace.memory_address,
                symbolic_tag="ΛMEM_COMPLETE",
                metadata={
                    "original_trace_id": trace_id,
                    "result": str(result) if result is not None else None,
                    "status": "completed",
                },
            )

            # Remove from active traces
            del self.active_traces[trace_id]

    def get_trace_chain(self, memory_address: str) -> list[MemoryTrace]:
        """Get all traces for a specific memory address."""
        return [trace for trace in self.trace_stack if trace.memory_address == memory_address]

    def get_active_traces(self) -> dict[str, MemoryTrace]:
        """Get all currently active traces."""
        return self.active_traces.copy()

    def export_traces(self, format: str = "json") -> str:
        """Export trace stack for analysis."""
        if format == "json":
            return json.dumps([trace.to_dict() for trace in self.trace_stack], indent=2)
        elif format == "symbolic":
            return self._export_symbolic_format()
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _export_symbolic_format(self) -> str:
        """Export traces in symbolic format."""
        symbolic_output = []
        symbolic_output.append("ΛTRACE_EXPORT")
        symbolic_output.append(f"ΛAGENT: {self.agent_id}")
        symbolic_output.append(f"ΛTRACE_COUNT: {len(self.trace_stack)}")
        symbolic_output.append("")

        for trace in self.trace_stack:
            symbolic_output.append(f"ΛTRACE: {trace.trace_id}")
            symbolic_output.append(f"  ΛTIME: {trace.timestamp}")
            symbolic_output.append(f"  ΛOPERATION: {trace.operation_type}")
            symbolic_output.append(f"  ΛADDRESS: {trace.memory_address}")
            symbolic_output.append(f"  ΛTAG: {trace.symbolic_tag}")
            if trace.metadata:
                symbolic_output.append(f"  ΛMETADATA: {json.dumps(trace.metadata)}")
            symbolic_output.append("")

        return "\n".join(symbolic_output)

    def clear_traces(self) -> None:
        """Clear all traces."""
        self.trace_stack.clear()
        self.active_traces.clear()


# Global trace injector instance
_global_injector = TraceInjector("system")


def get_global_injector() -> TraceInjector:
    """Get the global trace injector instance."""
    return _global_injector


def inject_memory_trace(
    operation_type: str,
    memory_address: str,
    symbolic_tag: str,
    metadata: Optional[dict[str, Any]] = None,
) -> MemoryTrace:
    """Convenience function to inject a trace using global injector."""
    return _global_injector.inject_trace(operation_type, memory_address, symbolic_tag, metadata)


def start_memory_trace(operation_type: str, memory_address: str) -> str:
    """Convenience function to start memory operation trace."""
    return _global_injector.start_memory_operation(operation_type, memory_address)


def end_memory_trace(trace_id: str, result: Any = None) -> None:
    """Convenience function to end memory operation trace."""
    _global_injector.end_memory_operation(trace_id, result)


def export_trace_data(format: str = "json") -> str:
    """Convenience function to export trace data."""
    return _global_injector.export_traces(format)


if __name__ == "__main__":
    # Test the trace injector
    injector = TraceInjector("test_agent")

    # Test basic trace injection
    trace = injector.inject_trace("READ", "0x1000", "ΛMEM_READ", {"size": 1024})
    print(f"Injected trace: {trace.trace_id}")

    # Test operation tracing
    trace_id = injector.start_memory_operation("WRITE", "0x2000")
    injector.end_memory_operation(trace_id, "success")

    # Export traces
    print("\nSymbolic Export:")
    print(injector.export_traces("symbolic"))
