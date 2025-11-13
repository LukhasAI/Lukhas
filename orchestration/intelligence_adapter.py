"""Bridge module for orchestration.intelligence_adapter → labs.orchestration.intelligence_adapter"""
from __future__ import annotations

from labs.orchestration.intelligence_adapter import (
    AdapterManager,
    IntelligenceAdapter,
    create_intelligence_adapter,
)

__all__ = ["AdapterManager", "IntelligenceAdapter", "create_intelligence_adapter"]
