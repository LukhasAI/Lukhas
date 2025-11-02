"""
LUKHAS Phase 8: Lane Assignment & Canary Deployment System
==========================================================

Comprehensive deployment pipeline with lane management and progressive rollout capabilities.

## Architecture

### Lane Progression
- **candidate**: Development/Integration testing lane
- **lukhas**: Staging/Pre-production lane
- **MATRIZ**: Production lane with full traffic

### Components
- **LaneManager**: Central lane assignment and coordination
- **CanaryController**: Progressive deployment automation
- **TrafficRouter**: Intelligent traffic distribution
- **HealthMonitor**: Multi-dimensional health checking
- **DeploymentPipeline**: End-to-end orchestration
- **ConfigurationManager**: Dynamic feature flags
- **RollbackSystem**: Automated failure detection and recovery

### Performance Targets
- Lane switching: <50ms latency
- Availability: 99.99% during deployments
- Rollback detection: <30s SLA violation detection
- Health checks: <10ms multi-dimensional validation

### Integration Points
- Constellation Framework hub (148 files)
- Identity-Consciousness-Memory coordination
- 150+ API integration layer
- Observability and monitoring systems
- Guardian safety validation
"""

from .canary_controller import CanaryController
from .config_manager import ConfigurationManager
from .deployment_coordinator import DeploymentCoordinator
from .deployment_pipeline import DeploymentPipeline
from .health_monitor import HealthMonitor
from .lane_manager import LaneManager
from .rollback_system import RollbackSystem
from .traffic_router import TrafficRouter

__all__ = [
    "LaneManager",
    "CanaryController",
    "TrafficRouter",
    "HealthMonitor",
    "DeploymentPipeline",
    "ConfigurationManager",
    "RollbackSystem",
    "DeploymentCoordinator",
]
