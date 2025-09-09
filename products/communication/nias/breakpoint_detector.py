"""
Natural Breakpoint Detection System for NIAS
Identifies optimal moments for ad display without disrupting user workflow
"""
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional


class WorkflowState(Enum):
    """User workflow states"""

    IDLE = "idle"
    ACTIVE = "active"
    READING = "reading"
    TYPING = "typing"
    SCROLLING = "scrolling"
    WATCHING = "watching"
    TRANSITIONING = "transitioning"
    COMPLETING_TASK = "completing_task"
    PAUSED = "paused"
    WAITING = "waiting"


class BreakpointType(Enum):
    """Types of natural breakpoints"""

    TASK_COMPLETION = "task_completion"
    NATURAL_PAUSE = "natural_pause"
    CONTENT_BOUNDARY = "content_boundary"
    USER_INITIATED = "user_initiated"
    IDLE_THRESHOLD = "idle_threshold"
    PERMISSION_GRANTED = "permission_granted"
    AFTER_SUCCESS = "after_success"
    BETWEEN_SECTIONS = "between_sections"
    LOADING_SCREEN = "loading_screen"
    ERROR_RECOVERY = "error_recovery"


@dataclass
class UserActivity:
    """Track user activity patterns"""

    timestamp: datetime
    action_type: str
    duration: float
    context: dict[str, Any] = field(default_factory=dict)
    completed: bool = False


@dataclass
class WorkflowContext:
    """Current workflow context"""

    state: WorkflowState
    task_id: Optional[str] = None
    task_type: Optional[str] = None
    start_time: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    activity_count: int = 0
    interruption_score: float = 0.0
    user_satisfaction: float = 1.0


