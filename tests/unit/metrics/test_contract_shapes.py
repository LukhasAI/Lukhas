"""
Unit tests for metrics contract shapes and normalization

These tests lock down the canonical metric schemas to prevent drift
between test expectations and actual runtime metric shapes.
"""
import pytest

from candidate.core.metrics_contract import (
    normalize_metrics,
    validate_bio_processor_stats,
    validate_router_stats,
    assert_bio_processor_contract,
    assert_router_contract,
    BioProcessorStats,
    RouterStats,
    NetworkMetrics
)


class TestMetricsNormalization:
    """Test metrics normalization and legacy alias handling"""

    def test_router_metrics_contract(self):
        """Test router metrics meet the canonical contract"""
        # Sample router stats as they might come from the router
        sample = {
            "signals_processed": 10,
            "cascade_preventions": 1,
            "avg_routing_time_ms": 0.2,
            "max_routing_time_ms": 1.5,
            "cascade_prevention_rate": 0.1
        }

        normalized = normalize_metrics(sample)

        # Verify required fields are present
        assert "signals_processed" in normalized
        assert "cascade_preventions" in normalized
        assert "avg_routing_time_ms" in normalized

        # Verify contract validation passes
        assert validate_router_stats(normalized)
        assert_router_contract(normalized)

    def test_biosym_metrics_contract(self):
        """Test bio-symbolic processor metrics meet the canonical contract"""
        # Sample with legacy alias names
        sample = {
            "patterns_processed": 5,  # legacy alias for signals_processed
            "avg_processing_time": 0.1,  # legacy alias for avg_processing_time_ms
            "adaptation_success_rate": 0.4,  # legacy alias for adaptation_rate
            "adaptations_applied": 2,
            "patterns_evolved": 1,
            "coherence_violations": 0
        }

        normalized = normalize_metrics(sample)

        # Verify legacy aliases were mapped to canonical keys
        assert normalized["signals_processed"] == 5
        assert normalized["avg_processing_time_ms"] == 0.1
        assert normalized["adaptation_rate"] == 0.4

        # Verify contract validation passes
        assert validate_bio_processor_stats(normalized)
        assert_bio_processor_contract(normalized)

    def test_legacy_alias_mapping(self):
        """Test all legacy aliases are properly mapped"""
        legacy_data = {
            "patterns_processed": 10,
            "total_processed": 15,  # Should not override patterns_processed
            "avg_processing_time": 2.5,
            "adaptation_success_rate": 0.8,
            "signals_routed": 20,
            "cascade_prevented": 3,
            "routing_latency_avg": 1.2,
            "coherence_score": 0.9,
            "node_count": 5,
            "active_node_count": 4
        }

        normalized = normalize_metrics(legacy_data)

        # Verify aliases were mapped
        assert normalized["signals_processed"] == 10  # from patterns_processed
        assert normalized["avg_processing_time_ms"] == 2.5
        assert normalized["adaptation_rate"] == 0.8
        assert normalized["cascade_preventions"] == 3
        assert normalized["avg_routing_time_ms"] == 1.2
        assert normalized["network_coherence"] == 0.9
        assert normalized["total_nodes"] == 5
        assert normalized["active_nodes"] == 4

    def test_no_overwrite_canonical_keys(self):
        """Test that canonical keys are not overwritten by legacy aliases"""
        data = {
            "signals_processed": 100,  # canonical
            "patterns_processed": 50,  # legacy alias - should not overwrite
            "avg_processing_time_ms": 5.0,  # canonical
            "avg_processing_time": 2.0,  # legacy alias - should not overwrite
        }

        normalized = normalize_metrics(data)

        # Canonical keys should be preserved
        assert normalized["signals_processed"] == 100
        assert normalized["avg_processing_time_ms"] == 5.0
        # Legacy keys should also be present
        assert normalized["patterns_processed"] == 50
        assert normalized["avg_processing_time"] == 2.0


class TestContractValidation:
    """Test contract validation functions"""

    def test_bio_processor_contract_success(self):
        """Test bio processor contract validation with valid data"""
        valid_stats = {
            "signals_processed": 10,
            "adaptations_applied": 3,
            "avg_processing_time_ms": 1.5,
            "adaptation_rate": 0.3,
            "patterns_evolved": 2,
            "coherence_violations": 1
        }

        # Should not raise any exceptions
        assert_bio_processor_contract(valid_stats)

    def test_bio_processor_contract_failure(self):
        """Test bio processor contract validation with invalid data"""
        invalid_stats = {
            "signals_processed": 10,
            # Missing required fields
        }

        with pytest.raises(AssertionError, match="Missing adaptations_applied"):
            assert_bio_processor_contract(invalid_stats)

    def test_router_contract_success(self):
        """Test router contract validation with valid data"""
        valid_stats = {
            "signals_processed": 20,
            "cascade_preventions": 2,
            "avg_routing_time_ms": 0.8,
            "cascade_prevention_rate": 0.1
        }

        # Should not raise any exceptions
        assert_router_contract(valid_stats)

    def test_router_contract_failure(self):
        """Test router contract validation with invalid data"""
        invalid_stats = {
            "signals_processed": 20,
            # Missing required fields
        }

        with pytest.raises(AssertionError, match="Missing cascade_preventions"):
            assert_router_contract(invalid_stats)

    def test_type_validation(self):
        """Test that contract validation checks types"""
        invalid_types = {
            "signals_processed": "not_a_number",  # Should be numeric
            "adaptations_applied": 3,
            "avg_processing_time_ms": 1.5,
            "adaptation_rate": 0.3
        }

        with pytest.raises(AssertionError, match="signals_processed must be numeric"):
            assert_bio_processor_contract(invalid_types)


class TestSchemaDataclasses:
    """Test schema dataclass definitions"""

    def test_bio_processor_stats_schema(self):
        """Test BioProcessorStats dataclass"""
        stats = BioProcessorStats(
            signals_processed=10,
            adaptations_applied=3,
            patterns_evolved=2,
            coherence_violations=1,
            avg_processing_time_ms=1.5,
            adaptation_rate=0.3
        )

        assert stats.signals_processed == 10
        assert stats.adaptation_rate == 0.3
        assert stats.p95_processing_time_ms == 0.0  # default value

    def test_router_stats_schema(self):
        """Test RouterStats dataclass"""
        stats = RouterStats(
            signals_processed=20,
            cascade_preventions=2,
            avg_routing_time_ms=0.8
        )

        assert stats.signals_processed == 20
        assert stats.cascade_preventions == 2
        assert stats.cascade_prevention_rate == 0.0  # default value

    def test_network_metrics_schema(self):
        """Test NetworkMetrics dataclass"""
        metrics = NetworkMetrics(
            total_nodes=5,
            active_nodes=4,
            network_coherence=0.8,
            average_latency_ms=2.0,
            processing_load_avg=0.3,
            queue_utilization_avg=0.1
        )

        assert metrics.total_nodes == 5
        assert metrics.network_coherence == 0.8
        assert metrics.cascade_events == 0  # default value


if __name__ == "__main__":
    pytest.main([__file__, "-v"])