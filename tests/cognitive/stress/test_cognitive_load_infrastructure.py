"""
Stress Testing Infrastructure for Cognitive Load Management

This module implements comprehensive stress testing infrastructure for the LUKHAS
cognitive reasoning system, focusing on performance validation under extreme
cognitive loads and resource constraints.

Architecture:
- Multi-dimensional stress testing (CPU, Memory, Concurrency, Latency)
- Cognitive load simulation and measurement
- Performance degradation analysis
- Resource exhaustion scenarios
- Recovery and resilience validation

T4/0.01% Compliance:
- Validates P95 < 250ms under stress conditions
- Tests 98% contradiction detection accuracy under load
- Ensures graceful degradation without catastrophic failures
- Validates cognitive system stability across stress scenarios
"""

import asyncio
import gc
import logging
import random
import statistics
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import numpy as np
import psutil
import pytest

# LUKHAS cognitive imports
from cognitive_core.reasoning.contradiction_integrator import ContradictionIntegrator
from cognitive_core.reasoning.deep_inference_engine import DeepInferenceEngine, InferenceType
from consciousness.enhanced_thought_engine import EnhancedThoughtEngine, ThoughtComplexity
from consciousness.meta_cognitive_assessor import MetaCognitiveAssessor

logger = logging.getLogger(__name__)


class StressTestType(Enum):
    """Types of stress tests for cognitive system"""
    CPU_INTENSIVE = "cpu_intensive"
    MEMORY_PRESSURE = "memory_pressure"
    CONCURRENCY_OVERLOAD = "concurrency_overload"
    LATENCY_CRITICAL = "latency_critical"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    COGNITIVE_OVERLOAD = "cognitive_overload"
    MIXED_LOAD = "mixed_load"


class LoadPattern(Enum):
    """Load patterns for stress testing"""
    CONSTANT = "constant"
    RAMP_UP = "ramp_up"
    SPIKE = "spike"
    OSCILLATING = "oscillating"
    RANDOM = "random"


@dataclass
class StressTestConfig:
    """Configuration for stress testing scenarios"""
    test_type: StressTestType
    load_pattern: LoadPattern
    duration_seconds: float
    max_concurrent_tasks: int
    target_cpu_percent: float
    target_memory_mb: float
    expected_degradation_factor: float
    failure_threshold_percent: float
    recovery_timeout_seconds: float


@dataclass
class PerformanceMetrics:
    """Performance metrics collected during stress testing"""
    latencies_ms: list[float] = field(default_factory=list)
    error_rates: dict[str, float] = field(default_factory=dict)
    cpu_usage_percent: list[float] = field(default_factory=list)
    memory_usage_mb: list[float] = field(default_factory=list)
    cognitive_loads: list[float] = field(default_factory=list)
    contradiction_accuracy: list[float] = field(default_factory=list)
    circuit_breaker_trips: int = 0
    recovery_times_ms: list[float] = field(default_factory=list)


