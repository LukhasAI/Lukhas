"""Bridge module for bio.compound_governor → labs.bio.compound_governor"""
from __future__ import annotations

from labs.bio.compound_governor import (
    BioCompoundGovernor,
    BiologicalModulatorState,
    SystemHealthState,
    SystemStabilityMetrics,
)

__all__ = ["BioCompoundGovernor", "BiologicalModulatorState", "SystemHealthState", "SystemStabilityMetrics"]
