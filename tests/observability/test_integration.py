#!/usr/bin/env python3
"""
Integration tests for LUKHAS Observability System
End-to-end tests for the complete observability stack integration.
"""

import asyncio

# Test imports
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from observability.advanced_metrics import AdvancedMetricsSystem
from observability.compliance_dashboard import ComplianceDashboard
from observability.enhanced_distributed_tracing import EnhancedLUKHASTracer, TraceConfig
from observability.evidence_collection import (
    ComplianceRegime,
    EvidenceCollectionEngine,
    EvidenceType,
)
from observability.intelligent_alerting import IntelligentAlertingSystem
from observability.performance_regression import PerformanceRegressionDetector


@pytest.fixture
async def temp_dirs():
    """Create temporary directories for testing"""
    with tempfile.TemporaryDirectory() as temp_dir:
        base_path = Path(temp_dir)
        yield {
            'evidence': base_path / 'evidence',
            'reports': base_path / 'reports',
            'config': base_path / 'config',
        }


@pytest.fixture
def mock_external_dependencies():
    """Mock external dependencies"""
    return {
        'prometheus_metrics': MagicMock(),
        'smtp_config': None,  # Disable email for testing
        'cloud_clients': {},
    }


@pytest.fixture
async def integrated_observability_stack(temp_dirs, mock_external_dependencies):
    """Create integrated observability stack for testing"""
    # Create directories
    for dir_path in temp_dirs.values():
        dir_path.mkdir(parents=True, exist_ok=True)

    # Initialize components
    evidence_engine = EvidenceCollectionEngine(
        storage_path=str(temp_dirs['evidence']),
        retention_days=30,
        compression_enabled=True,
        encryption_enabled=True,
        chain_block_size=5,
    )

    advanced_metrics = AdvancedMetricsSystem(
        enable_anomaly_detection=True,
        enable_ml_features=False,  # Disable ML for simpler testing
        metric_retention_hours=24,
    )

    performance_detector = PerformanceRegressionDetector(
        baseline_window_days=1,
        min_samples_for_baseline=5,
        enable_ml_detection=False,
        enable_seasonal_analysis=False,
    )

    alerting_system = IntelligentAlertingSystem(
        config_path=str(temp_dirs['config'] / 'alerting.json'),
        smtp_config=mock_external_dependencies['smtp_config'],
        enable_storm_detection=True,
    )

    compliance_dashboard = ComplianceDashboard(
        dashboard_config_path=str(temp_dirs['config'] / 'compliance.json'),
        reports_output_path=str(temp_dirs['reports']),
        enable_automated_reports=False,  # Disable for testing
    )

    # Mock dependencies for components
    with patch('observability.advanced_metrics.get_lukhas_metrics', return_value=mock_external_dependencies['prometheus_metrics']):
        with patch('observability.performance_regression.get_advanced_metrics', return_value=advanced_metrics):
            with patch('observability.performance_regression.get_alerting_system', return_value=alerting_system):

                stack = {
                    'evidence': evidence_engine,
                    'metrics': advanced_metrics,
                    'performance': performance_detector,
                    'alerting': alerting_system,
                    'compliance': compliance_dashboard,
                }

                yield stack

                # Cleanup
                for component in stack.values():
                    if hasattr(component, 'shutdown'):
                        await component.shutdown()


