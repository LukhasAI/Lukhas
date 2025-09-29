"""
Canary Controller - Progressive deployment automation for LUKHAS
===============================================================

Automated canary deployment with progressive traffic shifting, real-time monitoring,
and rollback triggers integrated with the Constellation Framework.
"""

import asyncio
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
import logging
from datetime import datetime

from .lane_manager import Lane, LaneManager
from ..core.types import LUKHASError
from ..constellation_framework import ConstellationFramework
from ..observability.metrics import MetricsCollector
from ..governance.guardian_integration import GuardianValidator


class CanaryState(Enum):
    """Canary deployment states"""
    PENDING = "pending"
    INITIALIZING = "initializing"
    RAMPING = "ramping"
    MONITORING = "monitoring"
    COMPLETING = "completing"
    COMPLETED = "completed"
    ROLLING_BACK = "rolling_back"
    FAILED = "failed"
    PAUSED = "paused"


class CanaryStrategy(Enum):
    """Canary deployment strategies"""
    LINEAR = "linear"        # Linear traffic increase
    EXPONENTIAL = "exponential"  # Exponential traffic increase
    BLUE_GREEN = "blue_green"    # Blue-green deployment
    FEATURE_FLAG = "feature_flag"  # Feature flag based


@dataclass
class CanaryConfig:
    """Configuration for a canary deployment"""
    deployment_id: str
    service_name: str
    version: str
    strategy: CanaryStrategy
    target_lane: Lane

    # Traffic progression
    initial_traffic: float = 1.0  # Start with 1% traffic
    target_traffic: float = 100.0  # End with 100% traffic
    step_size: float = 10.0  # Increase by 10% each step
    step_duration: int = 300  # 5 minutes per step

    # Health thresholds
    max_error_rate: float = 0.02  # 2% max error rate
    max_latency_p95: float = 0.250  # 250ms max P95 latency
    min_success_rate: float = 0.98  # 98% min success rate

    # Monitoring
    monitoring_duration: int = 1800  # 30 minutes monitoring
    health_check_interval: int = 30  # 30 seconds

    # Rollback
    auto_rollback: bool = True
    rollback_on_sla_violation: bool = True

    # Feature flags
    feature_flags: Dict[str, Any] = field(default_factory=dict)

    # Validation
    smoke_tests: List[str] = field(default_factory=list)
    validation_endpoints: List[str] = field(default_factory=list)


@dataclass
class CanaryMetrics:
    """Real-time metrics for a canary deployment"""
    deployment_id: str
    timestamp: datetime
    current_traffic: float
    error_rate: float
    latency_p95: float
    latency_p99: float
    success_rate: float
    throughput_rps: float
    health_score: float
    sla_violations: int
    active_connections: int


@dataclass
class CanaryDeployment:
    """Active canary deployment state"""
    config: CanaryConfig
    state: CanaryState
    started_at: datetime
    current_step: int
    current_traffic: float
    metrics_history: List[CanaryMetrics] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    rollback_reason: Optional[str] = None
    completed_at: Optional[datetime] = None


