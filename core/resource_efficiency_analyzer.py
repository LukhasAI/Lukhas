"""Bridge module for core.resource_efficiency_analyzer → labs.core.resource_efficiency_analyzer"""
from __future__ import annotations

from labs.core.resource_efficiency_analyzer import (
    AnalyzerManager,
    ResourceEfficiencyAnalyzer,
    create_analyzer,
)

__all__ = ["AnalyzerManager", "ResourceEfficiencyAnalyzer", "create_analyzer"]
