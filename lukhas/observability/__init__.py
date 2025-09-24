"""
LUKHAS Observability Module - Phase 5 Enhanced Observability and Evidence Collection
Enterprise-grade monitoring, tracing, metrics collection, and compliance systems.

Phase 5 Implementation Features:
- Tamper-evident evidence collection with cryptographic integrity
- Advanced metrics with ML-based anomaly detection
- Intelligent alerting with escalation and noise reduction
- Compliance dashboard with regulatory audit trail visualization
- Performance regression detection with automated root cause analysis
- Evidence archival with long-term storage and integrity verification
- Enhanced distributed tracing with LUKHAS semantic conventions
- Security hardening with audit trail protection
"""

# Core observability (Phase 0-4)
from .opentelemetry_tracing import (
    LUKHASTracer,
    initialize_tracing,
    get_lukhas_tracer,
    shutdown_tracing,
    trace_function,
    trace_memory_recall,
    trace_matriz_execution,
    OTEL_AVAILABLE,
)

from .prometheus_metrics import (
    LUKHASMetrics,
    MetricsConfig,
    initialize_metrics,
    get_lukhas_metrics,
    shutdown_metrics,
    PROMETHEUS_AVAILABLE,
)

# Phase 5 Enhanced Observability
from .evidence_collection import (
    EvidenceCollectionEngine,
    EvidenceRecord,
    EvidenceType,
    ComplianceRegime,
    initialize_evidence_collection,
    get_evidence_engine,
    collect_evidence,
)

from .advanced_metrics import (
    AdvancedMetricsSystem,
    MetricAnomaly,
    AnomalyType,
    MetricSeverity,
    initialize_advanced_metrics,
    get_advanced_metrics,
    record_metric,
    record_operation_performance,
)

from .intelligent_alerting import (
    IntelligentAlertingSystem,
    AlertState,
    NotificationChannel,
    EscalationLevel,
    initialize_alerting,
    get_alerting_system,
    trigger_alert,
)

from .compliance_dashboard import (
    ComplianceDashboard,
    ComplianceStatus,
    AuditReport,
    initialize_compliance_dashboard,
    get_compliance_dashboard,
)

from .performance_regression import (
    PerformanceRegressionDetector,
    PerformanceBaseline,
    PerformanceRegression,
    RegressionSeverity,
    DetectionMethod,
    initialize_regression_detector,
    get_regression_detector,
    record_performance_data,
)

from .evidence_archival import (
    EvidenceArchivalSystem,
    StorageTier,
    CloudProvider,
    RetentionPolicy,
    initialize_archival_system,
    get_archival_system,
    schedule_archival,
)

from .enhanced_distributed_tracing import (
    EnhancedLUKHASTracer,
    TraceConfig,
    LUKHASSemanticConventions,
    initialize_enhanced_tracing,
    get_enhanced_tracer,
    trace_lukhas_operation,
    trace_evidence_collection,
    trace_performance_check,
    create_correlation_id,
    propagate_trace_context,
    extract_trace_context,
)

from .security_hardening import (
    ObservabilitySecurityHardening,
    SecurityLevel,
    ThreatType,
    SecurityEvent,
    initialize_security_hardening,
    get_security_hardening,
    secure_evidence_operation,
)

__all__ = [
    # Core observability (Phase 0-4)
    "LUKHASTracer",
    "initialize_tracing",
    "get_lukhas_tracer",
    "shutdown_tracing",
    "trace_function",
    "trace_memory_recall",
    "trace_matriz_execution",
    "OTEL_AVAILABLE",
    "LUKHASMetrics",
    "MetricsConfig",
    "initialize_metrics",
    "get_lukhas_metrics",
    "shutdown_metrics",
    "PROMETHEUS_AVAILABLE",

    # Phase 5 Evidence Collection
    "EvidenceCollectionEngine",
    "EvidenceRecord",
    "EvidenceType",
    "ComplianceRegime",
    "initialize_evidence_collection",
    "get_evidence_engine",
    "collect_evidence",

    # Phase 5 Advanced Metrics
    "AdvancedMetricsSystem",
    "MetricAnomaly",
    "AnomalyType",
    "MetricSeverity",
    "initialize_advanced_metrics",
    "get_advanced_metrics",
    "record_metric",
    "record_operation_performance",

    # Phase 5 Intelligent Alerting
    "IntelligentAlertingSystem",
    "AlertState",
    "NotificationChannel",
    "EscalationLevel",
    "initialize_alerting",
    "get_alerting_system",
    "trigger_alert",

    # Phase 5 Compliance Dashboard
    "ComplianceDashboard",
    "ComplianceStatus",
    "AuditReport",
    "initialize_compliance_dashboard",
    "get_compliance_dashboard",

    # Phase 5 Performance Regression Detection
    "PerformanceRegressionDetector",
    "PerformanceBaseline",
    "PerformanceRegression",
    "RegressionSeverity",
    "DetectionMethod",
    "initialize_regression_detector",
    "get_regression_detector",
    "record_performance_data",

    # Phase 5 Evidence Archival
    "EvidenceArchivalSystem",
    "StorageTier",
    "CloudProvider",
    "RetentionPolicy",
    "initialize_archival_system",
    "get_archival_system",
    "schedule_archival",

    # Phase 5 Enhanced Distributed Tracing
    "EnhancedLUKHASTracer",
    "TraceConfig",
    "LUKHASSemanticConventions",
    "initialize_enhanced_tracing",
    "get_enhanced_tracer",
    "trace_lukhas_operation",
    "trace_evidence_collection",
    "trace_performance_check",
    "create_correlation_id",
    "propagate_trace_context",
    "extract_trace_context",

    # Phase 5 Security Hardening
    "ObservabilitySecurityHardening",
    "SecurityLevel",
    "ThreatType",
    "SecurityEvent",
    "initialize_security_hardening",
    "get_security_hardening",
    "secure_evidence_operation",
]


