"""
Orchestrator Timeout Management
================================

Configurable timeout infrastructure for async cognitive pipelines.
Prevents indefinite hangs with graceful degradation.

Timeout Strategy:
- Per-stage configurable timeouts
- Cascading timeout prevention (parent > children)
- Graceful degradation (partial results on timeout)
- Forensic logging and metrics
"""

from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional
import asyncio
import time

try:
    from prometheus_client import Counter, Histogram
    TIMEOUT_TOTAL = Counter(
        "lukhas_orchestrator_timeouts_total",
        "Total timeout events",
        ["stage", "lane"]
    )
    STAGE_DURATION = Histogram(
        "lukhas_orchestrator_stage_duration_seconds",
        "Stage processing duration",
        ["stage", "lane"],
        buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0]
    )
    PROM = True
except Exception:
    class _N:
        def labels(self, *_, **__): return self
        def inc(self, *_): pass
        def observe(self, *_): pass
    TIMEOUT_TOTAL = _N()
    STAGE_DURATION = _N()
    PROM = False


@dataclass
class TimeoutConfig:
    """Per-stage timeout configuration"""
    memory_retrieval_s: float = 1.0
    matriz_processing_s: float = 5.0
    llm_generation_s: float = 10.0
    guardian_check_s: float = 0.5
    total_pipeline_s: float = 20.0  # Must exceed sum of stages

    def validate(self):
        """Ensure cascading timeout constraint"""
        stage_sum = (
            self.memory_retrieval_s +
            self.matriz_processing_s +
            self.llm_generation_s +
            self.guardian_check_s
        )
        if self.total_pipeline_s <= stage_sum:
            raise ValueError(
                f"Total pipeline timeout ({self.total_pipeline_s}s) must exceed "
                f"sum of stage timeouts ({stage_sum}s)"
            )


@dataclass
class TimeoutResult:
    """Result from timed execution"""
    success: bool
    result: Any
    duration_s: float
    timed_out: bool
    partial_result: Optional[Any] = None


class TimeoutManager:
    """
    Manage timeouts for async orchestrator stages.

    Features:
    - Per-stage timeout enforcement
    - Graceful degradation (partial results)
    - Cascading timeout validation
    - Forensic logging on timeout
    - Prometheus metrics
    """

    def __init__(self, config: Optional[TimeoutConfig] = None, lane: str = "experimental"):
        self.config = config or TimeoutConfig()
        self.config.validate()
        self.lane = lane

    async def run_with_timeout(
        self,
        coro: Callable,
        stage: str,
        timeout_s: float,
        fallback_result: Optional[Any] = None
    ) -> TimeoutResult:
        """
        Run async coroutine with timeout.

        Args:
            coro: Async coroutine to execute
            stage: Stage name (for metrics)
            timeout_s: Timeout in seconds
            fallback_result: Result to return on timeout

        Returns:
            TimeoutResult with success/failure info
        """
        t0 = time.perf_counter()

        try:
            result = await asyncio.wait_for(coro, timeout=timeout_s)
            duration = time.perf_counter() - t0

            if PROM:
                STAGE_DURATION.labels(stage=stage, lane=self.lane).observe(duration)

            return TimeoutResult(
                success=True,
                result=result,
                duration_s=duration,
                timed_out=False
            )

        except asyncio.TimeoutError:
            duration = time.perf_counter() - t0

            # Log timeout
            print(f"[TIMEOUT] Stage '{stage}' timed out after {duration:.2f}s (limit: {timeout_s}s)")

            # Increment metric
            if PROM:
                TIMEOUT_TOTAL.labels(stage=stage, lane=self.lane).inc()
                STAGE_DURATION.labels(stage=stage, lane=self.lane).observe(timeout_s)

            return TimeoutResult(
                success=False,
                result=None,
                duration_s=timeout_s,
                timed_out=True,
                partial_result=fallback_result
            )

        except Exception as e:
            duration = time.perf_counter() - t0
            print(f"[ERROR] Stage '{stage}' failed: {e}")

            return TimeoutResult(
                success=False,
                result=None,
                duration_s=duration,
                timed_out=False
            )

    async def run_pipeline(
        self,
        stages: Dict[str, Callable],
        stage_timeouts: Optional[Dict[str, float]] = None
    ) -> Dict[str, TimeoutResult]:
        """
        Run full pipeline with per-stage timeouts.

        Args:
            stages: Dict of stage_name -> async_coroutine
            stage_timeouts: Optional per-stage timeout overrides

        Returns:
            Dict of stage_name -> TimeoutResult
        """
        results = {}

        # Use default timeouts if not provided
        timeouts = stage_timeouts or {
            "memory_retrieval": self.config.memory_retrieval_s,
            "matriz_processing": self.config.matriz_processing_s,
            "llm_generation": self.config.llm_generation_s,
            "guardian_check": self.config.guardian_check_s,
        }

        # Execute stages sequentially with timeouts
        for stage_name, coro in stages.items():
            timeout = timeouts.get(stage_name, 5.0)  # Default 5s

            result = await self.run_with_timeout(
                coro=coro,
                stage=stage_name,
                timeout_s=timeout
            )

            results[stage_name] = result

            # Stop pipeline if critical stage timed out
            if result.timed_out and stage_name in ["memory_retrieval", "guardian_check"]:
                print(f"[HALT] Critical stage '{stage_name}' timed out - halting pipeline")
                break

        return results
