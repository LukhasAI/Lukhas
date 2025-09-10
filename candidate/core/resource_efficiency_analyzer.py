"""
══════════════════════════════════════════════════════════════════════════════════
║ 🧠 LUKHAS AI - RESOURCE EFFICIENCY ANALYZER
║ Comprehensive analysis of system resource consumption and optimization
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: resource_efficiency_analyzer.py
║ Path: lukhas/core/resource_efficiency_analyzer.py
║ Version: 1.0.0 | Created: 2025-07-27
║ Authors: LUKHAS AI Core Team
╠══════════════════════════════════════════════════════════════════════════════════
║ DESCRIPTION
╠══════════════════════════════════════════════════════════════════════════════════
║ Addresses REALITY_TODO 135: Analysis of Resource Efficiency and Implementation.
║ Provides detailed metrics on memory usage, computational efficiency, energy
║ consumption patterns, and optimization opportunities for the Symbiotic Swarm.
╚══════════════════════════════════════════════════════════════════════════════════
"""
import gc
import json
import logging
import threading
import time
import tracemalloc
from collections import defaultdict, deque
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any

import numpy as np
import psutil

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResourceType(Enum):
    """Types of resources to monitor"""

    CPU = "cpu"
    MEMORY = "memory"
    DISK_IO = "disk_io"
    NETWORK_IO = "network_io"
    ENERGY = "energy"  # Estimated based on CPU usage
    THREADS = "threads"
    FILE_DESCRIPTORS = "file_descriptors"


@dataclass
class ResourceSnapshot:
    """Point-in-time resource usage snapshot"""

    timestamp: float
    cpu_percent: float
    memory_rss: int  # Resident Set Size in bytes
    memory_vms: int  # Virtual Memory Size in bytes
    memory_percent: float
    disk_read_bytes: int
    disk_write_bytes: int
    network_sent_bytes: int
    network_recv_bytes: int
    thread_count: int
    open_files: int
    energy_estimate: float  # Estimated watt-hours
    gc_stats: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ResourceTrend:
    """Resource usage trend analysis"""

    resource_type: ResourceType
    current_value: float
    average_value: float
    peak_value: float
    min_value: float
    trend_direction: str  # "increasing", "decreasing", "stable"
    trend_rate: float  # Change rate per second
    prediction_1h: float  # Predicted value in 1 hour
    optimization_potential: float  # 0-1 score of optimization opportunity


@dataclass
class EfficiencyReport:
    """Comprehensive efficiency analysis report"""

    timestamp: float
    duration_seconds: float
    snapshots_analyzed: int

    # Overall metrics
    efficiency_score: float  # 0-100 overall efficiency score
    resource_utilization: dict[str, float]  # Utilization by resource type

    # Trends
    trends: dict[str, ResourceTrend]

    # Bottlenecks
    bottlenecks: list[dict[str, Any]]

    # Recommendations
    recommendations: list[dict[str, Any]]

    # Detailed analysis
    memory_analysis: dict[str, Any]
    cpu_analysis: dict[str, Any]
    io_analysis: dict[str, Any]
    energy_analysis: dict[str, Any]

    def to_json(self) -> str:
        """Convert report to JSON format"""
        return json.dumps(asdict(self), indent=2, default=str)


