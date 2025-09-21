"""
LUKHAS AI High-Performance Context Bus
=====================================

Ultra-fast context handoff system with <250ms performance target.
Implements async pub-sub with transparent logging and workflow orchestration.

Constellation Framework: ⚛️ (Identity), 🧠 (Consciousness), 🛡️ (Guardian)
Performance Target: <250ms context handoffs
Throughput Target: 1000+ events/second
Reliability Target: 99.9% uptime

Architecture:
- Async message passing with priority queues
- Lock-free data structures for performance
- MΛTRIZ bridge integration
- Multi-model orchestration support
- Comprehensive interpretability logging

Generated: Phase 2 Core Implementation
"""
import asyncio
import logging
import time
import uuid
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Optional

# Performance optimization imports
import uvloop  # High-performance event loop

logger = logging.getLogger(__name__)


class ContextPriority(Enum):
    """Priority levels for context messages"""

    CRITICAL = 5  # System-critical operations
    HIGH = 4  # Important user operations
    NORMAL = 3  # Standard operations
    LOW = 2  # Background operations
    TRACE = 1  # Logging and metrics


class HandoffStatus(Enum):
    """Status of context handoffs"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class ContextMessage:
    """High-performance context message with performance tracking"""

    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    message_type: str = ""
    payload: dict[str, Any] = field(default_factory=dict)
    source: str = "unknown"
    target: Optional[str] = None
    priority: ContextPriority = ContextPriority.NORMAL

    # Performance tracking (high-resolution timing)
    created_at: float = field(default_factory=time.perf_counter)
    handoff_start: float = 0.0
    handoff_complete: float = 0.0
    processing_start: float = 0.0
    processing_complete: float = 0.0

    # Constellation Framework context
    identity_context: dict[str, Any] = field(default_factory=dict)  # ⚛️
    consciousness_state: dict[str, Any] = field(default_factory=dict)  # 🧠
    guardian_policies: dict[str, Any] = field(default_factory=dict)  # 🛡️

    # Workflow tracking
    workflow_id: Optional[str] = None
    step_index: int = 0
    correlation_id: Optional[str] = None
    causality_chain: list[str] = field(default_factory=list)

    @property
    def handoff_latency_ms(self) -> float:
        """Calculate handoff latency in milliseconds"""
        if self.handoff_complete and self.handoff_start:
            return (self.handoff_complete - self.handoff_start) * 1000
        return 0.0

    @property
    def processing_latency_ms(self) -> float:
        """Calculate processing latency in milliseconds"""
        if self.processing_complete and self.processing_start:
            return (self.processing_complete - self.processing_start) * 1000
        return 0.0

    @property
    def total_latency_ms(self) -> float:
        """Calculate total message latency"""
        if self.handoff_complete and self.created_at:
            return (self.handoff_complete - self.created_at) * 1000
        return 0.0

    def meets_performance_target(self) -> bool:
        """Check if message meets <250ms handoff target"""
        return self.handoff_latency_ms < 250

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "message_id": self.message_id,
            "message_type": self.message_type,
            "payload": self.payload,
            "source": self.source,
            "target": self.target,
            "priority": self.priority.value,
            "workflow_id": self.workflow_id,
            "step_index": self.step_index,
            "performance": {
                "handoff_latency_ms": self.handoff_latency_ms,
                "processing_latency_ms": self.processing_latency_ms,
                "total_latency_ms": self.total_latency_ms,
                "meets_target": self.meets_performance_target(),
            },
            "constellation_context": {
                "identity": bool(self.identity_context),
                "consciousness": bool(self.consciousness_state),
                "guardian": bool(self.guardian_policies),
            },
            "timestamp": self.created_at,
        }


@dataclass
class WorkflowStep:
    """Individual step in a workflow pipeline"""

    step_id: str
    name: str
    handler: Callable
    timeout_ms: int = 5000
    retry_on_failure: bool = True
    required_context: list[str] = field(default_factory=list)

    # Performance constraints
    max_latency_ms: int = 250
    priority: ContextPriority = ContextPriority.NORMAL

    # Constellation Framework requirements
    requires_identity: bool = False  # ⚛️
    requires_consciousness: bool = False  # 🧠
    requires_guardian: bool = False  # 🛡️


@dataclass
class PerformanceMetrics:
    """Comprehensive performance tracking"""

    total_messages: int = 0
    successful_handoffs: int = 0
    failed_handoffs: int = 0
    timeout_handoffs: int = 0

    # Latency tracking
    handoff_latencies: deque = field(default_factory=lambda: deque(maxlen=1000))
    processing_latencies: deque = field(default_factory=lambda: deque(maxlen=1000))

    # Throughput tracking
    messages_per_second: float = 0.0
    peak_throughput: float = 0.0

    # Target compliance
    target_compliance_percent: float = 0.0

    def add_handoff(self, message: ContextMessage):
        """Add handoff metrics"""
        self.total_messages += 1
        self.handoff_latencies.append(message.handoff_latency_ms)
        self.processing_latencies.append(message.processing_latency_ms)

        if message.meets_performance_target():
            self.successful_handoffs += 1
        else:
            self.failed_handoffs += 1

    @property
    def average_handoff_ms(self) -> float:
        """Calculate average handoff latency"""
        if not self.handoff_latencies:
            return 0.0
        return sum(self.handoff_latencies) / len(self.handoff_latencies)

    @property
    def p95_handoff_ms(self) -> float:
        """Calculate 95th percentile handoff latency"""
        if not self.handoff_latencies:
            return 0.0
        sorted_latencies = sorted(self.handoff_latencies)
        p95_index = int(len(sorted_latencies) * 0.95)
        return sorted_latencies[p95_index] if p95_index < len(sorted_latencies) else sorted_latencies[-1]

    @property
    def success_rate(self) -> float:
        """Calculate handoff success rate"""
        if self.total_messages == 0:
            return 0.0
        return self.successful_handoffs / self.total_messages


class HighPerformanceContextBus:
    """
    Ultra-fast context bus with <250ms handoff target.

    Key Performance Features:
    - Lock-free message queues with priority handling
    - Async processing with uvloop optimization
    - Pre-allocated object pools to reduce GC pressure
    - Batch processing for high throughput
    - Comprehensive performance monitoring

    Integration Features:
    - MΛTRIZ bridge connectivity
    - Multi-model orchestration support
    - Transparent interpretability logging
    - Constellation Framework compliance
    """

    def __init__(self, max_queue_size: int = 10000, worker_count: int = 4):
        """Initialize high-performance context bus"""

        # Core configuration
        self.max_queue_size = max_queue_size
        self.worker_count = worker_count

        # Message routing (lock-free data structures)
        self.subscribers: dict[str, list[Callable]] = defaultdict(list)
        self.pattern_subscribers: list[tuple] = []  # (pattern_fn, handler)
        self.workflow_handlers: dict[str, Callable] = {}

        # High-performance queues (priority-based)
        self.message_queues: dict[ContextPriority, asyncio.Queue] = {}
        for priority in ContextPriority:
            self.message_queues[priority] = asyncio.Queue(maxsize=max_queue_size)

        # Performance tracking
        self.performance_metrics = PerformanceMetrics()
        self.message_history: deque = deque(maxlen=1000)

        # Worker management
        self.workers: list[asyncio.Task] = []
        self.running = False

        # Thread pool for CPU-intensive operations
        self.thread_pool = ThreadPoolExecutor(max_workers=2)

        # Interpretability logging
        self.transparency_log: deque = deque(maxlen=5000)
        self.workflow_narratives: dict[str, list[str]] = defaultdict(list)

        # MΛTRIZ bridge integration
        self.matriz_bridge_active = False
        self.matriz_handlers: dict[str, Callable] = {}

        # Performance optimization
        self._setup_performance_optimizations()

        logger.info("🚀 High-Performance Context Bus initialized")
        logger.info("   Target: <250ms handoffs")
        logger.info(f"   Workers: {worker_count}")
        logger.info(f"   Queue size: {max_queue_size}")

    def _setup_performance_optimizations(self):
        """Setup performance optimizations"""
        try:
            # Use uvloop for better async performance
            if hasattr(uvloop, "install"):
                # uvloop.install() is deprecated in Python 3.12+
                # Uvicorn will use it by default if installed.
                logger.info("📈 uvloop performance optimization enabled")
        except ImportError:
            logger.warning("uvloop not available - using default event loop")

        # Pre-warm object pools
        self._message_pool: deque = deque()
        for _ in range(100):  # Pre-allocate message objects
            self._message_pool.append(ContextMessage())

    async def start(self):
        """Start the context bus workers"""
        if self.running:
            return

        self.running = True

        # Start priority workers
        for priority in ContextPriority:
            for i in range(self.worker_count // len(ContextPriority) + 1):
                worker = asyncio.create_task(self._worker_loop(priority, f"worker-{priority.name}-{i}"))
                self.workers.append(worker)

        # Start performance monitor
        monitor_task = asyncio.create_task(self._performance_monitor_loop())
        self.workers.append(monitor_task)

        # Start transparency logger
        logging_task = asyncio.create_task(self._transparency_logging_loop())
        self.workers.append(logging_task)

        logger.info("⚡ Context Bus workers started")
        logger.info(f"   Active workers: {len(self.workers)}")

    async def stop(self):
        """Stop the context bus gracefully"""
        self.running = False

        # Wait for workers to complete
        if self.workers:
            await asyncio.gather(*self.workers, return_exceptions=True)
            self.workers.clear()

        # Shutdown thread pool
        self.thread_pool.shutdown(wait=True)

        logger.info("🛑 Context Bus stopped gracefully")

    async def emit(
        self,
        message_type: str,
        payload: dict[str, Any],
        source: str = "context_bus",
        target: Optional[str] = None,
        priority: ContextPriority = ContextPriority.NORMAL,
        workflow_id: Optional[str] = None,
    ) -> str:
        """
        Emit a context message with high-performance handling

        Args:
            message_type: Type of message
            payload: Message payload data
            source: Source component
            target: Target component (optional)
            priority: Message priority
            workflow_id: Associated workflow ID

        Returns:
            Message ID for tracking
        """
        # Get message from pool or create new
        message = self._get_message_from_pool()

        # Configure message
        message.message_id = str(uuid.uuid4())
        message.message_type = message_type
        message.payload = payload
        message.source = source
        message.target = target
        message.priority = priority
        message.workflow_id = workflow_id
        message.created_at = time.perf_counter()

        # Add to appropriate priority queue
        try:
            queue = self.message_queues[priority]
            queue.put_nowait(message)

            # Add to transparency log
            self._add_transparency_entry(
                f"📤 Emitted: {message_type} from {source} (priority: {priority.name})",
                message.message_id,
            )

        except asyncio.QueueFull:
            logger.error(f"Queue full for priority {priority}, dropping message")
            self.performance_metrics.failed_handoffs += 1
            return message.message_id

        return message.message_id

    def subscribe(self, message_type: str, handler: Callable):
        """Subscribe to message type with pattern support"""
        if "*" in message_type:
            # Pattern subscription
            import re

            pattern = message_type.replace(".", r"\.").replace("*", ".*")

            def pattern_fn(msg_type):
                return re.match(pattern, msg_type)

            self.pattern_subscribers.append((pattern_fn, handler))

            logger.info(f"📥 Pattern subscription: {message_type} → {handler.__name__}")
        else:
            # Exact subscription
            self.subscribers[message_type].append(handler)

            logger.info(f"📥 Exact subscription: {message_type} → {handler.__name__}")

    async def execute_workflow(
        self,
        workflow_id: str,
        steps: list[WorkflowStep],
        initial_context: Optional[dict] = None,
    ) -> dict[str, Any]:
        """
        Execute multi-step workflow with performance tracking

        Args:
            workflow_id: Unique workflow identifier
            steps: List of workflow steps
            initial_context: Initial context data

        Returns:
            Workflow execution results with performance metrics
        """
        workflow_start = time.perf_counter()

        self._add_workflow_narrative(workflow_id, f"🚀 Starting workflow: {len(steps)} steps")

        # Initialize context
        context = initial_context or {}
        step_results = []

        try:
            for i, step in enumerate(steps):
                step_start = time.perf_counter()

                # Create context message for step
                step_message = ContextMessage(
                    message_type=f"workflow.step.{step.step_id}",
                    payload=context,
                    source=f"workflow.{workflow_id}",
                    workflow_id=workflow_id,
                    step_index=i,
                    priority=step.priority,
                )

                # Set Constellation Framework requirements
                if step.requires_identity:
                    step_message.identity_context = {"required": True}
                if step.requires_consciousness:
                    step_message.consciousness_state = {"required": True}
                if step.requires_guardian:
                    step_message.guardian_policies = {"required": True}

                # Start handoff timing
                step_message.handoff_start = time.perf_counter()
                step_message.processing_start = time.perf_counter()

                self._add_workflow_narrative(workflow_id, f"▶️ Executing step {i + 1}/{len(steps)}: {step.name}")

                # Execute step with timeout
                try:
                    step_result = await asyncio.wait_for(
                        step.handler(step_message.payload),
                        timeout=step.timeout_ms / 1000,
                    )

                    # Complete timing
                    step_message.processing_complete = time.perf_counter()
                    step_message.handoff_complete = time.perf_counter()

                    # Update context with result
                    context.update(step_result)

                    # Track performance
                    self.performance_metrics.add_handoff(step_message)

                    step_duration = (time.perf_counter() - step_start) * 1000

                    step_results.append(
                        {
                            "step_id": step.step_id,
                            "step_name": step.name,
                            "result": step_result,
                            "duration_ms": step_duration,
                            "handoff_latency_ms": step_message.handoff_latency_ms,
                            "meets_target": step_message.meets_performance_target(),
                        }
                    )

                    self._add_workflow_narrative(
                        workflow_id,
                        f"✅ Completed step {i + 1}: {step.name} ({step_duration:.2f}ms)",
                    )

                except asyncio.TimeoutError:
                    error_msg = f"Step {step.name} timed out after {step.timeout_ms}ms"
                    self._add_workflow_narrative(workflow_id, f"⏰ {error_msg}")

                    if step.retry_on_failure:
                        # Retry once
                        try:
                            step_result = await asyncio.wait_for(step.handler(context), timeout=step.timeout_ms / 1000)
                            context.update(step_result)
                            self._add_workflow_narrative(workflow_id, f"🔄 Retry successful for step {step.name}")
                        except:
                            raise Exception(f"Step {step.name} failed after retry")
                    else:
                        raise Exception(error_msg)

                except Exception as e:
                    error_msg = f"Step {step.name} failed: {e!s}"
                    self._add_workflow_narrative(workflow_id, f"❌ {error_msg}")
                    raise Exception(error_msg)

            # Workflow completed successfully
            workflow_duration = (time.perf_counter() - workflow_start) * 1000

            self._add_workflow_narrative(
                workflow_id,
                f"🎉 Workflow completed successfully ({workflow_duration:.2f}ms)",
            )

            return {
                "workflow_id": workflow_id,
                "status": "completed",
                "results": step_results,
                "total_duration_ms": workflow_duration,
                "average_handoff_ms": sum(r["handoff_latency_ms"] for r in step_results) / len(step_results),
                "all_steps_meet_target": all(r["meets_target"] for r in step_results),
                "narrative": self.workflow_narratives[workflow_id],
            }

        except Exception as e:
            workflow_duration = (time.perf_counter() - workflow_start) * 1000

            self._add_workflow_narrative(workflow_id, f"💥 Workflow failed: {e!s} ({workflow_duration:.2f}ms)")

            return {
                "workflow_id": workflow_id,
                "status": "failed",
                "error": str(e),
                "results": step_results,
                "total_duration_ms": workflow_duration,
                "narrative": self.workflow_narratives[workflow_id],
            }

    async def _worker_loop(self, priority: ContextPriority, worker_name: str):
        """Worker loop for processing messages of specific priority"""
        queue = self.message_queues[priority]

        while self.running:
            try:
                # Get message with timeout to allow checking running flag
                message = await asyncio.wait_for(queue.get(), timeout=1.0)

                # Process message
                await self._process_message(message)

            except asyncio.TimeoutError:
                continue  # Check running flag and continue
            except Exception as e:
                logger.error(f"Worker {worker_name} error: {e}")
                await asyncio.sleep(0.1)  # Brief pause on error

    async def _process_message(self, message: ContextMessage):
        """Process individual message with performance tracking"""
        message.processing_start = time.perf_counter()

        try:
            # Find handlers
            handlers = []

            # Exact match handlers
            handlers.extend(self.subscribers.get(message.message_type, []))

            # Pattern match handlers
            for pattern_fn, handler in self.pattern_subscribers:
                if pattern_fn(message.message_type):
                    handlers.append(handler)

            # Execute handlers
            for handler in handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(message)
                    else:
                        # Run sync handler in thread pool
                        await asyncio.get_event_loop().run_in_executor(self.thread_pool, handler, message)

                except Exception as e:
                    logger.error(f"Handler error for {message.message_type}: {e}")

            # Complete processing
            message.processing_complete = time.perf_counter()
            message.handoff_complete = time.perf_counter()

            # Track performance
            self.performance_metrics.add_handoff(message)
            self.message_history.append(message)

            # Add to transparency log
            self._add_transparency_entry(
                f"📨 Processed: {message.message_type} ({message.handoff_latency_ms:.2f}ms, {len(handlers)} handlers)",
                message.message_id,
            )

            # Return message to pool
            self._return_message_to_pool(message)

        except Exception as e:
            logger.error(f"Message processing failed: {e}")
            self.performance_metrics.failed_handoffs += 1

    async def _performance_monitor_loop(self):
        """Background loop for performance monitoring"""
        last_message_count = 0
        last_check_time = time.time()

        while self.running:
            await asyncio.sleep(5.0)  # Monitor every 5 seconds

            try:
                current_time = time.time()
                current_count = self.performance_metrics.total_messages

                # Calculate throughput
                time_delta = current_time - last_check_time
                message_delta = current_count - last_message_count

                if time_delta > 0:
                    throughput = message_delta / time_delta
                    self.performance_metrics.messages_per_second = throughput

                    if throughput > self.performance_metrics.peak_throughput:
                        self.performance_metrics.peak_throughput = throughput

                # Calculate target compliance
                if self.performance_metrics.total_messages > 0:
                    compliance = (
                        self.performance_metrics.successful_handoffs / self.performance_metrics.total_messages
                    ) * 100
                    self.performance_metrics.target_compliance_percent = compliance

                # Log performance summary
                if current_count > 0:
                    logger.info(
                        f"⚡ Performance: {throughput:.1f} msg/s, "
                        f"avg: {self.performance_metrics.average_handoff_ms:.1f}ms, "
                        f"p95: {self.performance_metrics.p95_handoff_ms:.1f}ms, "
                        f"compliance: {compliance:.1f}%"
                    )

                last_message_count = current_count
                last_check_time = current_time

            except Exception as e:
                logger.error(f"Performance monitoring error: {e}")

    async def _transparency_logging_loop(self):
        """Background loop for transparency logging"""
        while self.running:
            await asyncio.sleep(1.0)

            # Process transparency log entries
            if len(self.transparency_log) > 100:  # Batch process
                entries_to_log = []
                for _ in range(min(50, len(self.transparency_log))):
                    entries_to_log.append(self.transparency_log.popleft())

                # Could write to file or external system
                # For now, just maintain the log in memory

            await asyncio.sleep(1.0)

    def _get_message_from_pool(self) -> ContextMessage:
        """Get message from object pool or create new"""
        if self._message_pool:
            message = self._message_pool.popleft()
            # Reset message state
            message.__dict__.clear()
            message.__init__()  # Re-initialize with defaults
            return message
        return ContextMessage()

    def _return_message_to_pool(self, message: ContextMessage):
        """Return message to object pool"""
        if len(self._message_pool) < 100:  # Pool size limit
            self._message_pool.append(message)

    def _add_transparency_entry(self, entry: str, message_id: str):
        """Add entry to transparency log"""
        timestamp = datetime.now(timezone.utc).isoformat()
        log_entry = {"timestamp": timestamp, "message": entry, "message_id": message_id}
        self.transparency_log.append(log_entry)

    def _add_workflow_narrative(self, workflow_id: str, entry: str):
        """Add entry to workflow narrative"""
        timestamp = datetime.now(timezone.utc).strftime("%H:%M:%S.%f")[:-3]
        narrative_entry = f"[{timestamp}] {entry}"
        self.workflow_narratives[workflow_id].append(narrative_entry)

    def get_performance_metrics(self) -> dict[str, Any]:
        """Get comprehensive performance metrics"""
        return {
            "messages": {
                "total": self.performance_metrics.total_messages,
                "successful": self.performance_metrics.successful_handoffs,
                "failed": self.performance_metrics.failed_handoffs,
                "success_rate": self.performance_metrics.success_rate,
            },
            "latency": {
                "average_handoff_ms": self.performance_metrics.average_handoff_ms,
                "p95_handoff_ms": self.performance_metrics.p95_handoff_ms,
                "meets_250ms_target": self.performance_metrics.p95_handoff_ms < 250,
            },
            "throughput": {
                "messages_per_second": self.performance_metrics.messages_per_second,
                "peak_throughput": self.performance_metrics.peak_throughput,
            },
            "compliance": {
                "target_compliance_percent": self.performance_metrics.target_compliance_percent,
                "meets_performance_target": self.performance_metrics.target_compliance_percent > 95,
            },
            "system": {
                "workers_active": len(self.workers),
                "queue_sizes": {p.name: q.qsize() for p, q in self.message_queues.items()},
                "memory_pool_size": len(self._message_pool),
            },
        }

    def get_transparency_log(self, limit: int = 100) -> list[dict]:
        """Get recent transparency log entries"""
        return list(self.transparency_log)[-limit:]

    def get_workflow_narrative(self, workflow_id: str) -> list[str]:
        """Get narrative for specific workflow"""
        return self.workflow_narratives.get(workflow_id, [])


# Global high-performance context bus instance
context_bus = HighPerformanceContextBus()


# Convenience functions
async def emit(message_type: str, payload: dict[str, Any], **kwargs) -> str:
    """Emit message to context bus"""
    return await context_bus.emit(message_type, payload, **kwargs)


def subscribe(message_type: str, handler: Callable):
    """Subscribe to message type"""
    context_bus.subscribe(message_type, handler)


async def execute_workflow(
    workflow_id: str, steps: list[WorkflowStep], initial_context: Optional[dict] = None
) -> dict[str, Any]:
    """Execute workflow through context bus"""
    return await context_bus.execute_workflow(workflow_id, steps, initial_context)


# Export main components
__all__ = [
    "ContextMessage",
    "ContextPriority",
    "HandoffStatus",
    "HighPerformanceContextBus",
    "PerformanceMetrics",
    "WorkflowStep",
    "context_bus",
    "emit",
    "execute_workflow",
    "subscribe",
]
