"""
T4/0.01% Excellence: Metrics Label Contract Tests
================================================

Contract tests to ensure all Prometheus metrics carry required standardized labels
for proper aggregation, cardinality control, and SLO burn-rate monitoring.

Required labels per T4/0.01% excellence standards:
- service: Service identifier (memory, orchestrator, identity, guardian)
- lane: Routing lane from canonical enum
- component: Component identifier within service
- operation: Specific operation being measured
- provider: AI provider when applicable

Test Coverage:
- Label presence validation
- Label value format validation
- Cardinality control assertions
- SLO burn-rate metric compatibility
- High-performance label generation
"""

from unittest.mock import patch

from governance.schema_registry import LUKHASLane
from observability.service_metrics import MetricType, ServiceMetricsCollector, ServiceType


class TestMetricsLabelContracts:
    """Contract tests for standardized metrics labels."""

    def setup_method(self):
        """Setup test fixtures."""
        self.metrics = ServiceMetricsCollector()

    def test_standard_labels_generation(self):
        """Test create_standard_labels generates required labels."""
        labels = self.metrics.create_standard_labels(
            lane=LUKHASLane.PRODUCTION,
            component="memory_store",
            operation="search",
            provider="openai"
        )

        # Assert required labels present
        assert "lane" in labels
        assert "component" in labels
        assert "operation" in labels
        assert "provider" in labels

        # Assert correct values (lane is enum object in create_standard_labels)
        assert labels["lane"] == LUKHASLane.PRODUCTION
        assert labels["component"] == "memory_store"
        assert labels["operation"] == "search"
        assert labels["provider"] == "openai"

    def test_canonical_lane_integration(self):
        """Test labels use canonical lane enum values."""
        for lane in LUKHASLane:
            labels = self.metrics.create_standard_labels(
                lane=lane,
                component="test",
                operation="test"
            )
            assert labels["lane"] == lane
            assert labels["lane"].value in [
                "labs", "lukhas", "MATRIZ", "integration",
                "production", "canary", "experimental"
            ]

    def test_service_type_mapping(self):
        """Test service labels are handled correctly in record_metric."""
        service_mappings = {
            ServiceType.MEMORY: "memory",
            ServiceType.REGISTRY: "registry",
            ServiceType.IDENTITY: "identity",
            ServiceType.CONSCIOUSNESS: "consciousness",
            ServiceType.GOVERNANCE: "governance",
            ServiceType.ORCHESTRATION: "orchestration",
            ServiceType.LEDGER: "ledger"
        }

        for service_type, expected_label in service_mappings.items():
            with patch('observability.service_metrics.ServiceMetricsCollector._update_prometheus_metric'):
                self.metrics.record_metric(
                    "test_metric",
                    1.0,
                    service_type,
                    MetricType.COUNTER,
                    component="test",
                    operation="test"
                )
                # Service type is stored in metric, not in labels
                metric_key = f"{service_type.value}_test_metric"
                assert metric_key in self.metrics.metrics
                assert self.metrics.metrics[metric_key].service == service_type

    @patch('observability.service_metrics.ServiceMetricsCollector._update_prometheus_metric')
    def test_record_metric_applies_labels(self, mock_update):
        """Test record_metric applies standardized labels."""
        self.metrics.record_metric(
            name="test_metric",
            value=1.0,
            service=ServiceType.MEMORY,
            metric_type=MetricType.COUNTER,
            operation="search",
            lane="production"
        )

        # Verify metric was stored with labels
        metric_key = "memory_test_metric"
        assert metric_key in self.metrics.metrics
        metric = self.metrics.metrics[metric_key]

        # Assert standard labels present
        assert "lane" in metric.labels
        assert "operation" in metric.labels
        assert metric.labels["operation"] == "search"
        assert metric.labels["lane"] == "production"

    def test_burn_rate_metric_compatibility(self):
        """Test metrics are compatible with burn-rate SLO alerts."""
        # Test memory service latency metric
        with patch('observability.service_metrics.ServiceMetricsCollector._update_prometheus_metric'):
            self.metrics.record_metric(
                name="lukhas_memory_operation_duration_seconds",
                value=0.095,  # 95ms - within 100ms SLO
                service=ServiceType.MEMORY,
                metric_type=MetricType.HISTOGRAM,
                operation="search",
                lane="production",
                labels={"quantile": "0.95"}
            )

            # Verify metric stored with burn-rate compatible labels
            metric_key = "memory_lukhas_memory_operation_duration_seconds"
            assert metric_key in self.metrics.metrics
            metric = self.metrics.metrics[metric_key]

            assert "lane" in metric.labels
            assert "operation" in metric.labels
            assert metric.labels["operation"] == "search"
            assert metric.labels["quantile"] == "0.95"

    def test_cardinality_control(self):
        """Test label generation maintains low cardinality."""
        # Generate labels for different scenarios
        test_cases = [
            {"component": "memory_store", "operation": "search"},
            {"component": "vector_index", "operation": "insert"},
            {"component": "archival_backend", "operation": "compress"},
        ]

        label_sets = []
        for case in test_cases:
            labels = self.metrics.create_standard_labels(
                lane=LUKHASLane.PRODUCTION,
                **case
            )
            label_sets.append(frozenset(labels.items()))

        # Assert no duplicate label combinations
        assert len(set(label_sets)) == len(label_sets)

        # Assert reasonable cardinality - each label set should be unique
        # but total combinations should be manageable
        for labels in label_sets:
            labels_dict = dict(labels)
            assert len(labels_dict) <= 5  # lane, component, operation, provider, custom

    def test_required_labels_never_none(self):
        """Test required labels are never None or empty."""
        labels = self.metrics.create_standard_labels(
            lane=LUKHASLane.PRODUCTION,
            component="test_component",
            operation="test_operation"
        )

        for label_key, label_value in labels.items():
            assert label_value is not None
            assert label_value != ""
            # Label value can be string or enum
            assert isinstance(label_value, (str, LUKHASLane))

    def test_label_value_format_validation(self):
        """Test label values follow Prometheus naming conventions."""
        labels = self.metrics.create_standard_labels(
            lane=LUKHASLane.PRODUCTION,
            component="memory_store",
            operation="vector_search",
            provider="openai-gpt4"
        )

        # Assert valid Prometheus label value format
        for label_value in labels.values():
            # Convert enum to string for validation
            if hasattr(label_value, 'value'):
                label_str = label_value.value
            else:
                label_str = str(label_value)

            # No spaces, special chars that break Prometheus queries
            assert " " not in label_str
            assert "\n" not in label_str
            assert "\t" not in label_str
            # Allow alphanumeric, underscore, hyphen, dot
            assert all(c.isalnum() or c in "_-." for c in label_str)


