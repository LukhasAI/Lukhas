#!/usr/bin/env python3
"""
Optimized MATRIZ Async Orchestrator for T4/0.01% Tail Latency
Target: p95 < 250ms, p99 within safety margins

Key Optimizations:
- Hot data caching with LRU eviction
- Memory-mapped node access patterns
- Async-first operations with timeouts
- Circuit breakers for outlier protection
- Streamlined MATRIZ node creation
"""

import asyncio
import hashlib
import time
from collections import OrderedDict
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

from matriz.core.async_orchestrator import AsyncCognitiveOrchestrator, StageResult, StageType
from matriz.core.node_interface import CognitiveNode
from observability.matriz_instrumentation import (
import collections
    cognitive_pipeline_span,
    initialize_cognitive_instrumentation,
    instrument_cognitive_stage,
    record_decision_confidence,
    record_focus_drift,
    record_thought_complexity,
)


class CacheType(Enum):
    """Types of caches used in the orchestrator"""
    INTENT_ANALYSIS = "intent"
    NODE_SELECTION = "node_selection"
    NODE_HEALTH = "node_health"
    PROCESSING_RESULTS = "processing"


@dataclass
class CacheEntry:
    """Cache entry with TTL and access tracking"""
    key: str
    value: Any
    created_at: float
    last_accessed: float
    access_count: int = 0
    ttl: float = 60.0  # 1 minute default TTL


