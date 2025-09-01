"""
══════════════════════════════════════════════════════════════════════════════════
║ 🔋 LUKHAS AI - ENERGY CONSUMPTION ANALYSIS MODULE
║ Advanced energy monitoring and optimization for distributed AI systems
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: energy_consumption_analysis.py
║ Path: lukhas/core/energy_consumption_analysis.py
║ Version: 1.0.0 | Created: 2025-07-27 | Modified: 2025-07-27
║ Authors: Claude (Anthropic AI Assistant)
╠══════════════════════════════════════════════════════════════════════════════════
║ DESCRIPTION
╠══════════════════════════════════════════════════════════════════════════════════
║ Implements TODO 139: Energy Consumption Analysis
║
║ This module provides comprehensive energy monitoring, analysis, and optimization
║ capabilities for the Symbiotic Swarm architecture. It tracks energy consumption
║ across communication, computation, and memory operations, providing real-time
║ insights and optimization recommendations.
║
║ Key Features:
║ - Real-time energy consumption tracking
║ - Component-level energy profiling
║ - Predictive energy modeling
║ - Optimization recommendations
║ - Energy budget management
║ - Carbon footprint estimation
╚══════════════════════════════════════════════════════════════════════════════════
"""

import asyncio
import json
import logging
import math
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional

# Try to import optional dependencies
try:
    import numpy as np

    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

try:
    import psutil

    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

logger = logging.getLogger(__name__)


class EnergyComponent(Enum):
    """System components that consume energy"""

    CPU = "cpu"
    MEMORY = "memory"
    NETWORK = "network"
    STORAGE = "storage"
    GPU = "gpu"
    COMMUNICATION = "communication"
    COMPUTATION = "computation"
    ORCHESTRATION = "orchestration"


class EnergyProfile(Enum):
    """Energy consumption profiles for different operation types"""

    IDLE = "idle"
    LOW_POWER = "low_power"
    NORMAL = "normal"
    HIGH_PERFORMANCE = "high_performance"
    BURST = "burst"


@dataclass
class EnergyMetric:
    """Individual energy consumption metric"""

    timestamp: float
    component: EnergyComponent
    operation: str
    energy_joules: float
    duration_ms: float
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def power_watts(self) -> float:
        """Calculate power consumption in watts"""
        if self.duration_ms > 0:
            return (self.energy_joules / self.duration_ms) * 1000
        return 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "component": self.component.value,
            "operation": self.operation,
            "energy_joules": self.energy_joules,
            "duration_ms": self.duration_ms,
            "power_watts": self.power_watts,
            "metadata": self.metadata,
        }


@dataclass
class EnergyBudget:
    """Energy budget constraints and tracking"""

    total_budget_joules: float
    time_window_seconds: float
    component_budgets: dict[EnergyComponent, float] = field(default_factory=dict)
    consumed_joules: float = 0.0
    start_time: float = field(default_factory=time.time)

    def remaining_budget(self) -> float:
        """Calculate remaining energy budget"""
        return self.total_budget_joules - self.consumed_joules

    def budget_percentage_used(self) -> float:
        """Calculate percentage of budget consumed"""
        if self.total_budget_joules > 0:
            return (self.consumed_joules / self.total_budget_joules) * 100
        return 0.0

    def time_elapsed(self) -> float:
        """Time elapsed since budget start"""
        return time.time() - self.start_time

    def is_within_budget(self, additional_joules: float = 0) -> bool:
        """Check if consumption is within budget"""
        return (self.consumed_joules + additional_joules) <= self.total_budget_joules

    def reset(self):
        """Reset budget tracking"""
        self.consumed_joules = 0.0
        self.start_time = time.time()


