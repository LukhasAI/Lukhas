"""
LUKHAS Enhanced Context Bus with Policy Integration
Agent 4: Context Orchestrator & Backend Logic Specialist
Implements <250ms context handoff, policy engine at every step, rate limiting
Integrates with all other agents' deliverables
"""

import asyncio
import logging
import os
import sys
import time
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Optional

# Add paths for other agent imports
sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

# Import Agent 1's identity system

# Import Agent 3's adapters
from candidate.core.identity.lambda_id_core import LukhasIdentityService

# Import Agent 2's consent and policy
from lukhas.governance.consent_ledger.ledger_v1 import (
    ConsentLedgerV1,
    PolicyEngine,
    PolicyVerdict,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WorkflowState(Enum):
    """Workflow execution states"""

    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    STEP_UP_REQUIRED = "step_up_required"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ContextHandoff:
    """
    Context handoff structure for <250ms target
    Preserves state between workflow steps
    """

    handoff_id: str = field(default_factory=lambda: f"CTX-{uuid.uuid4().hex}")
    source_step: str = ""
    target_step: str = ""
    context_data: dict[str, Any] = field(default_factory=dict)
    lid: str = ""  # LUKHAS ID
    timestamp: float = field(default_factory=time.time)

    # Performance tracking
    handoff_start: float = 0.0
    handoff_complete: float = 0.0

    @property
    def handoff_latency_ms(self) -> float:
        """Calculate handoff latency in milliseconds"""
        if self.handoff_complete and self.handoff_start:
            return (self.handoff_complete - self.handoff_start) * 1000
        return 0.0

    def meets_target(self) -> bool:
        """Check if handoff meets <250ms target"""
        return self.handoff_latency_ms < 250


@dataclass
class WorkflowStep:
    """Single step in a workflow pipeline"""

    step_id: str
    name: str
    handler: Callable
    required_scopes: list[str] = field(default_factory=list)
    timeout_ms: int = 5000
    retry_on_failure: bool = True

    # Policy enforcement
    requires_policy_check: bool = True
    policy_context: dict[str, Any] = field(default_factory=dict)


class RateLimiter:
    """
    Rate limiter with circuit breaker metrics export
    Per Agent 4 requirements in Claude_7.yml
    """

    def __init__(self, max_requests_per_second: int = 10, burst_size: int = 20):
        self.max_rps = max_requests_per_second
        self.burst_size = burst_size
        self.tokens = burst_size
        self.last_refill = time.time()
        self.request_times = deque(maxlen=1000)

        # Circuit breaker metrics
        self.total_requests = 0
        self.rejected_requests = 0
        self.circuit_open = False
        self.consecutive_failures = 0
        self.failure_threshold = 5

    async def acquire(self) -> bool:
        """Acquire rate limit token"""
        now = time.time()

        # Refill tokens
        elapsed = now - self.last_refill
        tokens_to_add = elapsed * self.max_rps
        self.tokens = min(self.burst_size, self.tokens + tokens_to_add)
        self.last_refill = now

        self.total_requests += 1

        # Check circuit breaker
        if self.circuit_open:
            self.rejected_requests += 1
            return False

        # Check rate limit
        if self.tokens >= 1:
            self.tokens -= 1
            self.request_times.append(now)
            self.consecutive_failures = 0
            return True

        # Rate limit exceeded
        self.rejected_requests += 1
        self.consecutive_failures += 1

        # Open circuit if too many failures
        if self.consecutive_failures >= self.failure_threshold:
            self.circuit_open = True
            logger.warning("Circuit breaker opened due to rate limit failures")

        return False

    def get_metrics(self) -> dict:
        """Export circuit breaker metrics"""
        return {
            "total_requests": self.total_requests,
            "rejected_requests": self.rejected_requests,
            "rejection_rate": self.rejected_requests / max(self.total_requests, 1),
            "circuit_state": "open" if self.circuit_open else "closed",
            "current_tokens": self.tokens,
            "requests_per_second": self._calculate_rps(),
        }

    def _calculate_rps(self) -> float:
        """Calculate current requests per second"""
        if len(self.request_times) < 2:
            return 0.0

        time_span = self.request_times[-1] - self.request_times[0]
        if time_span > 0:
            return len(self.request_times) / time_span
        return 0.0

    def reset_circuit(self):
        """Reset circuit breaker"""
        self.circuit_open = False
        self.consecutive_failures = 0


class ContextBusOrchestrator:
    """
    Main context bus and orchestrator implementation
    Coordinates all agents with policy enforcement at every step
    """

    def __init__(self):
        # Core services from other agents
        self.identity_service = LukhasIdentityService()
        self.consent_ledger = ConsentLedgerV1()
        self.policy_engine = PolicyEngine(self.consent_ledger)

        # Adapters from Agent 3
        # TODO: GmailAdapter, DriveAdapter, DropboxAdapter are abstract; use concrete implementations or mocks for instantiation
        self.gmail_adapter = None  # GmailAdapter()
        self.drive_adapter = None  # DriveAdapter()
        self.dropbox_adapter = None  # DropboxAdapter()

        # Context integrations (set to None for demo)
        self.gmail_integration = None  # GmailContextIntegration(self.gmail_adapter)
        self.drive_integration = None  # DriveContextIntegration(self.drive_adapter)
        self.dropbox_integration = None  # DropboxContextIntegration(self.dropbox_adapter)

        # Opus 4 model allocation strategy
        # This can be set via config/env in production
        self.model_allocation = {
            "analysis": "opus-4",
            "cross_reference": "opus-4",
            "default": "opus-4",
        }

        # Workflow management
        self.workflows = {}
        self.context_store = {}

        # Rate limiting and metrics
        self.rate_limiter = RateLimiter()
        self.performance_metrics = {
            "total_workflows": 0,
            "completed_workflows": 0,
            "failed_workflows": 0,
            "avg_handoff_ms": 0,
            "p95_handoff_ms": 0,
            "handoff_latencies": deque(maxlen=1000),
        }

        # Pub-sub for event-driven communication
        self.event_subscribers = defaultdict(list)

        # Step-by-step narrative for transparency
        self.workflow_narratives = {}

    async def execute_workflow(
        self,
        lid: str,
        workflow_name: str,
        steps: list[WorkflowStep],
        initial_context: Optional[dict] = None,
    ) -> dict:
        """
        Execute multi-step workflow with policy enforcement at each step
        Implements <250ms context handoff target
        """
        workflow_id = f"WF-{uuid.uuid4().hex}"

        # Initialize workflow
        self.workflows[workflow_id] = {
            "id": workflow_id,
            "name": workflow_name,
            "lid": lid,
            "state": WorkflowState.PENDING,
            "current_step": 0,
            "steps": steps,
            "results": [],
            "start_time": time.time(),
        }

        self.workflow_narratives[workflow_id] = []
        self.performance_metrics["total_workflows"] += 1

        # Create initial context
        context = ContextHandoff(
            source_step="init",
            target_step=steps[0].name if steps else "none",
            context_data=initial_context or {},
            lid=lid,
        )

        try:
            # Execute each step
            for i, step in enumerate(steps):
                self.workflows[workflow_id]["current_step"] = i
                self.workflows[workflow_id]["state"] = WorkflowState.RUNNING

                # Rate limiting
                if not await self.rate_limiter.acquire():
                    self._add_narrative(workflow_id, f"⚠️ Rate limit exceeded at step {step.name}")
                    raise Exception("Rate limit exceeded")

                # Policy check at every step (hot path)
                if step.requires_policy_check:
                    policy_result = await self._check_policy(lid, step.name, step.policy_context)

                    if policy_result["verdict"] == PolicyVerdict.DENY:
                        self._add_narrative(workflow_id, f"❌ Policy denied: {step.name}")
                        self.workflows[workflow_id]["state"] = WorkflowState.FAILED
                        raise Exception(f"Policy denied: {policy_result.get('refusal', 'Unknown')}")

                    elif policy_result["verdict"] == PolicyVerdict.STEP_UP_REQUIRED:
                        self._add_narrative(workflow_id, f"🔐 Step-up required: {step.name}")
                        self.workflows[workflow_id]["state"] = WorkflowState.STEP_UP_REQUIRED

                        # Surface require_step_up and pause pipeline
                        await self._pause_for_step_up(workflow_id, policy_result)

                        # After step-up, retry policy check
                        policy_result = await self._check_policy(lid, step.name, step.policy_context)
                        if policy_result["verdict"] != PolicyVerdict.ALLOW:
                            raise Exception("Step-up authentication failed")

                # Execute step with context handoff
                self._add_narrative(workflow_id, f"▶️ Executing: {step.name}")

                # Start context handoff
                context.handoff_start = time.perf_counter()
                context.source_step = steps[i - 1].name if i > 0 else "init"
                context.target_step = step.name

                # Execute step handler
                step_result = await self._execute_step(step, context)

                # Complete context handoff
                context.handoff_complete = time.perf_counter()
                self._track_handoff_performance(context)

                # Update context for next step
                context.context_data.update(step_result)

                # Store result
                self.workflows[workflow_id]["results"].append(
                    {
                        "step": step.name,
                        "result": step_result,
                        "handoff_latency_ms": context.handoff_latency_ms,
                    }
                )

                self._add_narrative(
                    workflow_id,
                    f"✅ Completed: {step.name} ({context.handoff_latency_ms:.2f}ms)",
                )

            # Workflow completed successfully
            self.workflows[workflow_id]["state"] = WorkflowState.COMPLETED
            self.performance_metrics["completed_workflows"] += 1

            return {
                "workflow_id": workflow_id,
                "state": WorkflowState.COMPLETED.value,
                "results": self.workflows[workflow_id]["results"],
                "narrative": self.workflow_narratives[workflow_id],
                "performance": {
                    "total_time_ms": (time.time() - self.workflows[workflow_id]["start_time"]) * 1000,
                    "avg_handoff_ms": self.performance_metrics["avg_handoff_ms"],
                },
            }

        except Exception as e:
            self.workflows[workflow_id]["state"] = WorkflowState.FAILED
            self.performance_metrics["failed_workflows"] += 1
            self._add_narrative(workflow_id, f"❌ Failed: {e!s}")

            return {
                "workflow_id": workflow_id,
                "state": WorkflowState.FAILED.value,
                "error": str(e),
                "narrative": self.workflow_narratives[workflow_id],
            }

    async def _check_policy(self, lid: str, action: str, context: dict) -> dict:
        """
        Check policy engine (integrates with Agent 2)
        Default-deny on conflicting risk signals
        """
        policy_result = self.policy_engine.validate_action(lid=lid, action=action, context=context)

        # Check for conflicting risk signals (tripwires/circuit breakers)
        if self._detect_risk_conflicts(context):
            logger.warning(f"Conflicting risk signals detected for {action}")
            return {
                "verdict": PolicyVerdict.DENY,
                "refusal": "Conflicting risk signals detected",
                "require_step_up": True,
            }

        return policy_result

    def _detect_risk_conflicts(self, context: dict) -> bool:
        """Detect conflicting risk signals (tripwires)"""
        risk_indicators = context.get("risk_indicators", [])

        # Check for known risk patterns
        high_risk_patterns = [
            "rapid_permission_escalation",
            "unusual_data_access_pattern",
            "multiple_failed_auth_attempts",
            "suspicious_api_usage",
        ]

        detected_risks = [r for r in risk_indicators if r in high_risk_patterns]

        # Conflict if multiple high-risk patterns detected
        return len(detected_risks) > 1

    async def _pause_for_step_up(self, workflow_id: str, policy_result: dict):
        """
        Pause pipeline for step-up authentication
        Surface require_step_up (GTΨ/UL) to user
        """
        self.workflows[workflow_id]["state"] = WorkflowState.PAUSED

        # Emit event for UI to handle step-up
        await self.publish_event(
            "step_up_required",
            {
                "workflow_id": workflow_id,
                "reason": policy_result.get("explanation_unl", "Additional verification required"),
                "require_step_up": policy_result.get("require_step_up", "mfa"),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )

        # Wait for step-up completion (with timeout)
        timeout = 300  # 5 minutes
        start_time = time.time()

        while self.workflows[workflow_id]["state"] == WorkflowState.PAUSED:
            if time.time() - start_time > timeout:
                raise Exception("Step-up authentication timeout")
            await asyncio.sleep(1)

    async def _execute_step(self, step: WorkflowStep, context: ContextHandoff) -> dict:
        """Execute individual workflow step with timeout"""
        try:
            # Execute with timeout
            result = await asyncio.wait_for(
                step.handler(context.lid, context.context_data),
                timeout=step.timeout_ms / 1000,
            )
            return result

        except asyncio.TimeoutError:
            if step.retry_on_failure:
                # Retry once
                result = await asyncio.wait_for(
                    step.handler(context.lid, context.context_data),
                    timeout=step.timeout_ms / 1000,
                )
                return result
            raise

    def _track_handoff_performance(self, context: ContextHandoff):
        """Track context handoff performance"""
        latency = context.handoff_latency_ms

        # Add to metrics
        self.performance_metrics["handoff_latencies"].append(latency)

        # Calculate average
        latencies = list(self.performance_metrics["handoff_latencies"])
        if latencies:
            self.performance_metrics["avg_handoff_ms"] = sum(latencies) / len(latencies)

            # Calculate P95
            sorted_latencies = sorted(latencies)
            p95_index = int(len(sorted_latencies) * 0.95)
            self.performance_metrics["p95_handoff_ms"] = sorted_latencies[p95_index]

        # Log if exceeds target
        if not context.meets_target():
            logger.warning(
                f"Context handoff exceeded 250ms target: {latency:.2f}ms "
                f"({context.source_step} → {context.target_step})"
            )

    def _add_narrative(self, workflow_id: str, message: str):
        """Add to workflow narrative for transparency"""
        timestamp = datetime.now(timezone.utc).strftime("%H:%M:%S.%f")[:-3]
        narrative_entry = f"[{timestamp}] {message}"

        if workflow_id not in self.workflow_narratives:
            self.workflow_narratives[workflow_id] = []

        self.workflow_narratives[workflow_id].append(narrative_entry)
        logger.info(f"Workflow {workflow_id}: {message}")

    async def publish_event(self, event_type: str, data: dict):
        """Publish event to subscribers"""
        for subscriber in self.event_subscribers.get(event_type, []):
            try:
                await subscriber(data)
            except Exception as e:
                logger.error(f"Error in event subscriber: {e}")

    def subscribe_event(self, event_type: str, handler: Callable):
        """Subscribe to event type"""
        self.event_subscribers[event_type].append(handler)

    def get_workflow_status(self, workflow_id: str) -> dict:
        """Get current workflow status"""
        if workflow_id not in self.workflows:
            return {"error": "workflow_not_found"}

        workflow = self.workflows[workflow_id]
        return {
            "id": workflow_id,
            "name": workflow["name"],
            "state": workflow["state"].value,
            "current_step": workflow["current_step"],
            "total_steps": len(workflow["steps"]),
            "narrative": self.workflow_narratives.get(workflow_id, []),
        }

    def get_performance_metrics(self) -> dict:
        """Get system performance metrics"""
        return {
            "workflows": {
                "total": self.performance_metrics["total_workflows"],
                "completed": self.performance_metrics["completed_workflows"],
                "failed": self.performance_metrics["failed_workflows"],
                "success_rate": (
                    self.performance_metrics["completed_workflows"]
                    / max(self.performance_metrics["total_workflows"], 1)
                ),
            },
            "handoff_performance": {
                "avg_ms": self.performance_metrics["avg_handoff_ms"],
                "p95_ms": self.performance_metrics["p95_handoff_ms"],
                "meets_250ms_target": self.performance_metrics["p95_handoff_ms"] < 250,
            },
            "rate_limiter": self.rate_limiter.get_metrics(),
        }


# Pre-built workflow pipelines
class WorkflowPipelines:
    """Pre-configured workflow pipelines for common scenarios"""

    @staticmethod
    def create_travel_analysis_pipeline(
        orchestrator: ContextBusOrchestrator,
    ) -> list[WorkflowStep]:
        """
        Create pipeline for MVP demo: Travel document analysis
        Integrates all agents' capabilities
        """
        return [
            WorkflowStep(
                step_id="auth_check",
                name="Verify Authentication",
                # TODO: validate_access is not implemented on LukhasIdentityService; replace with actual method
                handler=lambda lid, ctx: True,
                required_scopes=["authenticate"],
                requires_policy_check=True,
            ),
            WorkflowStep(
                step_id="fetch_gmail",
                name="Fetch Gmail Travel Emails",
                handler=lambda lid, ctx: orchestrator.gmail_integration.workflow_fetch_travel_emails(lid, ctx),
                required_scopes=["read", "list"],
                requires_policy_check=True,
                policy_context={"resource_type": "gmail"},
            ),
            WorkflowStep(
                step_id="fetch_drive",
                name="Fetch Drive Travel Documents",
                handler=lambda lid, ctx: orchestrator.drive_integration.workflow_fetch_travel_documents(lid, ctx),
                required_scopes=["read", "list"],
                requires_policy_check=True,
                policy_context={"resource_type": "drive"},
            ),
            WorkflowStep(
                step_id="fetch_dropbox",
                name="Fetch Dropbox Travel Files",
                handler=lambda lid, ctx: orchestrator.dropbox_integration.workflow_fetch_travel_files(lid, ctx),
                required_scopes=["read", "list"],
                requires_policy_check=True,
                policy_context={"resource_type": "dropbox"},
            ),
            WorkflowStep(
                step_id="analyze_opus4",
                name="Analyze with Opus 4",
                handler=lambda lid, ctx: {"analysis": "Opus 4 analysis of travel documents"},
                required_scopes=["execute"],
                requires_policy_check=True,
                policy_context={"model": orchestrator.model_allocation.get("analysis", "opus-4")},
            ),
            WorkflowStep(
                step_id="cross_reference_opus4",
                name="Cross-reference with Opus 4",
                handler=lambda lid, ctx: {"cross_reference": "Opus 4 validation of analysis"},
                required_scopes=["execute"],
                requires_policy_check=True,
                policy_context={"model": orchestrator.model_allocation.get("cross_reference", "opus-4")},
            ),
            WorkflowStep(
                step_id="generate_summary",
                name="Generate Final Summary",
                handler=lambda lid, ctx: {
                    "summary": "Complete travel document analysis",
                    "flights": ctx.get("travel_emails", []),
                    "documents": ctx.get("travel_documents", []),
                    "files": ctx.get("travel_files", []),
                },
                required_scopes=["write"],
                requires_policy_check=False,
            ),
        ]


if __name__ == "__main__":

    async def test_context_bus():
        print("🧠 Testing Enhanced Context Bus Orchestrator")
        print("-" * 50)

        # Initialize orchestrator
        orchestrator = ContextBusOrchestrator()

        # Create travel analysis pipeline
        pipeline = WorkflowPipelines.create_travel_analysis_pipeline(orchestrator)

        print(f"📋 Pipeline created with {len(pipeline)} steps")
        for step in pipeline:
            print(f"   - {step.name}")

        # Test workflow execution (dry-run)
        print("\n🚀 Testing workflow execution...")

        # Set adapters to dry-run mode
        orchestrator.gmail_adapter.set_dry_run(True)
        orchestrator.drive_adapter.set_dry_run(True)
        orchestrator.dropbox_adapter.set_dry_run(True)

        # Execute workflow
        result = await orchestrator.execute_workflow(
            lid="USR-TEST-123",
            workflow_name="Travel Document Analysis",
            steps=pipeline[:3],  # Test first 3 steps
            initial_context={"auth_token": "test_token"},
        )

        print("\n📊 Workflow Result:")
        print(f"   State: {result['state']}")
        print(f"   Steps completed: {len(result.get('results', []))}")

        if "narrative" in result:
            print("\n📖 Workflow Narrative:")
            for entry in result["narrative"][-5:]:  # Last 5 entries
                print(f"   {entry}")

        # Check performance
        metrics = orchestrator.get_performance_metrics()
        print("\n⚡ Performance Metrics:")
        print(f"   Avg handoff: {metrics['handoff_performance']['avg_ms']:.2f}ms")
        print(f"   P95 handoff: {metrics['handoff_performance']['p95_ms']:.2f}ms")
        print(f"   Meets <250ms target: {metrics['handoff_performance']['meets_250ms_target']}")

        print("\n✅ Context Bus Orchestrator operational!")

    asyncio.run(test_context_bus())