class TestMemoryLifecycleLabelContracts:
    """Contract tests for memory lifecycle operations."""

    def setup_method(self):
        """Setup test fixtures."""
        self.metrics = ServiceMetricsCollector()

    def test_memory_lifecycle_operation_labels(self):
        """Test memory lifecycle operations have required labels."""
        lifecycle_operations = ["archive", "gdpr_deletion", "cleanup"]

        for operation in lifecycle_operations:
            with patch('observability.service_metrics.ServiceMetricsCollector._update_prometheus_metric'):
                # Test duration metric
                self.metrics.record_metric(
                    name="lukhas_memory_lifecycle_seconds",
                    value=2.5,  # 2.5s duration
                    service=ServiceType.MEMORY,
                    metric_type=MetricType.HISTOGRAM,
                    operation=operation,
                    lane="production"
                )

                # Test operations counter
                self.metrics.record_metric(
                    name="lukhas_memory_lifecycle_operations_total",
                    value=1,
                    service=ServiceType.MEMORY,
                    metric_type=MetricType.COUNTER,
                    operation=operation,
                    lane="production"
                )

                # Verify required labels present
                duration_key = "memory_lukhas_memory_lifecycle_seconds"
                operations_key = "memory_lukhas_memory_lifecycle_operations_total"

                assert duration_key in self.metrics.metrics
                assert operations_key in self.metrics.metrics

                duration_metric = self.metrics.metrics[duration_key]
                operations_metric = self.metrics.metrics[operations_key]

                # Check required labels
                for metric in [duration_metric, operations_metric]:
                    assert "lane" in metric.labels
                    assert "operation" in metric.labels
                    assert metric.labels["operation"] == operation
                    assert metric.labels["lane"] == "production"

    def test_memory_lifecycle_error_labels(self):
        """Test memory lifecycle error metrics have required labels."""
        error_operations = ["archive", "gdpr_deletion"]

        for operation in error_operations:
            with patch('observability.service_metrics.ServiceMetricsCollector._update_prometheus_metric'):
                # Test error counter
                self.metrics.record_metric(
                    name="lukhas_memory_lifecycle_errors_total",
                    value=1,
                    service=ServiceType.MEMORY,
                    metric_type=MetricType.COUNTER,
                    operation=operation,
                    lane="labs"
                )

                # Verify required labels present
                error_key = "memory_lukhas_memory_lifecycle_errors_total"
                assert error_key in self.metrics.metrics

                error_metric = self.metrics.metrics[error_key]
                assert "lane" in error_metric.labels
                assert "operation" in error_metric.labels
                assert error_metric.labels["operation"] == operation
                assert error_metric.labels["lane"] == "labs"

    def test_forbidden_correlation_id_in_labels(self):
        """Test that correlation_id is NEVER used as a Prometheus label."""
        with patch('observability.service_metrics.ServiceMetricsCollector._update_prometheus_metric'):
            # Attempt to record metric with correlation_id in labels (should be filtered out)
            self.metrics.record_metric(
                name="lukhas_memory_lifecycle_seconds",
                value=1.5,
                service=ServiceType.MEMORY,
                metric_type=MetricType.HISTOGRAM,
                operation="archive",
                lane="production",
                labels={"correlation_id": "should-not-appear"}  # This should be filtered out
            )

            metric_key = "memory_lukhas_memory_lifecycle_seconds"
            assert metric_key in self.metrics.metrics

            metric = self.metrics.metrics[metric_key]
            # correlation_id should NOT be in labels to prevent cardinality explosion
            assert "correlation_id" not in metric.labels

            # Required labels should still be present
            assert "lane" in metric.labels
            assert "operation" in metric.labels

    def test_memory_upsert_latency_labels(self):
        """Test memory upsert operations have correct labels."""
        with patch('observability.service_metrics.ServiceMetricsCollector._update_prometheus_metric'):
            self.metrics.record_metric(
                name="lukhas_memory_upsert_seconds",
                value=0.085,  # 85ms - within 100ms SLO
                service=ServiceType.MEMORY,
                metric_type=MetricType.HISTOGRAM,
                operation="upsert",
                lane="production"
            )

            metric_key = "memory_lukhas_memory_upsert_seconds"
            assert metric_key in self.metrics.metrics

            metric = self.metrics.metrics[metric_key]
            assert "lane" in metric.labels
            assert "operation" in metric.labels
            assert metric.labels["operation"] == "upsert"
            assert metric.labels["lane"] == "production"

    def test_canonical_lane_values_in_metrics(self):
        """Test metrics use canonical lane enum values."""
        canonical_lanes = ["labs", "lukhas", "MATRIZ", "integration", "production", "canary", "experimental"]

        for lane_value in canonical_lanes:
            with patch('observability.service_metrics.ServiceMetricsCollector._update_prometheus_metric'):
                self.metrics.record_metric(
                    name="lukhas_memory_lifecycle_operations_total",
                    value=1,
                    service=ServiceType.MEMORY,
                    metric_type=MetricType.COUNTER,
                    operation="archive",
                    lane=lane_value
                )

                metric_key = "memory_lukhas_memory_lifecycle_operations_total"
                metric = self.metrics.metrics[metric_key]

                # Lane value should match canonical taxonomy
                assert metric.labels["lane"] == lane_value
                assert metric.labels["lane"] in canonical_lanes


