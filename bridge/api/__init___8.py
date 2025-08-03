"""

#TAG:bridge
#TAG:api
#TAG:neuroplastic
#TAG:colony


Orchestrator Configuration Module
Provides production-ready configuration management for the orchestrator migration
"""

from .orchestrator_flags import OrchestratorFlags, get_orchestrator_flags
from .production_config import ProductionOrchestratorConfig
from .migration_router import OrchestratorRouter, ShadowOrchestrator, get_orchestrator_router

__all__ = [
    'OrchestratorFlags',
    'get_orchestrator_flags',
    'ProductionOrchestratorConfig',
    'OrchestratorRouter',
    'ShadowOrchestrator',
    'get_orchestrator_router'
]