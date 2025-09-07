#!/usr/bin/env python3
"""
ΛBAS Core - Lambda Boundary Attention System
Advanced attention management and cognitive boundary protection

Part of the Lambda Products Suite by LUKHAS AI
Commercial Version - Ready for Enterprise Deployment
"""
from consciousness.qi import qi
import streamlit as st
from datetime import timezone

import asyncio
import logging
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger("Lambda.ΛBAS", timezone)


class AttentionState(Enum):
    """States of user attention"""

    AVAILABLE = "available"  # Ready for new input
    FOCUSED = "focused"  # Deep work, minimal interruption
    OVERLOADED = "overloaded"  # Too much input, needs protection
    RECOVERING = "recovering"  # Post-overload recovery
    FLOW_STATE = "flow_state"  # Optimal performance, protect carefully
    INTERRUPTED = "interrupted"  # Recently disrupted, sensitive
    OFFLINE = "offline"  # User unavailable


class BoundaryType(Enum):
    """Types of attention boundaries"""

    TEMPORAL = "temporal"  # Time-based boundaries
    COGNITIVE = "cognitive"  # Mental capacity boundaries
    EMOTIONAL = "emotional"  # Emotional protection boundaries
    CONTEXTUAL = "contextual"  # Situation-based boundaries
    SOCIAL = "social"  # Social interaction boundaries
    CREATIVE = "creative"  # Creative flow boundaries


class BoundaryMode(Enum):
    """Boundary enforcement modes"""

    SOFT = "soft"  # Gentle suggestions
    FIRM = "firm"  # Clear blocking with override
    STRICT = "strict"  # Absolute blocking
    ADAPTIVE = "adaptive"  # AI-determined enforcement


@dataclass
class AttentionMetrics:
    """Comprehensive attention state metrics"""

    focus_level: float = 0.5  # 0.0 = scattered, 1.0 = laser focused
    cognitive_load: float = 0.5  # 0.0 = idle, 1.0 = maximum capacity
    interruption_cost: float = 0.0  # Cost of current interruption
    attention_residue: float = 0.0  # Lingering effects from previous tasks
    flow_probability: float = 0.0  # Likelihood of entering flow state
    recovery_rate: float = 1.0  # How quickly attention recovers
    multitask_penalty: float = 0.0  # Performance hit from multitasking
    last_updated: datetime = None

    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = datetime.now(timezone.utc)


@dataclass
class AttentionBoundary:
    """Individual attention boundary configuration"""

    id: str
    type: BoundaryType
    mode: BoundaryMode
    threshold: float  # Trigger threshold (0.0-1.0)
    duration: timedelta  # How long boundary stays active
    exceptions: list[str]  # Exception categories
    auto_adjust: bool = True  # Whether boundary self-adjusts
    lambda_signature: str = None  # Λ authenticity signature
    created_at: datetime = None
    last_triggered: Optional[datetime] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
        if self.lambda_signature is None:
            self.lambda_signature = f"Λ-BOUNDARY-{self.id[:8].upper()}"


@dataclass
class AttentionRequest:
    """Request for user attention"""

    id: str
    source: str  # Where the request comes from
    urgency: float  # 0.0 = low, 1.0 = critical
    cognitive_cost: float  # Estimated mental effort required
    duration_estimate: float  # Expected time required (minutes)
    interruptibility: float  # How ok it is to interrupt (0.0-1.0)
    context_tags: list[str]  # Contextual information
    metadata: dict[str, Any] = None


@dataclass
class AttentionDecision:
    """ΛBAS decision on attention request"""

    request_id: str
    decision: str  # "allow", "defer", "block", "transform"
    confidence: float  # Confidence in decision (0.0-1.0)
    reasoning: list[str]  # Human-readable reasoning
    defer_until: Optional[datetime] = None
    alternative_suggestions: list[str] = None
    lambda_trace: str = None  # Λ decision audit trail
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)
        if self.lambda_trace is None:
            import hashlib

            trace_data = f"{self.request_id}{self.decision}{self.confidence}"
            trace_hash = hashlib.sha256(trace_data.encode()).hexdigest()[:8]
            self.lambda_trace = f"Λ-DECISION-{trace_hash.upper()}"


