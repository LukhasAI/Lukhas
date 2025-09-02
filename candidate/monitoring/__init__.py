#!/usr/bin/env python3
"""
LUKHAS  Enhanced Monitoring System
====================================
Advanced monitoring and observability with endocrine-triggered plasticity

This module provides a comprehensive biological-inspired monitoring system that:
- Monitors hormone levels and biological state
- Triggers neuroplastic adaptations based on endocrine patterns
- Maintains bio-symbolic coherence across system components
- Collects context-aware metrics with anomaly detection
- Provides predictive dashboard with hormone-driven insights
- Orchestrates system-wide learning and adaptation
- Integrates seamlessly with existing LUKHAS architecture

Key Components:
- EndocrineObservabilityEngine: Central biological state monitoring
- PlasticityTriggerManager: Intelligent adaptation decision-making
- BioSymbolicCoherenceMonitor: Alignment between biological and symbolic systems
- AdaptiveMetricsCollector: Context-aware multi-dimensional metrics
- HormoneDrivenDashboard: Predictive visualization and insights
- NeuroplasticLearningOrchestrator: System-wide learning coordination
- IntegratedMonitoringSystem: Unified integration hub
- ComprehensiveMonitoringConfig: Biological parameter configuration

This creates a living, breathing AI system that actively monitors itself,
adapts to changing conditions, and continuously learns from its experiences.
"""

from typing import Optional

from .adaptive_metrics_collector import AdaptiveMetricsCollector, MetricContext
from .bio_symbolic_coherence_monitor import (
    BioSymbolicCoherenceMonitor,
    CoherenceLevel,
    CoherenceReport,
)
from .endocrine_observability_engine import (
    EndocrineObservabilityEngine,
    EndocrineSnapshot,
    PlasticityEvent,
    PlasticityTriggerType,
)
from .hormone_driven_dashboard import DashboardMode, HormoneDrivenDashboard
from .integrated_monitoring_system import (
    IntegratedMonitoringSystem,
    IntegrationState,
    MonitoringLevel,
    SystemHealthMetrics,
    create_integrated_monitoring_system,
    start_complete_monitoring_system,
)
from .monitoring_config import (
    ComprehensiveMonitoringConfig,
    MonitoringConfigManager,
    MonitoringProfile,
    load_monitoring_config,
)
from .neuroplastic_learning_orchestrator import (
    LearningInsight,
    LearningPhase,
    NeuroplasticLearningOrchestrator,
)
from .plasticity_trigger_manager import PlasticityTriggerManager

# Version information
__version__ = "1.0.0"
__author__ = "LUKHAS AI"
__description__ = (
    "Enhanced monitoring and observability with endocrine-triggered plasticity"
)

# Main entry points
__all__ = [
    # Main system components
    "IntegratedMonitoringSystem",
    "start_complete_monitoring_system",
    "create_integrated_monitoring_system",
    # Individual components
    "EndocrineObservabilityEngine",
    "PlasticityTriggerManager",
    "BioSymbolicCoherenceMonitor",
    "AdaptiveMetricsCollector",
    "HormoneDrivenDashboard",
    "NeuroplasticLearningOrchestrator",
    # Configuration
    "ComprehensiveMonitoringConfig",
    "MonitoringProfile",
    "MonitoringConfigManager",
    "load_monitoring_config",
    # Key data structures
    "EndocrineSnapshot",
    "PlasticityEvent",
    "CoherenceReport",
    "SystemHealthMetrics",
    "LearningInsight",
    # Enums and types
    "PlasticityTriggerType",
    "CoherenceLevel",
    "MetricContext",
    "DashboardMode",
    "LearningPhase",
    "IntegrationState",
    "MonitoringLevel",
]


def create_monitoring_system_from_config(
    config_path: Optional[str] = None, profile: MonitoringProfile = None
):
    """
    Convenience function to create a complete monitoring system from configuration.

    Args:
        config_path: Path to configuration file
        profile: Monitoring profile to use

    Returns:
        Configured IntegratedMonitoringSystem ready to start

    Example:
        >>> from monitoring import create_monitoring_system_from_config, MonitoringProfile
        >>> from candidate.orchestration.signals.signal_bus import SignalBus
        >>>
        >>> signal_bus = SignalBus()
        >>> monitoring = create_monitoring_system_from_config(
        ...     config_path="config/monitoring.yaml", profile=MonitoringProfile.PRODUCTION
        ... )
        >>> await monitoring.initialize()
        >>> await monitoring.start_monitoring()
    """
    from candidate.orchestration.signals.signal_bus import SignalBus

    # Load configuration
    config = load_monitoring_config(config_path, profile)

    # Create signal bus (would typically be passed from main system)
    signal_bus = SignalBus()

    # Create integrated system with configuration
    return create_integrated_monitoring_system(
        signal_bus,
        {
            "endocrine_config": config.endocrine.__dict__,
            "plasticity_config": config.plasticity.__dict__,
            "coherence_config": {},  # BioSymbolicCoherenceMonitor uses defaults
            "metrics_config": config.metrics.__dict__,
            "dashboard_config": config.dashboard.__dict__,
            "learning_config": config.learning.__dict__,
            **config.integration.__dict__,
        },
    )


# Quick start example
QUICK_START_EXAMPLE = """
# Quick Start Example - Enhanced LUKHAS Monitoring

from monitoring import start_complete_monitoring_system, MonitoringProfile
from candidate.orchestration.signals.signal_bus import SignalBus
import asyncio

async def main():
    # Create signal bus (or get from existing LUKHAS system)
    signal_bus = SignalBus()

    # Start the complete monitoring system
    monitoring_system = await start_complete_monitoring_system(
        signal_bus,
        config={
            "profile": MonitoringProfile.DEVELOPMENT,
            "learning_enabled": True,
            "dashboard_enabled": True,
            "auto_adaptation": True
        }
    )

    # System is now running with:
    # - Hormone level monitoring and plasticity triggers
    # - Bio-symbolic coherence tracking
    # - Adaptive metrics collection with context awareness
    # - Predictive dashboard with hormone-driven insights
    # - Neuroplastic learning and adaptation
    # - Full integration with existing LUKHAS systems

    # Get system status
    status = monitoring_system.get_system_status()
    print(f"System Health: {status['health']['overall']:.2f}")
    print(f"Risk Level: {status['health']['risk_level']}")

    # Get recent insights
    insights = monitoring_system.get_unified_insights(limit=5)
    print(f"Recent Insights: {len(insights)}")

    # Run for demonstration
    await asyncio.sleep(60)

    # Stop monitoring
    await monitoring_system.stop_monitoring()

if __name__ == "__main__":
    asyncio.run(main())
"""