class EnergyModel:
    """
    Predictive energy model for estimating consumption
    Uses historical data to predict future energy requirements
    """

    def __init__(self, history_size: int = 1000):
        self.history_size = history_size
        self.history: dict[str, deque] = defaultdict(lambda: deque(maxlen=history_size))
        self.model_params: dict[str, dict[str, float]] = {}
        self._lock = threading.Lock()

    def record_observation(
        self,
        operation: str,
        input_size: int,
        energy_consumed: float,
        duration_ms: float,
    ):
        """Record an energy consumption observation"""
        with self._lock:
            self.history[operation].append(
                {
                    "input_size": input_size,
                    "energy_consumed": energy_consumed,
                    "duration_ms": duration_ms,
                    "timestamp": time.time(),
                }
            )

            # Update model parameters
            self._update_model(operation)

    def predict_energy(self, operation: str, input_size: int) -> tuple[float, float]:
        """
        Predict energy consumption for an operation
        Returns: (predicted_energy_joules, confidence_score)
        """
        with self._lock:
            if operation not in self.model_params:
                # No historical data, return conservative estimate
                base_energy = 0.001 * input_size  # 1mJ per unit
                return base_energy, 0.0

            params = self.model_params[operation]

            # Simple linear model: energy = base + scale * input_size
            predicted_energy = params["base"] + params["scale"] * input_size

            # Add uncertainty based on variance
            if params["variance"] > 0:
                uncertainty = math.sqrt(params["variance"])
                predicted_energy += uncertainty * 0.1  # Conservative estimate

            confidence = min(params["confidence"], 1.0)
            return predicted_energy, confidence

    def _update_model(self, operation: str):
        """Update model parameters based on historical data"""
        if len(self.history[operation]) < 5:
            return  # Not enough data

        data = list(self.history[operation])

        if HAS_NUMPY:
            # Use numpy for efficient computation
            sizes = np.array([d["input_size"] for d in data])
            energies = np.array([d["energy_consumed"] for d in data])

            # Fit linear model
            A = np.vstack([sizes, np.ones(len(sizes))]).T
            scale, base = np.linalg.lstsq(A, energies, rcond=None)[0]

            # Calculate variance
            predictions = base + scale * sizes
            residuals = energies - predictions
            variance = np.var(residuals)

            # Confidence based on data points and variance
            confidence = min(len(data) / 100.0, 1.0) * (1.0 / (1.0 + variance))
        else:
            # Simple average-based model without numpy
            avg_size = sum(d["input_size"] for d in data) / len(data)
            avg_energy = sum(d["energy_consumed"] for d in data) / len(data)

            # Estimate scale factor
            scale = avg_energy / avg_size if avg_size > 0 else 0.001

            base = avg_energy * 0.1  # Assume 10% base overhead
            variance = 0.1  # Default variance
            confidence = min(len(data) / 100.0, 0.8)

        self.model_params[operation] = {
            "base": base,
            "scale": scale,
            "variance": variance,
            "confidence": confidence,
            "last_updated": time.time(),
        }


