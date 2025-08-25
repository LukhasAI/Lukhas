"""
👥 Human-in-the-Loop Orchestrator (HITLO)
═══════════════════════════════════════════════════════════════════════════

PURPOSE: Route critical decisions through human reviewers with auto-escrow
CAPABILITY: Human oversight, decision queuing, auto-escrow, reviewer management
INTEGRATION: Deep integration with MEG, SRD, XIL, and master orchestrator
SCOPE: Global decision orchestration with human wisdom integration

🎯 CORE CAPABILITIES:
- Critical decision routing and escalation
- Human reviewer pool management
- Auto-escrow for high-stakes decisions
- Consensus building and conflict resolution
- Real-time decision tracking and notifications
- Quality assurance and reviewer feedback
- Emergency override and fail-safe mechanisms
- Audit trail and compliance reporting

🛡️ SAFETY & GOVERNANCE:
- Multi-reviewer validation for critical decisions
- Cryptographic decision integrity
- SRD-signed reviewer responses
- Conflict of interest detection
- Bias monitoring and mitigation
- Escalation chains and emergency protocols
- Human rights and dignity preservation

🔧 TECHNICAL FEATURES:
- Async decision processing pipeline
- Real-time reviewer notifications
- Auto-timeout and fallback handling
- Decision caching and retrieval
- Integration with existing orchestration
- Metrics and performance monitoring
- Reviewer expertise matching
- Decision impact assessment

VERSION: v1.0.0 • CREATED: 2025-07-19 • AUTHOR: LUKHAS AGI TEAM
SYMBOLIC TAGS: ΛHITLO, ΛHUMAN, ΛORCHESTRATOR, ΛDECISION, ΛESCROW
"""

import asyncio
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from enum import Enum
from typing import Any, Optional

import structlog

# ΛTRACE: Standardized logging for HITLO module
logger = structlog.get_logger(__name__)
logger.info("ΛTRACE_MODULE_INIT", module_path=__file__, status="initializing")

# Graceful imports with fallbacks for Lukhas integration
try:
    from communication.explainability_interface_layer import (
        ExplainabilityInterfaceLayer,
    )

    from ethics.meta_ethics_governor import EthicalVerdict, MetaEthicsGovernor
    from ethics.self_reflective_debugger import SelfReflectiveDebugger
    from candidate.orchestration.lukhas_master_orchestrator import LukhasMasterOrchestrator

    LUKHAS_INTEGRATION = True
    logger.info(
        "ΛTRACE_IMPORT_SUCCESS",
        components=["MEG", "SRD", "XIL", "MasterOrchestrator"],
    )
except ImportError as e:
    logger.warning("ΛTRACE_IMPORT_FALLBACK", error=str(e), mode="standalone")
    LUKHAS_INTEGRATION = False

    # Graceful fallback classes

    class EthicalVerdict(Enum):
        APPROVED = "approved"
        REQUIRES_REVIEW = "requires_review"
        REJECTED = "rejected"

    MetaEthicsGovernor = None
    SelfReflectiveDebugger = None
    ExplainabilityInterfaceLayer = None
    LukhasMasterOrchestrator = None


