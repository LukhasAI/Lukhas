#!/usr/bin/env python3
"""
MATRIZ Async Cognitive Orchestrator with Timeout Support
T4/0.01% Performance-optimized orchestration with per-stage timeouts.

Features:
- Per-stage timeout enforcement with asyncio.wait_for
- Fail-soft handling for non-critical stages
- Configurable timeouts per stage type
- Performance metrics and budget tracking
"""

import asyncio
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum

from .node_interface import CognitiveNode, NodeReflection, NodeState, NodeTrigger
from .orchestrator import ExecutionTrace


class StageType(Enum):
    """Stage types with default timeout budgets"""
    INTENT = "intent"
    DECISION = "decision"
    PROCESSING = "processing"
    VALIDATION = "validation"
    REFLECTION = "reflection"


class StageConfig:
    """Configuration for stage execution"""

    DEFAULT_TIMEOUTS = {
        StageType.INTENT: 0.05,      # 50ms for intent analysis
        StageType.DECISION: 0.02,     # 20ms for decision
        StageType.PROCESSING: 0.10,   # 100ms for main processing
        StageType.VALIDATION: 0.03,   # 30ms for validation
        StageType.REFLECTION: 0.02,   # 20ms for reflection
    }

    DEFAULT_CRITICAL = {
        StageType.INTENT: True,       # Critical - must understand intent
        StageType.DECISION: True,     # Critical - must select node
        StageType.PROCESSING: True,   # Critical - main work
        StageType.VALIDATION: False,  # Non-critical - can skip
        StageType.REFLECTION: False,  # Non-critical - can skip
    }


@dataclass
class StageResult:
    """Result from a stage execution"""
    stage_type: StageType
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    duration_ms: float = 0.0
    timeout: bool = False


@dataclass
class OrchestrationMetrics:
    """Performance metrics for orchestration"""
    total_duration_ms: float = 0.0
    stage_durations: Dict[str, float] = field(default_factory=dict)
    timeout_count: int = 0
    error_count: int = 0
    stages_completed: int = 0
    stages_skipped: int = 0


async def run_with_timeout(
    coro: Any,
    stage_type: StageType,
    timeout_sec: Optional[float] = None
) -> StageResult:
    """
    Run a coroutine with timeout and error handling.

    Args:
        coro: Coroutine to execute
        stage_type: Type of stage for metrics
        timeout_sec: Timeout in seconds (uses default if None)

    Returns:
        StageResult with execution details
    """
    if timeout_sec is None:
        timeout_sec = StageConfig.DEFAULT_TIMEOUTS[stage_type]

    start = time.perf_counter()

    try:
        result = await asyncio.wait_for(coro, timeout=timeout_sec)
        duration_ms = (time.perf_counter() - start) * 1000

        return StageResult(
            stage_type=stage_type,
            success=True,
            data=result,
            duration_ms=duration_ms,
        )

    except asyncio.TimeoutError:
        duration_ms = (time.perf_counter() - start) * 1000
        return StageResult(
            stage_type=stage_type,
            success=False,
            error=f"Stage {stage_type.value} timed out after {timeout_sec}s",
            duration_ms=duration_ms,
            timeout=True,
        )

    except Exception as e:
        duration_ms = (time.perf_counter() - start) * 1000
        return StageResult(
            stage_type=stage_type,
            success=False,
            error=f"Stage {stage_type.value} error: {str(e)}",
            duration_ms=duration_ms,
        )