class EnergyConsumptionAnalyzer:
    """
    Main energy consumption analysis system
    Provides comprehensive energy monitoring and optimization
    """

    def __init__(self, carbon_intensity_kwh: float = 0.5):
        """
        Initialize analyzer
        carbon_intensity_kwh: kg CO2 per kWh (default: global average)
        """
        self.metrics: deque = deque(maxlen=10000)
        self.component_totals: dict[EnergyComponent, float] = defaultdict(float)
        self.operation_totals: dict[str, float] = defaultdict(float)
        self.current_profile = EnergyProfile.NORMAL
        self.carbon_intensity_kwh = carbon_intensity_kwh

        # Energy budget management
        self.budgets: dict[str, EnergyBudget] = {}
        self.active_budget: Optional[str] = None

        # Predictive model
        self.energy_model = EnergyModel()

        # Real-time monitoring
        self.monitoring_enabled = True
        self.monitoring_interval = 1.0  # seconds
        self._monitoring_task: Optional[asyncio.Task] = None

        # Optimization recommendations
        self.recommendations: list[dict[str, Any]] = []
        self.optimization_threshold = 0.8  # 80% budget usage triggers optimization

        # Thread safety
        self._lock = threading.Lock()

        # Component energy profiles (joules per operation)
        self.component_profiles = {
            EnergyComponent.CPU: {
                EnergyProfile.IDLE: 0.001,
                EnergyProfile.LOW_POWER: 0.01,
                EnergyProfile.NORMAL: 0.1,
                EnergyProfile.HIGH_PERFORMANCE: 0.5,
                EnergyProfile.BURST: 1.0,
            },
            EnergyComponent.MEMORY: {
                EnergyProfile.IDLE: 0.0001,
                EnergyProfile.LOW_POWER: 0.001,
                EnergyProfile.NORMAL: 0.01,
                EnergyProfile.HIGH_PERFORMANCE: 0.05,
                EnergyProfile.BURST: 0.1,
            },
            EnergyComponent.NETWORK: {
                EnergyProfile.IDLE: 0.0001,
                EnergyProfile.LOW_POWER: 0.01,
                EnergyProfile.NORMAL: 0.05,
                EnergyProfile.HIGH_PERFORMANCE: 0.2,
                EnergyProfile.BURST: 0.5,
            },
        }

    def record_energy_consumption(
        self,
        component: EnergyComponent,
        operation: str,
        energy_joules: float,
        duration_ms: float,
        metadata: dict[str, Any] = None,
    ):
        """Record an energy consumption event"""
        metric = EnergyMetric(
            timestamp=time.time(),
            component=component,
            operation=operation,
            energy_joules=energy_joules,
            duration_ms=duration_ms,
            metadata=metadata or {},
        )

        with self._lock:
            self.metrics.append(metric)
            self.component_totals[component] += energy_joules
            self.operation_totals[operation] += energy_joules

            # Update budget if active
            if self.active_budget and self.active_budget in self.budgets:
                budget = self.budgets[self.active_budget]
                budget.consumed_joules += energy_joules

                # Check budget threshold
                if budget.budget_percentage_used() >= self.optimization_threshold * 100:
                    self._generate_optimization_recommendations()

            # Update predictive model
            input_size = metadata.get("input_size", 1) if metadata else 1
            self.energy_model.record_observation(operation, input_size, energy_joules, duration_ms)

    def create_budget(
        self,
        budget_name: str,
        total_joules: float,
        time_window_seconds: float,
        component_budgets: dict[EnergyComponent, float] = None,
    ) -> EnergyBudget:
        """Create a new energy budget"""
        budget = EnergyBudget(
            total_budget_joules=total_joules,
            time_window_seconds=time_window_seconds,
            component_budgets=component_budgets or {},
        )

        with self._lock:
            self.budgets[budget_name] = budget
            if not self.active_budget:
                self.active_budget = budget_name

        logger.info(f"Created energy budget '{budget_name}' with {total_joules}J over {time_window_seconds}s")
        return budget

    def set_active_budget(self, budget_name: str):
        """Set the active energy budget"""
        with self._lock:
            if budget_name in self.budgets:
                self.active_budget = budget_name
                logger.info(f"Active budget set to '{budget_name}'")
            else:
                raise ValueError(f"Budget '{budget_name}' not found")

    def predict_operation_energy(self, operation: str, input_size: int) -> dict[str, Any]:
        """Predict energy consumption for an operation"""
        predicted_energy, confidence = self.energy_model.predict_energy(operation, input_size)

        # Check against budget
        can_afford = True
        budget_impact = 0.0

        if self.active_budget and self.active_budget in self.budgets:
            budget = self.budgets[self.active_budget]
            can_afford = budget.is_within_budget(predicted_energy)
            if budget.total_budget_joules > 0:
                budget_impact = (predicted_energy / budget.remaining_budget()) * 100

        return {
            "operation": operation,
            "input_size": input_size,
            "predicted_energy_joules": predicted_energy,
            "confidence": confidence,
            "can_afford": can_afford,
            "budget_impact_percent": budget_impact,
        }

    def get_energy_statistics(self, time_window_seconds: Optional[float] = None) -> dict[str, Any]:
        """Get comprehensive energy statistics"""
        with self._lock:
            current_time = time.time()

            # Filter metrics by time window if specified
            if time_window_seconds:
                cutoff_time = current_time - time_window_seconds
                recent_metrics = [m for m in self.metrics if m.timestamp >= cutoff_time]
            else:
                recent_metrics = list(self.metrics)

            if not recent_metrics:
                return {
                    "total_energy_joules": 0.0,
                    "average_power_watts": 0.0,
                    "component_breakdown": {},
                    "operation_breakdown": {},
                    "carbon_footprint_kg": 0.0,
                }

            # Calculate statistics
            total_energy = sum(m.energy_joules for m in recent_metrics)
            time_span = max(m.timestamp for m in recent_metrics) - min(m.timestamp for m in recent_metrics)

            avg_power = total_energy / time_span if time_span > 0 else 0.0

            # Component breakdown
            component_energy = defaultdict(float)
            for metric in recent_metrics:
                component_energy[metric.component.value] += metric.energy_joules

            # Operation breakdown
            operation_energy = defaultdict(float)
            for metric in recent_metrics:
                operation_energy[metric.operation] += metric.energy_joules

            # Carbon footprint calculation
            energy_kwh = total_energy / 3600000  # Convert joules to kWh
            carbon_kg = energy_kwh * self.carbon_intensity_kwh

            # Budget status
            budget_status = None
            if self.active_budget and self.active_budget in self.budgets:
                budget = self.budgets[self.active_budget]
                budget_status = {
                    "name": self.active_budget,
                    "total_budget_joules": budget.total_budget_joules,
                    "consumed_joules": budget.consumed_joules,
                    "remaining_joules": budget.remaining_budget(),
                    "percentage_used": budget.budget_percentage_used(),
                    "time_elapsed": budget.time_elapsed(),
                }

            return {
                "total_energy_joules": total_energy,
                "average_power_watts": avg_power,
                "peak_power_watts": (max(m.power_watts for m in recent_metrics) if recent_metrics else 0.0),
                "component_breakdown": dict(component_energy),
                "operation_breakdown": dict(operation_energy),
                "carbon_footprint_kg": carbon_kg,
                "metric_count": len(recent_metrics),
                "time_span_seconds": time_span,
                "current_profile": self.current_profile.value,
                "budget_status": budget_status,
                "recommendations": self.recommendations[-5:],  # Last 5 recommendations
            }

    def set_energy_profile(self, profile: EnergyProfile):
        """Set the current energy consumption profile"""
        with self._lock:
            self.current_profile = profile
            logger.info(f"Energy profile set to {profile.value}")

    def _generate_optimization_recommendations(self):
        """Generate energy optimization recommendations"""
        stats = self.get_energy_statistics(time_window_seconds=300)  # Last 5 minutes

        recommendations = []

        # Component-based recommendations
        component_breakdown = stats["component_breakdown"]
        if component_breakdown:
            highest_component = max(component_breakdown.items(), key=lambda x: x[1])
            if highest_component[1] > stats["total_energy_joules"] * 0.4:
                recommendations.append(
                    {
                        "type": "component_optimization",
                        "severity": "high",
                        "component": highest_component[0],
                        "message": f"{highest_component[0]} consuming {highest_component[1]:.2f}J "
                        f"({(highest_component[1] / stats['total_energy_joules'] * 100):.1f}% of total)",
                        "suggestion": f"Consider optimizing {highest_component[0]} operations or "
                        "switching to a lower power profile",
                    }
                )

        # Operation-based recommendations
        operation_breakdown = stats["operation_breakdown"]
        if operation_breakdown:
            top_operations = sorted(operation_breakdown.items(), key=lambda x: x[1], reverse=True)[:3]
            for op, energy in top_operations:
                if energy > stats["total_energy_joules"] * 0.2:
                    recommendations.append(
                        {
                            "type": "operation_optimization",
                            "severity": "medium",
                            "operation": op,
                            "message": f"Operation '{op}' consuming {energy:.2f}J",
                            "suggestion": f"Consider batching '{op}' operations or implementing caching",
                        }
                    )

        # Budget-based recommendations
        if stats["budget_status"] and stats["budget_status"]["percentage_used"] > 80:
            recommendations.append(
                {
                    "type": "budget_warning",
                    "severity": "high",
                    "message": f"Energy budget {stats['budget_status']['percentage_used']:.1f}% consumed",
                    "suggestion": "Consider deferring non-critical operations or switching to low-power mode",
                }
            )

        # Profile recommendations
        if self.current_profile in [
            EnergyProfile.HIGH_PERFORMANCE,
            EnergyProfile.BURST,
        ]:
            if stats["average_power_watts"] > 10.0:  # High sustained power
                recommendations.append(
                    {
                        "type": "profile_optimization",
                        "severity": "medium",
                        "message": f"Sustained high power consumption at {stats['average_power_watts']:.2f}W",
                        "suggestion": "Consider switching to NORMAL or LOW_POWER profile for non-critical operations",
                    }
                )

        with self._lock:
            self.recommendations.extend(recommendations)
            # Keep only recent recommendations
            self.recommendations = self.recommendations[-20:]

    async def start_monitoring(self):
        """Start real-time energy monitoring"""
        if self._monitoring_task and not self._monitoring_task.done():
            return

        self.monitoring_enabled = True
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Energy monitoring started")

    async def stop_monitoring(self):
        """Stop real-time energy monitoring"""
        self.monitoring_enabled = False
        if self._monitoring_task:
            await self._monitoring_task
        logger.info("Energy monitoring stopped")

    async def _monitoring_loop(self):
        """Real-time monitoring loop"""
        while self.monitoring_enabled:
            try:
                # Collect system metrics if available
                if HAS_PSUTIL:
                    cpu_percent = psutil.cpu_percent(interval=0.1)
                    memory_info = psutil.virtual_memory()

                    # Estimate energy based on utilization
                    cpu_energy = self._estimate_component_energy(EnergyComponent.CPU, cpu_percent / 100.0)
                    memory_energy = self._estimate_component_energy(EnergyComponent.MEMORY, memory_info.percent / 100.0)

                    # Record system energy consumption
                    self.record_energy_consumption(
                        EnergyComponent.CPU,
                        "system_monitoring",
                        cpu_energy,
                        self.monitoring_interval * 1000,
                        {"cpu_percent": cpu_percent},
                    )

                    self.record_energy_consumption(
                        EnergyComponent.MEMORY,
                        "system_monitoring",
                        memory_energy,
                        self.monitoring_interval * 1000,
                        {"memory_percent": memory_info.percent},
                    )

                # Check budgets and generate recommendations
                if self.active_budget and self.active_budget in self.budgets:
                    budget = self.budgets[self.active_budget]
                    if budget.time_elapsed() > budget.time_window_seconds:
                        # Reset budget for new time window
                        budget.reset()
                        logger.info(f"Budget '{self.active_budget}' reset for new time window")

                await asyncio.sleep(self.monitoring_interval)

            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self.monitoring_interval)

    def _estimate_component_energy(self, component: EnergyComponent, utilization: float) -> float:
        """Estimate energy consumption based on component utilization"""
        if component not in self.component_profiles:
            return 0.0

        profile_energy = self.component_profiles[component].get(self.current_profile, 0.1)

        # Energy scales with utilization
        return profile_energy * utilization * self.monitoring_interval

    def export_metrics(self, filepath: str, format: str = "json"):
        """Export energy metrics to file"""
        with self._lock:
            metrics_data = [m.to_dict() for m in self.metrics]
            stats = self.get_energy_statistics()

            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "statistics": stats,
                "metrics": metrics_data,
                "model_parameters": dict(self.energy_model.model_params),
                "recommendations": self.recommendations,
            }

            if format == "json":
                with open(filepath, "w") as f:
                    json.dump(export_data, f, indent=2)
            else:
                raise ValueError(f"Unsupported export format: {format}")

            logger.info(f"Exported {len(metrics_data)} metrics to {filepath}")


