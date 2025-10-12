"""
Migration Router for LUKHAS Orchestrator System
Provides intelligent routing between legacy and new orchestrators during migration
"""
import streamlit as st
from datetime import timezone

import asyncio
import logging
import time
import traceback
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Optional, Union

# Import orchestrator flags dynamically to avoid circular imports
# from .orchestrator_flags import OrchestratorFlags, OrchestrationMode, get_orchestrator_flags

logger = logging.getLogger(__name__)


@dataclass
class OrchestrationResult:
    """Result of orchestrator execution"""

    success: bool
    result: Any = None
    error: Optional[str] = None
    execution_time_ms: float = 0.0
    orchestrator_type: str = "unknown"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ShadowComparisonResult:
    """Result of comparing legacy and new orchestrator outputs"""

    legacy_result: OrchestrationResult
    new_result: OrchestrationResult
    results_match: bool
    differences: dict[str, Any] = field(default_factory=dict)
    comparison_time_ms: float = 0.0


class CircuitBreaker:
    """Circuit breaker for orchestrator failure protection"""

    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def can_execute(self) -> bool:
        """Check if execution is allowed"""
        if self.state == "CLOSED":
            return True
        elif self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
                return True
            return False
        else:  # HALF_OPEN
            return True

    def record_success(self):
        """Record successful execution"""
        if self.state == "HALF_OPEN":
            self.state = "CLOSED"
        self.failure_count = 0

    def record_failure(self):
        """Record failed execution"""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.warning(f"Circuit breaker opened after {self.failure_count} failures")


class PerformanceMetrics:
    """Track performance metrics for orchestrators"""

    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.execution_times = []
        self.error_count = 0
        self.success_count = 0
        self.total_requests = 0

    def record_execution(self, execution_time_ms: float, success: bool):
        """Record an execution"""
        self.execution_times.append(execution_time_ms)
        if len(self.execution_times) > self.window_size:
            self.execution_times.pop(0)

        self.total_requests += 1
        if success:
            self.success_count += 1
        else:
            self.error_count += 1

    def get_avg_latency(self) -> float:
        """Get average latency in milliseconds"""
        if not self.execution_times:
            return 0.0
        return sum(self.execution_times) / len(self.execution_times)

    def get_error_rate(self) -> float:
        """Get error rate as a percentage"""
        if self.total_requests == 0:
            return 0.0
        return self.error_count / self.total_requests

    def get_p95_latency(self) -> float:
        """Get 95th percentile latency"""
        if not self.execution_times:
            return 0.0
        sorted_times = sorted(self.execution_times)
        index = int(len(sorted_times) * 0.95)
        return sorted_times[min(index, len(sorted_times) - 1)]


