"""Bridge module for core.distributed_tracing → labs.core.distributed_tracing"""
from __future__ import annotations

from labs.core.distributed_tracing import DistributedTracer, TraceManager

__all__ = ["DistributedTracer", "TraceManager"]
