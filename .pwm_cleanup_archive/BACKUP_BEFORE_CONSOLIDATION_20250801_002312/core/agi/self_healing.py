"""
LUKHAS Self-Healing Architecture
Autonomous error recovery and system resilience
"""

import asyncio
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class FailureType(Enum):
    """Types of system failures"""

    MEMORY_OVERFLOW = "memory_overflow"
    DEADLOCK = "deadlock"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    CORRUPTION = "corruption"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    COMMUNICATION_FAILURE = "communication_failure"
    CONSCIOUSNESS_INCOHERENCE = "consciousness_incoherence"
    LEARNING_PLATEAU = "learning_plateau"


class HealingStrategy(Enum):
    """Self-healing strategies"""

    RESTART = "restart"
    ROLLBACK = "rollback"
    ISOLATE = "isolate"
    REPAIR = "repair"
    ADAPT = "adapt"
    RECONFIGURE = "reconfigure"
    DEGRADE_GRACEFULLY = "degrade_gracefully"


@dataclass
class SystemFailure:
    """System failure event"""

    id: str
    type: FailureType
    component: str
    error: Exception
    timestamp: datetime
    context: Dict[str, Any] = field(default_factory=dict)
    severity: float = 0.5  # 0.0 to 1.0


@dataclass
class HealingAction:
    """Healing action taken"""

    failure_id: str
    strategy: HealingStrategy
    component: str
    timestamp: datetime
    success: bool
    duration_ms: float
    details: Dict[str, Any] = field(default_factory=dict)


class ComponentHealth:
    """Track health of system component"""

    def __init__(self, name: str):
        self.name = name
        self.health_score = 1.0
        self.failure_count = 0
        self.last_failure: Optional[datetime] = None
        self.recovery_count = 0
        self.metrics_history = deque(maxlen=100)

    def record_failure(self):
        """Record component failure"""
        self.failure_count += 1
        self.last_failure = datetime.utcnow()
        self.health_score *= 0.9  # Decay health

    def record_recovery(self):
        """Record successful recovery"""
        self.recovery_count += 1
        self.health_score = min(1.0, self.health_score * 1.1)

    def update_metrics(self, metrics: Dict[str, float]):
        """Update component metrics"""
        self.metrics_history.append(
            {"timestamp": datetime.utcnow(), "metrics": metrics}
        )