class ΛBAS:
    """
    Lambda Boundary Attention System

    Core Features:
    - Real-time attention state monitoring
    - Adaptive boundary management
    - Flow state protection
    - Cognitive load balancing
    - Multi-dimensional attention filtering
    - Integration with NIΛS and DΛST systems
    """

    def __init__(self, config: Optional[dict] = None):
        self.config = config or self._default_config()
        self.lambda_brand = "Λ"

        # Core storage
        self.user_attention_states: dict[str, AttentionState] = {}
        self.attention_metrics: dict[str, AttentionMetrics] = {}
        self.active_boundaries: dict[str, list[AttentionBoundary]] = {}
        self.attention_history: dict[str, list[tuple[datetime, AttentionMetrics]]] = {}
        self.decision_log: list[AttentionDecision] = []

        # Request queues
        self.pending_requests: dict[str, list[AttentionRequest]] = {}
        self.deferred_requests: dict[str, list[tuple[AttentionRequest, datetime]]] = {}

        # Integration detection
        self.nias_available = False
        self.dast_available = False

        # Initialize default boundaries
        self._initialize_default_boundaries()

        logger.info("ΛBAS system initialized with attention consciousness")

    def _default_config(self) -> dict:
        """Default ΛBAS configuration"""
        return {
            "brand": "LUKHAS",
            "symbol": "Λ",
            "flow_protection_threshold": 0.8,
            "overload_protection_threshold": 0.7,
            "recovery_time_minutes": 15,
            "max_interruptions_per_hour": 6,
            "adaptive_learning": True,
            "flow_state_detection": True,
            "qi_attention_modeling": True,
            "biometric_integration": False,
        }

    def _initialize_default_boundaries(self):
        """Initialize standard attention boundaries"""
        default_boundaries = [
            AttentionBoundary(
                id="flow-protection",
                type=BoundaryType.COGNITIVE,
                mode=BoundaryMode.STRICT,
                threshold=0.8,
                duration=timedelta(minutes=25),  # Pomodoro-style
                exceptions=["emergency", "critical"],
            ),
            AttentionBoundary(
                id="overload-prevention",
                type=BoundaryType.COGNITIVE,
                mode=BoundaryMode.FIRM,
                threshold=0.7,
                duration=timedelta(minutes=10),
                exceptions=["urgent"],
            ),
            AttentionBoundary(
                id="recovery-protection",
                type=BoundaryType.TEMPORAL,
                mode=BoundaryMode.SOFT,
                threshold=0.3,
                duration=timedelta(minutes=5),
                exceptions=[],
            ),
            AttentionBoundary(
                id="creative-flow",
                type=BoundaryType.CREATIVE,
                mode=BoundaryMode.ADAPTIVE,
                threshold=0.6,
                duration=timedelta(minutes=45),
                exceptions=["inspiration", "collaboration"],
            ),
        ]

        # These will be applied as defaults for new users
        self._default_boundary_templates = {b.id: b for b in default_boundaries}

    async def register_user(self, user_id: str, initial_state: AttentionState = AttentionState.AVAILABLE) -> bool:
        """Register a new user with ΛBAS system"""
        try:
            self.user_attention_states[user_id] = initial_state
            self.attention_metrics[user_id] = AttentionMetrics()
            self.active_boundaries[user_id] = []
            self.attention_history[user_id] = []
            self.pending_requests[user_id] = []
            self.deferred_requests[user_id] = []

            # Apply default boundaries
            for boundary_template in self._default_boundary_templates.values():
                new_boundary = AttentionBoundary(
                    id=f"{user_id}-{boundary_template.id}",
                    type=boundary_template.type,
                    mode=boundary_template.mode,
                    threshold=boundary_template.threshold,
                    duration=boundary_template.duration,
                    exceptions=boundary_template.exceptions.copy(),
                    auto_adjust=boundary_template.auto_adjust,
                )
                self.active_boundaries[user_id].append(new_boundary)

            logger.info(f"Registered user {user_id} with ΛBAS attention management")
            return True

        except Exception as e:
            logger.error(f"Error registering user {user_id}: {e}")
            return False

    async def update_attention_metrics(self, user_id: str, metrics: AttentionMetrics) -> bool:
        """Update user's attention metrics"""
        if user_id not in self.user_attention_states:
            logger.error(f"User not registered: {user_id}")
            return False

        try:
            # Store previous metrics for trend analysis
            current_metrics = self.attention_metrics.get(user_id, AttentionMetrics())
            self.attention_history[user_id].append((datetime.now(timezone.utc), current_metrics))

            # Keep only recent history (last 24 hours)
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=24)
            self.attention_history[user_id] = [
                (timestamp, metric) for timestamp, metric in self.attention_history[user_id] if timestamp > cutoff_time
            ]

            # Update current metrics
            self.attention_metrics[user_id] = metrics

            # Determine attention state from metrics
            new_state = await self._determine_attention_state(user_id, metrics)
            old_state = self.user_attention_states[user_id]
            self.user_attention_states[user_id] = new_state

            # Log state transitions
            if new_state != old_state:
                logger.info(f"User {user_id} attention state: {old_state.value} -> {new_state.value}")

                # Trigger boundary adjustments if needed
                await self._adjust_boundaries_for_state_change(user_id, old_state, new_state)

            # Process any pending requests that might now be allowable
            await self._process_pending_requests(user_id)

            return True

        except Exception as e:
            logger.error(f"Error updating attention metrics for {user_id}: {e}")
            return False

    async def _determine_attention_state(self, user_id: str, metrics: AttentionMetrics) -> AttentionState:
        """Determine attention state from metrics"""

        # Flow state detection
        if (
            metrics.focus_level >= 0.8
            and metrics.cognitive_load >= 0.6
            and metrics.cognitive_load <= 0.8
            and metrics.attention_residue < 0.2
        ):
            return AttentionState.FLOW_STATE

        # Overload detection
        if metrics.cognitive_load >= 0.85 or metrics.attention_residue >= 0.7 or metrics.multitask_penalty >= 0.5:
            return AttentionState.OVERLOADED

        # Recovery state
        if metrics.cognitive_load <= 0.3 and metrics.attention_residue >= 0.4:
            return AttentionState.RECOVERING

        # Focused state
        if metrics.focus_level >= 0.7 and metrics.cognitive_load >= 0.5 and metrics.cognitive_load <= 0.7:
            return AttentionState.FOCUSED

        # Recently interrupted
        datetime.now(timezone.utc)
        if self.attention_history.get(user_id):
            recent_metrics = self.attention_history[user_id][-3:]  # Last 3 data points
            if any(m.interruption_cost >= 0.5 for _, m in recent_metrics):
                return AttentionState.INTERRUPTED

        # Default to available
        return AttentionState.AVAILABLE

    async def request_attention(self, user_id: str, request: AttentionRequest) -> AttentionDecision:
        """
        Primary entry point for attention requests

        Args:
            user_id: Target user identifier
            request: Attention request details

        Returns:
            AttentionDecision with allow/defer/block decision
        """
        if user_id not in self.user_attention_states:
            return AttentionDecision(
                request_id=request.id,
                decision="block",
                confidence=1.0,
                reasoning=["User not registered with ΛBAS system"],
            )

        try:
            # 1. Get current attention state and metrics
            current_state = self.user_attention_states[user_id]
            current_metrics = self.attention_metrics[user_id]

            # 2. Check active boundaries
            boundary_check = await self._check_boundary_violations(user_id, request)
            if boundary_check["blocked"]:
                return AttentionDecision(
                    request_id=request.id,
                    decision="block",
                    confidence=boundary_check["confidence"],
                    reasoning=boundary_check["reasons"],
                )

            # 3. Evaluate request against attention state
            state_evaluation = await self._evaluate_request_for_state(request, current_state, current_metrics)

            if state_evaluation["decision"] == "defer":
                # Add to deferred queue
                defer_until = datetime.now(timezone.utc) + timedelta(minutes=state_evaluation.get("defer_minutes", 15))
                self.deferred_requests[user_id].append((request, defer_until))

                return AttentionDecision(
                    request_id=request.id,
                    decision="defer",
                    confidence=state_evaluation["confidence"],
                    reasoning=state_evaluation["reasoning"],
                    defer_until=defer_until,
                    alternative_suggestions=state_evaluation.get("alternatives", []),
                )

            elif state_evaluation["decision"] == "block":
                return AttentionDecision(
                    request_id=request.id,
                    decision="block",
                    confidence=state_evaluation["confidence"],
                    reasoning=state_evaluation["reasoning"],
                )

            elif state_evaluation["decision"] == "transform":
                return AttentionDecision(
                    request_id=request.id,
                    decision="transform",
                    confidence=state_evaluation["confidence"],
                    reasoning=state_evaluation["reasoning"],
                    alternative_suggestions=state_evaluation.get("transformations", []),
                )

            # 4. Allow the request
            await self._process_allowed_request(user_id, request)

            return AttentionDecision(
                request_id=request.id,
                decision="allow",
                confidence=state_evaluation["confidence"],
                reasoning=state_evaluation["reasoning"],
            )

        except Exception as e:
            logger.error(f"Error processing attention request: {e}")
            return AttentionDecision(
                request_id=request.id,
                decision="block",
                confidence=1.0,
                reasoning=[f"System error: {e!s}"],
            )

    async def _check_boundary_violations(self, user_id: str, request: AttentionRequest) -> dict[str, Any]:
        """Check if request violates any active boundaries"""
        active_boundaries = self.active_boundaries[user_id]
        current_metrics = self.attention_metrics[user_id]

        for boundary in active_boundaries:
            # Check if boundary is currently active
            if not await self._is_boundary_active(boundary, current_metrics):
                continue

            # Check for exceptions
            if any(exception in request.context_tags for exception in boundary.exceptions):
                continue

            # Check violation conditions based on boundary type
            violation = False
            reason = ""

            if boundary.type == BoundaryType.COGNITIVE:
                if current_metrics.cognitive_load >= boundary.threshold:
                    violation = True
                    reason = f"Cognitive load ({current_metrics.cognitive_load:.2f}) exceeds boundary threshold ({boundary.threshold})"

            elif boundary.type == BoundaryType.TEMPORAL:
                # Check time-based boundaries (implementation depends on specific rules)
                violation = await self._check_temporal_boundary(boundary, request)
                reason = "Temporal boundary violation"

            elif boundary.type == BoundaryType.CREATIVE and (
                current_metrics.flow_probability >= boundary.threshold and request.interruptibility < 0.5
            ):
                violation = True
                reason = "Creative flow protection - interruption would be disruptive"

            if violation:
                return {
                    "blocked": True,
                    "boundary_id": boundary.id,
                    "boundary_type": boundary.type.value,
                    "reasons": [reason],
                    "confidence": 0.9 if boundary.mode == BoundaryMode.STRICT else 0.7,
                }

        return {"blocked": False}

    async def _is_boundary_active(self, boundary: AttentionBoundary, metrics: AttentionMetrics) -> bool:
        """Check if boundary is currently active"""
        # Check if recently triggered and still in duration
        if boundary.last_triggered:
            elapsed = datetime.now(timezone.utc) - boundary.last_triggered
            if elapsed < boundary.duration:
                return True

        # Check activation conditions
        if boundary.type == BoundaryType.COGNITIVE:
            return metrics.cognitive_load >= boundary.threshold
        elif boundary.type == BoundaryType.CREATIVE:
            return metrics.flow_probability >= boundary.threshold

        # Default to inactive
        return False

    async def _check_temporal_boundary(self, boundary: AttentionBoundary, request: AttentionRequest) -> bool:
        """Check temporal boundary violations"""
        # Implementation would depend on specific temporal rules
        # For now, simple time-of-day checking
        current_hour = datetime.now(timezone.utc).hour

        # Example: No interruptions during deep work hours (9-11 AM)
        return bool(9 <= current_hour <= 11 and request.urgency < 0.8)

    async def _evaluate_request_for_state(
        self,
        request: AttentionRequest,
        state: AttentionState,
        metrics: AttentionMetrics,
    ) -> dict[str, Any]:
        """Evaluate request appropriateness for current attention state"""

        if state == AttentionState.FLOW_STATE:
            # Extremely protective of flow state
            if request.urgency >= 0.9:
                return {
                    "decision": "allow",
                    "confidence": 0.6,
                    "reasoning": ["Critical urgency overrides flow protection"],
                }
            elif request.interruptibility >= 0.8:
                return {
                    "decision": "defer",
                    "confidence": 0.9,
                    "reasoning": ["Protecting flow state - deferring interruptible request"],
                    "defer_minutes": 25,
                    "alternatives": [
                        "Schedule for next break",
                        "Convert to ambient notification",
                    ],
                }
            else:
                return {
                    "decision": "block",
                    "confidence": 0.95,
                    "reasoning": ["Flow state protection - non-urgent, non-interruptible request blocked"],
                }

        elif state == AttentionState.OVERLOADED:
            # Reduce cognitive load
            if request.cognitive_cost >= 0.5:
                return {
                    "decision": "defer",
                    "confidence": 0.8,
                    "reasoning": ["Cognitive overload - deferring high-cost request"],
                    "defer_minutes": self.config["recovery_time_minutes"],
                    "alternatives": ["Simplify request", "Break into smaller parts"],
                }
            elif request.urgency >= 0.8:
                return {
                    "decision": "transform",
                    "confidence": 0.7,
                    "reasoning": ["High urgency during overload - suggesting transformation"],
                    "transformations": [
                        "Reduce cognitive complexity",
                        "Provide summary only",
                    ],
                }

        elif state == AttentionState.RECOVERING:
            # Gentle re-engagement
            if request.cognitive_cost >= 0.3:
                return {
                    "decision": "defer",
                    "confidence": 0.7,
                    "reasoning": ["Recovery period - deferring cognitively demanding request"],
                    "defer_minutes": 5,
                    "alternatives": ["Wait for full recovery", "Reduce complexity"],
                }

        elif state == AttentionState.FOCUSED:
            # Protect focused work but allow some flexibility
            if request.cognitive_cost >= 0.7 and request.urgency < 0.6:
                return {
                    "decision": "defer",
                    "confidence": 0.6,
                    "reasoning": ["Focused state - deferring high-cost, non-urgent request"],
                    "defer_minutes": 10,
                }

        elif state == AttentionState.INTERRUPTED:
            # Recently interrupted, be more protective
            if request.cognitive_cost >= 0.4:
                return {
                    "decision": "defer",
                    "confidence": 0.8,
                    "reasoning": ["Recent interruption detected - allowing recovery time"],
                    "defer_minutes": 3,
                }

        # Default allow with state-appropriate confidence
        confidence_map = {
            AttentionState.AVAILABLE: 0.9,
            AttentionState.FOCUSED: 0.7,
            AttentionState.INTERRUPTED: 0.6,
            AttentionState.RECOVERING: 0.5,
            AttentionState.OVERLOADED: 0.3,
            AttentionState.FLOW_STATE: 0.2,
        }

        return {
            "decision": "allow",
            "confidence": confidence_map.get(state, 0.5),
            "reasoning": [f"Request approved for {state.value} state"],
        }

    async def _process_allowed_request(self, user_id: str, request: AttentionRequest):
        """Process an allowed attention request"""
        # Update attention metrics based on request impact
        current_metrics = self.attention_metrics[user_id]

        # Estimate impact
        interruption_cost = request.cognitive_cost * (1.0 - request.interruptibility)
        current_metrics.interruption_cost = interruption_cost
        current_metrics.cognitive_load += request.cognitive_cost * 0.5
        current_metrics.attention_residue += interruption_cost * 0.3

        # Cap values at 1.0
        current_metrics.cognitive_load = min(1.0, current_metrics.cognitive_load)
        current_metrics.attention_residue = min(1.0, current_metrics.attention_residue)

        # Reduce flow probability if interrupted
        if interruption_cost > 0.3:
            current_metrics.flow_probability *= 1.0 - interruption_cost

        current_metrics.last_updated = datetime.now(timezone.utc)

    async def _process_pending_requests(self, user_id: str):
        """Process any pending requests that might now be allowable"""
        if user_id not in self.pending_requests:
            return

        pending = self.pending_requests[user_id].copy()
        self.pending_requests[user_id] = []

        for request in pending:
            decision = await self.request_attention(user_id, request)
            if decision.decision == "defer":
                # Still not ready, keep in pending
                self.pending_requests[user_id].append(request)

    async def _adjust_boundaries_for_state_change(
        self, user_id: str, old_state: AttentionState, new_state: AttentionState
    ):
        """Adjust boundaries when attention state changes"""
        if not self.config["adaptive_learning"]:
            return

        boundaries = self.active_boundaries[user_id]

        for boundary in boundaries:
            if not boundary.auto_adjust:
                continue

            # Flow state transitions
            if new_state == AttentionState.FLOW_STATE and old_state != AttentionState.FLOW_STATE:
                # Entering flow - strengthen boundaries
                if boundary.type in [BoundaryType.COGNITIVE, BoundaryType.CREATIVE]:
                    boundary.threshold = max(0.6, boundary.threshold * 0.9)
                    boundary.last_triggered = datetime.now(timezone.utc)

            elif old_state == AttentionState.FLOW_STATE and new_state != AttentionState.FLOW_STATE:
                # Exiting flow - gradually relax boundaries
                if boundary.type in [BoundaryType.COGNITIVE, BoundaryType.CREATIVE]:
                    boundary.threshold = min(0.9, boundary.threshold * 1.1)

    def is_attention_available(self, user_id: str) -> bool:
        """Simple boolean check if user attention is available (for external integrations)"""
        if user_id not in self.user_attention_states:
            return False

        state = self.user_attention_states[user_id]
        return state in [AttentionState.AVAILABLE, AttentionState.FOCUSED]

    async def get_attention_status(self, user_id: str) -> dict[str, Any]:
        """Get comprehensive attention status for a user"""
        if user_id not in self.user_attention_states:
            return {"error": "User not registered"}

        state = self.user_attention_states[user_id]
        metrics = self.attention_metrics[user_id]
        boundaries = self.active_boundaries[user_id]

        # Count active boundaries
        active_boundary_count = 0
        for boundary in boundaries:
            if await self._is_boundary_active(boundary, metrics):
                active_boundary_count += 1

        return {
            "user_id": user_id,
            "attention_state": state.value,
            "metrics": {
                "focus_level": metrics.focus_level,
                "cognitive_load": metrics.cognitive_load,
                "attention_residue": metrics.attention_residue,
                "flow_probability": metrics.flow_probability,
                "last_updated": metrics.last_updated.isoformat(),
            },
            "boundaries": {
                "total": len(boundaries),
                "active": active_boundary_count,
                "types": list({b.type.value for b in boundaries}),
            },
            "queues": {
                "pending_requests": len(self.pending_requests.get(user_id, [])),
                "deferred_requests": len(self.deferred_requests.get(user_id, [])),
            },
        }

    def get_system_metrics(self) -> dict[str, Any]:
        """Get ΛBAS system metrics"""
        total_users = len(self.user_attention_states)

        # Count users by state
        state_counts = {}
        for state in AttentionState:
            state_counts[state.value] = list(self.user_attention_states.values()).count(state)

        # Total boundaries and decisions
        total_boundaries = sum(len(boundaries) for boundaries in self.active_boundaries.values())
        total_decisions = len(self.decision_log)

        # Decision type breakdown
        decision_types = {}
        for decision in self.decision_log[-1000:]:  # Last 1000 decisions
            decision_type = decision.decision
            decision_types[decision_type] = decision_types.get(decision_type, 0) + 1

        return {
            "system": "ΛBAS",
            "version": "1.0.0-lambda",
            "lambda_brand": self.lambda_brand,
            "total_users": total_users,
            "user_states": state_counts,
            "total_boundaries": total_boundaries,
            "total_decisions": total_decisions,
            "recent_decision_types": decision_types,
            "integration_status": {
                "nias_available": self.nias_available,
                "dast_available": self.dast_available,
            },
            "config": {
                "flow_protection": self.config["flow_protection_threshold"],
                "adaptive_learning": self.config["adaptive_learning"],
                "qi_modeling": self.config["qi_attention_modeling"],
            },
        }

    async def create_custom_boundary(self, user_id: str, boundary_config: dict[str, Any]) -> str:
        """Create a custom attention boundary for a user"""
        if user_id not in self.user_attention_states:
            raise ValueError(f"User {user_id} not registered")

        boundary_id = f"{user_id}-custom-{uuid.uuid4().hex[:8]}"

        boundary = AttentionBoundary(
            id=boundary_id,
            type=BoundaryType(boundary_config.get("type", "cognitive")),
            mode=BoundaryMode(boundary_config.get("mode", "adaptive")),
            threshold=boundary_config.get("threshold", 0.7),
            duration=timedelta(minutes=boundary_config.get("duration_minutes", 15)),
            exceptions=boundary_config.get("exceptions", []),
            auto_adjust=boundary_config.get("auto_adjust", True),
        )

        self.active_boundaries[user_id].append(boundary)

        logger.info(f"Created custom boundary {boundary_id} for user {user_id}")
        return boundary_id

    async def remove_boundary(self, user_id: str, boundary_id: str) -> bool:
        """Remove a specific boundary for a user"""
        if user_id not in self.active_boundaries:
            return False

        original_count = len(self.active_boundaries[user_id])
        self.active_boundaries[user_id] = [b for b in self.active_boundaries[user_id] if b.id != boundary_id]

        removed = len(self.active_boundaries[user_id]) < original_count
        if removed:
            logger.info(f"Removed boundary {boundary_id} for user {user_id}")

        return removed