class CanaryController:
    """Progressive deployment automation system"""

    def __init__(
        self,
        lane_manager: LaneManager,
        constellation: ConstellationFramework,
        metrics_collector: MetricsCollector,
        guardian: GuardianValidator
    ):
        self.lane_manager = lane_manager
        self.constellation = constellation
        self.metrics_collector = metrics_collector
        self.guardian = guardian
        self.logger = logging.getLogger(f"{__name__}.CanaryController")

        # Deployment tracking
        self._active_deployments: Dict[str, CanaryDeployment] = {}
        self._deployment_history: List[CanaryDeployment] = []

        # Control
        self._running = False
        self._controller_task: Optional[asyncio.Task] = None

        # Callbacks
        self._rollback_callbacks: Dict[str, List[Callable]] = {}
        self._validation_callbacks: Dict[str, List[Callable]] = {}

        # Initialize metrics
        self._init_metrics()

    def _init_metrics(self):
        """Initialize metrics collection"""
        self.metrics_collector.register_histogram(
            "canary_deployment_duration_seconds",
            "Duration of canary deployments",
            buckets=[60, 300, 600, 1200, 1800, 3600, 7200]
        )

        self.metrics_collector.register_counter(
            "canary_deployments_total",
            "Total canary deployments",
            labels=["strategy", "result"]
        )

        self.metrics_collector.register_gauge(
            "canary_traffic_percentage",
            "Current canary traffic percentage",
            labels=["deployment_id", "service_name"]
        )

        self.metrics_collector.register_counter(
            "canary_rollbacks_total",
            "Total canary rollbacks",
            labels=["reason", "service_name"]
        )

        self.metrics_collector.register_histogram(
            "canary_validation_latency_seconds",
            "Canary validation check latency",
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
        )

    async def start(self):
        """Start the canary controller"""
        if self._running:
            return

        self.logger.info("Starting Canary Controller")
        self._running = True

        # Start controller task
        self._controller_task = asyncio.create_task(self._controller_loop())

        # Register with Constellation Framework
        if self.constellation:
            await self.constellation.register_component(
                "canary_controller",
                self,
                health_check=self._health_check
            )

        self.logger.info("Canary Controller started successfully")

    async def stop(self):
        """Stop the canary controller"""
        if not self._running:
            return

        self.logger.info("Stopping Canary Controller")
        self._running = False

        # Cancel active deployments
        for deployment_id in list(self._active_deployments.keys()):
            await self.cancel_deployment(deployment_id, "system_shutdown")

        if self._controller_task:
            self._controller_task.cancel()
            try:
                await self._controller_task
            except asyncio.CancelledError:
                pass

        self.logger.info("Canary Controller stopped")

    async def start_deployment(self, config: CanaryConfig) -> str:
        """
        Start a new canary deployment

        Args:
            config: Deployment configuration

        Returns:
            Deployment ID
        """
        try:
            # Validate configuration
            await self._validate_config(config)

            # Check for conflicts
            existing = self._find_conflicting_deployment(config)
            if existing:
                raise LUKHASError(
                    f"Conflicting deployment exists: {existing.config.deployment_id}"
                )

            # Guardian validation
            guardian_context = {
                "service_name": config.service_name,
                "version": config.version,
                "strategy": config.strategy.value,
                "target_lane": config.target_lane.value,
                "max_error_rate": config.max_error_rate
            }

            guardian_result = await self.guardian.validate_action_async(
                "canary_deployment",
                guardian_context,
                timeout=10.0
            )

            if not guardian_result.allowed:
                raise LUKHASError(f"Guardian blocked deployment: {guardian_result.reason}")

            # Create deployment
            deployment = CanaryDeployment(
                config=config,
                state=CanaryState.PENDING,
                started_at=datetime.now(),
                current_step=0,
                current_traffic=0.0
            )

            self._active_deployments[config.deployment_id] = deployment

            # Initialize traffic routing
            await self._setup_initial_routing(deployment)

            # Start deployment process
            deployment.state = CanaryState.INITIALIZING
            await self._run_smoke_tests(deployment)

            deployment.state = CanaryState.RAMPING
            deployment.current_traffic = config.initial_traffic

            self.logger.info(
                f"Started canary deployment {config.deployment_id} for "
                f"{config.service_name} v{config.version}"
            )

            # Update metrics
            self.metrics_collector.increment_counter(
                "canary_deployments_total",
                labels={"strategy": config.strategy.value, "result": "started"}
            )

            # Constellation Framework coordination
            if self.constellation:
                await self.constellation.coordinate_deployment(
                    config.deployment_id, config.service_name, config.version
                )

            return config.deployment_id

        except Exception as e:
            self.logger.error(f"Error starting canary deployment: {e}")
            if config.deployment_id in self._active_deployments:
                del self._active_deployments[config.deployment_id]
            raise

    async def _validate_config(self, config: CanaryConfig):
        """Validate deployment configuration"""
        if config.initial_traffic < 0 or config.initial_traffic > 100:
            raise ValueError("initial_traffic must be between 0 and 100")

        if config.target_traffic < config.initial_traffic:
            raise ValueError("target_traffic must be >= initial_traffic")

        if config.step_size <= 0 or config.step_size > 100:
            raise ValueError("step_size must be between 0 and 100")

        if config.max_error_rate <= 0 or config.max_error_rate >= 1:
            raise ValueError("max_error_rate must be between 0 and 1")

        # Validate lane assignment
        lane_config = await self.lane_manager.get_lane_assignment(config.service_name)
        if not lane_config:
            await self.lane_manager.assign_service_to_lane(
                config.service_name, "deployment", config.target_lane
            )

    def _find_conflicting_deployment(self, config: CanaryConfig) -> Optional[CanaryDeployment]:
        """Find conflicting active deployments"""
        for deployment in self._active_deployments.values():
            if (deployment.config.service_name == config.service_name and
                deployment.state in [CanaryState.RAMPING, CanaryState.MONITORING]):
                return deployment
        return None

    async def _setup_initial_routing(self, deployment: CanaryDeployment):
        """Setup initial traffic routing for deployment"""
        config = deployment.config

        # Configure lane for canary traffic
        await self.lane_manager.assign_service_to_lane(
            f"{config.service_name}_canary",
            "canary",
            config.target_lane
        )

        # Initialize traffic distribution
        await self._update_traffic_distribution(deployment, 0.0)

    async def _run_smoke_tests(self, deployment: CanaryDeployment):
        """Run smoke tests for the deployment"""
        config = deployment.config

        if not config.smoke_tests:
            return

        self.logger.info(f"Running smoke tests for deployment {config.deployment_id}")

        for test_name in config.smoke_tests:
            try:
                # Run smoke test (implementation would depend on test framework)
                await self._execute_smoke_test(test_name, deployment)
                self.logger.info(f"Smoke test {test_name} passed")

            except Exception as e:
                error_msg = f"Smoke test {test_name} failed: {e}"
                deployment.errors.append(error_msg)
                deployment.state = CanaryState.FAILED
                deployment.rollback_reason = f"smoke_test_failure: {test_name}"
                raise LUKHASError(error_msg)

    async def _execute_smoke_test(self, test_name: str, deployment: CanaryDeployment):
        """Execute a specific smoke test"""
        # Placeholder for actual smoke test execution
        # This would integrate with your testing framework
        await asyncio.sleep(1)  # Simulate test execution

        # Simulate some failures for demonstration
        if test_name == "failing_test":
            raise Exception("Simulated test failure")

    async def _controller_loop(self):
        """Main controller loop"""
        while self._running:
            try:
                await self._process_active_deployments()
                await asyncio.sleep(10)  # Process every 10 seconds

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in controller loop: {e}")
                await asyncio.sleep(30)

    async def _process_active_deployments(self):
        """Process all active deployments"""
        for deployment_id in list(self._active_deployments.keys()):
            deployment = self._active_deployments[deployment_id]

            try:
                await self._process_deployment(deployment)
            except Exception as e:
                self.logger.error(
                    f"Error processing deployment {deployment_id}: {e}"
                )
                deployment.errors.append(str(e))
                await self._initiate_rollback(deployment, f"processing_error: {e}")

    async def _process_deployment(self, deployment: CanaryDeployment):
        """Process a single deployment"""
        if deployment.state == CanaryState.RAMPING:
            await self._process_ramping(deployment)
        elif deployment.state == CanaryState.MONITORING:
            await self._process_monitoring(deployment)
        elif deployment.state == CanaryState.COMPLETING:
            await self._process_completing(deployment)
        elif deployment.state == CanaryState.ROLLING_BACK:
            await self._process_rollback(deployment)

    async def _process_ramping(self, deployment: CanaryDeployment):
        """Process deployment in ramping state"""
        config = deployment.config

        # Collect current metrics
        metrics = await self._collect_deployment_metrics(deployment)
        deployment.metrics_history.append(metrics)

        # Check SLA violations
        if await self._check_sla_violations(deployment, metrics):
            await self._initiate_rollback(deployment, "sla_violation")
            return

        # Check if we need to increase traffic
        step_elapsed = (datetime.now() - deployment.started_at).total_seconds()
        expected_step = int(step_elapsed / config.step_duration)

        if expected_step > deployment.current_step:
            new_traffic = min(
                deployment.current_traffic + config.step_size,
                config.target_traffic
            )

            await self._update_traffic_distribution(deployment, new_traffic)
            deployment.current_step = expected_step
            deployment.current_traffic = new_traffic

            self.logger.info(
                f"Increased traffic for deployment {config.deployment_id} "
                f"to {new_traffic:.1f}%"
            )

            # Check if ramping is complete
            if new_traffic >= config.target_traffic:
                deployment.state = CanaryState.MONITORING

    async def _process_monitoring(self, deployment: CanaryDeployment):
        """Process deployment in monitoring state"""
        config = deployment.config

        # Collect metrics
        metrics = await self._collect_deployment_metrics(deployment)
        deployment.metrics_history.append(metrics)

        # Check SLA violations
        if await self._check_sla_violations(deployment, metrics):
            await self._initiate_rollback(deployment, "sla_violation_monitoring")
            return

        # Check if monitoring period is complete
        monitoring_elapsed = (datetime.now() - deployment.started_at).total_seconds()
        if monitoring_elapsed >= config.monitoring_duration:
            deployment.state = CanaryState.COMPLETING

    async def _process_completing(self, deployment: CanaryDeployment):
        """Process deployment in completing state"""
        try:
            # Finalize deployment
            await self._finalize_deployment(deployment)
            deployment.state = CanaryState.COMPLETED
            deployment.completed_at = datetime.now()

            # Move to history
            self._deployment_history.append(deployment)
            del self._active_deployments[deployment.config.deployment_id]

            duration = (deployment.completed_at - deployment.started_at).total_seconds()
            self.logger.info(
                f"Completed canary deployment {deployment.config.deployment_id} "
                f"in {duration:.0f} seconds"
            )

            # Update metrics
            self.metrics_collector.record_histogram(
                "canary_deployment_duration_seconds", duration
            )
            self.metrics_collector.increment_counter(
                "canary_deployments_total",
                labels={
                    "strategy": deployment.config.strategy.value,
                    "result": "completed"
                }
            )

        except Exception as e:
            self.logger.error(f"Error completing deployment: {e}")
            await self._initiate_rollback(deployment, f"completion_error: {e}")

    async def _process_rollback(self, deployment: CanaryDeployment):
        """Process deployment in rollback state"""
        try:
            await self._execute_rollback(deployment)
            deployment.state = CanaryState.FAILED
            deployment.completed_at = datetime.now()

            # Move to history
            self._deployment_history.append(deployment)
            del self._active_deployments[deployment.config.deployment_id]

            self.logger.info(
                f"Rolled back deployment {deployment.config.deployment_id}: "
                f"{deployment.rollback_reason}"
            )

            # Update metrics
            self.metrics_collector.increment_counter(
                "canary_rollbacks_total",
                labels={
                    "reason": deployment.rollback_reason or "unknown",
                    "service_name": deployment.config.service_name
                }
            )

        except Exception as e:
            self.logger.error(f"Error during rollback: {e}")
            deployment.errors.append(f"rollback_error: {e}")

    async def _collect_deployment_metrics(self, deployment: CanaryDeployment) -> CanaryMetrics:
        """Collect real-time metrics for a deployment"""
        config = deployment.config

        # This would integrate with actual metrics collection
        # For now, simulate metrics based on deployment state
        error_rate = await self._get_service_error_rate(config.service_name)
        latency_p95 = await self._get_service_latency(config.service_name, 95)
        latency_p99 = await self._get_service_latency(config.service_name, 99)
        success_rate = 1.0 - error_rate
        throughput = await self._get_service_throughput(config.service_name)

        # Calculate health score
        health_score = self._calculate_deployment_health(
            error_rate, latency_p95, success_rate, config
        )

        return CanaryMetrics(
            deployment_id=config.deployment_id,
            timestamp=datetime.now(),
            current_traffic=deployment.current_traffic,
            error_rate=error_rate,
            latency_p95=latency_p95,
            latency_p99=latency_p99,
            success_rate=success_rate,
            throughput_rps=throughput,
            health_score=health_score,
            sla_violations=len([m for m in deployment.metrics_history
                              if m.error_rate > config.max_error_rate]),
            active_connections=100  # Placeholder
        )

    async def _get_service_error_rate(self, service_name: str) -> float:
        """Get error rate for a service (simulated)"""
        # This would query actual metrics
        return 0.01  # 1% error rate

    async def _get_service_latency(self, service_name: str, percentile: int) -> float:
        """Get latency percentile for a service (simulated)"""
        base = 0.05 if percentile == 95 else 0.08
        return base

    async def _get_service_throughput(self, service_name: str) -> float:
        """Get throughput for a service (simulated)"""
        return 50.0  # 50 RPS

    def _calculate_deployment_health(
        self,
        error_rate: float,
        latency: float,
        success_rate: float,
        config: CanaryConfig
    ) -> float:
        """Calculate overall health score for deployment"""
        error_score = max(0.0, 1.0 - (error_rate / config.max_error_rate))
        latency_score = max(0.0, 1.0 - (latency / config.max_latency_p95))
        success_score = success_rate

        return (error_score * 0.4 + latency_score * 0.3 + success_score * 0.3)

    async def _check_sla_violations(
        self,
        deployment: CanaryDeployment,
        metrics: CanaryMetrics
    ) -> bool:
        """Check if current metrics violate SLA thresholds"""
        config = deployment.config

        violations = []

        if metrics.error_rate > config.max_error_rate:
            violations.append(f"error_rate {metrics.error_rate:.3f} > {config.max_error_rate:.3f}")

        if metrics.latency_p95 > config.max_latency_p95:
            violations.append(f"latency_p95 {metrics.latency_p95:.3f} > {config.max_latency_p95:.3f}")

        if metrics.success_rate < config.min_success_rate:
            violations.append(f"success_rate {metrics.success_rate:.3f} < {config.min_success_rate:.3f}")

        if violations and config.rollback_on_sla_violation:
            self.logger.warning(
                f"SLA violations detected for deployment {config.deployment_id}: "
                f"{', '.join(violations)}"
            )
            return True

        return False

    async def _update_traffic_distribution(
        self,
        deployment: CanaryDeployment,
        traffic_percentage: float
    ):
        """Update traffic distribution for deployment"""
        config = deployment.config

        # Update metrics
        self.metrics_collector.set_gauge(
            "canary_traffic_percentage",
            traffic_percentage,
            labels={
                "deployment_id": config.deployment_id,
                "service_name": config.service_name
            }
        )

        # This would update actual traffic routing
        # For now, just log the change
        self.logger.info(
            f"Updated traffic for deployment {config.deployment_id} to {traffic_percentage:.1f}%"
        )

    async def _initiate_rollback(self, deployment: CanaryDeployment, reason: str):
        """Initiate rollback for a deployment"""
        deployment.state = CanaryState.ROLLING_BACK
        deployment.rollback_reason = reason

        self.logger.warning(
            f"Initiating rollback for deployment {deployment.config.deployment_id}: {reason}"
        )

        # Execute rollback callbacks
        callbacks = self._rollback_callbacks.get(deployment.config.deployment_id, [])
        for callback in callbacks:
            try:
                await callback(deployment, reason)
            except Exception as e:
                self.logger.error(f"Error in rollback callback: {e}")

    async def _execute_rollback(self, deployment: CanaryDeployment):
        """Execute rollback for a deployment"""
        config = deployment.config

        # Revert traffic to 0%
        await self._update_traffic_distribution(deployment, 0.0)

        # Clean up canary resources
        await self.lane_manager.force_lane_switch(
            config.target_lane, Lane.MATRIZ, "rollback"
        )

        self.logger.info(f"Executed rollback for deployment {config.deployment_id}")

    async def _finalize_deployment(self, deployment: CanaryDeployment):
        """Finalize successful deployment"""
        config = deployment.config

        # Promote canary to full production
        await self._update_traffic_distribution(deployment, 100.0)

        # Update service version
        # This would update service registry, configuration, etc.

        self.logger.info(f"Finalized deployment {config.deployment_id}")

    async def pause_deployment(self, deployment_id: str) -> bool:
        """Pause an active deployment"""
        if deployment_id not in self._active_deployments:
            return False

        deployment = self._active_deployments[deployment_id]
        if deployment.state in [CanaryState.RAMPING, CanaryState.MONITORING]:
            deployment.state = CanaryState.PAUSED
            self.logger.info(f"Paused deployment {deployment_id}")
            return True

        return False

    async def resume_deployment(self, deployment_id: str) -> bool:
        """Resume a paused deployment"""
        if deployment_id not in self._active_deployments:
            return False

        deployment = self._active_deployments[deployment_id]
        if deployment.state == CanaryState.PAUSED:
            deployment.state = CanaryState.RAMPING
            self.logger.info(f"Resumed deployment {deployment_id}")
            return True

        return False

    async def cancel_deployment(self, deployment_id: str, reason: str = "manual") -> bool:
        """Cancel an active deployment"""
        if deployment_id not in self._active_deployments:
            return False

        deployment = self._active_deployments[deployment_id]
        await self._initiate_rollback(deployment, f"cancelled: {reason}")
        return True

    async def get_deployment_status(self, deployment_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a deployment"""
        if deployment_id in self._active_deployments:
            deployment = self._active_deployments[deployment_id]
        else:
            # Check history
            deployment = next(
                (d for d in self._deployment_history if d.config.deployment_id == deployment_id),
                None
            )

        if not deployment:
            return None

        latest_metrics = deployment.metrics_history[-1] if deployment.metrics_history else None

        return {
            "deployment_id": deployment_id,
            "state": deployment.state.value,
            "config": {
                "service_name": deployment.config.service_name,
                "version": deployment.config.version,
                "strategy": deployment.config.strategy.value,
                "target_lane": deployment.config.target_lane.value
            },
            "progress": {
                "current_step": deployment.current_step,
                "current_traffic": deployment.current_traffic,
                "target_traffic": deployment.config.target_traffic
            },
            "timing": {
                "started_at": deployment.started_at.isoformat(),
                "completed_at": deployment.completed_at.isoformat() if deployment.completed_at else None
            },
            "metrics": {
                "error_rate": latest_metrics.error_rate if latest_metrics else 0.0,
                "latency_p95": latest_metrics.latency_p95 if latest_metrics else 0.0,
                "health_score": latest_metrics.health_score if latest_metrics else 0.0
            },
            "errors": deployment.errors,
            "rollback_reason": deployment.rollback_reason
        }

    async def list_active_deployments(self) -> List[Dict[str, Any]]:
        """List all active deployments"""
        return [
            await self.get_deployment_status(deployment_id)
            for deployment_id in self._active_deployments.keys()
        ]

    def register_rollback_callback(
        self,
        deployment_id: str,
        callback: Callable[[CanaryDeployment, str], Any]
    ):
        """Register callback for rollback events"""
        if deployment_id not in self._rollback_callbacks:
            self._rollback_callbacks[deployment_id] = []
        self._rollback_callbacks[deployment_id].append(callback)

    async def _health_check(self) -> Dict[str, Any]:
        """Health check for Constellation Framework"""
        return {
            "status": "healthy" if self._running else "stopped",
            "active_deployments": len(self._active_deployments),
            "total_deployments": len(self._deployment_history) + len(self._active_deployments),
            "states": {
                state.value: len([d for d in self._active_deployments.values() if d.state == state])
                for state in CanaryState
            }
        }