# Phase 5 Initialization Helper
async def initialize_phase5_observability(
    enable_evidence_collection: bool = True,
    enable_advanced_metrics: bool = True,
    enable_intelligent_alerting: bool = True,
    enable_compliance_dashboard: bool = True,
    enable_performance_regression: bool = True,
    enable_evidence_archival: bool = True,
    enable_enhanced_tracing: bool = True,
    enable_security_hardening: bool = True,
    **kwargs
) -> dict:
    """
    Initialize complete Phase 5 observability stack.

    Args:
        enable_*: Enable/disable specific components
        **kwargs: Component-specific configuration

    Returns:
        Dictionary of initialized components
    """
    components = {}

    try:
        if enable_evidence_collection:
            components['evidence_collection'] = initialize_evidence_collection(**kwargs.get('evidence', {}))

        if enable_advanced_metrics:
            components['advanced_metrics'] = initialize_advanced_metrics(**kwargs.get('metrics', {}))

        if enable_intelligent_alerting:
            components['intelligent_alerting'] = initialize_alerting(**kwargs.get('alerting', {}))

        if enable_compliance_dashboard:
            components['compliance_dashboard'] = initialize_compliance_dashboard(**kwargs.get('compliance', {}))

        if enable_performance_regression:
            components['performance_regression'] = initialize_regression_detector(**kwargs.get('regression', {}))

        if enable_evidence_archival:
            components['evidence_archival'] = initialize_archival_system(**kwargs.get('archival', {}))

        if enable_enhanced_tracing:
            components['enhanced_tracing'] = initialize_enhanced_tracing(**kwargs.get('tracing', {}))

        if enable_security_hardening:
            components['security_hardening'] = initialize_security_hardening(**kwargs.get('security', {}))

        print(f"Phase 5 observability initialized with {len(components)} components")
        return components

    except Exception as e:
        print(f"Error initializing Phase 5 observability: {e}")
        # Cleanup any partially initialized components
        for component in components.values():
            if hasattr(component, 'shutdown'):
                try:
                    await component.shutdown()
                except Exception:
                    pass
        raise


async def shutdown_phase5_observability():
    """Shutdown all Phase 5 observability components gracefully"""
    shutdown_tasks = []

    try:
        # Shutdown all global instances
        from . import evidence_collection, advanced_metrics, intelligent_alerting
        from . import compliance_dashboard, performance_regression, evidence_archival
        from . import enhanced_distributed_tracing, security_hardening

        shutdown_tasks.extend([
            evidence_collection.shutdown_evidence_collection(),
            advanced_metrics.shutdown_advanced_metrics(),
            intelligent_alerting.shutdown_alerting(),
            compliance_dashboard.shutdown_compliance_dashboard(),
            performance_regression.shutdown_regression_detector(),
            evidence_archival.shutdown_archival_system(),
            security_hardening.shutdown_security_hardening(),
        ])

        # Also shutdown enhanced tracing
        enhanced_distributed_tracing.shutdown_enhanced_tracing()

        # Execute all shutdowns concurrently
        await asyncio.gather(*shutdown_tasks, return_exceptions=True)

        print("Phase 5 observability shutdown completed")

    except Exception as e:
        print(f"Error during Phase 5 shutdown: {e}")


# Add shutdown to __all__
__all__.extend([
    "initialize_phase5_observability",
    "shutdown_phase5_observability",
])