# Integration with existing modules


class EnergyAwareComponent:
    """Base class for energy-aware system components"""

    def __init__(self, component_name: str, energy_analyzer: EnergyConsumptionAnalyzer):
        self.component_name = component_name
        self.energy_analyzer = energy_analyzer
        self._operation_count = 0

    async def execute_with_energy_tracking(self, operation: str, operation_func: Callable, *args, **kwargs) -> Any:
        """Execute an operation with automatic energy tracking"""
        start_time = time.time()

        # Predict energy consumption
        input_size = kwargs.get("input_size", 1)
        prediction = self.energy_analyzer.predict_operation_energy(f"{self.component_name}.{operation}", input_size)

        if not prediction["can_afford"]:
            logger.warning(f"Operation {operation} exceeds energy budget")
            # Could implement queuing or rejection logic here

        try:
            # Execute operation
            result = await operation_func(*args, **kwargs)

            # Calculate actual energy (simplified estimation)
            duration_ms = (time.time() - start_time) * 1000
            actual_energy = self._estimate_operation_energy(operation, duration_ms, input_size)

            # Record consumption
            self.energy_analyzer.record_energy_consumption(
                EnergyComponent.COMPUTATION,
                f"{self.component_name}.{operation}",
                actual_energy,
                duration_ms,
                {
                    "input_size": input_size,
                    "operation_count": self._operation_count,
                },
            )

            self._operation_count += 1
            return result

        except Exception as e:
            logger.error(f"Operation {operation} failed: {e}")
            raise

    def _estimate_operation_energy(self, operation: str, duration_ms: float, input_size: int) -> float:
        """Estimate energy consumption for an operation"""
        # Simple model: energy = base + computation + data
        base_energy = 0.001  # 1mJ base
        computation_energy = duration_ms * 0.0001  # 0.1mJ per ms
        data_energy = input_size * 0.000001  # 1µJ per unit

        return base_energy + computation_energy + data_energy


