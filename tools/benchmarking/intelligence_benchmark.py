"""
LUKHAS AI Intelligence Performance Benchmarking
=============================================
Comprehensive benchmarking system for intelligence engines and agent coordination.
Provides performance analysis, optimization recommendations, and competitive benchmarks.

Trinity Framework: ⚛️ (Identity), 🧠 (Consciousness), 🛡️ (Guardian)
"""

import asyncio
import json
import logging
import statistics
import time
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

import psutil

from lukhas.governance.intelligence_safety_validator import (
    SafetyLevel,
    get_safety_validator)
from lukhas.orchestration.agent_orchestrator.intelligence_bridge import (
    AgentType,
    IntelligenceRequestType,
    create_agent_request,
    get_agent_bridge,
)
from lukhas.orchestration.brain.monitoring.intelligence_monitor import get_monitor
from lukhas.orchestration.intelligence_adapter import get_orchestration_adapter

logger = logging.getLogger("LUKHAS.Tools.Benchmarking.Intelligence")


class BenchmarkType(Enum):
    """Types of benchmarks"""

    PERFORMANCE = "performance"  # Speed and efficiency benchmarks
    ACCURACY = "accuracy"  # Intelligence accuracy benchmarks
    SCALABILITY = "scalability"  # Load and scale testing
    SAFETY = "safety"  # Safety validation benchmarks
    AGENT_COORDINATION = "agent_coordination"  # Agent coordination efficiency
    TRINITY_COMPLIANCE = "trinity_compliance"  # Trinity Framework compliance
    COMPARATIVE = "comparative"  # Comparison against baselines


class BenchmarkScenario(Enum):
    """Predefined benchmark scenarios"""

    SINGLE_AGENT_ANALYSIS = "single_agent_analysis"
    MULTI_AGENT_COORDINATION = "multi_agent_coordination"
    COMPLEX_REASONING = "complex_reasoning"
    AUTONOMOUS_GOAL_FORMATION = "autonomous_goal_formation"
    SAFETY_VALIDATION_STRESS = "safety_validation_stress"
    HIGH_FREQUENCY_OPERATIONS = "high_frequency_operations"
    MEMORY_INTENSIVE_TASKS = "memory_intensive_tasks"
    TRINITY_COMPLIANCE_STRESS = "trinity_compliance_stress"


@dataclass
class BenchmarkConfig:
    """Configuration for benchmark execution"""

    scenario: BenchmarkScenario
    benchmark_type: BenchmarkType
    iterations: int = 100
    concurrency_level: int = 1
    timeout: float = 30.0
    warm_up_iterations: int = 10
    cool_down_delay: float = 1.0
    target_metrics: list[str] = None
    safety_level: SafetyLevel = SafetyLevel.MEDIUM
    metadata: Optional[dict[str, Any]] = None

    def __post_init__(self):
        if self.target_metrics is None:
            self.target_metrics = [
                "response_time",
                "success_rate",
                "confidence",
                "safety_score",
            ]


@dataclass
class BenchmarkResult:
    """Results from benchmark execution"""

    config: BenchmarkConfig
    start_time: datetime
    end_time: datetime
    total_duration: float
    iterations_completed: int
    successful_iterations: int
    failed_iterations: int
    metrics: dict[str, list[float]]
    statistics: dict[str, dict[str, float]]
    system_metrics: dict[str, float]
    agent_performance: dict[str, dict[str, Any]]
    intelligence_engine_performance: dict[str, dict[str, Any]]
    trinity_compliance_scores: list[float]
    safety_validation_results: list[dict[str, Any]]
    recommendations: list[str]
    metadata: Optional[dict[str, Any]] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            **asdict(self),
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "config": asdict(self.config),
        }