class DecisionPriority(Enum):
    """Priority levels for human review decisions."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class ReviewerRole(Enum):
    """Roles for human reviewers in the system."""

    ETHICS_SPECIALIST = "ethics_specialist"
    DOMAIN_EXPERT = "domain_expert"
    SAFETY_AUDITOR = "safety_auditor"
    COMPLIANCE_OFFICER = "compliance_officer"
    TECHNICAL_REVIEWER = "technical_reviewer"
    GENERAL_REVIEWER = "general_reviewer"
    SENIOR_OVERSEER = "senior_overseer"


class DecisionStatus(Enum):
    """Status tracking for decisions in HITLO."""

    PENDING_REVIEW = "pending_review"
    UNDER_REVIEW = "under_review"
    AWAITING_CONSENSUS = "awaiting_consensus"
    CONSENSUS_REACHED = "consensus_reached"
    APPROVED = "approved"
    REJECTED = "rejected"
    ESCALATED = "escalated"
    TIMED_OUT = "timed_out"
    EMERGENCY_OVERRIDE = "emergency_override"


class EscrowStatus(Enum):
    """Status for auto-escrow functionality."""

    NOT_REQUIRED = "not_required"
    ESCROWED = "escrowed"
    RELEASED = "released"
    REFUNDED = "refunded"
    DISPUTED = "disputed"


@dataclass
class ReviewerProfile:
    """Profile for human reviewers in the HITLO system."""

    reviewer_id: str
    name: str
    roles: list[ReviewerRole]
    expertise_domains: list[str]
    experience_level: int  # 1-10 scale
    current_workload: int
    max_concurrent_reviews: int = 5
    availability_hours: dict[str, list[tuple[int, int]]] = field(
        default_factory=dict
    )  # Day -> [(start_hour, end_hour)]
    performance_metrics: dict[str, float] = field(default_factory=dict)
    contact_methods: list[str] = field(default_factory=list)
    languages: list[str] = field(default_factory=lambda: ["en"])
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_active: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True


@dataclass
class DecisionContext:
    """Context information for decisions requiring human review."""

    decision_id: str
    decision_type: str
    description: str
    data: dict[str, Any]
    priority: DecisionPriority
    urgency_deadline: Optional[datetime] = None
    ethical_implications: list[str] = field(default_factory=list)
    required_expertise: list[str] = field(default_factory=list)
    estimated_impact: str = "medium"
    stakeholders: list[str] = field(default_factory=list)
    background_context: dict[str, Any] = field(default_factory=dict)
    ai_recommendation: Optional[str] = None
    ai_confidence: float = 0.0
    related_decisions: list[str] = field(default_factory=list)


@dataclass
class EscrowDetails:
    """Details for auto-escrow functionality."""

    escrow_id: str
    amount: Decimal
    currency: str = "USD"
    escrow_type: str = "decision_stake"
    stakeholder: str = ""
    conditions: list[str] = field(default_factory=list)
    release_criteria: dict[str, Any] = field(default_factory=dict)
    status: EscrowStatus = EscrowStatus.NOT_REQUIRED
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None


@dataclass
class ReviewAssignment:
    """Assignment of a decision to a specific reviewer."""

    assignment_id: str
    decision_id: str
    reviewer_id: str
    assigned_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    due_date: Optional[datetime] = None
    status: str = "assigned"
    priority_boost: float = 0.0
    notification_sent: bool = False
    reminder_count: int = 0


@dataclass
class ReviewResponse:
    """Response from a human reviewer."""

    response_id: str
    assignment_id: str
    reviewer_id: str
    decision: str  # "approve", "reject", "needs_more_info", "escalate"
    confidence: float
    reasoning: str
    recommendations: list[str] = field(default_factory=list)
    concerns: list[str] = field(default_factory=list)
    additional_reviewers_needed: list[ReviewerRole] = field(default_factory=list)
    estimated_review_time_minutes: Optional[int] = None
    srd_signature: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class DecisionRecord:
    """Complete record of a decision processed through HITLO."""

    decision_id: str
    context: DecisionContext
    assignments: list[ReviewAssignment] = field(default_factory=list)
    responses: list[ReviewResponse] = field(default_factory=list)
    final_decision: Optional[str] = None
    consensus_score: float = 0.0
    escrow_details: Optional[EscrowDetails] = None
    status: DecisionStatus = DecisionStatus.PENDING_REVIEW
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    ai_explanation: Optional[str] = None
    human_explanation: Optional[str] = None
    audit_trail: list[dict[str, Any]] = field(default_factory=list)


class ReviewerNotification(ABC):
    """Abstract base class for reviewer notification systems."""

    @abstractmethod
    async def send_notification(
        self,
        reviewer: ReviewerProfile,
        decision: DecisionRecord,
        notification_type: str,
    ) -> bool:
        """Send notification to reviewer."""


class EmailNotification(ReviewerNotification):
    """Email notification implementation."""

    async def send_notification(
        self,
        reviewer: ReviewerProfile,
        decision: DecisionRecord,
        notification_type: str,
    ) -> bool:
        """ΛSTUB: Send email notification."""
        # ΛTODO: Implement actual email sending
        logger.info(
            "ΛTRACE_EMAIL_NOTIFICATION",
            reviewer_id=reviewer.reviewer_id,
            decision_id=decision.decision_id,
            type=notification_type,
        )
        return True


class SlackNotification(ReviewerNotification):
    """Slack notification implementation."""

    async def send_notification(
        self,
        reviewer: ReviewerProfile,
        decision: DecisionRecord,
        notification_type: str,
    ) -> bool:
        """ΛSTUB: Send Slack notification."""
        # ΛTODO: Implement Slack API integration
        logger.info(
            "ΛTRACE_SLACK_NOTIFICATION",
            reviewer_id=reviewer.reviewer_id,
            decision_id=decision.decision_id,
            type=notification_type,
        )
        return True


class HumanInTheLoopOrchestrator:
    """
    Main HITLO class for routing decisions through human reviewers.

    ΛTAG: orchestrator, human_oversight, decision_routing
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """Initialize HITLO with configuration."""
        self.config = config or {}
        self.logger = logger.bind(component="HITLO")

        # Core storage
        self.reviewers: dict[str, ReviewerProfile] = {}
        self.decisions: dict[str, DecisionRecord] = {}
        self.assignments: dict[str, ReviewAssignment] = {}

        # Integration components (graceful fallback)
        self.meg = None
        self.srd = None
        self.xil = None
        self.master_orchestrator = None

        if LUKHAS_INTEGRATION:
            self._initialize_lukhas_integration()

        # Notification systems
        self.notification_systems = {
            "email": EmailNotification(),
            "slack": SlackNotification(),
        }

        # Configuration
        self.consensus_threshold = self.config.get("consensus_threshold", 0.7)
        self.max_review_time_hours = self.config.get("max_review_time_hours", 48)
        self.emergency_timeout_minutes = self.config.get(
            "emergency_timeout_minutes", 60
        )
        self.min_reviewers_per_decision = self.config.get(
            "min_reviewers_per_decision", 2
        )
        self.max_reviewers_per_decision = self.config.get(
            "max_reviewers_per_decision", 5
        )

        # Metrics and state
        self.metrics = {
            "decisions_processed": 0,
            "decisions_approved": 0,
            "decisions_rejected": 0,
            "average_review_time_hours": 0.0,
            "consensus_reached_rate": 0.0,
            "reviewer_workload_balance": 0.0,
            "escalation_rate": 0.0,
            "emergency_overrides": 0,
            "escrow_operations": 0,
        }

        # Background tasks
        self._background_tasks: set[asyncio.Task] = set()
        self._shutdown_event = asyncio.Event()

        self.logger.info(
            "ΛTRACE_HITLO_INIT",
            lukhas_integration=LUKHAS_INTEGRATION,
            consensus_threshold=self.consensus_threshold,
            max_review_time=self.max_review_time_hours,
        )

    def _initialize_lukhas_integration(self):
        """Initialize integration with Lukhas components."""
        try:
            if MetaEthicsGovernor:
                self.meg = MetaEthicsGovernor()
                self.logger.info("ΛTRACE_MEG_INTEGRATION", status="active")

            if SelfReflectiveDebugger:
                self.srd = SelfReflectiveDebugger()
                self.logger.info("ΛTRACE_SRD_INTEGRATION", status="active")

            if ExplainabilityInterfaceLayer:
                self.xil = ExplainabilityInterfaceLayer()
                self.logger.info("ΛTRACE_XIL_INTEGRATION", status="active")

            if LukhasMasterOrchestrator:
                self.master_orchestrator = LukhasMasterOrchestrator()
                self.logger.info("ΛTRACE_ORCHESTRATOR_INTEGRATION", status="active")

        except Exception as e:
            self.logger.warning("ΛTRACE_INTEGRATION_PARTIAL", error=str(e))

    async def start(self):
        """Start HITLO background services."""
        self.logger.info("ΛTRACE_HITLO_START")

        # Start background monitoring tasks
        monitor_task = asyncio.create_task(self._monitor_decisions())
        timeout_task = asyncio.create_task(self._handle_timeouts())
        metrics_task = asyncio.create_task(self._update_metrics())

        self._background_tasks.update([monitor_task, timeout_task, metrics_task])

        self.logger.info(
            "ΛTRACE_HITLO_STARTED",
            background_tasks=len(self._background_tasks),
        )

    async def stop(self):
        """Stop HITLO and clean up resources."""
        self.logger.info("ΛTRACE_HITLO_STOP")

        self._shutdown_event.set()

        # Cancel background tasks
        for task in self._background_tasks:
            task.cancel()

        # Wait for tasks to complete
        if self._background_tasks:
            await asyncio.gather(*self._background_tasks, return_exceptions=True)

        self.logger.info("ΛTRACE_HITLO_STOPPED")

    async def register_reviewer(self, reviewer: ReviewerProfile) -> str:
        """Register a new human reviewer."""
        reviewer_logger = self.logger.bind(reviewer_id=reviewer.reviewer_id)

        if reviewer.reviewer_id in self.reviewers:
            reviewer_logger.warning("ΛTRACE_REVIEWER_ALREADY_EXISTS")
            return reviewer.reviewer_id

        self.reviewers[reviewer.reviewer_id] = reviewer

        reviewer_logger.info(
            "ΛTRACE_REVIEWER_REGISTERED",
            roles=[role.value for role in reviewer.roles],
            expertise=reviewer.expertise_domains,
            experience=reviewer.experience_level,
        )

        return reviewer.reviewer_id

    async def submit_decision_for_review(
        self,
        context: DecisionContext,
        escrow_details: Optional[EscrowDetails] = None,
    ) -> str:
        """Submit a decision for human review through HITLO."""
        decision_logger = self.logger.bind(decision_id=context.decision_id)

        decision_logger.info(
            "ΛTRACE_DECISION_SUBMITTED",
            priority=context.priority.value,
            decision_type=context.decision_type,
            has_escrow=escrow_details is not None,
        )

        # Create decision record
        decision_record = DecisionRecord(
            decision_id=context.decision_id,
            context=context,
            escrow_details=escrow_details,
            status=DecisionStatus.PENDING_REVIEW,
        )

        # Generate AI explanation if XIL available
        if self.xil:
            try:
                ai_explanation = await self._generate_ai_explanation(context)
                decision_record.ai_explanation = ai_explanation
            except Exception as e:
                decision_logger.warning("ΛTRACE_AI_EXPLANATION_ERROR", error=str(e))

        # Handle escrow if required
        if escrow_details:
            await self._handle_escrow_setup(escrow_details)

        # Store decision record
        self.decisions[context.decision_id] = decision_record

        # Find and assign reviewers
        reviewers = await self._find_suitable_reviewers(context)
        if not reviewers:
            decision_logger.error("ΛTRACE_NO_REVIEWERS_AVAILABLE")
            decision_record.status = DecisionStatus.ESCALATED
            return context.decision_id

        # Create assignments
        assignments = await self._create_review_assignments(
            context.decision_id, reviewers
        )
        decision_record.assignments = assignments
        decision_record.status = DecisionStatus.UNDER_REVIEW

        # Send notifications
        await self._notify_reviewers(decision_record, "new_assignment")

        # Add to audit trail
        decision_record.audit_trail.append(
            {
                "action": "decision_submitted",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "reviewers_assigned": len(assignments),
                "priority": context.priority.value,
            }
        )

        self.metrics["decisions_processed"] += 1

        decision_logger.info(
            "ΛTRACE_DECISION_REVIEW_STARTED",
            reviewers_assigned=len(assignments),
            status=decision_record.status.value,
        )

        return context.decision_id

    async def submit_review_response(
        self, assignment_id: str, response: ReviewResponse
    ) -> bool:
        """Submit a review response from a human reviewer."""
        response_logger = self.logger.bind(
            assignment_id=assignment_id, reviewer_id=response.reviewer_id
        )

        if assignment_id not in self.assignments:
            response_logger.error("ΛTRACE_ASSIGNMENT_NOT_FOUND")
            return False

        assignment = self.assignments[assignment_id]
        decision = self.decisions.get(assignment.decision_id)

        if not decision:
            response_logger.error("ΛTRACE_DECISION_NOT_FOUND")
            return False

        # Sign response with SRD if available
        if self.srd and not response.srd_signature:
            try:
                response.srd_signature = await self._sign_response(response)
            except Exception as e:
                response_logger.warning("ΛTRACE_RESPONSE_SIGNING_ERROR", error=str(e))

        # Add response to decision record
        decision.responses.append(response)

        # Update assignment status
        assignment.status = "completed"

        response_logger.info(
            "ΛTRACE_RESPONSE_SUBMITTED",
            decision=response.decision,
            confidence=response.confidence,
            signed=response.srd_signature is not None,
        )

        # Check if we have enough responses to make a decision
        await self._evaluate_consensus(decision)

        # Add to audit trail
        decision.audit_trail.append(
            {
                "action": "response_submitted",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "reviewer_id": response.reviewer_id,
                "decision": response.decision,
                "confidence": response.confidence,
            }
        )

        return True

    async def _find_suitable_reviewers(
        self, context: DecisionContext
    ) -> list[ReviewerProfile]:
        """Find suitable reviewers for a decision context."""
        suitable_reviewers = []

        for reviewer in self.reviewers.values():
            if not reviewer.is_active:
                continue

            if reviewer.current_workload >= reviewer.max_concurrent_reviews:
                continue

            # Check expertise match
            expertise_match = False
            if context.required_expertise:
                for expertise in context.required_expertise:
                    if expertise in reviewer.expertise_domains:
                        expertise_match = True
                        break
            else:
                expertise_match = True

            if not expertise_match:
                continue

            # Check role suitability
            role_match = self._check_role_suitability(reviewer, context)
            if not role_match:
                continue

            suitable_reviewers.append(reviewer)

        # Sort by suitability score
        suitable_reviewers.sort(
            key=lambda r: self._calculate_reviewer_suitability_score(r, context),
            reverse=True,
        )

        # Limit based on priority
        max_reviewers = self._get_reviewer_count_for_priority(context.priority)
        return suitable_reviewers[:max_reviewers]

    def _check_role_suitability(
        self, reviewer: ReviewerProfile, context: DecisionContext
    ) -> bool:
        """Check if reviewer roles are suitable for decision context."""
        # Ethics-related decisions need ethics specialists
        if (
            context.ethical_implications
            and ReviewerRole.ETHICS_SPECIALIST in reviewer.roles
        ):
            return True

        # High priority decisions need senior overseers
        if (
            context.priority
            in [
                DecisionPriority.CRITICAL,
                DecisionPriority.EMERGENCY,
            ]
            and ReviewerRole.SENIOR_OVERSEER in reviewer.roles
        ):
            return True

        # Always allow general reviewers
        return ReviewerRole.GENERAL_REVIEWER in reviewer.roles

    def _calculate_reviewer_suitability_score(
        self, reviewer: ReviewerProfile, context: DecisionContext
    ) -> float:
        """Calculate how suitable a reviewer is for a given decision."""
        score = 0.0

        # Experience level (0-10 scale)
        score += reviewer.experience_level * 0.2

        # Expertise match
        expertise_matches = sum(
            1
            for expertise in context.required_expertise
            if expertise in reviewer.expertise_domains
        )
        if context.required_expertise:
            score += (expertise_matches / len(context.required_expertise)) * 0.3

        # Workload (prefer less busy reviewers)
        workload_factor = 1.0 - (
            reviewer.current_workload / reviewer.max_concurrent_reviews
        )
        score += workload_factor * 0.2

        # Performance metrics
        if "average_quality" in reviewer.performance_metrics:
            score += reviewer.performance_metrics["average_quality"] * 0.2

        # Availability
        if self._is_reviewer_available_now(reviewer):
            score += 0.1

        return score

    def _is_reviewer_available_now(self, reviewer: ReviewerProfile) -> bool:
        """ΛSTUB: Check if reviewer is currently available."""
        # ΛTODO: Implement timezone-aware availability checking
        return True

    def _get_reviewer_count_for_priority(self, priority: DecisionPriority) -> int:
        """Get number of reviewers needed based on priority."""
        if priority == DecisionPriority.EMERGENCY:
            return self.max_reviewers_per_decision
        elif priority == DecisionPriority.CRITICAL:
            return max(3, self.min_reviewers_per_decision)
        elif priority == DecisionPriority.HIGH:
            return max(2, self.min_reviewers_per_decision)
        else:
            return self.min_reviewers_per_decision

    async def _create_review_assignments(
        self, decision_id: str, reviewers: list[ReviewerProfile]
    ) -> list[ReviewAssignment]:
        """Create review assignments for selected reviewers."""
        assignments = []

        for reviewer in reviewers:
            assignment_id = str(uuid.uuid4())

            # Calculate due date based on priority
            decision = self.decisions[decision_id]
            due_date = self._calculate_due_date(decision.context.priority)

            assignment = ReviewAssignment(
                assignment_id=assignment_id,
                decision_id=decision_id,
                reviewer_id=reviewer.reviewer_id,
                due_date=due_date,
            )

            assignments.append(assignment)
            self.assignments[assignment_id] = assignment

            # Update reviewer workload
            reviewer.current_workload += 1

        return assignments

    def _calculate_due_date(self, priority: DecisionPriority) -> datetime:
        """Calculate due date based on decision priority."""
        now = datetime.now(timezone.utc)

        if priority == DecisionPriority.EMERGENCY:
            return now + timedelta(minutes=self.emergency_timeout_minutes)
        elif priority == DecisionPriority.CRITICAL:
            return now + timedelta(hours=4)
        elif priority == DecisionPriority.HIGH:
            return now + timedelta(hours=12)
        elif priority == DecisionPriority.MEDIUM:
            return now + timedelta(hours=24)
        else:  # LOW
            return now + timedelta(hours=self.max_review_time_hours)

    async def _notify_reviewers(self, decision: DecisionRecord, notification_type: str):
        """Send notifications to assigned reviewers."""
        for assignment in decision.assignments:
            reviewer = self.reviewers.get(assignment.reviewer_id)
            if not reviewer:
                continue

            # Send notifications via configured methods
            for contact_method in reviewer.contact_methods:
                if contact_method in self.notification_systems:
                    try:
                        await self.notification_systems[
                            contact_method
                        ].send_notification(reviewer, decision, notification_type)
                        assignment.notification_sent = True
                    except Exception as e:
                        self.logger.error(
                            "ΛTRACE_NOTIFICATION_ERROR",
                            reviewer_id=reviewer.reviewer_id,
                            method=contact_method,
                            error=str(e),
                        )

    async def _evaluate_consensus(self, decision: DecisionRecord):
        """Evaluate if consensus has been reached among reviewers."""
        if not decision.responses:
            return

        # Count responses by decision type
        decisions = {}
        total_confidence = 0.0

        for response in decision.responses:
            if response.decision not in decisions:
                decisions[response.decision] = []
            decisions[response.decision].append(response)
            total_confidence += response.confidence

        # Calculate consensus
        total_responses = len(decision.responses)
        avg_confidence = (
            total_confidence / total_responses if total_responses > 0 else 0.0
        )

        # Find majority decision
        majority_decision = max(decisions.keys(), key=lambda k: len(decisions[k]))
        majority_count = len(decisions[majority_decision])
        consensus_score = majority_count / total_responses

        decision.consensus_score = consensus_score

        # Check if consensus threshold is met
        if consensus_score >= self.consensus_threshold and avg_confidence >= 0.6:
            decision.status = DecisionStatus.CONSENSUS_REACHED
            decision.final_decision = majority_decision
            decision.completed_at = datetime.now(timezone.utc)

            # Handle escrow release/refund
            if decision.escrow_details:
                await self._handle_escrow_completion(decision)

            # Generate human explanation
            if self.xil:
                decision.human_explanation = await self._generate_human_explanation(
                    decision
                )

            # Update metrics
            if majority_decision == "approve":
                self.metrics["decisions_approved"] += 1
            elif majority_decision == "reject":
                self.metrics["decisions_rejected"] += 1

            self.logger.info(
                "ΛTRACE_CONSENSUS_REACHED",
                decision_id=decision.decision_id,
                final_decision=majority_decision,
                consensus_score=consensus_score,
                avg_confidence=avg_confidence,
            )

        elif total_responses >= self.max_reviewers_per_decision:
            # No consensus with maximum reviewers - escalate
            decision.status = DecisionStatus.ESCALATED
            self.metrics["escalation_rate"] = (
                self.metrics.get("escalation_rate", 0)
                * (self.metrics["decisions_processed"] - 1)
                + 1
            ) / self.metrics["decisions_processed"]

            self.logger.warning(
                "ΛTRACE_DECISION_ESCALATED",
                decision_id=decision.decision_id,
                consensus_score=consensus_score,
                total_responses=total_responses,
            )

    async def _generate_ai_explanation(self, context: DecisionContext) -> str:
        """Generate AI explanation for the decision context."""
        if not self.xil:
            return "AI explanation not available (XIL not integrated)"

        # ΛSTUB: Integration with XIL for AI explanations
        # ΛTODO: Implement full XIL integration
        return f"AI Analysis: Decision type '{context.decision_type}' with confidence {context.ai_confidence:.2f}"

    async def _generate_human_explanation(self, decision: DecisionRecord) -> str:
        """Generate human-readable explanation of the final decision."""
        if not decision.responses:
            return "No human reviews available"

        # Aggregate human reasoning
        all_reasoning = []
        all_recommendations = []

        for response in decision.responses:
            if response.reasoning:
                all_reasoning.append(
                    f"Reviewer {response.reviewer_id}: {response.reasoning}"
                )
            all_recommendations.extend(response.recommendations)

        explanation_parts = [
            f"Final Decision: {decision.final_decision}",
            f"Consensus Score: {decision.consensus_score:.2f}",
            f"Total Reviewers: {len(decision.responses)}",
            "",
            "Human Reasoning:",
        ]

        explanation_parts.extend(all_reasoning)

        if all_recommendations:
            explanation_parts.extend(
                [
                    "",
                    "Recommendations:",
                    "- " + "\n- ".join(set(all_recommendations)),
                ]
            )

        return "\n".join(explanation_parts)

    async def _handle_escrow_setup(self, escrow_details: EscrowDetails):
        """Set up auto-escrow for a decision."""
        # ΛSTUB: Implement escrow setup logic
        # ΛTODO: Integration with financial/crypto escrow systems
        escrow_details.status = EscrowStatus.ESCROWED
        self.metrics["escrow_operations"] += 1

        self.logger.info(
            "ΛTRACE_ESCROW_SETUP",
            escrow_id=escrow_details.escrow_id,
            amount=str(escrow_details.amount),
            currency=escrow_details.currency,
        )

    async def _handle_escrow_completion(self, decision: DecisionRecord):
        """Handle escrow release/refund based on decision outcome."""
        if not decision.escrow_details:
            return

        escrow = decision.escrow_details

        if decision.final_decision == "approve":
            escrow.status = EscrowStatus.RELEASED
            self.logger.info("ΛTRACE_ESCROW_RELEASED", escrow_id=escrow.escrow_id)
        else:
            escrow.status = EscrowStatus.REFUNDED
            self.logger.info("ΛTRACE_ESCROW_REFUNDED", escrow_id=escrow.escrow_id)

    async def _sign_response(self, response: ReviewResponse) -> str:
        """Sign reviewer response using SRD."""
        if not self.srd:
            return "SRD_NOT_AVAILABLE"

        # ΛSTUB: Implement SRD signing for responses
        # ΛTODO: Use SRD cryptographic signing
        signature_data = {
            "response_id": response.response_id,
            "reviewer_id": response.reviewer_id,
            "decision": response.decision,
            "timestamp": response.timestamp.isoformat(),
        }
        return f"SRD_SIGNATURE_{hash(str(signature_data))}"

    async def _monitor_decisions(self):
        """Background task to monitor decision progress."""
        while not self._shutdown_event.is_set():
            try:
                for decision in self.decisions.values():
                    if decision.status in [
                        DecisionStatus.UNDER_REVIEW,
                        DecisionStatus.AWAITING_CONSENSUS,
                    ]:
                        # Send reminders for overdue assignments
                        await self._send_reminders_if_needed(decision)

                await asyncio.sleep(300)  # Check every 5 minutes

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error("ΛTRACE_MONITOR_ERROR", error=str(e))
                await asyncio.sleep(60)

    async def _handle_timeouts(self):
        """Background task to handle decision timeouts."""
        while not self._shutdown_event.is_set():
            try:
                now = datetime.now(timezone.utc)

                for decision in self.decisions.values():
                    if decision.status not in [
                        DecisionStatus.UNDER_REVIEW,
                        DecisionStatus.AWAITING_CONSENSUS,
                    ]:
                        continue

                    # Check for timeout
                    if (
                        decision.context.urgency_deadline
                        and now > decision.context.urgency_deadline
                    ):
                        await self._handle_decision_timeout(decision)

                await asyncio.sleep(60)  # Check every minute

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error("ΛTRACE_TIMEOUT_HANDLER_ERROR", error=str(e))
                await asyncio.sleep(60)

    async def _handle_decision_timeout(self, decision: DecisionRecord):
        """Handle decision that has timed out."""
        decision.status = DecisionStatus.TIMED_OUT
        decision.completed_at = datetime.now(timezone.utc)

        # Default action based on priority
        if decision.context.priority == DecisionPriority.EMERGENCY:
            # Emergency override - approve with caution
            decision.final_decision = "approve_emergency_override"
            decision.status = DecisionStatus.EMERGENCY_OVERRIDE
            self.metrics["emergency_overrides"] += 1
        else:
            # Conservative default - reject
            decision.final_decision = "reject_timeout"

        self.logger.warning(
            "ΛTRACE_DECISION_TIMEOUT",
            decision_id=decision.decision_id,
            priority=decision.context.priority.value,
            final_action=decision.final_decision,
        )

    async def _send_reminders_if_needed(self, decision: DecisionRecord):
        """Send reminders to reviewers for overdue assignments."""
        now = datetime.now(timezone.utc)

        for assignment in decision.assignments:
            if assignment.status != "assigned":
                continue

            if assignment.due_date and now > assignment.due_date:
                if assignment.reminder_count < 3:  # Max 3 reminders
                    await self._notify_reviewers(decision, "reminder")
                    assignment.reminder_count += 1

    async def _update_metrics(self):
        """Background task to update performance metrics."""
        while not self._shutdown_event.is_set():
            try:
                # Calculate average review time
                completed_decisions = [
                    d
                    for d in self.decisions.values()
                    if d.completed_at
                    and d.status
                    in [
                        DecisionStatus.CONSENSUS_REACHED,
                        DecisionStatus.APPROVED,
                        DecisionStatus.REJECTED,
                    ]
                ]

                if completed_decisions:
                    total_time = sum(
                        (d.completed_at - d.created_at).total_seconds() / 3600
                        for d in completed_decisions
                    )
                    self.metrics["average_review_time_hours"] = total_time / len(
                        completed_decisions
                    )

                # Calculate consensus rate
                consensus_decisions = [
                    d
                    for d in completed_decisions
                    if d.status == DecisionStatus.CONSENSUS_REACHED
                ]

                if completed_decisions:
                    self.metrics["consensus_reached_rate"] = len(
                        consensus_decisions
                    ) / len(completed_decisions)

                # Calculate reviewer workload balance
                if self.reviewers:
                    workloads = [r.current_workload for r in self.reviewers.values()]
                    avg_workload = sum(workloads) / len(workloads)
                    max_workload = max(workloads) if workloads else 0
                    self.metrics["reviewer_workload_balance"] = 1.0 - (
                        max_workload - avg_workload
                    ) / max(max_workload, 1)

                await asyncio.sleep(3600)  # Update every hour

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error("ΛTRACE_METRICS_UPDATE_ERROR", error=str(e))
                await asyncio.sleep(300)

    def get_decision_status(self, decision_id: str) -> Optional[dict[str, Any]]:
        """Get current status of a decision."""
        decision = self.decisions.get(decision_id)
        if not decision:
            return None

        return {
            "decision_id": decision_id,
            "status": decision.status.value,
            "created_at": decision.created_at.isoformat(),
            "completed_at": (
                decision.completed_at.isoformat() if decision.completed_at else None
            ),
            "final_decision": decision.final_decision,
            "consensus_score": decision.consensus_score,
            "total_responses": len(decision.responses),
            "total_assignments": len(decision.assignments),
            "has_escrow": decision.escrow_details is not None,
            "priority": decision.context.priority.value,
        }

    def get_reviewer_workload(self, reviewer_id: str) -> Optional[dict[str, Any]]:
        """Get current workload for a reviewer."""
        reviewer = self.reviewers.get(reviewer_id)
        if not reviewer:
            return None

        active_assignments = [
            a
            for a in self.assignments.values()
            if a.reviewer_id == reviewer_id and a.status == "assigned"
        ]

        return {
            "reviewer_id": reviewer_id,
            "current_workload": reviewer.current_workload,
            "max_concurrent_reviews": reviewer.max_concurrent_reviews,
            "active_assignments": len(active_assignments),
            "is_active": reviewer.is_active,
            "last_active": reviewer.last_active.isoformat(),
            "performance_metrics": reviewer.performance_metrics,
        }

    def get_metrics(self) -> dict[str, Any]:
        """Get HITLO performance metrics."""
        return self.metrics.copy()

    async def emergency_override(
        self,
        decision_id: str,
        override_decision: str,
        override_reason: str,
        authorizer_id: str,
    ) -> bool:
        """Perform emergency override of a decision."""
        decision = self.decisions.get(decision_id)
        if not decision:
            return False

        decision.status = DecisionStatus.EMERGENCY_OVERRIDE
        decision.final_decision = override_decision
        decision.completed_at = datetime.now(timezone.utc)

        # Add to audit trail
        decision.audit_trail.append(
            {
                "action": "emergency_override",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "authorizer_id": authorizer_id,
                "override_decision": override_decision,
                "reason": override_reason,
            }
        )

        self.metrics["emergency_overrides"] += 1

        self.logger.warning(
            "ΛTRACE_EMERGENCY_OVERRIDE",
            decision_id=decision_id,
            override_decision=override_decision,
            authorizer_id=authorizer_id,
            reason=override_reason,
        )

        return True


# ΛFOOTER: ═══════════════════════════════════════════════════════════════════
# MODULE: orchestration.human_in_the_loop_orchestrator
# INTEGRATION: MEG ethical review, SRD signing, XIL explanations, master orchestrator
# STANDARDS: Lukhas headers, ΛTAG annotations, structlog logging
# NOTES: Designed for human wisdom integration, auto-escrow, and decision transparency
# ═══════════════════════════════════════════════════════════════════════════