class ResourceEfficiencyAnalyzer:
    """
    Analyzes resource consumption patterns and provides optimization recommendations
    for the Symbiotic Swarm architecture
    """

    def __init__(
        self,
        sample_interval: float = 1.0,
        history_size: int = 3600,  # 1 hour of second-by-second data
        enable_memory_profiling: bool = True,
    ):
        """
        Initialize the resource efficiency analyzer

        Args:
            sample_interval: Seconds between resource samples
            history_size: Number of historical samples to maintain
            enable_memory_profiling: Enable detailed memory profiling
        """
        self.sample_interval = sample_interval
        self.history_size = history_size
        self.enable_memory_profiling = enable_memory_profiling

        # Resource history
        self.resource_history: deque = deque(maxlen=history_size)
        self.start_time = time.time()

        # Process handle
        self.process = psutil.Process()

        # Baseline measurements
        self.baseline_snapshot = None
        self.disk_io_baseline = None
        self.network_io_baseline = None

        # Memory profiling
        if enable_memory_profiling:
            tracemalloc.start()

        # Monitoring control
        self._monitoring = False
        self._monitor_thread = None
        self._lock = threading.Lock()

        # Efficiency thresholds
        self.thresholds = {
            "cpu_high": 80.0,
            "memory_high": 80.0,
            "thread_excessive": 1000,
            "file_descriptor_high": 80.0,  # Percentage of limit
        }

        # Energy estimation parameters (simplified model)
        self.cpu_tdp = self._estimate_cpu_tdp()  # Thermal Design Power in watts

        logger.info(
            f"Resource efficiency analyzer initialized: interval={sample_interval}s, "
            f"history={history_size}, cpu_tdp={self.cpu_tdp}W"
        )

    def _estimate_cpu_tdp(self) -> float:
        """Estimate CPU TDP based on system info"""
        # Simplified estimation - in production would use hardware-specific data
        cpu_count = psutil.cpu_count(logical=False) or 4
        # Assume 15W per core for modern efficient CPUs
        return cpu_count * 15.0

    def start_monitoring(self):
        """Start continuous resource monitoring"""
        if self._monitoring:
            return

        self._monitoring = True
        self._monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self._monitor_thread.start()
        logger.info("Resource monitoring started")

    def stop_monitoring(self):
        """Stop resource monitoring"""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
        logger.info("Resource monitoring stopped")

    def _monitoring_loop(self):
        """Main monitoring loop"""
        # Initialize baseline I/O counters with error handling
        try:
            self.disk_io_baseline = self.process.io_counters()
        except (AttributeError, PermissionError, OSError):
            # io_counters() may not be available on all platforms
            self.disk_io_baseline = None

        try:
            self.network_io_baseline = psutil.net_io_counters()
        except (AttributeError, PermissionError, OSError):
            self.network_io_baseline = None

        while self._monitoring:
            try:
                snapshot = self._capture_snapshot()
                with self._lock:
                    self.resource_history.append(snapshot)

                    # Set baseline if first snapshot
                    if self.baseline_snapshot is None:
                        self.baseline_snapshot = snapshot

                time.sleep(self.sample_interval)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")

    def _capture_snapshot(self) -> ResourceSnapshot:
        """Capture current resource usage"""
        # CPU usage
        cpu_percent = self.process.cpu_percent()

        # Memory usage
        memory_info = self.process.memory_info()
        memory_percent = self.process.memory_percent()

        # I/O counters with fallback for unsupported platforms
        disk_read = disk_write = 0
        if self.disk_io_baseline is not None:
            try:
                disk_io = self.process.io_counters()
                disk_read = disk_io.read_bytes - self.disk_io_baseline.read_bytes
                disk_write = disk_io.write_bytes - self.disk_io_baseline.write_bytes
            except Exception:
                pass

        net_sent = net_recv = 0
        if self.network_io_baseline is not None:
            try:
                net_io = psutil.net_io_counters()
                net_sent = net_io.bytes_sent - self.network_io_baseline.bytes_sent
                net_recv = net_io.bytes_recv - self.network_io_baseline.bytes_recv
            except Exception:
                pass

        # Thread and file descriptor count
        thread_count = self.process.num_threads()
        try:
            open_files = len(self.process.open_files())
        except Exception:
            open_files = 0

        # Energy estimation (simplified)
        energy_estimate = self._estimate_energy_consumption(cpu_percent)

        # Garbage collection stats
        gc_stats = {f"gen{i}_collections": gc.get_stats()[i]["collections"] for i in range(len(gc.get_stats()))}

        return ResourceSnapshot(
            timestamp=time.time(),
            cpu_percent=cpu_percent,
            memory_rss=memory_info.rss,
            memory_vms=memory_info.vms,
            memory_percent=memory_percent,
            disk_read_bytes=disk_read,
            disk_write_bytes=disk_write,
            network_sent_bytes=net_sent,
            network_recv_bytes=net_recv,
            thread_count=thread_count,
            open_files=open_files,
            energy_estimate=energy_estimate,
            gc_stats=gc_stats,
        )

    def _estimate_energy_consumption(self, cpu_percent: float) -> float:
        """Estimate energy consumption in watt-hours"""
        # Simplified linear model: Energy = TDP * CPU% * time
        watts = self.cpu_tdp * (cpu_percent / 100.0)
        watt_hours = watts * (self.sample_interval / 3600.0)
        return watt_hours

    def analyze_efficiency(self, duration_hours: float = 1.0) -> EfficiencyReport:
        """
        Perform comprehensive efficiency analysis

        Args:
            duration_hours: Hours of history to analyze

        Returns:
            Detailed efficiency report
        """
        with self._lock:
            if not self.resource_history:
                raise ValueError("No resource data available for analysis")

            # Get relevant snapshots
            current_time = time.time()
            cutoff_time = current_time - (duration_hours * 3600)

            snapshots = [s for s in self.resource_history if s.timestamp >= cutoff_time]

            if not snapshots:
                snapshots = list(self.resource_history)

        # Analyze trends
        trends = self._analyze_trends(snapshots)

        # Identify bottlenecks
        bottlenecks = self._identify_bottlenecks(snapshots, trends)

        # Generate recommendations
        recommendations = self._generate_recommendations(trends, bottlenecks)

        # Detailed analysis
        memory_analysis = self._analyze_memory_usage(snapshots)
        cpu_analysis = self._analyze_cpu_usage(snapshots)
        io_analysis = self._analyze_io_patterns(snapshots)
        energy_analysis = self._analyze_energy_consumption(snapshots)

        # Calculate overall efficiency score
        efficiency_score = self._calculate_efficiency_score(trends, bottlenecks, memory_analysis, cpu_analysis)

        # Resource utilization summary
        resource_utilization = {
            ResourceType.CPU.value: cpu_analysis["average_utilization"],
            ResourceType.MEMORY.value: memory_analysis["average_utilization"],
            ResourceType.DISK_IO.value: io_analysis["disk_utilization"],
            ResourceType.NETWORK_IO.value: io_analysis["network_utilization"],
            ResourceType.ENERGY.value: energy_analysis["efficiency_rating"],
        }

        return EfficiencyReport(
            timestamp=current_time,
            duration_seconds=len(snapshots) * self.sample_interval,
            snapshots_analyzed=len(snapshots),
            efficiency_score=efficiency_score,
            resource_utilization=resource_utilization,
            trends=trends,
            bottlenecks=bottlenecks,
            recommendations=recommendations,
            memory_analysis=memory_analysis,
            cpu_analysis=cpu_analysis,
            io_analysis=io_analysis,
            energy_analysis=energy_analysis,
        )

    def _analyze_trends(self, snapshots: list[ResourceSnapshot]) -> dict[str, ResourceTrend]:
        """Analyze resource usage trends"""
        if not snapshots:
            return {}

        trends = {}

        # CPU trend
        cpu_values = [s.cpu_percent for s in snapshots]
        trends["cpu"] = self._calculate_trend(ResourceType.CPU, cpu_values, snapshots)

        # Memory trend
        memory_values = [s.memory_percent for s in snapshots]
        trends["memory"] = self._calculate_trend(ResourceType.MEMORY, memory_values, snapshots)

        # Thread trend
        thread_values = [float(s.thread_count) for s in snapshots]
        trends["threads"] = self._calculate_trend(ResourceType.THREADS, thread_values, snapshots)

        # Energy trend
        energy_values = [s.energy_estimate for s in snapshots]
        trends["energy"] = self._calculate_trend(ResourceType.ENERGY, energy_values, snapshots)

        return trends

    def _calculate_trend(
        self,
        resource_type: ResourceType,
        values: list[float],
        snapshots: list[ResourceSnapshot],
    ) -> ResourceTrend:
        """Calculate trend for a specific resource"""
        if not values:
            return None

        current = values[-1]
        average = np.mean(values)
        peak = max(values)
        minimum = min(values)

        # Calculate trend direction and rate
        if len(values) > 1:
            # Linear regression for trend
            x = np.arange(len(values))
            slope, _ = np.polyfit(x, values, 1)

            # Trend direction
            if abs(slope) < 0.01:
                direction = "stable"
            elif slope > 0:
                direction = "increasing"
            else:
                direction = "decreasing"

            # Rate per second
            rate = slope / self.sample_interval

            # Simple linear prediction for 1 hour
            samples_per_hour = 3600 / self.sample_interval
            prediction = current + (rate * samples_per_hour)
            prediction = max(0, prediction)  # Can't be negative
        else:
            direction = "stable"
            rate = 0.0
            prediction = current

        # Optimization potential (0-1)
        # Higher values mean more opportunity for optimization
        if resource_type == ResourceType.CPU:
            # High CPU with variation suggests optimization potential
            optimization = (average / 100.0) * (1 - minimum / max(peak, 1))
        elif resource_type == ResourceType.MEMORY:
            # Steady high memory suggests potential memory leaks
            optimization = (average / 100.0) if direction == "increasing" else 0.3
        elif resource_type == ResourceType.THREADS:
            # Excessive threads indicate potential consolidation
            optimization = min(1.0, current / 1000.0)
        else:
            optimization = 0.5

        return ResourceTrend(
            resource_type=resource_type,
            current_value=current,
            average_value=average,
            peak_value=peak,
            min_value=minimum,
            trend_direction=direction,
            trend_rate=rate,
            prediction_1h=prediction,
            optimization_potential=optimization,
        )

    def _identify_bottlenecks(
        self,
        snapshots: list[ResourceSnapshot],
        trends: dict[str, ResourceTrend],
    ) -> list[dict[str, Any]]:
        """Identify system bottlenecks"""
        bottlenecks = []

        # CPU bottleneck
        cpu_trend = trends.get("cpu")
        if cpu_trend and cpu_trend.average_value > self.thresholds["cpu_high"]:
            bottlenecks.append(
                {
                    "type": "cpu_saturation",
                    "severity": ("high" if cpu_trend.current_value > 90 else "medium"),
                    "impact": "Reduced throughput and increased latency",
                    "details": {
                        "current_usage": f"{cpu_trend.current_value:.1f}%",
                        "average_usage": f"{cpu_trend.average_value:.1f}%",
                        "trend": cpu_trend.trend_direction,
                    },
                }
            )

        # Memory bottleneck
        memory_trend = trends.get("memory")
        if memory_trend:
            if memory_trend.average_value > self.thresholds["memory_high"]:
                bottlenecks.append(
                    {
                        "type": "memory_pressure",
                        "severity": ("high" if memory_trend.current_value > 90 else "medium"),
                        "impact": "Risk of OOM, increased GC pressure",
                        "details": {
                            "current_usage": f"{memory_trend.current_value:.1f}%",
                            "trend": memory_trend.trend_direction,
                            "predicted_1h": f"{memory_trend.prediction_1h:.1f}%",
                        },
                    }
                )

            # Memory leak detection
            if memory_trend.trend_direction == "increasing" and memory_trend.trend_rate > 0.01:  # 1% per second
                bottlenecks.append(
                    {
                        "type": "potential_memory_leak",
                        "severity": "high",
                        "impact": "System will run out of memory",
                        "details": {
                            "growth_rate": f"{memory_trend.trend_rate:.3f}% per second",
                            "time_to_oom": self._estimate_time_to_oom(memory_trend),
                        },
                    }
                )

        # Thread explosion
        thread_trend = trends.get("threads")
        if thread_trend and thread_trend.current_value > self.thresholds["thread_excessive"]:
            bottlenecks.append(
                {
                    "type": "thread_explosion",
                    "severity": "medium",
                    "impact": "Increased context switching overhead",
                    "details": {
                        "thread_count": int(thread_trend.current_value),
                        "optimal_range": "100-500 threads",
                    },
                }
            )

        # I/O bottlenecks
        io_bottlenecks = self._check_io_bottlenecks(snapshots)
        bottlenecks.extend(io_bottlenecks)

        return bottlenecks

    def _estimate_time_to_oom(self, memory_trend: ResourceTrend) -> str:
        """Estimate time until out of memory"""
        if memory_trend.trend_rate <= 0:
            return "N/A"

        remaining_percent = 100 - memory_trend.current_value
        seconds_to_oom = remaining_percent / memory_trend.trend_rate

        if seconds_to_oom < 3600:
            return f"{seconds_to_oom / 60:.1f} minutes"
        elif seconds_to_oom < 86400:
            return f"{seconds_to_oom / 3600:.1f} hours"
        else:
            return f"{seconds_to_oom / 86400:.1f} days"

    def _check_io_bottlenecks(self, snapshots: list[ResourceSnapshot]) -> list[dict[str, Any]]:
        """Check for I/O bottlenecks"""
        bottlenecks = []

        if len(snapshots) < 10:
            return bottlenecks

        # Calculate I/O rates
        recent_snapshots = snapshots[-10:]

        disk_read_rate = np.mean([s.disk_read_bytes for s in recent_snapshots])
        disk_write_rate = np.mean([s.disk_write_bytes for s in recent_snapshots])

        # High I/O rate threshold (100 MB/s)
        high_io_threshold = 100 * 1024 * 1024

        if disk_read_rate > high_io_threshold or disk_write_rate > high_io_threshold:
            bottlenecks.append(
                {
                    "type": "high_disk_io",
                    "severity": "medium",
                    "impact": "Increased latency, potential disk saturation",
                    "details": {
                        "read_rate": f"{disk_read_rate / 1024 / 1024:.1f} MB/s",
                        "write_rate": f"{disk_write_rate / 1024 / 1024:.1f} MB/s",
                    },
                }
            )

        return bottlenecks

    def _generate_recommendations(
        self,
        trends: dict[str, ResourceTrend],
        bottlenecks: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Generate optimization recommendations"""
        recommendations = []

        # CPU recommendations
        cpu_trend = trends.get("cpu")
        if cpu_trend and cpu_trend.optimization_potential > 0.7:
            recommendations.append(
                {
                    "category": "cpu_optimization",
                    "priority": "high",
                    "title": "Optimize CPU Usage",
                    "description": "High CPU usage detected with optimization potential",
                    "actions": [
                        "Profile CPU hotspots using cProfile or py-spy",
                        "Consider algorithmic optimizations",
                        "Implement caching for expensive computations",
                        "Use vectorized operations where possible",
                        "Consider distributing work across multiple processes",
                    ],
                    "expected_impact": "20-40% reduction in CPU usage",
                }
            )

        # Memory recommendations
        memory_trend = trends.get("memory")
        if memory_trend and memory_trend.optimization_potential > 0.6:
            recommendations.append(
                {
                    "category": "memory_optimization",
                    "priority": (
                        "high" if any(b["type"] == "potential_memory_leak" for b in bottlenecks) else "medium"
                    ),
                    "title": "Reduce Memory Consumption",
                    "description": "Memory usage is high or growing",
                    "actions": [
                        "Use memory profiling to identify large allocations",
                        "Implement object pooling for frequently created objects",
                        "Use generators instead of lists for large datasets",
                        "Clear caches and temporary data periodically",
                        "Consider using more memory-efficient data structures",
                    ],
                    "expected_impact": "30-50% reduction in memory usage",
                }
            )

        # Thread recommendations
        thread_trend = trends.get("threads")
        if thread_trend and thread_trend.current_value > 500:
            recommendations.append(
                {
                    "category": "concurrency_optimization",
                    "priority": "medium",
                    "title": "Optimize Thread Usage",
                    "description": "Excessive thread count detected",
                    "actions": [
                        "Use thread pools instead of creating new threads",
                        "Consider async/await for I/O-bound operations",
                        "Implement proper thread lifecycle management",
                        "Use multiprocessing for CPU-bound tasks",
                    ],
                    "expected_impact": "Reduced context switching overhead",
                }
            )

        # Energy recommendations
        energy_trend = trends.get("energy")
        if energy_trend and energy_trend.average_value > 0.5:
            recommendations.append(
                {
                    "category": "energy_optimization",
                    "priority": "low",
                    "title": "Improve Energy Efficiency",
                    "description": "Opportunities to reduce energy consumption",
                    "actions": [
                        "Implement adaptive sampling rates",
                        "Use CPU frequency scaling during low activity",
                        "Batch operations to reduce wake-ups",
                        "Implement intelligent idle states",
                    ],
                    "expected_impact": "10-30% reduction in energy consumption",
                }
            )

        # Architecture-specific recommendations for Symbiotic Swarm
        recommendations.append(
            {
                "category": "swarm_optimization",
                "priority": "medium",
                "title": "Optimize Symbiotic Swarm Architecture",
                "description": "Leverage distributed nature for efficiency",
                "actions": [
                    "Implement intelligent task distribution based on node capabilities",
                    "Use locality-aware scheduling to reduce network overhead",
                    "Implement adaptive replication based on access patterns",
                    "Use compressed GLYPH tokens for inter-node communication",
                    "Enable collaborative caching across swarm nodes",
                ],
                "expected_impact": "Improved overall system efficiency",
            }
        )

        return recommendations

    def _analyze_memory_usage(self, snapshots: list[ResourceSnapshot]) -> dict[str, Any]:
        """Detailed memory usage analysis"""
        if not snapshots:
            return {}

        memory_rss = [s.memory_rss for s in snapshots]
        memory_vms = [s.memory_vms for s in snapshots]
        memory_percent = [s.memory_percent for s in snapshots]

        # Get detailed memory stats if profiling enabled
        memory_blocks = []
        if self.enable_memory_profiling:
            snapshot = tracemalloc.take_snapshot()
            top_stats = snapshot.statistics("lineno")[:10]

            for stat in top_stats:
                memory_blocks.append(
                    {
                        "file": stat.traceback.format()[0],
                        "size": stat.size,
                        "count": stat.count,
                    }
                )

        # GC analysis
        gc_pressure = self._analyze_gc_pressure(snapshots)

        return {
            "average_rss": np.mean(memory_rss),
            "peak_rss": max(memory_rss),
            "average_vms": np.mean(memory_vms),
            "peak_vms": max(memory_vms),
            "average_utilization": np.mean(memory_percent),
            "peak_utilization": max(memory_percent),
            "fragmentation_ratio": (np.mean(memory_vms) / np.mean(memory_rss) if memory_rss else 1),
            "top_allocations": memory_blocks,
            "gc_pressure": gc_pressure,
            "memory_efficiency": self._calculate_memory_efficiency(memory_rss, memory_vms),
        }

    def _analyze_gc_pressure(self, snapshots: list[ResourceSnapshot]) -> dict[str, Any]:
        """Analyze garbage collection pressure"""
        if not snapshots or not snapshots[0].gc_stats:
            return {"status": "unknown"}

        # Get GC frequency
        gc_counts = defaultdict(list)
        for snapshot in snapshots:
            for gen, count in snapshot.gc_stats.items():
                gc_counts[gen].append(count)

        # Calculate collection rates
        gc_rates = {}
        for gen, counts in gc_counts.items():
            if len(counts) > 1:
                collections = counts[-1] - counts[0]
                duration = snapshots[-1].timestamp - snapshots[0].timestamp
                gc_rates[gen] = collections / duration if duration > 0 else 0

        # Determine pressure level
        gen0_rate = gc_rates.get("gen0_collections", 0)
        if gen0_rate > 10:  # More than 10 gen0 collections per second
            pressure_level = "high"
        elif gen0_rate > 1:
            pressure_level = "medium"
        else:
            pressure_level = "low"

        return {
            "status": pressure_level,
            "collection_rates": gc_rates,
            "recommendation": ("Consider object pooling" if pressure_level == "high" else "Normal"),
        }

    def _calculate_memory_efficiency(self, rss_values: list[int], vms_values: list[int]) -> float:
        """Calculate memory efficiency score (0-100)"""
        if not rss_values or not vms_values:
            return 0

        # Factors:
        # 1. Low fragmentation (RSS close to VMS)
        # 2. Stable memory usage
        # 3. Reasonable absolute usage

        avg_rss = np.mean(rss_values)
        avg_vms = np.mean(vms_values)

        # Fragmentation score (0-40 points)
        fragmentation_ratio = avg_rss / avg_vms if avg_vms > 0 else 1
        fragmentation_score = min(40, fragmentation_ratio * 40)

        # Stability score (0-30 points)
        rss_std = np.std(rss_values)
        stability_ratio = 1 - min(1, rss_std / avg_rss if avg_rss > 0 else 0)
        stability_score = stability_ratio * 30

        # Absolute usage score (0-30 points)
        # Assume 4GB is reasonable max for single process
        max_reasonable_memory = 4 * 1024 * 1024 * 1024
        usage_ratio = 1 - min(1, avg_rss / max_reasonable_memory)
        usage_score = usage_ratio * 30

        return fragmentation_score + stability_score + usage_score

    def _analyze_cpu_usage(self, snapshots: list[ResourceSnapshot]) -> dict[str, Any]:
        """Detailed CPU usage analysis"""
        if not snapshots:
            return {}

        cpu_values = [s.cpu_percent for s in snapshots]

        # Calculate CPU efficiency metrics
        return {
            "average_utilization": np.mean(cpu_values),
            "peak_utilization": max(cpu_values),
            "min_utilization": min(cpu_values),
            "std_deviation": np.std(cpu_values),
            "idle_percentage": len([v for v in cpu_values if v < 5]) / len(cpu_values) * 100,
            "saturated_percentage": len([v for v in cpu_values if v > 90]) / len(cpu_values) * 100,
            "efficiency_score": self._calculate_cpu_efficiency(cpu_values),
        }

    def _calculate_cpu_efficiency(self, cpu_values: list[float]) -> float:
        """Calculate CPU efficiency score (0-100)"""
        if not cpu_values:
            return 0

        # Ideal CPU usage is between 40-70%
        # Penalize both under and over utilization

        avg_cpu = np.mean(cpu_values)

        if avg_cpu < 40:
            # Under-utilized
            efficiency = (avg_cpu / 40) * 70
        elif avg_cpu <= 70:
            # Optimal range
            efficiency = 70 + ((avg_cpu - 40) / 30) * 30
        else:
            # Over-utilized
            efficiency = max(0, 100 - (avg_cpu - 70))

        return efficiency

    def _analyze_io_patterns(self, snapshots: list[ResourceSnapshot]) -> dict[str, Any]:
        """Analyze I/O patterns"""
        if not snapshots:
            return {}

        disk_reads = [s.disk_read_bytes for s in snapshots]
        disk_writes = [s.disk_write_bytes for s in snapshots]
        net_sent = [s.network_sent_bytes for s in snapshots]
        net_recv = [s.network_recv_bytes for s in snapshots]

        # Calculate rates (bytes per second)
        time_span = snapshots[-1].timestamp - snapshots[0].timestamp if len(snapshots) > 1 else 1

        return {
            "disk_read_rate": sum(disk_reads) / time_span,
            "disk_write_rate": sum(disk_writes) / time_span,
            "network_send_rate": sum(net_sent) / time_span,
            "network_recv_rate": sum(net_recv) / time_span,
            "disk_utilization": self._estimate_disk_utilization(disk_reads, disk_writes, time_span),
            "network_utilization": self._estimate_network_utilization(net_sent, net_recv, time_span),
            "io_pattern": self._classify_io_pattern(disk_reads, disk_writes, net_sent, net_recv),
        }

    def _estimate_disk_utilization(self, reads: list[int], writes: list[int], time_span: float) -> float:
        """Estimate disk utilization percentage"""
        # Assume 500 MB/s as typical SSD throughput
        max_throughput = 500 * 1024 * 1024

        total_bytes = sum(reads) + sum(writes)
        actual_throughput = total_bytes / time_span if time_span > 0 else 0

        return min(100, (actual_throughput / max_throughput) * 100)

    def _estimate_network_utilization(self, sent: list[int], recv: list[int], time_span: float) -> float:
        """Estimate network utilization percentage"""
        # Assume 1 Gbps network
        max_throughput = 1024 * 1024 * 1024 / 8  # 1 Gbps in bytes

        total_bytes = sum(sent) + sum(recv)
        actual_throughput = total_bytes / time_span if time_span > 0 else 0

        return min(100, (actual_throughput / max_throughput) * 100)

    def _classify_io_pattern(
        self,
        disk_reads: list[int],
        disk_writes: list[int],
        net_sent: list[int],
        net_recv: list[int],
    ) -> str:
        """Classify the I/O pattern"""
        total_disk = sum(disk_reads) + sum(disk_writes)
        total_network = sum(net_sent) + sum(net_recv)

        if total_disk > total_network * 10:
            return "disk_intensive"
        elif total_network > total_disk * 10:
            return "network_intensive"
        elif total_disk > 1024 * 1024 and total_network > 1024 * 1024:
            return "mixed_io"
        else:
            return "low_io"

    def _analyze_energy_consumption(self, snapshots: list[ResourceSnapshot]) -> dict[str, Any]:
        """Analyze energy consumption patterns"""
        if not snapshots:
            return {}

        energy_values = [s.energy_estimate for s in snapshots]
        time_span = (snapshots[-1].timestamp - snapshots[0].timestamp) / 3600  # hours

        total_energy = sum(energy_values)
        average_power = total_energy / time_span if time_span > 0 else 0

        # Energy efficiency based on work done per watt
        cpu_values = [s.cpu_percent for s in snapshots]
        average_cpu = np.mean(cpu_values)

        # Performance per watt metric
        perf_per_watt = average_cpu / average_power if average_power > 0 else 0

        return {
            "total_consumption_kwh": total_energy / 1000,
            "average_power_watts": average_power,
            "peak_power_watts": max(energy_values) / (self.sample_interval / 3600),
            "performance_per_watt": perf_per_watt,
            "efficiency_rating": self._calculate_energy_efficiency(perf_per_watt),
            "carbon_footprint_kg": self._estimate_carbon_footprint(total_energy),
        }

    def _calculate_energy_efficiency(self, perf_per_watt: float) -> float:
        """Calculate energy efficiency rating (0-100)"""
        # Normalize performance per watt to 0-100 scale
        # Assume 5% CPU per watt is good efficiency
        target_efficiency = 5.0

        return min(100, (perf_per_watt / target_efficiency) * 100)

    def _estimate_carbon_footprint(self, total_energy_wh: float) -> float:
        """Estimate carbon footprint in kg CO2"""
        # Global average: 0.5 kg CO2 per kWh
        carbon_intensity = 0.5

        return (total_energy_wh / 1000) * carbon_intensity

    def _calculate_efficiency_score(
        self,
        trends: dict[str, ResourceTrend],
        bottlenecks: list[dict[str, Any]],
        memory_analysis: dict[str, Any],
        cpu_analysis: dict[str, Any],
    ) -> float:
        """Calculate overall efficiency score (0-100)"""
        scores = []

        # CPU efficiency (25%)
        if "efficiency_score" in cpu_analysis:
            scores.append(cpu_analysis["efficiency_score"] * 0.25)

        # Memory efficiency (25%)
        if "memory_efficiency" in memory_analysis:
            scores.append(memory_analysis["memory_efficiency"] * 0.25)

        # Bottleneck penalty (25%)
        bottleneck_penalty = len(bottlenecks) * 10
        bottleneck_score = max(0, 100 - bottleneck_penalty)
        scores.append(bottleneck_score * 0.25)

        # Resource balance (25%)
        # Good if resources are balanced, bad if one is saturated
        balance_scores = []
        for trend in trends.values():
            if trend.average_value < 70:
                balance_scores.append(100)
            elif trend.average_value < 85:
                balance_scores.append(50)
            else:
                balance_scores.append(0)

        if balance_scores:
            balance_score = np.mean(balance_scores)
            scores.append(balance_score * 0.25)

        return sum(scores)

    def get_quick_stats(self) -> dict[str, Any]:
        """Get quick resource statistics"""
        snapshot = self._capture_snapshot()

        return {
            "timestamp": snapshot.timestamp,
            "cpu_percent": snapshot.cpu_percent,
            "memory_mb": snapshot.memory_rss / 1024 / 1024,
            "memory_percent": snapshot.memory_percent,
            "threads": snapshot.thread_count,
            "open_files": snapshot.open_files,
        }

    def export_metrics(self, filepath: str):
        """Export metrics to file for external analysis"""
        with self._lock:
            data = {
                "metadata": {
                    "start_time": self.start_time,
                    "export_time": time.time(),
                    "sample_interval": self.sample_interval,
                    "samples": len(self.resource_history),
                },
                "snapshots": [s.to_dict() for s in self.resource_history],
            }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Exported {len(data['snapshots'])} snapshots to {filepath}")


# Demo usage
if __name__ == "__main__":
    # Create analyzer
    analyzer = ResourceEfficiencyAnalyzer(
        sample_interval=0.5,
        history_size=7200,  # 1 hour at 0.5s intervals
    )

    # Start monitoring
    analyzer.start_monitoring()

    # Simulate some work
    import random

    print("Monitoring resource usage for 30 seconds...")

    # Create some CPU and memory load
    data = []
    for i in range(30):
        # Allocate some memory
        data.append([random.random() for _ in range(100000)])

        # Do some CPU work
        result = sum(sum(row) for row in data)

        time.sleep(1)

        # Print quick stats every 5 seconds
        if i % 5 == 0:
            stats = analyzer.get_quick_stats()
            print(f"Quick stats: CPU={stats['cpu_percent']:.1f}%, Memory={stats['memory_mb']:.1f}MB")

    # Generate efficiency report
    print("\nGenerating efficiency report...")
    report = analyzer.analyze_efficiency(duration_hours=0.01)  # Last ~30 seconds

    # Print summary
    print(f"\nEfficiency Score: {report.efficiency_score:.1f}/100")
    print(f"Bottlenecks found: {len(report.bottlenecks)}")
    print(f"Recommendations: {len(report.recommendations)}")

    # Print bottlenecks
    if report.bottlenecks:
        print("\nBottlenecks:")
        for bottleneck in report.bottlenecks:
            print(f"  - {bottleneck['type']}: {bottleneck['impact']}")

    # Print top recommendations
    if report.recommendations:
        print("\nTop Recommendations:")
        for rec in report.recommendations[:3]:
            print(f"  - {rec['title']}: {rec['description']}")

    # Export full report
    with open("/tmp/efficiency_report.json", "w") as f:
        f.write(report.to_json())
    print("\nFull report exported to /tmp/efficiency_report.json")

    # Stop monitoring
    analyzer.stop_monitoring()