class LukhasIntelligenceBenchmarking:
    """
    Comprehensive benchmarking system for intelligence engines and agent coordination.
    Provides detailed performance analysis and optimization recommendations.
    """

    def __init__(self):
        self.benchmark_results = []
        self.baseline_metrics = {}
        self.performance_targets = self._initialize_performance_targets()
        self.agent_bridge = None
        self.orchestration_adapter = None
        self.safety_validator = None
        self.monitor = None
        self._initialized = False

    def _initialize_performance_targets(self) -> dict[str, float]:
        """Initialize performance targets for benchmarking"""
        return {
            "response_time": 0.1,  # 100ms target
            "success_rate": 0.95,  # 95% success rate
            "confidence": 0.8,  # 80% average confidence
            "safety_score": 0.9,  # 90% safety score
            "trinity_compliance": 0.9,  # 90% Trinity compliance
            "cpu_usage": 0.8,  # 80% max CPU usage
            "memory_usage": 0.8,  # 80% max memory usage
            "agent_coordination": 0.95,  # 95% coordination efficiency
        }

    async def initialize(self):
        """Initialize the benchmarking system"""
        logger.info("🏁 Initializing Intelligence Benchmarking System")

        # Initialize core components
        self.agent_bridge = await get_agent_bridge()
        self.orchestration_adapter = await get_orchestration_adapter()
        self.safety_validator = await get_safety_validator()
        self.monitor = get_monitor()

        # Start monitoring if not already active
        if not self.monitor._monitoring_active:
            await self.monitor.start_monitoring()

        self._initialized = True
        logger.info("✅ Intelligence Benchmarking System initialized")

    async def run_benchmark(self, config: BenchmarkConfig) -> BenchmarkResult:
        """
        Run a complete benchmark based on configuration

        Args:
            config: Benchmark configuration

        Returns:
            Comprehensive benchmark results
        """
        if not self._initialized:
            await self.initialize()

        start_time = datetime.now(timezone.utc)
        logger.info(f"🏁 Starting benchmark: {config.scenario.value} ({config.iterations} iterations)")

        # Initialize result tracking
        metrics = defaultdict(list)
        system_metrics = {}
        agent_performance = defaultdict(dict)
        intelligence_engine_performance = defaultdict(dict)
        trinity_compliance_scores = []
        safety_validation_results = []

        successful_iterations = 0
        failed_iterations = 0

        try:
            # Warm-up phase
            if config.warm_up_iterations > 0:
                logger.info(f"🔥 Warm-up phase: {config.warm_up_iterations} iterations")
                await self._run_warm_up(config)

            # Main benchmark phase
            logger.info(f"📊 Main benchmark phase: {config.iterations} iterations")

            # Record initial system state
            initial_system_metrics = await self._capture_system_metrics()

            # Execute benchmark iterations
            if config.concurrency_level > 1:
                # Concurrent execution
                tasks = []
                for i in range(config.iterations):
                    task = self._execute_benchmark_iteration(config, i)
                    tasks.append(task)

                # Process in batches to manage concurrency
                batch_size = config.concurrency_level
                for i in range(0, len(tasks), batch_size):
                    batch = tasks[i : i + batch_size]
                    results = await asyncio.gather(*batch, return_exceptions=True)

                    for result in results:
                        if isinstance(result, Exception):
                            failed_iterations += 1
                            logger.warning(f"Benchmark iteration failed: {result}")
                        else:
                            successful_iterations += 1
                            await self._process_iteration_result(
                                result,
                                metrics,
                                agent_performance,
                                intelligence_engine_performance,
                                trinity_compliance_scores,
                                safety_validation_results,
                            )
            else:
                # Sequential execution
                for i in range(config.iterations):
                    try:
                        result = await self._execute_benchmark_iteration(config, i)
                        successful_iterations += 1
                        await self._process_iteration_result(
                            result,
                            metrics,
                            agent_performance,
                            intelligence_engine_performance,
                            trinity_compliance_scores,
                            safety_validation_results,
                        )

                        # Cool-down delay
                        if config.cool_down_delay > 0:
                            await asyncio.sleep(config.cool_down_delay)

                    except Exception as e:
                        failed_iterations += 1
                        logger.warning(f"Benchmark iteration {i} failed: {e}")

            # Record final system state
            final_system_metrics = await self._capture_system_metrics()
            system_metrics = await self._calculate_system_metrics_delta(initial_system_metrics, final_system_metrics)

            # Calculate statistics
            statistics_data = await self._calculate_statistics(metrics)

            # Generate recommendations
            recommendations = await self._generate_recommendations(statistics_data, system_metrics, config)

            end_time = datetime.now(timezone.utc)
            total_duration = (end_time - start_time).total_seconds()

            # Create benchmark result
            result = BenchmarkResult(
                config=config,
                start_time=start_time,
                end_time=end_time,
                total_duration=total_duration,
                iterations_completed=successful_iterations + failed_iterations,
                successful_iterations=successful_iterations,
                failed_iterations=failed_iterations,
                metrics=dict(metrics),
                statistics=statistics_data,
                system_metrics=system_metrics,
                agent_performance=dict(agent_performance),
                intelligence_engine_performance=dict(intelligence_engine_performance),
                trinity_compliance_scores=trinity_compliance_scores,
                safety_validation_results=safety_validation_results,
                recommendations=recommendations,
                metadata=config.metadata,
            )

            # Store result
            self.benchmark_results.append(result)

            logger.info(f"✅ Benchmark completed: {successful_iterations}/{config.iterations} successful")
            return result

        except Exception as e:
            logger.error(f"❌ Benchmark execution failed: {e}")
            raise

    async def _run_warm_up(self, config: BenchmarkConfig):
        """Run warm-up iterations"""
        for i in range(config.warm_up_iterations):
            try:
                await self._execute_benchmark_iteration(config, i, is_warmup=True)
                await asyncio.sleep(0.1)  # Brief delay between warm-up iterations
            except Exception as e:
                logger.debug(f"Warm-up iteration {i} failed: {e}")

    async def _execute_benchmark_iteration(
        self, config: BenchmarkConfig, iteration: int, is_warmup: bool = False
    ) -> dict[str, Any]:
        """Execute a single benchmark iteration"""
        iteration_start = time.time()

        # Select scenario-specific execution
        if config.scenario == BenchmarkScenario.SINGLE_AGENT_ANALYSIS:
            result = await self._benchmark_single_agent_analysis(config, iteration)
        elif config.scenario == BenchmarkScenario.MULTI_AGENT_COORDINATION:
            result = await self._benchmark_multi_agent_coordination(config, iteration)
        elif config.scenario == BenchmarkScenario.COMPLEX_REASONING:
            result = await self._benchmark_complex_reasoning(config, iteration)
        elif config.scenario == BenchmarkScenario.AUTONOMOUS_GOAL_FORMATION:
            result = await self._benchmark_autonomous_goal_formation(config, iteration)
        elif config.scenario == BenchmarkScenario.SAFETY_VALIDATION_STRESS:
            result = await self._benchmark_safety_validation_stress(config, iteration)
        elif config.scenario == BenchmarkScenario.HIGH_FREQUENCY_OPERATIONS:
            result = await self._benchmark_high_frequency_operations(config, iteration)
        elif config.scenario == BenchmarkScenario.MEMORY_INTENSIVE_TASKS:
            result = await self._benchmark_memory_intensive_tasks(config, iteration)
        elif config.scenario == BenchmarkScenario.TRINITY_COMPLIANCE_STRESS:
            result = await self._benchmark_trinity_compliance_stress(config, iteration)
        else:
            raise ValueError(f"Unknown benchmark scenario: {config.scenario}")

        iteration_duration = time.time() - iteration_start
        result["iteration_duration"] = iteration_duration
        result["iteration_number"] = iteration
        result["is_warmup"] = is_warmup

        return result

    async def _benchmark_single_agent_analysis(self, config: BenchmarkConfig, iteration: int) -> dict[str, Any]:
        """Benchmark single agent analysis performance"""
        start_time = time.time()

        # Create agent request
        request = await create_agent_request(
            agent_id=f"benchmark_agent_{iteration}",
            agent_type=AgentType.CONSCIOUSNESS_ARCHITECT,
            request_type=IntelligenceRequestType.META_COGNITIVE_ANALYSIS,
            payload={
                "request": f"Analyze system performance optimization strategy for iteration {iteration}",
                "context": {"iteration": iteration, "benchmark": True},
            },
            priority=5,
            timeout=config.timeout,
        )

        # Process request
        response = await self.agent_bridge.process_agent_request(request)

        processing_time = time.time() - start_time

        return {
            "response_time": processing_time,
            "success": response.success,
            "confidence": response.confidence or 0.0,
            "agent_type": "consciousness_architect",
            "intelligence_engine": "meta_cognitive",
            "payload_size": len(str(request.payload)),
        }

    async def _benchmark_multi_agent_coordination(self, config: BenchmarkConfig, iteration: int) -> dict[str, Any]:
        """Benchmark multi-agent coordination performance"""
        start_time = time.time()

        # Coordinate multiple agents
        from .orchestration_adapter import coordinate_agent_intelligence

        response = await coordinate_agent_intelligence(
            agent_type=AgentType.CONSCIOUSNESS_DEVELOPER,
            intelligence_request={
                "type": "multi_agent_coordination",
                "request": f"Coordinate implementation task for iteration {iteration}",
                "context": {
                    "iteration": iteration,
                    "agents": ["architect", "developer", "guardian"],
                },
            },
            orchestration_context={
                "coordination_level": "high",
                "priority": "benchmark",
            },
        )

        processing_time = time.time() - start_time

        return {
            "response_time": processing_time,
            "success": True,
            "confidence": response.get("confidence", 0.8),
            "coordination_complexity": "multi_agent",
            "agents_involved": 3,
            "orchestration_effects": len(response.get("symbolic_effects", [])),
        }

    async def _benchmark_complex_reasoning(self, config: BenchmarkConfig, iteration: int) -> dict[str, Any]:
        """Benchmark complex reasoning performance"""
        start_time = time.time()

        request = await create_agent_request(
            agent_id=f"reasoning_agent_{iteration}",
            agent_type=AgentType.CONSCIOUSNESS_ARCHITECT,
            request_type=IntelligenceRequestType.DIMENSIONAL_ANALYSIS,
            payload={
                "problem": {
                    "technical": {"complexity": "high", "iteration": iteration},
                    "cognitive": {"reasoning_depth": "complex"},
                    "temporal": {"urgency": "medium"},
                    "social": {"stakeholder_impact": "high"},
                    "ethical": {"compliance_requirements": "strict"},
                }
            },
            priority=7,
            timeout=config.timeout,
        )

        response = await self.agent_bridge.process_agent_request(request)
        processing_time = time.time() - start_time

        return {
            "response_time": processing_time,
            "success": response.success,
            "confidence": response.confidence or 0.0,
            "reasoning_complexity": "dimensional_analysis",
            "dimensions_analyzed": 5,
            "intelligence_engine": "dimensional",
        }

    async def _benchmark_autonomous_goal_formation(self, config: BenchmarkConfig, iteration: int) -> dict[str, Any]:
        """Benchmark autonomous goal formation performance"""
        start_time = time.time()

        request = AgentRequest(
            agent_id=f"autonomy_test_{iteration}",
            task_type=AgentTaskType.AUTONOMOUS_GOAL_FORMATION,
            data={
                "request": f"Form autonomous goals for performance optimization iteration {iteration}",
                "meta_analysis": {"complexity": "high", "priority": "optimization"},
                "subsystem_responses": {"performance": {"current": 0.8, "target": 0.95}},
            },
            priority=6,
            timeout=config.timeout,
        )

        response = await self.agent_bridge.process_agent_request(request)
        processing_time = time.time() - start_time

        # Validate with safety system
        safety_start = time.time()
        from .safety_validator import validate_operation

        safety_response = await validate_operation(
            operation_id=f"goal_formation_{iteration}",
            agent_id=f"goal_agent_{iteration}",
            intelligence_engine="autonomous_goals",
            operation_type="autonomous_goal_formation",
            payload=request.payload,
            safety_level=config.safety_level,
        )
        safety_time = time.time() - safety_start

        return {
            "response_time": processing_time,
            "success": response.success,
            "confidence": response.confidence or 0.0,
            "safety_validation_time": safety_time,
            "safety_score": safety_response.safety_score,
            "safety_result": safety_response.result.value,
            "goals_formed": (len(response.result.get("goals", [])) if response.result else 0),
            "intelligence_engine": "autonomous_goals",
        }

    async def _benchmark_safety_validation_stress(self, config: BenchmarkConfig, iteration: int) -> dict[str, Any]:
        """Benchmark safety validation under stress"""
        start_time = time.time()

        # Create high-risk operation for safety validation
        from .safety_validator import validate_operation

        response = await validate_operation(
            operation_id=f"stress_test_{iteration}",
            agent_id=f"stress_agent_{iteration}",
            intelligence_engine="autonomous_goals",
            operation_type="high_risk_autonomous_operation",
            payload={
                "risk_level": "high",
                "autonomy_level": "full",
                "system_modifications": True,
                "iteration": iteration,
            },
            safety_level=SafetyLevel.CRITICAL,
            context={"stress_test": True, "benchmark": True},
        )

        processing_time = time.time() - start_time

        return {
            "response_time": processing_time,
            "success": response.result != "rejected",
            "safety_score": response.safety_score,
            "safety_result": response.result.value,
            "confidence": response.confidence,
            "validation_type": "critical_safety",
            "conditions_applied": len(response.conditions),
            "restrictions_applied": len(response.restrictions),
        }

    async def _benchmark_high_frequency_operations(self, config: BenchmarkConfig, iteration: int) -> dict[str, Any]:
        """Benchmark high-frequency operation performance"""
        start_time = time.time()

        # Execute rapid sequence of operations
        operations = []
        for i in range(10):  # 10 rapid operations per iteration
            request = await create_agent_request(
                agent_id=f"freq_agent_{iteration}_{i}",
                agent_type=AgentType.CONSCIOUSNESS_DEVELOPER,
                request_type=IntelligenceRequestType.META_COGNITIVE_ANALYSIS,
                payload={"request": f"Quick analysis {iteration}-{i}", "rapid": True},
                priority=3,
                timeout=5.0,
            )

            op_start = time.time()
            response = await self.agent_bridge.process_agent_request(request)
            op_time = time.time() - op_start

            operations.append(
                {
                    "success": response.success,
                    "time": op_time,
                    "confidence": response.confidence or 0.0,
                }
            )

        total_time = time.time() - start_time
        successful_ops = sum(1 for op in operations if op["success"])
        avg_op_time = statistics.mean([op["time"] for op in operations])

        return {
            "response_time": total_time,
            "success": successful_ops == len(operations),
            "operations_per_second": len(operations) / total_time,
            "average_operation_time": avg_op_time,
            "successful_operations": successful_ops,
            "total_operations": len(operations),
            "operation_type": "high_frequency",
        }

    async def _benchmark_memory_intensive_tasks(self, config: BenchmarkConfig, iteration: int) -> dict[str, Any]:
        """Benchmark memory-intensive task performance"""
        start_time = time.time()

        # Create large payload for memory testing
        large_payload = {
            "request": f"Process large dataset for iteration {iteration}",
            "data": [f"data_point_{i}" for i in range(1000)],  # Large dataset
            "context": {
                "memory_test": True,
                "iteration": iteration,
                "large_context": " ".join([f"context_{i}" for i in range(100)]),
            },
        }

        request = await create_agent_request(
            agent_id=f"memory_agent_{iteration}",
            agent_type=AgentType.CONSCIOUSNESS_DEVELOPER,
            request_type=IntelligenceRequestType.DIMENSIONAL_ANALYSIS,
            payload=large_payload,
            priority=5,
            timeout=config.timeout,
        )

        # Monitor memory before operation
        memory_before = psutil.virtual_memory().percent

        response = await self.agent_bridge.process_agent_request(request)

        # Monitor memory after operation
        memory_after = psutil.virtual_memory().percent
        processing_time = time.time() - start_time

        return {
            "response_time": processing_time,
            "success": response.success,
            "confidence": response.confidence or 0.0,
            "memory_usage_delta": memory_after - memory_before,
            "payload_size": len(str(large_payload)),
            "memory_before": memory_before,
            "memory_after": memory_after,
            "task_type": "memory_intensive",
        }

    async def _benchmark_trinity_compliance_stress(self, config: BenchmarkConfig, iteration: int) -> dict[str, Any]:
        """Benchmark Trinity Framework compliance under stress"""
        start_time = time.time()

        # Test Trinity compliance with challenging scenarios
        trinity_requests = [
            (
                "identity_preservation",
                "Preserve system identity while adapting to new requirements",
            ),
            (
                "consciousness_enhancement",
                "Enhance processing capabilities without losing core awareness",
            ),
            (
                "guardian_protection",
                "Implement safety measures while maintaining operational flexibility",
            ),
        ]

        trinity_scores = {"identity": [], "consciousness": [], "guardian": []}

        for component, test_request in trinity_requests:
            request = await create_agent_request(
                agent_id=f"trinity_agent_{iteration}_{component}",
                agent_type=AgentType.GUARDIAN_ENGINEER,
                request_type=IntelligenceRequestType.META_COGNITIVE_ANALYSIS,
                payload={
                    "request": test_request,
                    "trinity_focus": component,
                    "stress_test": True,
                },
                priority=8,
                timeout=config.timeout,
            )

            response = await self.agent_bridge.process_agent_request(request)

            # Simulate Trinity compliance scoring
            if component == "identity_preservation":
                trinity_scores["identity"].append(0.95 if response.success else 0.7)
            elif component == "consciousness_enhancement":
                trinity_scores["consciousness"].append(0.92 if response.success else 0.7)
            elif component == "guardian_protection":
                trinity_scores["guardian"].append(0.88 if response.success else 0.6)

        processing_time = time.time() - start_time

        # Record Trinity compliance
        if all(trinity_scores.values()):
            self.monitor.record_trinity_compliance(
                identity_score=statistics.mean(trinity_scores["identity"]),
                consciousness_score=statistics.mean(trinity_scores["consciousness"]),
                guardian_score=statistics.mean(trinity_scores["guardian"]),
                agent_id=f"trinity_stress_{iteration}",
            )

        return {
            "response_time": processing_time,
            "success": all(any(scores) for scores in trinity_scores.values()),
            "trinity_identity": (statistics.mean(trinity_scores["identity"]) if trinity_scores["identity"] else 0.0),
            "trinity_consciousness": (
                statistics.mean(trinity_scores["consciousness"]) if trinity_scores["consciousness"] else 0.0
            ),
            "trinity_guardian": (statistics.mean(trinity_scores["guardian"]) if trinity_scores["guardian"] else 0.0),
            "compliance_tests": len(trinity_requests),
            "test_type": "trinity_compliance_stress",
        }

    async def _process_iteration_result(
        self,
        result: dict[str, Any],
        metrics: dict[str, list[float]],
        agent_performance: dict[str, dict[str, Any]],
        intelligence_engine_performance: dict[str, dict[str, Any]],
        trinity_compliance_scores: list[float],
        safety_validation_results: list[dict[str, Any]],
    ):
        """Process and store results from a benchmark iteration"""

        # Store metrics
        for key, value in result.items():
            if isinstance(value, (int, float)):
                metrics[key].append(value)

        # Store agent performance
        agent_type = result.get("agent_type", "unknown")
        if agent_type not in agent_performance:
            agent_performance[agent_type] = {
                "operations": 0,
                "total_time": 0.0,
                "successes": 0,
            }

        agent_performance[agent_type]["operations"] += 1
        agent_performance[agent_type]["total_time"] += result.get("response_time", 0.0)
        if result.get("success", False):
            agent_performance[agent_type]["successes"] += 1

        # Store intelligence engine performance
        engine = result.get("intelligence_engine", "unknown")
        if engine not in intelligence_engine_performance:
            intelligence_engine_performance[engine] = {
                "operations": 0,
                "total_time": 0.0,
                "successes": 0,
            }

        intelligence_engine_performance[engine]["operations"] += 1
        intelligence_engine_performance[engine]["total_time"] += result.get("response_time", 0.0)
        if result.get("success", False):
            intelligence_engine_performance[engine]["successes"] += 1

        # Store Trinity compliance scores
        if "trinity_identity" in result and "trinity_consciousness" in result and "trinity_guardian" in result:
            trinity_overall = (
                result["trinity_identity"] + result["trinity_consciousness"] + result["trinity_guardian"]
            ) / 3
            trinity_compliance_scores.append(trinity_overall)

        # Store safety validation results
        if "safety_score" in result:
            safety_validation_results.append(
                {
                    "safety_score": result["safety_score"],
                    "safety_result": result.get("safety_result", "unknown"),
                    "validation_time": result.get("safety_validation_time", 0.0),
                }
            )

    async def _capture_system_metrics(self) -> dict[str, float]:
        """Capture current system metrics"""
        return {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage("/").percent,
            "timestamp": time.time(),
        }

    async def _calculate_system_metrics_delta(
        self, initial: dict[str, float], final: dict[str, float]
    ) -> dict[str, float]:
        """Calculate system metrics delta"""
        return {
            "cpu_usage_delta": final["cpu_percent"] - initial["cpu_percent"],
            "memory_usage_delta": final["memory_percent"] - initial["memory_percent"],
            "disk_usage_delta": final["disk_percent"] - initial["disk_percent"],
            "duration": final["timestamp"] - initial["timestamp"],
        }

    async def _calculate_statistics(self, metrics: dict[str, list[float]]) -> dict[str, dict[str, float]]:
        """Calculate statistical analysis of metrics"""
        stats = {}

        for metric_name, values in metrics.items():
            if not values:
                continue

            stats[metric_name] = {
                "mean": statistics.mean(values),
                "median": statistics.median(values),
                "min": min(values),
                "max": max(values),
                "std_dev": statistics.stdev(values) if len(values) > 1 else 0.0,
                "p95": self._percentile(values, 95),
                "p99": self._percentile(values, 99),
                "count": len(values),
            }

        return stats

    def _percentile(self, values: list[float], percentile: float) -> float:
        """Calculate percentile of values"""
        if not values:
            return 0.0
        sorted_values = sorted(values)
        index = (percentile / 100) * (len(sorted_values) - 1)
        lower_index = int(index)
        upper_index = min(lower_index + 1, len(sorted_values) - 1)
        weight = index - lower_index
        return sorted_values[lower_index] * (1 - weight) + sorted_values[upper_index] * weight

    async def _generate_recommendations(
        self,
        statistics: dict[str, dict[str, float]],
        system_metrics: dict[str, float],
        config: BenchmarkConfig,
    ) -> list[str]:
        """Generate optimization recommendations based on benchmark results"""
        recommendations = []

        # Response time recommendations
        if "response_time" in statistics:
            mean_response = statistics["response_time"]["mean"]
            target_response = self.performance_targets["response_time"]

            if mean_response > target_response * 2:
                recommendations.append(
                    f"Critical: Response time ({mean_response:.3f}s) is {mean_response / target_response:.1f}x target. Consider performance optimization."
                )
            elif mean_response > target_response:
                recommendations.append(
                    f"Warning: Response time ({mean_response:.3f}s) exceeds target. Consider optimization."
                )

        # Success rate recommendations
        if "success" in statistics:
            success_rate = statistics["success"]["mean"]
            target_success = self.performance_targets["success_rate"]

            if success_rate < target_success:
                recommendations.append(
                    f"Error handling: Success rate ({success_rate:.1%}) below target ({target_success:.1%}). Review error handling."
                )

        # System resource recommendations
        if system_metrics.get("cpu_usage_delta", 0) > 20:
            recommendations.append("High CPU usage detected. Consider optimizing computational intensity.")

        if system_metrics.get("memory_usage_delta", 0) > 20:
            recommendations.append("High memory usage detected. Consider optimizing memory allocation.")

        # Agent coordination recommendations
        if config.scenario == BenchmarkScenario.MULTI_AGENT_COORDINATION:
            if "coordination_complexity" in statistics:
                recommendations.append("Multi-agent coordination detected. Consider agent load balancing.")

        # Safety recommendations
        if "safety_score" in statistics:
            avg_safety = statistics["safety_score"]["mean"]
            target_safety = self.performance_targets["safety_score"]

            if avg_safety < target_safety:
                recommendations.append(
                    f"Safety: Average safety score ({avg_safety:.2f}) below target. Review safety protocols."
                )

        # General performance recommendations
        if not recommendations:
            recommendations.append(
                "Performance within acceptable ranges. Consider advanced optimizations for further improvements."
            )

        return recommendations

    async def generate_performance_report(self, include_comparisons: bool = True) -> dict[str, Any]:
        """Generate comprehensive performance report"""
        if not self.benchmark_results:
            return {"error": "No benchmark results available"}

        latest_result = self.benchmark_results[-1]

        report = {
            "summary": {
                "total_benchmarks": len(self.benchmark_results),
                "latest_benchmark": latest_result.to_dict(),
                "performance_targets": self.performance_targets,
            },
            "performance_analysis": {},
            "trends": {},
            "recommendations": latest_result.recommendations,
        }

        # Performance analysis
        if latest_result.statistics:
            report["performance_analysis"] = {
                "response_time": {
                    "current": latest_result.statistics.get("response_time", {}).get("mean", 0),
                    "target": self.performance_targets["response_time"],
                    "status": (
                        "excellent"
                        if latest_result.statistics.get("response_time", {}).get("mean", 999)
                        < self.performance_targets["response_time"]
                        else "needs_improvement"
                    ),
                },
                "success_rate": {
                    "current": latest_result.statistics.get("success", {}).get("mean", 0),
                    "target": self.performance_targets["success_rate"],
                    "status": (
                        "excellent"
                        if latest_result.statistics.get("success", {}).get("mean", 0)
                        >= self.performance_targets["success_rate"]
                        else "needs_improvement"
                    ),
                },
            }

        # Trend analysis
        if len(self.benchmark_results) > 1:
            report["trends"] = await self._analyze_performance_trends()

        # Comparisons with baselines
        if include_comparisons and self.baseline_metrics:
            report["comparisons"] = await self._compare_with_baselines(latest_result)

        return report

    async def _analyze_performance_trends(self) -> dict[str, Any]:
        """Analyze performance trends across benchmark results"""
        if len(self.benchmark_results) < 2:
            return {}

        trends = {}

        # Analyze response time trends
        response_times = []
        for result in self.benchmark_results[-10:]:  # Last 10 results
            if "response_time" in result.statistics:
                response_times.append(result.statistics["response_time"]["mean"])

        if len(response_times) >= 2:
            trend_direction = "improving" if response_times[-1] < response_times[0] else "degrading"
            trends["response_time"] = {
                "direction": trend_direction,
                "change_percent": ((response_times[-1] - response_times[0]) / response_times[0]) * 100,
            }

        return trends

    async def _compare_with_baselines(self, result: BenchmarkResult) -> dict[str, Any]:
        """Compare current results with baseline metrics"""
        comparisons = {}

        for metric_name, baseline_value in self.baseline_metrics.items():
            if metric_name in result.statistics:
                current_value = result.statistics[metric_name]["mean"]
                improvement = ((baseline_value - current_value) / baseline_value) * 100
                comparisons[metric_name] = {
                    "baseline": baseline_value,
                    "current": current_value,
                    "improvement_percent": improvement,
                    "status": "improved" if improvement > 0 else "degraded",
                }

        return comparisons

    def set_baseline_metrics(self, metrics: dict[str, float]):
        """Set baseline metrics for comparison"""
        self.baseline_metrics = metrics
        logger.info(f"✅ Baseline metrics set: {list(metrics.keys())}")

    async def export_benchmark_results(self, file_path: str):
        """Export benchmark results to file"""
        export_data = {
            "export_timestamp": datetime.now(timezone.utc).isoformat(),
            "performance_targets": self.performance_targets,
            "baseline_metrics": self.baseline_metrics,
            "benchmark_results": [result.to_dict() for result in self.benchmark_results],
        }

        with open(file_path, "w") as f:
            json.dump(export_data, f, indent=2)

        logger.info(f"📊 Benchmark results exported to {file_path}")