# Example usage and testing


async def demonstrate_energy_analysis():
    """Demonstrate energy consumption analysis capabilities"""
    analyzer = EnergyConsumptionAnalyzer(carbon_intensity_kwh=0.5)

    # Create energy budget
    analyzer.create_budget(
        "daily_budget",
        total_joules=1000.0,  # 1kJ daily budget
        time_window_seconds=86400,  # 24 hours
        component_budgets={
            EnergyComponent.CPU: 400.0,
            EnergyComponent.NETWORK: 300.0,
            EnergyComponent.MEMORY: 300.0,
        },
    )

    # Start monitoring
    await analyzer.start_monitoring()

    # Simulate various operations
    for i in range(10):
        # CPU-intensive operation
        analyzer.record_energy_consumption(
            EnergyComponent.CPU,
            "matrix_multiplication",
            energy_joules=0.5 + i * 0.1,
            duration_ms=100 + i * 10,
            metadata={"matrix_size": 100 + i * 10},
        )

        # Network operation
        analyzer.record_energy_consumption(
            EnergyComponent.NETWORK,
            "data_transfer",
            energy_joules=0.3 + i * 0.05,
            duration_ms=50 + i * 5,
            metadata={"bytes_transferred": 1024 * (i + 1)},
        )

        await asyncio.sleep(0.1)

    # Get statistics
    stats = analyzer.get_energy_statistics()
    print("Energy Statistics:")
    print(json.dumps(stats, indent=2))

    # Test prediction
    prediction = analyzer.predict_operation_energy("matrix_multiplication", 200)
    print(f"\nEnergy Prediction: {json.dumps(prediction, indent=2)}")

    # Stop monitoring
    await analyzer.stop_monitoring()

    # Export metrics
    analyzer.export_metrics("energy_metrics.json")


if __name__ == "__main__":
    asyncio.run(demonstrate_energy_analysis())