class NaturalBreakpointDetector:
    """
    Detects natural breakpoints in user workflow for non-intrusive ad timing
    Core principle: Never hijack the workflow
    """

    def __init__(self):
        self.current_workflow = WorkflowContext(state=WorkflowState.IDLE)
        self.activity_history: list[UserActivity] = []
        self.breakpoint_history: list[dict] = []
        self.user_permissions: dict[str, bool] = {
            "auto_display": False,
            "after_task": True,
            "during_idle": True,
            "between_content": True,
        }

        # Timing thresholds (in seconds)
        self.idle_threshold = 5.0
        self.pause_threshold = 2.0
        self.min_task_duration = 10.0
        self.cooldown_period = 60.0  # Minimum time between ads
        self.last_ad_time: Optional[datetime] = None

        # Pattern detection
        self.task_patterns: dict[str, list[float]] = {}
        self.completion_indicators = [
            "submit",
            "save",
            "done",
            "complete",
            "finish",
            "send",
            "post",
            "publish",
            "confirm",
            "success",
        ]

    def track_activity(self, action_type: str, context: Optional[dict[str, Any]] = None) -> None:
        """Track user activity for pattern detection"""
        activity = UserActivity(
            timestamp=datetime.now(timezone.utc),
            action_type=action_type,
            duration=0.0,
            context=context or {},
        )

        # Calculate duration if we have previous activity
        if self.activity_history:
            last_activity = self.activity_history[-1]
            activity.duration = (activity.timestamp - last_activity.timestamp).total_seconds()

        self.activity_history.append(activity)

        # Update workflow state
        self._update_workflow_state(action_type, context)

        # Check for task completion
        if self._is_task_completion(action_type, context):
            activity.completed = True
            self._record_task_completion()

    def check_breakpoint(self) -> tuple[bool, Optional[BreakpointType], dict[str, Any]]:
        """
        Check if current moment is a natural breakpoint for ad display
        Returns: (is_breakpoint, breakpoint_type, metadata)
        """

        # Check cooldown period
        if not self._check_cooldown():
            return False, None, {"reason": "cooldown_active"}

        # Priority 1: User explicitly granted permission
        if self._check_user_permission():
            return (
                True,
                BreakpointType.PERMISSION_GRANTED,
                {"confidence": 1.0, "user_initiated": True},
            )

        # Priority 2: Task just completed
        task_completed, task_data = self._check_task_completion()
        if task_completed:
            return (
                True,
                BreakpointType.TASK_COMPLETION,
                {
                    "confidence": 0.95,
                    "task_data": task_data,
                    "message": "Great job! Here's something that might interest you.",
                },
            )

        # Priority 3: Natural pause detected
        is_paused, pause_duration = self._check_natural_pause()
        if is_paused:
            return (
                True,
                BreakpointType.NATURAL_PAUSE,
                {
                    "confidence": 0.85,
                    "pause_duration": pause_duration,
                    "non_intrusive": True,
                },
            )

        # Priority 4: Content boundary
        at_boundary, boundary_type = self._check_content_boundary()
        if at_boundary:
            return (
                True,
                BreakpointType.CONTENT_BOUNDARY,
                {
                    "confidence": 0.8,
                    "boundary_type": boundary_type,
                    "smooth_transition": True,
                },
            )

        # Priority 5: Idle threshold exceeded
        is_idle, idle_duration = self._check_idle_state()
        if is_idle and self.user_permissions.get("during_idle", True):
            return (
                True,
                BreakpointType.IDLE_THRESHOLD,
                {
                    "confidence": 0.7,
                    "idle_duration": idle_duration,
                    "low_engagement": True,
                },
            )

        # Priority 6: Between sections/loading
        if self._check_transition_state():
            return (
                True,
                BreakpointType.BETWEEN_SECTIONS,
                {"confidence": 0.75, "natural_break": True},
            )

        return False, None, {"reason": "no_suitable_breakpoint"}

    def request_permission(self, context: str = "general", incentive: Optional[str] = None) -> dict[str, Any]:
        """
        Request user permission for ad display
        Implements the consent-based approach
        """
        request = {
            "type": "permission_request",
            "context": context,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": self._generate_permission_message(context, incentive),
            "incentive": incentive,
            "options": {
                "allow_once": "Show me this time",
                "allow_session": "Allow for this session",
                "allow_always": "Always allow at natural breaks",
                "deny": "Not now",
            },
        }

        # Record request
        self.breakpoint_history.append(
            {
                "type": "permission_request",
                "timestamp": datetime.now(timezone.utc),
                "context": context,
            }
        )

        return request

    def record_ad_display(
        self,
        ad_id: str,
        breakpoint_type: BreakpointType,
        user_response: Optional[str] = None,
    ) -> None:
        """Record when an ad was displayed"""
        self.last_ad_time = datetime.now(timezone.utc)

        record = {
            "timestamp": datetime.now(timezone.utc),
            "ad_id": ad_id,
            "breakpoint_type": breakpoint_type.value,
            "workflow_state": self.current_workflow.state.value,
            "user_response": user_response,
            "interruption_score": self.current_workflow.interruption_score,
        }

        self.breakpoint_history.append(record)

        # Update interruption score based on response
        if user_response == "dismissed_quickly":
            self.current_workflow.interruption_score += 0.2
        elif user_response == "engaged":
            self.current_workflow.interruption_score = max(0, self.current_workflow.interruption_score - 0.1)

    def get_timing_recommendations(self) -> dict[str, Any]:
        """Get recommendations for optimal ad timing"""

        # Analyze historical patterns
        best_times = self._analyze_best_times()
        worst_times = self._analyze_worst_times()

        # Current state analysis
        current_suitability = self._calculate_current_suitability()

        return {
            "current_suitability": current_suitability,
            "recommended_wait": self._calculate_recommended_wait(),
            "best_breakpoint_types": self._rank_breakpoint_types(),
            "user_patterns": {
                "average_task_duration": self._calculate_avg_task_duration(),
                "common_pause_points": self._identify_pause_patterns(),
                "peak_activity_times": best_times,
                "low_activity_times": worst_times,
            },
            "optimization_suggestions": self._generate_timing_suggestions(),
        }

    def _update_workflow_state(self, action_type: str, context: dict):
        """Update current workflow state based on activity"""
        self.current_workflow.last_activity = datetime.now(timezone.utc)
        self.current_workflow.activity_count += 1

        # State transitions
        if action_type in ["click", "tap", "select"]:
            self.current_workflow.state = WorkflowState.ACTIVE
        elif action_type in ["type", "input", "edit"]:
            self.current_workflow.state = WorkflowState.TYPING
        elif action_type in ["scroll", "swipe"]:
            self.current_workflow.state = WorkflowState.SCROLLING
        elif action_type in ["watch", "play", "stream"]:
            self.current_workflow.state = WorkflowState.WATCHING
        elif action_type in ["wait", "load", "buffer"]:
            self.current_workflow.state = WorkflowState.WAITING
        elif action_type in self.completion_indicators:
            self.current_workflow.state = WorkflowState.COMPLETING_TASK

        # Update task context
        if "task_id" in context:
            self.current_workflow.task_id = context["task_id"]
        if "task_type" in context:
            self.current_workflow.task_type = context["task_type"]

    def _is_task_completion(self, action_type: str, context: dict) -> bool:
        """Detect if an action indicates task completion"""
        # Check explicit completion indicators
        if action_type in self.completion_indicators:
            return True

        # Check context for success indicators
        if context:
            if context.get("status") == "success":
                return True
            if context.get("completed"):
                return True
            if "result" in context and context["result"] in [
                "success",
                "done",
                "complete",
            ]:
                return True

        # Check for form submission patterns
        return bool(action_type == "submit" and self.current_workflow.state == WorkflowState.TYPING)

    def _record_task_completion(self):
        """Record task completion for pattern learning"""
        if self.current_workflow.task_type:
            duration = (datetime.now(timezone.utc) - self.current_workflow.start_time).total_seconds()

            if self.current_workflow.task_type not in self.task_patterns:
                self.task_patterns[self.current_workflow.task_type] = []

            self.task_patterns[self.current_workflow.task_type].append(duration)

    def _check_cooldown(self) -> bool:
        """Check if enough time has passed since last ad"""
        if not self.last_ad_time:
            return True

        time_since_last = (datetime.now(timezone.utc) - self.last_ad_time).total_seconds()
        return time_since_last >= self.cooldown_period

    def _check_user_permission(self) -> bool:
        """Check if user has granted permission"""
        # Check for recent explicit permission
        for record in reversed(self.breakpoint_history[-10:]):
            if record.get("type") == "permission_granted":
                time_diff = (datetime.now(timezone.utc) - record["timestamp"]).total_seconds()
                if time_diff < 300:  # Permission valid for 5 minutes
                    return True
        return False

    def _check_task_completion(self) -> tuple[bool, Optional[dict]]:
        """Check if a task was just completed"""
        if self.current_workflow.state != WorkflowState.COMPLETING_TASK:
            return False, None

        # Check if we just transitioned to completion
        time_since_activity = (datetime.now(timezone.utc) - self.current_workflow.last_activity).total_seconds()
        if time_since_activity < 2.0:  # Within 2 seconds of completion
            task_data = {
                "task_type": self.current_workflow.task_type,
                "task_duration": (datetime.now(timezone.utc) - self.current_workflow.start_time).total_seconds(),
            }
            return True, task_data

        return False, None

    def _check_natural_pause(self) -> tuple[bool, float]:
        """Check if user is in a natural pause"""
        if self.current_workflow.state != WorkflowState.PAUSED:
            # Check for pause based on inactivity
            time_since_activity = (datetime.now(timezone.utc) - self.current_workflow.last_activity).total_seconds()
            if time_since_activity > self.pause_threshold:
                self.current_workflow.state = WorkflowState.PAUSED
                return True, time_since_activity

        return self.current_workflow.state == WorkflowState.PAUSED, 0.0

    def _check_content_boundary(self) -> tuple[bool, Optional[str]]:
        """Check if user is at a content boundary"""
        # Check recent activity for boundary indicators
        if len(self.activity_history) < 2:
            return False, None

        last_action = self.activity_history[-1]

        # Page transitions
        if last_action.action_type in ["page_change", "navigate", "route_change"]:
            return True, "page_transition"

        # Content completion
        if last_action.context.get("end_of_content"):
            return True, "content_end"

        # Section boundaries
        if last_action.action_type == "scroll" and last_action.context.get("at_section_break"):
            return True, "section_break"

        return False, None

    def _check_idle_state(self) -> tuple[bool, float]:
        """Check if user is idle"""
        time_since_activity = (datetime.now(timezone.utc) - self.current_workflow.last_activity).total_seconds()
        is_idle = time_since_activity > self.idle_threshold
        return is_idle, time_since_activity if is_idle else 0.0

    def _check_transition_state(self) -> bool:
        """Check if user is in a transition state"""
        return self.current_workflow.state in [
            WorkflowState.TRANSITIONING,
            WorkflowState.WAITING,
        ]

    def _generate_permission_message(self, context: str, incentive: Optional[str]) -> str:
        """Generate contextual permission message"""
        if incentive:
            return f"We have {incentive} available. Would you like to see it now?"

        messages = {
            "task_complete": "Great work! While you take a breather, would you like to see something interesting?",
            "idle": "Taking a break? Here's something you might enjoy.",
            "between_content": "Before you continue, there's something that might interest you.",
            "general": "We have relevant content for you. Is now a good time?",
        }

        return messages.get(context, messages["general"])

    def _calculate_current_suitability(self) -> float:
        """Calculate current suitability score for ad display (0-1)"""
        score = 0.5  # Base score

        # Positive factors
        if self.current_workflow.state == WorkflowState.IDLE:
            score += 0.2
        if self.current_workflow.state == WorkflowState.PAUSED:
            score += 0.15
        if self.current_workflow.state == WorkflowState.COMPLETING_TASK:
            score += 0.25

        # Negative factors
        if self.current_workflow.state == WorkflowState.TYPING:
            score -= 0.3
        if self.current_workflow.state == WorkflowState.WATCHING:
            score -= 0.25
        if self.current_workflow.interruption_score > 0.5:
            score -= 0.2

        # Time-based factors
        if not self._check_cooldown():
            score -= 0.4

        return max(0.0, min(1.0, score))

    def _calculate_recommended_wait(self) -> float:
        """Calculate recommended wait time before next ad (seconds)"""
        base_wait = 0.0

        # If in active state, wait longer
        if self.current_workflow.state in [WorkflowState.TYPING, WorkflowState.ACTIVE]:
            base_wait += 30.0

        # If recently showed ad, enforce cooldown
        if self.last_ad_time:
            time_since_last = (datetime.now(timezone.utc) - self.last_ad_time).total_seconds()
            if time_since_last < self.cooldown_period:
                base_wait = max(base_wait, self.cooldown_period - time_since_last)

        # If high interruption score, wait longer
        base_wait += self.current_workflow.interruption_score * 20.0

        return base_wait

    def _rank_breakpoint_types(self) -> list[str]:
        """Rank breakpoint types by current suitability"""
        rankings = []

        if self.current_workflow.state == WorkflowState.COMPLETING_TASK:
            rankings.append(BreakpointType.TASK_COMPLETION.value)

        if self.current_workflow.state == WorkflowState.PAUSED:
            rankings.append(BreakpointType.NATURAL_PAUSE.value)

        if self.current_workflow.state == WorkflowState.TRANSITIONING:
            rankings.append(BreakpointType.BETWEEN_SECTIONS.value)

        if self.current_workflow.state == WorkflowState.IDLE:
            rankings.append(BreakpointType.IDLE_THRESHOLD.value)

        # Always include permission as top option
        rankings.insert(0, BreakpointType.PERMISSION_GRANTED.value)

        return rankings

    def _calculate_avg_task_duration(self) -> float:
        """Calculate average task duration"""
        all_durations = []
        for task_durations in self.task_patterns.values():
            all_durations.extend(task_durations)

        if not all_durations:
            return 30.0  # Default estimate

        return sum(all_durations) / len(all_durations)

    def _identify_pause_patterns(self) -> list[dict]:
        """Identify common pause patterns"""
        pause_patterns = []

        for i in range(1, len(self.activity_history)):
            current = self.activity_history[i]
            previous = self.activity_history[i - 1]

            gap = (current.timestamp - previous.timestamp).total_seconds()
            if gap > self.pause_threshold:
                pause_patterns.append(
                    {
                        "after_action": previous.action_type,
                        "before_action": current.action_type,
                        "duration": gap,
                    }
                )

        return pause_patterns[-10:]  # Return last 10 patterns

    def _analyze_best_times(self) -> list[str]:
        """Analyze best times for ads based on history"""
        successful_displays = [record for record in self.breakpoint_history if record.get("user_response") == "engaged"]

        if not successful_displays:
            return ["after_task_completion", "during_natural_pause"]

        # Count breakpoint types
        type_counts = {}
        for record in successful_displays:
            bp_type = record.get("breakpoint_type", "unknown")
            type_counts[bp_type] = type_counts.get(bp_type, 0) + 1

        # Sort by count
        sorted_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)
        return [t[0] for t in sorted_types[:3]]

    def _analyze_worst_times(self) -> list[str]:
        """Analyze worst times for ads based on history"""
        poor_displays = [
            record for record in self.breakpoint_history if record.get("user_response") == "dismissed_quickly"
        ]

        if not poor_displays:
            return ["during_typing", "during_watching"]

        # Count workflow states
        state_counts = {}
        for record in poor_displays:
            state = record.get("workflow_state", "unknown")
            state_counts[state] = state_counts.get(state, 0) + 1

        # Sort by count
        sorted_states = sorted(state_counts.items(), key=lambda x: x[1], reverse=True)
        return [s[0] for s in sorted_states[:3]]

    def _generate_timing_suggestions(self) -> list[str]:
        """Generate suggestions for timing optimization"""
        suggestions = []

        if self.current_workflow.interruption_score > 0.3:
            suggestions.append("Consider longer cooldown periods between ads")

        if not self.user_permissions.get("auto_display"):
            suggestions.append("Request explicit permission for better user satisfaction")

        avg_task_duration = self._calculate_avg_task_duration()
        if avg_task_duration < 30:
            suggestions.append("Wait for longer tasks to complete before displaying ads")

        if len(self.breakpoint_history) > 10:
            success_rate = sum(1 for r in self.breakpoint_history[-10:] if r.get("user_response") == "engaged") / 10
            if success_rate < 0.3:
                suggestions.append("Improve targeting or reduce ad frequency")

        return suggestions


# Example usage
if __name__ == "__main__":
    detector = NaturalBreakpointDetector()

    # Simulate user activity
    detector.track_activity("type", {"task_id": "form_123", "task_type": "form_fill"})
    time.sleep(0.5)
    detector.track_activity("type", {"field": "email"})
    time.sleep(0.5)
    detector.track_activity("submit", {"task_id": "form_123", "status": "success"})

    # Check for breakpoint
    is_breakpoint, bp_type, metadata = detector.check_breakpoint()

    if is_breakpoint:
        print(f"Natural breakpoint detected: {bp_type.value}")
        print(f"Metadata: {metadata}")

        # Request permission if needed
        if bp_type != BreakpointType.PERMISSION_GRANTED:
            permission_request = detector.request_permission(context="task_complete", incentive="exclusive content")
            print(f"Permission request: {permission_request}")

    # Get timing recommendations
    recommendations = detector.get_timing_recommendations()
    print(f"\nTiming recommendations: {recommendations}")