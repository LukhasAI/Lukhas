import logging

logger = logging.getLogger(__name__)
"""

#TAG:consciousness
#TAG:reflection
#TAG:neuroplastic
#TAG:colony


Circuit Breakers and Cascading Failure Prevention
Addresses TODO 172: Fault containment patterns for distributed systems

This module implements comprehensive circuit breaker patterns and cascading failure
prevention mechanisms to protect the distributed actor system from propagating errors
and system-wide collapse.
"""

import asyncio
import contextlib
import hashlib
import json
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional

import numpy as np

from core.common import get_logger

try:
    from .actor_system import ActorRef
except ImportError:
    # Create a minimal ActorRef type for typing purposes
    class ActorRef:
        pass


logger = get_logger(__name__)


class CircuitState(Enum):
    """States of a circuit breaker"""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Blocking calls
    HALF_OPEN = "half_open"  # Testing recovery
    FORCED_OPEN = "forced_open"  # Manually opened


class FailureType(Enum):
    """Types of failures that can occur"""

    TIMEOUT = "timeout"
    ERROR = "error"
    REJECTION = "rejection"
    RESOURCE_EXHAUSTED = "resource_exhausted"
    ANOMALY_DETECTED = "anomaly_detected"
    CONSENSUS_FAILURE = "consensus_failure"


@dataclass
class FailureRecord:
    """Record of a failure event"""

    timestamp: float
    failure_type: FailureType
    actor_id: str
    error_message: str
    correlation_id: Optional[str] = None
    propagation_path: list[str] = field(default_factory=list)
    severity: float = 1.0  # 0-1 scale


@dataclass
class HealthCheck:
    """Health check configuration"""

    check_function: Callable
    interval: float = 30.0
    timeout: float = 5.0
    failure_threshold: int = 3
    success_threshold: int = 2