class ShadowOrchestrator:
    """Executes orchestrators in shadow mode for comparison"""

    def __init__(self, name: str):
        self.name = name
        self.comparisons: list[ShadowComparisonResult] = []
        self.max_comparisons = 1000

    async def execute_shadow(
        self,
        legacy_orchestrator: Callable,
        new_orchestrator: Callable,
        *args,
        **kwargs,
    ) -> ShadowComparisonResult:
        """Execute both orchestrators and compare results"""
        start_time = time.time()

        # Execute legacy orchestrator (primary)
        legacy_result = await self._execute_orchestrator(legacy_orchestrator, "legacy", *args, **kwargs)

        # Execute new orchestrator (shadow)
        new_result = await self._execute_orchestrator(new_orchestrator, "new", *args, **kwargs)

        # Compare results
        results_match, differences = self._compare_results(legacy_result.result, new_result.result)

        comparison_time_ms = (time.time() - start_time) * 1000

        comparison = ShadowComparisonResult(
            legacy_result=legacy_result,
            new_result=new_result,
            results_match=results_match,
            differences=differences,
            comparison_time_ms=comparison_time_ms,
        )

        # Store comparison (with size limit)
        self.comparisons.append(comparison)
        if len(self.comparisons) > self.max_comparisons:
            self.comparisons.pop(0)

        # Log comparison results
        self._log_comparison(comparison)

        return comparison

    async def _execute_orchestrator(
        self, orchestrator: Callable, orchestrator_type: str, *args, **kwargs
    ) -> OrchestrationResult:
        """Execute a single orchestrator safely"""
        start_time = time.time()

        try:
            if asyncio.iscoroutinefunction(orchestrator):
                result = await orchestrator(*args, **kwargs)
            else:
                result = orchestrator(*args, **kwargs)

            execution_time_ms = (time.time() - start_time) * 1000

            return OrchestrationResult(
                success=True,
                result=result,
                execution_time_ms=execution_time_ms,
                orchestrator_type=orchestrator_type,
            )

        except Exception as e:
            execution_time_ms = (time.time() - start_time) * 1000
            error_msg = f"{type(e)}.__name__}: {e!s}"  # noqa: invalid-syntax

            logger.warning(
                "Orchestrator execution failed",
                orchestrator_type=orchestrator_type,
                error=error_msg,
                execution_time_ms=execution_time_ms,
            )

            return OrchestrationResult(
                success=False,
                error=error_msg,
                execution_time_ms=execution_time_ms,
                orchestrator_type=orchestrator_type,
                metadata={"traceback": traceback.format_exc()},
            )

    def _compare_results(self, legacy_result: Any, new_result: Any) -> tuple[bool, dict[str, Any]]:
        """Compare orchestrator results for equivalence"""
        try:
            differences = {}

            # Type comparison
            if not isinstance(legacy_result, type(new_result)):
                differences["type_mismatch"] = {
                    "legacy_type": str(type(legacy_result)),
                    "new_type": str(type(new_result)),
                }

            # Content comparison
            if legacy_result == new_result:
                return True, {}

            # Deep comparison for complex objects
            if isinstance(legacy_result, dict) and isinstance(new_result, dict):
                differences.update(self._compare_dicts(legacy_result, new_result))
            elif isinstance(legacy_result, (list, tuple)) and isinstance(new_result, (list, tuple)):
                differences.update(self._compare_sequences(legacy_result, new_result))
            else:
                differences["value_mismatch"] = {
                    "legacy_value": str(legacy_result),
                    "new_value": str(new_result),
                }

            return len(differences) == 0, differences

        except Exception as e:
            logger.warning(f"Result comparison failed: {e}")
            return False, {"comparison_error": str(e)}

    def _compare_dicts(self, legacy: dict, new: dict) -> dict[str, Any]:
        """Compare dictionary results"""
        differences = {}

        all_keys = set(legacy.keys()) | set(new.keys())

        for key in all_keys:
            if key not in legacy:
                differences[f"missing_in_legacy.{key}"] = new[key]
            elif key not in new:
                differences[f"missing_in_new.{key}"] = legacy[key]
            elif legacy[key] != new[key]:
                differences[f"different_value.{key}"] = {
                    "legacy": legacy[key],
                    "new": new[key],
                }

        return differences

    def _compare_sequences(self, legacy: Union[list, tuple], new: Union[list, tuple]) -> dict[str, Any]:
        """Compare sequence results"""
        differences = {}

        if len(legacy) != len(new):
            differences["length_mismatch"] = {
                "legacy_length": len(legacy),
                "new_length": len(new),
            }

        min_length = min(len(legacy), len(new))
        for i in range(min_length):
            if legacy[i] != new[i]:
                differences[f"different_item.{i}"] = {
                    "legacy": legacy[i],
                    "new": new[i],
                }

        return differences

    def _log_comparison(self, comparison: ShadowComparisonResult):
        """Log shadow comparison results"""
        logger.info(
            "Shadow orchestrator comparison completed",
            orchestrator_name=self.name,
            results_match=comparison.results_match,
            legacy_success=comparison.legacy_result.success,
            new_success=comparison.new_result.success,
            legacy_time_ms=comparison.legacy_result.execution_time_ms,
            new_time_ms=comparison.new_result.execution_time_ms,
            comparison_time_ms=comparison.comparison_time_ms,
            differences_count=len(comparison.differences),
        )

    def get_comparison_summary(self) -> dict[str, Any]:
        """Get summary of shadow comparisons"""
        if not self.comparisons:
            return {"total_comparisons": 0}

        total = len(self.comparisons)
        matches = sum(1 for c in self.comparisons if c.results_match)
        legacy_successes = sum(1 for c in self.comparisons if c.legacy_result.success)
        new_successes = sum(1 for c in self.comparisons if c.new_result.success)

        avg_legacy_time = sum(c.legacy_result.execution_time_ms for c in self.comparisons) / total
        avg_new_time = sum(c.new_result.execution_time_ms for c in self.comparisons) / total

        return {
            "total_comparisons": total,
            "result_match_rate": matches / total,
            "legacy_success_rate": legacy_successes / total,
            "new_success_rate": new_successes / total,
            "avg_legacy_time_ms": avg_legacy_time,
            "avg_new_time_ms": avg_new_time,
            "performance_improvement": (
                (avg_legacy_time - avg_new_time) / avg_legacy_time if avg_legacy_time > 0 else 0
            ),
        }