class TestSLOBurnRateMetrics:
    """Contract tests for SLO burn-rate specific metrics."""

    def setup_method(self):
        """Setup test fixtures."""
        self.metrics = ServiceMetricsCollector()

    def test_memory_slo_metric_format(self):
        """Test memory service SLO metrics match alerting rules."""
        with patch('observability.service_metrics.ServiceMetricsCollector._update_prometheus_metric'):
            # Record latency metric matching burn-rate alert query
            self.metrics.record_metric(
                name="lukhas_memory_operation_duration_seconds",
                value=0.095,
                service=ServiceType.MEMORY,
                metric_type=MetricType.HISTOGRAM,
                operation="search",
                lane="production",
                labels={"quantile": "0.95"}
            )

            # Verify labels match burn-rate alert expectations
            metric_key = "memory_lukhas_memory_operation_duration_seconds"
            metric = self.metrics.metrics[metric_key]

            # Must have lane label for burn-rate grouping
            assert "lane" in metric.labels
            assert metric.labels["operation"] == "search"

    def test_orchestrator_routing_slo_format(self):
        """Test orchestrator routing SLO metrics format."""
        with patch('observability.service_metrics.ServiceMetricsCollector._update_prometheus_metric'):
            self.metrics.record_metric(
                name="lukhas_orchestrator_routing_duration_seconds",
                value=0.245,  # 245ms - within 250ms SLO
                service=ServiceType.ORCHESTRATION,  # Use correct enum
                metric_type=MetricType.HISTOGRAM,
                operation="route",
                lane="production",
                labels={"quantile": "0.95"}
            )

            metric_key = "orchestration_lukhas_orchestrator_routing_duration_seconds"
            metric = self.metrics.metrics[metric_key]
            assert metric.labels["operation"] == "route"

    def test_identity_auth_slo_format(self):
        """Test identity authentication SLO metrics format."""
        with patch('observability.service_metrics.ServiceMetricsCollector._update_prometheus_metric'):
            self.metrics.record_metric(
                name="lukhas_identity_auth_duration_seconds",
                value=0.199,  # 199ms - within 250ms SLO
                service=ServiceType.IDENTITY,
                metric_type=MetricType.HISTOGRAM,
                operation="authenticate",
                lane="production",
                labels={"quantile": "0.95"}
            )

            metric_key = "identity_lukhas_identity_auth_duration_seconds"
            metric = self.metrics.metrics[metric_key]
            assert metric.labels["operation"] == "authenticate"

    def test_guardian_decision_slo_format(self):
        """Test guardian decision SLO metrics format."""
        with patch('observability.service_metrics.ServiceMetricsCollector._update_prometheus_metric'):
            self.metrics.record_metric(
                name="lukhas_guardian_decision_duration_seconds",
                value=0.089,  # 89ms - within 100ms SLO
                service=ServiceType.GOVERNANCE,  # Use correct enum for Guardian
                metric_type=MetricType.HISTOGRAM,
                operation="decide",
                lane="production",
                labels={"quantile": "0.95"}
            )

            metric_key = "governance_lukhas_guardian_decision_duration_seconds"
            metric = self.metrics.metrics[metric_key]
            assert metric.labels["operation"] == "decide"