class SelfHealingSystem:
    """
    Autonomous self-healing system for LUKHAS AGI
    Detects, diagnoses, and repairs system failures
    """

    def __init__(self):
        # Component health tracking
        self.component_health: Dict[str, ComponentHealth] = {}

        # Failure history
        self.failure_history: List[SystemFailure] = []
        self.healing_history: List[HealingAction] = []

        # Healing strategies
        self.healing_strategies: Dict[FailureType, List[HealingStrategy]] = {
            FailureType.MEMORY_OVERFLOW: [
                HealingStrategy.RESTART,
                HealingStrategy.RECONFIGURE,
            ],
            FailureType.DEADLOCK: [HealingStrategy.RESTART, HealingStrategy.ISOLATE],
            FailureType.RESOURCE_EXHAUSTION: [
                HealingStrategy.DEGRADE_GRACEFULLY,
                HealingStrategy.RECONFIGURE,
            ],
            FailureType.CORRUPTION: [HealingStrategy.ROLLBACK, HealingStrategy.REPAIR],
            FailureType.PERFORMANCE_DEGRADATION: [
                HealingStrategy.ADAPT,
                HealingStrategy.RECONFIGURE,
            ],
            FailureType.COMMUNICATION_FAILURE: [
                HealingStrategy.RESTART,
                HealingStrategy.ISOLATE,
            ],
            FailureType.CONSCIOUSNESS_INCOHERENCE: [
                HealingStrategy.REPAIR,
                HealingStrategy.RESTART,
            ],
            FailureType.LEARNING_PLATEAU: [
                HealingStrategy.ADAPT,
                HealingStrategy.RECONFIGURE,
            ],
        }

        # Component dependencies
        self.dependencies: Dict[str, List[str]] = {}

        # Recovery procedures
        self.recovery_procedures: Dict[str, Callable] = {}

        # Circuit breakers
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}

        # Adaptive learning
        self.healing_learner = HealingLearner()

        self._running = False

    async def initialize(self):
        """Initialize self-healing system"""
        self._running = True

        # Start monitoring loops
        asyncio.create_task(self._health_monitor_loop())
        asyncio.create_task(self._pattern_detection_loop())
        asyncio.create_task(self._proactive_healing_loop())

    def register_component(
        self, name: str, dependencies: List[str] = None, recovery_proc: Callable = None
    ):
        """Register a system component for monitoring"""
        self.component_health[name] = ComponentHealth(name)
        self.dependencies[name] = dependencies or []

        if recovery_proc:
            self.recovery_procedures[name] = recovery_proc

        # Create circuit breaker
        self.circuit_breakers[name] = CircuitBreaker(name)

    async def handle_failure(
        self, component: str, error: Exception, context: Dict[str, Any] = None
    ) -> bool:
        """
        Handle system failure

        Args:
            component: Failed component name
            error: Exception that occurred
            context: Additional context

        Returns:
            Success status of healing
        """
        # Create failure record
        failure = SystemFailure(
            id=self._generate_failure_id(),
            type=self._classify_failure(error),
            component=component,
            error=error,
            timestamp=datetime.utcnow(),
            context=context or {},
            severity=self._assess_severity(component, error),
        )

        self.failure_history.append(failure)

        # Update component health
        if component in self.component_health:
            self.component_health[component].record_failure()

        # Check circuit breaker
        breaker = self.circuit_breakers.get(component)
        if breaker and breaker.is_open():
            # Component is circuit-broken, use fallback
            return await self._use_fallback(component)

        # Attempt healing
        success = await self._heal_failure(failure)

        # Learn from outcome
        await self.healing_learner.learn(failure, success)

        return success

    async def check_system_health(self) -> Dict[str, Any]:
        """Check overall system health"""
        health_report = {
            "timestamp": datetime.utcnow().isoformat(),
            "overall_health": self._calculate_overall_health(),
            "components": {},
            "active_issues": [],
        }

        # Check each component
        for name, health in self.component_health.items():
            health_report["components"][name] = {
                "health_score": health.health_score,
                "failure_count": health.failure_count,
                "recovery_count": health.recovery_count,
                "last_failure": (
                    health.last_failure.isoformat() if health.last_failure else None
                ),
            }

            if health.health_score < 0.7:
                health_report["active_issues"].append(
                    {
                        "component": name,
                        "health_score": health.health_score,
                        "recommendation": self._get_health_recommendation(name, health),
                    }
                )

        return health_report

    # Core healing logic
    async def _heal_failure(self, failure: SystemFailure) -> bool:
        """Attempt to heal a failure"""
        # Get healing strategies for this failure type
        strategies = self.healing_strategies.get(
            failure.type, [HealingStrategy.RESTART]
        )

        # Let learner suggest best strategy
        suggested_strategy = await self.healing_learner.suggest_strategy(
            failure, strategies
        )
        if suggested_strategy:
            strategies = [suggested_strategy] + [
                s for s in strategies if s != suggested_strategy
            ]

        # Try strategies in order
        for strategy in strategies:
            start_time = datetime.utcnow()

            try:
                success = await self._execute_healing_strategy(failure, strategy)

                # Record healing action
                duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
                action = HealingAction(
                    failure_id=failure.id,
                    strategy=strategy,
                    component=failure.component,
                    timestamp=start_time,
                    success=success,
                    duration_ms=duration_ms,
                )

                self.healing_history.append(action)

                if success:
                    # Update component health
                    if failure.component in self.component_health:
                        self.component_health[failure.component].record_recovery()

                    # Reset circuit breaker
                    if failure.component in self.circuit_breakers:
                        self.circuit_breakers[failure.component].reset()

                    return True

            except Exception as e:
                # Healing strategy failed
                print(f"Healing strategy {strategy} failed: {e}")
                continue

        # All strategies failed
        if failure.component in self.circuit_breakers:
            self.circuit_breakers[failure.component].trip()

        return False

    async def _execute_healing_strategy(
        self, failure: SystemFailure, strategy: HealingStrategy
    ) -> bool:
        """Execute specific healing strategy"""
        component = failure.component

        if strategy == HealingStrategy.RESTART:
            return await self._restart_component(component)

        elif strategy == HealingStrategy.ROLLBACK:
            return await self._rollback_component(component)

        elif strategy == HealingStrategy.ISOLATE:
            return await self._isolate_component(component)

        elif strategy == HealingStrategy.REPAIR:
            return await self._repair_component(component, failure)

        elif strategy == HealingStrategy.ADAPT:
            return await self._adapt_component(component, failure)

        elif strategy == HealingStrategy.RECONFIGURE:
            return await self._reconfigure_component(component)

        elif strategy == HealingStrategy.DEGRADE_GRACEFULLY:
            return await self._degrade_component(component)

        return False

    async def _restart_component(self, component: str) -> bool:
        """Restart a component"""
        if component in self.recovery_procedures:
            try:
                await self.recovery_procedures[component]("restart")
                return True
            except:
                return False
        return False

    async def _rollback_component(self, component: str) -> bool:
        """Rollback component to previous state"""
        # In production, would restore from checkpoint
        return True

    async def _isolate_component(self, component: str) -> bool:
        """Isolate component from system"""
        # Update dependencies to bypass isolated component
        for comp, deps in self.dependencies.items():
            if component in deps:
                self.dependencies[comp] = [d for d in deps if d != component]
        return True

    async def _repair_component(self, component: str, failure: SystemFailure) -> bool:
        """Attempt to repair component"""
        if component in self.recovery_procedures:
            try:
                await self.recovery_procedures[component]("repair", failure)
                return True
            except:
                return False
        return False

    async def _adapt_component(self, component: str, failure: SystemFailure) -> bool:
        """Adapt component configuration"""
        # In production, would adjust parameters based on failure
        return True

    async def _reconfigure_component(self, component: str) -> bool:
        """Reconfigure component settings"""
        # In production, would update configuration
        return True

    async def _degrade_component(self, component: str) -> bool:
        """Run component in degraded mode"""
        # In production, would reduce functionality
        return True

    async def _use_fallback(self, component: str) -> bool:
        """Use fallback for circuit-broken component"""
        # In production, would activate backup system
        return True

    # Monitoring loops
    async def _health_monitor_loop(self):
        """Monitor component health"""
        while self._running:
            await asyncio.sleep(30)  # Check every 30 seconds

            # Check for unhealthy components
            for name, health in self.component_health.items():
                if health.health_score < 0.5:
                    # Proactively attempt healing
                    await self.handle_failure(
                        name,
                        Exception("Low health score"),
                        {"health_score": health.health_score},
                    )

    async def _pattern_detection_loop(self):
        """Detect failure patterns"""
        while self._running:
            await asyncio.sleep(300)  # Every 5 minutes

            # Analyze recent failures
            recent_failures = [
                f
                for f in self.failure_history
                if f.timestamp > datetime.utcnow() - timedelta(hours=1)
            ]

            patterns = self._detect_failure_patterns(recent_failures)

            for pattern in patterns:
                # Take preventive action
                await self._prevent_failure_pattern(pattern)

    async def _proactive_healing_loop(self):
        """Proactively heal before failures occur"""
        while self._running:
            await asyncio.sleep(600)  # Every 10 minutes

            # Predict potential failures
            predictions = await self._predict_failures()

            for prediction in predictions:
                # Take preventive action
                await self._prevent_predicted_failure(prediction)

    # Helper methods
    def _classify_failure(self, error: Exception) -> FailureType:
        """Classify failure type from error"""
        error_str = str(error).lower()

        if "memory" in error_str:
            return FailureType.MEMORY_OVERFLOW
        elif "deadlock" in error_str or "timeout" in error_str:
            return FailureType.DEADLOCK
        elif "resource" in error_str:
            return FailureType.RESOURCE_EXHAUSTION
        elif "corrupt" in error_str:
            return FailureType.CORRUPTION
        elif "performance" in error_str or "slow" in error_str:
            return FailureType.PERFORMANCE_DEGRADATION
        elif "connection" in error_str or "network" in error_str:
            return FailureType.COMMUNICATION_FAILURE
        elif "consciousness" in error_str or "coherence" in error_str:
            return FailureType.CONSCIOUSNESS_INCOHERENCE
        elif "learning" in error_str or "plateau" in error_str:
            return FailureType.LEARNING_PLATEAU

        return FailureType.CORRUPTION  # Default

    def _assess_severity(self, component: str, error: Exception) -> float:
        """Assess failure severity"""
        # Critical components have higher severity
        critical_components = ["consciousness", "memory", "core"]

        severity = 0.5

        if any(c in component.lower() for c in critical_components):
            severity += 0.3

        if isinstance(error, MemoryError):
            severity += 0.2
        elif isinstance(error, RecursionError):
            severity += 0.1

        return min(1.0, severity)

    def _calculate_overall_health(self) -> float:
        """Calculate overall system health"""
        if not self.component_health:
            return 1.0

        health_scores = [h.health_score for h in self.component_health.values()]

        # Weighted average with penalty for any very unhealthy component
        avg_health = sum(health_scores) / len(health_scores)
        min_health = min(health_scores)

        return 0.7 * avg_health + 0.3 * min_health

    def _get_health_recommendation(
        self, component: str, health: ComponentHealth
    ) -> str:
        """Get health improvement recommendation"""
        if health.failure_count > 10:
            return "Consider replacing or major refactoring"
        elif health.health_score < 0.3:
            return "Immediate intervention required"
        elif health.health_score < 0.5:
            return "Schedule maintenance"
        else:
            return "Monitor closely"

    def _detect_failure_patterns(
        self, failures: List[SystemFailure]
    ) -> List[Dict[str, Any]]:
        """Detect patterns in failures"""
        patterns = []

        # Component failure clustering
        component_failures = defaultdict(list)
        for failure in failures:
            component_failures[failure.component].append(failure)

        for component, comp_failures in component_failures.items():
            if len(comp_failures) > 3:
                patterns.append(
                    {
                        "type": "repeated_component_failure",
                        "component": component,
                        "count": len(comp_failures),
                    }
                )

        return patterns

    async def _prevent_failure_pattern(self, pattern: Dict[str, Any]):
        """Prevent detected failure pattern"""
        if pattern["type"] == "repeated_component_failure":
            # Proactively reconfigure problematic component
            await self._reconfigure_component(pattern["component"])

    async def _predict_failures(self) -> List[Dict[str, Any]]:
        """Predict potential failures"""
        predictions = []

        for name, health in self.component_health.items():
            # Simple prediction based on health trend
            if len(health.metrics_history) > 10:
                recent_metrics = list(health.metrics_history)[-10:]
                # Check for degrading trend
                # In production, would use ML model

        return predictions

    async def _prevent_predicted_failure(self, prediction: Dict[str, Any]):
        """Prevent predicted failure"""
        # Take preventive action based on prediction
        pass

    def _generate_failure_id(self) -> str:
        """Generate unique failure ID"""
        import uuid

        return f"fail_{uuid.uuid4().hex[:8]}"


