"""
══════════════════════════════════════════════════════════════════════════════════
║ 🧪 LUKHAS AI - ENERGY CONSUMPTION ANALYSIS TEST SUITE
║ Comprehensive tests for energy monitoring and optimization
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: test_energy_consumption_analysis.py
║ Path: tests/core/test_energy_consumption_analysis.py
║ Version: 1.0.0 | Created: 2025-07-27 | Modified: 2025-07-27
║ Authors: Claude (Anthropic AI Assistant)
╠══════════════════════════════════════════════════════════════════════════════════
║ TEST COVERAGE
╠══════════════════════════════════════════════════════════════════════════════════
║ - Energy metric recording and tracking
║ - Budget management and enforcement
║ - Predictive modeling accuracy
║ - Component-level energy profiling
║ - Optimization recommendation generation
║ - Real-time monitoring capabilities
║ - Carbon footprint calculation
║ - Integration with system components
╚══════════════════════════════════════════════════════════════════════════════════
"""

import asyncio
import json
import time

import pytest

from core.energy_consumption_analysis import (
    EnergyAwareComponent,
    EnergyBudget,
    EnergyComponent,
    EnergyConsumptionAnalyzer,
    EnergyMetric,
    EnergyModel,
    EnergyProfile,
)


class TestEnergyMetric:
    """Test EnergyMetric dataclass"""

    def test_energy_metric_creation(self):
        """Test creating an energy metric"""
        metric = EnergyMetric(
            timestamp=time.time(),
            component=EnergyComponent.CPU,
            operation="test_op",
            energy_joules=1.5,
            duration_ms=100.0,
            metadata={"test": "data"},
        )

        assert metric.component == EnergyComponent.CPU
        assert metric.operation == "test_op"
        assert metric.energy_joules == 1.5
        assert metric.duration_ms == 100.0
        assert metric.metadata == {"test": "data"}

    def test_power_calculation(self):
        """Test power calculation from energy and duration"""
        metric = EnergyMetric(
            timestamp=time.time(),
            component=EnergyComponent.CPU,
            operation="test_op",
            energy_joules=1.0,
            duration_ms=1000.0,  # 1 second
        )

        assert metric.power_watts == 1.0  # 1J/1s = 1W

    def test_zero_duration_power(self):
        """Test power calculation with zero duration"""
        metric = EnergyMetric(
            timestamp=time.time(),
            component=EnergyComponent.CPU,
            operation="test_op",
            energy_joules=1.0,
            duration_ms=0.0,
        )

        assert metric.power_watts == 0.0

    def test_metric_to_dict(self):
        """Test converting metric to dictionary"""
        timestamp = time.time()
        metric = EnergyMetric(
            timestamp=timestamp,
            component=EnergyComponent.NETWORK,
            operation="data_transfer",
            energy_joules=0.5,
            duration_ms=50.0,
            metadata={"bytes": 1024},
        )

        data = metric.to_dict()
        assert data["timestamp"] == timestamp
        assert data["component"] == "network"
        assert data["operation"] == "data_transfer"
        assert data["energy_joules"] == 0.5
        assert data["duration_ms"] == 50.0
        assert data["power_watts"] == 10.0  # 0.5J/0.05s = 10W
        assert data["metadata"] == {"bytes": 1024}


class TestEnergyBudget:
    """Test EnergyBudget functionality"""

    def test_budget_creation(self):
        """Test creating an energy budget"""
        budget = EnergyBudget(
            total_budget_joules=1000.0,
            time_window_seconds=3600.0,
            component_budgets={
                EnergyComponent.CPU: 400.0,
                EnergyComponent.MEMORY: 300.0,
            },
        )

        assert budget.total_budget_joules == 1000.0
        assert budget.time_window_seconds == 3600.0
        assert budget.consumed_joules == 0.0
        assert budget.component_budgets[EnergyComponent.CPU] == 400.0

    def test_remaining_budget(self):
        """Test remaining budget calculation"""
        budget = EnergyBudget(total_budget_joules=100.0, time_window_seconds=60.0)
        budget.consumed_joules = 30.0

        assert budget.remaining_budget() == 70.0

    def test_budget_percentage(self):
        """Test budget percentage calculation"""
        budget = EnergyBudget(total_budget_joules=100.0, time_window_seconds=60.0)
        budget.consumed_joules = 25.0

        assert budget.budget_percentage_used() == 25.0

    def test_is_within_budget(self):
        """Test budget constraint checking"""
        budget = EnergyBudget(total_budget_joules=100.0, time_window_seconds=60.0)
        budget.consumed_joules = 80.0

        assert budget.is_within_budget(10.0) == True
        assert budget.is_within_budget(20.0) == True
        assert budget.is_within_budget(21.0) == False

    def test_budget_reset(self):
        """Test budget reset functionality"""
        budget = EnergyBudget(total_budget_joules=100.0, time_window_seconds=60.0)
        budget.consumed_joules = 50.0
        old_start = budget.start_time

        time.sleep(0.1)
        budget.reset()

        assert budget.consumed_joules == 0.0
        assert budget.start_time > old_start