# Demo and testing
if __name__ == "__main__":

    async def demo():
        print("🧠 ΛBAS - Lambda Boundary Attention System Demo")
        print("=" * 60)

        # Initialize ΛBAS
        abas = ΛBAS()

        # Register test user
        await abas.register_user("alice", AttentionState.AVAILABLE)
        print("✅ Registered user: alice")

        # Update attention metrics
        metrics = AttentionMetrics(
            focus_level=0.8,
            cognitive_load=0.6,
            flow_probability=0.7,
            attention_residue=0.2,
        )

        await abas.update_attention_metrics("alice", metrics)
        print(f"📊 Updated attention metrics - State: {abas.user_attention_states['alice'].value}")

        # Create test attention request
        request = AttentionRequest(
            id=str(uuid.uuid4()),
            source="email-notification",
            urgency=0.3,
            cognitive_cost=0.4,
            duration_estimate=2.0,
            interruptibility=0.6,
            context_tags=["work", "communication"],
        )

        print("\n📨 Processing attention request:")
        print(f"   Source: {request.source}")
        print(f"   Urgency: {request.urgency}")
        print(f"   Cognitive Cost: {request.cognitive_cost}")

        # Process request
        decision = await abas.request_attention("alice", request)

        print("\n🎯 ΛBAS Decision:")
        print(f"   Decision: {decision.decision}")
        print(f"   Confidence: {decision.confidence:.2f}")
        print(f"   Reasoning: {', '.join(decision.reasoning)}")
        print(f"   Λ Trace: {decision.lambda_trace}")

        # Get status
        status = await abas.get_attention_status("alice")
        print("\n📊 Attention Status:")
        print(f"   State: {status['attention_state']}")
        print(f"   Focus Level: {status['metrics']['focus_level']:.2f}")
        print(f"   Cognitive Load: {status['metrics']['cognitive_load']:.2f}")
        print(f"   Active Boundaries: {status['boundaries']['active']}/{status['boundaries']['total']}")

        # System metrics
        system_metrics = abas.get_system_metrics()
        print("\n🔧 System Metrics:")
        print(f"   Total Users: {system_metrics['total_users']}")
        print(f"   Total Boundaries: {system_metrics['total_boundaries']}")
        print(f"   Flow Protection: {system_metrics['config']['flow_protection']}")
        print("   Integration Mode: ΛBAS Standalone")

    asyncio.run(demo())