class AdvancedCircuitBreaker:
    """
    Advanced circuit breaker with multiple failure types,
    health checks, and adaptive thresholds
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        success_threshold: int = 3,
        timeout: float = 60.0,
        half_open_max_calls: int = 3,
        error_rate_threshold: float = 0.5,
        slow_call_duration: float = 1.0,
        slow_call_rate_threshold: float = 0.5,
        minimum_number_of_calls: int = 10,
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold
        self.timeout = timeout
        self.half_open_max_calls = half_open_max_calls
        self.error_rate_threshold = error_rate_threshold
        self.slow_call_duration = slow_call_duration
        self.slow_call_rate_threshold = slow_call_rate_threshold
        self.minimum_number_of_calls = minimum_number_of_calls

        # State management
        self.state = CircuitState.CLOSED
        self.state_changed_at = time.time()
        self.last_failure_time = 0.0

        # Metrics
        self.call_stats: deque[tuple[float, bool, float]] = deque(maxlen=100)
        self.failure_count = 0
        self.success_count = 0
        self.half_open_calls = 0

        # Health checks
        self.health_checks: list[HealthCheck] = []
        self.health_check_results: dict[str, bool] = {}

        # Thread safety
        self._lock = threading.Lock()

        # Listeners
        self.state_change_listeners: list[Callable] = []

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute a function through the circuit breaker"""
        if not self._allow_request():
            raise CircuitBreakerOpen(f"Circuit breaker {self.name} is open")

        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            self._on_success(time.time() - start_time)
            return result
        except Exception as e:
            self._on_failure(time.time() - start_time, e)
            raise

    async def async_call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute an async function through the circuit breaker"""
        if not self._allow_request():
            raise CircuitBreakerOpen(f"Circuit breaker {self.name} is open")

        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            self._on_success(time.time() - start_time)
            return result
        except Exception as e:
            self._on_failure(time.time() - start_time, e)
            raise

    def _allow_request(self) -> bool:
        """Check if request is allowed to proceed"""
        with self._lock:
            if self.state == CircuitState.FORCED_OPEN:
                return False

            if self.state == CircuitState.CLOSED:
                return True

            if self.state == CircuitState.OPEN:
                if time.time() - self.state_changed_at > self.timeout:
                    self._transition_to(CircuitState.HALF_OPEN)
                    return True
                return False

            if self.state == CircuitState.HALF_OPEN:
                if self.half_open_calls < self.half_open_max_calls:
                    self.half_open_calls += 1
                    return True
                return False

            return False

    def _on_success(self, duration: float):
        """Handle successful call"""
        with self._lock:
            self.call_stats.append((time.time(), True, duration))

            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.success_threshold:
                    self._transition_to(CircuitState.CLOSED)
            elif self.state == CircuitState.CLOSED:
                self.failure_count = max(0, self.failure_count - 1)

    def _on_failure(self, duration: float, error: Exception):
        """Handle failed call"""
        with self._lock:
            self.call_stats.append((time.time(), False, duration))
            self.last_failure_time = time.time()

            if self.state == CircuitState.HALF_OPEN:
                self._transition_to(CircuitState.OPEN)
            elif self.state == CircuitState.CLOSED:
                self.failure_count += 1

                # Check if we should open
                if self._should_open():
                    self._transition_to(CircuitState.OPEN)

    def _should_open(self) -> bool:
        """Determine if circuit should open based on metrics"""
        if len(self.call_stats) < self.minimum_number_of_calls:
            return False

        # Check failure count threshold
        if self.failure_count >= self.failure_threshold:
            return True

        # Calculate error rate
        recent_window = time.time() - 60.0  # Last minute
        recent_calls = [(t, s, d) for t, s, d in self.call_stats if t > recent_window]

        if len(recent_calls) >= self.minimum_number_of_calls:
            error_count = sum(1 for _, success, _ in recent_calls if not success)
            error_rate = error_count / len(recent_calls)

            if error_rate > self.error_rate_threshold:
                return True

            # Check slow call rate
            slow_calls = sum(1 for _, _, duration in recent_calls if duration > self.slow_call_duration)
            slow_rate = slow_calls / len(recent_calls)

            if slow_rate > self.slow_call_rate_threshold:
                return True

        return False

    def _transition_to(self, new_state: CircuitState):
        """Transition to a new state"""
        old_state = self.state
        self.state = new_state
        self.state_changed_at = time.time()

        # Reset counters
        if new_state == CircuitState.CLOSED:
            self.failure_count = 0
            self.success_count = 0
            self.half_open_calls = 0
        elif new_state == CircuitState.HALF_OPEN:
            self.success_count = 0
            self.half_open_calls = 0

        logger.info(f"Circuit breaker {self.name}: {old_state.value} -> {new_state.value}")

        # Notify listeners
        for listener in self.state_change_listeners:
            try:
                listener(self.name, old_state, new_state)
            except Exception as e:
                logger.error(f"Error in state change listener: {e}")

    def force_open(self):
        """Manually open the circuit"""
        with self._lock:
            self._transition_to(CircuitState.FORCED_OPEN)

    def force_close(self):
        """Manually close the circuit"""
        with self._lock:
            self._transition_to(CircuitState.CLOSED)

    def add_health_check(self, health_check: HealthCheck):
        """Add a health check"""
        self.health_checks.append(health_check)

    async def run_health_checks(self) -> dict[str, bool]:
        """Run all health checks"""
        results = {}

        for i, check in enumerate(self.health_checks):
            check_name = f"health_check_{i}"
            try:
                result = await asyncio.wait_for(check.check_function(), timeout=check.timeout)
                results[check_name] = bool(result)
            except Exception as e:
                logger.error(f"Health check {check_name} failed: {e}")
                results[check_name] = False

        self.health_check_results = results
        return results

    def get_metrics(self) -> dict[str, Any]:
        """Get circuit breaker metrics"""
        with self._lock:
            total_calls = len(self.call_stats)
            if total_calls == 0:
                return {
                    "state": self.state.value,
                    "total_calls": 0,
                    "error_rate": 0.0,
                    "slow_call_rate": 0.0,
                }

            errors = sum(1 for _, success, _ in self.call_stats if not success)
            slow_calls = sum(1 for _, _, duration in self.call_stats if duration > self.slow_call_duration)

            return {
                "state": self.state.value,
                "total_calls": total_calls,
                "error_rate": errors / total_calls,
                "slow_call_rate": slow_calls / total_calls,
                "failure_count": self.failure_count,
                "state_duration": time.time() - self.state_changed_at,
                "health_checks": self.health_check_results,
            }


class CircuitBreakerOpen(Exception):
    """Exception raised when circuit breaker is open"""


class AnomalyDetector:
    """
    Detects anomalous behavior in actors to prevent cascading failures
    """

    def __init__(
        self,
        window_size: int = 100,
        z_score_threshold: float = 3.0,
        isolation_forest_contamination: float = 0.1,
    ):
        self.window_size = window_size
        self.z_score_threshold = z_score_threshold
        self.contamination = isolation_forest_contamination

        # Metrics storage
        self.actor_metrics: dict[str, dict[str, deque]] = defaultdict(
            lambda: defaultdict(lambda: deque(maxlen=window_size))
        )

        # Anomaly history
        self.anomaly_history: dict[str, list[tuple[float, str, float]]] = defaultdict(list)

        # Baseline statistics
        self.baselines: dict[str, dict[str, tuple[float, float]]] = {}

        self._lock = threading.Lock()

    def record_metric(self, actor_id: str, metric_name: str, value: float):
        """Record a metric value for an actor"""
        with self._lock:
            self.actor_metrics[actor_id][metric_name].append((time.time(), value))

    def detect_anomalies(self, actor_id: str) -> list[tuple[str, float]]:
        """Detect anomalies for a specific actor"""
        anomalies = []

        with self._lock:
            if actor_id not in self.actor_metrics:
                return anomalies

            for metric_name, values in self.actor_metrics[actor_id].items():
                if len(values) < 10:  # Need minimum data
                    continue

                # Extract just the values
                metric_values = [v for _, v in values]

                # Z-score based detection
                z_score = self._calculate_z_score(metric_values)
                if abs(z_score) > self.z_score_threshold:
                    anomalies.append((metric_name, z_score))
                    self.anomaly_history[actor_id].append((time.time(), metric_name, z_score))

                # Update baseline if no anomaly
                else:
                    mean = np.mean(metric_values)
                    std = np.std(metric_values)
                    if actor_id not in self.baselines:
                        self.baselines[actor_id] = {}
                    self.baselines[actor_id][metric_name] = (mean, std)

        return anomalies

    def _calculate_z_score(self, values: list[float]) -> float:
        """Calculate z-score for the most recent value"""
        if len(values) < 2:
            return 0.0

        # Use all but last value for baseline
        baseline = values[:-1]
        mean = np.mean(baseline)
        std = np.std(baseline)

        if std == 0:
            return 0.0

        return (values[-1] - mean) / std

    def get_anomaly_score(self, actor_id: str) -> float:
        """Get overall anomaly score for an actor (0-1)"""
        with self._lock:
            if actor_id not in self.anomaly_history:
                return 0.0

            # Count recent anomalies
            recent_window = time.time() - 300  # Last 5 minutes
            recent_anomalies = [a for a in self.anomaly_history[actor_id] if a[0] > recent_window]

            if not recent_anomalies:
                return 0.0

            # Calculate severity-weighted score
            total_severity = sum(abs(z_score) for _, _, z_score in recent_anomalies)
            max_possible = len(recent_anomalies) * 10  # Assume max z-score of 10

            return min(1.0, total_severity / max_possible)


class ErrorPropagationTracker:
    """
    Tracks error propagation paths to identify and contain cascading failures
    """

    def __init__(self, max_propagation_depth: int = 5):
        self.max_propagation_depth = max_propagation_depth

        # Track error propagation chains
        self.propagation_chains: dict[str, list[FailureRecord]] = {}

        # Actor infection status
        self.infected_actors: set[str] = set()

        # Quarantine list
        self.quarantined_actors: set[str] = set()

        self._lock = threading.Lock()

    def record_failure(self, failure: FailureRecord):
        """Record a failure and track its propagation"""
        with self._lock:
            correlation_id = failure.correlation_id or str(time.time())

            if correlation_id not in self.propagation_chains:
                self.propagation_chains[correlation_id] = []

            self.propagation_chains[correlation_id].append(failure)

            # Check for cascading pattern
            if len(failure.propagation_path) > self.max_propagation_depth:
                logger.warning(f"Deep propagation detected: {failure.propagation_path}")
                # Mark actors in path as infected
                for actor_id in failure.propagation_path:
                    self.infected_actors.add(actor_id)

    def is_actor_infected(self, actor_id: str) -> bool:
        """Check if an actor is marked as infected"""
        with self._lock:
            return actor_id in self.infected_actors

    def quarantine_actor(self, actor_id: str):
        """Quarantine an actor to prevent further propagation"""
        with self._lock:
            self.quarantined_actors.add(actor_id)
            logger.warning(f"Actor {actor_id} quarantined")

    def is_quarantined(self, actor_id: str) -> bool:
        """Check if an actor is quarantined"""
        with self._lock:
            return actor_id in self.quarantined_actors

    def analyze_propagation_patterns(self) -> dict[str, Any]:
        """Analyze propagation patterns to identify problem areas"""
        with self._lock:
            patterns = {"hotspots": {}, "propagation_depths": [], "common_paths": []}

            # Find actors that appear frequently in propagation paths
            actor_counts = defaultdict(int)

            for chain in self.propagation_chains.values():
                for failure in chain:
                    for actor in failure.propagation_path:
                        actor_counts[actor] += 1

                    patterns["propagation_depths"].append(len(failure.propagation_path))

            # Identify hotspots
            if actor_counts:
                avg_count = np.mean(list(actor_counts.values()))
                std_count = np.std(list(actor_counts.values()))

                for actor, count in actor_counts.items():
                    if count > avg_count + 2 * std_count:
                        patterns["hotspots"][actor] = count

            return patterns


class ConsensusValidator:
    """
    Validates consensus among actors to prevent corrupted state propagation
    """

    def __init__(self, quorum_size: int = 3, agreement_threshold: float = 0.7):
        self.quorum_size = quorum_size
        self.agreement_threshold = agreement_threshold

        # Consensus results cache
        self.consensus_cache: dict[str, tuple[Any, float, float]] = {}
        self.cache_ttl = 60.0  # 1 minute

    async def validate_consensus(
        self, actor_refs: list[ActorRef], query: str, timeout: float = 5.0
    ) -> tuple[bool, Any]:
        """
        Validate consensus among multiple actors
        Returns (consensus_reached, consensus_value)
        """

        if len(actor_refs) < self.quorum_size:
            logger.warning(f"Insufficient actors for consensus: {len(actor_refs)}")
            return False, None

        # Check cache
        cache_key = self._create_cache_key(actor_refs, query)
        if cache_key in self.consensus_cache:
            value, timestamp, _ = self.consensus_cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                return True, value

        # Query all actors
        responses = []
        tasks = []

        for actor_ref in actor_refs[: self.quorum_size * 2]:  # Query more than needed
            task = asyncio.create_task(self._query_actor_with_timeout(actor_ref, query, timeout))
            tasks.append(task)

        # Gather responses
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for i, result in enumerate(results):
            if not isinstance(result, Exception):
                responses.append((actor_refs[i].actor_id, result))

        if len(responses) < self.quorum_size:
            logger.warning(f"Insufficient responses for consensus: {len(responses)}")
            return False, None

        # Analyze consensus
        consensus_reached, consensus_value = self._analyze_responses(responses)

        # Cache result
        if consensus_reached:
            self.consensus_cache[cache_key] = (
                consensus_value,
                time.time(),
                len(responses),
            )

        return consensus_reached, consensus_value

    async def _query_actor_with_timeout(self, actor_ref: ActorRef, query: str, timeout: float) -> Any:
        """Query an actor with timeout"""
        try:
            return await asyncio.wait_for(actor_ref.ask(query, {}), timeout=timeout)
        except asyncio.TimeoutError:
            raise TimeoutError(f"Actor {actor_ref.actor_id} timed out")

    def _analyze_responses(self, responses: list[tuple[str, Any]]) -> tuple[bool, Any]:
        """Analyze responses for consensus"""
        if not responses:
            return False, None

        # Group identical responses
        response_groups = defaultdict(list)

        for actor_id, response in responses:
            # Create hash of response for grouping
            response_hash = hashlib.sha256(  # Changed from MD5 for security
                json.dumps(response, sort_keys=True).encode()
            ).hexdigest()
            response_groups[response_hash].append((actor_id, response))

        # Find majority response
        total_responses = len(responses)
        for response_hash, group in response_groups.items():
            if len(group) / total_responses >= self.agreement_threshold:
                # Consensus reached
                return True, group[0][1]  # Return the response value

        return False, None

    def _create_cache_key(self, actor_refs: list[ActorRef], query: str) -> str:
        """Create cache key for consensus query"""
        sorted([ref.actor_id for ref in actor_refs])
        return hashlib.sha256()  #  Changed from MD5 for securityf"{','.join(actor_ids)}:{query}".encode()).hexdigest()


class CascadePreventionSystem:
    """
    Main system for preventing cascading failures in the distributed actor system
    """

    def __init__(
        self,
        actor_system: ActorSystem,
        observability: Optional[ObservabilityCollector] = None,
    ):
        self.actor_system = actor_system
        self.observability = observability

        # Components
        self.circuit_breakers: dict[str, AdvancedCircuitBreaker] = {}
        self.anomaly_detector = AnomalyDetector()
        self.error_tracker = ErrorPropagationTracker()
        self.consensus_validator = ConsensusValidator()

        # Global state
        self.system_health_score = 1.0
        self.emergency_mode = False

        # Monitoring
        self._monitoring_task = None
        self._running = False

    async def start(self):
        """Start the cascade prevention system"""
        self._running = True
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Cascade prevention system started")

    async def stop(self):
        """Stop the cascade prevention system"""
        self._running = False
        if self._monitoring_task:
            self._monitoring_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._monitoring_task
        logger.info("Cascade prevention system stopped")

    def get_or_create_circuit_breaker(self, actor_id: str, **kwargs) -> AdvancedCircuitBreaker:
        """Get or create a circuit breaker for an actor"""
        if actor_id not in self.circuit_breakers:
            cb = AdvancedCircuitBreaker(name=actor_id, **kwargs)
            cb.state_change_listeners.append(self._on_circuit_state_change)
            self.circuit_breakers[actor_id] = cb

        return self.circuit_breakers[actor_id]

    async def protected_call(
        self,
        actor_ref: ActorRef,
        message_type: str,
        payload: dict[str, Any],
        timeout: float = 30.0,
    ) -> Any:
        """Make a protected call through circuit breaker and validation"""

        # Check quarantine
        if self.error_tracker.is_quarantined(actor_ref.actor_id):
            raise ActorQuarantined(f"Actor {actor_ref.actor_id} is quarantined")

        # Get circuit breaker
        cb = self.get_or_create_circuit_breaker(actor_ref.actor_id)

        # Make call through circuit breaker
        async def make_call():
            # Record pre-call metrics
            if self.observability:
                snapshot = await self._get_actor_snapshot(actor_ref.actor_id)
                if snapshot:
                    self.anomaly_detector.record_metric(actor_ref.actor_id, "mailbox_size", snapshot.mailbox_size)

            # Make the actual call
            result = await actor_ref.ask(message_type, payload, timeout=timeout)

            # Check for anomalies
            anomalies = self.anomaly_detector.detect_anomalies(actor_ref.actor_id)
            if anomalies:
                logger.warning(f"Anomalies detected in {actor_ref.actor_id}: {anomalies}")

                # Check anomaly score
                score = self.anomaly_detector.get_anomaly_score(actor_ref.actor_id)
                if score > 0.7:
                    self.error_tracker.quarantine_actor(actor_ref.actor_id)
                    raise AnomalyDetected(f"High anomaly score ({score}) for {actor_ref.actor_id}")

            return result

        return await cb.async_call(make_call)

    async def validate_with_consensus(self, actor_refs: list[ActorRef], query: str) -> tuple[bool, Any]:
        """Validate a query with consensus among multiple actors"""

        # Filter out quarantined actors
        valid_refs = [ref for ref in actor_refs if not self.error_tracker.is_quarantined(ref.actor_id)]

        if len(valid_refs) < self.consensus_validator.quorum_size:
            logger.error("Insufficient healthy actors for consensus")
            return False, None

        return await self.consensus_validator.validate_consensus(valid_refs, query)

    def report_failure(self, failure: FailureRecord):
        """Report a failure to the system"""
        self.error_tracker.record_failure(failure)

        # Update anomaly detection
        self.anomaly_detector.record_metric(failure.actor_id, f"failure_{failure.failure_type.value}", failure.severity)

        # Check for emergency conditions
        self._check_emergency_conditions()

    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self._running:
            try:
                await self._collect_system_metrics()
                await self._run_health_checks()
                self._update_system_health_score()

                await asyncio.sleep(10.0)  # Run every 10 seconds

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")

    async def _collect_system_metrics(self):
        """Collect metrics from all actors"""
        if not self.observability:
            return

        for actor_id in self.actor_system.actors:
            try:
                snapshot = await self._get_actor_snapshot(actor_id)
                if snapshot:
                    # Record various metrics
                    self.anomaly_detector.record_metric(actor_id, "message_rate", snapshot.message_rate)
                    self.anomaly_detector.record_metric(actor_id, "error_rate", snapshot.error_rate)
                    self.anomaly_detector.record_metric(actor_id, "memory_usage", snapshot.memory_usage)
            except Exception as e:
                logger.debug(f"Failed to collect metrics for {actor_id}: {e}")

    async def _get_actor_snapshot(self, actor_id: str) -> Optional[ActorSnapshot]:
        """Get snapshot for an actor"""
        if not self.observability:
            return None

        # Get from observability collector
        snapshots = self.observability.actor_snapshots.get(actor_id, [])
        if snapshots:
            return snapshots[-1]  # Most recent

        return None

    async def _run_health_checks(self):
        """Run health checks on all circuit breakers"""
        tasks = []

        for actor_id, cb in self.circuit_breakers.items():
            if cb.health_checks:
                task = asyncio.create_task(cb.run_health_checks())
                tasks.append((actor_id, task))

        if tasks:
            results = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)

            for i, (actor_id, _) in enumerate(tasks):
                if isinstance(results[i], Exception):
                    logger.error(f"Health check failed for {actor_id}: {results[i]}")

    def _update_system_health_score(self):
        """Update overall system health score"""
        scores = []

        # Circuit breaker states
        open_circuits = sum(
            1 for cb in self.circuit_breakers.values() if cb.state in [CircuitState.OPEN, CircuitState.FORCED_OPEN]
        )
        if self.circuit_breakers:
            cb_score = 1.0 - (open_circuits / len(self.circuit_breakers))
            scores.append(cb_score)

        # Quarantined actors
        if self.actor_system.actors:
            quarantine_score = 1.0 - (len(self.error_tracker.quarantined_actors) / len(self.actor_system.actors))
            scores.append(quarantine_score)

        # Anomaly scores
        anomaly_scores = []
        for actor_id in self.actor_system.actors:
            score = self.anomaly_detector.get_anomaly_score(actor_id)
            anomaly_scores.append(1.0 - score)

        if anomaly_scores:
            scores.append(np.mean(anomaly_scores))

        # Calculate overall score
        if scores:
            self.system_health_score = np.mean(scores)
        else:
            self.system_health_score = 1.0

    def _check_emergency_conditions(self):
        """Check if emergency mode should be activated"""
        # Multiple conditions for emergency mode
        conditions = [
            self.system_health_score < 0.3,
            len(self.error_tracker.quarantined_actors) > len(self.actor_system.actors) * 0.5,
            sum(1 for cb in self.circuit_breakers.values() if cb.state == CircuitState.OPEN)
            > len(self.circuit_breakers) * 0.5,
        ]

        if any(conditions) and not self.emergency_mode:
            self.emergency_mode = True
            logger.critical("EMERGENCY MODE ACTIVATED - System health critical")

            # Take emergency actions
            self._execute_emergency_protocol()

        elif all(not c for c in conditions) and self.emergency_mode:
            self.emergency_mode = False
            logger.warning("Emergency mode deactivated - System recovering")

    def _execute_emergency_protocol(self):
        """Execute emergency protocol to prevent total system collapse"""
        logger.critical("Executing emergency protocol")

        # 1. Open all circuit breakers to stop cascading
        for cb in self.circuit_breakers.values():
            if cb.state == CircuitState.CLOSED:
                cb.force_open()

        # 2. Quarantine high-risk actors
        for actor_id in self.actor_system.actors:
            if self.anomaly_detector.get_anomaly_score(actor_id) > 0.8:
                self.error_tracker.quarantine_actor(actor_id)

        # 3. Clear propagation chains to prevent further spread
        self.error_tracker.propagation_chains.clear()

        # 4. Notify system administrators (would be implemented in production)
        logger.critical(
            f"Emergency protocol executed. "
            f"Quarantined: {len(self.error_tracker.quarantined_actors)}, "
            f"Open circuits: {len([cb for cb in self.circuit_breakers.values() if cb.state == CircuitState.OPEN])}"
        )

    def _on_circuit_state_change(self, name: str, old_state: CircuitState, new_state: CircuitState):
        """Handle circuit breaker state changes"""
        logger.info(f"Circuit breaker {name}: {old_state.value} -> {new_state.value}")

        # Record state change as system event
        if self.observability:
            self.observability.record_system_event(
                "circuit_breaker_state_change",
                {
                    "actor_id": name,
                    "old_state": old_state.value,
                    "new_state": new_state.value,
                },
            )

    def get_system_status(self) -> dict[str, Any]:
        """Get comprehensive system status"""
        return {
            "health_score": self.system_health_score,
            "emergency_mode": self.emergency_mode,
            "circuit_breakers": {actor_id: cb.get_metrics() for actor_id, cb in self.circuit_breakers.items()},
            "quarantined_actors": list(self.error_tracker.quarantined_actors),
            "infected_actors": list(self.error_tracker.infected_actors),
            "propagation_analysis": self.error_tracker.analyze_propagation_patterns(),
        }


# Custom exceptions
class ActorQuarantined(Exception):
    """Raised when trying to communicate with a quarantined actor"""


class AnomalyDetected(Exception):
    """Raised when anomalous behavior is detected"""


# Example usage and demo
async def demo_cascade_prevention():
    """Demonstrate cascade prevention capabilities"""
    from .actor_system import AIAgentActor, get_global_actor_system
    from .observability_steering import ObservabilityCollector

    # Setup
    system = await get_global_actor_system()
    collector = ObservabilityCollector()
    collector.start()

    cascade_prevention = CascadePreventionSystem(system, collector)
    await cascade_prevention.start()

    # Create test actors
    class TestActor(AIAgentActor):
        def __init__(self, actor_id: str, failure_rate: float = 0.0):
            super().__init__(actor_id)
            self.failure_rate = failure_rate
            self.register_handler("process", self._handle_process)

        async def _handle_process(self, message):
            import random

            if random.random() < self.failure_rate:
                raise Exception("Simulated failure")

            await asyncio.sleep(0.1)  # Simulate work
            return {"result": "processed"}

    # Create actor network
    actors = []
    for i in range(5):
        failure_rate = 0.1 if i == 2 else 0.0  # One faulty actor
        actor_ref = await system.create_actor(TestActor, f"test-actor-{i}", failure_rate=failure_rate)
        actors.append(actor_ref)

    # Simulate cascading failure scenario
    for i in range(20):
        try:
            # Make protected calls
            actor_ref = actors[i % len(actors)]
            result = await cascade_prevention.protected_call(actor_ref, "process", {"data": f"request_{i}"})
            print(f"Request {i} processed: {result}")

        except CircuitBreakerOpen as e:
            print(f"Request {i} blocked: {e}")
        except Exception as e:
            print(f"Request {i} failed: {e}")

            # Report failure
            cascade_prevention.report_failure(
                FailureRecord(
                    timestamp=time.time(),
                    failure_type=FailureType.ERROR,
                    actor_id=actor_ref.actor_id,
                    error_message=str(e),
                    propagation_path=[f"test-actor-{j}" for j in range(i % 3)],
                )
            )

        await asyncio.sleep(0.5)

    # Check system status
    status = cascade_prevention.get_system_status()
    print(f"System status: {json.dumps(status, indent=2)}")

    # Test consensus validation
    consensus_reached, value = await cascade_prevention.validate_with_consensus(actors[:3], "get_state")
    print(f"Consensus validation: {consensus_reached}, value: {value}")

    # Cleanup
    await cascade_prevention.stop()
    collector.stop()


if __name__ == "__main__":
    asyncio.run(demo_cascade_prevention())