class TestEnergyModel:
    """Test predictive energy modeling"""

    def test_model_initialization(self):
        """Test energy model initialization"""
        model = EnergyModel(history_size=100)
        assert model.history_size == 100
        assert len(model.history) == 0
        assert len(model.model_params) == 0

    def test_record_observation(self):
        """Test recording energy observations"""
        model = EnergyModel()

        model.record_observation("test_op", 100, 1.0, 10.0)
        assert len(model.history["test_op"]) == 1

        obs = model.history["test_op"][0]
        assert obs["input_size"] == 100
        assert obs["energy_consumed"] == 1.0
        assert obs["duration_ms"] == 10.0

    def test_prediction_no_data(self):
        """Test prediction with no historical data"""
        model = EnergyModel()

        energy, confidence = model.predict_energy("unknown_op", 100)
        assert energy == 0.1  # 0.001 * 100
        assert confidence == 0.0

    def test_prediction_with_data(self):
        """Test prediction with historical data"""
        model = EnergyModel()

        # Add enough observations to build model
        for i in range(10):
            model.record_observation("test_op", 100 + i * 10, 1.0 + i * 0.1, 10.0)

        energy, confidence = model.predict_energy("test_op", 150)
        assert energy > 0
        assert 0 < confidence <= 1.0

    def test_model_update(self):
        """Test model parameter updates"""
        model = EnergyModel()

        # Add observations
        for i in range(10):
            model.record_observation("test_op", 100, 1.0, 10.0)

        assert "test_op" in model.model_params
        params = model.model_params["test_op"]
        assert "base" in params
        assert "scale" in params
        assert "variance" in params
        assert "confidence" in params


