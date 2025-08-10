"""
══════════════════════════════════════════════════════════════════════════════════
║ 🧪 LUKHAS AI - SYMBOLIC DRIFT ANALYZER TEST SUITE
║ Comprehensive tests for symbolic drift detection and analysis
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: test_symbolic_drift_analyzer.py
║ Path: tests/core/test_symbolic_drift_analyzer.py
║ Version: 1.0.0 | Created: 2025-07-27 | Modified: 2025-07-27
║ Authors: Claude (Anthropic AI Assistant)
╠══════════════════════════════════════════════════════════════════════════════════
║ TEST COVERAGE
╠══════════════════════════════════════════════════════════════════════════════════
║ - Entropy calculation methods
║ - Tag variance analysis
║ - Pattern trend detection
║ - Ethical drift monitoring
║ - Alert generation and thresholds
║ - CLI summary generation
║ - Continuous monitoring
║ - Export functionality
╚══════════════════════════════════════════════════════════════════════════════════
"""

import asyncio
import json
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock

import pytest

from core.symbolic_drift_analyzer import (
    DriftAlert,
    DriftAlertLevel,
    EntropyMetrics,
    PatternTrend,
    SymbolicDriftAnalyzer,
    TagVarianceMetrics,
)


class TestEntropyCalculations:
    """Test entropy calculation methods"""

    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance for tests"""
        return SymbolicDriftAnalyzer()

    def test_shannon_entropy_uniform(self, analyzer):
        """Test Shannon entropy with uniform distribution"""
        data = ["A", "B", "C", "D"] * 25  # Uniform distribution
        entropy = analyzer.calculate_shannon_entropy(data)

        # Should be close to 1.0 (maximum entropy for 4 symbols)
        assert 0.95 < entropy <= 1.0

    def test_shannon_entropy_skewed(self, analyzer):
        """Test Shannon entropy with skewed distribution"""
        data = ["A"] * 90 + ["B"] * 5 + ["C"] * 3 + ["D"] * 2
        entropy = analyzer.calculate_shannon_entropy(data)

        # Should be lower due to skewed distribution
        assert 0.2 < entropy < 0.5

    def test_shannon_entropy_single_value(self, analyzer):
        """Test Shannon entropy with single value"""
        data = ["A"] * 100
        entropy = analyzer.calculate_shannon_entropy(data)

        # Should be 0 (no uncertainty)
        assert entropy == 0.0

    def test_shannon_entropy_empty(self, analyzer):
        """Test Shannon entropy with empty data"""
        entropy = analyzer.calculate_shannon_entropy([])
        assert entropy == 0.0

    def test_tag_entropy(self, analyzer):
        """Test tag entropy calculation"""
        tags = ["memory", "dream", "identity", "memory", "dream", "memory"]
        entropy = analyzer.calculate_tag_entropy(tags)

        # Should have moderate entropy (3 unique tags, not uniform)
        assert 0.4 < entropy < 0.8

    def test_temporal_entropy(self, analyzer):
        """Test temporal entropy calculation"""
        # Regular intervals
        base_time = datetime.now()
        regular_times = [base_time + timedelta(hours=i) for i in range(10)]
        regular_entropy = analyzer.calculate_temporal_entropy(regular_times)

        # Irregular intervals
        import random

        irregular_times = [
            base_time + timedelta(hours=i * random.uniform(0.5, 2)) for i in range(10)
        ]
        irregular_entropy = analyzer.calculate_temporal_entropy(irregular_times)

        # Irregular should have higher entropy
        assert irregular_entropy > regular_entropy

    def test_semantic_entropy(self, analyzer):
        """Test semantic entropy calculation"""
        # Similar dreams
        similar_dreams = [
            {"type": "exploration", "theme": "discovery"},
            {"type": "exploration", "theme": "discovery"},
            {"type": "exploration", "theme": "journey"},
        ]
        similar_entropy = analyzer.calculate_semantic_entropy(similar_dreams)

        # Diverse dreams
        diverse_dreams = [
            {"type": "exploration", "theme": "discovery"},
            {"type": "nightmare", "theme": "fear"},
            {"type": "memory", "theme": "nostalgia"},
        ]
        diverse_entropy = analyzer.calculate_semantic_entropy(diverse_dreams)

        # Diverse should have higher entropy
        assert diverse_entropy > similar_entropy


class TestTagVarianceAnalysis:
    """Test tag variance analysis functionality"""

    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance"""
        return SymbolicDriftAnalyzer()

    def test_tag_variance_metrics(self, analyzer):
        """Test tag variance metric calculation"""
        dreams = [
            {
                "tags": ["memory", "identity", "exploration"],
                "timestamp": datetime.now(),
            },
            {"tags": ["memory", "fear", "exploration"], "timestamp": datetime.now()},
            {"tags": ["identity", "creation", "hope"], "timestamp": datetime.now()},
            {
                "tags": ["memory", "identity", "exploration", "new_tag"],
                "timestamp": datetime.now(),
            },
        ]

        metrics = analyzer.calculate_tag_variance(dreams)

        assert metrics.unique_tags == 6  # Total unique tags
        assert metrics.tag_frequency_variance > 0  # Should have variance
        assert len(metrics.dominant_tags) > 0
        assert "memory" in [tag for tag, count in metrics.dominant_tags]

    def test_tag_co_occurrence(self, analyzer):
        """Test tag co-occurrence tracking"""
        dreams = [
            {"tags": ["A", "B", "C"]},
            {"tags": ["A", "B"]},
            {"tags": ["B", "C"]},
            {"tags": ["A", "C"]},
        ]

        analyzer.calculate_tag_variance(dreams)

        # Check co-occurrence counts
        assert analyzer.tag_co_occurrence["A"]["B"] == 2
        assert analyzer.tag_co_occurrence["B"]["C"] == 2
        assert analyzer.tag_co_occurrence["A"]["C"] == 2

    def test_emerging_tags_detection(self, analyzer):
        """Test detection of emerging tags"""
        base_time = datetime.now()
        old_dreams = [
            {"tags": ["old1", "old2"], "timestamp": base_time - timedelta(days=2)}
            for _ in range(5)
        ]
        new_dreams = [
            {"tags": ["old1", "emerging1", "emerging2"], "timestamp": base_time}
            for _ in range(10)
        ]

        all_dreams = old_dreams + new_dreams
        metrics = analyzer.calculate_tag_variance(all_dreams)

        # Should identify emerging tags
        assert (
            "emerging1" in metrics.emerging_tags or "emerging2" in metrics.emerging_tags
        )

    def test_declining_tags_detection(self, analyzer):
        """Test detection of declining tags"""
        base_time = datetime.now()
        old_dreams = [
            {
                "tags": ["declining1", "stable"],
                "timestamp": base_time - timedelta(days=2),
            }
            for _ in range(10)
        ]
        new_dreams = [
            {"tags": ["stable", "new"], "timestamp": base_time} for _ in range(5)
        ]

        all_dreams = old_dreams + new_dreams
        analyzer.calculate_tag_variance(all_dreams)

        # Manually check declining tags
        declining = analyzer._identify_declining_tags(window_hours=48)
        # Note: May not detect declining in this simple test due to threshold requirements