class AsyncCognitiveOrchestrator:
    """
    Async orchestrator with per-stage timeouts and fail-soft handling.
    Achieves T4/0.01% performance targets through strict budget enforcement.
    """

    def __init__(
        self,
        stage_timeouts: Optional[Dict[StageType, float]] = None,
        stage_critical: Optional[Dict[StageType, bool]] = None,
        total_timeout: float = 0.250,  # 250ms total budget
    ):
        """
        Initialize async orchestrator with timeout configuration.

        Args:
            stage_timeouts: Custom timeout per stage type
            stage_critical: Whether stage failure should fail pipeline
            total_timeout: Maximum total execution time
        """
        self.available_nodes = {}
        self.context_memory = []
        self.execution_trace = []
        self.matriz_graph = {}

        # Timeout configuration
        self.stage_timeouts = stage_timeouts or StageConfig.DEFAULT_TIMEOUTS
        self.stage_critical = stage_critical or StageConfig.DEFAULT_CRITICAL
        self.total_timeout = total_timeout

        # Performance tracking
        self.metrics = OrchestrationMetrics()
        self.node_health = {}  # Track node performance for adaptive routing

    def register_node(self, name: str, node: "CognitiveNode"):
        """Register a cognitive node"""
        self.available_nodes[name] = node
        self.node_health[name] = {
            "success_count": 0,
            "failure_count": 0,
            "total_duration_ms": 0.0,
            "p95_latency_ms": 0.0,
            "recent_latencies": [],
        }
        print(f"✓ Registered node: {name}")

    async def process_query(self, user_input: str) -> Dict[str, Any]:
        """
        Process user query through MATRIZ nodes with timeout enforcement.

        Args:
            user_input: User's query string

        Returns:
            Result dictionary with answer, trace, and metrics
        """
        start_time = time.perf_counter()
        stage_results = []

        try:
            # Apply total timeout to entire pipeline
            return await asyncio.wait_for(
                self._process_pipeline(user_input, stage_results),
                timeout=self.total_timeout
            )
        except asyncio.TimeoutError:
            total_ms = (time.perf_counter() - start_time) * 1000
            return {
                "error": f"Pipeline timeout exceeded {self.total_timeout}s",
                "partial_results": [asdict(r) for r in stage_results],
                "metrics": {
                    "total_duration_ms": total_ms,
                    "timeout": True,
                }
            }

    async def _process_pipeline(
        self,
        user_input: str,
        stage_results: List[StageResult]
    ) -> Dict[str, Any]:
        """
        Internal pipeline processing with stage management.
        """
        pipeline_start = time.perf_counter()

        # Stage 1: Intent Analysis
        intent_result = await run_with_timeout(
            self._analyze_intent_async(user_input),
            StageType.INTENT,
            self.stage_timeouts[StageType.INTENT]
        )
        stage_results.append(intent_result)

        if not intent_result.success and self.stage_critical[StageType.INTENT]:
            return self._build_error_response(
                "Intent analysis failed",
                stage_results,
                pipeline_start
            )

        intent_node = intent_result.data if intent_result.success else {}

        # Stage 2: Node Selection
        decision_result = await run_with_timeout(
            self._select_node_async(intent_node),
            StageType.DECISION,
            self.stage_timeouts[StageType.DECISION]
        )
        stage_results.append(decision_result)

        if not decision_result.success and self.stage_critical[StageType.DECISION]:
            return self._build_error_response(
                "Node selection failed",
                stage_results,
                pipeline_start
            )

        selected_node_name = decision_result.data if decision_result.success else "default"

        # Stage 3: Main Processing
        if selected_node_name not in self.available_nodes:
            return self._build_error_response(
                f"Node {selected_node_name} not available",
                stage_results,
                pipeline_start
            )

        node = self.available_nodes[selected_node_name]

        # Wrap synchronous node.process in async
        process_result = await run_with_timeout(
            self._process_node_async(node, user_input),
            StageType.PROCESSING,
            self.stage_timeouts[StageType.PROCESSING]
        )
        stage_results.append(process_result)

        if not process_result.success and self.stage_critical[StageType.PROCESSING]:
            return self._build_error_response(
                "Processing failed",
                stage_results,
                pipeline_start
            )

        result = process_result.data if process_result.success else {"answer": "Error occurred"}

        # Stage 4: Validation (non-critical)
        validation_success = False
        if "validator" in self.available_nodes:
            validation_result = await run_with_timeout(
                self._validate_async(result),
                StageType.VALIDATION,
                self.stage_timeouts[StageType.VALIDATION]
            )
            stage_results.append(validation_result)
            validation_success = validation_result.success and validation_result.data

        # Stage 5: Reflection (non-critical)
        if validation_success:
            reflection_result = await run_with_timeout(
                self._create_reflection_async(result, validation_success),
                StageType.REFLECTION,
                self.stage_timeouts[StageType.REFLECTION]
            )
            stage_results.append(reflection_result)

        # Update node health metrics
        self._update_node_health(selected_node_name, process_result)

        # Calculate final metrics
        total_duration_ms = (time.perf_counter() - pipeline_start) * 1000

        return self._build_success_response(
            result,
            stage_results,
            total_duration_ms
        )

    async def _analyze_intent_async(self, user_input: str) -> Dict:
        """Async wrapper for intent analysis"""
        # Simulate async work - in production, could call LLM
        await asyncio.sleep(0)  # Yield control

        # Simple intent detection
        if any(op in user_input for op in ["+", "-", "*", "/", "="]):
            detected_intent = "mathematical"
        elif "?" in user_input.lower():
            detected_intent = "question"
        else:
            detected_intent = "general"

        return {
            "id": f"intent_{int(time.time() * 1000)}",
            "type": "INTENT",
            "intent": detected_intent,
            "confidence": 0.9,
        }

    async def _select_node_async(self, intent_node: Dict) -> str:
        """Async node selection with adaptive routing"""
        await asyncio.sleep(0)  # Yield control

        intent = intent_node.get("intent", "general")

        # Map intent to node type
        intent_map = {
            "mathematical": "math",
            "question": "facts",
            "general": "facts",
        }

        base_node = intent_map.get(intent, "facts")

        # Adaptive selection based on health metrics
        if base_node in self.node_health:
            health = self.node_health[base_node]
            # If node is unhealthy, try alternatives
            if health["failure_count"] > health["success_count"]:
                # Find healthiest alternative
                alternatives = [n for n in self.available_nodes if n != base_node]
                if alternatives:
                    best_alt = min(alternatives,
                                 key=lambda n: self.node_health[n].get("p95_latency_ms", float('inf')))
                    return best_alt

        return base_node

    async def _process_node_async(self, node: CognitiveNode, user_input: str) -> Dict:
        """Async wrapper for node processing"""
        # Run synchronous node.process in executor to make it truly async and cancellable
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, node.process, {"query": user_input})

    async def _validate_async(self, result: Dict) -> bool:
        """Async validation"""
        await asyncio.sleep(0)  # Yield control
        validator = self.available_nodes.get("validator")
        if validator:
            return validator.validate_output(result)
        return True

    async def _create_reflection_async(self, result: Dict, validation: bool) -> Dict:
        """Async reflection creation"""
        await asyncio.sleep(0)  # Yield control
        return {
            "id": f"reflection_{int(time.time() * 1000)}",
            "type": "REFLECTION",
            "validation": validation,
        }

    def _update_node_health(self, node_name: str, result: StageResult):
        """Update node health metrics for adaptive routing"""
        if node_name not in self.node_health:
            return

        health = self.node_health[node_name]

        if result.success:
            health["success_count"] += 1
        else:
            health["failure_count"] += 1

        # Track latency
        health["total_duration_ms"] += result.duration_ms
        health["recent_latencies"].append(result.duration_ms)

        # Keep only last 100 latencies
        if len(health["recent_latencies"]) > 100:
            health["recent_latencies"] = health["recent_latencies"][-100:]

        # Calculate p95
        if health["recent_latencies"]:
            sorted_latencies = sorted(health["recent_latencies"])
            p95_index = int(len(sorted_latencies) * 0.95)
            health["p95_latency_ms"] = sorted_latencies[p95_index]

    def _build_error_response(
        self,
        error: str,
        stage_results: List[StageResult],
        start_time: float
    ) -> Dict[str, Any]:
        """Build error response with metrics"""
        total_ms = (time.perf_counter() - start_time) * 1000

        return {
            "error": error,
            "stages": [asdict(r) for r in stage_results],
            "metrics": {
                "total_duration_ms": total_ms,
                "stages_completed": sum(1 for r in stage_results if r.success),
                "stages_failed": sum(1 for r in stage_results if not r.success),
                "timeout_count": sum(1 for r in stage_results if r.timeout),
            }
        }

    def _build_success_response(
        self,
        result: Dict,
        stage_results: List[StageResult],
        total_duration_ms: float
    ) -> Dict[str, Any]:
        """Build success response with full metrics"""
        stage_durations = {
            r.stage_type.value: r.duration_ms
            for r in stage_results
        }

        return {
            "answer": result.get("answer", "No answer"),
            "confidence": result.get("confidence", 0.0),
            "stages": [asdict(r) for r in stage_results],
            "metrics": {
                "total_duration_ms": total_duration_ms,
                "stage_durations": stage_durations,
                "stages_completed": sum(1 for r in stage_results if r.success),
                "stages_failed": sum(1 for r in stage_results if not r.success),
                "timeout_count": sum(1 for r in stage_results if r.timeout),
                "within_budget": total_duration_ms < self.total_timeout * 1000,
            },
            "node_health": self.node_health,
        }

    def get_performance_report(self) -> Dict[str, Any]:
        """Get detailed performance report"""
        return {
            "node_health": self.node_health,
            "stage_timeouts": {k.value: v for k, v in self.stage_timeouts.items()},
            "stage_critical": {k.value: v for k, v in self.stage_critical.items()},
            "total_timeout": self.total_timeout,
        }