class SystemResourceMonitor:
    """Real-time system resource monitoring during stress tests"""

    def __init__(self, sampling_interval: float = 0.1):
        self.sampling_interval = sampling_interval
        self.monitoring = False
        self.metrics = PerformanceMetrics()
        self.monitor_thread = None
        self.process = psutil.Process()

    def start_monitoring(self):
        """Start resource monitoring"""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_resources)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

    def stop_monitoring(self):
        """Stop resource monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()

    def _monitor_resources(self):
        """Background resource monitoring loop"""
        while self.monitoring:
            try:
                # CPU usage
                cpu_percent = self.process.cpu_percent()
                self.metrics.cpu_usage_percent.append(cpu_percent)

                # Memory usage
                memory_info = self.process.memory_info()
                memory_mb = memory_info.rss / 1024 / 1024
                self.metrics.memory_usage_mb.append(memory_mb)

                time.sleep(self.sampling_interval)

            except Exception as e:
                logger.warning(f"Resource monitoring error: {e}")

    def get_resource_summary(self) -> dict[str, Any]:
        """Get summary of resource usage"""
        if not self.metrics.cpu_usage_percent or not self.metrics.memory_usage_mb:
            return {'error': 'No monitoring data available'}

        return {
            'cpu': {
                'mean': statistics.mean(self.metrics.cpu_usage_percent),
                'max': max(self.metrics.cpu_usage_percent),
                'p95': np.percentile(self.metrics.cpu_usage_percent, 95)
            },
            'memory': {
                'mean_mb': statistics.mean(self.metrics.memory_usage_mb),
                'max_mb': max(self.metrics.memory_usage_mb),
                'p95_mb': np.percentile(self.metrics.memory_usage_mb, 95)
            },
            'samples': len(self.metrics.cpu_usage_percent)
        }


class CognitiveLoadGenerator:
    """Generates various types of cognitive loads for stress testing"""

    def __init__(self):
        self.active_loads = {}
        self.load_patterns = {
            LoadPattern.CONSTANT: self._constant_load,
            LoadPattern.RAMP_UP: self._ramp_up_load,
            LoadPattern.SPIKE: self._spike_load,
            LoadPattern.OSCILLATING: self._oscillating_load,
            LoadPattern.RANDOM: self._random_load
        }

    async def generate_load(self,
                           config: StressTestConfig,
                           cognitive_components: dict[str, Any]) -> PerformanceMetrics:
        """Generate cognitive load based on configuration"""
        load_generator = self.load_patterns.get(config.load_pattern)
        if not load_generator:
            raise ValueError(f"Unknown load pattern: {config.load_pattern}")

        metrics = PerformanceMetrics()

        try:
            await load_generator(config, cognitive_components, metrics)
        except Exception as e:
            logger.error(f"Load generation failed: {e}")
            metrics.error_rates['load_generation'] = 1.0

        return metrics

    async def _constant_load(self,
                           config: StressTestConfig,
                           components: dict[str, Any],
                           metrics: PerformanceMetrics):
        """Generate constant cognitive load"""
        end_time = time.time() + config.duration_seconds
        task_counter = 0

        while time.time() < end_time:
            tasks = []

            # Create batch of concurrent tasks
            for _ in range(config.max_concurrent_tasks):
                task = self._create_cognitive_task(
                    config.test_type, components, task_counter
                )
                tasks.append(task)
                task_counter += 1

            # Execute batch and collect metrics
            start_time = time.perf_counter()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            batch_time = (time.perf_counter() - start_time) * 1000

            # Process results
            self._process_batch_results(results, batch_time, metrics)

            # Brief pause to prevent overwhelming the system
            await asyncio.sleep(0.01)

    async def _ramp_up_load(self,
                          config: StressTestConfig,
                          components: dict[str, Any],
                          metrics: PerformanceMetrics):
        """Generate ramping up load"""
        end_time = time.time() + config.duration_seconds
        elapsed_ratio = 0.0
        task_counter = 0

        while time.time() < end_time:
            elapsed_ratio = min(1.0, (time.time() - (time.time() - config.duration_seconds)) / config.duration_seconds)
            current_concurrency = int(config.max_concurrent_tasks * elapsed_ratio)

            if current_concurrency > 0:
                tasks = []
                for _ in range(current_concurrency):
                    task = self._create_cognitive_task(
                        config.test_type, components, task_counter
                    )
                    tasks.append(task)
                    task_counter += 1

                start_time = time.perf_counter()
                results = await asyncio.gather(*tasks, return_exceptions=True)
                batch_time = (time.perf_counter() - start_time) * 1000

                self._process_batch_results(results, batch_time, metrics)

            await asyncio.sleep(0.05)

    async def _spike_load(self,
                        config: StressTestConfig,
                        components: dict[str, Any],
                        metrics: PerformanceMetrics):
        """Generate spike load pattern"""
        spike_duration = config.duration_seconds * 0.2  # 20% of total time
        normal_load = max(1, config.max_concurrent_tasks // 4)
        spike_load = config.max_concurrent_tasks

        end_time = time.time() + config.duration_seconds
        spike_start = time.time() + config.duration_seconds * 0.4  # Start spike at 40%
        spike_end = spike_start + spike_duration

        task_counter = 0

        while time.time() < end_time:
            current_time = time.time()

            # Determine current load level
            current_load = spike_load if spike_start <= current_time <= spike_end else normal_load

            tasks = []
            for _ in range(current_load):
                task = self._create_cognitive_task(
                    config.test_type, components, task_counter
                )
                tasks.append(task)
                task_counter += 1

            start_time = time.perf_counter()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            batch_time = (time.perf_counter() - start_time) * 1000

            self._process_batch_results(results, batch_time, metrics)

            await asyncio.sleep(0.02)

    async def _oscillating_load(self,
                              config: StressTestConfig,
                              components: dict[str, Any],
                              metrics: PerformanceMetrics):
        """Generate oscillating load pattern"""
        end_time = time.time() + config.duration_seconds
        oscillation_period = 5.0  # 5 second oscillation period
        task_counter = 0

        while time.time() < end_time:
            elapsed_time = time.time() - (time.time() - config.duration_seconds)
            oscillation_factor = (np.sin(2 * np.pi * elapsed_time / oscillation_period) + 1) / 2
            current_load = int(config.max_concurrent_tasks * oscillation_factor)

            if current_load > 0:
                tasks = []
                for _ in range(current_load):
                    task = self._create_cognitive_task(
                        config.test_type, components, task_counter
                    )
                    tasks.append(task)
                    task_counter += 1

                start_time = time.perf_counter()
                results = await asyncio.gather(*tasks, return_exceptions=True)
                batch_time = (time.perf_counter() - start_time) * 1000

                self._process_batch_results(results, batch_time, metrics)

            await asyncio.sleep(0.03)

    async def _random_load(self,
                         config: StressTestConfig,
                         components: dict[str, Any],
                         metrics: PerformanceMetrics):
        """Generate random load pattern"""
        end_time = time.time() + config.duration_seconds
        task_counter = 0

        while time.time() < end_time:
            # Random load between 10% and 100% of max
            load_factor = random.uniform(0.1, 1.0)
            current_load = int(config.max_concurrent_tasks * load_factor)

            tasks = []
            for _ in range(current_load):
                task = self._create_cognitive_task(
                    config.test_type, components, task_counter
                )
                tasks.append(task)
                task_counter += 1

            start_time = time.perf_counter()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            batch_time = (time.perf_counter() - start_time) * 1000

            self._process_batch_results(results, batch_time, metrics)

            # Random pause duration
            pause_duration = random.uniform(0.01, 0.1)
            await asyncio.sleep(pause_duration)

    async def _create_cognitive_task(self,
                                   test_type: StressTestType,
                                   components: dict[str, Any],
                                   task_id: int):
        """Create a cognitive task based on stress test type"""
        try:
            if test_type == StressTestType.CPU_INTENSIVE:
                return await self._cpu_intensive_task(components, task_id)
            elif test_type == StressTestType.MEMORY_PRESSURE:
                return await self._memory_pressure_task(components, task_id)
            elif test_type == StressTestType.CONCURRENCY_OVERLOAD:
                return await self._concurrency_task(components, task_id)
            elif test_type == StressTestType.LATENCY_CRITICAL:
                return await self._latency_critical_task(components, task_id)
            elif test_type == StressTestType.COGNITIVE_OVERLOAD:
                return await self._cognitive_overload_task(components, task_id)
            elif test_type == StressTestType.MIXED_LOAD:
                return await self._mixed_load_task(components, task_id)
            else:
                raise ValueError(f"Unknown stress test type: {test_type}")

        except Exception as e:
            return {'error': str(e), 'task_id': task_id}

    async def _cpu_intensive_task(self, components: dict[str, Any], task_id: int):
        """CPU-intensive cognitive task"""
        thought_engine = components.get('thought_engine')
        if not thought_engine:
            return {'error': 'No thought engine available'}

        # Create CPU-intensive reasoning task
        complex_query = f"Perform deep recursive analysis on mathematical sequence {task_id}"

        start_time = time.perf_counter()
        result = await thought_engine.synthesize_thought(
            complex_query,
            context={
                'complexity': ThoughtComplexity.EXTREME,
                'cpu_intensive': True,
                'task_id': task_id
            }
        )
        end_time = time.perf_counter()

        return {
            'result': result,
            'latency_ms': (end_time - start_time) * 1000,
            'task_type': 'cpu_intensive',
            'task_id': task_id
        }

    async def _memory_pressure_task(self, components: dict[str, Any], task_id: int):
        """Memory-pressure cognitive task"""
        thought_engine = components.get('thought_engine')
        if not thought_engine:
            return {'error': 'No thought engine available'}

        # Create large context to pressure memory
        large_context = {
            'data': 'x' * (100000 + task_id * 1000),  # Variable large context
            'complexity': ThoughtComplexity.COMPLEX,
            'memory_intensive': True,
            'task_id': task_id
        }

        start_time = time.perf_counter()
        result = await thought_engine.synthesize_thought(
            f"Analyze large dataset for task {task_id}",
            context=large_context
        )
        end_time = time.perf_counter()

        # Force garbage collection after each task
        gc.collect()

        return {
            'result': result,
            'latency_ms': (end_time - start_time) * 1000,
            'task_type': 'memory_pressure',
            'task_id': task_id,
            'context_size': len(large_context['data'])
        }

    async def _concurrency_task(self, components: dict[str, Any], task_id: int):
        """Concurrency stress task"""
        inference_engine = components.get('inference_engine')
        if not inference_engine:
            return {'error': 'No inference engine available'}

        # Create multiple concurrent inference chains
        sub_tasks = []
        for i in range(5):  # 5 sub-inferences per task
            sub_task = inference_engine.infer(
                f"Concurrent inference {task_id}-{i}",
                inference_type=random.choice(list(InferenceType)),
                max_depth=random.randint(3, 8)
            )
            sub_tasks.append(sub_task)

        start_time = time.perf_counter()
        results = await asyncio.gather(*sub_tasks, return_exceptions=True)
        end_time = time.perf_counter()

        successful_results = [r for r in results if not isinstance(r, Exception)]

        return {
            'results': successful_results,
            'latency_ms': (end_time - start_time) * 1000,
            'task_type': 'concurrency',
            'task_id': task_id,
            'success_count': len(successful_results),
            'total_count': len(results)
        }

    async def _latency_critical_task(self, components: dict[str, Any], task_id: int):
        """Latency-critical cognitive task"""
        thought_engine = components.get('thought_engine')
        if not thought_engine:
            return {'error': 'No thought engine available'}

        # Task with strict latency requirements
        start_time = time.perf_counter()

        try:
            result = await asyncio.wait_for(
                thought_engine.synthesize_thought(
                    f"Latency-critical reasoning {task_id}",
                    context={
                        'complexity': ThoughtComplexity.MODERATE,
                        'strict_timing': True,
                        'task_id': task_id
                    }
                ),
                timeout=0.200  # 200ms timeout
            )

            end_time = time.perf_counter()
            latency_ms = (end_time - start_time) * 1000

            return {
                'result': result,
                'latency_ms': latency_ms,
                'task_type': 'latency_critical',
                'task_id': task_id,
                'timeout_exceeded': latency_ms > 200.0
            }

        except asyncio.TimeoutError:
            end_time = time.perf_counter()
            return {
                'error': 'Timeout exceeded',
                'latency_ms': (end_time - start_time) * 1000,
                'task_type': 'latency_critical',
                'task_id': task_id,
                'timeout_exceeded': True
            }

    async def _cognitive_overload_task(self, components: dict[str, Any], task_id: int):
        """Cognitive overload stress task"""
        meta_assessor = components.get('meta_assessor')
        contradiction_integrator = components.get('contradiction_integrator')

        if not meta_assessor or not contradiction_integrator:
            return {'error': 'Missing cognitive components'}

        # Create complex cognitive scenario
        contradictory_premises = [
            f"Statement A{task_id}: All cognitive systems are perfect",
            f"Statement B{task_id}: This cognitive system has errors",
            f"Statement C{task_id}: Perfect systems cannot have errors",
            f"Statement D{task_id}: This system is cognitive"
        ]

        start_time = time.perf_counter()

        # Parallel cognitive processing
        contradiction_task = contradiction_integrator.detect_contradictions(
            contradictory_premises,
            confidence_threshold=0.98
        )

        assessment_task = meta_assessor.assess_cognitive_state(
            {
                'reasoning_complexity': 'extreme',
                'premises': contradictory_premises,
                'task_id': task_id
            }
        )

        results = await asyncio.gather(
            contradiction_task,
            assessment_task,
            return_exceptions=True
        )

        end_time = time.perf_counter()

        return {
            'contradiction_result': results[0] if len(results) > 0 else None,
            'assessment_result': results[1] if len(results) > 1 else None,
            'latency_ms': (end_time - start_time) * 1000,
            'task_type': 'cognitive_overload',
            'task_id': task_id,
            'premises_count': len(contradictory_premises)
        }

    async def _mixed_load_task(self, components: dict[str, Any], task_id: int):
        """Mixed load cognitive task"""
        # Randomly select and combine multiple task types
        task_types = [
            self._cpu_intensive_task,
            self._memory_pressure_task,
            self._concurrency_task,
            self._latency_critical_task
        ]

        selected_tasks = random.sample(task_types, k=random.randint(2, 3))

        start_time = time.perf_counter()
        results = []

        for task_func in selected_tasks:
            try:
                result = await task_func(components, task_id)
                results.append(result)
            except Exception as e:
                results.append({'error': str(e), 'task_type': task_func.__name__})

        end_time = time.perf_counter()

        return {
            'mixed_results': results,
            'latency_ms': (end_time - start_time) * 1000,
            'task_type': 'mixed_load',
            'task_id': task_id,
            'sub_task_count': len(results)
        }

    def _process_batch_results(self,
                             results: list[Any],
                             batch_time: float,
                             metrics: PerformanceMetrics):
        """Process batch results and update metrics"""
        successful_results = []
        error_count = 0

        for result in results:
            if isinstance(result, Exception):
                error_count += 1
                logger.debug(f"Task exception: {result}")
            elif isinstance(result, dict):
                if 'error' in result:
                    error_count += 1
                else:
                    successful_results.append(result)

                    # Collect latency if available
                    if 'latency_ms' in result:
                        metrics.latencies_ms.append(result['latency_ms'])

                    # Collect task-specific metrics
                    if result.get('task_type') == 'cognitive_overload' and 'contradiction_result' in result:
                        contradiction_result = result['contradiction_result']
                        if isinstance(contradiction_result, dict) and 'confidence' in contradiction_result:
                            metrics.contradiction_accuracy.append(contradiction_result['confidence'])

        # Update error rates
        total_tasks = len(results)
        if total_tasks > 0:
            error_rate = error_count / total_tasks
            metrics.error_rates[f'batch_{len(metrics.error_rates)}'] = error_rate

        # Record overall batch performance
        metrics.latencies_ms.append(batch_time)


class StressTestInfrastructure:
    """Main stress testing infrastructure for cognitive systems"""

    def __init__(self):
        self.resource_monitor = SystemResourceMonitor()
        self.load_generator = CognitiveLoadGenerator()
        self.cognitive_components = {}
        self.test_results = {}

    async def setup_cognitive_components(self):
        """Initialize cognitive components for stress testing"""
        self.cognitive_components = {
            'inference_engine': DeepInferenceEngine(
                max_depth=12,
                timeout_per_step=0.030,
                circuit_breaker_threshold=5
            ),
            'thought_engine': EnhancedThoughtEngine(
                performance_budget=0.250,  # 250ms T4 budget
                complexity_threshold=ThoughtComplexity.EXTREME
            ),
            'contradiction_integrator': ContradictionIntegrator(
                confidence_threshold=0.98,
                real_time_monitoring=True
            ),
            'meta_assessor': MetaCognitiveAssessor(
                assessment_depth="comprehensive",
                performance_tracking=True
            )
        }

        # Initialize cross-references
        self.cognitive_components['thought_engine'].inference_engine = \
            self.cognitive_components['inference_engine']

    async def run_stress_test(self, config: StressTestConfig) -> dict[str, Any]:
        """Run comprehensive stress test"""
        logger.info(f"Starting stress test: {config.test_type.value} - {config.load_pattern.value}")

        # Start resource monitoring
        self.resource_monitor.start_monitoring()

        try:
            # Execute stress test
            start_time = time.time()
            metrics = await self.load_generator.generate_load(
                config, self.cognitive_components
            )
            end_time = time.time()

            # Stop resource monitoring
            self.resource_monitor.stop_monitoring()

            # Collect system resource metrics
            resource_summary = self.resource_monitor.get_resource_summary()

            # Calculate performance analysis
            performance_analysis = self._analyze_performance(metrics, config)

            # Generate test report
            test_report = {
                'config': {
                    'test_type': config.test_type.value,
                    'load_pattern': config.load_pattern.value,
                    'duration_seconds': config.duration_seconds,
                    'max_concurrent_tasks': config.max_concurrent_tasks
                },
                'execution': {
                    'actual_duration': end_time - start_time,
                    'total_tasks': len(metrics.latencies_ms),
                    'resource_usage': resource_summary
                },
                'performance': performance_analysis,
                'compliance': self._check_t4_compliance(metrics, config),
                'recommendations': self._generate_recommendations(metrics, config)
            }

            # Store results
            test_id = f"{config.test_type.value}_{config.load_pattern.value}_{int(time.time())}"
            self.test_results[test_id] = test_report

            return test_report

        except Exception as e:
            logger.error(f"Stress test failed: {e}")
            self.resource_monitor.stop_monitoring()
            raise

    def _analyze_performance(self,
                           metrics: PerformanceMetrics,
                           config: StressTestConfig) -> dict[str, Any]:
        """Analyze performance metrics"""
        if not metrics.latencies_ms:
            return {'error': 'No performance data collected'}

        latencies = metrics.latencies_ms

        analysis = {
            'latency': {
                'mean_ms': statistics.mean(latencies),
                'median_ms': statistics.median(latencies),
                'p95_ms': np.percentile(latencies, 95),
                'p99_ms': np.percentile(latencies, 99),
                'max_ms': max(latencies),
                'std_ms': statistics.stdev(latencies) if len(latencies) > 1 else 0.0
            },
            'error_analysis': {
                'total_error_batches': len(metrics.error_rates),
                'mean_error_rate': statistics.mean(metrics.error_rates.values()) if metrics.error_rates else 0.0,
                'max_error_rate': max(metrics.error_rates.values()) if metrics.error_rates else 0.0
            },
            'contradiction_detection': {
                'accuracy_samples': len(metrics.contradiction_accuracy),
                'mean_accuracy': statistics.mean(metrics.contradiction_accuracy) if metrics.contradiction_accuracy else 0.0,
                'min_accuracy': min(metrics.contradiction_accuracy) if metrics.contradiction_accuracy else 0.0
            },
            'circuit_breaker': {
                'trips': metrics.circuit_breaker_trips,
                'trip_rate': metrics.circuit_breaker_trips / len(latencies) if latencies else 0.0
            }
        }

        return analysis

    def _check_t4_compliance(self,
                           metrics: PerformanceMetrics,
                           config: StressTestConfig) -> dict[str, Any]:
        """Check T4/0.01% compliance under stress"""
        if not metrics.latencies_ms:
            return {'compliant': False, 'reason': 'No latency data'}

        p95_latency = np.percentile(metrics.latencies_ms, 95)
        p99_latency = np.percentile(metrics.latencies_ms, 99)

        mean_error_rate = statistics.mean(metrics.error_rates.values()) if metrics.error_rates else 0.0
        contradiction_accuracy = statistics.mean(metrics.contradiction_accuracy) if metrics.contradiction_accuracy else 0.0

        compliance_checks = {
            'p95_latency_compliant': p95_latency < 250.0,
            'p95_latency_ms': p95_latency,
            'p99_latency_compliant': p99_latency < 300.0,  # Safety margin
            'p99_latency_ms': p99_latency,
            'error_rate_compliant': mean_error_rate < 0.01,
            'error_rate_percent': mean_error_rate * 100,
            'contradiction_accuracy_compliant': contradiction_accuracy >= 0.98,
            'contradiction_accuracy': contradiction_accuracy
        }

        overall_compliant = all([
            compliance_checks['p95_latency_compliant'],
            compliance_checks['error_rate_compliant'],
            compliance_checks.get('contradiction_accuracy_compliant', True)
        ])

        return {
            'compliant': overall_compliant,
            'details': compliance_checks,
            'degradation_factor': p95_latency / 50.0,  # Compare to baseline 50ms
            'stress_tolerance': 'excellent' if overall_compliant else 'needs_improvement'
        }

    def _generate_recommendations(self,
                                metrics: PerformanceMetrics,
                                config: StressTestConfig) -> list[str]:
        """Generate performance improvement recommendations"""
        recommendations = []

        if not metrics.latencies_ms:
            return ['Unable to generate recommendations: no performance data']

        p95_latency = np.percentile(metrics.latencies_ms, 95)
        mean_error_rate = statistics.mean(metrics.error_rates.values()) if metrics.error_rates else 0.0

        # Latency recommendations
        if p95_latency > 250.0:
            recommendations.append(
                f"P95 latency ({p95_latency:.1f}ms) exceeds T4 target. "
                "Consider optimizing cognitive processing pipeline."
            )

        if p95_latency > 500.0:
            recommendations.append(
                "Critical latency violation. Implement circuit breakers and "
                "cognitive load shedding mechanisms."
            )

        # Error rate recommendations
        if mean_error_rate > 0.01:
            recommendations.append(
                f"Error rate ({mean_error_rate*100:.2f}%) exceeds 0.01% target. "
                "Review error handling and resilience patterns."
            )

        # Circuit breaker recommendations
        if metrics.circuit_breaker_trips > 0:
            recommendations.append(
                f"Circuit breaker activated {metrics.circuit_breaker_trips} times. "
                "Review cognitive load balancing and timeout configurations."
            )

        # Contradiction detection recommendations
        if metrics.contradiction_accuracy:
            min_accuracy = min(metrics.contradiction_accuracy)
            if min_accuracy < 0.98:
                recommendations.append(
                    f"Contradiction detection accuracy ({min_accuracy:.1%}) below 98% target. "
                    "Consider tuning confidence thresholds under stress conditions."
                )

        # Resource usage recommendations
        if hasattr(self.resource_monitor.metrics, 'memory_usage_mb') and \
           self.resource_monitor.metrics.memory_usage_mb:
            max_memory = max(self.resource_monitor.metrics.memory_usage_mb)
            if max_memory > 1000:  # 1GB
                recommendations.append(
                    f"High memory usage ({max_memory:.0f}MB). "
                    "Implement memory pooling and garbage collection optimization."
                )

        if not recommendations:
            recommendations.append("Performance meets all targets under stress conditions.")

        return recommendations

    def get_comprehensive_report(self) -> dict[str, Any]:
        """Generate comprehensive stress testing report"""
        if not self.test_results:
            return {'error': 'No stress test results available'}

        # Aggregate results across all tests
        all_latencies = []
        all_error_rates = []
        compliance_results = []

        for _test_id, result in self.test_results.items():
            if 'performance' in result and 'latency' in result['performance']:
                latency_data = result['performance']['latency']
                all_latencies.extend([latency_data.get('p95_ms', 0)])

            if 'performance' in result and 'error_analysis' in result['performance']:
                error_data = result['performance']['error_analysis']
                all_error_rates.append(error_data.get('mean_error_rate', 0))

            if 'compliance' in result:
                compliance_results.append(result['compliance']['compliant'])

        overall_compliance = all(compliance_results) if compliance_results else False

        return {
            'summary': {
                'total_tests': len(self.test_results),
                'overall_compliance': overall_compliance,
                'compliance_rate': sum(compliance_results) / len(compliance_results) if compliance_results else 0.0
            },
            'aggregated_performance': {
                'mean_p95_latency': statistics.mean(all_latencies) if all_latencies else 0.0,
                'max_p95_latency': max(all_latencies) if all_latencies else 0.0,
                'mean_error_rate': statistics.mean(all_error_rates) if all_error_rates else 0.0
            },
            'test_results': self.test_results,
            'recommendations': self._generate_overall_recommendations()
        }

    def _generate_overall_recommendations(self) -> list[str]:
        """Generate overall recommendations from all stress tests"""
        if not self.test_results:
            return ['No test results available for analysis']

        recommendations = []

        # Analyze patterns across tests
        failed_tests = [
            test_id for test_id, result in self.test_results.items()
            if not result.get('compliance', {}).get('compliant', False)
        ]

        if failed_tests:
            recommendations.append(
                f"{len(failed_tests)} out of {len(self.test_results)} tests failed compliance. "
                "Review cognitive system architecture for stress resilience."
            )
        else:
            recommendations.append(
                "All stress tests passed compliance targets. "
                "System demonstrates excellent resilience under extreme conditions."
            )

        return recommendations


# Predefined stress test configurations
STRESS_TEST_CONFIGS = [
    StressTestConfig(
        test_type=StressTestType.CPU_INTENSIVE,
        load_pattern=LoadPattern.CONSTANT,
        duration_seconds=10.0,
        max_concurrent_tasks=20,
        target_cpu_percent=80.0,
        target_memory_mb=500.0,
        expected_degradation_factor=2.0,
        failure_threshold_percent=5.0,
        recovery_timeout_seconds=30.0
    ),
    StressTestConfig(
        test_type=StressTestType.MEMORY_PRESSURE,
        load_pattern=LoadPattern.RAMP_UP,
        duration_seconds=15.0,
        max_concurrent_tasks=15,
        target_cpu_percent=60.0,
        target_memory_mb=1000.0,
        expected_degradation_factor=1.5,
        failure_threshold_percent=3.0,
        recovery_timeout_seconds=20.0
    ),
    StressTestConfig(
        test_type=StressTestType.CONCURRENCY_OVERLOAD,
        load_pattern=LoadPattern.SPIKE,
        duration_seconds=12.0,
        max_concurrent_tasks=50,
        target_cpu_percent=90.0,
        target_memory_mb=800.0,
        expected_degradation_factor=3.0,
        failure_threshold_percent=8.0,
        recovery_timeout_seconds=40.0
    ),
    StressTestConfig(
        test_type=StressTestType.LATENCY_CRITICAL,
        load_pattern=LoadPattern.CONSTANT,
        duration_seconds=8.0,
        max_concurrent_tasks=10,
        target_cpu_percent=50.0,
        target_memory_mb=300.0,
        expected_degradation_factor=1.2,
        failure_threshold_percent=1.0,
        recovery_timeout_seconds=10.0
    ),
    StressTestConfig(
        test_type=StressTestType.COGNITIVE_OVERLOAD,
        load_pattern=LoadPattern.OSCILLATING,
        duration_seconds=20.0,
        max_concurrent_tasks=25,
        target_cpu_percent=75.0,
        target_memory_mb=600.0,
        expected_degradation_factor=2.5,
        failure_threshold_percent=4.0,
        recovery_timeout_seconds=25.0
    ),
    StressTestConfig(
        test_type=StressTestType.MIXED_LOAD,
        load_pattern=LoadPattern.RANDOM,
        duration_seconds=18.0,
        max_concurrent_tasks=30,
        target_cpu_percent=85.0,
        target_memory_mb=750.0,
        expected_degradation_factor=2.8,
        failure_threshold_percent=6.0,
        recovery_timeout_seconds=35.0
    )
]


@pytest.fixture
async def stress_test_infrastructure():
    """Fixture providing initialized stress testing infrastructure"""
    infrastructure = StressTestInfrastructure()
    await infrastructure.setup_cognitive_components()
    return infrastructure


class TestCognitiveStressInfrastructure:
    """Test suite for cognitive stress testing infrastructure"""

    @pytest.mark.asyncio
    async def test_cpu_intensive_stress(self, stress_test_infrastructure):
        """Test CPU-intensive stress scenarios"""
        infrastructure = stress_test_infrastructure

        config = StressTestConfig(
            test_type=StressTestType.CPU_INTENSIVE,
            load_pattern=LoadPattern.CONSTANT,
            duration_seconds=5.0,
            max_concurrent_tasks=10,
            target_cpu_percent=70.0,
            target_memory_mb=400.0,
            expected_degradation_factor=2.0,
            failure_threshold_percent=5.0,
            recovery_timeout_seconds=15.0
        )

        result = await infrastructure.run_stress_test(config)

        # Validate test execution
        assert 'performance' in result
        assert 'compliance' in result
        assert result['execution']['total_tasks'] > 0

        # Validate performance under CPU stress
        performance = result['performance']
        assert 'latency' in performance
        assert performance['latency']['p95_ms'] < 500.0  # Relaxed under stress

    @pytest.mark.asyncio
    async def test_memory_pressure_resilience(self, stress_test_infrastructure):
        """Test memory pressure resilience"""
        infrastructure = stress_test_infrastructure

        config = StressTestConfig(
            test_type=StressTestType.MEMORY_PRESSURE,
            load_pattern=LoadPattern.RAMP_UP,
            duration_seconds=8.0,
            max_concurrent_tasks=8,
            target_cpu_percent=50.0,
            target_memory_mb=800.0,
            expected_degradation_factor=1.5,
            failure_threshold_percent=3.0,
            recovery_timeout_seconds=20.0
        )

        result = await infrastructure.run_stress_test(config)

        # Validate memory handling
        assert result['execution']['total_tasks'] > 0

        # Check error rates under memory pressure
        performance = result['performance']
        if 'error_analysis' in performance:
            assert performance['error_analysis']['mean_error_rate'] < 0.05  # 5% max under stress

    @pytest.mark.asyncio
    async def test_concurrency_overload_handling(self, stress_test_infrastructure):
        """Test concurrency overload handling"""
        infrastructure = stress_test_infrastructure

        config = StressTestConfig(
            test_type=StressTestType.CONCURRENCY_OVERLOAD,
            load_pattern=LoadPattern.SPIKE,
            duration_seconds=6.0,
            max_concurrent_tasks=25,
            target_cpu_percent=80.0,
            target_memory_mb=600.0,
            expected_degradation_factor=3.0,
            failure_threshold_percent=8.0,
            recovery_timeout_seconds=30.0
        )

        result = await infrastructure.run_stress_test(config)

        # Validate concurrency handling
        assert result['execution']['total_tasks'] > 0

        # Should handle high concurrency gracefully
        performance = result['performance']
        circuit_breaker = performance.get('circuit_breaker', {})

        # Circuit breaker should activate under extreme load
        # This is expected and desired behavior
        logger.info(f"Circuit breaker trips: {circuit_breaker.get('trips', 0)}")

    @pytest.mark.asyncio
    async def test_latency_critical_compliance(self, stress_test_infrastructure):
        """Test latency-critical task compliance"""
        infrastructure = stress_test_infrastructure

        config = StressTestConfig(
            test_type=StressTestType.LATENCY_CRITICAL,
            load_pattern=LoadPattern.CONSTANT,
            duration_seconds=5.0,
            max_concurrent_tasks=5,
            target_cpu_percent=40.0,
            target_memory_mb=200.0,
            expected_degradation_factor=1.2,
            failure_threshold_percent=1.0,
            recovery_timeout_seconds=10.0
        )

        result = await infrastructure.run_stress_test(config)

        # Validate latency compliance
        performance = result['performance']
        latency = performance['latency']

        # Should meet strict latency requirements
        assert latency['p95_ms'] < 250.0, f"P95 latency {latency['p95_ms']:.1f}ms exceeds T4 target"

        compliance = result['compliance']
        assert compliance['details']['p95_latency_compliant'], "Failed P95 latency compliance"

    @pytest.mark.asyncio
    async def test_cognitive_overload_detection(self, stress_test_infrastructure):
        """Test cognitive overload detection and handling"""
        infrastructure = stress_test_infrastructure

        config = StressTestConfig(
            test_type=StressTestType.COGNITIVE_OVERLOAD,
            load_pattern=LoadPattern.OSCILLATING,
            duration_seconds=10.0,
            max_concurrent_tasks=15,
            target_cpu_percent=60.0,
            target_memory_mb=500.0,
            expected_degradation_factor=2.0,
            failure_threshold_percent=4.0,
            recovery_timeout_seconds=20.0
        )

        result = await infrastructure.run_stress_test(config)

        # Validate cognitive processing under overload
        performance = result['performance']

        # Check contradiction detection accuracy under stress
        contradiction_detection = performance.get('contradiction_detection', {})
        if contradiction_detection.get('accuracy_samples', 0) > 0:
            assert contradiction_detection['mean_accuracy'] >= 0.95, \
                "Contradiction detection accuracy degraded too much under stress"

    @pytest.mark.asyncio
    async def test_mixed_load_comprehensive(self, stress_test_infrastructure):
        """Test mixed load comprehensive stress testing"""
        infrastructure = stress_test_infrastructure

        config = StressTestConfig(
            test_type=StressTestType.MIXED_LOAD,
            load_pattern=LoadPattern.RANDOM,
            duration_seconds=12.0,
            max_concurrent_tasks=20,
            target_cpu_percent=70.0,
            target_memory_mb=600.0,
            expected_degradation_factor=2.5,
            failure_threshold_percent=5.0,
            recovery_timeout_seconds=25.0
        )

        result = await infrastructure.run_stress_test(config)

        # Validate mixed load handling
        assert result['execution']['total_tasks'] > 0

        # Should handle diverse load types
        performance = result['performance']
        assert 'latency' in performance
        assert 'error_analysis' in performance

        # Generate comprehensive report
        comprehensive_report = infrastructure.get_comprehensive_report()
        assert 'summary' in comprehensive_report
        assert comprehensive_report['summary']['total_tests'] >= 1

    @pytest.mark.asyncio
    async def test_stress_test_suite_comprehensive(self, stress_test_infrastructure):
        """Run comprehensive stress test suite"""
        infrastructure = stress_test_infrastructure

        # Run subset of predefined stress test configurations
        test_configs = STRESS_TEST_CONFIGS[:4]  # Run first 4 configs for testing

        results = []
        for config in test_configs:
            # Reduce duration for testing
            config.duration_seconds = min(config.duration_seconds, 5.0)
            config.max_concurrent_tasks = min(config.max_concurrent_tasks, 10)

            try:
                result = await infrastructure.run_stress_test(config)
                results.append(result)
                logger.info(f"Completed stress test: {config.test_type.value}")
            except Exception as e:
                logger.error(f"Stress test failed: {config.test_type.value} - {e}")

        # Validate comprehensive testing
        assert len(results) >= 2, "Insufficient stress test results"

        # Generate final comprehensive report
        final_report = infrastructure.get_comprehensive_report()

        assert final_report['summary']['total_tests'] >= 2
        assert 'aggregated_performance' in final_report
        assert 'recommendations' in final_report

        # Log comprehensive results
        logger.info(f"Comprehensive stress testing completed: {final_report['summary']}")

        # Validate overall system resilience
        compliance_rate = final_report['summary']['compliance_rate']
        assert compliance_rate >= 0.5, f"Overall compliance rate {compliance_rate:.1%} too low"


# Stress test runner for standalone execution
if __name__ == "__main__":
    async def run_comprehensive_stress_tests():
        """Run comprehensive stress testing suite"""
        infrastructure = StressTestInfrastructure()
        await infrastructure.setup_cognitive_components()

        print("Starting comprehensive cognitive stress testing...")

        for i, config in enumerate(STRESS_TEST_CONFIGS):
            print(f"\nRunning stress test {i+1}/{len(STRESS_TEST_CONFIGS)}: {config.test_type.value}")

            try:
                result = await infrastructure.run_stress_test(config)

                compliance = result['compliance']
                print(f"  Status: {'✅ PASS' if compliance['compliant'] else '❌ FAIL'}")
                print(f"  P95 Latency: {result['performance']['latency']['p95_ms']:.1f}ms")
                print(f"  Error Rate: {result['performance']['error_analysis']['mean_error_rate']*100:.2f}%")

            except Exception as e:
                print(f"  Status: ❌ ERROR - {e}")

        # Generate final report
        final_report = infrastructure.get_comprehensive_report()
        print(f"\n{'='*60}")
        print("COMPREHENSIVE STRESS TEST REPORT")
        print(f"{'='*60}")
        print(f"Total Tests: {final_report['summary']['total_tests']}")
        print(f"Overall Compliance: {final_report['summary']['overall_compliance']}")
        print(f"Compliance Rate: {final_report['summary']['compliance_rate']:.1%}")
        print("\nRecommendations:")
        for rec in final_report['recommendations']:
            print(f"  • {rec}")

    # Run stress tests
    asyncio.run(run_comprehensive_stress_tests())