class LRUCache:
    """High-performance LRU cache with TTL support"""

    def __init__(self, max_size: int = 1000, default_ttl: float = 60.0):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: collections.collections.OrderedDict[str, CacheEntry] = OrderedDict()
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache, returning None if expired or missing"""
        current_time = time.time()

        if key in self._cache:
            entry = self._cache[key]

            # Check TTL
            if current_time - entry.created_at <= entry.ttl:
                # Move to end (most recently used)
                self._cache.move_to_end(key)
                entry.last_accessed = current_time
                entry.access_count += 1
                self._hits += 1
                return entry.value
            else:
                # Expired, remove
                del self._cache[key]

        self._misses += 1
        return None

    def put(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """Put value in cache with optional custom TTL"""
        current_time = time.time()
        ttl = ttl or self.default_ttl

        # Remove if exists
        if key in self._cache:
            del self._cache[key]

        # Create new entry
        entry = CacheEntry(
            key=key,
            value=value,
            created_at=current_time,
            last_accessed=current_time,
            ttl=ttl
        )

        self._cache[key] = entry

        # Evict if over capacity
        while len(self._cache) > self.max_size:
            self._cache.popitem(last=False)  # Remove least recently used

    def invalidate(self, key: str) -> bool:
        """Invalidate specific cache entry"""
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def clear(self) -> None:
        """Clear all cache entries"""
        self._cache.clear()
        self._hits = 0
        self._misses = 0

    def get_stats(self) -> dict[str, Any]:
        """Get cache performance statistics"""
        total_requests = self._hits + self._misses
        hit_rate = self._hits / total_requests if total_requests > 0 else 0.0

        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": hit_rate,
            "utilization": len(self._cache) / self.max_size
        }


class NodePool:
    """Optimized node pool with health-based routing"""

    def __init__(self):
        self.nodes: dict[str, CognitiveNode] = {}
        self.node_stats: dict[str, dict[str, float]] = {}
        self._node_cache = LRUCache(max_size=100, default_ttl=300)  # 5 min TTL

    def register_node(self, name: str, node: CognitiveNode) -> None:
        """Register a node with optimized tracking"""
        self.nodes[name] = node
        self.node_stats[name] = {
            "total_requests": 0,
            "total_duration_ms": 0,
            "success_count": 0,
            "error_count": 0,
            "avg_latency_ms": 0,
            "p95_latency_ms": 0,
            "health_score": 1.0,
            "last_request": time.time(),
            "recent_latencies": []
        }

    def get_node(self, name: str) -> Optional[CognitiveNode]:
        """Get node with caching"""
        # Try cache first
        cached = self._node_cache.get(f"node_{name}")
        if cached is not None:
            return cached

        # Get from nodes dict
        node = self.nodes.get(name)
        if node:
            # Cache for quick access
            self._node_cache.put(f"node_{name}", node, ttl=300)

        return node

    def get_best_node_for_intent(self, intent: str) -> Optional[str]:
        """Select best node based on intent and health metrics"""
        cache_key = f"best_node_{intent}"
        cached = self._node_cache.get(cache_key)
        if cached:
            return cached

        # Intent mapping with health-based selection
        intent_candidates = {
            "mathematical": ["math", "facts"],
            "question": ["facts", "math"],
            "general": ["facts"]
        }

        candidates = intent_candidates.get(intent, ["facts"])
        available_candidates = [name for name in candidates if name in self.nodes]

        if not available_candidates:
            return None

        # Select based on health score
        best_node = max(available_candidates,
                       key=lambda n: self.node_stats[n]["health_score"])

        # Cache decision for 30 seconds
        self._node_cache.put(cache_key, best_node, ttl=30)
        return best_node

    def update_node_stats(self, name: str, duration_ms: float, success: bool) -> None:
        """Update node statistics with optimized tracking"""
        if name not in self.node_stats:
            return

        stats = self.node_stats[name]
        stats["total_requests"] += 1
        stats["total_duration_ms"] += duration_ms
        stats["last_request"] = time.time()

        if success:
            stats["success_count"] += 1
        else:
            stats["error_count"] += 1

        # Update latency tracking (keep last 20 for efficiency)
        stats["recent_latencies"].append(duration_ms)
        if len(stats["recent_latencies"]) > 20:
            stats["recent_latencies"] = stats["recent_latencies"][-20:]

        # Calculate metrics
        if stats["total_requests"] > 0:
            stats["avg_latency_ms"] = stats["total_duration_ms"] / stats["total_requests"]

        if stats["recent_latencies"]:
            sorted_latencies = sorted(stats["recent_latencies"])
            p95_index = min(len(sorted_latencies) - 1, int(len(sorted_latencies) * 0.95))
            stats["p95_latency_ms"] = sorted_latencies[p95_index]

        # Calculate health score (0.0 - 1.0)
        success_rate = stats["success_count"] / stats["total_requests"]
        latency_penalty = min(1.0, stats["p95_latency_ms"] / 1000.0)  # Penalty for >1s latency
        recency_factor = max(0.1, 1.0 - (time.time() - stats["last_request"]) / 3600)  # Decay over 1 hour

        stats["health_score"] = success_rate * (1.0 - latency_penalty) * recency_factor


class OptimizedAsyncOrchestrator(AsyncCognitiveOrchestrator):
    """
    Optimized async orchestrator targeting T4/0.01% tail latency performance.

    Key optimizations:
    - Multi-level caching for hot paths
    - Streamlined memory operations
    - Async-first design with circuit breakers
    - Reduced MATRIZ node overhead
    - Optimized timeout handling
    """

    def __init__(
        self,
        stage_timeouts: Optional[dict[StageType, float]] = None,
        stage_critical: Optional[dict[StageType, bool]] = None,
        total_timeout: float = 0.240,  # 240ms for safety margin
        cache_enabled: bool = True,
        metrics_enabled: bool = True,
    ):
        """
        Initialize optimized orchestrator.

        Args:
            stage_timeouts: Custom timeout per stage type (optimized defaults)
            stage_critical: Whether stage failure should fail pipeline
            total_timeout: Maximum total execution time (240ms for T4/0.01%)
            cache_enabled: Enable caching optimizations
            metrics_enabled: Enable metrics collection
        """
        # Optimized default timeouts (more aggressive)
        optimized_timeouts = {
            StageType.INTENT: 0.030,      # 30ms for intent analysis (was 50ms)
            StageType.DECISION: 0.040,     # 40ms for decision (was 100ms)
            StageType.PROCESSING: 0.100,   # 100ms for main processing (was 120ms)
            StageType.VALIDATION: 0.025,   # 25ms for validation (was 40ms)
            StageType.REFLECTION: 0.020,   # 20ms for reflection (was 30ms)
        }

        if stage_timeouts:
            optimized_timeouts.update(stage_timeouts)

        super().__init__(
            stage_timeouts=optimized_timeouts,
            stage_critical=stage_critical,
            total_timeout=total_timeout
        )

        # Optimization components
        self.cache_enabled = cache_enabled
        self.metrics_enabled = metrics_enabled

        # Optimized node pool
        self.node_pool = NodePool()

        # Multi-level caching
        if cache_enabled:
            self.caches = {
                CacheType.INTENT_ANALYSIS: LRUCache(max_size=500, default_ttl=120),
                CacheType.NODE_SELECTION: LRUCache(max_size=200, default_ttl=60),
                CacheType.NODE_HEALTH: LRUCache(max_size=100, default_ttl=30),
                CacheType.PROCESSING_RESULTS: LRUCache(max_size=1000, default_ttl=300),
            }
        else:
            self.caches = {}

        # Performance tracking
        self.optimization_metrics = {
            "cache_hits": 0,
            "cache_misses": 0,
            "timeout_fast_fails": 0,
            "circuit_breaker_trips": 0,
            "memory_access_optimizations": 0,
            "total_optimizations_applied": 0
        }

        # Initialize cognitive instrumentation
        self.cognitive_enabled = initialize_cognitive_instrumentation(enable_metrics=metrics_enabled)

        # Circuit breaker state
        self.circuit_breaker_state = {
            "open": False,
            "failure_count": 0,
            "last_failure_time": 0,
            "timeout_threshold": 5,
            "reset_timeout": 30
        }

    def register_node(self, name: str, node: CognitiveNode) -> None:
        """Register node using optimized node pool"""
        self.node_pool.register_node(name, node)
        # Keep compatibility with parent class
        super().register_node(name, node)

    async def process_query(self, user_input: str) -> dict[str, Any]:
        """
        Optimized process_query with caching, fast paths, and cognitive observability.

        Target: p95 < 250ms, p99 < 300ms
        """
        # Use cognitive pipeline span if enabled
        if self.cognitive_enabled:
            expected_stages = ["memory", "attention", "thought", "action", "decision", "awareness"]
            async with cognitive_pipeline_span(
                "optimized_cognitive_pipeline",
                user_input,
                expected_stages=expected_stages,
                target_slo_ms=self.total_timeout * 1000
            ):
                return await self._process_query_with_observability(user_input)
        else:
            return await self._process_query_with_observability(user_input)

    async def _process_query_with_observability(self, user_input: str) -> dict[str, Any]:
        """Internal process query method with observability hooks"""
        start_time = time.perf_counter()

        # Check circuit breaker
        if self._should_circuit_break():
            self.optimization_metrics["circuit_breaker_trips"] += 1
            return self._build_circuit_breaker_response(user_input, start_time)

        # Try fast path for cached results
        if self.cache_enabled:
            input_hash = self._hash_input(user_input)
            cached_result = self.caches[CacheType.PROCESSING_RESULTS].get(input_hash)
            if cached_result:
                self.optimization_metrics["cache_hits"] += 1
                cached_result["from_cache"] = True
                cached_result["cache_hit_time_ms"] = (time.perf_counter() - start_time) * 1000
                return cached_result

        try:
            # Execute optimized pipeline
            result = await self._execute_optimized_pipeline(user_input, start_time)

            # Cache successful results
            if self.cache_enabled and result.get("answer") and not result.get("error"):
                input_hash = self._hash_input(user_input)
                # Cache for 5 minutes with shorter TTL for dynamic content
                cache_ttl = 60 if "?" in user_input else 300
                self.caches[CacheType.PROCESSING_RESULTS].put(input_hash, result, ttl=cache_ttl)

            return result

        except Exception as e:
            # Handle circuit breaker failures
            self._record_failure()
            total_ms = (time.perf_counter() - start_time) * 1000

            return {
                "error": f"Pipeline optimization failure: {e!s}",
                "metrics": {
                    "total_duration_ms": total_ms,
                    "optimization_failure": True,
                },
                "optimization_metrics": self.optimization_metrics.copy()
            }

    async def _execute_optimized_pipeline(self, user_input: str, start_time: float) -> dict[str, Any]:
        """Execute pipeline with all optimizations enabled"""
        stage_results = []
        time.perf_counter()

        # Pre-allocate context to reduce memory allocations
        pipeline_context = {
            "user_input": user_input,
            "intent_data": None,
            "selected_node": None,
            "processing_result": None,
            "optimization_applied": []
        }

        try:
            # Stage 1: Optimized Intent Analysis
            intent_result = await self._optimized_analyze_intent(user_input, pipeline_context)
            stage_results.append(intent_result)

            if not intent_result.success and self.stage_critical[StageType.INTENT]:
                return self._build_optimized_error_response(
                    "Intent analysis failed", stage_results, start_time
                )

            pipeline_context["intent_data"] = intent_result.data if intent_result.success else {}

            # Stage 2: Optimized Node Selection
            decision_result = await self._optimized_select_node(pipeline_context)
            stage_results.append(decision_result)

            if not decision_result.success and self.stage_critical[StageType.DECISION]:
                return self._build_optimized_error_response(
                    "Node selection failed", stage_results, start_time
                )

            pipeline_context["selected_node"] = decision_result.data if decision_result.success else "default"

            # Stage 3: Optimized Processing
            process_result = await self._optimized_process_node(pipeline_context)
            stage_results.append(process_result)

            if not process_result.success and self.stage_critical[StageType.PROCESSING]:
                return self._build_optimized_error_response(
                    "Processing failed", stage_results, start_time
                )

            pipeline_context["processing_result"] = process_result.data if process_result.success else {"answer": "Error occurred"}

            # Stage 4 & 5: Optional stages with fast skipping
            await self._execute_optional_stages(pipeline_context, stage_results)

            # Build optimized success response
            total_duration_ms = (time.perf_counter() - start_time) * 1000
            return self._build_optimized_success_response(
                pipeline_context, stage_results, total_duration_ms
            )

        except asyncio.TimeoutError:
            # Fast timeout handling
            self.optimization_metrics["timeout_fast_fails"] += 1
            total_ms = (time.perf_counter() - start_time) * 1000

            return {
                "error": f"Pipeline timeout exceeded {self.total_timeout}s",
                "partial_results": [self._serialize_stage_result(r) for r in stage_results],
                "metrics": {
                    "total_duration_ms": total_ms,
                    "timeout": True,
                    "stages_completed": len([r for r in stage_results if r.success])
                },
                "optimization_metrics": self.optimization_metrics.copy()
            }

    @instrument_cognitive_stage("attention", node_id="intent_analyzer", slo_target_ms=30.0)
    async def _optimized_analyze_intent(self, user_input: str, context: dict[str, Any]) -> StageResult:
        """Optimized intent analysis with caching and cognitive observability"""
        stage_start = time.perf_counter()

        if self.cache_enabled:
            # Create cache key from input hash
            input_words = user_input.lower().strip()[:50]  # Limit key size
            cache_key = f"intent_{hashlib.md5(input_words.encode()).hexdigest()[:8]}"

            cached_intent = self.caches[CacheType.INTENT_ANALYSIS].get(cache_key)
            if cached_intent:
                self.optimization_metrics["cache_hits"] += 1
                context["optimization_applied"].append("intent_cache_hit")

                duration_ms = (time.perf_counter() - stage_start) * 1000
                return StageResult(
                    stage_type=StageType.INTENT,
                    success=True,
                    data=cached_intent,
                    duration_ms=duration_ms
                )

        # Optimized intent detection (reduce string operations)
        intent_data = None
        try:
            # Fast intent detection using character scanning
            has_math_ops = any(op in user_input for op in "+-*/=")
            has_question = "?" in user_input

            if has_math_ops:
                detected_intent = "mathematical"
            elif has_question:
                detected_intent = "question"
            else:
                detected_intent = "general"

            intent_data = {
                "id": f"intent_{int(time.time() * 1000)}",
                "type": "INTENT",
                "intent": detected_intent,
                "confidence": 0.9,
            }

            # Cache successful intent analysis
            if self.cache_enabled:
                self.caches[CacheType.INTENT_ANALYSIS].put(cache_key, intent_data, ttl=60)

            # Record attention focus metrics
            if self.cognitive_enabled:
                attention_weights = [0.9, 0.1] if has_math_ops else [0.7, 0.3] if has_question else [0.5, 0.5]
                record_focus_drift("intent_analyzer", attention_weights, window_size=5)

            success = True
            context["optimization_applied"].append("fast_intent_detection")

        except Exception as e:
            intent_data = {"error": str(e)}
            success = False

        duration_ms = (time.perf_counter() - stage_start) * 1000
        return StageResult(
            stage_type=StageType.INTENT,
            success=success,
            data=intent_data,
            duration_ms=duration_ms
        )

    @instrument_cognitive_stage("decision", node_id="node_selector", slo_target_ms=40.0)
    async def _optimized_select_node(self, context: dict[str, Any]) -> StageResult:
        """Optimized node selection using health-based routing with cognitive observability"""
        stage_start = time.perf_counter()

        try:
            intent_data = context["intent_data"] or {}
            intent = intent_data.get("intent", "general")

            # Use optimized node pool
            selected_node = self.node_pool.get_best_node_for_intent(intent)

            if not selected_node:
                selected_node = "default"

            # Record decision confidence based on node selection
            if self.cognitive_enabled:
                confidence = 0.9 if selected_node != "default" else 0.3
                record_decision_confidence(confidence, "node_selection", "node_selector")

            context["optimization_applied"].append("health_based_routing")

            duration_ms = (time.perf_counter() - stage_start) * 1000
            return StageResult(
                stage_type=StageType.DECISION,
                success=True,
                data=selected_node,
                duration_ms=duration_ms
            )

        except Exception as e:
            duration_ms = (time.perf_counter() - stage_start) * 1000
            return StageResult(
                stage_type=StageType.DECISION,
                success=False,
                error=str(e),
                duration_ms=duration_ms
            )

    @instrument_cognitive_stage("thought", node_id="thought_processor", slo_target_ms=100.0)
    async def _optimized_process_node(self, context: dict[str, Any]) -> StageResult:
        """Optimized node processing with reduced overhead and cognitive metrics"""
        stage_start = time.perf_counter()
        selected_node_name = context["selected_node"]
        user_input = context["user_input"]

        try:
            # Get node from optimized pool
            node = self.node_pool.get_node(selected_node_name)
            if not node:
                # Fallback to available nodes
                if self.available_nodes:
                    node = next(iter(self.available_nodes.values()))
                    selected_node_name = next(iter(self.available_nodes.keys()))
                else:
                    raise Exception("No nodes available")

            # Execute with timeout (use asyncio.wait_for directly for efficiency)
            processing_timeout = self.stage_timeouts[StageType.PROCESSING]

            # Optimized node execution
            loop = asyncio.get_event_loop()
            result = await asyncio.wait_for(
                loop.run_in_executor(None, node.process, {"query": user_input}),
                timeout=processing_timeout
            )

            duration_ms = (time.perf_counter() - stage_start) * 1000

            # Update node statistics
            self.node_pool.update_node_stats(selected_node_name, duration_ms, True)

            # Record thought complexity metrics
            if self.cognitive_enabled:
                # Estimate complexity based on processing time and result
                reasoning_depth = min(10, int(duration_ms / 10))  # Rough estimation
                logic_chains = 2 if "calculation" in str(result).lower() else 1
                inference_steps = max(1, int(duration_ms / 5))  # Another rough estimation
                record_thought_complexity(reasoning_depth, logic_chains, inference_steps)

            context["optimization_applied"].append("optimized_node_execution")

            return StageResult(
                stage_type=StageType.PROCESSING,
                success=True,
                data=result,
                duration_ms=duration_ms
            )

        except Exception as e:
            duration_ms = (time.perf_counter() - stage_start) * 1000

            # Update node statistics for failure
            if selected_node_name:
                self.node_pool.update_node_stats(selected_node_name, duration_ms, False)

            return StageResult(
                stage_type=StageType.PROCESSING,
                success=False,
                error=str(e),
                duration_ms=duration_ms
            )

    def _hash_input(self, user_input: str) -> str:
        """Create hash for input caching"""
        return hashlib.md5(user_input.encode()).hexdigest()[:16]

    def _should_circuit_break(self) -> bool:
        """Check if circuit breaker should be triggered"""
        if not self.circuit_breaker_state["open"]:
            return False

        # Check if we should reset
        if (time.time() - self.circuit_breaker_state["last_failure_time"]) > self.circuit_breaker_state["reset_timeout"]:
            self.circuit_breaker_state["open"] = False
            self.circuit_breaker_state["failure_count"] = 0
            return False

        return True

    def _record_failure(self) -> None:
        """Record failure for circuit breaker"""
        self.circuit_breaker_state["failure_count"] += 1
        self.circuit_breaker_state["last_failure_time"] = time.time()

        if self.circuit_breaker_state["failure_count"] >= self.circuit_breaker_state["timeout_threshold"]:
            self.circuit_breaker_state["open"] = True

    def _build_circuit_breaker_response(self, user_input: str, start_time: float) -> dict[str, Any]:
        """Build response when circuit breaker is open"""
        total_ms = (time.perf_counter() - start_time) * 1000

        return {
            "error": "Service temporarily unavailable (circuit breaker open)",
            "answer": "I'm currently experiencing high latency. Please try again in a moment.",
            "metrics": {
                "total_duration_ms": total_ms,
                "circuit_breaker_active": True,
            },
            "optimization_metrics": self.optimization_metrics.copy()
        }

    def _build_optimized_success_response(
        self,
        context: dict[str, Any],
        stage_results: list[StageResult],
        total_duration_ms: float
    ) -> dict[str, Any]:
        """Build optimized success response with minimal object creation"""

        result = context["processing_result"] or {"answer": "No answer"}
        stage_durations = {r.stage_type.value: r.duration_ms for r in stage_results}

        stages_completed = sum(1 for r in stage_results if r.success)
        stages_failed = len(stage_results) - stages_completed
        within_budget = total_duration_ms < self.total_timeout * 1000

        # Update global optimization metrics
        self.optimization_metrics["total_optimizations_applied"] += len(context.get("optimization_applied", []))

        return {
            "answer": result.get("answer", "No answer"),
            "confidence": result.get("confidence", 0.0),
            "metrics": {
                "total_duration_ms": total_duration_ms,
                "stage_durations": stage_durations,
                "stages_completed": stages_completed,
                "stages_failed": stages_failed,
                "within_budget": within_budget,
                "optimizations_applied": context.get("optimization_applied", [])
            },
            "optimization_metrics": self.optimization_metrics.copy(),
            "cache_stats": self._get_cache_stats() if self.cache_enabled else {},
        }

    def _build_optimized_error_response(
        self,
        error: str,
        stage_results: list[StageResult],
        start_time: float
    ) -> dict[str, Any]:
        """Build optimized error response"""
        total_ms = (time.perf_counter() - start_time) * 1000

        return {
            "error": error,
            "stages": [self._serialize_stage_result(r) for r in stage_results],
            "metrics": {
                "total_duration_ms": total_ms,
                "stages_completed": sum(1 for r in stage_results if r.success),
                "stages_failed": sum(1 for r in stage_results if not r.success),
            },
            "optimization_metrics": self.optimization_metrics.copy()
        }

    def _serialize_stage_result(self, result: StageResult) -> dict[str, Any]:
        """Efficiently serialize stage result"""
        return {
            "stage_type": result.stage_type.value,
            "success": result.success,
            "duration_ms": result.duration_ms,
            "data": result.data,
            "error": getattr(result, 'error', None)
        }

    async def _execute_optional_stages(self, context: dict[str, Any], stage_results: list[StageResult]) -> None:
        """Execute validation and reflection stages with fast skipping"""

        # Skip non-critical stages if we're approaching timeout
        elapsed_ms = sum(r.duration_ms for r in stage_results)
        remaining_budget = (self.total_timeout * 1000) - elapsed_ms

        if remaining_budget < 50:  # Less than 50ms remaining
            context["optimization_applied"].append("optional_stage_skip")
            return

        # Quick validation stage
        if "validator" in self.available_nodes and remaining_budget > 30:
            try:
                validation_result = await asyncio.wait_for(
                    self._quick_validate(context["processing_result"]),
                    timeout=min(0.025, remaining_budget / 1000)
                )
                stage_results.append(validation_result)
            except asyncio.TimeoutError:
                # Skip if timeout
                pass

        # Quick reflection stage
        elapsed_ms = sum(r.duration_ms for r in stage_results)
        remaining_budget = (self.total_timeout * 1000) - elapsed_ms

        if remaining_budget > 20:
            try:
                reflection_result = await asyncio.wait_for(
                    self._quick_reflect(context),
                    timeout=min(0.020, remaining_budget / 1000)
                )
                stage_results.append(reflection_result)
            except asyncio.TimeoutError:
                # Skip if timeout
                pass

    async def _quick_validate(self, result: dict[str, Any]) -> StageResult:
        """Quick validation with minimal overhead"""
        stage_start = time.perf_counter()

        try:
            # Simple validation - check if result has required fields
            has_answer = "answer" in result
            has_confidence = "confidence" in result
            is_valid = has_answer and (not has_confidence or 0 <= result.get("confidence", 0) <= 1)

            duration_ms = (time.perf_counter() - stage_start) * 1000

            return StageResult(
                stage_type=StageType.VALIDATION,
                success=True,
                data=is_valid,
                duration_ms=duration_ms
            )

        except Exception as e:
            duration_ms = (time.perf_counter() - stage_start) * 1000
            return StageResult(
                stage_type=StageType.VALIDATION,
                success=False,
                error=str(e),
                duration_ms=duration_ms
            )

    async def _quick_reflect(self, context: dict[str, Any]) -> StageResult:
        """Quick reflection with minimal processing"""
        stage_start = time.perf_counter()

        try:
            reflection_data = {
                "id": f"reflection_{int(time.time() * 1000)}",
                "type": "REFLECTION",
                "optimizations_applied": len(context.get("optimization_applied", [])),
            }

            duration_ms = (time.perf_counter() - stage_start) * 1000

            return StageResult(
                stage_type=StageType.REFLECTION,
                success=True,
                data=reflection_data,
                duration_ms=duration_ms
            )

        except Exception as e:
            duration_ms = (time.perf_counter() - stage_start) * 1000
            return StageResult(
                stage_type=StageType.REFLECTION,
                success=False,
                error=str(e),
                duration_ms=duration_ms
            )

    def _get_cache_stats(self) -> dict[str, Any]:
        """Get comprehensive cache statistics"""
        if not self.cache_enabled:
            return {}

        stats = {}
        for cache_type, cache in self.caches.items():
            stats[cache_type.value] = cache.get_stats()

        return stats

    def get_optimization_report(self) -> dict[str, Any]:
        """Get detailed optimization performance report"""
        node_stats = {}
        for name, stats in self.node_pool.node_stats.items():
            node_stats[name] = {
                "health_score": stats["health_score"],
                "avg_latency_ms": stats["avg_latency_ms"],
                "p95_latency_ms": stats["p95_latency_ms"],
                "success_rate": stats["success_count"] / max(1, stats["total_requests"]),
                "total_requests": stats["total_requests"]
            }

        return {
            "optimization_metrics": self.optimization_metrics.copy(),
            "cache_stats": self._get_cache_stats(),
            "node_performance": node_stats,
            "circuit_breaker": self.circuit_breaker_state.copy(),
            "configuration": {
                "cache_enabled": self.cache_enabled,
                "total_timeout_ms": self.total_timeout * 1000,
                "stage_timeouts_ms": {k.value: v * 1000 for k, v in self.stage_timeouts.items()}
            }
        }

    async def warmup_caches(self, test_queries: list[str]) -> dict[str, Any]:
        """Warm up caches with test queries for optimal performance"""
        if not self.cache_enabled:
            return {"status": "caching_disabled"}

        warmup_start = time.perf_counter()
        processed_queries = 0

        for query in test_queries:
            try:
                await self.process_query(query)
                processed_queries += 1
            except Exception:
                continue  # Skip failed warmup queries

        warmup_duration = time.perf_counter() - warmup_start

        return {
            "status": "completed",
            "queries_processed": processed_queries,
            "warmup_duration_ms": warmup_duration * 1000,
            "cache_stats": self._get_cache_stats()
        }