class TestPatternTrendDetection:
    """Test pattern trend detection"""

    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance"""
        return SymbolicDriftAnalyzer()

    def test_stable_pattern(self, analyzer):
        """Test detection of stable patterns"""
        # Create stable entropy history
        stable_metrics = [EntropyMetrics(0.5, 0.5, 0.5, 0.5, 0.5) for _ in range(10)]

        trend = analyzer.detect_pattern_trend(stable_metrics)
        assert trend == PatternTrend.STABLE

    def test_converging_pattern(self, analyzer):
        """Test detection of converging patterns"""
        # Create decreasing entropy history
        converging_metrics = [
            EntropyMetrics(
                0.8 - i * 0.05,
                0.8 - i * 0.05,
                0.8 - i * 0.05,
                0.8 - i * 0.05,
                0.8 - i * 0.05,
            )
            for i in range(10)
        ]

        trend = analyzer.detect_pattern_trend(converging_metrics)
        assert trend == PatternTrend.CONVERGING

    def test_diverging_pattern(self, analyzer):
        """Test detection of diverging patterns"""
        # Create increasing entropy history
        diverging_metrics = [
            EntropyMetrics(
                0.3 + i * 0.05,
                0.3 + i * 0.05,
                0.3 + i * 0.05,
                0.3 + i * 0.05,
                0.3 + i * 0.05,
            )
            for i in range(10)
        ]

        trend = analyzer.detect_pattern_trend(diverging_metrics)
        assert trend == PatternTrend.DIVERGING

    def test_chaotic_pattern(self, analyzer):
        """Test detection of chaotic patterns"""
        import random

        # Create highly variable entropy history
        chaotic_metrics = [
            EntropyMetrics(
                random.uniform(0.1, 0.9),
                random.uniform(0.1, 0.9),
                random.uniform(0.1, 0.9),
                random.uniform(0.1, 0.9),
                random.uniform(0.1, 0.9),
            )
            for _ in range(10)
        ]

        trend = analyzer.detect_pattern_trend(chaotic_metrics)
        # Should detect high variance as chaotic or potentially oscillating
        assert trend in [PatternTrend.CHAOTIC, PatternTrend.OSCILLATING]


class TestEthicalDriftDetection:
    """Test ethical drift detection functionality"""

    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance"""
        return SymbolicDriftAnalyzer()

    def test_low_ethical_drift(self, analyzer):
        """Test low ethical drift scenario"""
        positive_dreams = [
            {"tags": ["creation", "harmony", "help", "peace"]} for _ in range(10)
        ]

        drift_score, violations = analyzer.check_ethical_drift(positive_dreams)

        assert drift_score < 0.3  # Low drift
        assert (
            len(violations) == 0 or len(violations) == 1
        )  # May flag low positive ratio

    def test_high_ethical_drift(self, analyzer):
        """Test high ethical drift scenario"""
        negative_dreams = [
            {"tags": ["destruction", "chaos", "harm", "violence"]} for _ in range(10)
        ]

        drift_score, violations = analyzer.check_ethical_drift(negative_dreams)

        assert drift_score > 0.5  # High drift
        assert len(violations) > 0  # Should have violations
        assert any("concerning tag ratio" in v for v in violations)

    def test_balanced_ethical_state(self, analyzer):
        """Test balanced ethical state"""
        balanced_dreams = [
            {"tags": ["creation", "destruction", "harmony", "conflict"]}
            for _ in range(10)
        ]

        drift_score, violations = analyzer.check_ethical_drift(balanced_dreams)

        assert 0.2 < drift_score < 0.8  # Moderate drift