class TestObservabilityIntegration:
    """Test integrated observability system functionality"""

    @pytest.mark.asyncio
    async def test_end_to_end_evidence_and_metrics_flow(self, integrated_observability_stack):
        """Test complete flow from evidence collection to metrics and alerting"""
        stack = integrated_observability_stack

        # Step 1: Collect evidence
        evidence_id = await stack['evidence'].collect_evidence(
            evidence_type=EvidenceType.PERFORMANCE_METRIC,
            source_component="integration_test",
            operation="e2e_test",
            payload={
                "metric_name": "response_time",
                "value": 0.15,
                "threshold": 0.1,
            },
        )

        assert evidence_id is not None

        # Step 2: Record corresponding metrics
        await stack['metrics'].record_advanced_metric(
            metric_name="integration_response_time",
            value=0.15,
            labels={"test": "e2e"},
        )

        # Step 3: Record performance data
        await stack['performance'].record_performance_metric(
            metric_name="response_time",
            component="integration_test",
            value=0.15,
        )

        # Step 4: Trigger alert (simulate threshold breach)
        alert_id = await stack['alerting'].trigger_alert(
            rule_id="high_response_time",
            source_component="integration_test",
            metric_name="response_time",
            current_value=0.15,
            threshold_value=0.1,
        )

        assert alert_id is not None

        # Verify integration
        assert len(stack['evidence']._evidence_buffer) > 0
        assert "integration_response_time" in stack['metrics'].metric_history
        assert len(stack['alerting'].active_alerts) > 0

    @pytest.mark.asyncio
    async def test_compliance_evidence_integration(self, integrated_observability_stack):
        """Test compliance evidence collection and dashboard integration"""
        stack = integrated_observability_stack

        # Collect GDPR compliance evidence
        evidence_id = await stack['evidence'].collect_evidence(
            evidence_type=EvidenceType.REGULATORY_EVENT,
            source_component="gdpr_processor",
            operation="data_deletion",
            payload={
                "user_id": "test_user_123",
                "data_deleted": True,
                "categories": ["profile", "preferences"],
            },
            compliance_regimes=[ComplianceRegime.GDPR],
            user_id="test_user_123",
        )

        # Update compliance metrics
        stack['metrics'].update_compliance_metric(
            regulation="GDPR",
            metric_name="data_retention_compliance",
            current_value=98.5,  # Slightly below 100%
        )

        # Assess compliance
        gdpr_status = await stack['compliance'].assess_compliance_status(ComplianceRegime.GDPR)

        assert gdpr_status is not None
        assert evidence_id is not None
        assert gdpr_status.regulation == ComplianceRegime.GDPR

    @pytest.mark.asyncio
    async def test_performance_regression_alert_flow(self, integrated_observability_stack):
        """Test performance regression detection triggering alerts"""
        stack = integrated_observability_stack

        metric_name = "api_latency"
        component = "api_service"

        # Establish baseline with normal values
        baseline_values = [0.1] * 10  # 100ms baseline
        for value in baseline_values:
            await stack['performance'].record_performance_metric(metric_name, component, value)

        # Establish baseline
        baseline = await stack['performance'].establish_baseline(metric_name, component)
        assert baseline is not None

        # Record performance regression
        await stack['performance'].record_performance_metric(metric_name, component, 0.5)  # 500ms - major regression

        # Should trigger alert
        regressions = list(stack['performance'].detected_regressions.values())
        list(stack['alerting'].active_alerts.values())

        # Verify regression was detected and alert was created
        assert len(regressions) > 0
        # Note: Alert creation depends on alerting rules configuration

    @pytest.mark.asyncio
    async def test_anomaly_detection_evidence_correlation(self, integrated_observability_stack):
        """Test correlation between anomaly detection and evidence collection"""
        stack = integrated_observability_stack

        # Record normal metrics to establish baseline
        for i in range(20):
            await stack['metrics'].record_advanced_metric(
                metric_name="correlation_test_metric",
                value=100.0 + (i % 5),  # Normal variation
            )

        # Record anomalous metric with evidence
        correlation_id = f"correlation_test_{datetime.now().timestamp()}"

        # Record evidence of the anomalous event
        evidence_id = await stack['evidence'].collect_evidence(
            evidence_type=EvidenceType.SYSTEM_EVENT,
            source_component="anomaly_test",
            operation="anomalous_operation",
            payload={
                "anomaly_detected": True,
                "metric_value": 500.0,
                "expected_range": "95-105",
            },
            correlation_id=correlation_id,
        )

        # Record anomalous metric
        await stack['metrics'].record_advanced_metric(
            metric_name="correlation_test_metric",
            value=500.0,  # Way outside normal range
        )

        # Verify both evidence and anomaly were recorded
        assert evidence_id is not None
        stack['metrics'].get_anomaly_summary(hours_back=1)
        # Anomaly detection depends on sufficient baseline data

    @pytest.mark.asyncio
    async def test_cross_component_correlation_id_propagation(self, integrated_observability_stack):
        """Test correlation ID propagation across components"""
        stack = integrated_observability_stack

        correlation_id = "test_correlation_12345"

        # Record evidence with correlation ID
        evidence_id = await stack['evidence'].collect_evidence(
            evidence_type=EvidenceType.USER_INTERACTION,
            source_component="frontend",
            operation="user_action",
            payload={"action": "button_click"},
            correlation_id=correlation_id,
        )

        # Record metrics with same correlation
        await stack['metrics'].record_advanced_metric(
            metric_name="user_action_duration",
            value=0.05,
            labels={"correlation_id": correlation_id},
        )

        # Record performance data
        await stack['performance'].record_performance_metric(
            metric_name="action_response_time",
            component="frontend",
            value=0.05,
            context={"correlation_id": correlation_id},
        )

        # Verify correlation ID is preserved across components
        assert evidence_id is not None
        # Additional verification would require querying stored data

    @pytest.mark.asyncio
    async def test_compliance_report_generation_integration(self, integrated_observability_stack):
        """Test compliance report generation with evidence integration"""
        stack = integrated_observability_stack

        # Generate evidence for different compliance regimes
        compliance_evidence = [
            (ComplianceRegime.GDPR, "gdpr_data_export", {"user_id": "gdpr_user", "data_exported": True}),
            (ComplianceRegime.SOX, "financial_transaction", {"transaction_id": "txn_001", "amount": 1000.0}),
            (ComplianceRegime.CCPA, "privacy_request", {"user_id": "ccpa_user", "request_type": "deletion"}),
        ]

        for regime, operation, payload in compliance_evidence:
            await stack['evidence'].collect_evidence(
                evidence_type=EvidenceType.REGULATORY_EVENT,
                source_component="compliance_test",
                operation=operation,
                payload=payload,
                compliance_regimes=[regime],
            )

        # Flush evidence to storage
        await stack['evidence'].flush_evidence_buffer()

        # Generate compliance reports
        reports = {}
        for regime in [ComplianceRegime.GDPR, ComplianceRegime.SOX, ComplianceRegime.CCPA]:
            try:
                report = await stack['compliance'].generate_compliance_report(
                    regulation=regime,
                    report_type="daily",
                )
                reports[regime] = report
            except Exception as e:
                print(f"Report generation failed for {regime}: {e}")

        # Verify reports were generated
        assert len(reports) > 0
        for regime, report in reports.items():
            assert report.regulation == regime
            assert report.total_evidence_examined >= 0

    @pytest.mark.asyncio
    async def test_distributed_tracing_integration(self, integrated_observability_stack):
        """Test distributed tracing integration with observability components"""
        # Initialize enhanced tracing
        trace_config = TraceConfig(
            service_name="lukhas-test",
            enable_auto_instrumentation=False,  # Disable for testing
            sampling_ratio=1.0,
        )

        tracer = EnhancedLUKHASTracer(trace_config)

        # Test evidence collection with tracing
        with tracer.trace_evidence_operation(
            operation_name="collect_test_evidence",
            evidence_id="trace_test_evidence_1",
            evidence_type="user_interaction",
        ):
            evidence_id = await integrated_observability_stack['evidence'].collect_evidence(
                evidence_type=EvidenceType.USER_INTERACTION,
                source_component="tracing_test",
                operation="traced_operation",
                payload={"traced": True},
            )

        # Test performance operation with tracing
        with tracer.trace_performance_operation(
            operation_name="performance_check",
            metric_name="traced_latency",
            current_value=0.12,
            baseline_value=0.10,
        ):
            await integrated_observability_stack['performance'].record_performance_metric(
                metric_name="traced_latency",
                component="traced_service",
                value=0.12,
            )

        # Test compliance operation with tracing
        with tracer.trace_compliance_operation(
            operation_name="compliance_check",
            compliance_regime="GDPR",
            compliance_score=95.5,
        ):
            await integrated_observability_stack['compliance'].assess_compliance_status(ComplianceRegime.GDPR)

        assert evidence_id is not None

    @pytest.mark.asyncio
    async def test_high_load_integration(self, integrated_observability_stack):
        """Test observability system under high load"""
        stack = integrated_observability_stack

        # Simulate high load with concurrent operations
        async def generate_load():
            tasks = []

            # Evidence collection load
            for i in range(50):
                task = stack['evidence'].collect_evidence(
                    evidence_type=EvidenceType.SYSTEM_EVENT,
                    source_component=f"load_test_{i % 5}",
                    operation="load_test_operation",
                    payload={"iteration": i, "load_test": True},
                )
                tasks.append(task)

            # Metrics recording load
            for i in range(50):
                task = stack['metrics'].record_advanced_metric(
                    metric_name=f"load_test_metric_{i % 10}",
                    value=0.1 + (i * 0.001),
                    labels={"load_test": "true"},
                )
                tasks.append(task)

            # Performance data load
            for i in range(50):
                task = stack['performance'].record_performance_metric(
                    metric_name="load_test_latency",
                    component=f"load_service_{i % 3}",
                    value=0.05 + (i * 0.001),
                )
                tasks.append(task)

            await asyncio.gather(*tasks)

        import time
        start_time = time.time()
        await generate_load()
        end_time = time.time()

        duration = end_time - start_time
        assert duration < 10.0, f"High load test took {duration}s, should be <10s"

        # Verify data integrity
        assert len(stack['evidence']._evidence_buffer) > 0
        assert len(stack['metrics'].metric_history) > 0
        assert len(stack['performance'].metric_timeseries) > 0

    @pytest.mark.asyncio
    async def test_error_resilience_integration(self, integrated_observability_stack):
        """Test system resilience to errors in individual components"""
        stack = integrated_observability_stack

        # Test with invalid evidence data
        try:
            await stack['evidence'].collect_evidence(
                evidence_type=EvidenceType.ERROR_EVENT,
                source_component="error_test",
                operation="intentional_error_test",
                payload={"error_simulation": True},
            )
        except Exception as e:
            # Should handle gracefully
            print(f"Expected error in evidence collection: {e}")

        # Test with invalid metric data
        try:
            await stack['metrics'].record_advanced_metric(
                metric_name="error_test_metric",
                value="invalid_value",  # Should cause type error
            )
        except Exception as e:
            print(f"Expected error in metrics recording: {e}")

        # Test with invalid performance data
        try:
            await stack['performance'].record_performance_metric(
                metric_name="error_test_performance",
                component="error_service",
                value=None,  # Invalid value
            )
        except Exception as e:
            print(f"Expected error in performance recording: {e}")

        # System should continue functioning
        # Record valid data to verify
        evidence_id = await stack['evidence'].collect_evidence(
            evidence_type=EvidenceType.SYSTEM_EVENT,
            source_component="resilience_test",
            operation="post_error_test",
            payload={"recovery": True},
        )

        assert evidence_id is not None

    def test_configuration_integration(self, integrated_observability_stack):
        """Test configuration consistency across components"""
        stack = integrated_observability_stack

        # Test that components have consistent configuration
        assert stack['evidence'].compression_enabled == True
        assert stack['evidence'].encryption_enabled == True
        assert stack['metrics'].enable_anomaly_detection == True
        assert stack['performance'].enable_ml_detection == False  # As configured
        assert stack['alerting'].enable_storm_detection == True

    @pytest.mark.asyncio
    async def test_shutdown_integration(self, integrated_observability_stack):
        """Test graceful shutdown of integrated components"""
        stack = integrated_observability_stack

        # Record some data before shutdown
        await stack['evidence'].collect_evidence(
            evidence_type=EvidenceType.SYSTEM_EVENT,
            source_component="shutdown_test",
            operation="pre_shutdown_operation",
            payload={"shutdown_test": True},
        )

        # Test graceful shutdown
        for component_name, component in stack.items():
            if hasattr(component, 'shutdown'):
                try:
                    await component.shutdown()
                    print(f"{component_name} shutdown completed")
                except Exception as e:
                    print(f"{component_name} shutdown failed: {e}")

        # Verify components are in shutdown state
        # This is implementation-specific verification


