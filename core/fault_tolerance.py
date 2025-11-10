"""Bridge module for core.fault_tolerance → labs.core.fault_tolerance"""
from __future__ import annotations

from labs.core.fault_tolerance import FaultTolerance, FaultHandler, handle_faults

__all__ = ["FaultTolerance", "FaultHandler", "handle_faults"]