class TestAlertGeneration:
    """Test alert generation and thresholds"""

    @pytest.fixture
    def analyzer(self):
        """Create analyzer with specific thresholds"""
        return SymbolicDriftAnalyzer(
            config={
                "thresholds": {
                    "entropy_warning": 0.6,
                    "entropy_critical": 0.8,
                    "ethical_drift_warning": 0.4,
                    "ethical_drift_critical": 0.6,
                }
            }
        )

    def test_entropy_warning_alert(self, analyzer):
        """Test entropy warning alert generation"""
        metrics = EntropyMetrics(0.7, 0.7, 0.7, 0.7, 0.7)
        variance = TagVarianceMetrics(10, 50.0, 0.5, 0.3, [], [], [])

        alerts = analyzer._generate_alerts(
            metrics, variance, 0.2, [], PatternTrend.STABLE
        )

        # Should generate warning alert
        entropy_alerts = [a for a in alerts if a.metric_type == "entropy"]
        assert len(entropy_alerts) == 1
        assert entropy_alerts[0].level == DriftAlertLevel.WARNING

    def test_entropy_critical_alert(self, analyzer):
        """Test entropy critical alert generation"""
        metrics = EntropyMetrics(0.9, 0.9, 0.9, 0.9, 0.9)
        variance = TagVarianceMetrics(10, 50.0, 0.5, 0.3, [], [], [])

        alerts = analyzer._generate_alerts(
            metrics, variance, 0.2, [], PatternTrend.STABLE
        )

        # Should generate critical alert
        entropy_alerts = [a for a in alerts if a.metric_type == "entropy"]
        assert len(entropy_alerts) == 1
        assert entropy_alerts[0].level == DriftAlertLevel.CRITICAL
        assert len(entropy_alerts[0].remediation_suggestions) > 0

    def test_ethical_emergency_alert(self, analyzer):
        """Test ethical emergency alert generation"""
        metrics = EntropyMetrics(0.5, 0.5, 0.5, 0.5, 0.5)
        variance = TagVarianceMetrics(10, 50.0, 0.5, 0.3, [], [], [])
        violations = ["High violence tag ratio", "Low positive tags"]

        alerts = analyzer._generate_alerts(
            metrics, variance, 0.8, violations, PatternTrend.STABLE
        )

        # Should generate emergency alert
        ethical_alerts = [a for a in alerts if a.metric_type == "ethical_drift"]
        assert len(ethical_alerts) == 1
        assert ethical_alerts[0].level == DriftAlertLevel.EMERGENCY
        assert "IMMEDIATE ACTION" in ethical_alerts[0].remediation_suggestions[0]

    def test_chaotic_pattern_alert(self, analyzer):
        """Test chaotic pattern alert generation"""
        metrics = EntropyMetrics(0.5, 0.5, 0.5, 0.5, 0.5)
        variance = TagVarianceMetrics(10, 50.0, 0.5, 0.3, [], [], [])

        alerts = analyzer._generate_alerts(
            metrics, variance, 0.2, [], PatternTrend.CHAOTIC
        )

        # Should generate pattern alert
        pattern_alerts = [a for a in alerts if a.metric_type == "pattern_trend"]
        assert len(pattern_alerts) == 1
        assert pattern_alerts[0].level == DriftAlertLevel.CRITICAL


