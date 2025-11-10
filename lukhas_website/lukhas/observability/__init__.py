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
from .advanced_metrics import (
    AdvancedMetricsSystem,
    AnomalyType,
    MetricAnomaly,
    MetricSeverity,
    get_advanced_metrics,
    initialize_advanced_metrics,
    record_metric,
    record_operation_performance,
)
from .compliance_dashboard import (
    AuditReport,
    ComplianceDashboard,
    ComplianceStatus,
    get_compliance_dashboard,
    initialize_compliance_dashboard,
)
from .enhanced_distributed_tracing import (
    EnhancedLUKHASTracer,
    LUKHASSemanticConventions,
    TraceConfig,
    create_correlation_id,
    extract_trace_context,
    get_enhanced_tracer,
    initialize_enhanced_tracing,
    propagate_trace_context,
    trace_evidence_collection,
    trace_lukhas_operation,
    trace_performance_check,
)
from .evidence_archival import (
    CloudProvider,
    EvidenceArchivalSystem,
    RetentionPolicy,
    StorageTier,
    get_archival_system,
    initialize_archival_system,
    schedule_archival,
)

# Phase 5 Enhanced Observability
from .evidence_collection import (
    ComplianceRegime,
    EvidenceCollectionEngine,
    EvidenceRecord,
    EvidenceType,
    collect_evidence,
    get_evidence_engine,
    initialize_evidence_collection,
)
from .intelligent_alerting import (
    AlertState,
    EscalationLevel,
    IntelligentAlertingSystem,
    NotificationChannel,
    get_alerting_system,
    initialize_alerting,
    trigger_alert,
)
from .opentelemetry_tracing import (
    OTEL_AVAILABLE,
    LUKHASTracer,
    get_lukhas_tracer,
    initialize_tracing,
    shutdown_tracing,
    trace_function,
    trace_matriz_execution,
    trace_memory_recall,
)
from .performance_regression import (
    DetectionMethod,
    PerformanceBaseline,
    PerformanceRegression,
    PerformanceRegressionDetector,
    RegressionSeverity,
    get_regression_detector,
    initialize_regression_detector,
    record_performance_data,
)
from .prometheus_metrics import (
    PROMETHEUS_AVAILABLE,
    LUKHASMetrics,
    MetricsConfig,
    get_lukhas_metrics,
    initialize_metrics,
    shutdown_metrics,
)
from .security_hardening import (
    ObservabilitySecurityHardening,
    SecurityEvent,
    SecurityLevel,
    ThreatType,
    get_security_hardening,
    initialize_security_hardening,
    secure_evidence_operation,
)
import contextlib

__all__ = [
    "OTEL_AVAILABLE",
    "PROMETHEUS_AVAILABLE",
    # Phase 5 Advanced Metrics
    "AdvancedMetricsSystem",
    "AlertState",
    "AnomalyType",
    "AuditReport",
    "CloudProvider",
    # Phase 5 Compliance Dashboard
    "ComplianceDashboard",
    "ComplianceRegime",
    "ComplianceStatus",
    "DetectionMethod",
    # Phase 5 Enhanced Distributed Tracing
    "EnhancedLUKHASTracer",
    "EscalationLevel",
    # Phase 5 Evidence Archival
    "EvidenceArchivalSystem",
    # Phase 5 Evidence Collection
    "EvidenceCollectionEngine",
    "EvidenceRecord",
    "EvidenceType",
    # Phase 5 Intelligent Alerting
    "IntelligentAlertingSystem",
    "LUKHASMetrics",
    "LUKHASSemanticConventions",
    # Core observability (Phase 0-4)
    "LUKHASTracer",
    "MetricAnomaly",
    "MetricSeverity",
    "MetricsConfig",
    "NotificationChannel",
    # Phase 5 Security Hardening
    "ObservabilitySecurityHardening",
    "PerformanceBaseline",
    "PerformanceRegression",
    # Phase 5 Performance Regression Detection
    "PerformanceRegressionDetector",
    "RegressionSeverity",
    "RetentionPolicy",
    "SecurityEvent",
    "SecurityLevel",
    "StorageTier",
    "ThreatType",
    "TraceConfig",
    "collect_evidence",
    "create_correlation_id",
    "extract_trace_context",
    "get_advanced_metrics",
    "get_alerting_system",
    "get_archival_system",
    "get_compliance_dashboard",
    "get_enhanced_tracer",
    "get_evidence_engine",
    "get_lukhas_metrics",
    "get_lukhas_tracer",
    "get_regression_detector",
    "get_security_hardening",
    "initialize_advanced_metrics",
    "initialize_alerting",
    "initialize_archival_system",
    "initialize_compliance_dashboard",
    "initialize_enhanced_tracing",
    "initialize_evidence_collection",
    "initialize_metrics",
    "initialize_regression_detector",
    "initialize_security_hardening",
    "initialize_tracing",
    "propagate_trace_context",
    "record_metric",
    "record_operation_performance",
    "record_performance_data",
    "schedule_archival",
    "secure_evidence_operation",
    "shutdown_metrics",
    "shutdown_tracing",
    "trace_evidence_collection",
    "trace_function",
    "trace_lukhas_operation",
    "trace_matriz_execution",
    "trace_memory_recall",
    "trace_performance_check",
    "trigger_alert",
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
                with contextlib.suppress(Exception):
                    await component.shutdown()
        raise


async def shutdown_phase5_observability():
    """Shutdown all Phase 5 observability components gracefully"""
    shutdown_tasks = []

    try:
        # Shutdown all global instances
        from . import (
            advanced_metrics,
            compliance_dashboard,
            enhanced_distributed_tracing,
            evidence_archival,
            evidence_collection,
            intelligent_alerting,
            performance_regression,
            security_hardening,
        )

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
# T4: code=F821 | ticket=SKELETON-836A1CA1 | owner=lukhas-platform | status=skeleton
# reason: Undefined asyncio in development skeleton - awaiting implementation
# estimate: 4h | priority=low | dependencies=production-implementation
        await asyncio.gather(*shutdown_tasks, return_exceptions=True)  # TODO: asyncio

        print("Phase 5 observability shutdown completed")

    except Exception as e:
        print(f"Error during Phase 5 shutdown: {e}")


# Add shutdown to __all__
__all__.extend([
    "initialize_phase5_observability",
    "shutdown_phase5_observability",
])