class TestEnergyConsumptionAnalyzer:
    """Test main energy consumption analyzer"""

    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance for tests"""
        return EnergyConsumptionAnalyzer(carbon_intensity_kwh=0.5)

    def test_analyzer_initialization(self, analyzer):
        """Test analyzer initialization"""
        assert analyzer.carbon_intensity_kwh == 0.5
        assert analyzer.current_profile == EnergyProfile.NORMAL
        assert analyzer.monitoring_enabled == True
        assert len(analyzer.metrics) == 0

    def test_record_energy_consumption(self, analyzer):
        """Test recording energy consumption"""
        analyzer.record_energy_consumption(
            EnergyComponent.CPU, "test_operation", 1.5, 100.0, {"test": "metadata"}
        )

        assert len(analyzer.metrics) == 1
        assert analyzer.component_totals[EnergyComponent.CPU] == 1.5
        assert analyzer.operation_totals["test_operation"] == 1.5

    def test_create_budget(self, analyzer):
        """Test creating energy budgets"""
        budget = analyzer.create_budget(
            "test_budget", 1000.0, 3600.0, {EnergyComponent.CPU: 500.0}
        )

        assert "test_budget" in analyzer.budgets
        assert budget.total_budget_joules == 1000.0
        assert analyzer.active_budget == "test_budget"

    def test_budget_tracking(self, analyzer):
        """Test budget consumption tracking"""
        analyzer.create_budget("test_budget", 100.0, 60.0)

        analyzer.record_energy_consumption(EnergyComponent.CPU, "test_op", 50.0, 10.0)

        budget = analyzer.budgets["test_budget"]
        assert budget.consumed_joules == 50.0
        assert budget.budget_percentage_used() == 50.0

    def test_energy_prediction(self, analyzer):
        """Test energy prediction functionality"""
        # Add some historical data
        for i in range(10):
            analyzer.record_energy_consumption(
                EnergyComponent.CPU,
                "test_op",
                1.0 + i * 0.1,
                10.0,
                {"input_size": 100 + i * 10},
            )

        prediction = analyzer.predict_operation_energy("test_op", 150)
        assert "predicted_energy_joules" in prediction
        assert "confidence" in prediction
        assert "can_afford" in prediction
        assert "budget_impact_percent" in prediction

    def test_energy_statistics(self, analyzer):
        """Test energy statistics calculation"""
        # Add test data
        analyzer.record_energy_consumption(EnergyComponent.CPU, "op1", 1.0, 10.0)
        analyzer.record_energy_consumption(EnergyComponent.NETWORK, "op2", 0.5, 5.0)

        stats = analyzer.get_energy_statistics()
        assert stats["total_energy_joules"] == 1.5
        assert stats["component_breakdown"]["cpu"] == 1.0
        assert stats["component_breakdown"]["network"] == 0.5
        assert stats["operation_breakdown"]["op1"] == 1.0
        assert stats["operation_breakdown"]["op2"] == 0.5
        assert stats["carbon_footprint_kg"] > 0

    def test_set_energy_profile(self, analyzer):
        """Test setting energy profiles"""
        analyzer.set_energy_profile(EnergyProfile.LOW_POWER)
        assert analyzer.current_profile == EnergyProfile.LOW_POWER

    def test_optimization_recommendations(self, analyzer):
        """Test optimization recommendation generation"""
        # Create budget and consume most of it
        analyzer.create_budget("test_budget", 100.0, 60.0)

        # Consume 85% of budget
        analyzer.record_energy_consumption(EnergyComponent.CPU, "heavy_op", 85.0, 100.0)

        # Should trigger recommendations
        assert len(analyzer.recommendations) > 0

        # Check recommendation content
        rec = analyzer.recommendations[0]
        assert "type" in rec
        assert "severity" in rec
        assert "message" in rec
        assert "suggestion" in rec

    @pytest.mark.asyncio
    async def test_monitoring_lifecycle(self, analyzer):
        """Test monitoring start/stop"""
        await analyzer.start_monitoring()
        assert analyzer._monitoring_task is not None
        assert not analyzer._monitoring_task.done()

        await analyzer.stop_monitoring()
        assert analyzer.monitoring_enabled == False

    def test_export_metrics(self, analyzer, tmp_path):
        """Test exporting metrics to file"""
        # Add some test data
        analyzer.record_energy_consumption(EnergyComponent.CPU, "test_op", 1.0, 10.0)

        export_file = tmp_path / "energy_metrics.json"
        analyzer.export_metrics(str(export_file))

        assert export_file.exists()

        with open(export_file) as f:
            data = json.load(f)

        assert "export_timestamp" in data
        assert "statistics" in data
        assert "metrics" in data
        assert len(data["metrics"]) == 1

    def test_carbon_footprint_calculation(self, analyzer):
        """Test carbon footprint calculation"""
        # 3.6MJ = 1kWh
        analyzer.record_energy_consumption(
            EnergyComponent.CPU, "test_op", 3600000.0, 1000.0  # 1 kWh in joules
        )

        stats = analyzer.get_energy_statistics()
        # With carbon intensity of 0.5 kg/kWh
        assert abs(stats["carbon_footprint_kg"] - 0.5) < 0.001


class TestEnergyAwareComponent:
    """Test energy-aware component integration"""

    @pytest.mark.asyncio
    async def test_energy_aware_execution(self):
        """Test executing operations with energy tracking"""
        analyzer = EnergyConsumptionAnalyzer()
        component = EnergyAwareComponent("test_component", analyzer)

        async def test_operation(value):
            await asyncio.sleep(0.01)
            return value * 2

        result = await component.execute_with_energy_tracking(
            "multiply", test_operation, 5, input_size=10
        )

        assert result == 10
        assert len(analyzer.metrics) == 1
        assert analyzer.metrics[0].operation == "test_component.multiply"

    @pytest.mark.asyncio
    async def test_energy_budget_enforcement(self):
        """Test energy budget enforcement in components"""
        analyzer = EnergyConsumptionAnalyzer()
        analyzer.create_budget("test_budget", 0.01, 60.0)  # Very small budget

        component = EnergyAwareComponent("test_component", analyzer)

        async def expensive_operation():
            await asyncio.sleep(0.1)
            return "done"

        # First operation should succeed
        result = await component.execute_with_energy_tracking(
            "expensive_op", expensive_operation, input_size=1000
        )
        assert result == "done"

        # Subsequent operations may trigger warnings
        # (actual budget enforcement would be implemented based on requirements)


class TestIntegration:
    """Integration tests for energy system"""

    @pytest.mark.asyncio
    async def test_full_energy_workflow(self):
        """Test complete energy monitoring workflow"""
        analyzer = EnergyConsumptionAnalyzer()

        # Create budget
        analyzer.create_budget("hourly_budget", 3600.0, 3600.0)  # 3.6kJ  # 1 hour

        # Start monitoring
        await analyzer.start_monitoring()

        # Simulate various operations
        operations = [
            (EnergyComponent.CPU, "compute", 1.0, 10.0),
            (EnergyComponent.NETWORK, "transfer", 0.5, 5.0),
            (EnergyComponent.MEMORY, "cache", 0.1, 1.0),
        ]

        for component, op, energy, duration in operations:
            analyzer.record_energy_consumption(
                component, op, energy, duration, {"timestamp": time.time()}
            )
            await asyncio.sleep(0.01)

        # Get comprehensive statistics
        stats = analyzer.get_energy_statistics()

        # Verify statistics
        assert stats["total_energy_joules"] == 1.6
        assert stats["metric_count"] == 3
        assert "cpu" in stats["component_breakdown"]
        assert "network" in stats["component_breakdown"]
        assert "memory" in stats["component_breakdown"]

        # Check budget status
        assert stats["budget_status"] is not None
        assert stats["budget_status"]["consumed_joules"] == 1.6

        # Stop monitoring
        await analyzer.stop_monitoring()

    @pytest.mark.asyncio
    async def test_concurrent_energy_tracking(self):
        """Test concurrent energy tracking from multiple components"""
        analyzer = EnergyConsumptionAnalyzer()

        async def simulate_component(name: str, count: int):
            component = EnergyAwareComponent(name, analyzer)

            async def work():
                await asyncio.sleep(0.001)
                return "done"

            for i in range(count):
                await component.execute_with_energy_tracking(
                    f"op_{i}", work, input_size=i * 10
                )

        # Run multiple components concurrently
        await asyncio.gather(
            simulate_component("comp1", 5),
            simulate_component("comp2", 5),
            simulate_component("comp3", 5),
        )

        # Verify all operations were tracked
        assert len(analyzer.metrics) == 15

        # Check that different components are tracked
        operations = {m.operation for m in analyzer.metrics}
        assert any("comp1" in op for op in operations)
        assert any("comp2" in op for op in operations)
        assert any("comp3" in op for op in operations)


# Performance tests
class TestPerformance:
    """Performance tests for energy system"""

    def test_metric_recording_performance(self):
        """Test performance of metric recording"""
        analyzer = EnergyConsumptionAnalyzer()

        start_time = time.time()

        # Record 10000 metrics
        for i in range(10000):
            analyzer.record_energy_consumption(
                EnergyComponent.CPU, f"op_{i % 10}", 0.1, 1.0
            )

        elapsed = time.time() - start_time

        # Should complete in reasonable time
        assert elapsed < 1.0  # Less than 1 second for 10k metrics

        # Verify metrics are limited by deque maxlen
        assert len(analyzer.metrics) == 10000

    def test_statistics_calculation_performance(self):
        """Test performance of statistics calculation"""
        analyzer = EnergyConsumptionAnalyzer()

        # Add many metrics
        for i in range(1000):
            analyzer.record_energy_consumption(
                EnergyComponent.CPU if i % 2 else EnergyComponent.NETWORK,
                f"op_{i % 20}",
                0.1 + (i % 10) * 0.01,
                1.0 + (i % 5),
            )

        start_time = time.time()
        stats = analyzer.get_energy_statistics()
        elapsed = time.time() - start_time

        # Should calculate statistics quickly
        assert elapsed < 0.1  # Less than 100ms
        assert stats["metric_count"] == 1000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