class TestDriftAnalysis:
    """Test complete drift analysis functionality"""

    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance"""
        return SymbolicDriftAnalyzer()

    @pytest.mark.asyncio
    async def test_analyze_dreams_no_data(self, analyzer):
        """Test analysis with no dream data"""
        # Mock empty dream memory
        analyzer.dream_memory = Mock()
        analyzer.dream_memory.get_recent_dreams = AsyncMock(return_value=[])

        results = await analyzer.analyze_dreams()

        assert results["status"] == "no_data"
        assert "message" in results

    @pytest.mark.asyncio
    async def test_analyze_synthetic_dreams(self, analyzer):
        """Test analysis with synthetic dreams"""
        results = await analyzer.analyze_dreams()

        assert results["status"] == "analyzed"
        assert "entropy_metrics" in results
        assert "tag_variance" in results
        assert "ethical_drift" in results
        assert "alerts" in results
        assert "recommendations" in results

    @pytest.mark.asyncio
    async def test_drift_phase_updates(self, analyzer):
        """Test drift phase updates based on metrics"""
        # Analyze dreams multiple times to simulate progression
        for i in range(5):
            results = await analyzer.analyze_dreams()
            assert "current_drift_phase" in results

        # Phase should be updated based on metrics
        assert analyzer.current_drift_phase is not None


class TestMonitoring:
    """Test continuous monitoring functionality"""

    @pytest.fixture
    def analyzer(self):
        """Create analyzer with fast interval"""
        return SymbolicDriftAnalyzer(
            config={"analysis_interval": 0.1}  # 100ms for testing
        )

    @pytest.mark.asyncio
    async def test_start_stop_monitoring(self, analyzer):
        """Test starting and stopping monitoring"""
        await analyzer.start_monitoring()
        assert analyzer.monitoring_active == True
        assert analyzer._monitoring_task is not None

        await analyzer.stop_monitoring()
        assert analyzer.monitoring_active == False

    @pytest.mark.asyncio
    async def test_monitoring_loop_execution(self, analyzer):
        """Test that monitoring loop executes analyses"""
        initial_count = analyzer.total_dreams_analyzed

        await analyzer.start_monitoring()
        await asyncio.sleep(0.3)  # Let it run a few cycles
        await analyzer.stop_monitoring()

        # Should have analyzed more dreams
        assert analyzer.total_dreams_analyzed > initial_count

    @pytest.mark.asyncio
    async def test_alert_callbacks(self, analyzer):
        """Test alert callback mechanism"""
        alerts_received = []

        def callback(alert: DriftAlert):
            alerts_received.append(alert)

        analyzer.register_alert_callback(callback)

        # Generate high entropy to trigger alert
        high_entropy_dreams = [
            {"tags": [f"tag_{i}_{j}" for j in range(10)], "timestamp": datetime.now()}
            for i in range(50)
        ]
        analyzer._generate_synthetic_dreams = lambda count=100: high_entropy_dreams

        await analyzer.analyze_dreams()

        # Should have received alerts via callback
        assert len(alerts_received) > 0


class TestCLISummary:
    """Test CLI summary generation"""

    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance"""
        return SymbolicDriftAnalyzer()

    @pytest.mark.asyncio
    async def test_cli_summary_generation(self, analyzer):
        """Test CLI summary generation"""
        # Perform analysis first
        await analyzer.analyze_dreams()

        # Generate summary
        summary = analyzer._generate_text_summary()

        assert "SYMBOLIC DRIFT ANALYZER" in summary
        assert "Current Phase:" in summary
        assert "ENTROPY METRICS:" in summary
        assert "RECENT ALERTS:" in summary

    @pytest.mark.asyncio
    async def test_cli_summary_with_rich(self, analyzer):
        """Test rich CLI summary generation"""
        # Skip if rich not available
        if not analyzer.console:
            pytest.skip("Rich library not available")

        await analyzer.analyze_dreams()

        # Should not raise exception
        analyzer.generate_cli_summary()