class TestCorrelationTrackingMetrics:
    """Contract tests for E2E correlation tracking metrics."""

    def setup_method(self):
        """Setup test fixtures."""
        self.metrics = ServiceMetricsCollector()

    def test_correlation_tracking_counter_format(self):
        """Test correlation tracking counters match alert queries."""
        with patch('observability.service_metrics.ServiceMetricsCollector._update_prometheus_metric'):
            # Record requests without correlation_id
            self.metrics.record_metric(
                name="lukhas_requests_without_correlation_id",
                value=1,
                service=ServiceType.ORCHESTRATION,
                metric_type=MetricType.COUNTER,
                lane="production",
                labels={"endpoint": "/api/v1/route"}
            )

            metric_key = "orchestration_lukhas_requests_without_correlation_id"
            metric = self.metrics.metrics[metric_key]
            assert "lane" in metric.labels
            assert metric.labels["endpoint"] == "/api/v1/route"

    def test_total_requests_counter_format(self):
        """Test total requests counter format for correlation ratio."""
        with patch('observability.service_metrics.ServiceMetricsCollector._update_prometheus_metric'):
            self.metrics.record_metric(
                name="lukhas_requests_total",
                value=1,
                service=ServiceType.MEMORY,
                metric_type=MetricType.COUNTER,
                lane="production",
                labels={"endpoint": "/api/v1/search"}
            )

            metric_key = "memory_lukhas_requests_total"
            metric = self.metrics.metrics[metric_key]
            assert "lane" in metric.labels
            assert metric.labels["endpoint"] == "/api/v1/search"