class OrchestratorRouter:
    """Main router for orchestrator migration"""

    def __init__(self):
        self.circuit_breakers: dict[str, CircuitBreaker] = {}
        self.performance_metrics: dict[str, PerformanceMetrics] = {}
        self.shadow_orchestrators: dict[str, ShadowOrchestrator] = {}
        self.flags = None  # Will be loaded on first use

    def _get_flags(self):
        """Get orchestrator flags with delayed import"""
        if self.flags is None:
            try:
                from .orchestrator_flags import get_orchestrator_flags

                self.flags = get_orchestrator_flags()
            except ImportError:
                # Create minimal flags for testing
                from dataclasses import dataclass
                from enum import Enum

                class OrchestrationMode(Enum):
                    LEGACY = "legacy"
                    SHADOW = "shadow"
                    CANARY = "canary"
                    NEW = "new"

                @dataclass
                class MinimalFlags:
                    def get_orchestrator_mode(self, name):
                        return OrchestrationMode.LEGACY

                    def is_orchestrator_enabled(self, name):
                        return True

                    def should_use_new_orchestrator(self, name, user_id=None):
                        return False

                    def should_use_legacy_orchestrator(self, name):
                        return True

                self.flags = MinimalFlags()
        return self.flags

    async def route_orchestrator(
        self,
        orchestrator_name: str,
        legacy_orchestrator: Callable,
        new_orchestrator: Callable,
        user_id: Optional[str] = None,
        *args,
        **kwargs,
    ) -> Any:
        """Route orchestrator execution based on configuration"""

        # Get flags
        flags = self._get_flags()

        # Check if orchestrator is enabled
        if not flags.is_orchestrator_enabled(orchestrator_name):
            raise ValueError(f"Orchestrator '{orchestrator_name}' is disabled")

        # Get orchestrator mode
        mode = flags.get_orchestrator_mode(orchestrator_name)

        # Initialize metrics and circuit breaker if needed
        self._ensure_orchestrator_tracking(orchestrator_name)

        # Check circuit breaker
        circuit_breaker = self.circuit_breakers[orchestrator_name]
        if not circuit_breaker.can_execute():
            logger.warning(f"Circuit breaker is open for {orchestrator_name}, using fallback")
            return await self._execute_fallback(orchestrator_name, *args, **kwargs)

        try:
            # Use string comparison to avoid import issues
            mode_str = getattr(mode, "value", str(mode))

            if mode_str == "legacy":
                return await self._execute_legacy_only(orchestrator_name, legacy_orchestrator, *args, **kwargs)

            elif mode_str == "new":
                return await self._execute_new_only(orchestrator_name, new_orchestrator, *args, **kwargs)

            elif mode_str == "shadow":
                return await self._execute_shadow_mode(
                    orchestrator_name,
                    legacy_orchestrator,
                    new_orchestrator,
                    *args,
                    **kwargs,
                )

            elif mode_str == "parallel":
                return await self._execute_parallel_mode(
                    orchestrator_name,
                    legacy_orchestrator,
                    new_orchestrator,
                    *args,
                    **kwargs,
                )

            elif mode_str == "canary":
                return await self._execute_canary_mode(
                    orchestrator_name,
                    legacy_orchestrator,
                    new_orchestrator,
                    user_id,
                    *args,
                    **kwargs,
                )

            else:
                raise ValueError(f"Unknown orchestration mode: {mode}")

        except Exception:
            circuit_breaker.record_failure()
            self._record_metrics(orchestrator_name, 0, False)
            raise

    async def _execute_legacy_only(
        self,
        orchestrator_name: str,
        legacy_orchestrator: Callable,
        *args,
        **kwargs,
    ) -> Any:
        """Execute only the legacy orchestrator"""
        start_time = time.time()

        try:
            if asyncio.iscoroutinefunction(legacy_orchestrator):
                result = await legacy_orchestrator(*args, **kwargs)
            else:
                result = legacy_orchestrator(*args, **kwargs)

            execution_time_ms = (time.time() - start_time) * 1000
            self._record_metrics(orchestrator_name, execution_time_ms, True)
            self.circuit_breakers[orchestrator_name].record_success()

            return result

        except Exception:
            execution_time_ms = (time.time() - start_time) * 1000
            self._record_metrics(orchestrator_name, execution_time_ms, False)
            self.circuit_breakers[orchestrator_name].record_failure()
            raise

    async def _execute_new_only(
        self,
        orchestrator_name: str,
        new_orchestrator: Callable,
        *args,
        **kwargs,
    ) -> Any:
        """Execute only the new orchestrator"""
        start_time = time.time()

        try:
            if asyncio.iscoroutinefunction(new_orchestrator):
                result = await new_orchestrator(*args, **kwargs)
            else:
                result = new_orchestrator(*args, **kwargs)

            execution_time_ms = (time.time() - start_time) * 1000
            self._record_metrics(orchestrator_name, execution_time_ms, True)
            self.circuit_breakers[orchestrator_name].record_success()

            return result

        except Exception:
            execution_time_ms = (time.time() - start_time) * 1000
            self._record_metrics(orchestrator_name, execution_time_ms, False)
            self.circuit_breakers[orchestrator_name].record_failure()
            raise

    async def _execute_shadow_mode(
        self,
        orchestrator_name: str,
        legacy_orchestrator: Callable,
        new_orchestrator: Callable,
        *args,
        **kwargs,
    ) -> Any:
        """Execute in shadow mode (legacy primary, new for comparison)"""
        shadow_orch = self.shadow_orchestrators[orchestrator_name]

        comparison = await shadow_orch.execute_shadow(legacy_orchestrator, new_orchestrator, *args, **kwargs)

        # Record metrics for the primary (legacy) result
        self._record_metrics(
            orchestrator_name,
            comparison.legacy_result.execution_time_ms,
            comparison.legacy_result.success,
        )

        if comparison.legacy_result.success:
            self.circuit_breakers[orchestrator_name].record_success()
            return comparison.legacy_result.result
        else:
            self.circuit_breakers[orchestrator_name].record_failure()
            if comparison.legacy_result.error:
                raise Exception(comparison.legacy_result.error)
            raise Exception("Legacy orchestrator failed")

    async def _execute_parallel_mode(
        self,
        orchestrator_name: str,
        legacy_orchestrator: Callable,
        new_orchestrator: Callable,
        *args,
        **kwargs,
    ) -> Any:
        """Execute in parallel mode (both run, compare, use legacy)"""
        shadow_orch = self.shadow_orchestrators[orchestrator_name]

        comparison = await shadow_orch.execute_shadow(legacy_orchestrator, new_orchestrator, *args, **kwargs)

        # Log detailed comparison
        logger.info(
            "Parallel execution completed",
            orchestrator_name=orchestrator_name,
            results_match=comparison.results_match,
            legacy_faster=comparison.legacy_result.execution_time_ms < comparison.new_result.execution_time_ms,
        )

        # Use legacy result as primary
        self._record_metrics(
            orchestrator_name,
            comparison.legacy_result.execution_time_ms,
            comparison.legacy_result.success,
        )

        if comparison.legacy_result.success:
            self.circuit_breakers[orchestrator_name].record_success()
            return comparison.legacy_result.result
        else:
            self.circuit_breakers[orchestrator_name].record_failure()
            if comparison.legacy_result.error:
                raise Exception(comparison.legacy_result.error)
            raise Exception("Legacy orchestrator failed")

    async def _execute_canary_mode(
        self,
        orchestrator_name: str,
        legacy_orchestrator: Callable,
        new_orchestrator: Callable,
        user_id: Optional[str],
        *args,
        **kwargs,
    ) -> Any:
        """Execute in canary mode (route percentage to new)"""
        flags = self._get_flags()
        use_new = flags.should_use_new_orchestrator(orchestrator_name, user_id)

        if use_new:
            logger.debug(f"Canary routing to new orchestrator for {orchestrator_name}")
            return await self._execute_new_only(orchestrator_name, new_orchestrator, *args, **kwargs)
        else:
            logger.debug(f"Canary routing to legacy orchestrator for {orchestrator_name}")
            return await self._execute_legacy_only(orchestrator_name, legacy_orchestrator, *args, **kwargs)

    async def _execute_fallback(self, orchestrator_name: str, *args, **kwargs) -> Any:
        """Execute fallback when circuit breaker is open"""
        logger.warning(f"Executing fallback for {orchestrator_name}")
        # In a real implementation, this would use a safe fallback orchestrator
        # For now, raise an exception
        raise Exception(f"Orchestrator '{orchestrator_name}' is currently unavailable (circuit breaker open)")

    def _ensure_orchestrator_tracking(self, orchestrator_name: str):
        """Ensure tracking objects exist for orchestrator"""
        if orchestrator_name not in self.circuit_breakers:
            self.circuit_breakers[orchestrator_name] = CircuitBreaker(
                failure_threshold=self.flags.performance.circuit_breaker_failure_threshold,
                recovery_timeout=self.flags.performance.circuit_breaker_recovery_timeout,
            )

        if orchestrator_name not in self.performance_metrics:
            self.performance_metrics[orchestrator_name] = PerformanceMetrics()

        if orchestrator_name not in self.shadow_orchestrators:
            self.shadow_orchestrators[orchestrator_name] = ShadowOrchestrator(orchestrator_name)

    def _record_metrics(self, orchestrator_name: str, execution_time_ms: float, success: bool):
        """Record performance metrics"""
        if orchestrator_name in self.performance_metrics:
            self.performance_metrics[orchestrator_name].record_execution(execution_time_ms, success)

    def get_orchestrator_health(self, orchestrator_name: str) -> dict[str, Any]:
        """Get health status for an orchestrator"""
        if orchestrator_name not in self.performance_metrics:
            return {"status": "unknown", "message": "No metrics available"}

        metrics = self.performance_metrics[orchestrator_name]
        circuit_breaker = self.circuit_breakers.get(orchestrator_name)

        avg_latency = metrics.get_avg_latency()
        error_rate = metrics.get_error_rate()

        # Check if circuit breaker should activate
        should_break = False
        if circuit_breaker and self.flags.enable_circuit_breaker:
            from .orchestrator_flags import should_circuit_break

            should_break = should_circuit_break(orchestrator_name, error_rate, avg_latency)

        # Determine overall health status
        if should_break or (circuit_breaker and circuit_breaker.state == "OPEN"):
            status = "unhealthy"
        elif error_rate > 0.1 or avg_latency > self.flags.max_latency_threshold_ms:
            status = "degraded"
        elif metrics.total_requests == 0:
            status = "unknown"
        else:
            status = "healthy"

        return {
            "status": status,
            "orchestrator_name": orchestrator_name,
            "circuit_breaker_state": (circuit_breaker.state if circuit_breaker else "N/A"),
            "total_requests": metrics.total_requests,
            "success_rate": 1.0 - error_rate,
            "error_rate": error_rate,
            "avg_latency_ms": avg_latency,
            "p95_latency_ms": metrics.get_p95_latency(),
            "last_check": datetime.now(timezone.utc).isoformat(),
        }

    def get_shadow_summary(self, orchestrator_name: str) -> Optional[dict[str, Any]]:
        """Get shadow mode comparison summary"""
        if orchestrator_name not in self.shadow_orchestrators:
            return None

        return self.shadow_orchestrators[orchestrator_name].get_comparison_summary()

    def get_all_orchestrator_status(self) -> dict[str, dict[str, Any]]:
        """Get status for all tracked orchestrators"""
        status = {}

        for orchestrator_name in self.performance_metrics:
            status[orchestrator_name] = self.get_orchestrator_health(orchestrator_name)

            # Add shadow summary if available
            shadow_summary = self.get_shadow_summary(orchestrator_name)
            if shadow_summary:
                status[orchestrator_name]["shadow_mode"] = shadow_summary

        return status


# Global router instance
_orchestrator_router: Optional[OrchestratorRouter] = None


def get_orchestrator_router() -> OrchestratorRouter:
    """Get the global orchestrator router instance"""
    global _orchestrator_router

    if _orchestrator_router is None:
        _orchestrator_router = OrchestratorRouter()

    return _orchestrator_router


@asynccontextmanager
async def orchestrator_context(orchestrator_name: str, user_id: Optional[str] = None):
    """Context manager for orchestrator execution with automatic routing"""
    router = get_orchestrator_router()
    start_time = time.time()

    try:
        yield router
    finally:
        execution_time = (time.time() - start_time) * 1000
        logger.debug(
            "Orchestrator context completed",
            orchestrator_name=orchestrator_name,
            execution_time_ms=execution_time,
        )