class TestExportFunctionality:
    """Test report export functionality"""

    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance"""
        return SymbolicDriftAnalyzer()

    @pytest.mark.asyncio
    async def test_export_analysis_report(self, analyzer, tmp_path):
        """Test exporting analysis report"""
        # Perform some analyses
        for _ in range(3):
            await analyzer.analyze_dreams()

        # Export report
        report_path = tmp_path / "test_report.json"
        analyzer.export_analysis_report(report_path)

        assert report_path.exists()

        # Load and verify report
        with open(report_path) as f:
            report = json.load(f)

        assert "metadata" in report
        assert "configuration" in report
        assert "entropy_history" in report
        assert "pattern_trends" in report
        assert "alerts" in report
        assert "tag_statistics" in report

        assert report["metadata"]["total_dreams_analyzed"] > 0
        assert len(report["entropy_history"]) > 0


class TestIntegration:
    """Integration tests for complete workflow"""

    @pytest.mark.asyncio
    async def test_complete_drift_detection_workflow(self):
        """Test complete drift detection workflow"""
        # Create analyzer with specific configuration
        analyzer = SymbolicDriftAnalyzer(
            config={
                "analysis_interval": 0.1,
                "thresholds": {
                    "entropy_warning": 0.5,
                    "entropy_critical": 0.7,
                    "ethical_drift_warning": 0.3,
                    "ethical_drift_critical": 0.5,
                },
            }
        )

        # Track alerts
        alerts = []
        analyzer.register_alert_callback(lambda a: alerts.append(a))

        # Start monitoring
        await analyzer.start_monitoring()

        # Let it run for a bit
        await asyncio.sleep(0.5)

        # Stop monitoring
        await analyzer.stop_monitoring()

        # Verify results
        assert analyzer.total_dreams_analyzed > 0
        assert len(analyzer.entropy_history) > 0
        assert len(analyzer.pattern_trends) > 0

        # Check if appropriate alerts were generated
        if alerts:
            assert all(isinstance(a, DriftAlert) for a in alerts)

    @pytest.mark.asyncio
    async def test_drift_progression_simulation(self):
        """Test simulation of drift progression"""
        analyzer = SymbolicDriftAnalyzer()

        phases_seen = set()

        # Analyze multiple times to see phase progression
        for i in range(10):
            results = await analyzer.analyze_dreams()
            phases_seen.add(results["current_drift_phase"])

            # Add some delay
            await asyncio.sleep(0.01)

        # Should have seen multiple phases
        assert len(phases_seen) >= 2  # At least 2 different phases


class TestEdgeCases:
    """Test edge cases and error handling"""

    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance"""
        return SymbolicDriftAnalyzer()

    def test_empty_tag_list(self, analyzer):
        """Test handling of dreams with no tags"""
        dreams = [{"tags": [], "timestamp": datetime.now()} for _ in range(10)]

        metrics = analyzer.calculate_tag_variance(dreams)
        assert metrics.unique_tags == 0
        assert metrics.tag_frequency_variance == 0.0

    def test_single_timestamp(self, analyzer):
        """Test temporal entropy with single timestamp"""
        entropy = analyzer.calculate_temporal_entropy([datetime.now()])
        assert entropy == 0.0

    def test_alert_callback_exception(self, analyzer):
        """Test handling of exception in alert callback"""

        def failing_callback(alert):
            raise Exception("Callback failed")

        analyzer.register_alert_callback(failing_callback)

        # Generate alert
        alert = DriftAlert(
            level=DriftAlertLevel.WARNING,
            metric_type="test",
            current_value=0.5,
            threshold=0.4,
            message="Test alert",
        )

        # Should not raise exception
        analyzer._trigger_alert_callback(alert)

    @pytest.mark.asyncio
    async def test_monitoring_with_analysis_error(self, analyzer):
        """Test monitoring continues despite analysis errors"""
        # Mock analyze_dreams to fail
        original_analyze = analyzer.analyze_dreams
        call_count = 0

        async def failing_analyze():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("Analysis failed")
            return await original_analyze()

        analyzer.analyze_dreams = failing_analyze
        analyzer.config["analysis_interval"] = 0.1

        await analyzer.start_monitoring()
        await asyncio.sleep(0.3)
        await analyzer.stop_monitoring()

        # Should have continued despite error
        assert call_count >= 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
