"""Bridge module for core.resource_optimization_integration → labs.core.resource_optimization_integration"""
from __future__ import annotations

from labs.core.resource_optimization_integration import (
    IntegrationManager,
    ResourceOptimizationIntegration,
    create_integration,
)

__all__ = ["IntegrationManager", "ResourceOptimizationIntegration", "create_integration"]