class CircuitBreaker:
    """Circuit breaker for component protection"""

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        timeout: timedelta = timedelta(minutes=5),
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = "closed"  # closed, open, half-open

    def is_open(self) -> bool:
        """Check if circuit is open"""
        if self.state == "open":
            # Check if timeout has passed
            if datetime.utcnow() - self.last_failure_time > self.timeout:
                self.state = "half-open"
                return False
            return True
        return False

    def trip(self):
        """Trip the circuit breaker"""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()

        if self.failure_count >= self.failure_threshold:
            self.state = "open"

    def reset(self):
        """Reset circuit breaker"""
        self.failure_count = 0
        self.state = "closed"


class HealingLearner:
    """Learn from healing successes and failures"""

    def __init__(self):
        self.strategy_success_rates: Dict[
            Tuple[FailureType, HealingStrategy], float
        ] = defaultdict(lambda: 0.5)
        self.healing_patterns: List[Dict[str, Any]] = []

    async def learn(self, failure: SystemFailure, success: bool):
        """Learn from healing outcome"""
        # Update success rates
        key = (failure.type, HealingStrategy.RESTART)  # Would get actual strategy used

        current_rate = self.strategy_success_rates[key]
        # Exponential moving average
        self.strategy_success_rates[key] = 0.9 * current_rate + 0.1 * (
            1.0 if success else 0.0
        )

        # Record pattern
        self.healing_patterns.append(
            {
                "failure_type": failure.type,
                "success": success,
                "timestamp": datetime.utcnow(),
            }
        )

    async def suggest_strategy(
        self, failure: SystemFailure, available: List[HealingStrategy]
    ) -> Optional[HealingStrategy]:
        """Suggest best healing strategy based on learning"""
        best_strategy = None
        best_rate = 0.0

        for strategy in available:
            rate = self.strategy_success_rates.get((failure.type, strategy), 0.5)
            if rate > best_rate:
                best_rate = rate
                best_strategy = strategy

        return best_strategy if best_rate > 0.6 else None