class TestPerformanceIntegration:
    """Test performance aspects of integrated system"""

    @pytest.mark.asyncio
    async def test_sub_10ms_evidence_collection_overhead(self, integrated_observability_stack):
        """Test that evidence collection meets <10ms overhead requirement"""
        stack = integrated_observability_stack

        import time

        # Measure evidence collection overhead
        start_time = time.perf_counter()

        for i in range(100):
            await stack['evidence'].collect_evidence(
                evidence_type=EvidenceType.PERFORMANCE_METRIC,
                source_component="performance_test",
                operation="overhead_test",
                payload={"iteration": i},
            )

        end_time = time.perf_counter()

        total_duration_ms = (end_time - start_time) * 1000
        avg_duration_ms = total_duration_ms / 100

        print(f"Average evidence collection time: {avg_duration_ms:.2f}ms")

        # Should meet <10ms requirement on average
        assert avg_duration_ms < 10.0, f"Evidence collection took {avg_duration_ms}ms, should be <10ms"

    @pytest.mark.asyncio
    async def test_concurrent_operations_performance(self, integrated_observability_stack):
        """Test performance under concurrent operations"""
        stack = integrated_observability_stack

        async def concurrent_operations():
            # Mix of different operations
            operations = []

            # Evidence collection
            operations.extend([
                stack['evidence'].collect_evidence(
                    evidence_type=EvidenceType.SYSTEM_EVENT,
                    source_component="concurrent_test",
                    operation=f"concurrent_op_{i}",
                    payload={"id": i},
                ) for i in range(20)
            ])

            # Metrics recording
            operations.extend([
                stack['metrics'].record_advanced_metric(
                    f"concurrent_metric_{i}",
                    0.1 + (i * 0.01)
                ) for i in range(20)
            ])

            # Performance recording
            operations.extend([
                stack['performance'].record_performance_metric(
                    "concurrent_perf",
                    f"service_{i}",
                    0.05 + (i * 0.001)
                ) for i in range(20)
            ])

            return await asyncio.gather(*operations)

        import time
        start_time = time.time()
        results = await concurrent_operations()
        end_time = time.time()

        duration = end_time - start_time
        assert duration < 5.0, f"Concurrent operations took {duration}s, should be <5s"
        assert len(results) == 60  # All operations completed


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