# Global benchmarking instance
_benchmarking_instance = None


async def get_benchmarking_system() -> LukhasIntelligenceBenchmarking:
    """Get the global benchmarking system instance"""
    global _benchmarking_instance
    if _benchmarking_instance is None:
        _benchmarking_instance = LukhasIntelligenceBenchmarking()
        await _benchmarking_instance.initialize()
    return _benchmarking_instance


# Convenience functions
async def run_quick_benchmark(scenario: BenchmarkScenario, iterations: int = 10) -> BenchmarkResult:
    """Run a quick benchmark with default settings"""
    benchmarking = await get_benchmarking_system()

    config = BenchmarkConfig(
        scenario=scenario,
        benchmark_type=BenchmarkType.PERFORMANCE,
        iterations=iterations,
        warm_up_iterations=2,
        cool_down_delay=0.1,
    )

    return await benchmarking.run_benchmark(config)


async def run_comprehensive_benchmark() -> list[BenchmarkResult]:
    """Run comprehensive benchmarks across all scenarios"""
    benchmarking = await get_benchmarking_system()
    results = []

    scenarios = [
        BenchmarkScenario.SINGLE_AGENT_ANALYSIS,
        BenchmarkScenario.MULTI_AGENT_COORDINATION,
        BenchmarkScenario.COMPLEX_REASONING,
        BenchmarkScenario.AUTONOMOUS_GOAL_FORMATION,
        BenchmarkScenario.SAFETY_VALIDATION_STRESS,
    ]

    for scenario in scenarios:
        config = BenchmarkConfig(
            scenario=scenario,
            benchmark_type=BenchmarkType.PERFORMANCE,
            iterations=20,
            warm_up_iterations=5,
        )

        result = await benchmarking.run_benchmark(config)
        results.append(result)

        # Brief pause between scenarios
        await asyncio.sleep(1)

    return results


if __name__ == "__main__":
    # Example usage and testing
    async def example_benchmarking():
        """Example of benchmarking system usage"""

        # Run quick benchmark
        print("🏁 Running quick benchmark...")
        result = await run_quick_benchmark(BenchmarkScenario.SINGLE_AGENT_ANALYSIS, iterations=5)

        print("📊 Benchmark Results:")
        print(f"Duration: {result.total_duration:.2f}s")
        print(f"Success Rate: {result.successful_iterations}/{result.iterations_completed}")
        print(f"Recommendations: {len(result.recommendations)}")

        for rec in result.recommendations:
            print(f"  • {rec}")

        # Generate performance report
        benchmarking = await get_benchmarking_system()
        report = await benchmarking.generate_performance_report()

        print("\n📈 Performance Report:")
        print(f"Total Benchmarks: {report['summary']['total_benchmarks']}")
        print(f"Performance Analysis: {len(report.get('performance_analysis', {}))}")

    # Run example
    asyncio.run(example_benchmarking())